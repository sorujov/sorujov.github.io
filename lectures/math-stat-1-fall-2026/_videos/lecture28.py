"""Lecture 28 intuition video: the multinomial distribution — trials into cells, binomial marginals, negative covariance, revenue risk."""
from common import *

N = 200
P = (0.50, 0.35, 0.15)
PRICE = (10, 20, 35)
NAMES = ("Basic", "Standard", "Premium")
COLS = (BLUE_, TEAL_, PURPLE_)


class Lecture28(IntuitionScene):
    parts = ("hook", "trials", "marginal", "covariance", "revenue", "closing")

    def hook(self):
        q = T("200 new subscribers: Basic 10, Standard 20, Premium 35 AZN", 34)
        q2 = T("How uncertain is next month's revenue?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A mobile operator in Baku signs two hundred new subscribers. Each one picks a "
                      "tariff: Basic at ten manat a month, Standard at twenty, or Premium at thirty-five. "
                      "How uncertain is next month's revenue? To answer that, we need the counts in all "
                      "three tariffs at once.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("The multinomial distribution", 28,
                        "That is the multinomial distribution: the binomial, with more than two "
                        "outcomes.")

    def bins(self):
        g = VGroup()
        for i in range(3):
            x = -4 + 4 * i
            box = VGroup(Line([x - 1.1, -1.2, 0], [x - 1.1, -3.2, 0]), Line([x - 1.1, -3.2, 0], [x + 1.1, -3.2, 0]),
                         Line([x + 1.1, -3.2, 0], [x + 1.1, -1.2, 0])).set_color(COLS[i])
            lab = T(f"{NAMES[i]}  p = {P[i]:.2f}", 26, COLS[i]).next_to(box, UP, buff=0.2)
            g.add(VGroup(box, lab))
        return g

    def trials(self):
        bins = self.bins()
        src = T("subscriber", 26, GREY_).move_to(UP * 2.9)
        rng = np.random.default_rng(7)
        picks = rng.choice(3, size=20, p=P)
        counts = [0, 0, 0]
        cnt = VGroup(*[MathTex(f"Y_{i + 1}=0", font_size=36, color=COLS[i]).move_to([-4 + 4 * i, -3.6, 0]) for i in range(3)])
        with self.say("Picture each subscriber as a ball dropping into one of three bins, independently, "
                      "with the same probabilities every time: one half, point three five, and point one "
                      "five. Here are the first twenty. Y one, Y two and Y three count the balls in each "
                      "bin, and together they always add up to n.") as tr:
            self.play(FadeIn(bins), FadeIn(src), FadeIn(cnt))
            for c in picks:
                k = counts[c]
                counts[c] += 1
                d = Dot(UP * 2.4, radius=0.14, color=COLS[c])
                x = -4 + 4 * c - 0.75 + 0.5 * (k % 4)
                y = -2.95 + 0.4 * (k // 4)
                new = MathTex(f"Y_{c + 1}={counts[c]}", font_size=36, color=COLS[c]).move_to(cnt[c])
                self.play(d.animate.move_to([x, y, 0]), Transform(cnt[c], new), run_time=0.3)
            self.fill(tr, 1 + 0.3 * len(picks))
        self.counts = counts
        f1 = MathTex(r"p(y_1,y_2,y_3)=", r"\frac{n!}{y_1!\,y_2!\,y_3!}", r"\;p_1^{y_1}p_2^{y_2}p_3^{y_3}", font_size=44).move_to(UP * 1.4)
        b1 = Brace(f1[2], DOWN, color=YELLOW_)
        t1 = T("one ordered sequence", 24, YELLOW_).next_to(b1, DOWN, buff=0.1)
        b2 = Brace(f1[1], UP, color=RED_)
        t2 = T("number of orderings", 24, RED_).next_to(b2, UP, buff=0.1)
        with self.say("The probability of a particular set of counts has two factors, just as in Chapter "
                      "two. One ordered sequence with these counts has probability p one to the y one, "
                      "times p two to the y two, times p three to the y three. And the coefficient counts "
                      "how many orderings give the same counts.") as tr:
            self.play(FadeOut(src), Write(f1), run_time=2)
            self.play(GrowFromCenter(b1), FadeIn(t1))
            self.play(GrowFromCenter(b2), FadeIn(t2))
            self.fill(tr, 4)

    def marginal(self):
        bins = self.bins()
        self.add(bins)
        other = SurroundingRectangle(VGroup(bins[1], bins[2]), color=GREY_, buff=0.15)
        ol = T("not Basic: p = 0.50", 28, GREY_).next_to(other, UP, buff=0.15)
        eq = MathTex(r"Y_1\sim\text{Bin}(n,p_1)", font_size=44, color=BLUE_).move_to(UP * 2.7)
        eq2 = MathTex(r"E(Y_i)=np_i,\qquad V(Y_i)=np_i(1-p_i)", font_size=42).next_to(eq, DOWN, buff=0.3)
        with self.say("Now a shortcut. If you only care about Basic, merge the other two bins into one: "
                      "not Basic. Every subscriber is now a success or a failure, so Y one on its own is "
                      "just binomial. Its mean is n p one and its variance n p one q one. The same holds "
                      "for every cell.") as tr:
            self.play(bins[1][1].animate.set_opacity(0.3), bins[2][1].animate.set_opacity(0.3), Create(other), FadeIn(ol))
            self.play(Write(eq))
            self.play(Write(eq2))
            self.fill(tr, 3)
        tab = MathTex(r"E:\ 100,\ 70,\ 30\qquad V:\ 50,\ 45.5,\ 25.5", font_size=38, color=YELLOW_).next_to(eq2, DOWN, buff=0.3)
        with self.say("With two hundred subscribers, we expect one hundred on Basic, seventy on Standard, "
                      "thirty on Premium.") as tr:
            self.play(FadeIn(tab))
            self.fill(tr, 1)

    def covariance(self):
        rng = np.random.default_rng(28)
        Y = rng.multinomial(N, P, size=250)
        ax = Axes(x_range=[75, 125, 10], y_range=[10, 50, 10], x_length=6.5, y_length=5, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(LEFT * 2.6 + DOWN * 0.3)
        xl = T("Basic, Y₁", 24, BLUE_).next_to(ax, DOWN, buff=0.2)
        yl = T("Premium, Y₃", 24, PURPLE_).rotate(PI / 2).next_to(ax, LEFT, buff=0.25)
        dots = VGroup(*[Dot(ax.c2p(a + rng.uniform(-0.3, 0.3), c + rng.uniform(-0.3, 0.3)), radius=0.04, color=YELLOW_, fill_opacity=0.7) for a, _, c in Y])
        with self.say("Now simulate two hundred and fifty months, and plot the Basic count against the "
                      "Premium count. The cloud tilts downward. That is not a coincidence.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.01), run_time=2.5)
            self.fill(tr, 3.5)
        slope = -P[2] / (1 - P[0])
        line = ax.plot(lambda x: 30 + slope * (x - 100), x_range=[76, 124], color=RED_, stroke_width=4)
        c1 = MathTex(r"\text{Cov}(Y_s,Y_t)=-np_sp_t", font_size=40, color=RED_).move_to(RIGHT * 3.6 + UP * 1.6)
        c2 = MathTex(r"\text{Cov}(Y_1,Y_3)=-200(0.5)(0.15)=-15", font_size=32).next_to(c1, DOWN, buff=0.4)
        c3 = T("the total is fixed at n", 28, YELLOW_).next_to(c2, DOWN, buff=0.5)
        with self.say("The bins share a fixed total. A subscriber who picks Premium is one who did not "
                      "pick Basic. So when one count is high, the others tend to be low, and every pair of "
                      "cells has negative covariance: minus n p s p t. For Basic and Premium, minus "
                      "fifteen.") as tr:
            self.play(Create(line))
            self.play(Write(c1))
            self.play(FadeIn(c2), FadeIn(c3))
            self.fill(tr, 3)

    def revenue(self):
        r = MathTex(r"R=10Y_1+20Y_2+35Y_3", r"\qquad E(R)=3450\ \text{AZN}", font_size=42).to_edge(UP, buff=0.6)
        with self.say("Back to revenue. R is ten Y one plus twenty Y two plus thirty-five Y three. Its "
                      "mean needs only the cell means: three thousand four hundred and fifty manat.") as tr:
            self.play(Write(r), run_time=2)
            self.fill(tr, 2)
        u = 0.03
        base = LEFT * 4.2
        b1 = Rectangle(width=233.3 * u, height=0.8, fill_color=GREY_, fill_opacity=0.8, stroke_width=0).move_to(base + UP * 0.6, aligned_edge=LEFT)
        b2 = Rectangle(width=123.4 * u, height=0.8, fill_color=TEAL_, fill_opacity=0.9, stroke_width=0).move_to(base + DOWN * 1.2, aligned_edge=LEFT)
        l1 = T("ignoring covariances", 30, GREY_).next_to(b1, UP, buff=0.15).align_to(b1, LEFT)
        l2 = T("with covariances", 30, TEAL_).next_to(b2, UP, buff=0.15).align_to(b2, LEFT)
        v1 = T("SD 233 AZN", 34, GREY_).next_to(b1, RIGHT, buff=0.3)
        v2 = T("SD 123 AZN", 34, TEAL_).next_to(b2, RIGHT, buff=0.3)
        with self.say("The spread is different. Treat the three counts as unrelated, and the standard "
                      "deviation comes out at about two hundred and thirty-three manat. Include the "
                      "negative covariances, and it drops to about one hundred and twenty-three. The "
                      "counts move against each other, so the revenue swings much less than you'd think.") as tr:
            self.play(GrowFromEdge(b1, LEFT), FadeIn(l1), FadeIn(v1), run_time=1.5)
            self.play(GrowFromEdge(b2, LEFT), FadeIn(l2), FadeIn(v2), run_time=1.5)
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("n trials, k cells", 38, YELLOW_), T("counts always add up to n", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("each count alone", 38, BLUE_), T("binomial: mean npᵢ, variance npᵢqᵢ", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("any two counts", 38, RED_), T("covariance −npₛpₜ, always negative", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: a multinomial experiment drops n independent trials into k cells, and the "
                      "counts add up to n. Each count on its own is binomial. And because the total is "
                      "fixed, any two counts have negative covariance, which you must keep when you add "
                      "them up.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
