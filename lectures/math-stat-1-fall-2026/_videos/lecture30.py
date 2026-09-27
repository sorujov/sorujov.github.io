"""Lecture 30 intuition video: Chapter 5 as one chain — joint, marginal, conditional, covariance, linear functions — on two loans and a portfolio."""
from common import *
from scipy.stats import norm


class Lecture30(IntuitionScene):
    parts = ("hook", "table", "loss", "portfolio", "closing")

    def hook(self):
        q = T("A bank lends to two construction firms in the same sector.", 36)
        q2 = T("If one defaults, should it worry about the other?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A bank in Baku lends to two construction firms, both in the same sector. If one "
                      "of them defaults, should the bank worry more about the other? And how does that "
                      "change the risk of its loan book? Answering this uses every idea of Chapter five, "
                      "one after another.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Chapter 5 as one chain", 30,
                        "So let's walk the chain once, from start to finish.")

    def table(self):
        vals = ((0.90, 0.04), (0.04, 0.02))
        w, h = 2.6, 1.3
        org = np.array([-3.2, 1.3, 0])
        cells = VGroup()
        nums = VGroup()
        for i in range(2):
            for j in range(2):
                c = org + np.array([j * w, -i * h, 0])
                cells.add(Rectangle(width=w, height=h, stroke_color=GREY_).move_to(c))
                nums.add(MathTex(f"{vals[i][j]:.2f}", font_size=48).move_to(c))
        ch = VGroup(MathTex("D_2=0", font_size=36), MathTex("D_2=1", font_size=36))
        for j in range(2):
            ch[j].move_to(org + np.array([j * w, h * 0.85, 0]))
        rh = VGroup(MathTex("D_1=0", font_size=36), MathTex("D_1=1", font_size=36))
        for i in range(2):
            rh[i].move_to(org + np.array([-w * 0.5 - 0.8, -i * h, 0]))
        lab = T("joint distribution", 30, YELLOW_).next_to(VGroup(cells, ch), UP, buff=0.3)
        with self.say("Step one, the joint distribution. D one and D two are one if the firm defaults "
                      "within the year. The table gives the probability of each pair: both survive with "
                      "probability point nine zero, both default with point zero two.") as tr:
            self.play(Create(cells), FadeIn(ch), FadeIn(rh), FadeIn(lab))
            self.play(Write(nums))
            self.fill(tr, 3)
        marg = MathTex(r"P(D_1=1)=0.04+0.02=0.06", font_size=36, color=TEAL_).move_to(RIGHT * 3.7 + UP * 2.2)
        hl = SurroundingRectangle(VGroup(cells[2], cells[3]), color=TEAL_, buff=0.05)
        with self.say("Step two, the marginals. Add along the row, and firm one defaults with "
                      "probability six percent. By symmetry, firm two does too.") as tr:
            self.play(Create(hl), Write(marg))
            self.fill(tr, 2)
        cond = MathTex(r"P(D_2=1\mid D_1=1)=\frac{0.02}{0.06}=\frac13", font_size=36, color=YELLOW_).next_to(marg, DOWN, buff=0.5)
        hl2 = SurroundingRectangle(cells[3], color=YELLOW_, buff=0.08)
        note = T("from 6% to 33%: dependent", 28, RED_).next_to(cond, DOWN, buff=0.4)
        with self.say("Step three, conditioning. Suppose firm one has defaulted: keep only that row, and "
                      "rescale it to add up to one. Now firm two defaults with probability one third. It "
                      "jumped from six percent to thirty-three. So the two are clearly not independent.") as tr:
            self.play(Create(hl2), Write(cond), run_time=2)
            self.play(FadeIn(note))
            self.fill(tr, 3)
        cov = MathTex(r"\text{Cov}=E(D_1D_2)-\mu_1\mu_2=0.02-0.06^2=0.0164", font_size=34).move_to(DOWN * 2.4 + RIGHT * 0.4)
        rho = MathTex(r"\rho\approx0.29", font_size=38, color=YELLOW_).next_to(cov, DOWN, buff=0.3)
        with self.say("Step four puts a number on it. The covariance is the expected product minus the "
                      "product of the means: point zero one six four, a correlation of about point two "
                      "nine.") as tr:
            self.play(Write(cov), run_time=2)
            self.play(FadeIn(rho))
            self.fill(tr, 3)

    def loss(self):
        L = MathTex(r"L=36{,}000\,D_1+54{,}000\,D_2", font_size=44).to_edge(UP, buff=0.6)
        e = MathTex(r"E(L)=90{,}000\times0.06=5{,}400\ \text{AZN}", font_size=38, color=TEAL_).next_to(L, DOWN, buff=0.4)
        with self.say("Step five, a linear function. With forty-five percent lost on default, the bank's "
                      "loss is thirty-six thousand D one plus fifty-four thousand D two. The expected loss "
                      "needs only the marginals: fifty-four hundred manat.") as tr:
            self.play(Write(L), run_time=2)
            self.play(FadeIn(e))
            self.fill(tr, 3)
        u = 0.00027
        base = LEFT * 3.6
        b1 = Rectangle(width=15413 * u, height=0.75, fill_color=GREY_, fill_opacity=0.8, stroke_width=0).move_to(base + DOWN * 0.3, aligned_edge=LEFT)
        b2 = Rectangle(width=17359 * u, height=0.75, fill_color=RED_, fill_opacity=0.9, stroke_width=0).move_to(base + DOWN * 2.1, aligned_edge=LEFT)
        l1 = T("if independent", 26, GREY_).next_to(b1, UP, buff=0.15).align_to(b1, LEFT)
        l2 = T("with the covariance", 26, RED_).next_to(b2, UP, buff=0.15).align_to(b2, LEFT)
        v1 = T("SD 15,413", 28, GREY_).next_to(b1, RIGHT, buff=0.3)
        v2 = T("SD 17,359", 28, RED_).next_to(b2, RIGHT, buff=0.3)
        with self.say("The spread does not. If the firms were independent, the standard deviation would "
                      "be about fifteen thousand four hundred. The positive covariance adds a term, and "
                      "pushes it to about seventeen thousand four hundred. Same-sector loans fail together, "
                      "and the variance of a sum prices that in.") as tr:
            self.play(GrowFromEdge(b1, LEFT), FadeIn(l1), FadeIn(v1), run_time=1.5)
            self.play(GrowFromEdge(b2, LEFT), FadeIn(l2), FadeIn(v2), run_time=1.5)
            self.fill(tr, 3)

    def portfolio(self):
        mp, sp = 1.04, np.sqrt(8.64)
        ax = Axes(x_range=[-14, 16, 4], y_range=[0, 0.15, 0.05], x_length=11, y_length=3.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"numbers_to_include": [-12, -8, -4, 0, 4, 8, 12]}).shift(DOWN * 1.2)
        xl = T("monthly return (%)", 22, GREY_).next_to(ax, DOWN, buff=0.15).align_to(ax, RIGHT)
        cA = DashedVMobject(ax.plot(lambda x: norm.pdf(x, 1.2, 5), x_range=[-14, 16], color=BLUE_), num_dashes=60)
        cP = ax.plot(lambda x: norm.pdf(x, mp, sp), x_range=[-14, 16], color=YELLOW_, stroke_width=4)
        lA = T("bank-share fund alone: σ = 5", 24, BLUE_).next_to(ax.c2p(7, 0.07), RIGHT, buff=0.1)
        lP = T("60/40 with bonds: σ = 2.94", 24, YELLOW_).next_to(ax.c2p(3.5, 0.13), RIGHT, buff=0.2)
        v = MathTex(r"V(R)=0.6^2(25)+0.4^2(2.25)+2(0.6)(0.4)(-0.2)(5)(1.5)=8.64", font_size=34).to_edge(UP, buff=0.4)
        with self.say("The same chain prices a portfolio. Sixty percent in a bank-share fund, forty in a "
                      "bond fund, with a slightly negative correlation. The variance of the mix uses the "
                      "same formula: squared weights times variances, plus the covariance term. It comes "
                      "out at eight point six four.") as tr:
            self.play(Write(v), run_time=2)
            self.play(Create(ax), FadeIn(xl), Create(cA), FadeIn(lA))
            self.play(Create(cP), FadeIn(lP))
            self.fill(tr, 5)
        tA = ax.get_area(ax.plot(lambda x: norm.pdf(x, 1.2, 5), x_range=[-14, -3]), x_range=[-14, -3], color=BLUE_, opacity=0.35)
        tP = ax.get_area(cP, x_range=[-14, -3], color=RED_, opacity=0.8)
        line = DashedLine(ax.c2p(-3, 0), ax.c2p(-3, 0.12), color=GREY_)
        p = MathTex(r"P(R<-3\%):\ 0.200\ \to\ 0.085", font_size=38, color=RED_).next_to(v, DOWN, buff=0.35)
        with self.say("Now assume normality, and bring in Chapter four. The chance of losing more than "
                      "three percent in a month: twenty percent for the bank fund alone, but only eight and "
                      "a half percent for the mix. Chapter five gave the variance; Chapter four turned it "
                      "into a probability.") as tr:
            self.play(Create(line), FadeIn(tA), FadeIn(tP))
            self.play(Write(p))
            self.fill(tr, 2)

    def closing(self):
        rows = (("joint", "the probability of every pair", YELLOW_),
                ("marginal", "add over the other variable", TEAL_),
                ("conditional", "keep one slice, rescale it", BLUE_),
                ("covariance", "how the two move together", RED_),
                ("linear functions", "means add; variances need the covariances", PURPLE_))
        g = VGroup(*[VGroup(T(a, 36, c), T(b, 28)).arrange(RIGHT, buff=0.5) for a, b, c in rows]
                   ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        with self.say("So Chapter five is one chain. The joint distribution holds everything. Marginals "
                      "add it up, conditionals slice it, covariance measures how the variables move "
                      "together, and for any sum, the means just add, while the variance needs every "
                      "covariance. That is exactly the toolkit that inference will build on.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 8)
