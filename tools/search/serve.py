#!/usr/bin/env python3
"""Local offline search server for the exam kit (127.0.0.1 only).

    python3 tools/search/serve.py [--port 8090] [--no-browser]

Python 3.8+, standard library only.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import html
import json
import mimetypes
import os
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

KIT = engine.KIT
REF_ROOT = KIT / "6_reference" / "cppreference" / "reference"
QA = KIT / "7_stackoverflow" / "qa.jsonl"

mimetypes.add_type("text/plain; charset=utf-8", ".md")
mimetypes.add_type("text/plain; charset=utf-8", ".cpp")
mimetypes.add_type("text/plain; charset=utf-8", ".h")
mimetypes.add_type("text/plain; charset=utf-8", ".hpp")
mimetypes.add_type("text/plain; charset=utf-8", ".txt")
mimetypes.add_type("text/plain; charset=utf-8", ".py")
mimetypes.add_type("text/plain; charset=utf-8", ".yaml")

_CSS = """
:root{--ground:#e7e8e3;--surface:#f5f5f2;--ink:#121314;--muted:#4b4f55;--signal:#f5c518}
@media (prefers-color-scheme:dark){:root{--ground:#0e0f11;--surface:#17191c;--ink:#ecede7;--muted:#a2a6ac}}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
code,pre,kbd{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono",monospace}
a{color:var(--ink)}
mark{background:var(--signal);color:#121314;padding:0 1px}
"""

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Deep search · Post-Apo C++</title>
<style>__CSS__
.wrap{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:15px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.08em}
.top{position:sticky;top:0;background:var(--ground);padding:12px 0 8px;z-index:2}
#q{width:100%;font:inherit;font-size:18px;padding:10px 12px;border:2px solid var(--ink);background:var(--surface);color:var(--ink);border-radius:0;outline:none}
#q:focus{box-shadow:4px 4px 0 var(--signal)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.chip{font:inherit;font-size:13px;padding:3px 10px;border:2px solid var(--ink);background:var(--surface);color:var(--ink);border-radius:0;cursor:pointer}
.chip.on{background:var(--signal);color:#121314;font-weight:700}
#dym{margin:10px 0;color:var(--muted)}
#dym a{font-weight:700;cursor:pointer}
#meta{color:var(--muted);font-size:12px;margin:8px 0}
.res{display:block;text-decoration:none;color:inherit;background:var(--surface);border:2px solid var(--ink);padding:8px 10px;margin:0 0 8px}
.res.sel{outline:3px solid var(--signal);outline-offset:1px;box-shadow:4px 4px 0 var(--ink)}
.res:hover{box-shadow:4px 4px 0 var(--ink)}
.row{display:flex;gap:8px;align-items:baseline}
.src{font-size:11px;font-weight:700;letter-spacing:.06em;padding:1px 6px;border:2px solid var(--ink);flex:none}
.src.fn,.src.kit{background:var(--signal);color:#121314}
.ttl{font-weight:700;overflow-wrap:anywhere;flex:1}
.sc{font-size:12px;color:var(--muted);flex:none;font-family:ui-monospace,monospace}
.sn{color:var(--muted);font-size:13px;margin-top:3px;overflow-wrap:anywhere}
.hint{color:var(--muted);font-size:12px;margin-top:20px}
kbd{border:1px solid var(--muted);padding:0 4px;font-size:11px}
</style></head><body><div class="wrap">
<div class="top"><h1><a href="/kit/START_HERE.html" target="pac-kit" style="color:inherit;text-decoration:none">&larr; Post-Apo C++</a> / deep search</h1>
<input id="q" type="search" autocomplete="off" spellcheck="false" autofocus placeholder="pop_back, erase while iterating, priority_queue min heap ...">
<div class="chips" id="chips"></div></div>
<div id="dym"></div><div id="meta"></div><div id="out"></div>
<p class="hint"><kbd>/</kbd> focus &nbsp; <kbd>&uarr;</kbd><kbd>&darr;</kbd> select &nbsp; <kbd>Enter</kbd> open &nbsp; <a href="/kit/START_HERE.html">START_HERE</a></p>
</div><script>window.name="pac-search";
const SRC=[["all","All"],["kit","Kit"],["fn","Functions"],["cppref","cppreference"],["so","Stack Overflow"]];
const LABEL={kit:"KIT",fn:"FN",cppref:"REF",so:"SO"};
const q=document.getElementById("q"),out=document.getElementById("out"),meta=document.getElementById("meta"),dym=document.getElementById("dym"),chips=document.getElementById("chips");
let src="all",sel=-1,seq=0,timer=null,items=[];
const esc=s=>s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
const hl=s=>esc(s).replace(/\\x02/g,"<mark>").replace(/\\x03/g,"</mark>");
SRC.forEach(([k,l])=>{const b=document.createElement("button");b.className="chip"+(k===src?" on":"");b.textContent=l;b.type="button";
 b.onclick=()=>{src=k;[...chips.children].forEach(c=>c.classList.toggle("on",c===b));run();q.focus()};chips.appendChild(b)});
function render(d){
 items=d.results;sel=items.length?0:-1;
 out.innerHTML=items.map((r,i)=>`<a class="res${i===sel?" sel":""}" href="${esc(r.url)}" data-i="${i}"><div class="row"><span class="src ${r.source}">${LABEL[r.source]}</span><span class="ttl">${esc(r.title)}</span>${r.source==="so"?`<span class="sc">&#9650; ${r.score}</span>`:""}</div>${r.snippet?`<div class="sn">${hl(r.snippet)}</div>`:""}</a>`).join("");
 meta.textContent=q.value.trim()?items.length+" result"+(items.length===1?"":"s"):"";
 if(d.corrected_from){dym.innerHTML='Showing results for <b>'+esc(d.q)+'</b>. Typed: <a>'+esc(d.corrected_from)+'</a>';dym.firstElementChild.nextElementSibling.onclick=()=>{q.value=d.q;run();q.focus()}}
 else if(d.suggest){dym.innerHTML='Did you mean: <a>'+esc(d.suggest)+'</a>';dym.firstElementChild.onclick=()=>{q.value=d.suggest;run();q.focus()}}else dym.innerHTML="";
}
async function run(){
 const v=q.value.trim();try{history.replaceState(null,"","?q="+encodeURIComponent(v)+(src!=="all"?"&src="+src:""))}catch(e){}
 if(!v){out.innerHTML="";meta.textContent="";dym.innerHTML="";items=[];return}
 const my=++seq;
 try{const r=await fetch("/api?q="+encodeURIComponent(q.value)+"&src="+src+"&n=30");const d=await r.json();if(my===seq)render(d)}catch(e){meta.textContent="search failed"}
}
function mark(){[...out.children].forEach((c,i)=>c.classList.toggle("sel",i===sel));if(out.children[sel])out.children[sel].scrollIntoView({block:"nearest"})}
q.addEventListener("input",()=>{clearTimeout(timer);timer=setTimeout(run,150)});
document.addEventListener("keydown",e=>{
 if(e.key==="/"&&document.activeElement!==q){e.preventDefault();q.focus();q.select();return}
 if(e.key==="ArrowDown"){e.preventDefault();if(sel<items.length-1){sel++;mark()}}
 else if(e.key==="ArrowUp"){e.preventDefault();if(sel>0){sel--;mark()}}
 else if(e.key==="Enter"&&items[sel]&&(document.activeElement===q||document.activeElement===document.body)){e.preventDefault();location.href=items[sel].url}
 else if(e.key==="Escape"){q.value="";run();q.focus()}
});
const p=new URLSearchParams(location.search);
if(p.get("src")){src=p.get("src");[...chips.children].forEach((c,i)=>c.classList.toggle("on",SRC[i][0]===src))}
if(p.get("q")){q.value=p.get("q");run()}
</script></body></html>""".replace("__CSS__", _CSS)

_SCRIPT_RE = re.compile(r"<script\b.*?</script\s*>|<script\b[^>]*>", re.I | re.S)
_ON_RE = re.compile(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
_JSURL_RE = re.compile(r"(href|src)\s*=\s*([\"']?)\s*javascript:", re.I)


_LOCAL_QIDS = None


def _local_qids():
    """qids of the Stack Overflow questions that are on the drive (cached)."""
    global _LOCAL_QIDS
    if _LOCAL_QIDS is None:
        try:
            con = engine.connect()
            _LOCAL_QIDS = {str(r[0]) for r in con.execute("SELECT url_or_path FROM docs WHERE source='so'")}
            con.close()
        except Exception:
            _LOCAL_QIDS = set()
    return _LOCAL_QIDS


_HREF_RE = re.compile(r'<a\s+([^>]*?)href="([^"]*)"([^>]*)>', re.I)
_SOQ_RE = re.compile(r'^(?:https?:)?(?://(?:www\.)?stackoverflow\.com)?/(?:questions|q)/(\d+)', re.I)


def fix_links(s):
    """Links inside Q&As: a question we have -> local /so/<qid>; everything else -> its real web
    address, dimmed and marked 'needs internet' (instead of a local 'not found')."""
    local = _local_qids()

    def repl(m):
        pre, href, post = m.group(1), m.group(2), m.group(3)
        q = _SOQ_RE.match(href)
        if q and q.group(1) in local:
            return '<a %shref="/so/%s"%s>' % (pre, q.group(1), post)
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://stackoverflow.com" + href
        if href.startswith("http"):
            return ('<a %shref="%s" class="web" title="Not on the drive: needs internet"%s>'
                    % (pre, href.replace('"', "%22"), post))
        return m.group(0)
    return _HREF_RE.sub(repl, s)


def clean_html(s):
    s = _SCRIPT_RE.sub("", s or "")
    s = _ON_RE.sub("", s)
    return fix_links(_JSURL_RE.sub(r"\1=\2#blocked:", s))


def load_so(qid):
    """Return (list of rows for the question) or [] ."""
    from_idx = []
    try:
        con = engine.connect()
        r = con.execute("SELECT extra FROM docs WHERE source='so' AND url_or_path=?", (qid,)).fetchone()
        con.close()
        if r:
            from_idx = json.loads(r["extra"]).get("offs", [])
    except Exception:
        pass
    rows = []
    if not QA.exists():
        return rows
    with open(QA, "rb") as f:
        for off in from_idx:
            try:
                f.seek(off)
                d = json.loads(f.readline().decode("utf-8", errors="replace"))
                if str(d.get("qid")) == qid:
                    rows.append(d)
            except ValueError:
                pass
        if not rows:                                   # offsets stale: scan
            f.seek(0)
            for line in f:
                if qid.encode() in line:
                    try:
                        d = json.loads(line.decode("utf-8", errors="replace"))
                    except ValueError:
                        continue
                    if str(d.get("qid")) == qid:
                        rows.append(d)
    return rows


SO_CSS = _CSS + """
.wrap{max-width:860px;margin:0 auto;padding:16px}
a.web{opacity:.55;text-decoration-style:dashed}
a.web::after{content:" \\2197";font-size:.8em}
.bar a{font-size:13px}
h1{font-size:24px;line-height:1.2;margin:12px 0 6px}
.tags span{display:inline-block;border:2px solid var(--ink);padding:0 6px;font-size:12px;margin:0 4px 4px 0;background:var(--surface)}
.box{background:var(--surface);border:2px solid var(--ink);padding:4px 14px 10px;margin:12px 0;overflow-x:auto}
.box img{max-width:100%}
pre{background:var(--ground);border:2px solid var(--ink);padding:10px;overflow-x:auto;font-size:13px;line-height:1.4}
code{background:var(--ground);padding:0 3px;font-size:.92em}
pre code{background:none;padding:0}
.badge{display:inline-block;background:var(--signal);color:#121314;font-weight:700;border:2px solid var(--ink);padding:0 8px;font-size:12px}
.sc{font-family:ui-monospace,monospace;color:var(--muted)}
.attr{color:var(--muted);font-size:13px;border-top:2px solid var(--ink);margin-top:24px;padding-top:8px;overflow-wrap:anywhere}
blockquote{border-left:4px solid var(--muted);margin:8px 0;padding:0 12px;color:var(--muted)}
"""


def so_page(qid):
    rows = load_so(qid)
    if not rows:
        return None
    q = rows[0]
    rows.sort(key=lambda d: (not d.get("accepted"), -(d.get("a_score") or 0)))
    e = lambda x: html.escape(str(x if x is not None else ""))
    tags = "".join("<span>%s</span>" % e(t) for t in (q.get("tags") or []))
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             '<title>%s</title><style>%s</style></head><body><div class="wrap">' % (e(q.get("title")), SO_CSS),
             '<div class="bar"><a href="/">&larr; search</a></div>',
             '<h1>%s</h1><div class="tags">%s</div><div class="sc">question score %s</div>' % (e(q.get("title")), tags, e(q.get("score"))),
             '<div class="box">%s</div>' % clean_html(q.get("q_html"))]
    authors = []
    for d in rows:
        badge = '<span class="badge">ACCEPTED</span> ' if d.get("accepted") else ""
        parts.append('<h2 style="font-size:16px;margin:20px 0 0">%sAnswer <span class="sc">score %s, by %s</span></h2><div class="box">%s</div>'
                     % (badge, e(d.get("a_score")), e(d.get("a_author")), clean_html(d.get("a_html"))))
        authors.append(str(d.get("a_author") or ""))
    link = q.get("link") or ""
    names = ", ".join(dict.fromkeys(a for a in authors if a)) or "?"
    parts.append('<div class="attr">From Stack Overflow, by %s / %s, CC BY-SA, %s <a href="%s">%s</a></div></div></body></html>'
                 % (e(q.get("q_author")), e(names), e(link), e(link), e(link)))
    return "".join(parts).encode("utf-8")


def safe_path(root, rel):
    root = os.path.realpath(str(root))
    p = os.path.realpath(os.path.join(root, *[x for x in rel.replace("\\", "/").split("/") if x]))
    try:
        if os.path.commonpath([root, p]) != root:
            return None
    except ValueError:
        return None
    return p


class Handler(BaseHTTPRequestHandler):
    server_version = "KitSearch"

    def log_message(self, fmt, *a):
        pass

    def send(self, code, body, ctype="text/html; charset=utf-8", head=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def static(self, root, rel, head=False):
        p = safe_path(root, rel)
        if not p or not os.path.exists(p):
            return self.send(404, b"not found", "text/plain", head)
        if os.path.isdir(p):
            idx = os.path.join(p, "index.html")
            if not os.path.isfile(idx):
                return self.send(404, b"not found", "text/plain", head)
            p = idx
        ctype = mimetypes.guess_type(p)[0] or "application/octet-stream"
        try:
            with open(p, "rb") as f:
                data = f.read()
        except OSError:
            return self.send(404, b"not found", "text/plain", head)
        self.send(200, data, ctype, head)

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        u = urlparse(self.path)
        path = unquote(u.path)
        try:
            if path in ("/", "/index.html"):
                return self.send(200, PAGE.encode("utf-8"), head=head)
            if path == "/api":
                qs = parse_qs(u.query)
                q = (qs.get("q") or [""])[0][:300]
                src = (qs.get("src") or ["all"])[0]
                try:
                    n = max(1, min(100, int((qs.get("n") or ["30"])[0])))
                except ValueError:
                    n = 30
                data = engine.search(q, src, n, prefix=True)
                return self.send(200, json.dumps(data).encode("utf-8"), "application/json; charset=utf-8", head)
            if path.startswith("/so/"):
                body = so_page(path[4:].strip("/"))
                if body is None:
                    return self.send(404, b"Stack Overflow entry not found (qa.jsonl missing?)", "text/plain", head)
                return self.send(200, body, head=head)
            if path.startswith("/ref/"):
                return self.static(REF_ROOT, path[5:], head)
            if path.startswith("/kit/"):
                return self.static(KIT, path[5:], head)
            self.send(404, b"not found", "text/plain", head)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as ex:                          # keep the server alive
            try:
                self.send(500, ("error: %s" % ex).encode("utf-8"), "text/plain", head)
            except Exception:
                pass


def main():
    ap = argparse.ArgumentParser(description="Offline exam-kit search server")
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    if not engine.DB_PATH.exists():
        print("Search index not found: %s" % engine.DB_PATH)
        print("Build it first:  python3 tools/search/build_index.py")
        return 1
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    except OSError as ex:
        print("Cannot listen on 127.0.0.1:%d (%s). Try --port %d" % (a.port, ex, a.port + 1))
        return 1
    url = "http://127.0.0.1:%d/" % a.port
    print("Kit search running at " + url + "   (Ctrl+C to stop)")
    sys.stdout.flush()
    if not a.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
