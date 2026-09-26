"""Shared style and voice plumbing for the STAT-2311 intuition videos."""
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


def voice_service():
    if os.environ.get("VOICE") == "precomputed":
        return PrecomputedService(os.environ.get("TTS_DIR", "tts"), transcription_model=None)
    from manim_voiceover.services.gtts import GTTSService
    return GTTSService(lang="en", tld="co.uk", transcription_model=None)


def T(s, size=34, color=WHITE_, **kw):
    return Text(s, font_size=size, color=color, **kw)


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
        return self.voiceover(text)

    def fill(self, tr, used):
        self.wait(max(tr.duration - used, 0.2))

    def title_card(self, title, lecture, text):
        t = T(title, 56)
        sub = T(f"Mathematical Statistics I  ·  Lecture {lecture}", 28, GREY_).next_to(t, DOWN, buff=0.35)
        with self.say(text) as tr:
            self.play(Write(t), run_time=2)
            self.play(FadeIn(sub))
            self.fill(tr, 3)
