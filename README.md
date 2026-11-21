# Hive Academy (linkable preview)

Static site for academy.codex-hive.com. The home page is a public preview of what is here now, starting with Hive Astra, the Rosetta Logos research module and the Hive Kids Bible preview. Search engines are still asked not to index the site: noindex/nofollow on every page, robots.txt Disallow: /, no sitemap. Pages carry the shared Google Analytics tag (G-DW4D6JPPB4) to count visits. Rosetta Logos is listed on the home page and keeps its preliminary, not-peer-reviewed banner.

- `tools/make_logos.py` builds web logo assets from the official Hive Academy files.
- `tools/make_og.py` builds the share image.
- `tools/build_scripture_memory.py` builds `modules/scripture-memory/data/stories.json` (Hive Kids Bible) from the public-domain KJV (default; eBible.org eng-kjv, via Hive Scribe) and WEB (option; eBible.org engwebp) files, checks every key verse and supporting quote is quoted exactly, and copies the shared nav into the module page. Retellings stay with the scripture text of the passage listed with each story, in line with Apostolic Pentecostal teaching (Acts 2:38). Progress is kept in localStorage only.
