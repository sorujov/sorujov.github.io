"""Lecture 15 intuition video: moments, and the moment-generating function as a package of all of them."""
from common import *

YS = [0, 1, 2, 3]
PS = [0.50, 0.30, 0.15, 0.05]


def m(t):
    return sum(p * np.exp(t * y) for y, p in zip(YS, PS))


class Lecture15(IntuitionScene):
    parts = ("hook", "moments", "package", "derivative", "fingerprint", "closing")

    def hook(self):
        q = T("Mean, variance, skewness, tail weight ...", 40)
        q2 = T("Is there one object that holds them all?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("We describe a distribution by a few numbers: its mean, its variance, sometimes "
                      "its skewness or how heavy its tails are. Each one takes its own calculation. Is "
                      "there a single object that holds all of them at once?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Moment-generating functions", 15,
                        "There is, and it's called the moment-generating function. The name tells you "
                        "exactly what it does.")

    def moments(self):
        rows = VGroup(
            VGroup(MathTex(r"\mu_1'=E(Y)", font_size=44), T("where it balances", 28, GREY_)).arrange(RIGHT, buff=0.6),
            VGroup(MathTex(r"\mu_2'=E(Y^2)", font_size=44), T("with the mean, gives the spread", 28, GREY_)).arrange(RIGHT, buff=0.6),
            VGroup(MathTex(r"\mu_3'=E(Y^3)", font_size=44), T("lopsidedness", 28, GREY_)).arrange(RIGHT, buff=0.6),
            VGroup(MathTex(r"\mu_k'=E(Y^k)", font_size=44), T("... and so on", 28, GREY_)).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("The k-th moment of Y is the expected value of Y to the k. The first moment is the "
                      "mean. The second, together with the first, gives the variance. The third measures "
                      "lopsidedness, and there are infinitely many more.") as tr:
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(1)
            self.fill(tr, 7.2)

    def package(self):
        d = MathTex(r"m(t)=E\!\left(e^{tY}\right)", font_size=54, color=YELLOW_).to_edge(UP, buff=0.7)
        with self.say("Here is the trick. Define m of t as the expected value of e to the t Y. At first "
                      "sight it looks like a strange thing to compute.") as tr:
            self.play(Write(d))
            self.fill(tr, 1.5)
        ex = MathTex(r"e^{tY}", "=", "1", "+", "tY", "+", r"\frac{t^2Y^2}{2!}", "+", r"\frac{t^3Y^3}{3!}", "+", r"\cdots", font_size=46).next_to(d, DOWN, buff=0.8)
        ex2 = MathTex(r"m(t)", "=", "1", "+", r"t\,E(Y)", "+", r"\frac{t^2}{2!}E(Y^2)", "+", r"\frac{t^3}{3!}E(Y^3)", "+", r"\cdots", font_size=46).next_to(ex, DOWN, buff=0.7)
        for k, c in zip([4, 6, 8], [TEAL_, RED_, PURPLE_]):
            ex2[k].set_color(c)
        with self.say("But expand the exponential as a power series: one, plus t Y, plus t squared Y "
                      "squared over two factorial, and so on. Now take expectations term by term. Every "
                      "moment appears, each attached to its own power of t. The moments are packed into "
                      "one function, like items on a clothesline.") as tr:
            self.play(Write(ex), run_time=2.5)
            self.play(TransformMatchingTex(ex.copy(), ex2), run_time=2.5)
            self.fill(tr, 5)

    def derivative(self):
        ax = Axes(x_range=[-1, 1, 0.5], y_range=[0, 4, 1], x_length=6, y_length=4.5, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(LEFT * 3 + DOWN * 0.4)
        c = ax.plot(m, x_range=[-1, 1], color=YELLOW_)
        lab = MathTex("m(t)", font_size=36, color=YELLOW_).next_to(ax.c2p(1, m(1)), LEFT, buff=0.2)
        mu = sum(y * p for y, p in zip(YS, PS))
        tan = ax.plot(lambda t: 1 + mu * t, x_range=[-0.8, 0.8], color=TEAL_)
        dot = Dot(ax.c2p(0, 1), color=TEAL_)
        with self.say("To get a moment back out, differentiate and set t to zero. Differentiating once "
                      "knocks the first term away, and at t equals zero all higher terms vanish, leaving "
                      "the mean. Geometrically, the mean is the slope of m at zero.") as tr:
            self.play(Create(ax), Create(c), FadeIn(lab))
            self.play(FadeIn(dot), Create(tan))
            self.fill(tr, 3)
        f = VGroup(MathTex(r"m'(0)=E(Y)", font_size=44, color=TEAL_),
                   MathTex(r"m''(0)=E(Y^2)", font_size=44, color=RED_),
                   MathTex(r"m^{(k)}(0)=E(Y^k)", font_size=44)).arrange(DOWN, aligned_edge=LEFT, buff=0.45).shift(RIGHT * 3.2)
        with self.say("Differentiate twice for the second moment, and k times for the k-th. For the outage "
                      "example from lecture ten, the slope at zero is point seven five, exactly the mean we "
                      "found before.") as tr:
            self.play(LaggedStart(*[Write(x) for x in f], lag_ratio=0.5), run_time=3)
            self.fill(tr, 3)

    def fingerprint(self):
        t1 = T("Same MGF  ⇒  same distribution", 40, YELLOW_).shift(UP * 1.5)
        t2 = T("An MGF is a fingerprint.", 34).next_to(t1, DOWN, buff=0.5)
        e = MathTex(r"(pe^t+q)^n\ \Longleftrightarrow\ \text{Binomial}(n,p)", font_size=44, color=TEAL_).next_to(t2, DOWN, buff=0.8)
        with self.say("There's a second reason MGFs matter. Two distributions with the same MGF are the "
                      "same distribution. So an MGF works like a fingerprint: if you recognise it, you know "
                      "the distribution. For example, p e to the t plus q, all to the n, belongs to the "
                      "binomial and nothing else. Later in the course, this is how we identify the "
                      "distribution of sums of random variables.") as tr:
            self.play(Write(t1))
            self.play(FadeIn(t2))
            self.play(Write(e), run_time=2)
            self.fill(tr, 5)

    def closing(self):
        g = VGroup(
            MathTex(r"m(t)=E(e^{tY})=\sum_k \frac{t^k}{k!}E(Y^k)", font_size=48),
            T("all the moments, on one clothesline", 32, YELLOW_),
            T("differentiate at 0 to take one off", 32, TEAL_),
        ).arrange(DOWN, buff=0.5)
        with self.say("So the moment-generating function is all the moments on one clothesline. "
                      "Differentiate at zero to take one off the line. And because the line identifies the "
                      "distribution, it's also a fingerprint.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=UP * 0.2))
                self.wait(0.6)
            self.fill(tr, 4)
