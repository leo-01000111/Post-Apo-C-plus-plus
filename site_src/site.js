(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var KEY = "pac-";
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
    $$(".card[id]", page).forEach(function (c) {
      var h = $(".card-h", c); if (!h) return;
      var t = h.querySelector(".tw") || h.querySelector("span:not(.k):not(.idx):not(.label)");
      if (!t) return;
      var a = document.createElement("a");
      a.href = "#" + pid + "/" + c.id; a.textContent = t.textContent.trim();
      toc.appendChild(a);
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
    $$(".toc").forEach(function (t) { t.classList.toggle("on", t.dataset.toc === pid); });
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
  var IDX = (window.INDEX || []).map(function (e) { e.tl = e.t.toLowerCase(); return e; });
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function score(e, toks, q) {
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], inT = e.tl.indexOf(t), inX = e.x.indexOf(t);
      if (inT < 0 && inX < 0) return -1;
      s += inT === 0 ? 30 : inT > 0 ? 18 : 4;
    }
    if (e.tl.indexOf(q) >= 0) s += 25;
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
    if (!shown.length) { res.innerHTML = '<div class="pal-empty">No results for <b>' + esc(inp.value) + "</b>. Try fewer or shorter words, or <code>bash tools/find.sh</code> in a terminal.</div>"; return; }
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
    else if (/^[1-8]$/.test(ev.key)) { var a = $$(".nav-p")[+ev.key - 1]; if (a) location.hash = "#" + a.dataset.page; }
    else if (ev.key === "t") setTheme(curTheme() === "dark" ? "light" : "dark");
    else if (ev.key === "+" || ev.key === "=") font(1);
    else if (ev.key === "-") font(-1);
    else if (ev.key === "?") help.hidden = !help.hidden;
  });

  /* ---------- exam timer (2 h) ---------- */
  var DUR = 120 * 60 * 1000;
  function fmt(ms) { ms = Math.max(0, ms); var m = Math.floor(ms / 60000), h = Math.floor(m / 60); return h + ":" + ("0" + (m % 60)).slice(-2); }
  function lampHtml(state, word) { return '<span class="hp-lamp hp-lamp--' + state + '"><i aria-hidden="true"></i><span>' + word + "</span></span>"; }
  function tick() {
    var st = +store.get("start"), mini = $("#mini-timer");
    if (!st) { $("#t-elapsed").textContent = "0:00"; $("#t-left").textContent = "2:00"; $("#t-fill").style.width = "0";
      $("#t-phase").textContent = "Not started."; mini.innerHTML = ""; return; }
    var el = Date.now() - st, left = DUR - el, min = el / 60000, frac = Math.min(1, Math.max(0, el / DUR));
    $("#t-elapsed").textContent = fmt(el); $("#t-left").textContent = fmt(left);
    $("#t-fill").style.width = (frac * 100) + "%";
    $("#t-phase").textContent = min < 10 ? "Phase 1: read the whole subject, build the untouched project, git init."
      : min < 110 ? "Phase 2: TODOs in order, commit after each one that works."
      : left > 0 ? "Phase 3: make sure it compiles, comment out broken code, final commit." : "Time is up.";
    mini.innerHTML = lampHtml(left <= 0 ? "hold" : min >= 100 ? "caution" : "go", fmt(left) + " left");
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
