#!/usr/bin/env python3
"""Shared search logic for the exam-kit search (used by serve.py and search.sh).

Python 3.8+, standard library only.  Can also be run directly:
    python3 tools/search/engine.py "query words"
"""
import sys
sys.dont_write_bytecode = True
import difflib
import json
import math
import re
import sqlite3
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent.parent
DB_PATH = KIT / "8_search" / "search.db"
SOURCES = ("kit", "fn", "cppref", "so")
HL_A, HL_B = "\x02", "\x03"          # highlight markers inside snippets
_SRC_PRIOR = {"fn": 1.3, "kit": 1.15, "cppref": 1.0, "so": 1.0}


def connect(path=None):
    path = Path(path or DB_PATH)
    try:
        con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, check_same_thread=False)
    except sqlite3.Error:
        con = sqlite3.connect(str(path), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


# ------------------------------------------------------------------ query
def build_match(q, prefix=True, op="AND"):
    """Turn free user text into a safe FTS5 MATCH expression (or None)."""
    items = []
    for raw in q.split():
        parts = re.findall(r"\w+", raw)
        if not parts:
            continue
        # single word -> quoted term; std::sort / foo.bar / a-b -> quoted phrase
        items.append('"%s"' % " ".join(parts))
    if not items:
        return None
    if prefix and q and not q[-1].isspace():
        items[-1] += "*"
    return (" %s " % op).join(items)


def _leaf(title):
    t = title
    while True:
        n = re.sub(r"<[^<>]*>", "", t)
        if n == t:
            break
        t = n
    return t.split("::")[-1].strip().lower()


def _qnorm(q):
    q = q.strip().lower()
    return re.sub(r"\(\s*\)$", "", q)


def _qleaf(q):
    return _qnorm(q).split("::")[-1].lstrip(".")


# ------------------------------------------------------------------ vocab
_vocab_cache = {}


def _vocab(con):
    v = _vocab_cache.get("v")
    if v is None:
        words = {}
        try:
            for w, n in con.execute("SELECT w, n FROM words"):
                words[w] = n
        except sqlite3.Error:
            pass
        by_first = {}
        for w in words:
            by_first.setdefault(w[:1], []).append(w)
        v = _vocab_cache["v"] = (words, by_first)
    return v


def suggest(con, q):
    words, by_first = _vocab(con)
    if not words:
        return None
    out, changed = [], False
    for raw in q.split():
        core = re.sub(r"[^a-z0-9_]", "", raw.lower())
        if len(core) < 3 or core in words or core.isdigit():
            out.append(raw)
            continue
        cands = [w for w in by_first.get(core[:1], ()) if abs(len(w) - len(core)) <= 2]
        m = difflib.get_close_matches(core, cands, n=5, cutoff=0.75)
        if m:
            best = max(m, key=lambda w: difflib.SequenceMatcher(None, core, w).ratio()
                       + 0.02 * math.log1p(words[w]))
            out.append(best)
            changed = True
        else:
            out.append(raw)
    return " ".join(out) if changed else None


# ------------------------------------------------------------------ search
def _url(source, path):
    if source == "cppref":
        return "/ref/" + path
    if source in ("kit", "fn"):
        return "/kit/" + path
    return "/so/" + path


_SQL = ("SELECT d.rowid AS id, d.source, d.title, d.url_or_path AS path, d.score, d.extra, "
        "bm25(idx, 10.0, 4.0, 1.0) AS r, snippet(idx, -1, ?, ?, ' ... ', 24) AS sn "
        "FROM idx JOIN docs d ON d.rowid = idx.rowid "
        "WHERE idx MATCH ? AND d.source = ? ORDER BY r LIMIT ?")


def _run(con, match, srcs, per_src):
    rows = []
    for s in srcs:
        try:
            rows.extend(con.execute(_SQL, (HL_A, HL_B, match, s, per_src)).fetchall())
        except sqlite3.OperationalError:
            continue
    return rows


def search(q, src="all", n=30, prefix=True, con=None):
    """Search; if the words find nothing exact and a spelling correction exists, show the
    corrected results directly ("Showing results for ..."), keeping the original as corrected_from."""
    own = con is None
    if own:
        con = connect()
    try:
        out = _search(q, src, n, prefix, con)
        sug = out.get("suggest")
        if out.pop("_used_or", False) or not out["results"]:   # exact hits, even few, win
            if sug and sug.lower() != q.lower():
                fixed = _search(sug, src, n, prefix, con)
                if fixed["results"] and not fixed.pop("_used_or", False):
                    return {"q": sug, "results": fixed["results"], "suggest": None, "corrected_from": q}
        return out
    finally:
        if own:
            con.close()


def _search(q, src, n, prefix, con):
    if True:
        srcs = list(SOURCES) if src == "all" else [src]
        if any(s not in SOURCES for s in srcs):
            srcs = list(SOURCES)
        rows, used_or = [], False
        for op in ("AND", "OR"):
            match = build_match(q, prefix, op)
            if not match:
                return {"q": q, "results": [], "suggest": None}
            rows = _run(con, match, srcs, max(60, n * 2))
            used_or = op == "OR"
            if rows or len(q.split()) < 2:
                break
        qn, ql = _qnorm(q), _qleaf(q)
        res = []
        for r in rows:
            base = -r["r"]
            if base <= 0:
                base = 1e-6
            mult = _SRC_PRIOR.get(r["source"], 1.0)
            title = r["title"]
            if r["source"] == "fn":
                name = title.split(" (")[0].lower()
                if name == ql or name == qn:
                    mult *= 25
                elif qn.split(" ")[0] == name or ql.split(" ")[0] == name:
                    mult *= 6   # query starts with the function's name: "accumulate double"
            elif r["source"] == "cppref":
                if title.lower() == qn or _leaf(title) == ql:
                    mult *= 3
                if r["path"].startswith("en/c/"):
                    mult *= 0.85
            elif title.lower() == qn:
                mult *= 3
            if r["source"] == "so":
                mult *= 1 + 0.12 * math.log1p(max(r["score"] or 0, 0))
            try:
                extra = json.loads(r["extra"]) if r["extra"] else {}
            except ValueError:
                extra = {}
            sn = re.sub(r"\s+", " ", r["sn"] or "").strip()
            if HL_A not in sn and extra.get("preview"):
                sn = re.sub(r"\s+", " ", extra["preview"])[:160]
            res.append({
                "id": r["id"], "source": r["source"], "title": title, "path": r["path"],
                "url": _url(r["source"], r["path"]), "score": r["score"], "snippet": sn,
                "rank": base * mult,
                "tags": extra.get("tags", ""), "hdr": extra.get("header", ""),
            })
        res.sort(key=lambda x: -x["rank"])
        res = res[:n]
        for x in res:
            x["rank"] = round(x["rank"], 3)
        sug = suggest(con, q) if (len(res) < 3 or used_or) else None
        return {"q": q, "results": res, "suggest": sug, "_used_or": used_or}


# ------------------------------------------------------------------ CLI
def cli(argv):
    if not argv:
        print("usage: engine.py <query words> [-n N]")
        return 2
    n = 10
    if "-n" in argv:
        i = argv.index("-n")
        n = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    q = " ".join(argv)
    if not DB_PATH.exists():
        print("No index yet. Build it with:  python3 tools/search/build_index.py")
        return 1
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    out = search(q, n=n, prefix=False)
    if not out["results"]:
        print("No results for: " + q)
    for i, r in enumerate(out["results"], 1):
        loc = r["path"]
        if r["source"] == "so":
            loc = "stackoverflow qid " + loc
        elif r["source"] == "cppref":
            loc = "6_reference/cppreference/reference/" + loc
        sn = r["snippet"].replace(HL_A, "[").replace(HL_B, "]")[:150]
        extra = "  (score %s)" % r["score"] if r["source"] == "so" else ""
        print("%2d. [%s] %s%s" % (i, r["source"], r["title"], extra))
        print("      " + loc)
        if sn:
            print("      " + sn)
    if out.get("corrected_from"):
        print()
        print("Showing results for: " + out["q"] + "   (typed: " + out["corrected_from"] + ")")
    if out["suggest"]:
        print("\nDid you mean: " + out["suggest"])
    return 0


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]))
