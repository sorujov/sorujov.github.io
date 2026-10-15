"""Shared style and voice plumbing for the Time Series Econometrics intuition videos."""
import hashlib
import os
import shutil
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.base import SpeechService

BG = "#111111"
WHITE_ = "#ECECEC"
BLUE_ = "#58C4DD"
TEAL_ = "#5CD0B3"
YELLOW_ = "#F4D345"
RED_ = "#FC6255"
GREEN_ = "#83C167"
PURPLE_ = "#B189C6"
GREY_ = "#7A7A7A"
DIM = "#3A3A3A"
FONT = "Latin Modern Roman"

config.background_color = BG
config.max_files_cached = 1000
Text.set_default(color=WHITE_, font=FONT)
MathTex.set_default(color=WHITE_)
Tex.set_default(color=WHITE_)


class PrecomputedService(SpeechService):
    """Plays mp3 files generated elsewhere (named md5(text).mp3); gTTS if one is missing."""

    def __init__(self, audio_dir, **kwargs):
        super().__init__(**kwargs)
        self.audio_dir = Path(audio_dir)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        h = hashlib.md5(text.encode()).hexdigest()
        src = self.audio_dir / f"{h}.mp3"
        if src.exists():
            shutil.copy(src, cache_dir / f"{h}.mp3")
        else:
            from gtts import gTTS
            print(f"[voice] missing {h}, using gTTS")
            gTTS(text, lang="en", tld="co.uk").save(str(cache_dir / f"{h}.mp3"))
        return {"input_text": text, "input_data": {"input_text": text, "service": "pre"},
                "original_audio": f"{h}.mp3"}


class SilentService(SpeechService):
    """Preview voice: silence lasting as long as the sentence would take to say (~2.6 words/s)."""

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        h = hashlib.md5(text.encode()).hexdigest()
        out = cache_dir / f"{h}.mp3"
        if not out.exists():
            dur = max(1.0, len(text.split()) / 2.6)
            os.system(f"ffmpeg -v error -y -f lavfi -i anullsrc=r=44100:cl=mono -t {dur:.2f} -q:a 9 {out}")
        return {"input_text": text, "input_data": {"input_text": text, "service": "silent"},
                "original_audio": f"{h}.mp3"}


def voice_service():
    if os.environ.get("VOICE") == "silent":
        return SilentService(transcription_model=None)
    if os.environ.get("VOICE") == "precomputed":
        return PrecomputedService(os.environ.get("TTS_DIR", "tts"), transcription_model=None)
    from manim_voiceover.services.gtts import GTTSService
    return GTTSService(lang="en", tld="co.uk", transcription_model=None)


def T(s, size=34, color=WHITE_, **kw):
    return Text(s, font_size=size, color=color, **kw)


COURSE = "Time Series Econometrics"


class IntuitionScene(VoiceoverScene):
    parts = ()

    def construct(self):
        self.set_speech_service(voice_service())
        for name in self.parts:
            getattr(self, name)()
            if self.mobjects:
                self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)
                self.wait(0.3)

    def say(self, text):
        # NARRATION_MAP=path.json ({md5(english): translated text}) narrates in another language.
        m = os.environ.get("NARRATION_MAP")
        if m:
            if not hasattr(self, "_nmap"):
                import json
                self._nmap = json.load(open(m, encoding="utf-8"))
            text = self._nmap.get(hashlib.md5(text.encode()).hexdigest(), text)
        return self.voiceover(text)

    def fill(self, tr, used):
        self.wait(max(tr.duration - used, 0.2))

    def title_card(self, title, lecture, text):
        t = T(title, 56)
        sub = T(f"{COURSE}  ·  Lecture {lecture}", 28, GREY_).next_to(t, DOWN, buff=0.35)
        with self.say(text) as tr:
            self.play(Write(t), run_time=2)
            self.play(FadeIn(sub))
            self.fill(tr, 3)


class ZoomScene(IntuitionScene, MovingCameraScene):
    """IntuitionScene with a movable camera (self.camera.frame) for zooms and pans."""

    def construct(self):
        IntuitionScene.construct(self)


def series_path(ax, ys, color=BLUE_, width=3, x0=0):
    """A time-series line on axes ax from a sequence ys (x = x0, x0+1, ...)."""
    pts = [ax.c2p(x0 + i, y) for i, y in enumerate(ys)]
    return VMobject(color=color, stroke_width=width).set_points_as_corners(pts)


def load_csv(name):
    """Real data shipped beside the scripts in data/ (date,value)."""
    import csv
    here = Path(__file__).parent / "data" / name
    rows = [r for r in csv.reader(open(here)) if r and r[1] not in (".", "")][1:]
    return [r[0] for r in rows], np.array([float(r[1]) for r in rows])
