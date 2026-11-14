(function () {
  "use strict";
  if (!window.name) window.name = "pac-kit";   // lets the search page link back to this tab
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var KEY = "pac-";

  /* Deep search: switch to the already open search tab (keeps its query); open it only if missing */
  $$('a[target="pac-search"]').forEach(function (a) {
    a.addEventListener("click", function (ev) {
      if (a.dataset.localOnly && document.documentElement.classList.contains("is-online")) return;
      ev.preventDefault();
      var w = window.open("", "pac-search");
      if (!w) { location.href = a.href; return; }
      try { if (w.location.href === "about:blank") w.location.href = a.href; }
      catch (e) { /* the search tab is on another origin: it exists, just focus it */ }
      w.focus();
    });
  });
  var store = {
    get: function (k) { try { return localStorage.getItem(KEY + k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(KEY + k, v); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem(KEY + k); } catch (e) {} }
  };
  var PAGE_LABEL = {};
  $$(".nav-p").forEach(function (a) { PAGE_LABEL[a.dataset.page] = a.textContent.replace(/^\d+/, "").trim(); });

  function toast(msg) {
    var t = $("#toast"); t.textContent = msg; t.classList.add("on");
    clearTimeout(toast.h); toast.h = setTimeout(function () { t.classList.remove("on"); }, 1300);
  }

  /* ---------- online (GitHub Pages) vs drive: swap drive-only links ---------- */
  var online = /^https?:$/.test(location.protocol) && !/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
  if (online) {
    document.documentElement.classList.add("is-online");
    $$("[data-online]").forEach(function (a) {
      var url = a.getAttribute("data-online");
      if (url) { a.href = url; a.target = "_blank"; a.rel = "noopener"; }
      else { a.classList.add("local-only"); a.title = "On the drive only (course material is not published)";
        a.addEventListener("click", function (ev) { ev.preventDefault(); toast("On the drive only"); }); }
    });
    $$("[data-online-note]").forEach(function (n) { n.hidden = false; });
  }

  /* ---------- table of contents per page ---------- */
  $$(".toc").forEach(function (toc) {
    var pid = toc.dataset.toc, page = $("#page-" + pid);
    var sections = $$("[data-toc-item]", page);     // long pages (Functions) list their groups instead
    if (sections.length) {
      sections.forEach(function (s) {
        var a = document.createElement("a");
        a.href = "#" + pid + "/" + s.id; a.textContent = s.textContent.trim();
        toc.appendChild(a);
      });
      return;
    }
    $$(".card[id]", page).forEach(function (c) {
      var h = $(".card-h", c); if (!h) return;
      var t = h.querySelector(".tw") || h.querySelector("span:not(.k):not(.idx):not(.label)");
      if (!t) return;
      var a = document.createElement("a");
      a.href = "#" + pid + "/" + c.id; a.textContent = t.textContent.trim();
      toc.appendChild(a);
    });
  });

  /* ---------- sidebar: clicking the current page folds / unfolds its list ---------- */
  var curPage = null, tocCollapsed = false;
  function paintToc() {
    $$(".toc").forEach(function (t) { t.classList.toggle("on", t.dataset.toc === curPage && !tocCollapsed); });
    $$(".nav-p").forEach(function (a) {
      if (a.dataset.page === curPage) a.setAttribute("aria-expanded", tocCollapsed ? "false" : "true");
      else a.removeAttribute("aria-expanded");
    });
  }
  $$(".nav-p").forEach(function (a) {
    a.addEventListener("click", function (ev) {
      if (a.dataset.page !== curPage) return;          // other page: normal navigation
      ev.preventDefault();
      tocCollapsed = !tocCollapsed; paintToc();
    });
  });

  /* ---------- router: #page or #page/target ---------- */
  function route() {
    var h = decodeURIComponent(location.hash.slice(1)) || "home";
    var parts = h.split("/"), pid = parts[0], target = parts[1];
    if (!$("#page-" + pid)) { pid = "home"; target = null; }
    $$(".page").forEach(function (p) { p.hidden = p.dataset.page !== pid; });
    $$(".nav-p").forEach(function (a) {
      var on = a.dataset.page === pid; a.classList.toggle("on", on);
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    if (pid !== curPage) { curPage = pid; tocCollapsed = false; }
    paintToc();
    $("#side").classList.remove("open");
    document.title = (pid === "home" ? "" : PAGE_LABEL[pid] + " · ") + "Post-Apocalyptic C++";
    if (!target) { window.scrollTo(0, 0); return; }
    var el = document.getElementById(target);
    if (!el) return;
    var det = el.closest("details"); if (det) det.open = true;
    var isLine = /-L-\d+$/.test(target);
    setTimeout(function () {
      el.scrollIntoView({ block: isLine ? "center" : "start" });
      if (isLine) {
        var pre = el.closest("pre"), y = el.getBoundingClientRect().top - pre.getBoundingClientRect().top + pre.scrollTop;
        pre.scrollTop = Math.max(0, y - pre.clientHeight / 3);
        flashLine(el);
      } else {
        var card = el.closest(".card") || el;
        card.classList.remove("flash"); void card.offsetWidth; card.classList.add("flash");
      }
    }, 30);
  }
  function flashLine(anchor) {
    var n = anchor.nextSibling, nodes = [], wrap = document.createElement("span");
    wrap.className = "line-target";
    while (n) {
      if (n.nodeType === 1 && n.tagName === "A" && n.id) break;
      nodes.push(n);
      if (n.textContent.indexOf("\n") >= 0) break;
      n = n.nextSibling;
    }
    if (!nodes.length) return;
    anchor.parentNode.insertBefore(wrap, nodes[0]);
    nodes.forEach(function (x) { wrap.appendChild(x); });
    setTimeout(function () { while (wrap.firstChild) wrap.parentNode.insertBefore(wrap.firstChild, wrap); wrap.remove(); }, 2500);
  }
  window.addEventListener("hashchange", route);

  /* ---------- copy buttons ---------- */
  $$(".hl").forEach(function (box) {
    var b = document.createElement("button");
    b.className = "copy"; b.textContent = "Copy"; b.type = "button";
    b.addEventListener("click", function (ev) {
      ev.preventDefault(); ev.stopPropagation();
      var clone = box.querySelector("pre").cloneNode(true);
      $$(".linenos", clone).forEach(function (x) { x.remove(); });
      var text = clone.textContent.replace(/\n$/, "");
      var ok = function () { b.textContent = "Copied"; b.classList.add("done"); setTimeout(function () { b.textContent = "Copy"; b.classList.remove("done"); }, 1200); };
      var fallback = function () {
        var ta = document.createElement("textarea"); ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { document.execCommand("copy"); ok(); } catch (e) { toast("Copy failed: select the text"); }
        ta.remove();
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fallback); else fallback();
    });
    box.appendChild(b);
  });

  /* ---------- command palette ---------- */
  var pal = $("#palette"), inp = $("#pal-in"), res = $("#pal-res"), sel = 0, shown = [];
  /* search: exact substring first, then the same without _ : spaces, then typos
     (1 edit for words up to 5 letters, 2 above). A function's syntax card wins on its own name. */
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function norm(s) { return s.replace(/[_\s:.\-]/g, ""); }
  function words(s) {
    var seen = {}, out = [];
    s.split(/[^a-z0-9_+]+/).forEach(function (w) { if (w.length >= 3 && !seen[w]) { seen[w] = 1; out.push(w); } });
    return out;
  }
  var IDX = (window.INDEX || []).map(function (e) {
    e.tl = e.t.toLowerCase(); e.tn = norm(e.tl); e.xn = norm(e.x);
    e.tw = words(e.tl); e.xw = words(e.x).slice(0, 120);
    if (e.nm) { e.nm = e.nm.toLowerCase(); e.nmn = norm(e.nm); }
    return e;
  });
  function dist(a, b, max) {            // optimal string alignment distance, gives up above max
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prev2 = null, prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev.push(j);
    for (i = 1; i <= a.length; i++) {
      cur = [i]; var best = i;
      for (j = 1; j <= b.length; j++) {
        var c = a[i - 1] === b[j - 1] ? 0 : 1;
        var v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + c);
        if (prev2 && i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
        cur.push(v); if (v < best) best = v;
      }
      if (best > max) return max + 1;
      prev2 = prev; prev = cur;
    }
    return prev[b.length];
  }
  function allowed(t) { return t.length <= 3 ? 0 : t.length <= 5 ? 1 : 2; }
  function fuzzyIn(t, ws) {
    var m = allowed(t); if (!m) return false;
    var tn = norm(t);
    for (var i = 0; i < ws.length; i++) if (dist(t, ws[i], m) <= m || dist(tn, norm(ws[i]), m) <= m) return true;
    return false;
  }
  function score(e, toks, q) {
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], tn = norm(t), inT = e.tl.indexOf(t);
      if (inT === 0) s += 30;
      else if (inT > 0) s += 18;
      else if (tn && e.tn.indexOf(tn) >= 0) s += 16;
      else if (e.x.indexOf(t) >= 0) s += 4;
      else if (tn && e.xn.indexOf(tn) >= 0) s += 3;
      else if (fuzzyIn(t, e.tw)) s += 12;
      else if (fuzzyIn(t, e.xw)) s += 2;
      else return -1;
    }
    if (e.tl.indexOf(q) >= 0) s += 25;
    if (e.nm) {                          // syntax card: exact or near-exact name beats everything
      var qn = norm(q);
      if (e.nm === q || e.nmn === qn) s += 150;
      else if (qn.length > 3 && dist(qn, e.nmn, allowed(qn)) <= allowed(qn)) s += 90;
    }
    if (e.k === "page") s += 5;
    if (e.k === "code") s += 2;
    return s - e.tl.length / 40;
  }
  function snippet(e, toks) {
    if (!e.x) return "";
    var i = e.x.indexOf(toks[0]); if (i < 0) i = 0;
    var start = Math.max(0, i - 40);
    return (start ? "…" : "") + e.x.slice(start, start + 120);
  }
  function mark(s, toks) {
    var out = esc(s);
    toks.forEach(function (t) {
      if (t.length < 2) return;
      out = out.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return out;
  }
  function render() {
    var q = inp.value.trim().toLowerCase(), toks = q.split(/\s+/).filter(Boolean);
    shown = !toks.length ? IDX.filter(function (e) { return e.k === "page"; })
      : IDX.map(function (e) { return [score(e, toks, q), e]; }).filter(function (p) { return p[0] >= 0; })
          .sort(function (a, b) { return b[0] - a[0]; }).slice(0, 40).map(function (p) { return p[1]; });
    sel = 0;
    if (!shown.length) { res.innerHTML = '<div class="pal-empty">No results for <b>' + esc(inp.value) + "</b>. Terminal: <code>bash tools/find.sh</code></div>"; return; }
    res.innerHTML = shown.map(function (e, i) {
      return '<div class="pal-it' + (i === 0 ? " on" : "") + '" data-i="' + i + '"><span class="hp-tag">' + esc(PAGE_LABEL[e.p] || e.p) + "</span>" +
        '<div style="min-width:0"><div class="tt">' + mark(e.t, toks) + "</div>" +
        (e.k !== "page" ? '<div class="sn">' + mark(snippet(e, toks), toks) + "</div>" : "") + "</div></div>";
    }).join("");
  }
  function go(i) {
    var e = shown[i]; if (!e) return;
    closePal();
    var h = "#" + e.p + (e.id ? "/" + e.id : "");
    if (location.hash === h) route(); else location.hash = h;
  }
  function openPal() { pal.hidden = false; inp.value = ""; render(); inp.focus(); }
  function closePal() { pal.hidden = true; }
  function moveSel(d) {
    var items = $$(".pal-it", res); if (!items.length) return;
    items[sel].classList.remove("on"); sel = (sel + d + items.length) % items.length;
    items[sel].classList.add("on"); items[sel].scrollIntoView({ block: "nearest" });
  }
  inp.addEventListener("input", render);
  inp.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowDown") { ev.preventDefault(); moveSel(1); }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); moveSel(-1); }
    else if (ev.key === "Enter") { ev.preventDefault(); go(sel); }
    else if (ev.key === "Escape") closePal();
  });
  res.addEventListener("click", function (ev) { var it = ev.target.closest(".pal-it"); if (it) go(+it.dataset.i); });
  pal.addEventListener("click", function (ev) { if (ev.target === pal) closePal(); });
  $$("[data-open-palette]").forEach(function (b) { b.addEventListener("click", openPal); });

  /* ---------- theme (Day / Night), font size, help, mobile nav ---------- */
  function curTheme() {
    var t = document.documentElement.dataset.theme;
    return t || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function paintTheme() { var c = curTheme(); $$("[data-theme-set]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.themeSet === c ? "true" : "false"); }); }
  function setTheme(t) { document.documentElement.dataset.theme = t; store.set("theme", t); paintTheme(); }
  $$("[data-theme-set]").forEach(function (b) { b.addEventListener("click", function () { setTheme(b.dataset.themeSet); }); });
  paintTheme();
  function font(d) {
    var cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--fs")) || 15;
    var n = Math.max(11, Math.min(22, cur + d));
    document.documentElement.style.setProperty("--fs", n + "px"); store.set("font", n);
  }
  $("#font-up").addEventListener("click", function () { font(1); });
  $("#font-dn").addEventListener("click", function () { font(-1); });
  var help = $("#helpbox");
  $("#help").addEventListener("click", function () { help.hidden = false; });
  help.addEventListener("click", function () { help.hidden = true; });
  $("#nav-toggle").addEventListener("click", function () { $("#side").classList.toggle("open"); });

  /* ---------- keyboard ---------- */
  document.addEventListener("keydown", function (ev) {
    var typing = /INPUT|TEXTAREA|SELECT/.test(ev.target.tagName || "");
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") { ev.preventDefault(); pal.hidden ? openPal() : closePal(); return; }
    if (ev.key === "Escape") { closePal(); help.hidden = true; return; }
    if (typing || ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (ev.key === "/") { ev.preventDefault(); openPal(); }
    else if (/^[0-9]$/.test(ev.key)) { var a = $$(".nav-p")[ev.key === "0" ? 9 : +ev.key - 1]; if (a) location.hash = "#" + a.dataset.page; }
    else if (ev.key === "t") setTheme(curTheme() === "dark" ? "light" : "dark");
    else if (ev.key === "+" || ev.key === "=") font(1);
    else if (ev.key === "-") font(-1);
    else if (ev.key === "?") help.hidden = !help.hidden;
  });

  /* ---------- exam timer (2 h) ---------- */
  var DUR = 120 * 60 * 1000;
  function fmt(ms, up) {                 // up: round up (time left), so elapsed + left = 2:00:00
    var t = (up ? Math.ceil : Math.floor)(Math.max(0, ms) / 1000), h = Math.floor(t / 3600), m = Math.floor(t / 60) % 60, s = t % 60;
    return h + ":" + ("0" + m).slice(-2) + ":" + ("0" + s).slice(-2);
  }
  function lampHtml(state, word) { return '<span class="hp-lamp hp-lamp--' + state + '"><i aria-hidden="true"></i><span>' + word + "</span></span>"; }
  function tick() {
    var st = +store.get("start"), mini = $("#mini-timer");
    if (!st) { $("#t-elapsed").textContent = "0:00:00"; $("#t-left").textContent = "2:00:00"; $("#t-fill").style.width = "0";
      $("#t-phase").textContent = "Not started."; mini.innerHTML = ""; return; }
    var el = Date.now() - st, left = DUR - el, min = el / 60000, frac = Math.min(1, Math.max(0, el / DUR));
    $("#t-elapsed").textContent = fmt(el); $("#t-left").textContent = fmt(left, true);
    $("#t-fill").style.width = (frac * 100) + "%";
    $("#t-phase").textContent = min < 10 ? "Phase 1: read the whole subject, build the untouched project, git init."
      : min < 110 ? "Phase 2: TODOs in order, commit after each one that works."
      : left > 0 ? "Phase 3: make sure it compiles, comment out broken code, final commit." : "Time is up.";
    mini.innerHTML = lampHtml(left <= 0 ? "hold" : min >= 100 ? "caution" : "go", fmt(left, true) + " left");
  }
  $("#t-start").addEventListener("click", function () { store.set("start", Date.now()); tick(); });
  $("#t-08").addEventListener("click", function () { var d = new Date(); d.setHours(8, 0, 0, 0); store.set("start", +d); tick(); });
  $("#t-reset").addEventListener("click", function () { store.del("start"); tick(); });
  setInterval(tick, 1000); tick();

  /* ---------- routine checklist ---------- */
  $$(".chk input").forEach(function (c) {
    c.checked = store.get(c.dataset.k) === "1";
    c.addEventListener("change", function () { store.set(c.dataset.k, c.checked ? "1" : "0"); });
  });
  $("#chk-reset").addEventListener("click", function () { $$(".chk input").forEach(function (c) { c.checked = false; store.set(c.dataset.k, "0"); }); });

  route();
})();
