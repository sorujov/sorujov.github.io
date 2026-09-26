"""Lecture 17 intuition video: from histograms to densities; probability as area; F as accumulated area."""
from common import *
from scipy.stats import gamma

SHAPE, SCALE = 2.0, 1.5          # payment processing time, minutes


def f(x):
    return gamma.pdf(x, SHAPE, scale=SCALE)


def F(x):
    return gamma.cdf(x, SHAPE, scale=SCALE)


class Lecture17(IntuitionScene):
    parts = ("hook", "histograms", "area", "cdf", "closing")

    def hook(self):
        q = T("How long does a payment take to clear?", 40)
        q2 = T("What is P(exactly 3.000... minutes)?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("How long does a payment take to clear? Time is continuous: two minutes, two point "
                      "five, two point five one... So what's the probability that it takes exactly three "
                      "minutes, to infinitely many decimal places?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Continuous random variables", 17,
                        "The answer is zero, and understanding why leads straight to the idea of a "
                        "density.")

    def axes(self):
        return Axes(x_range=[0, 12, 2], y_range=[0, 0.3, 0.1], x_length=10, y_length=4.2, tips=False,
                    axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.5)

    def hist(self, ax, w, color=BLUE_):
        edges = np.arange(0, 12, w)
        bars = VGroup()
        for a in edges:
            h = (F(a + w) - F(a)) / w
            bars.add(Rectangle(width=w * ax.x_axis.get_unit_size(), height=h * ax.y_axis.get_unit_size(),
                               stroke_width=1 if w > 0.3 else 0, stroke_color=BG, fill_color=color, fill_opacity=0.8
                               ).move_to(ax.c2p(a, 0), aligned_edge=DL))
        return bars

    def histograms(self):
        ax = self.axes()
        xl = T("minutes to clear", 26, GREY_).next_to(ax, DOWN, buff=0.3)
        yl = T("probability per minute", 24, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        h = self.hist(ax, 2)
        with self.say("Record thousands of payments and draw a histogram, with bars two minutes wide. "
                      "Make each bar's area, not its height, equal to the share of payments in that "
                      "range. Then the total area is one.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in h], lag_ratio=0.1), run_time=2)
            self.fill(tr, 3)
        curve = ax.plot(f, x_range=[0.01, 12], color=YELLOW_, stroke_width=4)
        with self.say("Now make the bars narrower. One minute. Half a minute. A tenth of a minute. The "
                      "outline stops being jagged and settles onto a smooth curve. That curve is the "
                      "probability density function, f of y.") as tr:
            for w in (1, 0.5, 0.1):
                self.play(Transform(h, self.hist(ax, w)), run_time=1.5)
                self.wait(0.4)
            self.play(Create(curve))
            fl = MathTex("f(y)", font_size=40, color=YELLOW_).next_to(ax.c2p(3.5, f(3)), UR, buff=0.1)
            self.play(FadeIn(fl))
            self.fill(tr, 7)
        self.stuff = VGroup(ax, xl, yl, curve, fl)
        self.hbars = h

    def area(self):
        ax, xl, yl, curve, fl = self.stuff
        self.add(self.stuff)
        a, b = 2, 4
        reg = ax.get_area(curve, x_range=[a, b], color=TEAL_, opacity=0.6)
        p = MathTex(rf"P({a}\le Y\le {b})=\int_{a}^{b}f(y)\,dy\approx{F(b) - F(a):.2f}", font_size=40, color=TEAL_).to_corner(UR, buff=0.5)
        with self.say("Probabilities are now areas under the curve. The chance a payment takes between "
                      "two and four minutes is the area between two and four: about thirty-six percent.") as tr:
            self.play(FadeIn(reg))
            self.play(Write(p), run_time=2)
            self.fill(tr, 3)
        w = ValueTracker(1.0)
        thin = always_redraw(lambda: ax.get_area(curve, x_range=[3 - w.get_value(), 3 + w.get_value()], color=RED_, opacity=0.8))
        z = MathTex(r"P(Y=3)=0", font_size=44, color=RED_).next_to(p, DOWN, buff=0.4).align_to(p, RIGHT)
        with self.say("And the probability of exactly three minutes? Shrink an interval around three. "
                      "The area shrinks with it, all the way to zero. A single point has no width, so it "
                      "has no area. For continuous variables, individual values have probability zero, and "
                      "only intervals matter.") as tr:
            self.play(FadeOut(reg), FadeOut(p))
            self.add(thin)
            self.play(w.animate.set_value(0.02), run_time=4)
            self.play(Write(z))
            self.fill(tr, 5.5)
        self.remove(thin)

    def cdf(self):
        ax = self.axes()
        ax2 = Axes(x_range=[0, 12, 2], y_range=[0, 1, 0.5], x_length=10, y_length=2.2, tips=False,
                   axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).to_edge(UP, buff=0.5)
        ax.scale(0.75).to_edge(DOWN, buff=0.4)
        curve = ax.plot(f, x_range=[0.01, 12], color=YELLOW_)
        y = ValueTracker(0.3)
        reg = always_redraw(lambda: ax.get_area(curve, x_range=[0.01, y.get_value()], color=TEAL_, opacity=0.6))
        Fc = always_redraw(lambda: ax2.plot(F, x_range=[0, y.get_value()], color=TEAL_, stroke_width=4))
        dot = always_redraw(lambda: Dot(ax2.c2p(y.get_value(), F(y.get_value())), color=TEAL_))
        l1 = MathTex("f(y)", font_size=34, color=YELLOW_).next_to(ax, LEFT, buff=0.2)
        l2 = MathTex(r"F(y)=P(Y\le y)", font_size=34, color=TEAL_).next_to(ax2, DOWN, buff=0.15).align_to(ax2, RIGHT)
        with self.say("Finally, the distribution function, capital F of y: the probability of being at "
                      "most y, which is the area to the left of y. Sweep y across, and watch that area "
                      "accumulate into F.") as tr:
            self.play(Create(ax), Create(curve), Create(ax2), FadeIn(l1), FadeIn(l2))
            self.add(reg, Fc, dot)
            self.play(y.animate.set_value(11.9), run_time=6, rate_func=linear)
            self.fill(tr, 8)
        r = MathTex(r"f(y)=F'(y)", font_size=44, color=WHITE_).move_to(RIGHT * 4 + DOWN * 0.1)
        with self.say("F climbs fastest where the density is tallest, and it flattens out at one. In "
                      "fact the density is exactly the slope of F. For a discrete variable, F would be a "
                      "staircase that jumps at each value; for a continuous one, it rises smoothly, with no "
                      "jumps at all.") as tr:
            self.play(Write(r))
            self.fill(tr, 1.5)

    def closing(self):
        g = VGroup(
            VGroup(T("density f", 38, YELLOW_), T("histogram with infinitely thin bars", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("probability", 38, TEAL_), T("area under f over an interval", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("single points", 38, RED_), T("probability zero", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("distribution F", 38, BLUE_), T("area so far; f is its slope", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("So: a density is what a histogram becomes when the bars are infinitely thin. "
                      "Probabilities are areas under it. Single points get probability zero. And the "
                      "distribution function is the area accumulated so far, with the density as its "
                      "slope.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5)
