"""Lecture 23 intuition video: joint distributions — same marginals, different joints; a joint table; a joint density as a cloud of points."""
from common import *


def grid(vals, rows, cols, cell=1.1, fs=28, color=BLUE_, scale_area=True, pmax=None):
    """A probability table: one square per cell, its area proportional to the probability."""
    pmax = pmax or max(max(r) for r in vals)
    g = VGroup()
    cells = {}
    for i, r in enumerate(vals):
        for j, p in enumerate(r):
            frame = Square(cell, stroke_color=DIM, stroke_width=2).move_to(RIGHT * j * cell + DOWN * i * cell)
            side = cell * 0.9 * np.sqrt(p / pmax) if scale_area else cell * 0.9
            box = Square(max(side, 0.02), stroke_width=0, fill_color=color, fill_opacity=0.4 if p > 0 else 0).move_to(frame)
            num = T(f"{p:g}", fs).move_to(frame)
            cells[(i, j)] = VGroup(frame, box, num)
            g.add(cells[(i, j)])
    rl = VGroup(*[MathTex(s, font_size=fs + 4, color=GREY_).next_to(cells[(i, 0)], LEFT, buff=0.2) for i, s in enumerate(rows)])
    cl = VGroup(*[MathTex(s, font_size=fs + 4, color=GREY_).next_to(cells[(0, j)], UP, buff=0.2) for j, s in enumerate(cols)])
    whole = VGroup(g, rl, cl)
    whole.cells = cells
    return whole


class Lecture23(IntuitionScene):
    parts = ("hook", "table", "density", "closing")

    def hook(self):
        q = T("Two construction borrowers, each defaults with probability 0.07", 32).to_edge(UP, buff=0.5)
        q2 = T("P(both default) = ?", 38, YELLOW_).next_to(q, DOWN, buff=0.35)
        rows, cols = (r"A\ \text{def.}", r"A\ \text{pays}"), (r"B\ \text{def.}", r"B\ \text{pays}")
        ind = grid([[0.0049, 0.0651], [0.0651, 0.8649]], rows, cols, cell=1.45, fs=26, pmax=0.93)
        tog = grid([[0.07, 0], [0, 0.93]], rows, cols, cell=1.45, fs=26, color=RED_, pmax=0.93)
        ind.move_to(LEFT * 2.8 + DOWN * 0.9)
        tog.move_to(RIGHT * 3.8 + DOWN * 0.9)
        il = T("unrelated", 30, BLUE_).next_to(ind, DOWN, buff=0.3)
        tl = T("always together", 30, RED_).next_to(tog, DOWN, buff=0.3)
        with self.say("Two small construction firms borrow from the same bank. Each defaults within the "
                      "year with probability seven percent. What's the chance that both default? If the two "
                      "are unrelated, it's seven percent of seven percent: about half of one percent. If "
                      "they always move together, it's the full seven percent.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.play(FadeIn(ind), FadeIn(il))
            self.play(Indicate(ind.cells[(0, 0)][2], color=YELLOW_))
            self.play(FadeIn(tog), FadeIn(tl))
            self.play(Indicate(tog.cells[(0, 0)][2], color=YELLOW_))
            self.fill(tr, 6)
        with self.say("A fourteen-fold difference. Yet each firm, looked at alone, has exactly the same "
                      "seven percent in both tables. The answer isn't in the single-variable distributions. "
                      "It's in the joint one.") as tr:
            for g in (ind, tog):
                self.play(Indicate(VGroup(g.cells[(0, 0)], g.cells[(0, 1)]), color=TEAL_, scale_factor=1.05), run_time=1)
            self.fill(tr, 2)
        self.play(*[FadeOut(m) for m in (q, q2, ind, tog, il, tl)])
        self.title_card("Bivariate distributions", 23,
                        "Today we describe two random variables at once.")

    def table(self):
        vals = [[0.10, 0.08, 0.02], [0.06, 0.30, 0.09], [0.02, 0.12, 0.21]]
        g = grid(vals, (r"y_1=-2", r"y_1=0", r"y_1=4"), (r"y_2=-1", r"y_2=1", r"y_2=3"), cell=1.35, fs=28)
        g.move_to(LEFT * 2.6 + DOWN * 0.5)
        head = T("Monthly returns (%): a bank share (Y1) and an oil bond fund (Y2)", 28).to_edge(UP, buff=0.4)
        pl = MathTex(r"p(y_1,y_2)=P(Y_1=y_1,\,Y_2=y_2)", font_size=34, color=BLUE_).next_to(g, RIGHT, buff=0.6).shift(UP * 1.5)
        with self.say("For discrete variables, the joint distribution is a table. Here are monthly "
                      "returns on a bank share and an oil-sector bond fund. Each cell holds the probability "
                      "of that pair of outcomes, and the squares are drawn with areas to match. All nine add "
                      "up to one.") as tr:
            self.play(FadeIn(head))
            self.play(LaggedStart(*[FadeIn(c) for c in g[0]], lag_ratio=0.1), FadeIn(g[1]), FadeIn(g[2]), run_time=2.5)
            self.play(Write(pl))
            self.fill(tr, 4)
        diag = VGroup(*[g.cells[(i, i)] for i in range(3)])
        dl = T("mass sits on the diagonal:\nthe two tend to move together", 26, GREY_).next_to(pl, DOWN, buff=0.5).align_to(pl, LEFT)
        with self.say("Notice where the big squares are: along the diagonal. When the bank share does well, "
                      "the bond fund tends to do well too. No single-variable table could show you that.") as tr:
            self.play(*[c[1].animate.set_fill(YELLOW_, 0.5) for c in diag], FadeIn(dl))
            self.fill(tr, 1)
        both = [(2, 1), (2, 2)]
        gain = [(0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        b1 = MathTex(r"P(\text{both gain})=0.12+0.21=0.33", font_size=34, color=TEAL_).next_to(dl, DOWN, buff=0.5).align_to(pl, LEFT)
        b2 = MathTex(r"P(Y_1+Y_2>0)=0.76", font_size=34, color=RED_).next_to(b1, DOWN, buff=0.4).align_to(pl, LEFT)
        with self.say("Any question about the pair is answered by adding cells. Both assets gain: two "
                      "cells, thirty-three percent. An equal-weight portfolio gains when the two returns sum "
                      "to more than zero: six cells, seventy-six percent.") as tr:
            self.play(*[c[1].animate.set_fill(BLUE_, 0.4) for c in diag], FadeOut(dl))
            self.play(*[g.cells[k][0].animate.set_stroke(TEAL_, 5) for k in both], Write(b1))
            self.wait(1.5)
            self.play(*[g.cells[k][0].animate.set_stroke(DIM, 2) for k in both])
            self.play(*[g.cells[k][0].animate.set_stroke(RED_, 5) for k in gain], Write(b2))
            self.fill(tr, 6.5)

    def density(self):
        rng = np.random.default_rng(3)
        e = rng.exponential(size=(1500, 2))
        y1, y2 = e.min(axis=1), e.max(axis=1)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], x_length=5.8, y_length=5.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).to_edge(LEFT, buff=0.9).shift(DOWN * 0.2)
        xl = MathTex(r"y_1", font_size=32, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex(r"y_2", font_size=32, color=GREY_).next_to(ax.y_axis, UP, buff=0.15)
        diag = DashedLine(ax.c2p(0, 0), ax.c2p(4, 4), color=GREY_)
        keep = (y1 < 4) & (y2 < 4)
        dots = VGroup(*[Dot(ax.c2p(a, b), radius=0.025, color=YELLOW_, fill_opacity=0.7) for a, b in zip(y1[keep], y2[keep])])
        R = RIGHT * 3.6
        head = T("An FX trade settles in two legs", 30).move_to(R + UP * 3.2)
        dens = MathTex(r"f(y_1,y_2)=2e^{-(y_1+y_2)}", r"0\le y_1\le y_2", font_size=34).arrange(DOWN, buff=0.2).next_to(head, DOWN, buff=0.35)
        with self.say("Continuous variables need a joint density. A currency trade settles in two legs: "
                      "Y one is the hour the first leg settles, Y two the second, so Y one is never larger "
                      "than Y two. Simulate fifteen hundred trades and plot each as a point. They fill the "
                      "triangle above the diagonal, thickest near the corner.") as tr:
            self.play(FadeIn(head), Create(ax), FadeIn(xl), FadeIn(yl), Create(diag))
            self.play(Write(dens))
            self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.002), run_time=3)
            self.fill(tr, 6)
        vol = T("density = height of a surface;\nprobability = volume over a region", 26, GREY_).next_to(dens, DOWN, buff=0.45)
        with self.say("The density is the height of a surface over this plane, high where the points "
                      "crowd. A probability is the volume under that surface over a region, and in the "
                      "picture, it's the share of points that land in it.") as tr:
            self.play(FadeIn(vol))
            self.fill(tr, 1)
        sq = Polygon(ax.c2p(0, 0), ax.c2p(1, 0), ax.c2p(1, 1), ax.c2p(0, 1), color=TEAL_, fill_opacity=0.2, stroke_width=3)
        n1 = np.mean((y1 <= 1) & (y2 <= 1))
        p1 = MathTex(r"F(1,1)=(1-e^{-1})^2=0.40", font_size=32, color=TEAL_).next_to(vol, DOWN, buff=0.45)
        s1 = T(f"share of points: {n1:.2f}", 24, TEAL_).next_to(p1, DOWN, buff=0.15)
        with self.say("Both legs settled within an hour: the square up to one, one. The double integral "
                      "gives forty percent, and forty percent of the points are in it.") as tr:
            self.play(DrawBorderThenFill(sq))
            self.play(Write(p1), FadeIn(s1))
            self.fill(tr, 2)
        gap = Polygon(ax.c2p(0, 1), ax.c2p(3, 4), ax.c2p(0, 4), color=RED_, fill_opacity=0.25, stroke_width=3)
        n2 = np.mean(y2 - y1 > 1)
        p2 = MathTex(r"P(Y_2-Y_1>1)=e^{-1}=0.37", font_size=32, color=RED_).next_to(s1, DOWN, buff=0.35)
        s2 = T(f"share of points: {n2:.2f}", 24, RED_).next_to(p2, DOWN, buff=0.15)
        with self.say("Now settlement risk: while one leg has settled and the other hasn't, the bank is "
                      "exposed. The chance the gap exceeds an hour is the region above the line y two "
                      "equals y one plus one. Sketch the region first, then set the limits. The answer is "
                      "e to the minus one, thirty-seven percent.") as tr:
            self.play(FadeOut(sq))
            self.play(DrawBorderThenFill(gap))
            self.play(Write(p2), FadeIn(s2))
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("joint distribution", 38, YELLOW_), T("margins alone can't tell you P(both)", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("discrete", 38, BLUE_), T("a table; add the cells in the event", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("continuous", 38, TEAL_), T("a density; integrate over the region", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("first", 38, RED_), T("sketch the region, then set the limits", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say("So: to answer questions about two variables together, you need their joint "
                      "distribution; the separate ones aren't enough. For discrete variables it's a table, "
                      "and you add cells. For continuous ones it's a density, and you integrate over a "
                      "region. And always sketch the region before you write the limits.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5.2)
