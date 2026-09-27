"""Lecture 24 intuition video: marginals as sums in the margins; conditionals as a renormalised slice."""
from common import *

INC = (600, 1200, 2400)            # Y1, monthly income (AZN)
SPE = (500, 900, 1500)             # Y2, monthly spending (AZN)
P = np.array([[0.20, 0.08, 0.02],
              [0.10, 0.25, 0.10],
              [0.02, 0.08, 0.15]])
S = 1.05                           # cell side


class Lecture24(IntuitionScene):
    parts = ("hook", "margins", "slice", "continuous", "closing")

    def hook(self):
        q = T("A bank surveys income and spending together.", 38)
        q1 = T("Card team: how much do customers spend?", 34, BLUE_).next_to(q, DOWN, buff=0.6)
        q2 = T("Credit team: how much do those earning 600 AZN spend?", 34, YELLOW_).next_to(q1, DOWN, buff=0.35)
        with self.say("A bank surveys its customers and records two numbers for each: monthly income and "
                      "monthly spending. The card team asks how much customers spend. The credit team asks "
                      "how much customers earning six hundred manat spend. Same data, two different "
                      "questions.") as tr:
            self.play(FadeIn(q))
            self.play(FadeIn(q1, shift=UP * 0.2))
            self.play(FadeIn(q2, shift=UP * 0.2))
            self.fill(tr, 3)
        self.play(FadeOut(q), FadeOut(q1), FadeOut(q2))
        self.title_card("Marginal and conditional distributions", 24,
                        "Both answers are already inside the joint table. One comes from adding it up, "
                        "the other from cutting a slice out of it.")

    def grid(self):
        cells = VGroup()
        for i in range(3):
            for j in range(3):
                sq = Square(S, stroke_color=GREY_, stroke_width=1.5, fill_color=BLUE_, fill_opacity=0.15 + 2.6 * P[i, j])
                sq.move_to(np.array([(j - 1) * S, (1 - i) * S, 0]))
                num = MathTex(f"{P[i, j]:.2f}", font_size=30).move_to(sq)
                cells.add(VGroup(sq, num))
        cells.move_to(LEFT * 2.2 + UP * 0.3)
        rl = VGroup(*[T(str(v), 26, GREY_).next_to(cells[3 * i], LEFT, buff=0.25) for i, v in enumerate(INC)])
        cl = VGroup(*[T(str(v), 26, GREY_).next_to(cells[j], UP, buff=0.2) for j, v in enumerate(SPE)])
        rt = T("income  Y₁", 26, GREY_).next_to(rl, LEFT, buff=0.3)
        ct = T("spending  Y₂", 26, GREY_).next_to(cl, UP, buff=0.2)
        return cells, VGroup(rl, cl, rt, ct)

    def margins(self):
        cells, labs = self.grid()
        with self.say("Here is the joint table. Each cell is the share of customers with that income and "
                      "that spending, and all nine cells add up to one.") as tr:
            self.play(FadeIn(labs))
            self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cells], lag_ratio=0.08), run_time=2)
            self.fill(tr, 3)
        col = P.sum(axis=0)
        bot = VGroup(*[MathTex(f"{col[j]:.2f}", font_size=32, color=TEAL_).next_to(cells[6 + j], DOWN, buff=0.35)
                       for j in range(3)])
        with self.say("The card team does not care about income. So squash each column down: add the three "
                      "cells, and write the total underneath. Thirty-two percent spend five hundred, forty-one "
                      "percent nine hundred, twenty-seven percent fifteen hundred.") as tr:
            for j in range(3):
                colg = VGroup(cells[j], cells[3 + j], cells[6 + j])
                self.play(Indicate(colg, color=TEAL_, scale_factor=1.04), run_time=0.8)
                self.play(TransformFromCopy(VGroup(*[c[1] for c in colg]), bot[j]), run_time=0.9)
            self.fill(tr, 5.1)
        row = P.sum(axis=1)
        side = VGroup(*[MathTex(f"{row[i]:.2f}", font_size=32, color=PURPLE_).next_to(cells[3 * i + 2], RIGHT, buff=0.35)
                        for i in range(3)])
        note = VGroup(T("column totals: spending alone", 28, TEAL_),
                      T("row totals: income alone", 28, PURPLE_),
                      T("they sit in the margins", 28, YELLOW_))
        for k, n in enumerate(note):
            n.move_to(RIGHT * 3.9 + UP * (0.9 - 0.7 * k))
        with self.say("Add across the rows instead, and you get the distribution of income alone. These "
                      "totals are written in the margins of the table, which is why they are called marginal "
                      "distributions. Summing out the other variable is all there is to it; for densities, the "
                      "sum becomes an integral.") as tr:
            self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in side], lag_ratio=0.3))
            for n in note:
                self.play(FadeIn(n))
            self.fill(tr, 4)
        self.play(FadeOut(note), FadeOut(bot), FadeOut(side))

    def slice(self):
        cells, labs = self.grid()
        self.add(cells, labs)
        box = SurroundingRectangle(VGroup(*cells[0:3]), color=YELLOW_, buff=0.06)
        with self.say("Now the credit team. They only care about customers earning six hundred. So throw away "
                      "every other row, and keep this one slice.") as tr:
            self.play(Create(box))
            self.play(*[c.animate.set_opacity(0.15) for c in cells[3:]], run_time=1)
            self.fill(tr, 2)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 0.8, 0.2], x_length=5, y_length=3.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0.2, 0.4, 0.6, 0.8]}).move_to(RIGHT * 3.9 + DOWN * 0.2)
        xl = VGroup(*[T(str(v), 22, GREY_).next_to(ax.c2p(k + 1, 0), DOWN, buff=0.15) for k, v in enumerate(SPE)])

        def bars(h, color, dx=0.0, w=0.5):
            return VGroup(*[Rectangle(width=w * ax.x_axis.get_unit_size(), height=max(h[k], 1e-3) * ax.y_axis.get_unit_size(),
                                      fill_color=color, fill_opacity=0.85, stroke_width=0).move_to(ax.c2p(k + 1 + dx, 0), aligned_edge=DOWN)
                            for k in range(3)])

        raw = bars(P[0], YELLOW_)
        s1 = MathTex(r"0.20+0.08+0.02=0.30", font_size=32, color=YELLOW_).next_to(ax, UP, buff=0.25)
        with self.say("On their own these three numbers add up to only thirty percent, so they are not yet a "
                      "distribution.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(TransformFromCopy(VGroup(*[c[0] for c in cells[0:3]]), raw), run_time=1.5)
            self.play(Write(s1))
            self.fill(tr, 3.5)
        cond = P[0] / P[0].sum()
        s2 = MathTex(r"p(y_2\mid 600)=\frac{p(600,y_2)}{0.30}", font_size=36, color=YELLOW_).move_to(s1)
        vals = VGroup(*[MathTex(f"{cond[k]:.2f}", font_size=26, color=YELLOW_) for k in range(3)])
        new = bars(cond, YELLOW_)
        for k in range(3):
            vals[k].next_to(new[k], UP, buff=0.1)
        with self.say("Divide each one by the row total, zero point three. The bars keep their shape but "
                      "stretch until they add to one. That is the conditional distribution: two thirds of "
                      "six-hundred earners spend five hundred, and fewer than one in fifteen spend fifteen "
                      "hundred.") as tr:
            self.play(Transform(s1, s2))
            self.play(Transform(raw, new), run_time=2)
            self.play(FadeIn(vals))
            self.fill(tr, 4)
        box2 = SurroundingRectangle(VGroup(*cells[6:9]), color=RED_, buff=0.06)
        rich = bars(P[2] / P[2].sum(), RED_, 0.16, 0.3)
        narrow = bars(cond, YELLOW_, -0.16, 0.3)
        with self.say("Cut the slice for the richest group instead, and the conditional distribution tips "
                      "the other way: sixty percent of them spend fifteen hundred. Conditioning is simply "
                      "choosing a slice and rescaling it.") as tr:
            self.play(FadeOut(vals), Transform(raw, narrow))
            self.play(ReplacementTransform(box, box2), cells[6:9].animate.set_opacity(1), cells[0:3].animate.set_opacity(0.15))
            self.play(GrowFromEdge(rich, DOWN), run_time=1.5)
            self.fill(tr, 3.5)

    def continuous(self):
        ax = Axes(x_range=[0, 4.5, 1], y_range=[0, 4.5, 1], x_length=4.6, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).move_to(LEFT * 3.4 + DOWN * 0.3)
        xl = MathTex("y_1", font_size=30, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex("y_2", font_size=30, color=GREY_).next_to(ax.y_axis, UP, buff=0.15)
        tri = Polygon(ax.c2p(0, 0), ax.c2p(4, 4), ax.c2p(0, 4), color=BLUE_, fill_opacity=0.35, stroke_width=2)
        head = T("Diesel: stock Y₂ at dawn, sales Y₁ ≤ Y₂", 30).to_edge(UP, buff=0.35)
        dens = MathTex(r"f(y_1,y_2)=\tfrac18", font_size=32, color=BLUE_).move_to(ax.c2p(1.2, 3.1))
        with self.say("The same two moves work for densities. A filling station starts the day with Y two "
                      "thousand litres of diesel and sells Y one, which can't exceed the stock. The joint "
                      "density is flat over this triangle.") as tr:
            self.play(FadeIn(head), Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(FadeIn(tri), Write(dens))
            self.fill(tr, 3)
        bx = Axes(x_range=[0, 4.5, 1], y_range=[0, 0.6, 0.25], x_length=4.6, y_length=3, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).move_to(RIGHT * 3.3 + DOWN * 0.9)
        bl = MathTex(r"f_2(y_2)=\frac{y_2}{8}", font_size=34, color=TEAL_).next_to(bx, UP, buff=0.3)
        bxl = MathTex("y_2", font_size=28, color=GREY_).next_to(bx.x_axis, RIGHT, buff=0.15)
        y = ValueTracker(0.2)
        seg = always_redraw(lambda: Line(ax.c2p(0, y.get_value()), ax.c2p(y.get_value(), y.get_value()), color=TEAL_, stroke_width=6))
        trace = always_redraw(lambda: bx.plot(lambda t: t / 8, x_range=[0, y.get_value()], color=TEAL_, stroke_width=4))
        dot = always_redraw(lambda: Dot(bx.c2p(y.get_value(), y.get_value() / 8), color=TEAL_))
        with self.say("For the marginal of the stock, fix Y two and integrate across: the horizontal slice "
                      "has length y two, so the marginal density is y two over eight. Higher stock levels "
                      "have longer slices, and so more probability.") as tr:
            self.play(Create(bx), FadeIn(bxl), FadeOut(dens))
            self.add(seg, trace, dot)
            self.play(y.animate.set_value(4), run_time=4, rate_func=linear)
            self.play(Write(bl))
            self.fill(tr, 6.5)
        self.remove(seg, trace, dot)
        fixed = Line(ax.c2p(0, 3), ax.c2p(3, 3), color=YELLOW_, stroke_width=7)
        self.add(bx.plot(lambda t: t / 8, x_range=[0, 4], color=TEAL_, stroke_width=4))
        cl = MathTex(r"f(y_1\mid 3)=\frac{1/8}{3/8}=\frac13,\quad 0\le y_1\le 3", font_size=32, color=YELLOW_).move_to(RIGHT * 3.3 + UP * 2.3)
        with self.say("And the conditional? Suppose we know the station opened with three thousand litres. "
                      "Take that slice, and rescale it so it has area one. It is flat, so sales are uniform "
                      "between zero and three: the joint density divided by the marginal.") as tr:
            self.play(FadeOut(bl), FadeOut(head))
            self.play(Create(fixed))
            self.play(Write(cl), run_time=2)
            self.fill(tr, 3.5)

    def closing(self):
        g = VGroup(
            VGroup(T("joint", 38, BLUE_), T("the whole table or surface", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("marginal", 38, TEAL_), T("sum or integrate the other variable out", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("conditional", 38, YELLOW_), T("take one slice, divide by its total", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: the joint distribution holds everything. A marginal adds the other variable out "
                      "and forgets it. A conditional keeps one slice and rescales it to total one. No new data "
                      "is needed for either.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
