# Intuition videos for Mathematical Statistics I (STAT-2311)

One short Manim video per lecture (2–5 minutes), 3Blue1Brown-style. It gives the intuition, not a walkthrough of the slides. The narration is Sam's cloned voice (ElevenLabs).

Each deck shows its video on a "🎬 The Idea in N Minutes" slide just before the learning objectives. The video, its `.srt` and its `.vtt` captions live in `NN-.../video/`.

## Files
- `common.py`: shared style (dark background, palette, Latin Modern font), the `IntuitionScene` base class, and `PrecomputedService`, which plays narration mp3s named `md5(text).mp3`.
- `lectureN.py`: one scene per lecture. The narration sits in `self.say("...")` blocks (and `title_card`).
- `texts.py lectureN.py out.json`: extracts the narration texts, keyed by md5.
- `render.sh N [l|h]`: renders with the precomputed voice and makes a contact sheet for checking frames.
- `prep.sh N`: copies the finished mp4/srt and makes the `.vtt` captions.
- `tools/`: helpers that run on ooklapc: `gen.py`, `pack.sh` (ElevenLabs narration), `add_slide.py`, `publish.sh` (deck slide and git push).
- `clone_voice.py`: one-off creation of the voice clone.

## Voice
- The key and voice id are in `C:\Users\ookla.user\.secrets\.env` (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`). They never go in this repo.
- Settings: model `eleven_multilingual_v2`, stability 0.55, similarity 0.85 (Sam chose the calm voice on 27 Sep 2026).
- Voice recordings are never committed here (see `.gitignore`).

## Adding a video
1. Write `lectureN.py` on the model of the others.
2. Run `texts.py`, generate the mp3s on ooklapc with `tools/pack.sh N`, and stage the tar.
3. Render at low quality with `render.sh N l`, check the sheet, fix the layout, then render at high quality with `render.sh N h`.
4. Run `prep.sh N`, then `tools/publish.sh <lecture-dir> lectureN_intuition <minutes> "<message>"`.

## Azerbaijani option (27 Sep 2026)
- Every video has an Azerbaijani caption track (`video/lectureN_intuition.az.vtt`), selectable from CC.
- Azerbaijani narration is prepared but not yet published. Translated clip texts are keyed by the md5 of the English clip. `common.py` narrates from them when `NARRATION_MAP=az_lN.json` is set, so the same scene renders an Azerbaijani version timed to the Azerbaijani audio. The clips are generated on ooklapc with `tools/gen_az.py`/`tools/pack_az.sh`, using the Azerbaijani clone (`ELEVENLABS_VOICE_ID_AZ`).
- `tools/add_video_slide.py NN MIN` writes the video slide (raw HTML block, EN/AZ tracks, previous-lecture link) into a deck's `.qmd`. `tools/pubvid.sh N` copies a rendered video into its deck, re-renders it and commits it.
