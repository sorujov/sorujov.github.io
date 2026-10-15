# Films for the Time Series Econometrics notes

One Manim film per lecture, three to four minutes, narrated by Sam's cloned voice
(ElevenLabs). A film gives the idea of the lecture, not a walkthrough of its slides.
Each deck shows its film on a "🎬 The Idea in N Minutes" slide before the objectives;
the mp4, `.srt` and `.vtt` live in `NN-slug/video/`.

## Files
- `common.py`: palette, Latin Modern type, `IntuitionScene` (voice-over scene),
  `ZoomScene` (adds a movable camera), `series_path`, `load_csv`, and three voices:
  `VOICE=silent` (silence timed to the text, for layout previews), `VOICE=precomputed`
  (mp3s named `md5(text).mp3` in `TTS_DIR`), and gTTS otherwise.
- `tseN.py`: the film for lecture N, class `TseN`. Narration sits in `self.say("...")`
  blocks and in `title_card`, always as literal strings.
- `texts.py tseN.py out.json`: extracts the narration, keyed by md5, with a character count.
- `add_video_slide.py N MIN`: writes the video slide, with the previous-lecture link, into deck N.
- `data/`: the FRED series the films draw (downloaded 15 October 2026).

## Making a film
1. Write `tseN.py`. Keep the narration at 2,000–2,600 characters.
2. Preview the layout: `VOICE=silent manim -ql tseN.py TseN`, then look at a contact sheet
   (`ffmpeg -i X.mp4 -vf "fps=1/4,scale=480:270,tile=4x4" sheet-%02d.png`).
3. Generate the narration with `texts.py`; the mp3s are made on ooklapc with the
   ElevenLabs key from the repository's `.env` (never committed), model
   `eleven_multilingual_v2`, stability 0.55, similarity 0.85, voice "Samir Orujov (lectures)".
4. Render: `VOICE=precomputed TTS_DIR=<mp3 dir> manim -qm tseN.py TseN` (720p30), convert the
   `.srt` to `.vtt` with ffmpeg, copy all three into the deck's `video/`, run
   `add_video_slide.py`, and re-render the deck.

Renders running in parallel must not share a LaTeX cache: each film sets its own
`config.tex_dir`. Readouts redrawn every frame use `T()`, not `MathTex`, which would call
LaTeX once per frame.
