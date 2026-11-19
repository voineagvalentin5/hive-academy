"""Build /modules/rosetta-logos/index.html from the original Rosetta Logos module.
Rebrands chrome only (palette, fonts, header, footer, shared nav). Data, script logic and text are untouched."""
import re, sys, pathlib
SRC = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "modules/rosetta-logos/index.html"
s = SRC.read_text(encoding="utf-8")
idx = (ROOT / "index.html").read_text(encoding="utf-8")

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
#chl-lab-nav{margin:0 calc(-1*clamp(16px,3vw,32px))}
h1,h2,.concept-name,.find .panel h3{letter-spacing:-.01em}
h1{font-weight:700}h2{font-weight:650}.find .panel h3{font-weight:600}
h1 em{font-style:normal;background:linear-gradient(180deg,#f0c77a,#c99a4b 60%,#9b6f2c);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.ac-head{margin:0 calc(-1*clamp(16px,3vw,32px));padding:14px clamp(16px,3vw,32px);border-bottom:1px solid rgba(201,154,75,.22);
  background:radial-gradient(60% 140% at 85% 0%,rgba(201,154,75,.14),transparent 60%),linear-gradient(180deg,#16171c,#111216)}
.ac-head__in{max-width:1180px;margin:0 auto;display:flex;align-items:center;gap:16px}
.ac-head__logo{display:block;flex:none}.ac-head__logo img{display:block;width:220px;height:auto}
.ac-head__mod{margin-left:auto;text-align:right;font:650 11px/1.5 var(--display);letter-spacing:.18em;text-transform:uppercase;color:var(--gold)}
.ac-head__mod a{color:var(--dim);text-decoration:none;letter-spacing:.12em}.ac-head__mod a:hover{color:var(--goldhi)}
.kick{font-family:var(--display);font-weight:650;letter-spacing:.2em;color:var(--gold)}
.prelim{display:flex;gap:10px;align-items:flex-start;font-size:13.5px;color:var(--dim);border-left:2px solid var(--gold);padding:8px 12px;background:rgba(201,154,75,.07);border-radius:0 3px 3px 0;max-width:80ch}
.prelim b{color:var(--paper);font-weight:600}
.plate{border-color:rgba(201,154,75,.22)}
footer.bf img{height:26px;filter:none}
footer.bf a{color:var(--gold2);text-decoration:none}
@media (max-width:560px){.ac-head__logo img{width:170px}.ac-head__mod{font-size:10px;letter-spacing:.12em}}
'''
head = sub1("</style>\n</head>", chrome_css + "</style>\n</head>", head)

# shared nav, copied verbatim from the Academy home page
nav = re.search(r"<!-- chl-lab-nav -->.*?<!-- /chl-lab-nav -->", idx, re.S).group(0)
brand = re.search(r'<div class="brandbar">.*?</div></div></div>', head, re.S).group(0)
head = sub1(brand, nav + '''
<div class="ac-head"><div class="ac-head__in">
  <a class="ac-head__logo" href="/" aria-label="Hive Academy home"><img src="/assets/brand/academy-wordmark-dark-360.webp" srcset="/assets/brand/academy-wordmark-dark-360.webp 1x, /assets/brand/academy-wordmark-dark-720.webp 2x" width="360" height="53" alt="Hive Academy, a Codex Hive division"></a>
  <div class="ac-head__mod">Module · Rosetta Logos<br><a href="/">← Hive Academy</a></div>
</div></div>''', head)
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
OUT.write_text(head + script, encoding="utf-8")
print("wrote", OUT, len(head + script))
