"""Lecture 29 intuition video: conditional expectation as a curve through the cloud; the bivariate normal; the tower rule and the variance split."""
from common import *
from scipy.stats import norm


class Lecture29(IntuitionScene):
    parts = ("hook", "slices", "bivariate", "variance_split", "closing")

    def hook(self):
        q = T("A household in Baku earns 1,500 AZN this month.", 38)
        q2 = T("How much do we expect it to spend?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A household in Baku earns fifteen hundred manat this month. How much do we expect "
                      "it to spend? The answer should depend on the income: a richer household spends "
                      "more. So what we want is not one number, but a whole function of income.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Conditional expectation", 29,
                        "That function is the conditional expectation, and it's the idea behind every "
                        "regression you will ever run.")

    def slices(self):
        ax = Axes(x_range=[0, 2, 0.5], y_range=[0, 2, 0.5], x_length=5.6, y_length=5.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(LEFT * 3 + DOWN * 0.2)
        xl = T("income Y₂ (thousand AZN)", 22, GREY_).next_to(ax, DOWN, buff=0.2)
        yl = T("spending Y₁", 22, GREY_).rotate(PI / 2).next_to(ax, LEFT, buff=0.25)
        rng = np.random.default_rng(29)
        pts = []
        while len(pts) < 400:
            a, b = rng.uniform(0, 2, 2)
            if a <= b:
                pts.append((b, a))
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.035, color=BLUE_, fill_opacity=0.8) for x, y in pts])
        d1 = MathTex(r"f(y_1,y_2)=\tfrac12,\quad 0\le y_1\le y_2\le 2", font_size=34).move_to(RIGHT * 3.4 + UP * 2.6)
        with self.say("Here is a simple model. Income and spending, in thousands of manat, are spread "
                      "evenly over a triangle: spending is never above income.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.005), Write(d1), run_time=2)
            self.fill(tr, 3)
        strip = Rectangle(width=0.1 * ax.x_axis.get_unit_size(), height=1.5 * ax.y_axis.get_unit_size(), stroke_color=YELLOW_,
                          fill_color=YELLOW_, fill_opacity=0.25).move_to(ax.c2p(1.45, 0), aligned_edge=DL)
        m = Dot(ax.c2p(1.5, 0.75), radius=0.1, color=RED_)
        d2 = MathTex(r"Y_1\mid Y_2=1.5\ \sim\ \text{uniform}(0,\,1.5)", font_size=34).next_to(d1, DOWN, buff=0.4)
        d3 = MathTex(r"E(Y_1\mid Y_2=1.5)=0.75", font_size=36, color=RED_).next_to(d2, DOWN, buff=0.3)
        with self.say("Fix the income at fifteen hundred and look only at that thin slice. Inside it, "
                      "spending is uniform between zero and one point five. So its average is the middle: "
                      "seven hundred and fifty manat.") as tr:
            self.play(dots.animate.set_opacity(0.35), FadeIn(strip))
            self.play(FadeIn(d2), GrowFromCenter(m), FadeIn(d3))
            self.fill(tr, 2)
        line = ax.plot(lambda x: x / 2, x_range=[0, 2], color=RED_, stroke_width=5)
        d4 = MathTex(r"E(Y_1\mid Y_2)=Y_2/2", font_size=38, color=RED_).next_to(d3, DOWN, buff=0.5)
        with self.say("Do this for every income and the slice averages trace a line: spending is half of "
                      "income. Now notice: since income is random, this line evaluated at income is itself "
                      "a random variable.") as tr:
            self.play(FadeOut(strip), FadeOut(m), Create(line), run_time=2)
            self.play(Write(d4))
            self.fill(tr, 3)
        d5 = MathTex(r"E(Y_1)=E\big[E(Y_1\mid Y_2)\big]=E(Y_2/2)=\tfrac23", font_size=34, color=YELLOW_).next_to(d4, DOWN, buff=0.5)
        with self.say("And its average is the average spending. Average the slice averages, weighting "
                      "each slice by how likely that income is, and you get about six hundred and sixty-"
                      "seven manat. That's Theorem five point fourteen: the mean of the conditional mean is "
                      "the mean.") as tr:
            self.play(Write(d5), run_time=2)
            self.fill(tr, 2)

    def bivariate(self):
        m1, s1, m2, s2 = 0.8, 4.5, 0.6, 3.8
        ax = Axes(x_range=[-12, 12, 4], y_range=[-14, 14, 7], x_length=6, y_length=5.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 20}).shift(LEFT * 3.1 + DOWN * 0.2)
        xl = T("emerging-markets index Y₂ (%)", 22, GREY_).next_to(ax, DOWN, buff=0.2)
        yl = T("regional index Y₁ (%)", 22, GREY_).rotate(PI / 2).next_to(ax, LEFT, buff=0.25)
        rng = np.random.default_rng(5)
        z = rng.standard_normal((250, 2))
        z = z[np.abs(z[:, 0]) < 2.8][:220]
        rho = ValueTracker(0)

        def cloud():
            r = rho.get_value()
            g = VGroup()
            for a, b in z:
                y1 = m1 + s1 * (r * a + np.sqrt(1 - r * r) * b)
                if abs(y1) < 13.5:
                    g.add(Dot(ax.c2p(m2 + s2 * a, y1), radius=0.035, color=BLUE_, fill_opacity=0.8))
            return g
        dots = always_redraw(cloud)
        line = always_redraw(lambda: ax.plot(lambda x: m1 + rho.get_value() * s1 / s2 * (x - m2), x_range=[-11, 11], color=RED_, stroke_width=4))
        rl = always_redraw(lambda: MathTex(rf"\rho={rho.get_value():.2f}", font_size=40, color=YELLOW_).move_to(RIGHT * 3.6 + UP * 2.8))
        f1 = MathTex(r"E(Y_1\mid y_2)=\mu_1+\rho\frac{\sigma_1}{\sigma_2}(y_2-\mu_2)", font_size=34, color=RED_).move_to(RIGHT * 3.6 + UP * 1.4)
        f2 = MathTex(r"V(Y_1\mid y_2)=\sigma_1^2(1-\rho^2)", font_size=34).next_to(f1, DOWN, buff=0.4)
        with self.say("For the bivariate normal, the slice averages always lie on a straight line. Two "
                      "stock indices with correlation zero: the cloud is round and the line is flat. "
                      "Raise the correlation, and the cloud tilts onto the line.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.add(dots, line, rl)
            self.play(FadeIn(f1))
            self.play(rho.animate.set_value(0.9), run_time=4)
            self.fill(tr, 5.5)
        f3 = T("spread about the line: 4.5% → 1.96%", 26, TEAL_).next_to(f2, DOWN, buff=0.5)
        with self.say("The slope of the line is rho times sigma one over sigma two. And the spread around "
                      "it, the conditional variance, is sigma one squared times one minus rho squared. The "
                      "more correlated the two, the better one predicts the other.") as tr:
            self.play(FadeIn(f2))
            self.play(FadeIn(f3))
            self.fill(tr, 2)

    def variance_split(self):
        ax = Axes(x_range=[-20, 16, 4], y_range=[0, 0.12, 0.04], x_length=11, y_length=3.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"numbers_to_include": [-16, -8, 0, 8]}).shift(UP * 1.6)
        xl = T("monthly return (%)", 22, GREY_).next_to(ax, DOWN, buff=0.15).align_to(ax, RIGHT)
        c1 = ax.plot(lambda x: 0.8 * norm.pdf(x, 1.2, 3), x_range=[-20, 16], color=BLUE_)
        c2 = ax.plot(lambda x: 0.2 * norm.pdf(x, -2.5, 7), x_range=[-20, 16], color=RED_)
        l1 = T("calm, 80%: mean 1.2, SD 3", 24, BLUE_).next_to(ax.c2p(4.5, 0.1), RIGHT, buff=0.2)
        l2 = T("stress, 20%: mean −2.5, SD 7", 24, RED_).next_to(ax.c2p(-13, 0.025), UP, buff=0.2)
        with self.say("Conditioning also splits risk. A pension fund's monthly return depends on the "
                      "regime. Eighty percent of months are calm: mean one point two percent, standard "
                      "deviation three. Twenty percent are oil-price stress: mean minus two point five, "
                      "standard deviation seven.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(Create(c1), FadeIn(l1))
            self.play(Create(c2), FadeIn(l2))
            self.fill(tr, 3)
        eq = MathTex(r"V(R)=", r"E[V(R\mid M)]", r"+", r"V[E(R\mid M)]", font_size=40).move_to(DOWN * 1.35)
        eq[1].set_color(TEAL_)
        eq[3].set_color(YELLOW_)
        u = 0.55
        w1 = Rectangle(width=17.0 * u / 1.4, height=0.6, fill_color=TEAL_, fill_opacity=0.9, stroke_width=0)
        w2 = Rectangle(width=2.19 * u / 1.4, height=0.6, fill_color=YELLOW_, fill_opacity=0.9, stroke_width=0)
        bar = VGroup(w1, w2).arrange(RIGHT, buff=0).move_to(DOWN * 2.75 + LEFT * 1.5)
        t1 = T("within: 17.00", 24, TEAL_).next_to(w1, DOWN, buff=0.15)
        t2 = T("between: 2.19", 24, YELLOW_).next_to(w2, UP, buff=0.15)
        t3 = T("= 19.19, SD 4.38%", 28).next_to(bar, RIGHT, buff=0.4)
        with self.say("Theorem five point fifteen splits the total variance in two. The within part is "
                      "the average spread inside each regime: seventeen. The between part is how much the "
                      "regime means themselves jump around: about two point two. Together, a standard "
                      "deviation of four point four percent, well above the calm three percent. Not knowing "
                      "the regime is a risk of its own.") as tr:
            self.play(Write(eq), run_time=2)
            self.play(GrowFromEdge(w1, LEFT), FadeIn(t1))
            self.play(GrowFromEdge(w2, LEFT), FadeIn(t2))
            self.play(FadeIn(t3))
            self.fill(tr, 5)

    def closing(self):
        g = VGroup(
            VGroup(MathTex(r"E(Y_1\mid Y_2)", font_size=44, color=RED_), T("the average inside each slice: a regression line", 28)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"E[E(Y_1\mid Y_2)]=E(Y_1)", font_size=44, color=YELLOW_), T("average the averages", 28)).arrange(RIGHT, buff=0.5),
            VGroup(T("variance", 38, TEAL_), T("= within the slices + between their means", 28)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: the conditional expectation is the average inside each slice, and it traces "
                      "a regression line through the cloud. Averaging those averages gives back the "
                      "ordinary mean. And total variance is the spread within the slices plus the spread "
                      "between their means.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
