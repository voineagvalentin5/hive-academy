"""Build /modules/scripture-memory/data/stories.json (Hive Kids Bible).

Usage: python3 tools/build_scripture_memory.py <engwebp_vpl.txt> <hive-scribe kjv dir>

Verse text is never typed by hand. Each key verse is read from the public-domain
source files and every memory text is checked to be an exact, unchanged run of
words from that verse. If a check fails the build stops.

  KJV (default) and WEB (option).
  WEB: eBible.org "engwebp" (World English Bible, 2020 stable text), engwebp_vpl.txt
  KJV: eBible.org "eng-kjv" (1769 text), as packaged in Hive Scribe data/kjv/*.json.gz.
       Brackets that mark words the translators supplied are removed; words are unchanged.

The module page has a breadcrumb header (Codex Hive Labs › Hive Academy › Hive Kids Bible).
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
    "Matthew": ("MAT", "Matt", "Matt"), "Acts": ("ACT", "Acts", "Acts"),
    "1 Timothy": ("1TI", "1Tim", "1Tim"), "Colossians": ("COL", "Col", "Col"),
}

# Retellings are short and kid-level. Every statement comes from the passage listed with it
# (KJV wording where practical); nothing is added from tradition. "more" quotes are verified like key verses.
ACTS_238 = dict(label="What should we do?", book="Acts", ch=2, v=38,
    kjv="Repent, and be baptized every one of you in the name of Jesus Christ for the remission of sins, and ye shall receive the gift of the Holy Ghost.",
    web="Repent and be baptized, every one of you, in the name of Jesus Christ for the forgiveness of sins, and you will receive the gift of the Holy Spirit.")
STORIES = [
    dict(id="creation", title="God Makes the World", testament="OT", passage="Genesis 1:1–2:3",
         retelling="In the beginning God created the heaven and the earth. God spoke, and there was light. "
                   "God made the sky, the dry land and the seas, the plants, the sun, the moon and the stars, the fish, the birds and the animals. "
                   "Then God created man in his own image, male and female. God saw everything he had made, and it was very good, and on the seventh day God rested.",
         book="Genesis", ch=1, v=1, web="In the beginning, God created the heavens and the earth.",
         kjv="In the beginning God created the heaven and the earth."),
    dict(id="noah", title="Noah and the Ark", testament="OT", passage="Genesis 6:9–9:17",
         retelling="Noah was a just man, and Noah walked with God. God told Noah to make an ark, and to come into it with his wife, his sons and his sons' wives, "
                   "and to bring two of every kind of living thing. Rain fell on the earth forty days and forty nights, and the flood covered the earth, "
                   "and Noah and everyone with him in the ark stayed alive. Afterward God set his bow in the cloud as a token of his covenant: there will never again be a flood to destroy the earth.",
         book="Genesis", ch=9, v=13, web="I set my rainbow in the cloud, and it will be a sign of a covenant between me and the earth.",
         kjv="I do set my bow in the cloud, and it shall be for a token of a covenant between me and the earth."),
    dict(id="abraham", title="God's Promise to Abraham", testament="OT", passage="Genesis 12:1–4; 15:5–6; 17:5; 18:1–14; 21:1–3",
         retelling="The LORD told Abram to leave his country and go to a land the LORD would show him, and Abram went. "
                   "God told him to look up at the stars and count them, and said his seed, the family that would come from him, would be like that. Abram believed in the LORD, and God later changed his name to Abraham. "
                   "Abraham and Sarah were very old, but the LORD said Sarah would have a son. The LORD did for Sarah as he had spoken, and their son Isaac was born.",
         book="Genesis", ch=18, v=14, web="Is anything too hard for the LORD?", kjv="Is any thing too hard for the LORD?"),
    dict(id="joseph", title="Joseph and His Brothers", testament="OT", passage="Genesis 37; 39–45; 50:15–21",
         retelling="Joseph's brothers hated him and envied him, and they sold him, and he was taken into Egypt. "
                   "Even in prison, the LORD was with Joseph. Joseph told Pharaoh that God would give the answer to his dreams, and Pharaoh set Joseph over all the land of Egypt, "
                   "and Joseph gathered up food before the famine came. When his brothers came to Egypt to buy food, Joseph told them who he was, and he kissed them and wept. "
                   "Later he told them not to be afraid, and he comforted them and spoke kindly to them.",
         book="Genesis", ch=50, v=20, web="As for you, you meant evil against me, but God meant it for good",
         kjv="But as for you, ye thought evil against me; but God meant it unto good"),
    dict(id="red-sea", title="Moses and the Red Sea", testament="OT", passage="Exodus 14",
         retelling="The LORD brought the children of Israel out of Egypt, but Pharaoh and his army chased after them and came near them by the sea. "
                   "Moses told the people not to be afraid. Moses stretched out his hand over the sea, the LORD sent a strong east wind, "
                   "and the people walked through the middle of the sea on dry ground, with the waters like a wall on each side. That day the LORD saved Israel from the Egyptians.",
         book="Exodus", ch=14, v=14, web="The LORD will fight for you, and you shall be still.",
         kjv="The LORD shall fight for you, and ye shall hold your peace."),
    dict(id="david", title="David and Goliath", testament="OT", passage="1 Samuel 17",
         retelling="A Philistine giant named Goliath defied the armies of Israel and called for a man to fight him, and the men of Israel were afraid. "
                   "David was a youth who kept his father's sheep. He said the LORD who saved him from the lion and the bear would save him from this Philistine too. "
                   "David took his staff, his sling and five smooth stones from the brook, and he came to Goliath in the name of the LORD. David's stone struck Goliath in the forehead, and the giant fell.",
         book="1 Samuel", ch=17, v=47, web="the battle is the LORD’s", kjv="the battle is the LORD’s"),
    dict(id="daniel", title="Daniel and the Lions", testament="OT", passage="Daniel 6",
         retelling="A new law said that for thirty days no one could pray to any god or man except the king. "
                   "Daniel still knelt and prayed and gave thanks to his God three times a day, as he always had, and he was thrown into the den of lions. "
                   "God sent his angel and shut the lions' mouths. Early in the morning Daniel was taken up out of the den, and he was not hurt at all, because he believed in his God.",
         book="Daniel", ch=6, v=22, web="My God has sent his angel, and has shut the lions’ mouths, and they have not hurt me",
         kjv="My God hath sent his angel, and hath shut the lions’ mouths, that they have not hurt me"),
    dict(id="jonah", title="Jonah and the Great Fish", testament="OT", passage="Jonah 1–3",
         retelling="God told Jonah to go to the great city of Nineveh, but Jonah ran away from the LORD on a ship. The LORD sent a great wind, Jonah was cast into the sea, "
                   "and the LORD prepared a great fish to swallow him. Jonah was in the belly of the fish three days and three nights, and he prayed to the LORD from inside the fish. "
                   "The LORD spoke to the fish, and it put Jonah out on dry land. Then Jonah went to Nineveh, the people believed God and turned from their evil way, and God did not destroy the city.",
         book="Jonah", ch=2, v=9, web="Salvation belongs to the LORD.", kjv="Salvation is of the LORD.", point=["pentecost"]),
    dict(id="jesus-born", title="Jesus Is Born", testament="NT", passage="Luke 2:1–20; Matthew 1:21–23",
         retelling="Mary and Joseph went to Bethlehem, and there Mary gave birth to her firstborn son. She wrapped him in swaddling clothes and laid him in a manger, because there was no room for them in the inn. "
                   "An angel of the Lord told shepherds the good news, and they came quickly and found the baby, just as they had been told. "
                   "His name is Jesus, because he shall save his people from their sins, and the Bible says he is Emmanuel, which means God with us.",
         book="Luke", ch=2, v=11, web="For there is born to you today, in David’s city, a Savior, who is Christ the Lord.",
         kjv="For unto you is born this day in the city of David a Saviour, which is Christ the Lord.",
         point=["who-is-jesus", "pentecost"]),
    dict(id="who-is-jesus", title="Who Is Jesus?", testament="NT", passage="John 1:1–17; Matthew 1:23; 1 Timothy 3:16",
         retelling="The Bible tells us who Jesus is. In the beginning was the Word, and the Word was God, and all things were made by him. "
                   "Then the Word was made flesh and dwelt among us, full of grace and truth, and grace and truth came by Jesus Christ. "
                   "Jesus is the Word made flesh: Emmanuel, God with us.",
         book="John", ch=1, v=1, web="In the beginning was the Word, and the Word was with God, and the Word was God.",
         kjv="In the beginning was the Word, and the Word was with God, and the Word was God.",
         also=[dict(book="John", ch=1, v=14,
                    kjv="And the Word was made flesh, and dwelt among us, (and we beheld his glory, the glory as of the only begotten of the Father,) full of grace and truth.",
                    web="The Word became flesh and lived among us. We saw his glory, such glory as of the only born Son of the Father, full of grace and truth.")],
         more=[dict(label="The Bible also says", book="1 Timothy", ch=3, v=16, kjv="God was manifest in the flesh", web="God was revealed in the flesh")],
         point=["pentecost"]),
    dict(id="storm", title="Jesus Calms the Storm", testament="NT", passage="Mark 4:35–41",
         retelling="Jesus and his disciples got into a ship to cross over the sea, and Jesus was asleep on a pillow in the back of the ship. "
                   "A great storm of wind came, the waves beat into the ship until it was full, and the disciples woke him. "
                   "Jesus rebuked the wind and said to the sea, Peace, be still. The wind stopped, and there was a great calm.",
         book="Mark", ch=4, v=41, web="Who then is this, that even the wind and the sea obey him?",
         kjv="What manner of man is this, that even the wind and the sea obey him?",
         more=[dict(label="Who is Jesus?", book="Colossians", ch=2, v=9, kjv="For in him dwelleth all the fulness of the Godhead bodily.",
                    web="For in him all the fullness of the Deity dwells bodily")]),
    dict(id="five-thousand", title="Jesus Feeds Five Thousand", testament="NT", passage="John 6:1–14, 35",
         retelling="A great multitude followed Jesus. A lad there had five barley loaves and two small fishes. "
                   "Jesus gave thanks and gave the bread and fish to his disciples to hand out, and about five thousand men sat down and ate as much as they wanted. "
                   "Afterward the disciples gathered up the pieces that were left and filled twelve baskets. Later Jesus told the people that he is the bread of life.",
         book="John", ch=6, v=35, web="I am the bread of life.", kjv="I am the bread of life"),
    dict(id="risen", title="Jesus Is Risen", testament="NT", passage="Matthew 27:57–28:10; Acts 2:38",
         retelling="After Jesus was crucified and died, Joseph of Arimathaea laid his body in a new tomb and rolled a great stone to the door. "
                   "Early on the first day of the week, Mary Magdalene and the other Mary came to see the tomb. An angel told them not to be afraid, because Jesus had risen, just as he said. "
                   "As they ran to tell his disciples, Jesus met them, and they worshipped him. "
                   "Later, on the day of Pentecost, Peter told the people what they should do: repent (turn away from sin), be baptized in the name of Jesus Christ, and receive the gift of the Holy Ghost.",
         book="Matthew", ch=28, v=6, web="He is not here, for he has risen, just like he said.",
         kjv="He is not here: for he is risen, as he said.", more=[ACTS_238], point=["pentecost"]),
    dict(id="pentecost", title="The Day of Pentecost", testament="NT", passage="Acts 1:4–5; 2:1–41",
         retelling="Jesus told his disciples to wait, because they would be baptized with the Holy Ghost. When the day of Pentecost came, they were all together in one place. "
                   "Suddenly a sound from heaven like a rushing mighty wind filled the house, and tongues like fire sat on each of them. "
                   "They were all filled with the Holy Ghost and began to speak with other tongues, as the Spirit gave them utterance. "
                   "Peter preached about Jesus, and the people asked, what shall we do? Peter told them, and about three thousand people who gladly received his word were baptized that same day.",
         book="Acts", ch=2, v=38, web=ACTS_238["web"], kjv=ACTS_238["kjv"],
         more=[dict(label="What happened that day", book="Acts", ch=2, v=4,
                    kjv="And they were all filled with the Holy Ghost, and began to speak with other tongues, as the Spirit gave them utterance.",
                    web="They were all filled with the Holy Spirit and began to speak with other languages, as the Spirit gave them the ability to speak.")]),
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

def quote(m, sid):
    code, kfile, osis = BOOKS[m["book"]]
    wsrc = web[(code, m["ch"], m["v"])]
    ksrc = kjv_verse(kfile, m["ch"], m["v"])
    return {"label": m["label"], "ref": f'{m["book"]} {m["ch"]}:{m["v"]}', "osis": f'{osis}.{m["ch"]}.{m["v"]}',
            "WEB": {"text": m["web"], "partOfVerse": check(m["web"], wsrc, sid + " more WEB")},
            "KJV": {"text": m["kjv"], "partOfVerse": check(m["kjv"], ksrc, sid + " more KJV")}}

stories = []
def key_verse(k, sid):
    code, kfile, osis = BOOKS[k["book"]]
    wsrc = web[(code, k["ch"], k["v"])]
    ksrc = kjv_verse(kfile, k["ch"], k["v"])
    return {"ref": f'{k["book"]} {k["ch"]}:{k["v"]}', "osis": f'{osis}.{k["ch"]}.{k["v"]}',
            "WEB": {"text": k["web"], "partOfVerse": check(k["web"], wsrc, sid + " WEB"), "fullVerse": wsrc},
            "KJV": {"text": k["kjv"], "partOfVerse": check(k["kjv"], ksrc, sid + " KJV"), "fullVerse": ksrc}}

for n, s in enumerate(STORIES, 1):
    verses = [key_verse(s, s["id"])] + [key_verse(dict(a, book=a.get("book", s["book"])), s["id"]) for a in s.get("also", [])]
    stories.append({
        "id": s["id"], "order": n, "title": s["title"], "testament": s["testament"],
        "passage": s["passage"], "retelling": s["retelling"],
        "verse": verses[0], "verses": verses,
        "more": [quote(m, s["id"]) for m in s.get("more", [])],
        "pointTo": s.get("point") or [],
    })

data = {
    "schema": 1,
    "module": {"id": "scripture-memory", "name": "Hive Kids Bible", "status": "preview"},
    "translations": {
        "KJV": {"name": "King James Version (1769)", "short": "KJV", "license": "public domain outside the UK",
                "source": "eBible.org, eng-kjv", "url": "https://ebible.org/kjv/"},
        "WEB": {"name": "World English Bible", "short": "WEB", "license": "public domain",
                "source": "eBible.org, engwebp (2020 stable text)", "url": "https://ebible.org/web/"},
    },
    "defaultTranslation": "KJV",
    "featured": [
        {"label": "Who is Jesus?", "story": "who-is-jesus"},
        {"label": "What should we do?", "story": "pentecost"},
    ],
    "stories": stories,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("wrote", OUT, len(stories), "stories")

# The module page uses a breadcrumb header (its first crumb, with the official Codex Hive logo,
# links back to codex-hive.com) instead of the shared nav, so nothing is copied in here any more.
if PAGE.exists():
    page = PAGE.read_text(encoding="utf-8")
    # Kids pages must stay free of analytics (COPPA): do not re-insert the Academy GA tag.
    assert "noindex" in page and "G-DW4D6JPPB4" not in page and "googletagmanager" not in page and "Google Analytics" not in page
    assert 'aria-label="Breadcrumb"' in page and "https://codex-hive.com" in page
