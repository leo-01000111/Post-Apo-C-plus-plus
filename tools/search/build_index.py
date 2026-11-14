#!/usr/bin/env python3
"""Build 8_search/search.db (SQLite FTS5) from cppreference, Stack Overflow and the kit.

    python3 tools/search/build_index.py

Python 3.8+, standard library only.
"""
import sys
sys.dont_write_bytecode = True
import collections
import html as htmlmod
import json
import os
import re
import sqlite3
import time
from html.parser import HTMLParser
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = KIT / "8_search"
DB = OUT_DIR / "search.db"
REF_ROOT = KIT / "6_reference" / "cppreference" / "reference"
QA = KIT / "7_stackoverflow" / "qa.jsonl"

TOKENIZE = "porter unicode61 tokenchars '_'"
VOID = {"br", "img", "hr", "meta", "link", "input", "area", "base", "col", "embed",
        "param", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "noscript", "svg", "head"}
SKIP_CLASSES = ("navbox", "t-navbar", "noprint", "mw-editsection", "toc", "printfooter",
                "catlinks", "t-dsc-see")


class TextExtractor(HTMLParser):
    """Visible text of a page. If only_id is found in the page, only text inside it is kept."""

    def __init__(self, only_id=None):
        super().__init__(convert_charrefs=True)
        self.only_id = only_id
        self.stack = []            # (tag, is_skip, is_root)
        self.skip = 0
        self.root = 0 if only_id else 1
        self.parts = []
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            if tag == "br" and self.root and not self.skip:
                self.parts.append(" ")
            return
        if tag == "title":
            self.in_title = True
        a = dict(attrs)
        skip = tag in SKIP_TAGS
        if not skip:
            cls = a.get("class") or ""
            if cls and any(c in cls for c in SKIP_CLASSES):
                skip = True
            elif a.get("id") in ("toc", "siteSub", "contentSub", "jump-to-nav", "mw-head", "mw-panel"):
                skip = True
        is_root = bool(self.only_id and a.get("id") == self.only_id)
        self.stack.append((tag, skip, is_root))
        if skip:
            self.skip += 1
        if is_root:
            self.root += 1
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4", "pre", "dt", "dd") and self.root:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _t, sk, rt in self.stack[i:]:
                    if sk:
                        self.skip -= 1
                    if rt:
                        self.root -= 1
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        elif self.root and not self.skip:
            self.parts.append(data)

    def text(self):
        return re.sub(r"\s+", " ", "".join(self.parts)).strip()


def html_to_text(s, only_id=None):
    if only_id and ('id="%s"' % only_id) not in s:
        only_id = None
    p = TextExtractor(only_id)
    try:
        p.feed(s)
        p.close()
    except Exception:
        pass
    title = re.sub(r"\s+", " ", "".join(p.title)).strip()
    return title, p.text()


def so_text(s):
    return html_to_text("<div>" + (s or "") + "</div>")[1]


# ----------------------------------------------------------------- cppreference
def parse_ref(rel):
    try:
        raw = (REF_ROOT / rel).read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"<title>(.*?)</title>", raw, re.S)
    a = raw.find('id="mw-content-text"')
    if a >= 0:                      # parse only the content region (much faster)
        a = raw.rfind("<", 0, a)
        b = raw.find("NewPP limit report", a)
        c = raw.find('class="printfooter"', a)
        ends = [x for x in (b, c) if x > 0]
        raw = "<title>%s</title>%s" % (m.group(1) if m else "", raw[a:min(ends) if ends else len(raw)])
    title, body = html_to_text(raw, "mw-content-text")
    title = re.sub(r"\s+-\s+cppreference\.com\s*$", "", title)
    if not title:
        title = Path(rel).stem
    return rel, title, body


def ref_files():
    out = []
    base = REF_ROOT / "en"
    for dp, _dn, fns in os.walk(base):
        for f in fns:
            if f.endswith(".html"):
                out.append(Path(dp, f).relative_to(REF_ROOT).as_posix())
    out.sort()
    return out


def collect_cppref():
    files = ref_files()
    results = []
    try:
        import multiprocessing as mp
        with mp.Pool(min(12, os.cpu_count() or 2)) as pool:
            for r in pool.imap(parse_ref, files, chunksize=40):
                results.append(r)
    except Exception as e:                       # no multiprocessing: do it serially
        print("  (serial fallback: %s)" % e)
        results = [parse_ref(f) for f in files]
    docs = []
    for r in results:
        if not r or len(r[2]) < 20:
            continue
        rel, title, body = r
        tags = " ".join(Path(rel).with_suffix("").parts[1:])
        docs.append(("cppref", title, rel, 0, {"preview": body[:400]}, tags, body))
    return docs


# ----------------------------------------------------------------- stack overflow
def collect_so():
    if not QA.exists():
        print("  7_stackoverflow/qa.jsonl not found - skipping Stack Overflow")
        return []
    qs = collections.OrderedDict()
    with open(QA, "rb") as f:
        off = 0
        for line in f:
            start, off = off, off + len(line)
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line.decode("utf-8", errors="replace"))
            except ValueError:
                continue                            # partial last line while downloading
            qid = str(d.get("qid"))
            q = qs.get(qid)
            if q is None:
                q = qs[qid] = {"title": d.get("title") or "", "tags": d.get("tags") or [],
                               "score": d.get("score") or 0, "link": d.get("link") or "",
                               "qtext": so_text(d.get("q_html")), "atext": [], "offs": []}
            q["atext"].append(so_text(d.get("a_html")))
            if len(q["offs"]) < 30:
                q["offs"].append(start)
    docs = []
    for qid, q in qs.items():
        title = htmlmod.unescape(q["title"])
        body = q["qtext"] + " " + " ".join(q["atext"])
        tags = " ".join(q["tags"]) if isinstance(q["tags"], list) else str(q["tags"])
        extra = {"preview": q["qtext"][:400], "tags": tags, "link": q["link"], "offs": q["offs"]}
        docs.append(("so", title, qid, int(q["score"] or 0), extra, tags, body))
    return docs


# ----------------------------------------------------------------- the kit
def collect_kit():
    docs = []
    # cheat-sheets: one doc per "## " section
    for p in sorted((KIT / "1_cheatsheet").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(KIT).as_posix()
        sections, cur_t, cur = [], p.stem, []
        for ln in text.splitlines():
            if ln.startswith("## "):
                if "".join(cur).strip():
                    sections.append((cur_t, "\n".join(cur)))
                cur_t, cur = re.sub(r"\s+", " ", ln[3:].replace("`", "")).strip(), []
            else:
                cur.append(ln)
        if "".join(cur).strip():
            sections.append((cur_t, "\n".join(cur)))
        for t, body in sections:
            title = "%s (%s)" % (t, p.name)
            docs.append(("kit", title, rel, 0, {"preview": body.strip()[:400]}, p.stem, body))
    # snippets and solved exams
    pats = [(KIT / "2_snippets", ("*.cpp", "*.h", "*.hpp")), (KIT / "3_solved_exams", ("**/*.cpp", "**/*.h", "**/*.hpp"))]
    for root, globs in pats:
        seen = set()
        for g in globs:
            for p in sorted(root.glob(g)):
                if p in seen or not p.is_file():
                    continue
                seen.add(p)
                body = p.read_text(encoding="utf-8", errors="replace")
                rel = p.relative_to(KIT).as_posix()
                title = p.relative_to(root).as_posix() if root.name == "3_solved_exams" else p.name
                docs.append(("kit", title, rel, 0, {"preview": body[:400]}, root.name, body))
    return docs


def collect_fn():
    sys.path.insert(0, str(KIT / "site_src"))
    try:
        import functions
    except Exception as e:
        print("  cannot import functions.py: %s" % e)
        return []
    def slug(s):
        s = re.sub(r"<[^>]+>|`", "", s)
        return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48] or "x"
    docs = []
    for f in functions.FUNCTIONS:
        name, scope = f["name"], f["scope"]
        body = "\n".join([name, f.get("header", ""), f.get("sig", ""), f.get("ex", ""),
                          f.get("cx", ""), f.get("note", "")])
        prev = (f.get("sig", "").split("\n")[0] + "  " + f.get("note", ""))[:400]
        path = "START_HERE.html#functions/fn-%s-%s" % (slug(scope), slug(name))
        extra = {"preview": prev, "header": f.get("header", ""), "tags": scope}
        docs.append(("fn", "%s (%s)" % (name, scope), path, 0, extra,
                     "%s %s" % (scope, f.get("header", "")), body))
    return docs


# ----------------------------------------------------------------- main
def main():
    t0 = time.time()
    OUT_DIR.mkdir(exist_ok=True)
    tmp = OUT_DIR / "search.db.tmp"
    for p in (tmp, Path(str(tmp) + "-journal")):
        if p.exists():
            p.unlink()
    print("Collecting ...")
    allsrc = []
    for name, fn in (("kit", collect_kit), ("fn", collect_fn), ("cppref", collect_cppref), ("so", collect_so)):
        t = time.time()
        d = fn()
        print("  %-7s %6d docs  (%.1fs)" % (name, len(d), time.time() - t))
        allsrc.append(d)

    con = sqlite3.connect(str(tmp))
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("CREATE TABLE docs(rowid INTEGER PRIMARY KEY, source TEXT NOT NULL "
                "CHECK(source IN ('kit','fn','cppref','so')), title TEXT, url_or_path TEXT, "
                "score INTEGER DEFAULT 0, extra TEXT)")
    con.execute("CREATE VIRTUAL TABLE idx USING fts5(title, tags, body, tokenize=\"%s\")" % TOKENIZE)
    con.execute("CREATE TABLE words(w TEXT PRIMARY KEY, n INTEGER) WITHOUT ROWID")
    word_re = re.compile(r"[a-z][a-z0-9_]{2,31}")
    counts = collections.Counter()
    rid = 0
    doc_rows, fts_rows = [], []
    for docs in allsrc:
        for source, title, path, score, extra, tags, body in docs:
            rid += 1
            doc_rows.append((rid, source, title, path, score, json.dumps(extra, ensure_ascii=False)))
            fts_rows.append((rid, title, tags, body))
            counts.update(word_re.findall((title + " " + tags + " " + body).lower()))
    with con:
        con.executemany("INSERT INTO docs VALUES (?,?,?,?,?,?)", doc_rows)
        con.executemany("INSERT INTO idx(rowid,title,tags,body) VALUES (?,?,?,?)", fts_rows)
        con.executemany("INSERT INTO words VALUES (?,?)", ((w, n) for w, n in counts.items() if n >= 2))
    con.execute("INSERT INTO idx(idx) VALUES('optimize')")
    con.commit()
    con.close()
    if DB.exists():
        DB.unlink()
    tmp.replace(DB)
    print("\nIndexed per source:")
    for docs, name in zip(allsrc, ("kit", "fn", "cppref", "so")):
        print("  %-7s %d" % (name, len(docs)))
    print("DB: %s  (%.1f MB)   build time %.1fs" % (DB, DB.stat().st_size / 1e6, time.time() - t0))


if __name__ == "__main__":
    main()
