/* Hive Kids Bible (Hive Academy preview). Static: reads data/stories.json, saves progress in localStorage only. */
(function () {
  "use strict";
  var KEY = "hiveAcademy.kidsBible.v1";
  var MODES = {
    fill: { name: "Missing word", icon: "✏️", how: "Pick the word that goes in the blank." },
    order: { name: "Words in order", icon: "🧩", how: "Tap the words in the right order." },
    letters: { name: "First letters", icon: "🔤", how: "Say the verse out loud. Only the first letters are shown. Tap a letter to peek at its word." }
  };
  var STOP = "a an and the of to in on for is it be as at by he she i me my you your his her him we us our they them their this that who which with from not was are has have had will shall so but or all any thing too then even what there ye thou thee thy hath unto shall".split(" ");
  var app = document.getElementById("app"), say = document.getElementById("say");
  var DATA = null, S = load();

  function load() {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { s = null; }
    if (!s || typeof s !== "object") s = {};
    s.tr = s.tr === "KJV" || s.tr === "WEB" ? s.tr : null; /* default comes from the data file (KJV) */
    s.stars = s.stars && typeof s.stars === "object" ? s.stars : {};
    s.days = Array.isArray(s.days) ? s.days : [];
    return s;
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* storage off: play still works */ } }
  function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function announce(t) { say.textContent = ""; setTimeout(function () { say.textContent = t; }, 30); }
  function dayStr(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function core(w) { return w.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ""); }
  function words(t) { return t.trim().split(/\s+/); }
  function story(id) { return DATA.stories.find(function (s) { return s.id === id; }); }
  /* A memory item is one key verse. Most stories have one; "Who Is Jesus?" has two (John 1:1 and 1:14). */
  var ITEMS = [];
  function buildItems() {
    ITEMS = [];
    DATA.stories.forEach(function (s) {
      var vs = s.verses || [s.verse];
      s.items = vs.map(function (v, i) { var it = { id: i ? s.id + "-" + (i + 1) : s.id, title: s.title, verse: v, story: s, n: i, of: vs.length }; ITEMS.push(it); return it; });
    });
  }
  function item(id) { return ITEMS.find(function (x) { return x.id === id; }); }
  function storyStars(s) { return s.items.reduce(function (a, it) { return a + starCount(it.id); }, 0); }
  function verse(s) { return s.verse[S.tr]; }
  function starCount(id) { var g = S.stars[id] || {}; return (g.fill ? 1 : 0) + (g.order ? 1 : 0) + (g.letters ? 1 : 0); }
  function starsHtml(n, label, max) {
    max = max || 3;
    var h = '<span class="stars" role="img" aria-label="' + esc(label || (n + " of " + max + " stars")) + '">';
    for (var i = 0; i < max; i++) h += '<span class="' + (i < n ? "on" : "") + '" aria-hidden="true">★</span>';
    return h + "</span>";
  }
  function learnedCount() { return ITEMS.filter(function (it) { return starCount(it.id) === 3; }).length; }
  function totalStars() { return ITEMS.reduce(function (a, it) { return a + starCount(it.id); }, 0); }
  function streak() {
    var set = {}; S.days.forEach(function (d) { set[d] = 1; });
    var d = new Date(); if (!set[dayStr(d)]) d.setDate(d.getDate() - 1);
    var n = 0; while (set[dayStr(d)]) { n++; d.setDate(d.getDate() - 1); }
    return n;
  }
  function award(id, mode) {
    var g = S.stars[id] = S.stars[id] || {}, fresh = !g[mode];
    g[mode] = true;
    var t = dayStr(new Date()); if (S.days.indexOf(t) < 0) S.days.push(t);
    S.days = S.days.sort().slice(-400);
    save();
    return fresh;
  }
  function refLine(s) {
    var v = verse(s);
    return esc(s.verse.ref) + " (" + S.tr + ")" + (v.partOfVerse ? ' <span class="part">Part of the verse</span>' : "");
  }

  /* ---------- views ---------- */
  function setTab(t) {
    document.querySelectorAll(".tabs a").forEach(function (a) { if (a.dataset.tab === t) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  }
  function focusTitle(title) {
    /* The tab title stays the same on purpose, so the browser history never shows which stories or games are played. */
    var h = app.querySelector("h1,h2"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    window.scrollTo(0, 0);
  }

  /* Breadcrumb: Codex Hive Labs › Hive Academy › Hive Kids Bible › [story] › [game] */
  function crumbs(trail) {
    var ol = document.getElementById("bc"), mod = ol.querySelector(".bc__item--module a");
    ol.querySelectorAll(".bc__item--extra").forEach(function (li) { li.remove(); });
    if (trail.length) mod.removeAttribute("aria-current"); else mod.setAttribute("aria-current", "page");
    trail.forEach(function (c, i) {
      var li = document.createElement("li"); li.className = "bc__item bc__item--extra";
      var el = document.createElement(c.href ? "a" : "span");
      if (c.href) el.href = c.href; else { el.className = "cur"; el.setAttribute("aria-current", "page"); }
      el.textContent = c.t; el.title = c.t; li.appendChild(el); ol.appendChild(li);
    });
    var nav = ol.closest(".bc");
    nav.classList.toggle("bc--deep", trail.length > 0);
    nav.classList.toggle("bc--deeper", trail.length > 1);
  }

  function home() {
    setTab("stories");
    crumbs([]);
    var h = '<div class="intro"><div><h1>Bible stories &amp; verse games</h1>' +
      "<p>Read a story together, then play three short games to learn its key verse. Earn a star for each game.</p></div>" +
      '<a class="pill" href="#/progress"><span><span aria-hidden="true">★</span> <b>' + totalStars() + "</b> star" + (totalStars() === 1 ? "" : "s") + "</span><span>· <b>" + learnedCount() + "</b> verse" + (learnedCount() === 1 ? "" : "s") + " learned</span><span>· <b>" + streak() + "</b>-day streak</span></a></div>" +
      featuredHtml() +
      '<h2 class="sec">All stories</h2><ul class="grid" aria-label="Bible stories">';
    DATA.stories.forEach(function (s) {
      var n = storyStars(s), mx = 3 * s.items.length;
      h += '<li><a class="tile" href="#/story/' + s.id + '"><span class="tile__n">' + (s.testament === "OT" ? "Old Testament" : "New Testament") + " · " + s.order + "</span>" +
        "<h3>" + esc(s.title) + '</h3><span class="tile__ref">' + esc(s.passage) + "</span>" + starsHtml(n, n + " of " + mx + " stars for " + s.title, mx) + "</a></li>";
    });
    app.innerHTML = h + "</ul>";
    focusTitle("Stories");
  }

  function featuredHtml() {
    var f = DATA.featured || []; if (!f.length) return "";
    var h = '<section class="featured" aria-labelledby="ft"><h2 id="ft" class="sec">Featured verses</h2><div class="featured__grid">';
    f.forEach(function (x) {
      var t = story(x.story); if (!t) return;
      h += '<article class="feat"><p class="kick">' + esc(x.label) + "</p>";
      t.items.forEach(function (it) { h += '<blockquote><p>“' + esc(it.verse[S.tr].text) + '”</p><cite>' + esc(it.verse.ref) + " (" + S.tr + ")</cite></blockquote>"; });
      h += '<a class="btn" href="#/story/' + t.id + '">Learn ' + (t.items.length > 1 ? "these verses" : "this verse") + ' <span aria-hidden="true">→</span></a></article>';
    });
    return h + "</div></section>";
  }

  function storyView(s) {
    setTab("stories");
    crumbs([{ t: s.title }]);
    var h = '<div class="story"><article class="panel" aria-labelledby="st-title"><p class="kick">Story ' + s.order + " of " + DATA.stories.length + "</p>" +
      '<h1 id="st-title">' + esc(s.title) + '</h1><p class="retell">' + esc(s.retelling) + "</p>" +
      '<p class="passage">Read it in the Bible: <strong>' + esc(s.passage) + "</strong></p>" + moreHtml(s) + "</article>" +
      '<div class="verses">';
    s.items.forEach(function (it, k) {
      var v = it.verse[S.tr], g = S.stars[it.id] || {};
      h += '<section class="verse" aria-labelledby="kv' + k + '"><p class="kick" id="kv' + k + '">' + (it.of > 1 ? "Key verse " + (k + 1) + " of " + it.of : "Key verse") + '</p><blockquote><p style="margin:0">“' + esc(v.text) + "”</p></blockquote>" +
        "<cite>" + refLine(it) + "</cite>" + '<ul class="games" aria-label="Verse games for ' + esc(it.verse.ref) + '">';
      Object.keys(MODES).forEach(function (m) {
        h += '<li><a class="game-btn" href="#/play/' + it.id + "/" + m + '"><b><span aria-hidden="true">' + MODES[m].icon + "</span> " + MODES[m].name + "</b>" +
          "<span>" + (g[m] ? '<span class="done">★ Star earned</span>' : "Play for a star") + "</span></a></li>";
      });
      h += "</ul>" + '<div style="margin-top:14px">' + starsHtml(starCount(it.id), starCount(it.id) + " of 3 stars for this verse") + "</div></section>";
    });
    h += "</div></div>";
    var i = DATA.stories.indexOf(s), nx = DATA.stories[(i + 1) % DATA.stories.length];
    h += '<div class="btns"><a class="btn btn--ghost" style="color:var(--text);border-color:rgba(236,232,225,.4)" href="#/story/' + nx.id + '">Next story: ' + esc(nx.title) + ' <span aria-hidden="true">→</span></a></div>';
    app.innerHTML = h;
    focusTitle(s.title);
  }

  function moreHtml(s) {
    var h = "";
    (s.more || []).forEach(function (m) {
      var q = m[S.tr];
      h += '<aside class="more" aria-label="' + esc(m.label) + '"><p class="kick">' + esc(m.label) + "</p><blockquote><p>“" + esc(q.text) + "”</p></blockquote>" +
        "<cite>" + esc(m.ref) + " (" + S.tr + ")" + (q.partOfVerse ? ' <span class="part">Part of the verse</span>' : "") + "</cite></aside>";
    });
    (s.pointTo || []).forEach(function (pid) {
      var t = story(pid); if (!t || t.id === s.id) return;
      var quoted = (s.more || []).some(function (m) { return m.ref === t.verse.ref; });
      var lead = pid === "who-is-jesus" ? "Who is Jesus? Read " + esc(t.title) + " (John 1:1, 14)" :
        quoted ? "Read the story of " + esc(t.title) : "What does the Bible say we should do? Read " + esc(t.title) + " (" + esc(t.verse.ref) + ")";
      h += '<p class="point"><a href="#/story/' + t.id + '">' + lead + ' <span aria-hidden="true">→</span></a></p>';
    });
    return h;
  }
  function winHtml(s, mode, fresh) {
    var n = starCount(s.id);
    var next = Object.keys(MODES).find(function (m) { return !(S.stars[s.id] || {})[m]; });
    return '<div class="win" role="status"><div class="big" aria-hidden="true">★</div><p><strong>' + (fresh ? "You earned a star!" : "Well done! You did it again.") + "</strong></p>" +
      "<p>" + starsHtml(n, n + " of 3 stars for this verse") + "</p>" +
      (n === 3 ? "<p>You learned this verse. Say it to someone today!</p>" : "") +
      '<div class="btns"><a class="btn" href="#/play/' + s.id + "/" + mode + '?again=' + Date.now() + '">Play again</a>' +
      (next ? '<a class="btn" href="#/play/' + s.id + "/" + next + '">Next game: ' + MODES[next].name + "</a>" : "") +
      '<a class="btn btn--ghost" href="#/story/' + s.story.id + '">Back to the story</a></div></div>';
  }

  function playShell(s, mode) {
    setTab("stories");
    crumbs([{ t: s.title, href: "#/story/" + s.story.id }, { t: MODES[mode].name + (s.of > 1 ? " (" + s.verse.ref + ")" : "") }]);
    app.innerHTML = '<div class="play">' +
      '<div class="play__head"><h1 style="font-size:clamp(26px,3.4vw,36px);margin:0"><span aria-hidden="true">' + MODES[mode].icon + "</span> " + MODES[mode].name + "</h1>" +
      starsHtml(starCount(s.id), starCount(s.id) + " of 3 stars for this verse") + "</div>" +
      '<section class="board" aria-label="' + esc(MODES[mode].name + " game") + '"><p class="how">' + esc(MODES[mode].how) + '</p><div id="game"></div>' +
      '<p class="ref">' + refLine(s) + '</p><p class="feedback" id="fb" aria-live="polite"></p></section></div>';
    focusTitle(MODES[mode].name + ": " + s.title);
    return document.getElementById("game");
  }
  function fb(t, ok) { var e = document.getElementById("fb"); e.textContent = t; e.className = "feedback " + (ok ? "ok" : "no"); }
  function finish(s, mode) {
    var fresh = award(s.id, mode);
    var b = app.querySelector(".board"); b.innerHTML = winHtml(s, mode, fresh);
    announce((fresh ? "You earned a star! " : "Well done! ") + starCount(s.id) + " of 3 stars for this verse.");
    var f = b.querySelector(".btn"); if (f) f.focus();
  }

  function pool(exclude) {
    var out = {};
    ITEMS.forEach(function (s) { words(verse(s).text).forEach(function (w) { var c = core(w); if (c.length > 2 && STOP.indexOf(c.toLowerCase()) < 0) out[c.toLowerCase()] = c; }); });
    exclude.forEach(function (x) { delete out[x.toLowerCase()]; });
    return Object.keys(out).map(function (k) { return out[k]; });
  }

  function gameFill(s) {
    var el = playShell(s, "fill"), w = words(verse(s).text);
    var cand = w.map(function (x, i) { return i; }).filter(function (i) { var c = core(w[i]); return c.length > 2 && STOP.indexOf(c.toLowerCase()) < 0; });
    if (!cand.length) cand = w.map(function (x, i) { return i; });
    var k = w.length <= 6 ? 1 : w.length <= 12 ? 2 : 3;
    var blanks = shuffle(cand).slice(0, k).sort(function (a, b) { return a - b; }), step = 0;
    function draw() {
      var at = blanks[step], ans = core(w[at]);
      var line = w.map(function (x, i) {
        var bi = blanks.indexOf(i);
        if (bi < 0) return esc(x);
        var c = core(x), pre = x.slice(0, x.indexOf(c)), post = x.slice(x.indexOf(c) + c.length);
        if (bi < step) return esc(pre) + '<span class="blank got">' + esc(c) + "</span>" + esc(post);
        return esc(pre) + '<span class="blank" aria-label="blank">' + (bi === step ? "?" : "&nbsp;") + "</span>" + esc(post);
      }).join(" ");
      var opts = shuffle([ans].concat(shuffle(pool([ans])).slice(0, 3)));
      el.innerHTML = '<p class="line">“' + line + "”</p>" + '<div class="choices" role="group" aria-label="Choose the missing word">' +
        opts.map(function (o) { return '<button type="button" class="word" data-w="' + esc(o) + '">' + esc(o) + "</button>"; }).join("") + "</div>";
      el.querySelectorAll(".word").forEach(function (b) {
        b.addEventListener("click", function () {
          if (b.dataset.w === ans) {
            b.classList.add("right"); step++;
            if (step >= blanks.length) return finish(s, "fill");
            fb("Yes! “" + ans + "” is right.", true); announce("Correct. Next blank."); draw();
            var f = el.querySelector(".word"); if (f) f.focus();
          } else {
            b.classList.add("wrong"); b.disabled = true; b.setAttribute("aria-label", b.dataset.w + ", not this one"); fb("Not that one. Try again!", false);
          }
        });
      });
    }
    draw();
  }

  function gameOrder(s) {
    var el = playShell(s, "order"), w = words(verse(s).text), next = 0;
    var tiles = w.map(function (x, i) { return { t: x, i: i }; }), mix = shuffle(tiles), tries = 0;
    while (w.length > 1 && mix.every(function (o, i) { return o.i === i; }) && tries++ < 10) mix = shuffle(tiles);
    el.innerHTML = '<div class="built" id="built" aria-label="Your verse so far"></div><div class="bank" role="group" aria-label="Word tiles">' +
      mix.map(function (o) { return '<button type="button" class="word" data-t="' + esc(o.t) + '">' + esc(o.t) + "</button>"; }).join("") + "</div>";
    var built = document.getElementById("built");
    el.querySelectorAll(".word").forEach(function (b) {
      b.addEventListener("click", function () {
        if (b.dataset.t === w[next]) {
          var sp = document.createElement("span"); sp.className = "w"; sp.textContent = w[next]; built.appendChild(sp);
          b.classList.add("used"); b.setAttribute("aria-hidden", "true"); b.tabIndex = -1; next++;
          if (next >= w.length) return finish(s, "order");
          fb("Good! " + (w.length - next) + " word" + (w.length - next === 1 ? "" : "s") + " to go.", true);
          var f = el.querySelector(".bank .word:not(.used)"); if (f && document.activeElement === b) f.focus();
        } else {
          b.classList.remove("wrong"); void b.offsetWidth; b.classList.add("wrong");
          fb("Not yet. Which word comes next?", false);
        }
      });
    });
  }

  function gameLetters(s) {
    var el = playShell(s, "letters"), w = words(verse(s).text);
    function hint(x) { var c = core(x); if (!c) return x; var i = x.indexOf(c); return x.slice(0, i) + c[0] + x.slice(i + c.length); }
    el.innerHTML = '<div class="letters" role="group" aria-label="First letters of each word">' +
      w.map(function (x, i) { return '<button type="button" class="lt" aria-pressed="false" data-i="' + i + '" aria-label="Word ' + (i + 1) + ', starts with ' + esc(core(x)[0] || x) + '">' + esc(hint(x)) + "</button>"; }).join("") +
      '</div><div class="btns" style="justify-content:flex-start"><button type="button" class="btn btn--ghost" id="all">Show all words</button>' +
      '<button type="button" class="btn" id="said"><span class="em" aria-hidden="true">🗣️</span> I said it!</button></div>';
    var btns = el.querySelectorAll(".lt"), shown = false;
    function set(b, on) { var x = w[+b.dataset.i]; b.textContent = on ? x : hint(x); b.setAttribute("aria-pressed", on ? "true" : "false"); b.setAttribute("aria-label", on ? x : "Word " + (+b.dataset.i + 1) + ", starts with " + (core(x)[0] || x)); }
    btns.forEach(function (b) { b.addEventListener("click", function () { set(b, b.getAttribute("aria-pressed") !== "true"); }); });
    document.getElementById("all").addEventListener("click", function () { shown = !shown; btns.forEach(function (b) { set(b, shown); }); this.textContent = shown ? "Hide the words" : "Show all words"; });
    document.getElementById("said").addEventListener("click", function () { finish(s, "letters"); });
  }

  function progress() {
    setTab("progress");
    crumbs([{ t: "My stars" }]);
    var h = "<h1>My stars</h1>" + '<div class="prog">' +
      '<div class="stat"><b>' + totalStars() + '</b><span>' + (totalStars() === 1 ? "star" : "stars") + ' of ' + ITEMS.length * 3 + "</span></div>" +
      '<div class="stat"><b>' + learnedCount() + '</b><span>' + (learnedCount() === 1 ? "verse" : "verses") + ' learned (3 stars)</span></div>' +
      '<div class="stat"><b>' + streak() + '</b><span>day streak' + (streak() ? "" : ": play today to start one") + "</span></div></div>" +
      '<table class="table"><caption class="sr-only">Stars for each verse</caption><thead><tr><th scope="col">Story</th><th scope="col" class="hide-s">Verse</th><th scope="col">Stars</th></tr></thead><tbody>';
    ITEMS.forEach(function (it) {
      var n = starCount(it.id);
      h += '<tr><td><a href="#/story/' + it.story.id + '">' + esc(it.title) + (it.of > 1 ? " (" + (it.n + 1) + ")" : "") + '</a></td><td class="muted hide-s">' + esc(it.verse.ref) + "</td><td>" + starsHtml(n, n + " of 3 stars") + "</td></tr>";
    });
    h += "</tbody></table>" +
      '<p class="note">Progress is saved only in this browser on this device (local storage). There are no accounts, and nothing about your play is sent to us. Clearing your browser data, or the button below, erases it.</p>' +
      '<button type="button" class="btn btn--danger" id="reset">Reset all progress</button>';
    app.innerHTML = h;
    document.getElementById("reset").addEventListener("click", function () {
      if (!window.confirm("Erase all stars and the streak on this device?")) return;
      S.stars = {}; S.days = []; save(); progress(); announce("Progress was reset.");
    });
    focusTitle("My stars");
  }

  /* ---------- router ---------- */
  function route() {
    if (!DATA) return;
    var p = (location.hash.replace(/^#\/?/, "").split("?")[0] || "").split("/");
    var s = p[1] && story(p[1]);
    if (p[0] === "story" && s) return storyView(s);
    var it = p[0] === "play" && p[1] && item(p[1]);
    if (it && MODES[p[2]]) return ({ fill: gameFill, order: gameOrder, letters: gameLetters })[p[2]](it);
    if (p[0] === "progress") return progress();
    home();
  }
  function setTr(t, persist) {
    S.tr = t; if (persist) save();
    document.querySelectorAll(".tr button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.tr === t ? "true" : "false"); });
    var tr = DATA && DATA.translations[t];
    if (tr) document.getElementById("trnote").innerHTML = "Scripture quotations are from the <strong>" + esc(tr.name) + "</strong>, " + esc(tr.license) + '. Text from <a href="' + esc(tr.url) + '" rel="noopener">' + esc(tr.source) + "</a>. Verses are quoted exactly; where only part of a verse is used, it says so. The short story retellings are written for children and are not quotations; each one follows the Bible passage listed with it.";
  }
  document.querySelectorAll(".tr button").forEach(function (b) { b.addEventListener("click", function () { setTr(b.dataset.tr, true); route(); announce(DATA.translations[b.dataset.tr].name); }); });
  window.addEventListener("hashchange", route);

  fetch("data/stories.json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
    DATA = d; buildItems(); setTr(S.tr || d.defaultTranslation || "KJV"); route();
  }).catch(function () { app.innerHTML = '<p class="note">The stories could not be loaded. Please refresh the page.</p>'; });
})();
