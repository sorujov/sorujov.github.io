"""Lecture 2 intuition video: mean as balance point, variance as average square, n-1, Tchebysheff."""
from common import *

A = np.array([0.4, 0.7, 0.9, 1.1, 1.3, 0.6, 1.5, 0.8, 1.2, 1.0, 1.4, 1.1])
B = np.array([-3.5, 4.2, 1.8, -1.9, 5.1, 0.2, -2.6, 3.4, 2.9, -0.8, 1.6, 1.6])
A = A - A.mean() + 1.0
B = B - B.mean() + 1.0


class Lecture2(IntuitionScene):
    parts = ("hook", "balance", "squares", "n_minus_one", "tchebysheff", "closing")

    def strip(self, data, y, color, lab):
        nl = NumberLine(x_range=[-5, 7, 1], length=11, include_numbers=True, font_size=22, color=GREY_).shift(UP * y)
        dots = VGroup(*[Dot(nl.n2p(v), radius=0.09, color=color) for v in data])
        t = T(lab, 26, color).next_to(nl, UP, buff=0.35).align_to(nl, LEFT)
        return nl, dots, t

    def hook(self):
        a = self.strip(A, 1.3, TEAL_, "Fund A: monthly returns (%)")
        b = self.strip(B, -1.9, YELLOW_, "Fund B: monthly returns (%)")
        with self.say("Two investment funds. Over the past year, both returned exactly one percent a "
                      "month on average. Same mean. Would you be indifferent between them?") as tr:
            for nl, dots, t in (a, b):
                self.play(Create(nl), FadeIn(t), LaggedStart(*[FadeIn(d, scale=0.4) for d in dots], lag_ratio=0.08))
            self.fill(tr, 4)
        with self.say("Of course not. Fund A barely moves. Fund B swings from minus three to plus five. "
                      "One number for the centre isn't enough; we need a second number for the spread.") as tr:
            self.play(Indicate(b[1], color=YELLOW_, scale_factor=1.3), run_time=1.5)
            self.fill(tr, 1.5)
        self.play(FadeOut(VGroup(*a, *b)))
        self.title_card("Centre and spread", 2,
                        "This lecture is about those two numbers: the mean, and the standard deviation. "
                        "And about one surprisingly strong guarantee that connects them.")

    def balance(self):
        nl = NumberLine(x_range=[-5, 7, 1], length=11, include_numbers=True, font_size=22, color=GREY_).shift(DOWN * 0.5)
        dots = VGroup()
        for v in sorted(B):
            k = sum(1 for d in dots if abs(d.get_x() - nl.n2p(v)[0]) < 0.05)
            dots.add(Dot(nl.n2p(v) + UP * (0.2 + 0.22 * k), radius=0.1, color=YELLOW_))
        tri = Triangle(color=WHITE_, fill_opacity=1).scale(0.18).next_to(nl.n2p(3.0), DOWN, buff=0.05)
        with self.say("Start with the mean. Put each observation on a line, as a small weight. Now look "
                      "for the point where the line would balance.") as tr:
            self.play(Create(nl), LaggedStart(*[FadeIn(d, shift=DOWN * 0.3) for d in dots], lag_ratio=0.06))
            self.play(FadeIn(tri))
            self.fill(tr, 3)
        grp = VGroup(nl, dots)
        with self.say("Put the pivot too far right, and the line tips left. Too far left, and it tips "
                      "right. There is exactly one balance point, and it's the mean: the place where "
                      "the deviations on each side cancel out.") as tr:
            self.play(Rotate(grp, 0.12, about_point=tri.get_top()), run_time=1)
            self.play(Rotate(grp, -0.12, about_point=tri.get_top()), run_time=0.6)
            self.play(tri.animate.next_to(nl.n2p(-1.5), DOWN, buff=0.05), run_time=1)
            self.play(Rotate(grp, -0.12, about_point=tri.get_top()), run_time=1)
            self.play(Rotate(grp, 0.12, about_point=tri.get_top()), run_time=0.6)
            self.play(tri.animate.next_to(nl.n2p(1.0), DOWN, buff=0.05), run_time=1)
            m = MathTex(r"\bar y=\tfrac1n\sum y_i=1.0", font_size=44, color=TEAL_).next_to(tri, DOWN, buff=0.6)
            self.play(Write(m))
            self.fill(tr, 7)

    def squares(self):
        nl = NumberLine(x_range=[-5, 7, 1], length=11, include_numbers=True, font_size=22, color=GREY_).shift(DOWN * 2.6)
        u = nl.get_unit_size()
        mean = DashedLine(nl.n2p(1) + DOWN * 0.1, nl.n2p(1) + UP * 5.8, color=TEAL_)
        pts = [-3.5, 5.1, -1.9, 3.4, 0.2]
        dots = VGroup(*[Dot(nl.n2p(v), radius=0.1, color=YELLOW_) for v in pts])
        with self.say("Now the spread. For each observation, measure how far it sits from the mean, and "
                      "draw a square on that distance.") as tr:
            self.play(Create(nl), Create(mean), FadeIn(dots))
            sq = VGroup()
            for v in pts:
                s = abs(v - 1) * u
                r = Square(side_length=s, stroke_color=YELLOW_, fill_color=YELLOW_, fill_opacity=0.15, stroke_width=2)
                r.move_to(nl.n2p((v + 1) / 2) + UP * s / 2)
                sq.add(r)
            self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in sq], lag_ratio=0.3), run_time=3)
            self.fill(tr, 4.5)
        var = MathTex(r"s^2=\frac{1}{n-1}\sum_i (y_i-\bar y)^2", font_size=44).to_corner(UL, buff=0.5)
        sd = MathTex(r"s=\sqrt{s^2}", font_size=44, color=TEAL_).next_to(var, DOWN, buff=0.3).align_to(var, LEFT)
        with self.say("The variance is, roughly, the average area of these squares. Far points get huge "
                      "squares, so they count for a lot. The standard deviation is the side of that "
                      "average square, which brings us back to the units of the data: percent per "
                      "month.") as tr:
            self.play(Write(var))
            self.play(Write(sd))
            self.fill(tr, 3)

    def n_minus_one(self):
        rng = np.random.default_rng(4)
        pop_mu = 1.0
        smp = np.array([2.9, 4.4, 1.2, 3.6, 2.3])
        xbar = smp.mean()
        nl = NumberLine(x_range=[-1, 6, 1], length=11, include_numbers=True, font_size=22, color=GREY_).shift(DOWN * 2.0)
        u = nl.get_unit_size()
        dots = VGroup(*[Dot(nl.n2p(v), radius=0.1, color=YELLOW_) for v in smp])
        mu = DashedLine(nl.n2p(pop_mu), nl.n2p(pop_mu) + UP * 2.4, color=RED_)
        mul = MathTex(r"\mu", font_size=40, color=RED_).next_to(mu, UP, buff=0.1)
        xb = DashedLine(nl.n2p(xbar), nl.n2p(xbar) + UP * 2.4, color=TEAL_)
        xbl = MathTex(r"\bar y", font_size=40, color=TEAL_).next_to(xb, UP, buff=0.1)
        q = T("Why divide by n − 1, not n?", 36).to_edge(UP, buff=0.4)
        with self.say("Why do we divide by n minus one instead of n? Here is the intuition. We want the "
                      "spread around the true mean, mu. But we don't know mu, so we measure distances "
                      "from the sample mean instead.") as tr:
            self.play(FadeIn(q), Create(nl), FadeIn(dots))
            self.play(Create(mu), FadeIn(mul))
            self.play(Create(xb), FadeIn(xbl))
            self.fill(tr, 4)
        s_true = sum((smp - pop_mu) ** 2)
        s_bar = sum((smp - xbar) ** 2)
        r1 = Rectangle(width=s_true / 25 * 5, height=0.45, fill_color=RED_, fill_opacity=0.7, stroke_width=0)
        r2 = Rectangle(width=s_bar / 25 * 5, height=0.45, fill_color=TEAL_, fill_opacity=0.7, stroke_width=0)
        l1 = T("sum of squares around μ", 24, RED_)
        l2 = T("sum of squares around ȳ", 24, TEAL_)
        bars = VGroup(VGroup(l1, r1).arrange(RIGHT, buff=0.3), VGroup(l2, r2).arrange(RIGHT, buff=0.3)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(UP * 1.75 + LEFT * 1.3)
        for g in bars:
            g[1].align_to(bars[0][1], LEFT)
        with self.say("The sample mean sits right in the middle of the sample. That's what a mean does. "
                      "So the data are always closer to their own mean than to the true one, and the "
                      "squares come out too small.") as tr:
            self.play(FadeIn(bars[0]), run_time=1)
            self.play(FadeIn(bars[1]), run_time=1)
            self.fill(tr, 2)
        fix = MathTex(r"\frac{1}{n}\ \to\ \frac{1}{n-1}", font_size=46, color=YELLOW_).next_to(bars, RIGHT, buff=0.8)
        with self.say("Dividing by n minus one, a slightly smaller number, inflates the answer by just "
                      "the right amount to make up for it, on average. With large samples the difference "
                      "hardly matters. With small ones, it does.") as tr:
            self.play(Write(fix))
            self.fill(tr, 1.5)

    def tchebysheff(self):
        q = T("How much data can sit far from the mean?", 36).to_edge(UP, buff=0.5)
        th = MathTex(r"\text{fraction beyond } k \text{ s.d.}\ \le\ \frac{1}{k^2}", font_size=48, color=YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("Now the guarantee. Knowing only the mean and the standard deviation, how much of "
                      "the data can lie far from the mean? Tchebysheff's theorem says: at most one over k "
                      "squared of it can lie more than k standard deviations away. No matter what shape "
                      "the data have.") as tr:
            self.play(FadeIn(q))
            self.play(Write(th), run_time=2)
            self.fill(tr, 3)
        budget = Rectangle(width=10, height=0.7, stroke_color=WHITE_, stroke_width=2).shift(DOWN * 0.6)
        bl = T("total budget of squared distance", 26, GREY_).next_to(budget, UP, buff=0.15)
        chunks = VGroup(*[Rectangle(width=10 / 4, height=0.7, fill_color=YELLOW_, fill_opacity=0.35 + 0.15 * (i % 2),
                                    stroke_width=1, stroke_color=BG) for i in range(4)]).arrange(RIGHT, buff=0).move_to(budget)
        cl = T("each far point costs at least k² s²", 26, YELLOW_).next_to(budget, DOWN, buff=0.3)
        with self.say("Here's why. Think of the total squared distance as a fixed budget. Every point "
                      "that sits more than k standard deviations out spends at least k squared times s "
                      "squared of that budget, all by itself. The budget runs out after one over k squared "
                      "of the data. So far points must be rare.") as tr:
            self.play(Create(budget), FadeIn(bl))
            self.play(LaggedStart(*[FadeIn(c) for c in chunks], lag_ratio=0.5), FadeIn(cl), run_time=3)
            self.fill(tr, 4)
        eg = VGroup(MathTex(r"k=2:\ \le 25\%", font_size=40), MathTex(r"k=3:\ \le 11\%", font_size=40)
                    ).arrange(RIGHT, buff=1.2).to_edge(DOWN, buff=0.6)
        with self.say("At two standard deviations, at most a quarter. At three, at most about eleven "
                      "percent. For nicely mound-shaped data the true fractions are far smaller, about "
                      "five percent and a third of a percent: that's the empirical rule. But Tchebysheff "
                      "holds for anything.") as tr:
            self.play(FadeIn(eg, shift=UP * 0.2))
            self.fill(tr, 1)

    def closing(self):
        a = VGroup(T("mean", 38, TEAL_), T("where the data balance", 30)).arrange(RIGHT, buff=0.5)
        b = VGroup(T("standard deviation", 38, YELLOW_), T("the side of the average square", 30)).arrange(RIGHT, buff=0.5)
        c = VGroup(T("Tchebysheff", 38, RED_), T("far from the mean is always rare", 30)).arrange(RIGHT, buff=0.5)
        g = VGroup(a, b, c).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: the mean is where the data balance. The standard deviation is the side of "
                      "the average square. And Tchebysheff tells you that, whatever the data look like, "
                      "being far from the mean is always rare. Back to our two funds: same balance point, "
                      "very different squares.") as tr:
            for x in (a, b, c):
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 5)
