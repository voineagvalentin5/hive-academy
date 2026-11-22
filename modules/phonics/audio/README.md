# Hive Phonics recorded audio (optional)

The page speaks with the device's built-in voice today. Recorded clips, when added, play instead.

1. Record short, clean clips (mp3 or m4a, mono, trimmed, about -16 LUFS).
2. Save them here with these names:
   - `sound-a.mp3` … `sound-z.mp3`: the single sound only (short /a/ as in apple, /k/ for c, and so on)
   - `letter-a.mp3` … `letter-z.mp3`: the letter card line, for example "A. A is for apple. Apple."
   - `word-cat.mp3`, `word-hat.mp3` …: each picture word on its own
3. List each file in the `CLIPS` map near the top of `../app.js`, e.g. `"sound-a": "audio/sound-a.mp3"`.

Any clip that is missing or fails to load falls back to the device voice.
