"""Lecture 25 intuition video: independence means every slice has the same shape; the product test; rectangles."""
from common import *

P1 = np.array([0.5, 0.3, 0.2])             # Nizami: low, medium, heavy withdrawals
P2 = np.array([0.6, 0.3, 0.1])             # Khatai
IND = np.outer(P1, P2)
DEP = np.array([[0.40, 0.08, 0.02],
                [0.15, 0.12, 0.03],
                [0.05, 0.10, 0.05]])
LEV = ("low", "medium", "heavy")
S = 1.2


class Lecture25(IntuitionScene):
    parts = ("hook", "slices", "product", "shapes", "closing")

    def hook(self):
        q = T("Two branches, one cash van.", 40)
        q2 = T("Is a heavy day in Nizami a warning for Khatai?", 36, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A bank refills the cash machines of two branches, Nizami and Khatai, from a single "
                      "cash centre. Does a heavy day of withdrawals in Nizami make a heavy day in Khatai more "
                      "likely? If not, the treasury can plan each branch from its own history. If so, both "
                      "running dry on the same day is a bigger risk than it looks.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Independent random variables", 25,
                        "Independence has a simple picture: learning one variable does not change the shape "
                        "of the other.")

    def table(self, M):
        cells = VGroup()
        for i in range(3):
            for j in range(3):
                sq = Square(S, stroke_color=GREY_, stroke_width=1.5, fill_color=BLUE_, fill_opacity=0.15 + 1.8 * M[i, j])
                sq.move_to(np.array([(j - 1) * S, (1 - i) * S, 0]))
                cells.add(VGroup(sq, MathTex(f"{M[i, j]:.2f}", font_size=28).move_to(sq)))
        return cells.move_to(LEFT * 3.0 + DOWN * 0.6)

    def _prof(self, M, cells, color):
        g = VGroup()
        for i in range(3):
            c = M[i] / M[i].sum()
            base = cells[3 * i + 2][0].get_bottom() + RIGHT * 1.5 + UP * 0.05
            g.add(VGroup(*[Rectangle(width=0.32, height=max(c[k], 0.01) * 1.05, fill_color=color, fill_opacity=0.9,
                                     stroke_width=0).move_to(base + RIGHT * 0.45 * k, aligned_edge=DOWN) for k in range(3)]))
        return g

    def slices(self):
        cells = self.table(IND)
        rl = VGroup(*[T(v, 24, GREY_).next_to(cells[3 * i], LEFT, buff=0.2) for i, v in enumerate(LEV)])
        cl = VGroup(*[T(v, 22, GREY_).move_to(cells[j].get_top() + UP * 0.28) for j, v in enumerate(LEV)])
        rt = T("Nizami  Y₁", 26, GREY_).next_to(rl, UP, buff=0.9).align_to(rl, RIGHT)
        ct = T("Khatai  Y₂", 26, GREY_).next_to(cl, UP, buff=0.15)
        prof = self._prof(IND, cells, TEAL_)
        ph = T("Khatai, given each Nizami row", 24, TEAL_).next_to(prof, UP, buff=0.9).align_to(prof, LEFT)
        with self.say("Here is one possible joint table for the two branches, each having a low, medium or "
                      "heavy day. Next to every row, draw the conditional distribution of Khatai: the row, "
                      "rescaled to total one.") as tr:
            self.play(FadeIn(cells), FadeIn(rl), FadeIn(cl), FadeIn(rt), FadeIn(ct))
            self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in prof], lag_ratio=0.3), FadeIn(ph), run_time=2)
            self.fill(tr, 3)
        same = T("same shape in every row", 28, TEAL_).next_to(prof, DOWN, buff=0.5)
        with self.say("All three profiles are identical. Whatever happened in Nizami, Khatai's chances stay "
                      "sixty, thirty, ten. Knowing one branch tells you nothing about the other. That is "
                      "independence.") as tr:
            self.play(*[Indicate(r, color=YELLOW_) for r in prof], run_time=1.5)
            self.play(FadeIn(same))
            self.fill(tr, 2.5)
        dcells = self.table(DEP)
        dprof = self._prof(DEP, dcells, RED_)
        diff = T("the shape tilts with Nizami", 28, RED_).move_to(same)
        with self.say("Now a second table with exactly the same row and column totals, but a different "
                      "inside. The profiles tilt: after a heavy day in Nizami, a heavy day in Khatai is five "
                      "times as likely as after a quiet one. These branches are dependent, perhaps because "
                      "salaries and holidays hit both.") as tr:
            self.play(Transform(cells, dcells), Transform(prof, dprof), Transform(same, diff), run_time=2)
            self.fill(tr, 2)
        self.cells = cells
        self.keep = VGroup(rl, cl, rt, ct, ph)
        self.prof = prof
        self.same = same

    def product(self):
        cells = self.table(DEP)
        rl = VGroup(*[T(v, 24, GREY_).next_to(cells[3 * i], LEFT, buff=0.2) for i, v in enumerate(LEV)])
        cl = VGroup(*[T(v, 22, GREY_).move_to(cells[j].get_top() + UP * 0.28) for j, v in enumerate(LEV)])
        side = VGroup(*[MathTex(f"{P1[i]:.1f}", font_size=30, color=PURPLE_).next_to(cells[3 * i + 2], RIGHT, buff=0.3) for i in range(3)])
        bot = VGroup(*[MathTex(f"{P2[j]:.1f}", font_size=30, color=TEAL_).next_to(cells[6 + j], DOWN, buff=0.3) for j in range(3)])
        rule = MathTex(r"p(y_1,y_2)\overset{?}{=}p_1(y_1)\,p_2(y_2)", font_size=36, color=YELLOW_).move_to(RIGHT * 3.4 + UP * 2.2)
        with self.say("To test independence without drawing profiles, use the margins. Independence means "
                      "every cell equals its row total times its column total.") as tr:
            self.play(FadeIn(cells), FadeIn(rl), FadeIn(cl))
            self.play(FadeIn(side), FadeIn(bot))
            self.play(Write(rule))
            self.fill(tr, 3)
        b1 = SurroundingRectangle(cells[0], color=RED_, buff=0.04)
        e1 = MathTex(r"0.40\ \ne\ 0.5\times0.6=0.30", font_size=36, color=RED_).move_to(RIGHT * 3.4 + UP * 0.9)
        st = T("one failing cell: dependent, stop", 28, RED_).next_to(e1, DOWN, buff=0.3)
        with self.say("Check the first cell. Zero point four, against zero point five times zero point six, "
                      "which is zero point three. They differ, and that single cell is enough: the branches are "
                      "dependent. Proving independence would need all nine cells to pass.") as tr:
            self.play(Create(b1))
            self.play(Write(e1), run_time=1.5)
            self.play(FadeIn(st))
            self.fill(tr, 3.5)
        b2 = SurroundingRectangle(cells[8], color=YELLOW_, buff=0.04)
        e2 = VGroup(MathTex(r"P(\text{both heavy})=0.05", font_size=34, color=YELLOW_),
                    MathTex(r"\text{not }0.2\times0.1=0.02", font_size=34, color=YELLOW_)).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.4 + DOWN * 1.5)
        with self.say("And it matters for the cash van. Both branches heavy on the same day has probability "
                      "five percent, not the two percent that multiplying would give. Planning each branch "
                      "separately would understate that risk by more than half.") as tr:
            self.play(Create(b2))
            self.play(Write(e2), run_time=1.5)
            self.fill(tr, 2.5)

    def shapes(self):
        ax = Axes(x_range=[0, 1.05, 0.5], y_range=[0, 1.05, 0.5], x_length=3.4, y_length=3.4, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 20})
        ax2 = ax.copy()
        ax.move_to(LEFT * 4.4 + DOWN * 0.4)
        ax2.move_to(LEFT * 0.2 + DOWN * 0.4)
        sq = Polygon(ax.c2p(0, 0), ax.c2p(1, 0), ax.c2p(1, 1), ax.c2p(0, 1), color=BLUE_, fill_opacity=0.3, stroke_width=2)
        tri = Polygon(ax2.c2p(0, 0), ax2.c2p(1, 0), ax2.c2p(1, 1), color=RED_, fill_opacity=0.3, stroke_width=2)
        l1 = MathTex(r"6y_1y_2^2", font_size=32, color=BLUE_).next_to(ax, UP, buff=0.25)
        l2 = MathTex(r"2,\ \ y_2\le y_1", font_size=32, color=RED_).next_to(ax2, UP, buff=0.25)
        lab = VGroup(MathTex("y_1", font_size=26, color=GREY_).next_to(ax.x_axis, DOWN, buff=0.45),
                     MathTex("y_1", font_size=26, color=GREY_).next_to(ax2.x_axis, DOWN, buff=0.45))
        with self.say("For densities, the picture is the same: slice at a value of y one, and ask whether the "
                      "slice has the same shape every time. Compare a density on a square with one on a "
                      "triangle.") as tr:
            self.play(Create(ax), Create(ax2), FadeIn(lab))
            self.play(FadeIn(sq), FadeIn(tri), Write(l1), Write(l2))
            self.fill(tr, 2)
        cx = Axes(x_range=[0, 1.05, 0.5], y_range=[0, 3.2, 1], x_length=3.2, y_length=3.4, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 20}).move_to(RIGHT * 4.6 + DOWN * 0.4)
        cl = MathTex(r"f(y_2\mid y_1)", font_size=30, color=WHITE_).next_to(cx, UP, buff=0.25)
        cxl = MathTex("y_2", font_size=26, color=GREY_).next_to(cx.x_axis, DOWN, buff=0.45)
        y = ValueTracker(0.4)
        s1 = always_redraw(lambda: Line(ax.c2p(y.get_value(), 0), ax.c2p(y.get_value(), 1), color=BLUE_, stroke_width=5))
        s2 = always_redraw(lambda: Line(ax2.c2p(y.get_value(), 0), ax2.c2p(y.get_value(), y.get_value()), color=RED_, stroke_width=5))
        c1 = always_redraw(lambda: cx.plot(lambda t: 3 * t * t, x_range=[0, 1], color=BLUE_, stroke_width=4))
        c2 = always_redraw(lambda: VMobject().set_points_as_corners(
            [cx.c2p(0, 0), cx.c2p(0, 1 / y.get_value()), cx.c2p(y.get_value(), 1 / y.get_value()), cx.c2p(y.get_value(), 0)]
        ).set_stroke(RED_, 4))
        with self.say("Sweep y one from left to right. On the square, every slice gives the same conditional "
                      "curve, three y two squared: independent. On the triangle, the slice gets longer as y one "
                      "grows, so the conditional density keeps changing width. Knowing y one tells you the "
                      "range of y two, so they are dependent, whatever the formula looks like.") as tr:
            self.play(Create(cx), FadeIn(cl), FadeIn(cxl))
            self.add(s1, s2, c1, c2)
            self.play(y.animate.set_value(0.95), run_time=4, rate_func=there_and_back_with_pause)
            self.play(y.animate.set_value(0.6), run_time=1.5)
            self.fill(tr, 6.5)
        rule = MathTex(r"f(y_1,y_2)=g(y_1)\,h(y_2)\ \text{ on a rectangle}", font_size=38, color=YELLOW_).to_edge(UP, buff=0.35)
        with self.say("That gives the quick test for densities. Independence holds exactly when the density "
                      "splits into a function of y one times a function of y two, over a rectangle.") as tr:
            self.play(Write(rule), run_time=2)
            self.fill(tr, 2)

    def closing(self):
        g = VGroup(
            VGroup(T("independent", 38, TEAL_), T("every slice has the same shape", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("test", 38, YELLOW_), T("joint = product of marginals, in every cell", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("dependent", 38, RED_), T("one failing cell is enough", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("densities", 38, BLUE_), T("g(y₁) h(y₂) on a rectangle", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("So: two variables are independent when every conditional slice has the same shape. "
                      "In a table, every cell must equal its row total times its column total, and one "
                      "failure proves dependence. For a density, look for a product over a rectangle.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5)
