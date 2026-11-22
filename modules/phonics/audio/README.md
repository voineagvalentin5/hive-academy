# Hive Phonics recorded audio (optional)

The page speaks letter names, "C is for cat" lines and whole words with the device's built-in voice. Recorded clips, when added, play instead.

**Single letter sounds are clip-only.** Device voices say phonemes badly, so no letter sound is ever spoken by the device voice. Until a `sound-x` clip is listed in `CLIPS`:
- the "Just the sound" button on that letter's card is hidden;
- tapping that letter in Blend only lights it up (the grown-up and child say the sound);
- the bee slide in Blend lights the letters silently. The slide plays sounds only for words where every letter has a `sound-` clip.

As soon as `"sound-c": "audio/sound-c.mp3"` is added to `CLIPS`, the C button and taps come back automatically. A listed clip that fails to load is skipped silently, never replaced by the device voice.

1. Record short, clean clips (mp3 or m4a, mono, trimmed, about -16 LUFS).
2. Save them here with these names:
   - `sound-a.mp3` … `sound-z.mp3`: the single sound only (short /a/ as in apple, /k/ for c, and so on)
   - `letter-a.mp3` … `letter-z.mp3`: the letter card line, for example "A. A is for apple. Apple."
   - `word-cat.mp3`, `word-hat.mp3` …: each picture word on its own
3. List each file in the `CLIPS` map near the top of `../app.js`, e.g. `"sound-a": "audio/sound-a.mp3"`.

Any clip that is missing or fails to load falls back to the device voice.
