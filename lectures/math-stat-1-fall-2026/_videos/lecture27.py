"""Lecture 27 intuition video: variance of a linear combination as a grid of blocks; diversification and its floor."""
from common import *

W1, W2 = 0.6, 0.4          # pension fund weights: energy, telecom
S1, S2 = 25.0, 15.0        # standard deviations (%)
A, B = W1 * S1, W2 * S2    # 15 and 6
U = 5.2 / (A + B)          # screen units per % of the square's side


def sd_p(w, rho):
    return np.sqrt(w * w * S1 * S1 + (1 - w) ** 2 * S2 * S2 + 2 * w * (1 - w) * rho * S1 * S2)


class Lecture27(IntuitionScene):
    parts = ("hook", "blocks", "curve", "floor", "closing")

    def hook(self):
        q = T("A pension fund: 60% energy, 40% telecom", 38)
        q1 = T("energy σ = 25%,  telecom σ = 15%", 32, GREY_).next_to(q, DOWN, buff=0.4)
        q2 = T("Is the fund's risk 0.6 × 25 + 0.4 × 15 = 21%?", 36, YELLOW_).next_to(q1, DOWN, buff=0.5)
        with self.say("A pension fund puts sixty percent in energy shares and forty percent in telecom. "
                      "Energy returns have a standard deviation of twenty-five percent, telecom fifteen. "
                      "The expected return is just the weighted average. Is the risk the weighted average "
                      "too, twenty-one percent?") as tr:
            self.play(FadeIn(q))
            self.play(FadeIn(q1))
            self.play(Write(q2))
            self.fill(tr, 3)
        self.play(FadeOut(q), FadeOut(q1), FadeOut(q2))
        self.title_card("Linear functions of random variables", 27,
                        "Only if the two move in perfect lockstep. The reason is easiest to see as a picture "
                        "made of blocks.")

    def blocks(self):
        o = LEFT * 5.6 + UP * 2.4                    # top-left corner of the square
        a, b = A * U, B * U

        def rect(w, h, x, y, **kw):
            return Rectangle(width=w, height=h, **kw).move_to(o + RIGHT * (x + w / 2) + DOWN * (y + h / 2))

        e = rect(a, a, 0, 0, fill_color=BLUE_, fill_opacity=0.55, stroke_color=BLUE_)
        t = rect(b, b, a, a, fill_color=TEAL_, fill_opacity=0.55, stroke_color=TEAL_)
        le = MathTex(r"(0.6\cdot25)^2=225", font_size=30).move_to(e)
        lt = MathTex("36", font_size=30).move_to(t)
        top = VGroup(MathTex(r"0.6\sigma_1=15", font_size=26, color=BLUE_).next_to(e, UP, buff=0.12),
                     MathTex(r"6", font_size=26, color=TEAL_).next_to(t, UP, buff=0.12).set_x(t.get_x()).set_y(e.get_top()[1] + 0.25))
        with self.say("Draw each asset's contribution to risk as a length: zero point six times twenty-five "
                      "is fifteen for energy, zero point four times fifteen is six for telecom. Variance is "
                      "measured in squared units, so each one contributes a square: two twenty-five and "
                      "thirty-six.") as tr:
            self.play(FadeIn(e), FadeIn(le), FadeIn(top[0]))
            self.play(FadeIn(t), FadeIn(lt), FadeIn(top[1]))
            self.fill(tr, 2)
        o1 = rect(b, a, a, 0, stroke_color=GREY_, fill_opacity=0)
        o2 = rect(a, b, 0, a, stroke_color=GREY_, fill_opacity=0)
        rho = ValueTracker(1.0)

        def part(r0, horizontal):
            r = rho.get_value()
            col = GREEN_ if r >= 0 else RED_
            f = max(abs(r), 0.002)
            if horizontal:
                p = Rectangle(width=r0.width, height=r0.height * f)
            else:
                p = Rectangle(width=r0.width * f, height=r0.height)
            return p.set_fill(col, 0.55).set_stroke(width=0).align_to(r0, UL)

        f1 = always_redraw(lambda: part(o1, False))
        f2 = always_redraw(lambda: part(o2, True))
        lo = VGroup(MathTex(r"15\cdot6\cdot\rho", font_size=26).move_to(o1), MathTex(r"15\cdot6\cdot\rho", font_size=26).move_to(o2))
        lo[0].rotate(PI / 2)
        read = always_redraw(lambda: VGroup(
            MathTex(rf"\rho={rho.get_value():+.2f}", font_size=40, color=YELLOW_),
            MathTex(rf"V(R_p)=225+36+2(90)\rho={225 + 36 + 180 * rho.get_value():.0f}", font_size=32),
            MathTex(rf"\sigma_{{R_p}}={np.sqrt(max(261 + 180 * rho.get_value(), 0)):.2f}\%", font_size=40, color=YELLOW_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 3.4 + UP * 0.6))
        with self.say("But the square has two more blocks, the cross terms, one for each ordering of the "
                      "pair. Their size is fifteen times six times the correlation. When rho is one, they "
                      "fill completely, the whole square has side twenty-one, and the risk really is "
                      "twenty-one percent.") as tr:
            self.play(Create(o1), Create(o2))
            self.add(f1, f2)
            self.play(FadeIn(lo), FadeIn(read))
            self.fill(tr, 3)
        with self.say("At the real correlation, zero point three, the cross blocks shrink to thirty percent "
                      "of their size. The variance is three fifteen, and the risk is seventeen point seven "
                      "five percent: same expected return, over three points less risk. That gap is "
                      "diversification.") as tr:
            self.play(rho.animate.set_value(0.3), run_time=3)
            self.fill(tr, 3)
        with self.say("Push rho negative and the cross blocks turn red and start subtracting. At minus one "
                      "the risk falls to fifteen minus six, just nine percent.") as tr:
            self.play(rho.animate.set_value(-1), run_time=3)
            self.fill(tr, 3)
        rule = MathTex(r"V(a_1Y_1+a_2Y_2)=a_1^2V(Y_1)+a_2^2V(Y_2)+2a_1a_2\,\text{Cov}(Y_1,Y_2)",
                       font_size=32, color=WHITE_).to_edge(DOWN, buff=0.4)
        with self.say("That's the whole theorem for two variables: two squares, and two cross blocks each "
                      "carrying a covariance.") as tr:
            self.play(rho.animate.set_value(0.3), run_time=1.5)
            self.play(Write(rule), run_time=2)
            self.fill(tr, 3.5)

    def curve(self):
        ax = Axes(x_range=[0, 1, 0.2], y_range=[0, 26, 5], x_length=9, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(DOWN * 0.5 + RIGHT * 0.3)
        xl = T("weight in energy, w", 24, GREY_).next_to(ax, DOWN, buff=0.2)
        yl = T("fund s.d. (%)", 24, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        rho = ValueTracker(1.0)
        c = always_redraw(lambda: ax.plot(lambda w: sd_p(w, rho.get_value()), x_range=[0, 1, 0.005], color=YELLOW_, stroke_width=4))
        lab = always_redraw(lambda: MathTex(rf"\rho={rho.get_value():+.2f}", font_size=40, color=YELLOW_).to_corner(UR, buff=0.6))
        with self.say("Now let the weight vary from all telecom to all energy. With rho equal to one, risk "
                      "is a straight line between fifteen and twenty-five. Lower the correlation and the "
                      "line sags: every mix in the middle is safer than the straight line says.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.add(c, lab)
            self.play(rho.animate.set_value(0.3), run_time=3)
            self.play(rho.animate.set_value(-1), run_time=3)
            self.fill(tr, 7)
        m = Dot(ax.c2p(0.375, 0), color=RED_)
        ml = MathTex(r"w^*=\tfrac{15}{40}", font_size=32, color=RED_).move_to(ax.c2p(0.375, 8.5))
        mline = DashedLine(ml.get_bottom() + DOWN * 0.1, m.get_center(), color=RED_, stroke_width=2)
        with self.say("At minus one, the curve touches zero: a mix with three eighths in energy has no risk "
                      "at all. Real assets are never perfectly opposed, but that is exactly the logic of a "
                      "hedge.") as tr:
            self.play(FadeIn(m), Write(ml), Create(mline))
            self.play(rho.animate.set_value(0.3), run_time=2)
            self.fill(tr, 3)

    def floor(self):
        ax = Axes(x_range=[0, 41, 5], y_range=[0, 32, 5], x_length=10, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(DOWN * 0.5)
        xl = T("number of shares held, n", 24, GREY_).next_to(ax, DOWN, buff=0.2)
        yl = T("s.d. of an equal-weight portfolio (%)", 24, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        f = MathTex(r"V=\frac{\sigma^2}{n}+\Big(1-\frac1n\Big)\rho\,\sigma^2", font_size=36).to_corner(UR, buff=0.5).shift(DOWN * 0.3)
        c0 = ax.plot(lambda n: 30 / np.sqrt(n), x_range=[1, 40], color=TEAL_, stroke_width=4)
        c1 = ax.plot(lambda n: np.sqrt(900 / n + (1 - 1 / n) * 0.25 * 900), x_range=[1, 40], color=RED_, stroke_width=4)
        fl = DashedLine(ax.c2p(0, 15), ax.c2p(40, 15), color=GREY_)
        l0 = MathTex(r"\rho=0", font_size=32, color=TEAL_).next_to(ax.c2p(40, 30 / np.sqrt(40)), UP, buff=0.2)
        l1 = MathTex(r"\rho=0.25", font_size=32, color=RED_).next_to(ax.c2p(40, 15.5), UP, buff=0.35).shift(LEFT * 0.3)
        with self.say("With many assets, the grid gets bigger: n squares on the diagonal, and n times n "
                      "minus one cross blocks. Hold n shares equally, each with thirty percent volatility. "
                      "If they were uncorrelated, only the diagonal survives and risk shrinks towards "
                      "zero.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), Write(f))
            self.play(Create(c0), FadeIn(l0), run_time=2)
            self.fill(tr, 4)
        with self.say("But real shares share a market. With a correlation of a quarter, the cross blocks "
                      "outnumber the squares, and risk levels off at fifteen percent, however many shares you "
                      "add. Diversification removes the risk that is specific to each company, not the risk "
                      "they all share.") as tr:
            self.play(Create(c1), FadeIn(l1), run_time=2)
            self.play(Create(fl))
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("means", 38, YELLOW_), T("weights carry straight through", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("variances", 38, BLUE_), T("squares a²V, plus cross blocks 2ab·Cov", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("ρ < 1", 38, GREEN_), T("risk below the weighted average", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("many assets", 38, RED_), T("the shared covariance sets a floor", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("So: for a linear combination, the means carry the weights straight through. The "
                      "variance is a grid: squared weights times variances on the diagonal, and covariance "
                      "blocks everywhere else. Whenever the correlation is below one, the mix is less risky "
                      "than its parts suggest, down to a floor set by what the assets have in common.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5)
