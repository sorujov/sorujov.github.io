"""Lecture 18 intuition video: expected value for continuous variables; the uniform distribution."""
from common import *
from scipy.stats import gamma

SHAPE, SCALE = 2.0, 1.5


def f(x):
    return gamma.pdf(x, SHAPE, scale=SCALE)


class Lecture18(IntuitionScene):
    parts = ("hook", "from_sums", "uniform", "variance", "closing")

    def hook(self):
        q = T("Payments take a random, continuous amount of time.", 38)
        q2 = T("What is the average, when every value has probability zero?", 32, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("Last time we saw that a continuous random variable gives probability zero to "
                      "every single value. So how can we talk about its average? For discrete variables "
                      "we summed value times probability. What replaces that?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Continuous expectation; the uniform", 18,
                        "The answer is the same idea, taken to the limit. And then we'll meet the simplest "
                        "continuous distribution of all.")

    def from_sums(self):
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 0.3, 0.1], x_length=10, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(UP * 0.1)
        xl = T("minutes to clear", 26, GREY_).next_to(ax, DOWN, buff=0.9)

        def bars(w):
            g = VGroup()
            for a in np.arange(0, 12, w):
                mid = a + w / 2
                g.add(Rectangle(width=w * ax.x_axis.get_unit_size(), height=f(mid) * ax.y_axis.get_unit_size(), stroke_width=1 if w > 0.3 else 0,
                                stroke_color=BG, fill_color=BLUE_, fill_opacity=0.8).move_to(ax.c2p(a, 0), aligned_edge=DL))
            return g
        b = bars(2)
        s1 = MathTex(r"E(Y)\approx\sum_i y_i\,f(y_i)\,\Delta y", font_size=44).to_corner(UR, buff=0.5)
        with self.say("Chop the time axis into strips. Each strip is a little bit like a discrete value: "
                      "its probability is about f of y times the width of the strip. So the mean is "
                      "approximately the sum of y times f of y times delta y, over the strips.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(LaggedStart(*[GrowFromEdge(x, DOWN) for x in b], lag_ratio=0.1))
            self.play(Write(s1))
            self.fill(tr, 4)
        s2 = MathTex(r"E(Y)=\int y\,f(y)\,dy", font_size=48, color=YELLOW_).next_to(s1, DOWN, buff=0.4).align_to(s1, RIGHT)
        curve = ax.plot(f, x_range=[0.01, 12], color=YELLOW_)
        with self.say("Make the strips thinner and thinner, and the sum becomes an integral: the expected "
                      "value is the integral of y times f of y. Sums become integrals, probabilities become "
                      "areas, and everything else carries over.") as tr:
            for w in (1, 0.5, 0.1):
                self.play(Transform(b, bars(w)), run_time=1.2)
            self.play(Create(curve), Write(s2))
            self.fill(tr, 5)
        mu = SHAPE * SCALE
        tri = Triangle(color=TEAL_, fill_opacity=1).scale(0.18).next_to(ax.c2p(mu, 0), DOWN, buff=0.35)
        ml = MathTex(r"E(Y)=3", font_size=40, color=TEAL_).next_to(ax.c2p(mu, f(mu)), UR, buff=0.2)
        with self.say("And the picture is the one we know: the expected value is the point where the area "
                      "under the density would balance, here three minutes. It sits to the right of the "
                      "peak, pulled out by the long tail of slow payments.") as tr:
            self.play(FadeIn(tri, shift=UP * 0.2), FadeIn(ml))
            self.fill(tr, 1)

    def uniform(self):
        q = T("A settlement arrives at a random moment between 10:00 and 10:30.", 32).to_edge(UP, buff=0.6)
        ax = Axes(x_range=[0, 40, 10], y_range=[0, 0.06, 0.02], x_length=10, y_length=3.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.6)
        xl = T("minutes after 10:00", 24, GREY_).next_to(ax, DOWN, buff=0.9)
        rect = Rectangle(width=30 * ax.x_axis.get_unit_size(), height=(1 / 30) * ax.y_axis.get_unit_size(), stroke_color=YELLOW_,
                         fill_color=YELLOW_, fill_opacity=0.35).move_to(ax.c2p(0, 0), aligned_edge=DL)
        h = MathTex(r"f(y)=\frac{1}{b-a}=\frac{1}{30}", font_size=40, color=YELLOW_).to_corner(UR, buff=0.5).shift(DOWN * 1.2)
        with self.say("Now the simplest continuous distribution. A settlement arrives at a completely "
                      "random moment between ten o'clock and ten thirty, with no time more likely than "
                      "any other. The density is flat. And since the total area must be one, its height "
                      "is one over the width: one thirtieth.") as tr:
            self.play(FadeIn(q))
            self.play(Create(ax), FadeIn(xl))
            self.play(GrowFromEdge(rect, DOWN), Write(h))
            self.fill(tr, 4)
        sub = ax.get_area(ax.plot(lambda x: 1 / 30, x_range=[5, 15]), x_range=[5, 15], color=TEAL_, opacity=0.7)
        p = MathTex(r"P(5\le Y\le15)=\frac{10}{30}=\frac13", font_size=40, color=TEAL_).next_to(h, DOWN, buff=0.3).align_to(h, RIGHT)
        with self.say("Probabilities are just lengths, as fractions of the window. Between five and "
                      "fifteen minutes past: ten out of thirty, one third.") as tr:
            self.play(FadeIn(sub), Write(p))
            self.fill(tr, 1.5)
        tri = Triangle(color=RED_, fill_opacity=1).scale(0.18).next_to(ax.c2p(15, 0), DOWN, buff=0.35)
        m = MathTex(r"E(Y)=\frac{a+b}{2}=15", font_size=40, color=RED_).next_to(ax.c2p(15, 1 / 30), UP, buff=0.25)
        with self.say("And a flat block balances right in its middle. The mean of a uniform is the "
                      "midpoint, a plus b over two: fifteen minutes past ten.") as tr:
            self.play(FadeOut(sub), FadeIn(tri), Write(m))
            self.fill(tr, 1.5)

    def variance(self):
        v = MathTex(r"V(Y)=\frac{(b-a)^2}{12}", font_size=56, color=YELLOW_).shift(UP * 1.2)
        s = MathTex(r"\sigma=\frac{b-a}{\sqrt{12}}\approx0.29\,(b-a)", font_size=44).next_to(v, DOWN, buff=0.6)
        n = T("for the window: σ ≈ 8.7 minutes", 30, TEAL_).next_to(s, DOWN, buff=0.5)
        with self.say("Its variance is b minus a squared, over twelve. So the standard deviation is about "
                      "twenty-nine percent of the window's width: for a thirty-minute window, about eight "
                      "point seven minutes. Wider window, proportionally more uncertainty.") as tr:
            self.play(Write(v))
            self.play(Write(s))
            self.play(FadeIn(n))
            self.fill(tr, 4)

    def closing(self):
        g = VGroup(
            VGroup(T("continuous mean", 38, YELLOW_), MathTex(r"\int y f(y)\,dy", font_size=44), T("the balance point of the area", 28, GREY_)).arrange(RIGHT, buff=0.4),
            VGroup(T("uniform on [a, b]", 38, TEAL_), T("flat; mean (a+b)/2; variance (b−a)²/12", 28)).arrange(RIGHT, buff=0.4),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: for continuous variables, the mean is the integral of y f of y, still the "
                      "balance point of the area. And the uniform distribution is a flat block: its mean is "
                      "the midpoint and its variance is the width squared over twelve.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 3)
