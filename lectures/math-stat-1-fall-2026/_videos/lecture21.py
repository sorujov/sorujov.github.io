"""Lecture 21 intuition video: the beta distribution — a model for proportions, its shapes, recovery rates, the binomial link."""
from common import *
from scipy.stats import beta as B, norm


class Lecture21(IntuitionScene):
    parts = ("hook", "shapes", "recovery", "binomial", "closing")

    def hook(self):
        q = T("Defaulted SME loans: share of exposure recovered", 36).to_edge(UP, buff=0.6)
        q2 = T("mean 0.40, standard deviation 0.20", 32, GREY_).next_to(q, DOWN, buff=0.25)
        q3 = T("What is P(recovery < 0.20)?", 38, YELLOW_).next_to(q2, DOWN, buff=0.6)
        with self.say("A bank's workout unit has closed two hundred and fifty defaulted small-business "
                      "loans. On average it recovered forty percent of each exposure, with a standard "
                      "deviation of twenty percent. For its provisions it needs the probability that a "
                      "loan recovers less than a fifth.") as tr:
            self.play(FadeIn(q), FadeIn(q2))
            self.play(Write(q3))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2), FadeOut(q3))
        self.title_card("The beta distribution", 21,
                        "A recovery rate is a proportion. It lives between zero and one, and it needs a "
                        "model that knows that.")

    def shapes(self):
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 4, 1], x_length=9, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).shift(DOWN * 0.7 + LEFT * 1.3)
        a, b = ValueTracker(1.0), ValueTracker(1.0)
        curve = always_redraw(lambda: ax.plot(lambda x: min(B.pdf(x, a.get_value(), b.get_value()), 4),
                                              x_range=[0.02, 0.98, 0.005], color=YELLOW_, stroke_width=4))
        lab = always_redraw(lambda: MathTex(rf"\alpha={a.get_value():.1f}", rf"\\ \beta={b.get_value():.1f}",
                                            font_size=40, color=YELLOW_).next_to(ax, RIGHT, buff=0.4).shift(UP * 1.2))
        dens = MathTex(r"f(y)=\frac{y^{\alpha-1}(1-y)^{\beta-1}}{B(\alpha,\beta)},\quad 0\le y\le 1",
                       font_size=36).to_edge(UP, buff=0.4)
        with self.say("The beta density lives on the interval from zero to one, and two parameters shape it. "
                      "Alpha and beta both equal to one give the flat, uniform density.") as tr:
            self.play(Write(dens), Create(ax), run_time=2)
            self.add(curve, lab)
            self.fill(tr, 2)
        with self.say("Make them equal and larger, and the curve becomes a symmetric hump that tightens "
                      "around one half. Make alpha smaller than beta and the mass moves toward zero; swap "
                      "them and it moves toward one. Push both below one and it turns into a U, piled up "
                      "at the two edges.") as tr:
            for av, bv in ((2, 2), (5, 5), (2, 5), (5, 2), (0.5, 0.5), (2, 3)):
                self.play(a.animate.set_value(av), b.animate.set_value(bv), run_time=1.3)
                self.wait(0.5)
            self.fill(tr, 10.8)
        mean = MathTex(r"E(Y)=\frac{\alpha}{\alpha+\beta}", font_size=40, color=TEAL_).next_to(ax, RIGHT, buff=0.4).shift(DOWN * 0.6)
        with self.say("The mean is alpha over alpha plus beta: alpha pulls toward one, beta toward zero.") as tr:
            self.play(Write(mean))
            self.fill(tr, 1)

    def recovery(self):
        ax = Axes(x_range=[-0.4, 1.2, 0.2], y_range=[0, 2.2, 1], x_length=11, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  x_axis_config={"numbers_to_include": [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0]},
                  y_axis_config={"numbers_to_include": [1, 2]}).shift(DOWN * 0.9)
        nc = ax.plot(lambda x: norm.pdf(x, 0.4, 0.2), x_range=[-0.4, 1.2], color=BLUE_, stroke_width=3)
        bc = ax.plot(lambda x: 12 * x * (1 - x) ** 2, x_range=[0, 1], color=YELLOW_, stroke_width=4)
        nl = T("normal", 26, BLUE_).next_to(ax.c2p(0.72, norm.pdf(0.72, 0.4, 0.2)), UR, buff=0.15)
        bl = MathTex(r"\text{Beta}(2,3)=12y(1-y)^2", font_size=30, color=YELLOW_).move_to(ax.c2p(0.74, 1.45), aligned_edge=LEFT)
        neg = ax.get_area(nc, x_range=[-0.4, 0], color=RED_, opacity=0.8)
        negl = T("2.3% below zero", 24, RED_).next_to(ax.c2p(-0.22, 0.25), UP, buff=0.25)
        with self.say("Try the normal first, with mean point four and standard deviation point two. It "
                      "puts two percent of its probability on recovering less than nothing. Now try the "
                      "beta with alpha equal to two and beta equal to three. Its mean is two fifths, its "
                      "standard deviation is point two, so it matches the data, and it never leaves the "
                      "interval from zero to one.") as tr:
            self.play(Create(ax))
            self.play(Create(nc), FadeIn(nl))
            self.play(FadeIn(neg), FadeIn(negl))
            self.play(Create(bc), FadeIn(bl), run_time=2)
            self.fill(tr, 5)
        low = ax.get_area(bc, x_range=[0, 0.2], color=TEAL_, opacity=0.8)
        ans = MathTex(r"P(Y<0.2)=\int_0^{0.2}12y(1-y)^2\,dy=0.181", font_size=36, color=TEAL_).to_edge(UP, buff=0.4)
        with self.say("The probability we want is the area under the beta curve up to point two. It's a "
                      "polynomial, so the integral is easy: about eighteen percent. The normal said sixteen, "
                      "and got the shape wrong at both ends.") as tr:
            self.play(FadeIn(low))
            self.play(Write(ans), run_time=2)
            self.fill(tr, 3)

    def binomial(self):
        rng = np.random.default_rng(7)
        line = NumberLine(x_range=[0, 1, 0.2], length=10, color=GREY_, include_numbers=True, font_size=22).shift(UP * 2.4)
        cut = DashedLine(line.n2p(0.2) + UP * 0.5, line.n2p(0.2) + DOWN * 0.3, color=TEAL_)
        head = T("drop 4 uniform points; keep the 2nd smallest", 30).to_edge(UP, buff=0.25)
        ax = Axes(x_range=[0, 1, 0.2], y_range=[0, 2, 1], x_length=10, y_length=3, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).shift(DOWN * 1.9)
        with self.say("Where does a beta come from? Here's one picture. Drop four points at random on the "
                      "interval from zero to one, and keep the second smallest. Do it again, and again.") as tr:
            self.play(FadeIn(head), Create(line))
            for _ in range(4):
                u = np.sort(rng.uniform(size=4))
                ds = VGroup(*[Dot(line.n2p(x), color=GREY_, radius=0.09) for x in u])
                ds[1].set_color(YELLOW_).scale(1.4)
                self.play(FadeIn(ds, shift=DOWN * 0.3), run_time=0.6)
                self.wait(0.5)
                self.play(FadeOut(ds), run_time=0.4)
            self.fill(tr, 6)
        s = np.sort(rng.uniform(size=(20000, 4)), axis=1)[:, 1]
        w = 0.05
        hts, _ = np.histogram(s, bins=np.arange(0, 1 + w / 2, w), density=True)
        bars = VGroup(*[Rectangle(width=w * ax.x_axis.get_unit_size(), height=max(h, 1e-3) * ax.y_axis.get_unit_size(),
                                  stroke_width=1, stroke_color=BG, fill_color=BLUE_, fill_opacity=0.8)
                        .move_to(ax.c2p(i * w, 0), aligned_edge=DL) for i, h in enumerate(hts)])
        bc = ax.plot(lambda x: 12 * x * (1 - x) ** 2, x_range=[0, 1], color=YELLOW_, stroke_width=4)
        bl = MathTex(r"\text{Beta}(2,3)", font_size=32, color=YELLOW_).next_to(ax.c2p(0.62, 12 * 0.62 * 0.38 ** 2), UR, buff=0.15)
        with self.say("Twenty thousand times, the second smallest point piles up into exactly our "
                      "beta two, three curve.") as tr:
            self.play(Create(ax), LaggedStart(*[GrowFromEdge(r, DOWN) for r in bars], lag_ratio=0.05), run_time=2.5)
            self.play(Create(bc), FadeIn(bl))
            self.fill(tr, 3.5)
        ex = MathTex(r"P(Y<0.2)=P(\text{at least 2 of 4 below }0.2)=1-0.8^4-4(0.2)(0.8)^3=0.181",
                     font_size=32, color=TEAL_).next_to(line, DOWN, buff=0.55)
        with self.say("And that explains the binomial link. The second smallest is below point two exactly "
                      "when at least two of the four points fall below point two. That's a binomial count "
                      "with n equal to four and p equal to point two, and it gives the same eighteen percent, "
                      "with no integral at all.") as tr:
            self.play(Create(cut))
            self.play(Write(ex), run_time=2.5)
            self.fill(tr, 3.5)

    def closing(self):
        g = VGroup(
            VGroup(T("beta(α, β)", 38, YELLOW_), T("a density for proportions, on [0, 1]", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("shape", 38, BLUE_), T("flat, hump, skewed or U, set by α and β", 30)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"\frac{\alpha}{\alpha+\beta}", font_size=44, color=TEAL_), T("the mean", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("binomial link", 38, PURPLE_), T("integer α, β: tail sums replace integrals", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say("So: when the quantity is a proportion, reach for the beta. Two parameters give "
                      "it almost any shape on zero to one, its mean is alpha over alpha plus beta, and with "
                      "integer parameters its probabilities are binomial sums.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5.2)
