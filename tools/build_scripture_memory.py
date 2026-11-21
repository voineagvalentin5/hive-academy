"""Build /modules/scripture-memory/data/stories.json (Hive Kids Bible).

Usage: python3 tools/build_scripture_memory.py <engwebp_vpl.txt> <hive-scribe kjv dir>

Verse text is never typed by hand. Each key verse is read from the public-domain
source files and every memory text is checked to be an exact, unchanged run of
words from that verse. If a check fails the build stops.

  WEB: eBible.org "engwebp" (World English Bible, 2020 stable text), engwebp_vpl.txt
  KJV: eBible.org "eng-kjv" (1769 text), as packaged in Hive Scribe data/kjv/*.json.gz.
       Brackets that mark words the translators supplied are removed; words are unchanged.

The module page also copies the shared Codex Hive Labs nav from /index.html,
so it stays identical to the Academy home page.
"""
import gzip, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "modules/scripture-memory/data/stories.json"
PAGE = ROOT / "modules/scripture-memory/index.html"
WEB_SRC = pathlib.Path(sys.argv[1])
KJV_DIR = pathlib.Path(sys.argv[2])

# book: (display name, WEB vpl code, Scribe KJV file, OSIS)
BOOKS = {
    "Genesis": ("GEN", "Gen", "Gen"), "Exodus": ("EXO", "Exod", "Exod"),
    "1 Samuel": ("1SA", "1Sam", "1Sam"), "Daniel": ("DAN", "Dan", "Dan"),
    "Jonah": ("JON", "Jonah", "Jonah"), "Luke": ("LUK", "Luke", "Luke"),
    "Mark": ("MAR", "Mark", "Mark"), "John": ("JOH", "John", "John"),
    "Matthew": ("MAT", "Matt", "Matt"),
}

# Retellings are short and kid-level, and stay with what each passage says.
STORIES = [
    dict(id="creation", title="God Makes the World", testament="OT", passage="Genesis 1:1–2:3",
         retelling="In the beginning, God made the heavens and the earth. God spoke, and there was light. "
                   "Over six days God made the sky, the land and the seas, plants, the sun, moon and stars, fish, birds and animals, "
                   "and then he made people in his own image. God saw everything he had made, and it was very good, and on the seventh day he rested.",
         book="Genesis", ch=1, v=1, web="In the beginning, God created the heavens and the earth.",
         kjv="In the beginning God created the heaven and the earth."),
    dict(id="noah", title="Noah and the Ark", testament="OT", passage="Genesis 6:9–9:17",
         retelling="Noah walked with God. God told Noah to build a big ark and to bring his family and the animals inside. "
                   "Rain fell for forty days and forty nights, and the flood covered the earth, but God kept everyone in the ark safe. "
                   "Afterward, God put his rainbow in the clouds as a sign of his promise never again to destroy the earth with a flood.",
         book="Genesis", ch=9, v=13, web="I set my rainbow in the cloud, and it will be a sign of a covenant between me and the earth.",
         kjv="I do set my bow in the cloud, and it shall be for a token of a covenant between me and the earth."),
    dict(id="abraham", title="God's Promise to Abraham", testament="OT", passage="Genesis 12:1–7; 15:5–6; 18:1–14; 21:1–3",
         retelling="God told Abraham to leave his home and go to a land God would show him, and Abraham went. "
                   "God told him to look at the stars and promised him children as many as the stars, and Abraham believed God. "
                   "Abraham and Sarah were very old, but the LORD said Sarah would have a son. God kept his promise, and their son Isaac was born.",
         book="Genesis", ch=18, v=14, web="Is anything too hard for the LORD?", kjv="Is any thing too hard for the LORD?"),
    dict(id="joseph", title="Joseph Forgives His Brothers", testament="OT", passage="Genesis 37; 39–45; 50:15–21",
         retelling="Joseph's brothers were jealous of him, and they sold him, and he was taken to Egypt. "
                   "Even in prison, the LORD was with Joseph. God helped Joseph explain Pharaoh's dreams, and Pharaoh put him in charge of storing food before a famine. "
                   "When his brothers came to Egypt for food, Joseph forgave them and was kind to them.",
         book="Genesis", ch=50, v=20, web="As for you, you meant evil against me, but God meant it for good",
         kjv="But as for you, ye thought evil against me; but God meant it unto good"),
    dict(id="red-sea", title="Moses and the Red Sea", testament="OT", passage="Exodus 14",
         retelling="God led his people, Israel, out of Egypt, but Pharaoh and his army chased them to the edge of the sea. "
                   "Moses told the people not to be afraid. Moses stretched out his hand over the sea, the LORD sent a strong east wind, "
                   "and the people walked through the sea on dry ground. That day the LORD saved Israel from the Egyptians.",
         book="Exodus", ch=14, v=14, web="The LORD will fight for you, and you shall be still.",
         kjv="The LORD shall fight for you, and ye shall hold your peace."),
    dict(id="david", title="David and Goliath", testament="OT", passage="1 Samuel 17",
         retelling="A giant named Goliath dared Israel's army to fight him, and the soldiers were afraid. "
                   "David, a young shepherd, said the LORD who saved him from the lion and the bear would save him from this Philistine too. "
                   "David took his sling and five smooth stones and went out in the name of the LORD. His stone struck Goliath, and the giant fell.",
         book="1 Samuel", ch=17, v=47, web="the battle is the LORD’s", kjv="the battle is the LORD’s"),
    dict(id="daniel", title="Daniel and the Lions", testament="OT", passage="Daniel 6",
         retelling="Daniel prayed to God three times every day, even after a new law said no one could pray to anyone but the king. "
                   "Daniel was thrown into a den of lions. God sent his angel and shut the lions' mouths. "
                   "In the morning Daniel was taken out of the den, and he was not hurt at all, because he trusted in his God.",
         book="Daniel", ch=6, v=22, web="My God has sent his angel, and has shut the lions’ mouths, and they have not hurt me",
         kjv="My God hath sent his angel, and hath shut the lions’ mouths, that they have not hurt me"),
    dict(id="jonah", title="Jonah and the Big Fish", testament="OT", passage="Jonah 1–3",
         retelling="God told Jonah to go to the city of Nineveh, but Jonah ran away on a ship. A great storm came, Jonah was thrown into the sea, "
                   "and the LORD sent a huge fish to swallow him. Jonah prayed inside the fish for three days and three nights, and the fish put him out on dry land. "
                   "Then Jonah went to Nineveh, the people turned from their evil ways, and God had mercy on them.",
         book="Jonah", ch=2, v=9, web="Salvation belongs to the LORD.", kjv="Salvation is of the LORD."),
    dict(id="jesus-born", title="Jesus Is Born", testament="NT", passage="Luke 2:1–20",
         retelling="Mary and Joseph traveled to Bethlehem, and there Mary gave birth to her son, Jesus. "
                   "She wrapped him in cloth and laid him in a manger, because there was no room for them in the inn. "
                   "An angel told shepherds the good news. They hurried, found the baby just as they had been told, and went back praising God.",
         book="Luke", ch=2, v=11, web="For there is born to you today, in David’s city, a Savior, who is Christ the Lord.",
         kjv="For unto you is born this day in the city of David a Saviour, which is Christ the Lord."),
    dict(id="storm", title="Jesus Calms the Storm", testament="NT", passage="Mark 4:35–41",
         retelling="Jesus and his disciples were crossing the lake in a boat, and Jesus fell asleep on a cushion. "
                   "A big windstorm came, the waves filled the boat, and the disciples woke him up. "
                   "Jesus spoke to the wind and the sea, the wind stopped, and there was a great calm.",
         book="Mark", ch=4, v=41, web="Who then is this, that even the wind and the sea obey him?",
         kjv="What manner of man is this, that even the wind and the sea obey him?"),
    dict(id="five-thousand", title="Jesus Feeds Five Thousand", testament="NT", passage="John 6:1–14, 35",
         retelling="A great crowd followed Jesus. A boy there had five barley loaves and two fish. "
                   "Jesus gave thanks and shared out the bread and fish, and about five thousand men sat down and ate as much as they wanted. "
                   "Afterward the disciples filled twelve baskets with the pieces left over.",
         book="John", ch=6, v=35, web="I am the bread of life.", kjv="I am the bread of life"),
    dict(id="risen", title="Jesus Is Risen", testament="NT", passage="Matthew 27:57–28:10",
         retelling="After Jesus died on the cross, his body was laid in a tomb, and a big stone was rolled in front of it. "
                   "Early on the first day of the week, women came to see the tomb, and an angel told them not to be afraid, because Jesus had risen. "
                   "As they ran to tell his disciples, Jesus met them, and they worshiped him.",
         book="Matthew", ch=28, v=6, web="He is not here, for he has risen, just like he said.",
         kjv="He is not here: for he is risen, as he said."),
]

def load_web():
    d = {}
    for line in WEB_SRC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\S+) (\d+):(\d+) (.*)$", line)
        if m:
            d[(m[1], int(m[2]), int(m[3]))] = m[4]
    return d

_kjv = {}
def kjv_verse(fname, ch, v):
    if fname not in _kjv:
        _kjv[fname] = json.load(gzip.open(KJV_DIR / f"{fname}.json.gz"))
    raw = _kjv[fname][str(ch)][str(v)]
    return re.sub(r"[\[\]]", "", raw).lstrip("¶ ").strip()

def check(portion, source, label):
    assert portion in source, f"{label}: not an exact run of the source verse\n  {portion!r}\n  {source!r}"
    # must start and end on word boundaries
    i = source.index(portion)
    assert i == 0 or not source[i - 1].isalnum(), label
    j = i + len(portion)
    assert j == len(source) or not source[j].isalnum(), label
    return portion != source.rstrip("”’ ").strip("“")

web = load_web()
stories = []
for n, s in enumerate(STORIES, 1):
    code, kfile, osis = BOOKS[s["book"]]
    wsrc = web[(code, s["ch"], s["v"])]
    ksrc = kjv_verse(kfile, s["ch"], s["v"])
    wpart = check(s["web"], wsrc, s["id"] + " WEB")
    kpart = check(s["kjv"], ksrc, s["id"] + " KJV")
    stories.append({
        "id": s["id"], "order": n, "title": s["title"], "testament": s["testament"],
        "passage": s["passage"], "retelling": s["retelling"],
        "verse": {
            "ref": f'{s["book"]} {s["ch"]}:{s["v"]}', "osis": f'{osis}.{s["ch"]}.{s["v"]}',
            "WEB": {"text": s["web"], "partOfVerse": wpart, "fullVerse": wsrc},
            "KJV": {"text": s["kjv"], "partOfVerse": kpart, "fullVerse": ksrc},
        },
    })

data = {
    "schema": 1,
    "module": {"id": "scripture-memory", "name": "Hive Kids Bible", "status": "preview"},
    "translations": {
        "WEB": {"name": "World English Bible", "short": "WEB", "license": "public domain",
                "source": "eBible.org, engwebp (2020 stable text)", "url": "https://ebible.org/web/"},
        "KJV": {"name": "King James Version (1769)", "short": "KJV", "license": "public domain outside the UK",
                "source": "eBible.org, eng-kjv", "url": "https://ebible.org/kjv/"},
    },
    "defaultTranslation": "WEB",
    "stories": stories,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("wrote", OUT, len(stories), "stories")

# shared nav, copied verbatim from the Academy home page
if PAGE.exists():
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    nav = re.search(r"<!-- chl-lab-nav -->.*?<!-- /chl-lab-nav -->", idx, re.S).group(0)
    page = PAGE.read_text(encoding="utf-8")
    page, k = re.subn(r"<!-- chl-lab-nav -->.*?<!-- /chl-lab-nav -->", lambda m: nav, page, flags=re.S)
    assert k == 1
    assert "noindex" in page and "G-DW4D6JPPB4" in page
    PAGE.write_text(page, encoding="utf-8")
    print("synced nav into", PAGE)
