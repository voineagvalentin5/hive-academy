"""Build /modules/rosetta-logos/index.html from the original Rosetta Logos module.
Rebrands chrome only (palette, fonts, header, footer, shared nav). Data, script logic and text are untouched."""
import re, sys, pathlib
SRC = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "modules/rosetta-logos/index.html"
s = SRC.read_text(encoding="utf-8")

def sub1(old, new, txt, count=1):
    n = txt.count(old)
    assert n == count, (old[:80], n)
    return txt.replace(old, new)

i = s.find("<script")
head, script = s[:i], s[i:]

# ---- head meta: match the existing Academy pages ----
head = sub1('<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Rosetta Logos · Hive Academy</title>',
'''<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
<title>Rosetta Logos · Hive Academy</title>
<meta name="description" content="Rosetta Logos, a Hive Academy module: an interactive look at how languages share a shape of meaning. Preliminary, not peer-reviewed.">
<meta name="theme-color" content="#111216">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/montserrat-var.woff2" as="font" type="font/woff2" crossorigin>''', head)
# fonts: drop Jost (display -> Academy Montserrat); keep IBM Plex (canvas labels and numbers use it)
head = sub1("family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Jost:wght@400;500;600&display=swap",
            "family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap", head)
# palette + fonts
head = sub1('''  --ink:#121214; --plate:#1b1c20; --rule:#3b3c42; --paper:#f2eee4; --dim:#a9a69d; --mean:#e0a42a; --warn:#e8875a;
  --display:"Jost","Segoe UI",system-ui,sans-serif; --body:"IBM Plex Sans",system-ui,sans-serif;''',
'''  /* Rebranded to the Hive Academy gold-and-charcoal look. */
  --ink:#111216; --plate:#1b1c22; --rule:#3a3428; --paper:#ece8e1; --dim:#a7a29a; --mean:#e0a42a; --warn:#e8875a;
  --gold:#c99a4b; --gold2:#e0b56a; --goldhi:#ffd36b;
  --display:"Montserrat",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif; --body:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;''', head)
head = sub1(":root{", '@font-face{font-family:"Montserrat";src:url(/assets/fonts/montserrat-var.woff2) format("woff2");font-weight:100 900;font-display:swap}\n:root{', head)
# scope the module's view tabs so they don't style the shared nav
head = sub1("\nnav{display:flex;", "\nnav.views{display:flex;", head)
head = sub1("\nnav a{", "\nnav.views a{", head)
head = sub1("\nnav a:hover{", "\nnav.views a:hover{", head)
head = sub1('\nnav a[aria-current="page"]{color:var(--ink)', '\nnav.views a[aria-current="page"]{color:var(--ink)', head)
head = sub1('\nnav a[aria-current="page"]{color:#121214}', '\nnav.views a[aria-current="page"]{color:#111216}', head)
head = sub1('<nav aria-label="Views">', '<nav class="views" aria-label="Views">', head)
# warm the hard-coded rule tint used in CSS
head = head.replace("rgba(59,60,66,", "rgba(58,52,40,")

# Academy chrome CSS
chrome_css = '''
/* Hive Academy chrome */
h1,h2,.concept-name,.find .panel h3{letter-spacing:-.01em}
h1{font-weight:700}h2{font-weight:650}.find .panel h3{font-weight:600}
h1 em{font-style:normal;background:linear-gradient(180deg,#f0c77a,#c99a4b 60%,#9b6f2c);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.kick{font-family:var(--display);font-weight:650;letter-spacing:.2em;color:var(--gold)}
.prelim{display:flex;gap:10px;align-items:flex-start;font-size:13.5px;color:var(--dim);border-left:2px solid var(--gold);padding:8px 12px;background:rgba(201,154,75,.07);border-radius:0 3px 3px 0;max-width:80ch}
.prelim b{color:var(--paper);font-weight:600}
.plate{border-color:rgba(201,154,75,.22)}
footer.bf img{height:26px;filter:none}
footer.bf a{color:var(--gold2);text-decoration:none}
'''
head = sub1("</style>\n</head>", chrome_css + "</style>\n</head>", head)

# Breadcrumb + compact module bar (replaces the stacked Labs nav + Academy wordmark bar)
ROSETTA_BC = r'''
<style id="rl-appbar">
.bc,.top{margin-left:calc(-1 * clamp(16px,3vw,32px));margin-right:calc(-1 * clamp(16px,3vw,32px))}
.top{border-bottom:1px solid rgba(201,154,75,.28);background:#14151a;position:relative}
.top__in{max-width:1180px;margin:0 auto;padding:8px 24px;display:flex;align-items:center;gap:14px;min-width:0}
.top__home{display:flex;align-items:center;gap:12px;color:#ece8e1;text-decoration:none;flex:none}
.top__home img{width:40px;height:40px;display:block}
.top__name{display:block;font:750 20px/1.1 "Montserrat",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;white-space:nowrap;color:#ece8e1}
.top .views{display:flex;flex-wrap:nowrap;align-items:center;gap:4px;margin-left:auto;min-width:0;overflow-x:auto;scrollbar-width:none;flex:1;justify-content:flex-end;-webkit-overflow-scrolling:touch}
.top .views a{white-space:nowrap;flex:none}.top .views::-webkit-scrollbar{display:none}
@media (max-width:560px){
  .top__in{padding:8px 12px;gap:8px}
  .top__home .top__name{display:none}
  .top__home img{width:36px;height:36px}
  .top .views{justify-content:flex-start}
}
</style>
<!-- chl-bc -->
<style id="chl-bc">
:root{--chl-nav-h:calc(52px + env(safe-area-inset-top,0px))}
.bc,.bc *{box-sizing:border-box}
.bc__badge{display:inline-block;font:700 10px/1 "Montserrat",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase;background:linear-gradient(180deg,#e2b768,#c99a4b);color:#16130d;padding:5px 9px;border-radius:999px;flex:none}
.bc{position:sticky;top:0;z-index:40;background:#141414;border-bottom:1px solid rgba(224,165,38,.42);padding-top:env(safe-area-inset-top,0px);color:#e9e6df;-webkit-text-size-adjust:100%;overflow:hidden}
.bc__in{max-width:1180px;margin:0 auto;padding:0 24px;height:52px;display:flex;align-items:center;gap:12px;min-width:0}
.bc__list{display:flex;align-items:center;min-width:0;flex:1;list-style:none;margin:0;padding:0;font:650 15px/1.2 "Montserrat",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;white-space:nowrap}
.bc__item{display:flex;align-items:center;min-width:0;flex:none}
.bc__item+.bc__item::before{content:"›";content:"›"/"";color:#8f8778;font-size:20px;line-height:1;margin:0 10px;flex:none}
.bc__item a,.bc__item span.cur{display:inline-flex;align-items:center;gap:9px;min-height:44px;color:#e0a526;text-decoration:none;border-radius:6px;padding:0 2px}
.bc__item a:hover{color:#ffd36b;text-decoration:underline;text-underline-offset:4px}
.bc__item [aria-current="page"],.bc__item span.cur{color:#f3f0ea}
.bc__item a[aria-current="page"]:hover{color:#fff}
.bc__item a:focus-visible{outline:2px solid #e0a526;outline-offset:2px}
.bc__item--home a{color:#f3f0ea}
.bc__item--home img{height:28px;width:auto;display:block;max-width:none}
.bc__labs{color:#e0a526}
.bc__dots{display:none}
.bc__item--module,.bc__item--extra{flex:0 1 auto}
.bc__item--module a,.bc__item--extra a,.bc__item--extra span.cur{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:44px}
.bc__item--extra:last-child{flex-shrink:1;min-width:3em}
.bc__item--module{flex-shrink:3;min-width:2.5em}
@media (max-width:560px){
  .bc__in{padding:0 12px;gap:8px}
  .bc__list{font-size:14px}
  .bc__item+.bc__item::before{margin:0 6px}
  .bc__item--home .bc__t{display:none}
  .bc--deep .bc__item--academy .bc__t{display:none}
  .bc--deep .bc__item--academy .bc__dots{display:inline;padding:0 6px;font-size:18px}
  .bc--deep .bc__badge{display:none}
  .bc__badge{font-size:9px;padding:4px 7px;letter-spacing:.12em}
  .bc__item--module{flex-shrink:0}
  .bc__item--academy{flex:0 1 auto;min-width:2.2em}
  .bc__item--academy a{min-width:0;overflow:hidden}
  .bc__item--academy .bc__t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .bc--deep .bc__item--module{flex-shrink:0}
  .bc--deeper .bc__item--module{display:none}
}
</style>
<nav class="bc" aria-label="Breadcrumb">
  <div class="bc__in">
    <ol class="bc__list" id="bc">
      <li class="bc__item bc__item--home"><a href="https://codex-hive.com" aria-label="Codex Hive Labs, codex-hive.com"><picture><source type="image/webp" srcset="/chl-assets/codex-hive-mark-1x.webp 1x, /chl-assets/codex-hive-mark-2x.webp 2x, /chl-assets/codex-hive-mark-3x.webp 3x"><img src="/chl-assets/codex-hive-mark-1x.png" srcset="/chl-assets/codex-hive-mark-1x.png 1x, /chl-assets/codex-hive-mark-2x.png 2x, /chl-assets/codex-hive-mark-3x.png 3x" width="26" height="32" alt="" decoding="async"></picture><span class="bc__t">Codex Hive <span class="bc__labs">Labs</span></span></a></li>
      <li class="bc__item bc__item--academy"><a href="/" aria-label="Hive Academy"><span class="bc__t">Hive Academy</span><span class="bc__dots" aria-hidden="true">…</span></a></li>
      <li class="bc__item bc__item--module"><a href="/modules/rosetta-logos/" aria-current="page">Rosetta Logos</a></li>
    </ol>
    <span class="bc__badge">Preview</span>
  </div>
</nav>
<!-- /chl-bc -->
<header class="top">
  <div class="top__in">
    <a class="top__home" href="/modules/rosetta-logos/" aria-label="Rosetta Logos">
      <img src="/assets/img/rosetta-logos-emblem-240.webp" srcset="/assets/img/rosetta-logos-emblem-240.webp 1x, /assets/img/rosetta-logos-emblem-480.webp 2x" width="40" height="40" alt="">
      <span class="top__name">Rosetta Logos</span>
    </a>
    <nav class="views" aria-label="Views">
      <a href="#chart">Chart</a><a href="#languages">Languages</a><a href="#concepts">Concepts</a><a href="#root">Root</a><a href="#world">World</a><a href="#findings">Findings</a>
    </nav>
  </div>
</header>
'''
brand = re.search(r'<div class="brandbar">.*?</div></div></div>', head, re.S).group(0)
# If a views nav is already in the source header, drop it; the compact bar carries the tabs.
head = re.sub(
    r'\s*<nav class="views" aria-label="Views">.*?</nav>',
    "",
    head,
    count=1,
    flags=re.S,
)
head = sub1(brand, ROSETTA_BC, head)
# The in-page kick is redundant once the breadcrumb names Hive Academy / Rosetta Logos.
head = head.replace('<p class="kick">Hive Academy · Module</p>\n      ', "", 1)

# preliminary note (no new claims)
head = sub1('  <div class="facts" id="facts"></div>',
'''  <p class="prelim" role="note"><span><b>Preliminary.</b> This is an early research module. Its findings are preliminary and have not been peer-reviewed.</span></p>
  <div class="facts" id="facts"></div>''', head)
# footer: Academy wordmark instead of the embedded logo
head, n = re.subn(r'<footer class="bf"><img src="data:image/webp;base64,[A-Za-z0-9+/=]+" alt="">',
    '<footer class="bf"><img src="/assets/brand/academy-wordmark-dark-360.webp" width="180" height="26" alt="">', head)
assert n == 1
head = sub1("<span>Valentin Voineag</span></footer>", '<span>Valentin Voineag</span><span>© 2026 Codex Hive Labs LLC · <a href="https://codex-hive.com">codex-hive.com</a></span></footer>', head)

# ---- script: only the tab selector and UI chrome colours ----
script = sub1('document.querySelectorAll("nav a")', 'document.querySelectorAll("nav.views a")', script)
for a, b in [('"#121214"', '"#111216"'), ('"#1b1c20"', '"#1b1c22"'), ('"#3b3c42"', '"#3a3428"'),
             ('"#f2eee4"', '"#ece8e1"'), ('"#a9a69d"', '"#a7a29a"'),
             ('rgba(59,60,66,', 'rgba(58,52,40,'), ('rgba(242,238,228,', 'rgba(236,232,225,'), ('rgba(169,166,157,', 'rgba(167,162,154,')]:
    script = script.replace(a, b)

OUT.parent.mkdir(parents=True, exist_ok=True)
# Keep the same Google Analytics tag as the other Academy pages.
if "G-DW4D6JPPB4" not in head:
    head = head.replace("</head>", (
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-DW4D6JPPB4"></script>\n'
        "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
        "gtag('js',new Date());gtag('config','G-DW4D6JPPB4');</script>\n</head>"
    ), 1)

OUT.write_text(head + script, encoding="utf-8")
print("wrote", OUT, len(head + script))
