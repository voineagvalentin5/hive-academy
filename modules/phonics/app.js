/* Hive Phonics (Hive Academy preview). Static page: no accounts, no ads. Progress lives in localStorage only.
   Audio: recorded clips first (see CLIPS and audio/README.md), then the browser's speechSynthesis voice. */
(function () {
  "use strict";
  var KEY = "hiveAcademy.phonics.v1";
  var NAME = "Hive Phonics";

  /* ---------- content ---------- */
  /* One picture word per letter. Vowels use short-vowel words. X uses a word that ends in x. */
  var LETTERS = [
    ["a", "apple", "🍎"], ["b", "bee", "🐝"], ["c", "cat", "🐱"], ["d", "dog", "🐶"], ["e", "egg", "🥚"],
    ["f", "fish", "🐟"], ["g", "goat", "🐐"], ["h", "hat", "🎩"], ["i", "insect", "🐞"], ["j", "juice", "🧃"],
    ["k", "key", "🔑"], ["l", "lion", "🦁"], ["m", "moon", "🌙"], ["n", "nose", "👃"], ["o", "octopus", "🐙"],
    ["p", "pig", "🐷"], ["q", "queen", "👑"], ["r", "rabbit", "🐰"], ["s", "sun", "☀️"], ["t", "turtle", "🐢"],
    ["u", "umbrella", "☂️"], ["v", "van", "🚐"], ["w", "web", "🕸️"], ["x", "fox", "🦊"], ["y", "yarn", "🧶"], ["z", "zebra", "🦓"]
  ].map(function (r) { return { l: r[0], word: r[1], em: r[2], end: r[0] === "x" }; });

  /* Short-vowel consonant-vowel-consonant words, grouped by vowel. */
  var WORDS = {
    a: [["cat", "🐱"], ["hat", "🎩"], ["bat", "🦇"], ["van", "🚐"], ["map", "🗺️"]],
    e: [["bed", "🛏️"], ["hen", "🐔"], ["pen", "🖊️"], ["net", "🥅"], ["jet", "✈️"]],
    i: [["pig", "🐷"], ["pin", "📌"], ["lip", "👄"], ["six", "6️⃣"]],
    o: [["dog", "🐶"], ["fox", "🦊"], ["box", "📦"], ["log", "🪵"]],
    u: [["sun", "☀️"], ["bus", "🚌"], ["cup", "☕"], ["bug", "🐛"], ["nut", "🥜"]]
  };
  var VOWEL_NAME = { a: "Short a", e: "Short e", i: "Short i", o: "Short o", u: "Short u" };
  var WORDLIST = [];
  Object.keys(WORDS).forEach(function (v) { WORDS[v].forEach(function (w) { WORDLIST.push({ w: w[0], em: w[1], v: v }); }); });

  /* Rough spoken stand-ins for single sounds. Device voices say these imperfectly, which is why
     letter cards lead with the letter name and a picture word, and why recorded clips win when present. */
  var SOUND = { a: "aa", b: "buh", c: "kuh", d: "duh", e: "eh", f: "fff", g: "guh", h: "huh", i: "ih", j: "juh", k: "kuh", l: "lll", m: "mmm",
    n: "nnn", o: "ah", p: "puh", q: "kwuh", r: "rrr", s: "sss", t: "tuh", u: "uh", v: "vvv", w: "wuh", x: "ks", y: "yuh", z: "zzz" };

  /* Recorded-audio hook. Drop files into audio/ and list them here, for example:
       "sound-a": "audio/sound-a.mp3"   (the short /a/ sound)
       "letter-a": "audio/letter-a.mp3" (the full letter card line: "A. A is for apple.")
       "word-cat": "audio/word-cat.mp3"
     Any key not listed falls back to the device voice. */
  var CLIPS = {};

  /* ---------- state ---------- */
  var app = document.getElementById("app"), say = document.getElementById("say"), sndBtn = document.getElementById("snd");
  var REDUCED = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var S = load();

  function load() {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { s = null; }
    if (!s || typeof s !== "object") s = {};
    ["heard", "blended", "first"].forEach(function (k) { s[k] = s[k] && typeof s[k] === "object" ? s[k] : {}; });
    s.days = Array.isArray(s.days) ? s.days : [];
    s.sound = s.sound !== false;
    return s;
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* storage off: play still works */ } }
  function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function announce(t) { say.textContent = ""; setTimeout(function () { say.textContent = t; }, 30); }
  function dayStr(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function letter(l) { return LETTERS.find(function (x) { return x.l === l; }); }
  function wordObj(w) { return WORDLIST.find(function (x) { return x.w === w; }); }
  function count(o) { return Object.keys(o).filter(function (k) { return o[k]; }).length; }
  function total() { return count(S.heard) + count(S.blended) + count(S.first); }
  var MAX = 26 + WORDLIST.length + 26;
  function plural(n, w) { return n + " " + w + (n === 1 ? "" : "s"); }
  function streak() {
    var set = {}; S.days.forEach(function (d) { set[d] = 1; });
    var d = new Date(); if (!set[dayStr(d)]) d.setDate(d.getDate() - 1);
    var n = 0; while (set[dayStr(d)]) { n++; d.setDate(d.getDate() - 1); }
    return n;
  }
  function award(kind, id) {
    var fresh = !S[kind][id];
    S[kind][id] = true;
    var t = dayStr(new Date()); if (S.days.indexOf(t) < 0) S.days.push(t);
    S.days = S.days.sort().slice(-400);
    save();
    return fresh;
  }

  /* ---------- audio ---------- */
  var synth = window.speechSynthesis || null, voice = null, clipEl = null;
  function pickVoice() {
    if (!synth) return;
    var vs = synth.getVoices().filter(function (v) { return /^en(-|_|$)/i.test(v.lang); });
    var pref = [/samantha/i, /google us english/i, /aria/i, /jenny/i, /en-us/i];
    voice = null;
    for (var i = 0; i < pref.length && !voice; i++) voice = vs.find(function (v) { return pref[i].test(v.name) || pref[i].test(v.lang); }) || null;
    voice = voice || vs.find(function (v) { return v.localService; }) || vs[0] || null;
  }
  if (synth) { pickVoice(); if ("onvoiceschanged" in synth) synth.onvoiceschanged = pickVoice; }
  function stopAudio() { if (synth) synth.cancel(); if (clipEl) { clipEl.pause(); clipEl = null; } }
  /* parts: [{ key: "sound-c", text: "kuh", rate: 0.6 }, ...]; plays in order. A key with a recorded clip plays the clip. */
  function play(parts, done) {
    stopAudio();
    if (!S.sound) { if (done) done(); return; }
    var i = 0;
    (function next() {
      if (i >= parts.length) { if (done) done(); return; }
      var p = typeof parts[i] === "string" ? { text: parts[i] } : parts[i]; i++;
      if (p.key && CLIPS[p.key]) {
        clipEl = new Audio(CLIPS[p.key]);
        clipEl.onended = next; clipEl.onerror = function () { speakOne(p, next); };
        clipEl.play().catch(function () { speakOne(p, next); });
      } else speakOne(p, next);
    })();
  }
  function speakOne(p, next) {
    if (!synth || !window.SpeechSynthesisUtterance) { setTimeout(next, 10); return; }
    var u = new SpeechSynthesisUtterance(p.text);
    if (voice) u.voice = voice;
    u.lang = voice ? voice.lang : "en-US";
    u.rate = p.rate || 0.85; u.pitch = 1.1;
    var t = setTimeout(next, 6000); /* some browsers never fire onend */
    u.onend = u.onerror = function () { clearTimeout(t); setTimeout(next, p.pause || 120); };
    synth.speak(u);
  }
  function up(l) { return l.toUpperCase(); }
  function letterLine(L) {
    return L.end ? [{ key: "letter-" + L.l, text: up(L.l) + ". " + up(L.l) + " is at the end of " + L.word + ". " + L.word + "." }]
      : [{ key: "letter-" + L.l, text: up(L.l) + ". " + up(L.l) + " is for " + L.word + ". " + L.word + "." }];
  }
  function setSound(on) {
    S.sound = on; save(); if (!on) stopAudio();
    sndBtn.setAttribute("aria-pressed", on ? "true" : "false");
    sndBtn.setAttribute("aria-label", on ? "Sound on" : "Sound off");
    sndBtn.firstElementChild.textContent = on ? "🔊" : "🔇";
  }

  /* ---------- shared view bits ---------- */
  function setTab(t) {
    document.querySelectorAll(".tabs a").forEach(function (a) { if (a.dataset.tab === t) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  }
  function focusTitle() {
    /* The tab title stays the same on purpose, so analytics never shows which letters or words a child played. */
    var h = app.querySelector("h1,h2"); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
    window.scrollTo(0, 0);
  }
  /* Breadcrumb: Codex Hive Labs › Hive Academy › Hive Phonics › [activity] › [item] */
  function crumbs(trail) {
    var ol = document.getElementById("bc"), mod = ol.querySelector(".bc__item--module a");
    ol.querySelectorAll(".bc__item--extra").forEach(function (li) { li.remove(); });
    if (trail.length) mod.removeAttribute("aria-current"); else mod.setAttribute("aria-current", "page");
    trail.forEach(function (c) {
      var li = document.createElement("li"); li.className = "bc__item bc__item--extra";
      var el = document.createElement(c.href ? "a" : "span");
      if (c.href) el.href = c.href; else { el.className = "cur"; el.setAttribute("aria-current", "page"); }
      el.textContent = c.t; el.title = c.t; li.appendChild(el); ol.appendChild(li);
    });
    var nav = ol.closest(".bc");
    nav.classList.toggle("bc--deep", trail.length > 0);
    nav.classList.toggle("bc--deeper", trail.length > 1);
  }
  function starPill() {
    var n = total();
    return '<a class="pill" href="#/stars"><span><span aria-hidden="true">★</span> <b>' + n + "</b> star" + (n === 1 ? "" : "s") + "</span><span>· <b>" + streak() + "</b>-day streak</span></a>";
  }
  function wordHtml(w, l, end) {
    /* Highlight the focus letter inside the picture word. */
    var i = end ? w.lastIndexOf(l) : w.indexOf(l);
    if (i < 0) return esc(w);
    return esc(w.slice(0, i)) + '<mark>' + esc(w[i]) + "</mark>" + esc(w.slice(i + 1));
  }
  function noVoiceNote() {
    return synth ? "" : '<p class="note">This browser has no built-in voice, so say the sounds out loud together. Everything else still works.</p>';
  }

  /* ---------- home ---------- */
  function home() {
    setTab(""); crumbs([]);
    var h = '<div class="intro"><div><h1>Letters, sounds &amp; first words</h1>' +
      "<p>Tap a letter to hear it, slide sounds together to read little words, and find the sound a picture starts with. Big buttons for small hands, and a star for everything learned.</p></div>" + starPill() + "</div>" +
      noVoiceNote() +
      '<ul class="acts" aria-label="Activities">' +
      act("#/letters", "🔤", "Letter sounds", "A to Z. Tap a letter, hear it, and meet its picture word.", count(S.heard), 26, "c1") +
      act("#/blend", "🐝", "Blend it", "Slide c-a-t together with the bee and read a word.", count(S.blended), WORDLIST.length, "c2") +
      act("#/game", "🎯", "First sound", "Look at the picture. Which letter does it start with?", count(S.first), 26, "c3") +
      "</ul>" +
      '<section class="tips" aria-labelledby="tips-t"><h2 id="tips-t" class="sec">Tips for grown-ups</h2><ul>' +
      "<li>Keep it short: five happy minutes beats twenty tired ones.</li>" +
      "<li>Say the sound, not the letter name, when you can: <b>c</b> says “k” as in <b>c</b>at.</li>" +
      "<li>Point under each letter as you slide the sounds together, then say the word fast.</li>" +
      "<li>Cheer the trying, not just the right answers.</li></ul></section>";
    app.innerHTML = h; focusTitle();
  }
  function act(href, em, t, d, n, max, cls) {
    return '<li><a class="act ' + cls + '" href="' + href + '"><span class="act__em" aria-hidden="true">' + em + "</span><h2>" + t + "</h2><p>" + d + "</p>" +
      '<span class="meter" role="img" aria-label="' + n + " of " + max + ' stars"><span style="width:' + Math.round(100 * n / max) + '%"></span></span><span class="act__n">★ ' + n + " / " + max + "</span></a></li>";
  }

  /* ---------- letter sounds ---------- */
  function letters() {
    setTab("letters"); crumbs([{ t: "Letter sounds" }]);
    var h = '<div class="intro"><div><h1>Letter sounds</h1><p>Tap a letter to hear it and see its picture word. Every new letter earns a star.</p></div>' +
      '<span class="pill"><span><b>' + count(S.heard) + "</b> of 26 letters</span></span></div>" + noVoiceNote() + '<ul class="abc" aria-label="Alphabet">';
    LETTERS.forEach(function (L) {
      var got = S.heard[L.l];
      h += '<li><a class="abc__k' + (got ? " got" : "") + '" href="#/letter/' + L.l + '" data-letter="' + L.l + '" aria-label="' + up(L.l) + ", " + L.word + (got ? ", star earned" : "") + '">' +
        '<span class="abc__l">' + up(L.l) + L.l + '</span><span class="abc__em" aria-hidden="true">' + L.em + "</span>" + (got ? '<span class="abc__s" aria-hidden="true">★</span>' : "") + "</a></li>";
    });
    app.innerHTML = h + "</ul>"; focusTitle();
  }
  function letterCard(l) {
    var L = letter(l); if (!L) { location.hash = "#/letters"; return; }
    setTab("letters"); crumbs([{ t: "Letter sounds", href: "#/letters" }, { t: up(l) }]);
    var fresh = award("heard", l);
    var i = LETTERS.indexOf(L), prev = LETTERS[(i + 25) % 26], next = LETTERS[(i + 1) % 26];
    app.innerHTML = '<div class="card">' +
      '<div class="card__l" aria-hidden="true">' + up(l) + "<span>" + l + "</span></div>" +
      '<button type="button" class="card__pic" id="hear" aria-label="Hear ' + up(l) + " for " + L.word + '"><span aria-hidden="true">' + L.em + "</span></button>" +
      '<h1 class="card__w">' + wordHtml(L.word, l, L.end) + "</h1>" +
      '<p class="card__say">' + (L.end ? "<b>" + up(l) + "</b> is at the end of <b>" + L.word + "</b>. It says “ks”." : "<b>" + up(l) + "</b> is for <b>" + L.word + "</b>.") + "</p>" +
      (fresh ? '<p class="feedback ok" role="status">★ New star!</p>' : '<p class="feedback ok">★ Star earned</p>') +
      '<div class="btns"><button type="button" class="btn" id="again"><span class="em" aria-hidden="true">🔊</span> Hear it again</button>' +
      '<button type="button" class="btn btn--ghost" id="snd1"><span class="em" aria-hidden="true">👄</span> Just the sound</button></div>' +
      '<div class="nav2"><a class="btn btn--ghost" href="#/letter/' + prev.l + '" data-letter="' + prev.l + '" aria-label="Previous letter, ' + up(prev.l) + '">← ' + up(prev.l) + '</a>' +
      '<a class="btn btn--ghost" href="#/letters">All letters</a>' +
      '<a class="btn btn--ghost" href="#/letter/' + next.l + '" data-letter="' + next.l + '" aria-label="Next letter, ' + up(next.l) + '">' + up(next.l) + " →</a></div></div>";
    var line = function () { play(letterLine(L)); bounce(document.getElementById("hear")); };
    document.getElementById("hear").addEventListener("click", line);
    document.getElementById("again").addEventListener("click", line);
    document.getElementById("snd1").addEventListener("click", function () { play([{ key: "sound-" + l, text: SOUND[l], rate: 0.7 }]); });
    announce(up(l) + " is for " + L.word);
    focusTitle();
  }
  function bounce(el) { if (!el || REDUCED) return; el.classList.remove("pop"); void el.offsetWidth; el.classList.add("pop"); }

  /* ---------- blending ---------- */
  function blendList() {
    setTab("blend"); crumbs([{ t: "Blend it" }]);
    var h = '<div class="intro"><div><h1>Blend it</h1><p>Pick a word. Tap each letter to hear its sound, then slide the bee to push the sounds together.</p></div>' +
      '<span class="pill"><span><b>' + count(S.blended) + "</b> of " + WORDLIST.length + " words</span></span></div>" + noVoiceNote();
    Object.keys(WORDS).forEach(function (v) {
      h += '<section class="vg" aria-labelledby="vg-' + v + '"><h2 class="sec" id="vg-' + v + '">' + VOWEL_NAME[v] + ' <span class="vg__ex">' + WORDS[v][0][0].replace(v, "<mark>" + v + "</mark>") + "</span></h2><ul class=\"words\">";
      WORDS[v].forEach(function (w) {
        var got = S.blended[w[0]];
        h += '<li><a class="wd' + (got ? " got" : "") + '" href="#/blend/' + w[0] + '" aria-label="' + w[0].split("").join(" ") + (got ? ", read, star earned" : "") + '">' +
          '<span class="wd__em" aria-hidden="true">' + (got ? w[1] : "❔") + '</span><span class="wd__t">' + w[0].split("").map(function (c) { return c === v ? "<mark>" + c + "</mark>" : c; }).join("") + "</span>" +
          (got ? '<span class="abc__s" aria-hidden="true">★</span>' : "") + "</a></li>";
      });
      h += "</ul></section>";
    });
    app.innerHTML = h; focusTitle();
  }
  function blendWord(w) {
    var W = wordObj(w); if (!W) { location.hash = "#/blend"; return; }
    setTab("blend"); crumbs([{ t: "Blend it", href: "#/blend" }, { t: w }]);
    var ls = w.split(""), idx = WORDLIST.indexOf(W), next = WORDLIST[(idx + 1) % WORDLIST.length];
    var opts = shuffle([W].concat(shuffle(WORDLIST.filter(function (x) { return x.w !== w && x.em !== W.em; })).slice(0, 2)));
    app.innerHTML = '<div class="play"><div class="board">' +
      '<h1 class="board__t">Read the word</h1>' +
      '<p class="how">1. Tap each letter. 2. Slide the bee. 3. Find the picture.</p>' +
      '<div class="track" id="track">' + ls.map(function (c, i) {
        return '<button type="button" class="tile' + (c === W.v ? " tile--v" : "") + '" data-i="' + i + '" aria-label="Letter ' + up(c) + ', hear its sound">' + c + "</button>";
      }).join("") + "</div>" +
      '<div class="slide"><button type="button" class="slide__bee" id="bee" aria-label="Slide the sounds together"><span class="slide__rail" aria-hidden="true"></span><span class="slide__b" aria-hidden="true">🐝</span><span class="slide__lbl">Slide the sounds</span></button></div>' +
      '<h2 class="q">Which picture is it?</h2>' +
      '<div class="pics" role="group" aria-label="Pick the picture">' + opts.map(function (o) {
        return '<button type="button" class="pic" data-w="' + o.w + '" aria-label="' + o.w + '"><span aria-hidden="true">' + o.em + "</span></button>";
      }).join("") + "</div>" +
      '<p class="feedback" id="fb" role="status"></p>' +
      '<div class="btns"><button type="button" class="btn btn--ghost" id="hint"><span class="em" aria-hidden="true">👂</span> Hear the word</button>' +
      '<a class="btn" href="#/blend/' + next.w + '" id="next">Next word →</a></div></div></div>';
    var tiles = [].slice.call(app.querySelectorAll(".tile"));
    tiles.forEach(function (t) {
      t.addEventListener("click", function () { var c = ls[+t.dataset.i]; light(t); play([{ key: "sound-" + c, text: SOUND[c], rate: 0.7 }]); });
    });
    function light(t) { t.classList.add("on"); bounce(t); }
    var bee = document.getElementById("bee"), busy = false;
    bee.addEventListener("click", function () {
      if (busy) return; busy = true;
      bee.classList.remove("go"); void bee.offsetWidth; if (!REDUCED) bee.classList.add("go");
      var parts = ls.map(function (c) { return { key: "sound-" + c, text: SOUND[c], rate: 0.55, pause: 60 }; });
      var k = 0;
      tiles.forEach(function (t) { t.classList.remove("on"); });
      /* Light letters in time with the bee (or all at once when motion is reduced). */
      if (REDUCED) tiles.forEach(light);
      else tiles.forEach(function (t, i) { setTimeout(function () { light(t); }, 250 + i * 650); });
      play(parts, function () { busy = false; });
      if (!S.sound) setTimeout(function () { busy = false; }, 2200);
      announce(ls.join(" "));
    });
    document.getElementById("hint").addEventListener("click", function () { play([{ key: "word-" + w, text: w, rate: 0.8 }]); });
    var fb = document.getElementById("fb"), done = false;
    app.querySelectorAll(".pic").forEach(function (b) {
      b.addEventListener("click", function () {
        if (done) return;
        if (b.dataset.w === w) {
          done = true; b.classList.add("right");
          var fresh = award("blended", w);
          fb.className = "feedback ok"; fb.textContent = "Yes! " + ls.join("-") + ", " + w + "!" + (fresh ? " ★ New star!" : "");
          tiles.forEach(light);
          play([{ key: "word-" + w, text: "Yes! " + w + "!", rate: 0.85 }]);
          document.getElementById("next").focus();
        } else {
          b.classList.remove("wrong"); void b.offsetWidth; b.classList.add("wrong");
          fb.className = "feedback no"; fb.textContent = "That's " + b.dataset.w + ". Slide the bee and listen again.";
          play([{ text: "That's " + b.dataset.w + ". Try again.", rate: 0.85 }]);
        }
      });
    });
    focusTitle();
  }

  /* ---------- first sound game ---------- */
  /* Picture pool: letter-card words plus blend words, minus fox (x is at the end) and words that would clash with c/k. */
  var POOL = LETTERS.filter(function (L) { return !L.end; }).map(function (L) { return { w: L.word, em: L.em, l: L.l }; })
    .concat(WORDLIST.map(function (x) { return { w: x.w, em: x.em, l: x.w[0] }; }))
    .filter(function (p, i, a) { return a.findIndex(function (q) { return q.w === p.w; }) === i; });
  var CLASH = { c: "k", k: "c" };
  var G = null;
  function game() {
    setTab("game"); crumbs([{ t: "First sound" }]);
    if (!G || G.over) {
      app.innerHTML = '<div class="play"><div class="board center">' +
        '<p class="big" aria-hidden="true">🎯</p><h1 class="board__t">Which sound does it start with?</h1>' +
        '<p class="how">Look at the picture and listen to its name. Then tap the letter it starts with. Five pictures a round, and a star the first time you get each letter right.</p>' +
        '<p class="muted">' + count(S.first) + " of 26 first sounds found</p>" + noVoiceNote() +
        '<div class="btns"><button type="button" class="btn" id="start"><span class="em" aria-hidden="true">▶️</span> Start a round</button></div></div></div>';
      document.getElementById("start").addEventListener("click", function () {
        var seen = {}, qs = [];
        shuffle(POOL).forEach(function (p) { if (qs.length < 5 && !seen[p.l]) { seen[p.l] = 1; qs.push(p); } });
        G = { qs: qs, i: 0, right: 0, tries: 0, over: false };
        question();
      });
      focusTitle(); return;
    }
    question();
  }
  function question() {
    var q = G.qs[G.i];
    var wrong = shuffle(LETTERS.map(function (L) { return L.l; }).filter(function (l) { return l !== q.l && l !== CLASH[q.l] && l !== "x" && l !== "q"; })).slice(0, 2);
    var opts = shuffle([q.l].concat(wrong));
    G.tries = 0;
    app.innerHTML = '<div class="play"><div class="board center">' +
      '<div class="dots" role="img" aria-label="Picture ' + (G.i + 1) + " of " + G.qs.length + '">' + G.qs.map(function (_, i) { return '<span class="' + (i < G.i ? "done" : i === G.i ? "now" : "") + '"></span>'; }).join("") + "</div>" +
      '<h1 class="sr-only">Which sound does ' + q.w + " start with?</h1>" +
      '<button type="button" class="card__pic" id="hear" aria-label="Hear the word ' + q.w + '"><span aria-hidden="true">' + q.em + "</span></button>" +
      '<p class="gw"><span class="gw__gap" id="gap" aria-hidden="true">?</span>' + esc(q.w.slice(1)) + "</p>" +
      '<div class="choices" role="group" aria-label="Pick the first letter">' + opts.map(function (l) {
        return '<button type="button" class="lt" data-l="' + l + '" aria-label="' + up(l) + '">' + up(l) + l + "</button>";
      }).join("") + "</div>" +
      '<p class="feedback" id="fb" role="status"></p><div class="btns" id="after"></div></div></div>';
    var ask = function () { play([{ key: "word-" + q.w, text: q.w + ". What sound does " + q.w + " start with?", rate: 0.8 }]); };
    document.getElementById("hear").addEventListener("click", ask);
    ask();
    var fb = document.getElementById("fb"), locked = false;
    app.querySelectorAll(".lt").forEach(function (b) {
      b.addEventListener("click", function () {
        if (locked) return;
        G.tries++;
        if (b.dataset.l === q.l) {
          locked = true; b.classList.add("right");
          document.getElementById("gap").textContent = q.l; document.getElementById("gap").classList.add("got");
          var fresh = G.tries === 1 && award("first", q.l);
          if (G.tries === 1) G.right++;
          fb.className = "feedback ok"; fb.textContent = "Yes! " + q.w + " starts with " + up(q.l) + "." + (fresh ? " ★ New star!" : "");
          play([{ text: "Yes! " + q.w + " starts with " + up(q.l) + ".", rate: 0.85 }]);
          var last = G.i === G.qs.length - 1;
          document.getElementById("after").innerHTML = '<button type="button" class="btn" id="go">' + (last ? "See my round ★" : "Next picture →") + "</button>";
          var go = document.getElementById("go"); go.focus();
          go.addEventListener("click", function () { if (last) roundEnd(); else { G.i++; question(); } });
        } else {
          b.classList.remove("wrong"); void b.offsetWidth; b.classList.add("wrong"); b.disabled = true;
          fb.className = "feedback no"; fb.textContent = "Not " + up(b.dataset.l) + ". Listen again: " + q.w + ".";
          play([{ text: "Not " + up(b.dataset.l) + ". Listen. " + q.w + ".", rate: 0.8 }]);
        }
      });
    });
    focusTitle();
  }
  function roundEnd() {
    G.over = true;
    var n = G.right, m = G.qs.length;
    app.innerHTML = '<div class="play"><div class="board center win">' +
      '<p class="big" aria-hidden="true">' + (n === m ? "🏆" : n >= 3 ? "🌟" : "🐝") + '</p><h1 class="board__t">' + (n === m ? "Perfect round!" : "Great listening!") + "</h1>" +
      "<p>You got <b>" + n + " of " + m + "</b> on the first try.</p><p class=\"muted\">" + count(S.first) + " of 26 first sounds found</p>" +
      '<div class="btns"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="#/">Home</a></div></div></div>';
    play([{ text: n === m ? "Perfect round! Hooray!" : "Great listening!" }]);
    document.getElementById("again").addEventListener("click", function () { G = null; game(); document.getElementById("start").click(); });
    focusTitle();
  }

  /* ---------- stars ---------- */
  function stars() {
    setTab("stars"); crumbs([{ t: "My stars" }]);
    var h = '<div class="intro"><div><h1>My stars</h1><p>' + total() + " of " + MAX + " stars so far. Saved only on this device.</p></div></div>" +
      '<div class="prog">' +
      stat(count(S.heard), "of 26 letters heard") + stat(count(S.blended), "of " + WORDLIST.length + " words read") + stat(count(S.first), "of 26 first sounds") + stat(streak(), "day streak") + "</div>" +
      '<h2 class="sec">Letter by letter</h2><p class="muted">🔊 heard the letter card · 🎯 found it as a first sound</p><ul class="abc abc--sm" aria-label="Letters progress">';
    LETTERS.forEach(function (L) {
      var a = !!S.heard[L.l], b = !!S.first[L.l];
      h += '<li><a class="abc__k' + (a && b ? " got" : "") + '" href="#/letter/' + L.l + '" data-letter="' + L.l + '" aria-label="' + up(L.l) + ": " + (a ? "heard" : "not heard yet") + ", " + (L.end ? "not in the first-sound game" : b ? "first sound found" : "first sound not found yet") + '">' +
        '<span class="abc__l">' + up(L.l) + L.l + '</span><span class="marks" aria-hidden="true"><span class="' + (a ? "on" : "") + '">🔊</span><span class="' + (b ? "on" : "") + '">' + (L.end ? "–" : "🎯") + "</span></span></a></li>";
    });
    h += '</ul><div class="btns"><button type="button" class="btn btn--danger" id="reset">Start over</button></div>';
    app.innerHTML = h;
    document.getElementById("reset").addEventListener("click", function () {
      if (!confirm("Clear all stars and the streak on this device?")) return;
      S.heard = {}; S.blended = {}; S.first = {}; S.days = []; save(); stars(); announce("Progress cleared");
    });
    focusTitle();
  }
  function stat(n, t) { return '<div class="stat"><b>' + n + "</b><span>" + t + "</span></div>"; }

  /* ---------- router ---------- */
  var keepAudio = false;
  function route() {
    if (!keepAudio) stopAudio();
    keepAudio = false;
    var h = location.hash.replace(/^#\/?/, "").split("/");
    if (h[0] !== "game" && G && !G.over) G = null;
    if (h[0] === "letters") letters();
    else if (h[0] === "letter") letterCard((h[1] || "").toLowerCase());
    else if (h[0] === "blend" && h[1]) blendWord(h[1].toLowerCase());
    else if (h[0] === "blend") blendList();
    else if (h[0] === "game") game();
    else if (h[0] === "stars") stars();
    else home();
  }
  /* Speak a letter card inside the tap itself (mobile browsers only allow speech from a user gesture). */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-letter]");
    if (a) { var L = letter(a.dataset.letter); if (L) { play(letterLine(L)); keepAudio = true; setTimeout(function () { keepAudio = false; }, 400); } }
  });
  sndBtn.addEventListener("click", function () { setSound(!S.sound); announce(S.sound ? "Sound on" : "Sound off"); });
  setSound(S.sound);
  window.addEventListener("hashchange", route);
  route();

  /* Offline: cache this module after the first visit (network first, so updates still arrive). */
  if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "127.0.0.1" || location.hostname === "localhost")) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("sw.js").catch(function () {}); });
  }
})();
