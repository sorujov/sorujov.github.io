"""Lecture 16 intuition video: probability-generating functions and Tchebysheff for random variables."""
from common import *

YS = [0, 1, 2, 3]
PS = [0.50, 0.30, 0.15, 0.05]


class Lecture16(IntuitionScene):
    parts = ("hook", "pgf", "factorial", "tchebysheff", "closing")

    def hook(self):
        q = T("A risk desk knows only a mean and a standard deviation.", 36)
        q2 = T("How bad can a day get, with no model of the shape?", 36, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A bank's risk desk counts failed transactions each day. It knows the average and "
                      "the standard deviation, but it has no idea what the distribution looks like. Can it "
                      "still say how rare a really bad day is?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Generating functions and Tchebysheff", 16,
                        "Two tools today. One packs a whole count distribution into a polynomial. The "
                        "other bounds the tails using only two numbers.")

    def pgf(self):
        d = MathTex(r"P(t)=E\!\left(t^{Y}\right)", font_size=52, color=YELLOW_).to_edge(UP, buff=0.7)
        with self.say("For random variables that count things, zero, one, two and so on, there's a cousin "
                      "of the moment-generating function: the probability-generating function, P of t "
                      "equals the expected value of t to the Y.") as tr:
            self.play(Write(d))
            self.fill(tr, 1.5)
        poly = MathTex(r"P(t)", "=", "0.50", r"\,t^0", "+", "0.30", r"\,t^1", "+", "0.15", r"\,t^2", "+", "0.05", r"\,t^3",
                       font_size=50).next_to(d, DOWN, buff=0.9)
        for k in (2, 5, 8, 11):
            poly[k].set_color(TEAL_)
        ax = Axes(x_range=[0, 4.4, 1], y_range=[0, 0.6, 0.2], x_length=5, y_length=2.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [0.2, 0.4]}).next_to(poly, DOWN, buff=0.7)
        ax.add(VGroup(*[MathTex(str(y), font_size=26).next_to(ax.c2p(y + 0.7, 0), DOWN, buff=0.15) for y in YS]))
        bars = VGroup(*[Rectangle(width=0.6, height=p * ax.y_axis.get_unit_size(), stroke_width=0, fill_color=TEAL_,
                                  fill_opacity=0.8).move_to(ax.c2p(y + 0.7, 0), aligned_edge=DOWN) for y, p in zip(YS, PS)])
        with self.say("Write it out for the outage example. It's just a polynomial, and its coefficients "
                      "are the probabilities themselves. The coefficient of t to the y is the probability "
                      "that Y equals y. The whole distribution, hung on a line of powers of t.") as tr:
            self.play(Write(poly), run_time=2.5)
            self.play(Create(ax), LaggedStart(*[TransformFromCopy(poly[k], b) for k, b in zip((2, 5, 8, 11), bars)], lag_ratio=0.3), run_time=2.5)
            self.fill(tr, 5)

    def factorial(self):
        f1 = MathTex(r"P(1)=\sum_y p(y)=1", font_size=46).shift(UP * 1.6)
        f2 = MathTex(r"P'(t)=\sum_y y\,p(y)\,t^{y-1}\ \Rightarrow\ P'(1)=E(Y)", font_size=46, color=TEAL_).next_to(f1, DOWN, buff=0.6)
        f3 = MathTex(r"P''(1)=E\big[Y(Y-1)\big]", font_size=46, color=RED_).next_to(f2, DOWN, buff=0.6)
        with self.say("Setting t to one adds up all the coefficients, so P of one is always one. "
                      "Differentiate once, and set t to one: each probability gets multiplied by its y. "
                      "That's the mean. Differentiate twice and you get the expected value of Y times Y "
                      "minus one, a factorial moment, from which the variance follows.") as tr:
            self.play(Write(f1))
            self.play(Write(f2), run_time=2)
            self.play(Write(f3), run_time=1.5)
            self.fill(tr, 5)
        n = T("MGF: differentiate at t = 0.   PGF: differentiate at t = 1.", 30, GREY_).to_edge(DOWN, buff=0.8)
        with self.say("So the recipe mirrors the MGF, except that for the PGF you evaluate at one "
                      "instead of zero.") as tr:
            self.play(FadeIn(n))
            self.fill(tr, 1)

    def tchebysheff(self):
        th = MathTex(r"P\big(|Y-\mu|\ge k\sigma\big)\le\frac{1}{k^2}", font_size=52, color=YELLOW_).to_edge(UP, buff=0.6)
        with self.say("Now the risk desk. Tchebysheff's theorem, which we met for data, holds for any "
                      "random variable: the probability of landing k or more standard deviations from the "
                      "mean is at most one over k squared.") as tr:
            self.play(Write(th), run_time=2)
            self.fill(tr, 2)
        ax = Axes(x_range=[-4, 4, 1], y_range=[0, 0.75, 0.25], x_length=10, y_length=3.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}).shift(DOWN * 1.2)
        shapes = [lambda x: np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi),
                  lambda x: np.exp(-abs(x) * np.sqrt(2)) / np.sqrt(2),
                  lambda x: (0.35 if abs(x) < 1.3 else 0.0) + (0.12 if 1.6 < abs(x) < 2.6 else 0.0)]
        k = 2
        curves = [ax.plot(f, x_range=[-4, 4, 0.02], color=c, use_smoothing=False) for f, c in zip(shapes, [BLUE_, TEAL_, PURPLE_])]
        lines = VGroup(*[DashedLine(ax.c2p(s * k, 0), ax.c2p(s * k, 0.75), color=RED_) for s in (-1, 1)])
        lab = MathTex(r"\pm 2\sigma", font_size=34, color=RED_).next_to(lines[1], UP, buff=0.1)
        cap = T("whatever the shape: at most 25% beyond ±2σ", 28, RED_).next_to(ax, DOWN, buff=0.4)
        with self.say("Its power is that the shape doesn't matter. A bell curve, a sharp peak with long "
                      "tails, or something lumpy and strange: as long as the mean and standard deviation "
                      "are what they are, at most a quarter of the probability lies beyond two standard "
                      "deviations.") as tr:
            self.play(Create(ax), Create(lines), FadeIn(lab))
            cur = curves[0]
            self.play(Create(cur))
            for c in curves[1:]:
                self.play(Transform(cur, c), run_time=1.5)
                self.wait(0.8)
            self.play(FadeIn(cap))
            self.fill(tr, 7.5)
        ex = MathTex(r"\mu=40,\ \sigma=5:\quad P(Y\ge 55)\le P(|Y-40|\ge 3\sigma)\le\tfrac19", font_size=40).next_to(th, DOWN, buff=0.4)
        with self.say("For the risk desk: if failures average forty a day with a standard deviation of "
                      "five, then a day with fifty-five or more is at least three standard deviations out, "
                      "so its probability is at most one ninth. That's a guarantee, with no model at all. "
                      "It's usually conservative, but it's never wrong.") as tr:
            self.play(Write(ex), run_time=2.5)
            self.fill(tr, 2.5)

    def closing(self):
        g = VGroup(
            VGroup(T("PGF", 38, TEAL_), T("probabilities as coefficients; differentiate at t = 1", 28)).arrange(RIGHT, buff=0.5),
            VGroup(T("Tchebysheff", 38, YELLOW_), T("at most 1/k² beyond k σ, for any distribution", 28)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: the probability-generating function hangs the probabilities on powers of t, "
                      "and its derivatives at one give the moments. And Tchebysheff gives a tail bound "
                      "that holds for every distribution, from just the mean and the standard deviation.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 3)
