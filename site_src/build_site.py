"""Build START_HERE.html for Post-Apocalyptic C++: one self-contained page that works
offline (from a drive) and online (GitHub Pages). Styled with Holding Point, the design
system of leongorecki.eu (tokens + components + fonts are inlined, nothing is fetched).

Sources (single source of truth, also searched by tools/find.sh):
  1_cheatsheet/*.md, 2_snippets/*.cpp + README.md, 3_solved_exams/, site_src/content_algorithms.py
Run from anywhere:  python site_src/build_site.py
"""
import base64, html, json, re, textwrap
from pathlib import Path

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CMakeLexer, CppLexer, TextLexer

from content_algorithms import ALGOS, CONTAINERS, DECISION, PATTERNS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "START_HERE.html"
NAME = "Post-Apocalyptic C++"
REPO = "https://github.com/leo-01000111/Post-Apo-C-plus-plus"
SITE = "https://www.leongorecki.eu/"
COURSE_REPO = "https://github.com/oKermorgant/ecn_arpro/blob/master/"

PAGES = [  # id, label
    ("home", "Home"), ("cpp", "C++"), ("stl", "STL"), ("errors", "Errors & debug"),
    ("algo", "Algorithms"), ("snippets", "Snippets"), ("exams", "Solved exams"), ("course", "Course files"),
]
INDEX = []


# ---------------------------------------------------------------- helpers
def arrow(deg=0):
    return ('<svg class="arr" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><g transform="rotate(%d 12 12)" '
            'fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="square" stroke-linejoin="miter">'
            '<path d="M3.5 12H18.5"></path><path d="M12 5.2L18.8 12L12 18.8"></path></g></svg>' % deg)


_mk = [0]


def marking(kind="centerline", label=""):
    _mk[0] += 1
    pid = f"hp-mk-{_mk[0]}"
    if kind == "centerline":
        svg = (f'<svg class="hp-marking" width="100%" height="28" aria-hidden="true" focusable="false"><defs>'
               f'<pattern id="{pid}" width="36" height="28" patternUnits="userSpaceOnUse"><rect class="edge" x="0.5" y="11.5" '
               f'width="20" height="5" fill="currentColor" stroke-width="1"></rect></pattern></defs>'
               f'<rect x="0" y="0" width="100%" height="28" fill="url(#{pid})"></rect></svg>')
    else:
        svg = (f'<svg class="hp-marking" width="100%" height="28" aria-hidden="true" focusable="false"><defs>'
               f'<pattern id="{pid}" width="40" height="28" patternUnits="userSpaceOnUse">'
               f'<rect class="edge" x="0.5" y="16.5" width="23" height="4" fill="currentColor" stroke-width="1"></rect>'
               f'<rect class="edge" x="0.5" y="22.5" width="23" height="4" fill="currentColor" stroke-width="1"></rect></pattern></defs>'
               f'<rect class="edge" x="0.5" y="2.5" width="100%" height="4" fill="currentColor" stroke-width="1"></rect>'
               f'<rect class="edge" x="0.5" y="8.5" width="100%" height="4" fill="currentColor" stroke-width="1"></rect>'
               f'<rect x="0" y="0" width="100%" height="28" fill="url(#{pid})"></rect></svg>')
    if label:
        return (f'<div role="separator" aria-label="{html.escape(label)}" class="hp-marking-wrap marking-gap">{svg}'
                f'<span class="label">{html.escape(label)}</span></div>')
    return f'<div role="separator" class="marking-gap">{svg}</div>'


def slug(s):
    s = re.sub(r"<[^>]+>|`", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48] or "x"


def plain(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def md(text):
    return markdown.markdown(text, extensions=["fenced_code", "tables", "codehilite", "sane_lists"],
                             extension_configs={"codehilite": {"css_class": "hl", "guess_lang": False}})


def hl_cpp(code, **kw):
    return highlight(code, CppLexer(), HtmlFormatter(cssclass="hl", **kw))


def add_index(page, cid, title, body_html, kind="card"):
    INDEX.append({"p": page, "id": cid, "t": plain(title), "k": kind, "x": plain(body_html)[:500].lower()})


def card(page, title, body, cid=None, cls="", kicker=""):
    cid = cid or f"{page}-{slug(title)}"
    add_index(page, cid, title, body)
    k = f'<span class="k">{kicker}</span>' if kicker else ""
    return (f'<section class="card {cls}" id="{cid}"><h3 class="card-h">{k}<span>{title}</span>'
            f'<a href="#{page}/{cid}" class="anchor" title="Link to this card">LINK</a></h3>'
            f'<div class="card-b">{body}</div></section>')


def btn(label, href="", variant="ghost", deg=None, size="sm", attrs=""):
    a = arrow(deg) if deg is not None else ""
    pre, post = (a, "") if deg in (180, 225, 135) else ("", a)
    cls = f"hp-btn hp-btn--{variant}" + (" hp-btn--sm" if size == "sm" else "")
    if href:
        return f'<a class="{cls}" href="{href}"{attrs}>{pre}<span>{label}</span>{post}</a>'
    return f'<button type="button" class="{cls}"{attrs}>{pre}<span>{label}</span>{post}</button>'


def code_title(t):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(t, quote=False))


def md_cards(page, path, skip_h2=()):
    """Split a markdown file into cards at each '## ' heading (big tables get full width)."""
    lines, chunks, cur, intro, in_code = path.read_text(encoding="utf-8").splitlines(), [], None, [], False
    for ln in lines:
        if ln.startswith("```"):
            in_code = not in_code
        if not in_code and ln.startswith("# ") and cur is None and not chunks:
            continue
        if not in_code and ln.startswith("## "):
            cur = [ln[3:].strip(), []]
            chunks.append(cur)
        elif cur is None:
            intro.append(ln)
        else:
            cur[1].append(ln)
    out, cards, wide = [], [], []
    if "\n".join(intro).strip():
        out.append(f'<div class="lead">{md(chr(10).join(intro).strip())}</div>')
    for title, body in chunks:
        if title in skip_h2:
            continue
        body_html = md("\n".join(body))
        target = wide if ("<table" in body_html and body_html.count("<tr") > 6) else cards
        target.append(card(page, code_title(title), body_html, cls="wide" if target is wide else ""))
    out.append("".join(wide) + '<div class="cards">' + "".join(cards) + "</div>")
    return "".join(out)


def lamp(state, word):
    return f'<span class="hp-lamp hp-lamp--{state}"><i aria-hidden="true"></i><span>{word}</span></span>'


# local-only links: data-online gives the online replacement (or "" = only on the drive)
def flink(href, label, online=None, variant="ghost"):
    extra = ""
    if online is not None:
        extra = f' data-online="{online}"' + ("" if online else ' data-local-only="1"')
    return btn(label, href, variant, 0, attrs=extra)


# ---------------------------------------------------------------- pages
def page_home():
    items, cur = [], None
    for ln in (ROOT / "1_cheatsheet/my_mistakes.md").read_text(encoding="utf-8").splitlines():
        if ln.startswith("- "):
            cur = [ln[2:]]
            items.append(cur)
        elif cur is not None and (ln.startswith("  ") or not ln.strip()):
            cur.append(ln[2:] if ln.startswith("  ") else "")
    mcards = []
    for n, it in enumerate(items, 1):
        txt = "\n".join(it).strip()
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)", txt, re.S)
        title, rest = (m.group(1), m.group(2)) if m else (txt[:60], txt)
        mcards.append(card("home", code_title(title.rstrip(":.")), md(rest), cls="mistake", kicker=f"Mistake {n:02d}"))

    routine = [
        ("00-10 min", "Read the whole subject. Note every TODO and its order."),
        ("00-10 min", "Build the untouched project (bash tools/build.sh dir). It must compile before you touch it."),
        ("00-10 min", "git init && git add -A && git commit -qm start"),
        ("10-110 min", "TODOs in the subject's order. Translate the pseudocode line by line."),
        ("10-110 min", "Commit after every method that works (git commit -qam \"prune ok\")."),
        ("10-110 min", "Stuck for more than 10 min: move to the next TODO, come back later."),
        ("110-120 min", "Make sure it compiles. Comment out anything broken. Final commit."),
    ]
    checklist = "".join(f'<label class="chk"><input type="checkbox" data-k="r{i}"><span class="when">{w}</span>'
                        f'<span>{html.escape(t)}</span></label>' for i, (w, t) in enumerate(routine))
    add_index("home", "home-routine", "Exam routine checklist", " ".join(t for _, t in routine))
    add_index("home", "home-timer", "Exam timer (2 h)", "timer start 08:00 elapsed left phase")

    links = "".join([
        flink("4_course/subjects/sudoku_exam.pdf", "Sudoku exam", COURSE_REPO + "sudoku/subject/sudoku.pdf"),
        flink("4_course/subjects/maze_exam.pdf", "Maze exam", COURSE_REPO + "maze/subject/ARPRO_maze.pdf"),
        flink("4_course/subjects/open_projects.pdf", "Open projects", COURSE_REPO + "open_projects/open_projects.pdf"),
        flink("4_course/slides/okRobotProgramming.pdf", "C++ slides", ""),
        flink("6_reference/cppreference/reference/en/index.html", "cppreference", "https://en.cppreference.com/w/"),
    ])
    return f"""
<div class="hero">
  <div>
    <span class="label">ARPRO &middot; Centrale Nantes &middot; C++17</span>
    <h1>{NAME}</h1>
    <p class="lede">An offline C++ kit for the ARPRO exam: cheat-sheets, algorithm templates, my own mistakes and a solved past exam, searchable in one page. Built to work when there is no internet left.</p>
    <div class="row">{btn("Search everything", variant="primary", deg=0, size="lg", attrs=" data-open-palette")}
      {btn("Which algorithm", "#algo", "secondary", 0, size="lg")}</div>
  </div>
  <div class="hero-minor">
    <section class="card" id="home-timer"><h3 class="card-h"><span class="k">2 h</span><span>Exam timer</span></h3>
      <div class="card-b">
        <div class="t-big"><span><span class="label">Elapsed</span><br><b id="t-elapsed">0:00</b></span><span><span class="label">Left</span><br><b id="t-left">2:00</b></span></div>
        <div class="t-bar"><div class="t-ph p1" title="Read + build">Read</div><div class="t-ph p2" title="TODOs">TODOs</div><div class="t-ph p3" title="Compile + commit">End</div><div id="t-fill"></div></div>
        <div class="row">{btn("Start now", variant="secondary", attrs=' id="t-start"')}{btn("Started 08:00", variant="ghost", attrs=' id="t-08"')}{btn("Reset", variant="ghost", attrs=' id="t-reset"')}</div>
        <p class="small muted" id="t-phase" style="margin:12px 0 0">Not started.</p>
      </div></section>
  </div>
</div>
<div class="home-grid">
  <section class="card" id="home-routine"><h3 class="card-h"><span class="k">Checklist</span><span>Routine</span></h3>
    <div class="card-b checklist">{checklist}<div class="row" style="margin-top:12px">{btn("Uncheck all", variant="ghost", attrs=' id="chk-reset"')}</div></div></section>
  <div class="stack">
    <section class="card" id="home-links"><h3 class="card-h"><span class="k">Open</span><span>Quick open</span></h3>
      <div class="card-b"><div class="links">{links}</div>
      <p class="small muted local-note" data-online-note hidden>Online: exam subjects open from the course repo and cppreference from the web. Slides live on the drive only.</p></div></section>
  </div>
</div>
{marking("holding", "Hold short · read first")}
<h2 class="sec-h hold-head">My own mistakes <span class="label">from practice</span></h2>
<div class="cards">{''.join(mcards)}</div>
{marking("centerline")}
<h2 class="sec-h">Routine details</h2>
""" + md_cards("home", ROOT / "1_cheatsheet/exam_routine.md", skip_h2=("Exam routine",))


def page_stl():
    lab = {"1": ("go", "O(1)"), "1*": ("go", "O(1)*"), "top 1": ("go", "top O(1)"), "front 1": ("go", "front O(1)"),
           "pop 1": ("go", "pop O(1)"), "log": ("caution", "O(log n)"), "pop log": ("caution", "pop O(log n)"),
           "n": ("hold", "O(n)"), "-": ("off", "n/a")}
    rows = "".join(f"<tr><th><code>{c}</code></th>" + "".join(f"<td>{lamp(*lab.get(x, ('off', x)))}</td>" for x in r)
                   + f"<td class='muted'>{note}</td></tr>" for c, *r, note in CONTAINERS)
    table = (f'<table class="cx"><thead><tr><th>Container</th><th>Access [i]</th><th>Add at end</th><th>Insert middle</th>'
             f'<th>Find</th><th>Erase</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table>'
             f'<p class="small muted">* amortised. unordered_* are average case. Green lamp = cheap, yellow = fine, red = careful inside loops.</p>')
    return (card("stl", "Which container", table, cid="stl-complexity", cls="wide", kicker="Complexity")
            + md_cards("stl", ROOT / "1_cheatsheet/stl_quickref.md"))


def page_algo():
    rows = "".join(
        f'<div class="dec"><span class="q">{html.escape(q)}</span>'
        f'<a class="hp-sign hp-sign--direction hp-sign--sm" href="#algo/algo-{aid}"><span>{html.escape(a)}</span>{arrow(0)}</a>'
        f'<span class="why">{html.escape(w)}</span></div>' for q, a, aid, w in DECISION)
    add_index("algo", "algo-decide", "Which algorithm (decision guide)", " ".join(q + " " + a for q, a, _, _ in DECISION))
    out = [card("algo", "Which algorithm", f'<div class="decide">{rows}</div>', cid="algo-decide", cls="wide", kicker="Decide")]
    out.append('<div class="cards two">' + "".join(
        card("algo", t, "<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in xs) + "</ul>", kicker="Pattern")
        for t, xs in PATTERNS) + "</div>")
    for n, a in enumerate(ALGOS, 1):
        pseudo = highlight(a["pseudo"], TextLexer(), HtmlFormatter(cssclass="hl pseudo"))
        pseudo = re.sub(r"(//[^\n<]*)", r'<span class="c1">\1</span>', pseudo)
        impl = "".join(f"<li>{html.escape(x)}</li>" for x in a["implement"])
        bugs = "".join(f"<li>{html.escape(x)}</li>" for x in a["bugs"])
        body = (f'<div class="algo-grid"><div>{pseudo}</div><div>'
                f'<div class="meta-row"><span class="hp-tag">{html.escape(a["exam"])}</span>'
                f'{btn("Snippet", "#snippets/snip-" + a["snippet"], "ghost", 0)}</div>'
                f'<h4>You implement</h4><ul class="ok">{impl}</ul>'
                f'<h4>Classic bugs</h4><ul class="bad">{bugs}</ul>'
                f'<p class="small muted">{html.escape(a["cost"])}</p></div></div>')
        out.append(card("algo", a["name"], body, cid=f"algo-{a['id']}", cls="wide", kicker=f'<span class="idx">{n:02d}</span>'))
    return "".join(out)


FN_RE = re.compile(r"^(?:\s{0,4})(?:template\s*<[^>]*>\s*)?(?:(?:static|inline|constexpr|virtual)\s+)*"
                   r"[A-Za-z_][\w:<>,\s\*&]*?[\s\*&](?:[A-Za-z_]\w*::)*([A-Za-z_]\w*)\s*\([^;{]*\)\s*(?:const\s*)?(?:override\s*)?\{?\s*$")
FN2_RE = re.compile(r"^\s{0,4}(?:(?:static|inline|constexpr)\s+)*[A-Za-z_][\w:<>,\s\*&]*?[\s\*&]"
                    r"([A-Za-z_]\w*)\s*\([^;{)=]*,\s*$")
TYPE_RE = re.compile(r"^\s{0,4}(?:template\s*<[^>]*>\s*)?(struct|class)\s+([A-Za-z_]\w*)\b(?!.*;\s*$)")
SKIP = {"if", "for", "while", "switch", "return", "main", "else", "catch", "sizeof", "operator"}


def snippet_block(page, cid, title, desc, path):
    code = path.read_text(encoding="utf-8")
    lines = code.splitlines()
    adapt = [i + 1 for i, l in enumerate(lines) if "ADAPT" in l]
    chips, seen = [], set()
    for i, l in enumerate(lines, 1):
        if l.lstrip().startswith(("//", "#", "*", "return", "else")):
            continue
        m = TYPE_RE.match(l)
        name, kind = (m.group(2), "type") if m else (None, "fn")
        if not name:
            m = FN_RE.match(l) or FN2_RE.match(l)
            name = m.group(1) if m and "=" not in l.split("(")[0] else None
        if name and name not in SKIP and name not in seen:
            seen.add(name)
            chips.append((name, i, kind))
            INDEX.append({"p": page, "id": f"{cid}-L-{i}", "t": f"{name}  ({path.name}:{i})", "k": "code", "x": l.strip().lower()[:200]})
    chip_html = "".join(f'<li><a class="hp-tag {k}" href="#{page}/{cid}-L-{i}">{html.escape(n)}</a></li>' for n, i, k in chips)
    add_index(page, cid, title, desc)
    adapt_note = f'<span class="hp-tag hp-tag--solid">{len(adapt)} ADAPT lines</span>' if adapt else ""
    return (f'<details class="card wide snip" id="{cid}"><summary class="card-h"><span class="tw">{title}</span>'
            f'<span class="label">{html.escape(path.name)} &middot; {len(lines)} lines</span></summary>'
            f'<div class="card-b"><p>{desc}</p><div class="meta-row">{adapt_note}</div><ul class="chips">{chip_html}</ul>'
            f'<div class="codewrap">{hl_cpp(code, linenos="inline", lineanchors=f"{cid}-L", hl_lines=adapt)}</div></div></details>')


NICE = {"backtracking.cpp": "Backtracking — N-queens", "astar.cpp": "A* search — 8-puzzle and ecn::Astar",
        "bfs_dfs.cpp": "BFS, DFS and flood fill", "minimax_alphabeta.cpp": "Minimax with alpha-beta — Nim, Connect Four",
        "genetic_algorithm.cpp": "Genetic algorithm — TSP", "containers_tricks.cpp": "Container tricks",
        "random_timing.cpp": "Random numbers and timing", "recursion.cpp": "Recursion and memoisation"}


def page_snippets():
    descs = {}
    for ln in (ROOT / "2_snippets/README.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"- `([^`]+)` - (.*)", ln)
        if m:
            descs[m.group(1)] = md(m.group(2))[3:-4]
    out = ['<p class="lead">Every file compiles on its own: <code>g++ -std=c++17 -Wall -Wextra -O2 f.cpp</code>. '
           'Click a function to jump to it. Highlighted lines are marked <code>ADAPT:</code>, the parts you change.</p>']
    for f in NICE:
        out.append(snippet_block("snippets", f"snip-{f[:-4]}", NICE[f], descs.get(f, ""), ROOT / "2_snippets" / f))
    cm = (ROOT / "2_snippets/CMakeLists_template.txt").read_text(encoding="utf-8")
    out.append(card("snippets", "CMakeLists template", highlight(cm, CMakeLexer(), HtmlFormatter(cssclass="hl")),
                    cid="snip-cmake", cls="wide", kicker="Build"))
    return "".join(out)


def page_exams():
    base = ROOT / "3_solved_exams/sudoku"
    intro = ('<p class="lead">My own solution, written and debugged during practice. Subject: '
             f'<a href="4_course/subjects/sudoku_exam.pdf" data-online="{COURSE_REPO}sudoku/subject/sudoku.pdf">sudoku_exam.pdf</a>.</p>')
    return intro + "".join([
        snippet_block("exams", "ex-sudoku-cell", "Sudoku — Cell: prune, restore, set, cancel",
                      "Bookkeeping with <code>pruned_count_</code> so restore only re-adds a digit when no neighbour forbids it.",
                      base / "src/cell.cpp"),
        snippet_block("exams", "ex-sudoku-grid", "Sudoku — Grid: constructor, backtracking, bestNextCell",
                      "Backtracking loop and the most-constrained-cell comparator.", base / "src/grid.cpp"),
        snippet_block("exams", "ex-sudoku-cellh", "Sudoku — cell.h (given)", "The provided class declaration.",
                      base / "include/sudoku/cell.h")])


def page_course():
    groups = [
        ("Exam subjects", [("4_course/subjects/sudoku_exam.pdf", "Sudoku exam", COURSE_REPO + "sudoku/subject/sudoku.pdf"),
                           ("4_course/subjects/maze_exam.pdf", "Maze exam", COURSE_REPO + "maze/subject/ARPRO_maze.pdf"),
                           ("4_course/subjects/mobile_robot_lab2.pdf", "Mobile robot lab", COURSE_REPO + "mobile_robot/subject/ARPRO_lab2.pdf"),
                           ("4_course/subjects/open_projects.pdf", "Open projects", COURSE_REPO + "open_projects/open_projects.pdf")]),
        ("Slides", [("4_course/slides/okRobotProgramming.pdf", "C++ slides", ""),
                    ("4_course/slides/okRobotProgrammingPython.pdf", "Python slides", ""),
                    ("4_course/slides/ARPRO_IRP_GG_file_I.pdf", "Industrial robot prog. I", ""),
                    ("4_course/slides/ARPRO_IRP_GG_file_II.pdf", "Industrial robot prog. II", ""),
                    ("4_course/slides/ARPRO_IRP_GG_file_III.pdf", "Industrial robot prog. III", "")]),
        ("Reference", [("6_reference/cppreference/reference/en/index.html", "cppreference", "https://en.cppreference.com/w/"),
                       ("6_reference/cppreference/reference/en/cpp/container.html", "Containers", "https://en.cppreference.com/w/cpp/container"),
                       ("6_reference/cppreference/reference/en/cpp/algorithm.html", "Algorithms", "https://en.cppreference.com/w/cpp/algorithm"),
                       ("5_repo/ecn_arpro", "Course repo", "https://github.com/oKermorgant/ecn_arpro")]),
    ]
    cs = "".join(card("course", g, '<div class="links">' + "".join(flink(h, t, o) for h, t, o in items) + "</div>", kicker="Files")
                 for g, items in groups)
    tip = card("course", "Terminal tools", md(textwrap.dedent("""\
        ```bash
        cd ~/Post-Apo-C-plus-plus
        bash tools/find.sh min_element        # search all text, code and slides
        bash tools/find.sh -C 3 "erase.*remove"
        bash tools/build.sh path/to/project Sanitize   # crash -> exact line
        ```""")), kicker="Shell")
    note = card("course", "Missing files", md(
        "Course material is not in the public repository. Run `bash tools/fetch_extras.sh` once with internet: "
        "it clones the course repo, copies the exam subjects, downloads offline cppreference and extracts searchable text. "
        "Slides come from Hippocampus: drop the PDFs into `4_course/slides/` and run the script again."), kicker="Setup")
    return f'<div class="cards">{cs}{tip}{note}</div>'


# ---------------------------------------------------------------- assemble
def inline_fonts(css):
    def repl(m):
        data = base64.b64encode((HERE / "fonts" / m.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"
    return re.sub(r"url\(/assets/fonts/([\w.-]+\.woff2)\)", repl, css)


def build():
    bodies = {"home": page_home(), "cpp": md_cards("cpp", ROOT / "1_cheatsheet/cpp_cheatsheet.md"), "stl": page_stl(),
              "errors": md_cards("errors", ROOT / "1_cheatsheet/compiler_errors.md"), "algo": page_algo(),
              "snippets": page_snippets(), "exams": page_exams(), "course": page_course()}
    for pid, label in PAGES:
        INDEX.append({"p": pid, "id": "", "t": label, "k": "page", "x": ""})

    nav = "".join(f'<a class="nav-p" href="#{pid}" data-page="{pid}"><span class="num">{n:02d}</span>{label}</a>'
                  f'<div class="toc" data-toc="{pid}"></div>' for n, (pid, label) in enumerate(PAGES, 1))
    pages = "".join(
        f'<main class="page" id="page-{pid}" data-page="{pid}" hidden>'
        + ("" if pid == "home" else f'<div class="page-head"><span class="label">Page {n:02d} / {len(PAGES):02d}</span><h1>{label}</h1></div>')
        + bodies[pid] + "</main>" for n, (pid, label) in enumerate(PAGES, 1))
    foot = (f'<footer class="foot">{marking("centerline")}<p class="small muted">{NAME} &middot; made by Leon Górecki for the ARPRO exam at Centrale Nantes. '
            f'<a href="{SITE}">leongorecki.eu</a></p></footer>')

    tokens = inline_fonts((HERE / "hp/tokens.css").read_text(encoding="utf-8"))
    comps = (HERE / "hp/components.css").read_text(encoding="utf-8")
    comps = comps[:comps.find("/* ——— FlipBoard")]  # flip board not used here
    css = tokens + "\n" + comps + "\n" + (HERE / "site.css").read_text(encoding="utf-8")
    js = (HERE / "site.js").read_text(encoding="utf-8")
    mark = "data:image/svg+xml;base64," + base64.b64encode((HERE / "hp/lg-mark.svg").read_bytes()).decode()
    idx = json.dumps(INDEX, ensure_ascii=False).replace("</", "<\\/")
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{NAME}</title>
<meta name="description" content="Offline C++ exam kit for ARPRO at Centrale Nantes: cheat-sheets, algorithm templates, search.">
<link rel="icon" href="{mark}" type="image/svg+xml">
<script>try{{var t=localStorage.getItem('pac-theme');if(t)document.documentElement.dataset.theme=t;var f=localStorage.getItem('pac-font');if(f)document.documentElement.style.setProperty('--fs',f+'px')}}catch(e){{}}</script>
<style>{css}</style></head><body>
<header class="top">
  <button class="icon-btn" id="nav-toggle" aria-label="Menu">MENU</button>
  <a class="back" href="{SITE}">&larr; leongorecki.eu</a>
  <a class="hp-sign hp-sign--location hp-sign--sm" href="#home"><span>{NAME}</span></a>
  <button class="search-bar" data-open-palette><span>Search cards, functions, errors</span><kbd>CTRL K</kbd></button>
  <div class="top-r">
    <span class="mini-timer" id="mini-timer"></span>
    <button class="icon-btn" id="font-dn" title="Smaller text">A&minus;</button>
    <button class="icon-btn" id="font-up" title="Bigger text">A+</button>
    <div class="hp-lang" role="group" aria-label="Theme"><button type="button" data-theme-set="light">Day</button><button type="button" data-theme-set="dark">Night</button></div>
    <button class="icon-btn" id="help" title="Shortcuts">?</button>
  </div>
</header>
<div class="shell"><nav class="side" id="side" aria-label="Pages">{nav}</nav><div class="content">{pages}{foot}</div></div>
<div class="palette" id="palette" hidden><div class="pal-box" role="dialog" aria-label="Search">
  <input id="pal-in" placeholder="Search: erase, priority_queue, undefined reference, neighboors" autocomplete="off">
  <div id="pal-res" class="pal-res"></div>
  <div class="pal-foot label"><span><kbd>&uarr;</kbd> <kbd>&darr;</kbd> move</span><span><kbd>ENTER</kbd> open</span><span><kbd>ESC</kbd> close</span></div>
</div></div>
<div class="palette" id="helpbox" hidden><div class="pal-box help">
  <h3>Keyboard</h3>
  <p><kbd>CTRL K</kbd> or <kbd>/</kbd> search &middot; <kbd>1</kbd>&ndash;<kbd>8</kbd> pages &middot; <kbd>T</kbd> day or night &middot; <kbd>+</kbd> <kbd>&minus;</kbd> text size &middot; <kbd>ESC</kbd> close</p>
  <p class="small muted">Every code block has a copy button at its top right. LINK on a card gives a direct link to it.</p>
</div></div>
<div class="toast" id="toast"></div>
<script>window.INDEX={idx};</script>
<script>{js}</script>
</body></html>"""
    OUT.write_text(doc, encoding="utf-8", newline="\n")  # LF on every OS: same bytes as the repo
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(INDEX)} search entries)")


if __name__ == "__main__":
    build()
