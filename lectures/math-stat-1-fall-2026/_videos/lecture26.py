"""Lecture 26 intuition video: expectation as a probability-weighted average; covariance as signed rectangles."""
from common import *

Q = np.array([[0.30, 0.15, 0.05],       # retailer: Y1 fridges (rows), Y2 washing machines (cols)
              [0.10, 0.15, 0.10],
              [0.02, 0.05, 0.08]])
B1, B2 = np.array([-2, 1, 4]), np.array([-3, 1, 5])      # bank share returns (%)
PB = np.array([[0.15, 0.08, 0.02],
               [0.08, 0.30, 0.12],
               [0.02, 0.07, 0.16]])
M1, M2 = 1.0, 1.2
S = 1.05


class Lecture26(IntuitionScene):
    parts = ("hook", "weights", "rectangles", "zero", "closing")

    def hook(self):
        q = T("An appliance shop's peak hour:", 38)
        q1 = T("fridges at 1200 AZN, washing machines at 900 AZN", 32, GREY_).next_to(q, DOWN, buff=0.4)
        q2 = T("What revenue should it expect?", 38, YELLOW_).next_to(q1, DOWN, buff=0.5)
        with self.say("An appliance shop sells fridges at twelve hundred manat and washing machines at nine "
                      "hundred. In its peak hour it sells zero, one or two of each, and the two numbers are "
                      "related. What revenue should it expect, and do the two sales move together?") as tr:
            self.play(FadeIn(q))
            self.play(FadeIn(q1))
            self.play(Write(q2))
            self.fill(tr, 3)
        self.play(FadeOut(q), FadeOut(q1), FadeOut(q2))
        self.title_card("Expectation and covariance", 26,
                        "Both answers are averages over the joint distribution, one of a revenue, the other "
                        "of a product of deviations.")

    def weights(self):
        cells = VGroup()
        for i in range(3):
            for j in range(3):
                sq = Square(S, stroke_color=GREY_, stroke_width=1.5, fill_color=BLUE_, fill_opacity=0.12 + 2.2 * Q[i, j])
                sq.move_to(np.array([(j - 1) * S, (1 - i) * S, 0]))
                g = MathTex(str(1200 * i + 900 * j), font_size=28, color=YELLOW_).move_to(sq).shift(UP * 0.17)
                p = MathTex(f"{Q[i, j]:.2f}", font_size=24).move_to(sq).shift(DOWN * 0.22)
                cells.add(VGroup(sq, g, p))
        cells.move_to(LEFT * 3.2 + DOWN * 0.2)
        rl = VGroup(*[MathTex(str(i), font_size=28, color=GREY_).next_to(cells[3 * i], LEFT, buff=0.2) for i in range(3)])
        cl = VGroup(*[MathTex(str(j), font_size=28, color=GREY_).next_to(cells[j], UP, buff=0.15) for j in range(3)])
        rt = T("fridges Y₁", 24, GREY_).next_to(rl, LEFT, buff=0.2)
        ct = T("washers Y₂", 24, GREY_).next_to(cl, UP, buff=0.15)
        key = VGroup(T("yellow: revenue in AZN", 24, YELLOW_), T("white: probability", 24)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        key.next_to(cells, DOWN, buff=0.35)
        with self.say("Here is the joint table. Each cell now carries two numbers: its probability, and the "
                      "revenue it would produce, twelve hundred times fridges plus nine hundred times "
                      "washers.") as tr:
            self.play(FadeIn(rl), FadeIn(cl), FadeIn(rt), FadeIn(ct))
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cells], lag_ratio=0.08), run_time=2)
            self.play(FadeIn(key))
            self.fill(tr, 4)
        e1 = MathTex(r"E[g(Y_1,Y_2)]=\sum\sum g(y_1,y_2)\,p(y_1,y_2)", font_size=32).move_to(RIGHT * 3.3 + UP * 2.0)
        e2 = MathTex(r"=0(.30)+900(.15)+\cdots+4200(.08)", font_size=30).next_to(e1, DOWN, buff=0.35)
        e3 = MathTex(r"=1509\ \text{AZN}", font_size=40, color=YELLOW_).next_to(e2, DOWN, buff=0.35)
        with self.say("The expected revenue is what you'd get by weighting each cell's revenue by its "
                      "probability and adding up. Nine cells, and the answer is fifteen hundred and nine "
                      "manat.") as tr:
            self.play(Write(e1), run_time=1.5)
            self.play(LaggedStart(*[Indicate(c[1], color=WHITE_) for c in cells], lag_ratio=0.1), FadeIn(e2), run_time=2)
            self.play(Write(e3))
            self.fill(tr, 4.5)
        s1 = MathTex(r"E(R)=1200\,E(Y_1)+900\,E(Y_2)", font_size=34, color=TEAL_).move_to(RIGHT * 3.3 + DOWN * 1.2)
        s2 = MathTex(r"=1200(0.65)+900(0.81)=1509", font_size=32, color=TEAL_).next_to(s1, DOWN, buff=0.3)
        with self.say("But there's a shortcut. The expectation of a sum is the sum of the expectations, "
                      "always, whether or not the variables are related. Twelve hundred times the expected "
                      "fridges, plus nine hundred times the expected washers: the same fifteen hundred and "
                      "nine, from the two margins alone.") as tr:
            self.play(Write(s1), run_time=1.5)
            self.play(Write(s2), run_time=1.5)
            self.fill(tr, 3)

    def bank_axes(self):
        return Axes(x_range=[-3, 5, 1], y_range=[-4, 6, 2], x_length=6.2, y_length=5.6, tips=False,
                    axis_config={"color": GREY_, "font_size": 20, "include_numbers": True}).move_to(LEFT * 2.8 + DOWN * 0.3)

    def rects(self, ax, ys1, ys2, P, m1, m2):
        g = VGroup()
        for i, a in enumerate(ys1):
            for j, b in enumerate(ys2):
                if abs(a - m1) < 1e-9 or abs(b - m2) < 1e-9 or P[i, j] == 0:
                    continue
                col = GREEN_ if (a - m1) * (b - m2) > 0 else RED_
                p0, p1 = ax.c2p(m1, m2), ax.c2p(a, b)
                r = Rectangle(width=abs(p1[0] - p0[0]), height=abs(p1[1] - p0[1]), stroke_color=col, stroke_width=2,
                              fill_color=col, fill_opacity=min(0.1 + 2.5 * P[i, j], 0.8))
                g.add(r.move_to((p0 + p1) / 2))
        return g

    def dots(self, ax, ys1, ys2, P, color=BLUE_):
        return VGroup(*[Dot(ax.c2p(a, b), radius=0.05 + 0.35 * np.sqrt(P[i, j]), color=color, fill_opacity=0.9)
                        for i, a in enumerate(ys1) for j, b in enumerate(ys2) if P[i, j] > 0])

    def rectangles(self):
        ax = self.bank_axes()
        xl = T("bank A return (%)", 22, GREY_).next_to(ax, DOWN, buff=0.1)
        yl = T("bank B return (%)", 22, GREY_).rotate(PI / 2).next_to(ax, LEFT, buff=0.1)
        d = self.dots(ax, B1, B2, PB)
        with self.say("Now, do two variables move together? Take monthly returns on two bank shares. Each "
                      "dot is one possible pair of returns, and its size is the probability.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(LaggedStart(*[GrowFromCenter(x) for x in d], lag_ratio=0.1), run_time=1.5)
            self.fill(tr, 3)
        h = DashedLine(ax.c2p(-3, M2), ax.c2p(5, M2), color=GREY_)
        v = DashedLine(ax.c2p(M1, -4), ax.c2p(M1, 6), color=GREY_)
        ml = MathTex(r"\text{means }(\mu_1,\mu_2)=(1.0,\,1.2)", font_size=26, color=GREY_).next_to(ax.c2p(M1, 6), UP, buff=0.15)
        r = self.rects(ax, B1, B2, PB, M1, M2)
        with self.say("Draw cross-hairs through the two means. From the centre to each dot, draw a rectangle. "
                      "When both returns are above their means, or both below, the rectangle is green and "
                      "counts as positive. When one is up and the other is down, it's red and counts as "
                      "negative.") as tr:
            self.play(Create(h), Create(v), FadeIn(ml))
            self.play(LaggedStart(*[FadeIn(x) for x in r], lag_ratio=0.2), run_time=2.5)
            self.bring_to_front(d)
            self.fill(tr, 4)
        c1 = MathTex(r"\text{Cov}(Y_1,Y_2)=E[(Y_1-\mu_1)(Y_2-\mu_2)]", font_size=30).move_to(RIGHT * 3.6 + UP * 2.3)
        c2 = MathTex(r"=E(Y_1Y_2)-\mu_1\mu_2", font_size=30).next_to(c1, DOWN, buff=0.25).align_to(c1, LEFT).shift(RIGHT * 1.3)
        c3 = MathTex(r"=4.44-1.0(1.2)=3.24", font_size=32, color=GREEN_).next_to(c2, DOWN, buff=0.25).align_to(c2, LEFT)
        with self.say("Covariance is the probability-weighted average of these signed areas. Here the big, "
                      "likely rectangles are green, so the covariance is positive: three point two four. "
                      "The two shares tend to rise and fall together.") as tr:
            self.play(Write(c1), run_time=1.5)
            self.play(Write(c2))
            self.play(Write(c3))
            self.fill(tr, 3.5)
        rho = MathTex(r"\rho=\frac{\text{Cov}}{\sigma_1\sigma_2}=\frac{3.24}{\sqrt{4.5}\sqrt{8.76}}=0.52", font_size=32, color=YELLOW_).move_to(RIGHT * 3.6 + DOWN * 0.6)
        rn = T("no units, always between −1 and 1", 24, YELLOW_).next_to(rho, DOWN, buff=0.3)
        with self.say("The size of a covariance depends on units: measure returns in basis points and it "
                      "grows ten thousand times. Dividing by the two standard deviations removes that, and "
                      "gives the correlation, about zero point five two.") as tr:
            self.play(Write(rho), run_time=1.5)
            self.play(FadeIn(rn))
            self.fill(tr, 2.5)

    def zero(self):
        ax = Axes(x_range=[-1.6, 1.6, 1], y_range=[-1.6, 1.6, 1], x_length=4.6, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).move_to(LEFT * 3.2 + DOWN * 0.3)
        v = np.array([-1, 0, 1])
        P = np.array([[1, 3, 1], [3, 0, 3], [1, 3, 1]]) / 16
        head = T("Brent and gas positions: short, flat or long, never flat in both", 28).to_edge(UP, buff=0.35)
        d = self.dots(ax, v, v, P, PURPLE_)
        hole = Circle(radius=0.2, color=RED_, stroke_width=3).move_to(ax.c2p(0, 0))
        r = self.rects(ax, v, v, P, 0, 0)
        with self.say("One warning. An energy desk holds short, flat or long positions in oil and gas, but "
                      "is never flat in both. The corner rectangles are equal and opposite, so they cancel, "
                      "and the covariance is exactly zero.") as tr:
            self.play(FadeIn(head), Create(ax))
            self.play(LaggedStart(*[GrowFromCenter(x) for x in d], lag_ratio=0.1), run_time=1.5)
            self.play(FadeIn(r))
            self.bring_to_front(d)
            self.fill(tr, 4)
        t1 = MathTex(r"\text{Cov}=0", font_size=40, color=GREEN_).move_to(RIGHT * 3 + UP * 1.2)
        t2 = MathTex(r"p(0,0)=0\ne\left(\tfrac{6}{16}\right)^2", font_size=36, color=RED_).next_to(t1, DOWN, buff=0.5)
        t3 = T("zero covariance, still dependent", 30, YELLOW_).next_to(t2, DOWN, buff=0.5)
        with self.say("Yet the positions are clearly dependent: learn that oil is flat, and you know gas is "
                      "not. Independence forces zero covariance, but zero covariance does not force "
                      "independence. Covariance only sees straight-line co-movement.") as tr:
            self.play(Create(hole), Write(t1))
            self.play(Write(t2))
            self.play(FadeIn(t3))
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("E[g(Y₁, Y₂)]", 36, YELLOW_), T("weight every cell by its probability", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("sums", 36, TEAL_), T("expectations always add, related or not", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("covariance", 36, GREEN_), T("average signed rectangle from the means", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("zero covariance", 36, RED_), T("does not mean independent", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("So: an expectation over two variables weights every cell by its probability. The "
                      "expectation of a sum splits, always. Covariance is the average signed rectangle "
                      "around the means, and correlation is its unit-free version. And zero covariance is "
                      "not the same as independence.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5)
