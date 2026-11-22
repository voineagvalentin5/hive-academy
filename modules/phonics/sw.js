/* Hive Phonics offline support. Network first (so a new version shows up right away), cached copy when offline.
   Only same-origin GET requests are cached; analytics and other sites are never stored. */
var CACHE = "hive-phonics-v1";
var CORE = ["./", "index.html", "app.css", "app.js", "/assets/fonts/montserrat-var.woff2",
  "/chl-assets/codex-hive-mark-1x.webp", "/chl-assets/codex-hive-mark-2x.webp", "/chl-assets/codex-hive-mark-3x.webp",
  "/chl-assets/codex-hive-mark-1x.png", "/assets/brand/academy-wordmark-dark-360.webp", "/favicon.ico"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return Promise.all(CORE.map(function (u) { return c.add(u).catch(function () {}); })); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k.indexOf("hive-phonics-") === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin) return;
  e.respondWith(fetch(r).then(function (res) {
    if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(r, copy); }); }
    return res;
  }).catch(function () {
    return caches.match(r, { ignoreSearch: true }).then(function (m) { return m || (r.mode === "navigate" ? caches.match("index.html") : Response.error()); });
  }));
});
