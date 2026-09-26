"""Lecture 8 recap — Total Probability and Bayes' Rule (Wackerly §2.10).

Style: dark background, 3Blue1Brown-like Manim palette, serif maths font, picture first,
formula second. No pi-creatures or 3Blue1Brown branding.

Render:  manim -qh lecture8.py Lecture8
Voice:   VOICE=precomputed  -> uses mp3 files in $TTS_DIR named md5(text).mp3
                               (made with Sam's ElevenLabs clone; see README.md)
         VOICE=eleven       -> calls ElevenLabs directly (ELEVENLABS_API_KEY / _VOICE_ID)
         default            -> gTTS placeholder
"""
import hashlib
import os
import shutil
from pathlib import Path

try:  # keys live in the universal secrets file on ooklapc
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser(r"~/.secrets/.env"))
except ImportError:
    pass

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
        if not src.exists():
            from gtts import gTTS
            print(f"[voice] missing {h}, using gTTS")
            gTTS(text, lang="en", tld="co.uk").save(str(cache_dir / f"{h}.mp3"))
        else:
            shutil.copy(src, cache_dir / f"{h}.mp3")
        return {"input_text": text, "input_data": {"input_text": text, "service": "pre"},
                "original_audio": f"{h}.mp3"}


def voice_service():
    v = os.environ.get("VOICE", "gtts")
    if v == "precomputed":
        return PrecomputedService(os.environ.get("TTS_DIR", "tts"), transcription_model=None)
    if v == "eleven":
        from manim_voiceover.services.elevenlabs import ElevenLabsService
        return ElevenLabsService(voice_id=os.environ["ELEVENLABS_VOICE_ID"],
                                 model="eleven_multilingual_v2",
                                 voice_settings={"stability": 0.55, "similarity_boost": 0.85},
                                 transcription_model=None)
    from manim_voiceover.services.gtts import GTTSService
    return GTTSService(lang="en", tld="co.uk", transcription_model=None)


def T(s, size=34, color=WHITE_, **kw):
    return Text(s, font_size=size, color=color, **kw)


class Lecture8(VoiceoverScene):
    def construct(self):
        self.set_speech_service(voice_service())
        # short intuition video: the tree (procedure) is left to the lecture itself
        for part in (self.cold_open, self.dots, self.area, self.bayes,
                     self.base_rate, self.second_test, self.closing):
            part()
            if self.mobjects:
                self.play(FadeOut(Group(*self.mobjects)), run_time=0.7)
                self.wait(0.3)

    def say(self, text):
        return self.voiceover(text)

    def fill(self, tr, used):
        self.wait(max(tr.duration - used, 0.2))

    # ------------------------------------------------------------ cold open
    def cold_open(self):
        lines = VGroup(
            T("A fraud screen catches 95% of fraudulent payments.", t2c={"95%": TEAL_}),
            T("It wrongly flags only 3% of honest ones.", t2c={"3%": YELLOW_}),
            T("About 1 payment in 500 is fraud.", t2c={"1 payment in 500": RED_}),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).shift(UP * 0.9)
        q = T("A payment is flagged. How likely is it to be fraud?", 38, BLUE_).next_to(lines, DOWN, buff=0.9)
        with self.say("Here's a puzzle. A bank screens every card payment with a fraud model. "
                      "It catches ninety-five percent of fraudulent payments, and it wrongly flags "
                      "only three percent of honest ones. About one payment in five hundred is "
                      "actually fraud.") as tr:
            for ln in lines:
                self.play(FadeIn(ln, shift=UP * 0.2), run_time=1.2)
                self.wait(1.0)
            self.fill(tr, 6.6)
        with self.say("Now a payment gets flagged. What's the chance it really is fraud? Take a "
                      "second and commit to a number. Most people say something close to ninety-five "
                      "percent.") as tr:
            self.play(Write(q), run_time=2)
            self.fill(tr, 2)
        self.play(FadeOut(lines), FadeOut(q))
        title = T("Total probability and Bayes' rule", 58)
        sub = T("Mathematical Statistics I  ·  Lecture 8", 28, GREY_).next_to(title, DOWN, buff=0.35)
        with self.say("In the next few minutes you'll see why the honest answer is closer to six "
                      "percent, and you'll meet two tools that make this kind of question almost "
                      "mechanical: the law of total probability, and Bayes' rule.") as tr:
            self.play(Write(title), run_time=2)
            self.play(FadeIn(sub))
            self.fill(tr, 3)

    # ------------------------------------------------------------ 500 dots
    def dots(self):
        rng = np.random.default_rng(8)
        grid = VGroup(*[Dot(radius=0.065, color=GREY_) for _ in range(500)])
        grid.arrange_in_grid(20, 25, buff=0.13).move_to(LEFT * 2.9 + DOWN * 0.1)
        fraud = 263
        honest_flag = [i for i in rng.choice([k for k in range(500) if k != fraud], 15, replace=False)]
        cap = T("500 payments", 30, GREY_).next_to(grid, UP, buff=0.3)
        with self.say("Forget formulas for a moment and just picture five hundred payments. On "
                      "average, one of them is fraud.") as tr:
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in grid], lag_ratio=0.004, run_time=2.5),
                      FadeIn(cap))
            self.play(grid[fraud].animate.set_color(RED_).scale(1.6))
            self.play(Flash(grid[fraud], color=RED_))
            self.fill(tr, 4.5)
        ring = Circle(radius=0.16, color=YELLOW_, stroke_width=3).move_to(grid[fraud])
        with self.say("The screen almost always catches that one. But it also flags three percent of "
                      "the four hundred and ninety-nine honest payments. That's about fifteen of them.") as tr:
            self.play(Create(ring))
            self.play(LaggedStart(*[grid[i].animate.set_color(YELLOW_).scale(1.6) for i in honest_flag],
                                  lag_ratio=0.15, run_time=3))
            self.fill(tr, 4)
        flagged = [fraud] + honest_flag
        row = VGroup(*[grid[i].copy() for i in flagged])
        target = VGroup(*[Dot(radius=0.1) for _ in flagged]).arrange_in_grid(2, 8, buff=0.32).move_to(RIGHT * 3.9 + UP * 0.6)
        brace_lbl = T("the flagged payments", 28, YELLOW_).next_to(target, UP, buff=0.4)
        frac = MathTex(r"\frac{1}{16}", r"\approx", r"6\%", font_size=64).next_to(target, DOWN, buff=0.7)
        frac[0].set_color(RED_)
        with self.say("So when the alarm goes off, you are looking at one of about sixteen flagged "
                      "payments, and only one of those sixteen is fraud. One in sixteen is about six "
                      "percent.") as tr:
            self.play(*[d.animate.set_opacity(0.15) for i, d in enumerate(grid) if i not in flagged],
                      FadeOut(ring))
            self.play(*[Transform(r, t.set_color(r.get_color())) for r, t in zip(row, target)],
                      FadeIn(brace_lbl), run_time=2)
            self.play(Write(frac))
            self.fill(tr, 4.5)
        with self.say("The screen isn't bad. The trouble is that honest payments are so common that "
                      "a small error rate, applied to all of them, swamps the rare fraud. Hold on to "
                      "this picture. Everything that follows is a way of making it precise.") as tr:
            self.play(Indicate(VGroup(*row[1:]), color=YELLOW_, scale_factor=1.15), run_time=2)
            self.fill(tr, 2)

    # ------------------------------------------------------------ area model
    def area(self):
        W, H = 6.0, 4.6
        o = np.array([-6.6, -2.6, 0])
        square = Rectangle(width=W, height=H, color=WHITE_, stroke_width=2).move_to(o + [W / 2, H / 2, 0])
        S = MathTex("S", font_size=44).next_to(square, UP, buff=0.15).align_to(square, LEFT)
        one = T("total area = 1", 26, GREY_).next_to(square, UP, buff=0.18).align_to(square, RIGHT)
        with self.say("To make it precise, let's trade dots for area. Draw every possible outcome as "
                      "a square of total area one.") as tr:
            self.play(Create(square), FadeIn(S), FadeIn(one))
            self.fill(tr, 1)
        shares, rates, names = [0.50, 0.35, 0.15], [0.01, 0.04, 0.12], ["A", "B", "C"]
        cols, x = VGroup(), 0
        for s in shares:
            cols.add(Rectangle(width=s * W, height=H, stroke_color=WHITE_, stroke_width=2)
                     .move_to(o + [x + s * W / 2, H / 2, 0]))
            x += s * W
        blabels = VGroup(*[MathTex(f"B_{i+1}", font_size=38, color=BLUE_).move_to(c.get_top() + DOWN * 0.4)
                           for i, c in enumerate(cols)])
        with self.say("Now cut the square into pieces that don't overlap and together fill it. A "
                      "collection like that is called a partition. Every outcome lands in exactly one "
                      "piece.") as tr:
            self.play(Create(cols), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(b) for b in blabels], lag_ratio=0.3))
            self.fill(tr, 2.8)
        glabels = VGroup(*[T(f"grade {n}\n{s:.2f}", 24, GREY_, line_spacing=0.7).next_to(c, DOWN, buff=0.15)
                           for n, s, c in zip(names, shares, cols)])
        with self.say("For something concrete, think of a bank's loan book split by rating grade. Half "
                      "the loans are grade A, thirty-five percent grade B, and fifteen percent grade C. "
                      "Those shares are the widths of the pieces.") as tr:
            self.play(FadeIn(glabels))
            self.fill(tr, 1)
        vs = H / 0.15 * 0.9
        shades = VGroup()
        for s, r, c in zip(shares, rates, cols):
            shades.add(Rectangle(width=s * W, height=r * vs, stroke_width=0, fill_color=TEAL_, fill_opacity=0.8)
                       .align_to(c, DOWN).align_to(c, LEFT))
        rl = VGroup(*[T(f"{int(r*100)}%", 24, TEAL_).next_to(sh, UP, buff=0.08) for r, sh in zip(rates, shades)])
        rl[2].next_to(shades[2], LEFT, buff=0.08).align_to(shades[2], UP)
        note = T("(heights stretched)", 20, GREY_).next_to(square, RIGHT, buff=0.2).align_to(square, DOWN)
        with self.say("Inside each grade, some fraction of loans default: one percent in A, four in B, "
                      "twelve in C. Shade that fraction of each column. I've stretched the heights so "
                      "you can see them.") as tr:
            self.play(LaggedStart(*[GrowFromEdge(sh, DOWN) for sh in shades], lag_ratio=0.3),
                      FadeIn(rl), FadeIn(note), run_time=2.5)
            self.fill(tr, 2.5)
        prods = VGroup(*[MathTex(f"{s:.2f}", r"\times", f"{r:.2f}", "=", f"{s*r:.3f}", font_size=36)
                         for s, r in zip(shares, rates)]).arrange(DOWN, aligned_edge=RIGHT, buff=0.3)
        prods.to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
        for p in prods:
            p[4].set_color(TEAL_)
        total = MathTex(r"0.005+0.014+0.018", "=", "0.037", font_size=38).next_to(prods, DOWN, buff=0.5).align_to(prods, RIGHT)
        total[2].set_color(TEAL_)
        with self.say("So what fraction of the whole square is shaded? Each shaded piece is a width "
                      "times a height: the probability of the grade, times the probability of default "
                      "given that grade. Add the pieces and you get point zero three seven.") as tr:
            self.play(LaggedStart(*[TransformFromCopy(sh, p) for sh, p in zip(shades, prods)], lag_ratio=0.4), run_time=3)
            self.play(Write(total))
            self.fill(tr, 4)
        law = MathTex(r"P(A)", "=", r"\sum_{i}", r"P(A\mid B_i)", r"\,", r"P(B_i)", font_size=46)
        law[3].set_color(TEAL_)
        law[5].set_color(BLUE_)
        law.next_to(total, DOWN, buff=0.8).align_to(prods, RIGHT)
        box = SurroundingRectangle(law, color=YELLOW_, buff=0.2)
        with self.say("That's the law of total probability. In general, the probability of A is the "
                      "sum, over the pieces of a partition, of P of A given B i, times P of B i. It's "
                      "nothing more than adding up shaded area.") as tr:
            self.play(Write(law), run_time=2)
            self.play(Create(box))
            self.fill(tr, 3)
        self.keep = dict(square=square, cols=cols, shades=shades, glabels=glabels, rl=rl,
                         other=VGroup(S, one, blabels, note, prods, total, law, box))

    # ------------------------------------------------------------ Bayes
    def bayes(self):
        k = self.keep
        self.add(k["square"], k["cols"], k["shades"], k["glabels"], k["rl"])
        self.remove(*k["other"])
        with self.say("Now flip the question around. A loan has defaulted. Which grade did it come "
                      "from? Knowing that it defaulted means we are somewhere in the shaded region, "
                      "and nowhere else.") as tr:
            self.play(k["square"].animate.set_stroke(DIM), k["cols"].animate.set_stroke(DIM),
                      k["glabels"].animate.set_opacity(0.4), FadeOut(k["rl"]))
            self.play(Indicate(k["shades"], color=TEAL_, scale_factor=1.05))
            self.fill(tr, 2.5)
        prods = [0.005, 0.014, 0.018]
        L = 11.0
        bar, x = VGroup(), -L / 2
        for p, op in zip(prods, [0.45, 0.65, 0.9]):
            w = p / 0.037 * L
            bar.add(Rectangle(width=w, height=0.9, stroke_color=BG, stroke_width=3,
                              fill_color=TEAL_, fill_opacity=op).move_to([x + w / 2, 1.9, 0]))
            x += w
        lab = VGroup(*[T(f"{n}: {p/0.037:.1%}", 28, BG if i else WHITE_, weight=BOLD).move_to(b)
                       for i, (n, p, b) in enumerate(zip("ABC", prods, bar))])
        lab[0].set_color(WHITE_)
        cap = T("all the defaulted loans, total 0.037", 26, GREY_).next_to(bar, UP, buff=0.2)
        with self.say("So pull the shaded pieces out and line them up. Together they make up point "
                      "zero three seven, and each grade's share of that total is the answer.") as tr:
            self.play(FadeOut(VGroup(k["square"], k["cols"], k["glabels"])),
                      *[ReplacementTransform(s, b) for s, b in zip(k["shades"], bar)], run_time=2)
            self.play(FadeIn(cap), FadeIn(lab))
            self.fill(tr, 3)
        rule = MathTex(r"P(B_j\mid A)", "=", r"{P(A\mid B_j)\,P(B_j)", r"\over",
                       r"\sum_i P(A\mid B_i)\,P(B_i)}", font_size=50).shift(DOWN * 0.6)
        rule[2].set_color(YELLOW_)
        rule[4].set_color(TEAL_)
        b1 = Brace(rule[2], UP, color=YELLOW_)
        t1 = T("one piece", 26, YELLOW_).next_to(b1, UP, buff=0.1)
        b2 = Brace(rule[4], DOWN, color=TEAL_)
        t2 = T("all the pieces", 26, TEAL_).next_to(b2, DOWN, buff=0.1)
        with self.say("Grade C is only fifteen percent of the book, but almost half of the defaults. "
                      "And that computation is Bayes' rule: one shaded piece, divided by all of the "
                      "shaded pieces.") as tr:
            self.play(Indicate(bar[2], color=YELLOW_))
            self.play(Write(rule), run_time=2)
            self.play(GrowFromCenter(b1), FadeIn(t1), GrowFromCenter(b2), FadeIn(t2))
            self.fill(tr, 5)
        pp = VGroup(T("prior", 28, GREY_), MathTex("0.15", font_size=46),
                    MathTex(r"\longrightarrow", font_size=46),
                    MathTex("0.486", font_size=46, color=YELLOW_), T("posterior", 28, YELLOW_)
                    ).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.5)
        with self.say("Before we saw the default, grade C had fifteen percent. After, it has about "
                      "forty-nine. The first number is called the prior, the second the posterior. "
                      "Evidence is what carries you from one to the other.") as tr:
            self.play(FadeIn(pp, shift=UP * 0.2))
            self.fill(tr, 1)

    # ------------------------------------------------------------ tree
    def tree(self):
        root = np.array([-6.0, 0.2, 0])
        nF, nH = np.array([-2.6, 2.0, 0]), np.array([-2.6, -1.6, 0])
        lv = [np.array([0.9, y, 0]) for y in (2.7, 1.3, -0.9, -2.3)]

        def edge(a, b, lab, c=GREY_):
            ln = Line(a, b, color=c, stroke_width=3, buff=0.3)
            return VGroup(ln, MathTex(lab, font_size=30, color=c).move_to(ln.get_center() + UP * 0.3))
        e1, e2 = edge(root, nF, "0.002"), edge(root, nH, "0.998")
        NF = T("fraud", 28, RED_).move_to(nF)
        NH = T("honest", 28, WHITE_).move_to(nH)
        with self.say("Back to the fraud screen, this time with exact numbers. It helps to draw it as "
                      "a tree. First, split by the truth: fraud with probability point zero zero two, "
                      "honest with probability point nine nine eight.") as tr:
            self.play(FadeIn(Dot(root)), Create(e1), Create(e2), FadeIn(NF), FadeIn(NH))
            self.fill(tr, 1)
        e3, e4 = edge(nF, lv[0], "0.95"), edge(nF, lv[1], "0.05")
        e5, e6 = edge(nH, lv[2], "0.03"), edge(nH, lv[3], "0.97")
        L = VGroup(*[T(s, 26, c).move_to(p + RIGHT * 0.1) for s, c, p in
                     zip(["flagged", "missed", "flagged", "cleared"], [YELLOW_, GREY_, YELLOW_, GREY_], lv)])
        with self.say("Then split by what the screen says. Multiplying along a path gives the "
                      "probability of that whole path.") as tr:
            self.play(*[Create(e) for e in (e3, e4, e5, e6)], FadeIn(L), run_time=2)
            self.fill(tr, 2)
        J1 = MathTex(r"0.002\times0.95=", "0.0019", font_size=32).next_to(L[0], RIGHT, buff=0.4)
        J2 = MathTex(r"0.998\times0.03=", "0.0299", font_size=32).next_to(L[2], RIGHT, buff=0.4)
        J1[1].set_color(YELLOW_)
        J2[1].set_color(YELLOW_)
        with self.say("Two paths end in a flag. Fraud and flagged: point zero zero one nine. Honest "
                      "and flagged: about point zero three. Notice the honest path is sixteen times "
                      "bigger, which is exactly what our dots were telling us.") as tr:
            self.play(Write(J1))
            self.play(Write(J2))
            self.play(Indicate(J2[1], color=YELLOW_))
            self.fill(tr, 4)
        res = MathTex(r"P(\text{fraud}\mid\text{flag})=", r"\frac{0.0019}{0.0019+0.0299}", r"\approx", "0.06",
                      font_size=44).to_edge(DOWN, buff=0.5)
        res[3].set_color(RED_)
        with self.say("Bayes' rule is now just one flagged leaf over both flagged leaves. That's about "
                      "point zero six. Six percent, not ninety-five.") as tr:
            self.play(Write(res), run_time=2)
            self.play(Circumscribe(res[3], color=RED_))
            self.fill(tr, 3)

    # ------------------------------------------------------------ base rate
    def base_rate(self):
        ax = Axes(x_range=[0, 20, 5], y_range=[0, 1, 0.25], x_length=9, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 26}).shift(DOWN * 0.3 + LEFT * 0.4)
        xl = T("share of payments that are fraud (%)", 24, GREY_).next_to(ax, DOWN, buff=0.3)
        yl = MathTex(r"P(\text{fraud}\mid\text{flag})", font_size=30).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        post = lambda p: p * 0.95 / (p * 0.95 + (1 - p) * 0.03)
        curve = ax.plot(lambda x: post(x / 100), x_range=[0.05, 20, 0.05], color=BLUE_, stroke_width=4)
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(20, 0.5), color=GREY_)
        k = ValueTracker(0.2)
        dot = always_redraw(lambda: Dot(ax.c2p(k.get_value(), post(k.get_value() / 100)), color=YELLOW_, radius=0.1))
        read = always_redraw(lambda: MathTex(
            f"{k.get_value():.1f}\\%\\ \\text{{fraud}}\\ \\Rightarrow\\ {100*post(k.get_value()/100):.0f}\\%",
            font_size=36, color=YELLOW_).to_corner(UR, buff=0.6))
        with self.say("How much does that answer depend on how rare fraud is? Keep the screen exactly "
                      "the same, and let the share of fraudulent payments grow.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(Create(curve), Create(half), FadeIn(dot), FadeIn(read), run_time=2)
            self.fill(tr, 3)
        with self.say("At two tenths of a percent we get our six percent. At two percent fraud, a flag "
                      "means about thirty-nine percent. The curve only crosses one half when about "
                      "three percent of payments are fraud. The base rate is doing most of the work.") as tr:
            self.play(k.animate.set_value(2.0), run_time=3)
            self.wait(1)
            self.play(k.animate.set_value(3.06), run_time=2)
            self.wait(1)
            self.play(k.animate.set_value(15), run_time=3)
            self.fill(tr, 10)

    # ------------------------------------------------------------ second test
    def second_test(self):
        row = VGroup(*[Dot(radius=0.12, color=RED_ if i == 0 else YELLOW_) for i in range(16)]).arrange(RIGHT, buff=0.35).shift(UP * 1.6)
        cap = T("the 16 flagged payments", 28, YELLOW_).next_to(row, UP, buff=0.35)
        with self.say("So what can the bank do? Take the sixteen flagged payments and send them to a "
                      "second, independent check: a device check that fails for ninety percent of "
                      "fraud, and for only five percent of honest payments.") as tr:
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in row], lag_ratio=0.08), FadeIn(cap))
            self.fill(tr, 2)
        keep = VGroup(row[0].copy(), row[7].copy())
        tgt = VGroup(Dot(radius=0.16, color=RED_), Dot(radius=0.16, color=YELLOW_)).arrange(RIGHT, buff=0.6).shift(DOWN * 0.4)
        lbl = MathTex(r"\approx\frac{1}{2}", font_size=60).next_to(tgt, RIGHT, buff=0.8)
        with self.say("The fraud almost surely fails again. Of the fifteen honest ones, five percent "
                      "is less than one. So after both checks we're left with roughly one fraud and one "
                      "honest payment. About one in two.") as tr:
            self.play(*[d.animate.set_opacity(0.2) for d in row])
            self.play(TransformFromCopy(row[0], tgt[0]), TransformFromCopy(row[7], tgt[1]), run_time=1.5)
            self.play(Write(lbl))
            self.fill(tr, 3.5)
        chain = VGroup(MathTex("0.002", font_size=46), MathTex(r"\xrightarrow{\text{flag}}", font_size=46),
                       MathTex("0.060", font_size=46, color=YELLOW_), MathTex(r"\xrightarrow{\text{device}}", font_size=46),
                       MathTex("0.533", font_size=46, color=RED_)).arrange(RIGHT, buff=0.35).to_edge(DOWN, buff=0.9)
        with self.say("In exact numbers: the prior of point zero zero two becomes six percent after "
                      "the flag, and that six percent is the prior for the second check, which lifts it "
                      "to fifty-three percent. Today's posterior is tomorrow's prior.") as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in chain], lag_ratio=0.4), run_time=3)
            self.fill(tr, 3)

    # ------------------------------------------------------------ closing
    def closing(self):
        f1 = MathTex(r"P(A)", "=", r"\sum_i P(A\mid B_i)\,P(B_i)", font_size=48)
        f2 = MathTex(r"P(B_j\mid A)", "=", r"{P(A\mid B_j)\,P(B_j)", r"\over", r"P(A)}", font_size=48)
        f1[2].set_color(TEAL_)
        f2[2].set_color(YELLOW_)
        f2[4].set_color(TEAL_)
        g = VGroup(f1, f2).arrange(DOWN, buff=0.8).shift(UP * 0.6)
        l1 = T("add up the pieces", 26, TEAL_).next_to(f1, RIGHT, buff=0.6)
        l2 = T("one piece over all of them", 26, YELLOW_).next_to(f2, RIGHT, buff=0.6)
        VGroup(g, l1, l2).move_to(UP * 0.6)
        with self.say("So here's the whole story in two lines. The law of total probability adds up "
                      "the pieces of a partition. Bayes' rule takes one piece and divides by all of "
                      "them.") as tr:
            self.play(Write(f1), FadeIn(l1), run_time=2)
            self.play(Write(f2), FadeIn(l2), run_time=2)
            self.fill(tr, 4)
        q = T("Accurate compared to what base rate?", 38, BLUE_).to_edge(DOWN, buff=1.0)
        with self.say("And the next time you hear that a test is ninety-five percent accurate, ask "
                      "the question this video is really about: accurate, compared to what base rate? "
                      "The practice problems for this week are on Blackboard. See you in class.") as tr:
            self.play(Write(q), run_time=2)
            self.fill(tr, 2)
