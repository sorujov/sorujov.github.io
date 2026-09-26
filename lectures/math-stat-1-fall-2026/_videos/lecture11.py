"""Lecture 11 intuition video: where the binomial formula comes from, and how n and p shape it."""
from common import *
from itertools import product
from math import comb


def pmf_bars(ax, n, p, color=YELLOW_, width=0.6):
    return VGroup(*[Rectangle(width=width * ax.x_axis.get_unit_size(), height=max(comb(n, y) * p ** y * (1 - p) ** (n - y), 1e-4) * ax.y_axis.get_unit_size(),
                              stroke_width=0, fill_color=color, fill_opacity=0.85).move_to(ax.c2p(y, 0), aligned_edge=DOWN)
                    for y in range(n + 1)])


class Lecture11(IntuitionScene):
    parts = ("hook", "sequences", "formula", "shape", "closing")

    def hook(self):
        q = T("Each card payment is declined with probability 0.1.", 38)
        q2 = T("Out of 4 payments, how many are declined?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A card payment is declined ten percent of the time, independently of the others. "
                      "A customer makes four payments today. How many of them get declined? Zero is "
                      "likely, one is possible, four would be a very bad day. Let's find the whole "
                      "distribution.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("The binomial distribution", 11,
                        "The same pattern appears whenever we count successes in a fixed number of "
                        "independent, identical trials.")

    def sequences(self):
        seqs = ["".join(s) for s in product("SF", repeat=4)]
        groups = [[s for s in seqs if s.count("F") == y] for y in range(5)]
        cols = VGroup()
        for y, g in enumerate(groups):
            col = VGroup(*[VGroup(*[T(c, 32, RED_ if c == "F" else TEAL_) for c in s]).arrange(RIGHT, buff=0.08) for s in g])
            col.arrange(DOWN, buff=0.12)
            cols.add(col)
        cols.arrange(RIGHT, buff=1.1, aligned_edge=UP).shift(UP * 0.6)
        heads = VGroup(*[MathTex(f"y={y}", font_size=40, color=YELLOW_).next_to(c, UP, buff=0.3) for y, c in enumerate(cols)])
        for h in heads:
            h.set_y(heads[2].get_y())
        key = T("S = goes through,  F = declined", 24, GREY_).to_edge(DOWN, buff=0.3)
        with self.say("Each payment either goes through or is declined, so four payments give two to the "
                      "fourth, sixteen possible sequences. Let's sort them by how many declines they "
                      "contain.") as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cols], lag_ratio=0.3), FadeIn(heads), FadeIn(key), run_time=3)
            self.fill(tr, 3)
        cnt = VGroup(*[MathTex(rf"\binom{{4}}{{{y}}}={comb(4, y)}", font_size=36).next_to(cols[y], DOWN, buff=0.35) for y in range(5)])
        for c in cnt:
            c.set_y(cols[2].get_bottom()[1] - 0.55)
        with self.say("There is one sequence with no declines, four with exactly one, six with two, four "
                      "with three, and one with all four declined. Those counts are just 'four choose y': "
                      "the number of ways to pick which payments fail.") as tr:
            self.play(LaggedStart(*[FadeIn(c) for c in cnt], lag_ratio=0.3), run_time=2.5)
            self.fill(tr, 2.5)
        self.cols, self.cnt, self.heads = cols, cnt, heads

    def formula(self):
        one = VGroup(*[T(c, 44, RED_ if c == "F" else TEAL_) for c in "FSSF"]).arrange(RIGHT, buff=0.15).shift(UP * 2)
        pr = MathTex(r"0.1\times0.9\times0.9\times0.1=0.1^2\,0.9^2", font_size=44).next_to(one, DOWN, buff=0.5)
        with self.say("Now the probability of any one sequence. Take fail, succeed, succeed, fail. By "
                      "independence, multiply: point one times point nine times point nine times point "
                      "one. Every sequence with two declines has exactly this probability; only the order "
                      "differs.") as tr:
            self.play(FadeIn(one))
            self.play(Write(pr), run_time=2)
            self.fill(tr, 2.5)
        f = MathTex(r"p(y)", "=", r"\binom{n}{y}", r"\,p^{y}\,q^{\,n-y}", font_size=58).shift(DOWN * 1.0)
        f[2].set_color(YELLOW_)
        f[3].set_color(TEAL_)
        b1 = Brace(f[2], DOWN, color=YELLOW_)
        t1 = T("how many sequences", 26, YELLOW_).next_to(b1, DOWN, buff=0.1)
        b2 = Brace(f[3], UP, color=TEAL_)
        t2 = T("probability of each one", 26, TEAL_).next_to(b2, UP, buff=0.1)
        with self.say("So the probability of y declines is the number of such sequences, times the "
                      "probability of each one. That's the whole binomial formula: n choose y, times p "
                      "to the y, times q to the n minus y.") as tr:
            self.play(Write(f), run_time=2)
            self.play(GrowFromCenter(b1), FadeIn(t1))
            self.play(GrowFromCenter(b2), FadeIn(t2))
            self.fill(tr, 4)

    def shape(self):
        n = 20
        ax = Axes(x_range=[-0.5, 20.5, 5], y_range=[0, 0.3, 0.1], x_length=10, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.5)
        pt = ValueTracker(0.1)
        bars = always_redraw(lambda: pmf_bars(ax, n, pt.get_value()))
        lab = always_redraw(lambda: MathTex(f"n=20,\\ p={pt.get_value():.2f}", font_size=40, color=YELLOW_).to_corner(UR, buff=0.6))
        mean = always_redraw(lambda: Triangle(color=TEAL_, fill_opacity=1).scale(0.15).next_to(ax.c2p(n * pt.get_value(), 0), DOWN, buff=0.35))
        ml = MathTex(r"E(Y)=np", font_size=40, color=TEAL_).to_corner(UL, buff=0.6)
        with self.say("Now take twenty payments and watch the shape as p changes. With a small p the "
                      "distribution huddles near zero and is skewed to the right. As p grows, the hump "
                      "moves right and becomes more symmetric. The balance point is always n times p.") as tr:
            self.play(Create(ax), FadeIn(ml))
            self.add(bars, lab, mean)
            self.play(pt.animate.set_value(0.5), run_time=5)
            self.wait(0.5)
            self.play(pt.animate.set_value(0.85), run_time=3)
            self.fill(tr, 9.5)
        v = MathTex(r"V(Y)=npq", font_size=40, color=RED_).next_to(ml, DOWN, buff=0.3).align_to(ml, LEFT)
        with self.say("And the spread is n p q. It's largest at p equals one half, when each trial is "
                      "the most uncertain, and it shrinks as p approaches zero or one.") as tr:
            self.play(Write(v))
            self.play(pt.animate.set_value(0.5), run_time=2.5)
            self.fill(tr, 3.5)

    def closing(self):
        g = VGroup(
            T("fixed n, independent trials, same p", 36, BLUE_),
            MathTex(r"p(y)=\binom{n}{y}p^yq^{n-y}", font_size=50),
            T("= (number of sequences) × (probability of each)", 32, YELLOW_),
        ).arrange(DOWN, buff=0.5)
        with self.say("So when you count successes in a fixed number of independent trials with the same "
                      "chance, the binomial formula is just counting times multiplying: the number of "
                      "sequences with y successes, times the probability of any one of them.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=UP * 0.2))
                self.wait(0.6)
            self.fill(tr, 4)
