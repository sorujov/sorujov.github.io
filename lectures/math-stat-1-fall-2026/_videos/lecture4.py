"""Lecture 4 intuition video: counting (mn rule, permutations, combinations as 'divide out the orderings')."""
from common import *

NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
COLS = [BLUE_, TEAL_, YELLOW_, RED_, GREEN_, PURPLE_, "#FF9F43", "#E5E5E5", "#9AD1FF", "#F78FB3"]


def chip(i, r=0.28):
    c = Circle(radius=r, color=COLS[i], fill_opacity=0.9, stroke_width=0)
    return VGroup(c, T(NAMES[i], int(r * 80), BG, weight=BOLD).move_to(c))


class Lecture4(IntuitionScene):
    parts = ("hook", "mn_rule", "ordered", "unordered", "closing")

    def hook(self):
        q = T("Pick 3 of 10 stocks for a new fund.", 42)
        q2 = T("How many different portfolios are possible?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A fund manager wants to pick three stocks out of a shortlist of ten. How many "
                      "different portfolios could she end up with? When outcomes are equally likely, "
                      "probability is just counting, so we need to count well.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Counting sample points", 4,
                        "It turns out that almost every counting problem comes down to one rule, and one "
                        "trick.")

    def mn_rule(self):
        rows = ["AAA", "AA", "A"]
        cols = ["Aaa", "Aa", "A", "Baa"]
        g = VGroup()
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                sq = Rectangle(width=1.45, height=0.9, stroke_color=GREY_, stroke_width=1.5).move_to([(j - 1.5) * 1.5, (1 - i) * 0.95, 0])
                g.add(VGroup(sq, T(f"{r}, {c}", 18).move_to(sq)))
        g.shift(LEFT * 2.2 + DOWN * 0.3)
        rl = VGroup(*[T(r, 26, BLUE_).next_to(g[i * 4], LEFT, buff=0.3) for i, r in enumerate(rows)])
        cl = VGroup(*[T(c, 26, TEAL_).next_to(g[j], UP, buff=0.3) for j, c in enumerate(cols)])
        ra = T("rows: agency 1, three grades", 24, BLUE_).next_to(g, DOWN, buff=0.45).align_to(g, LEFT)
        ca = T("columns: agency 2, four grades", 24, TEAL_).next_to(ra, DOWN, buff=0.2).align_to(g, LEFT)
        with self.say("The rule first. A bond gets a rating from one agency, with three possible grades, "
                      "and from a second agency, with four. How many pairs of ratings are possible? Lay "
                      "them out as a grid: three rows, four columns.") as tr:
            self.play(FadeIn(rl), FadeIn(ra), FadeIn(cl), FadeIn(ca))
            self.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in g], lag_ratio=0.06, run_time=2))
            self.fill(tr, 3)
        f = MathTex(r"3\times4=12", font_size=60, color=YELLOW_).next_to(g, RIGHT, buff=1.0)
        f2 = MathTex(r"m\times n", font_size=46).next_to(f, DOWN, buff=0.4)
        with self.say("Twelve cells, three times four. That's the m n rule: if one choice has m options "
                      "and the next has n, together they have m times n. With more stages you just keep "
                      "multiplying.") as tr:
            self.play(Write(f))
            self.play(FadeIn(f2))
            self.fill(tr, 2)

    def ordered(self):
        pool = VGroup(*[chip(i) for i in range(10)]).arrange(RIGHT, buff=0.25).to_edge(UP, buff=1.0)
        slots = VGroup(*[RoundedRectangle(corner_radius=0.1, width=1.1, height=1.1, color=GREY_) for _ in range(3)]
                       ).arrange(RIGHT, buff=0.9).shift(DOWN * 0.6)
        sl = VGroup(*[T(s, 24, GREY_).next_to(b, DOWN, buff=0.2) for s, b in zip(["1st", "2nd", "3rd"], slots)])
        with self.say("Now the stocks, but let's first pretend order matters, as if we were ranking the "
                      "picks first, second and third. Ten stocks, three slots.") as tr:
            self.play(FadeIn(pool), Create(slots), FadeIn(sl))
            self.fill(tr, 1)
        nums = VGroup(*[MathTex(str(k), font_size=56, color=YELLOW_).next_to(b, DOWN, buff=0.8) for k, b in zip([10, 9, 8], slots)])
        times = VGroup(MathTex(r"\times", font_size=48).move_to((nums[0].get_center() + nums[1].get_center()) / 2),
                       MathTex(r"\times", font_size=48).move_to((nums[1].get_center() + nums[2].get_center()) / 2))
        with self.say("The first slot can take any of the ten. Once it's filled, nine remain for the "
                      "second, then eight for the third. By the m n rule, that's ten times nine times "
                      "eight: seven hundred and twenty ordered picks.") as tr:
            for k, idx in enumerate([2, 6, 0]):
                self.play(pool[idx].animate.move_to(slots[k]), FadeIn(nums[k]), run_time=1)
                if k:
                    self.play(FadeIn(times[k - 1]), run_time=0.3)
            res = MathTex("=720", font_size=56, color=YELLOW_).next_to(nums[2], RIGHT, buff=0.4)
            self.play(Write(res))
            self.fill(tr, 5)
        self.res = res

    def unordered(self):
        from itertools import permutations
        trio = [2, 6, 0]
        perms = list(permutations(trio))
        rows = VGroup()
        for p in perms:
            rows.add(VGroup(*[chip(i, 0.24) for i in p]).arrange(RIGHT, buff=0.12))
        rows.arrange_in_grid(2, 3, buff=(0.8, 0.5)).shift(UP * 1.4)
        with self.say("But a portfolio doesn't care about order. Take one particular trio: C, G and A. "
                      "In our list of seven hundred and twenty, it shows up six times, once for every way "
                      "of ordering it.") as tr:
            self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.2) for r in rows], lag_ratio=0.3, run_time=2.5))
            self.fill(tr, 2.5)
        one = VGroup(*[chip(i, 0.3) for i in sorted(trio)]).arrange(RIGHT, buff=0.15).move_to(UP * 1.4)
        with self.say("Every trio is counted three factorial, that is six, times. So we collapse each "
                      "group of six into one.") as tr:
            self.play(*[ReplacementTransform(r, one.copy()) for r in rows], run_time=2)
            self.fill(tr, 2)
        f = MathTex(r"\frac{10\times9\times8}{3!}=\frac{720}{6}=", "120", font_size=56).shift(DOWN * 0.8)
        f[1].set_color(YELLOW_)
        g = MathTex(r"\binom{n}{r}=\frac{n!}{r!\,(n-r)!}", font_size=48, color=TEAL_).next_to(f, DOWN, buff=0.6)
        with self.say("Seven hundred and twenty divided by six: one hundred and twenty possible "
                      "portfolios. In general, the number of ways to choose r things from n, ignoring "
                      "order, is n choose r.") as tr:
            self.play(Write(f), run_time=2)
            self.play(Write(g))
            self.fill(tr, 3.5)

    def closing(self):
        a = T("Count as if order mattered,", 40, YELLOW_)
        b = T("then divide by the orderings you don't care about.", 40, TEAL_)
        g = VGroup(a, b).arrange(DOWN, buff=0.5)
        with self.say("So here's the trick worth remembering. Count as if order mattered, which is easy "
                      "with the m n rule. Then divide by the number of orderings you don't care about. "
                      "Permutations, combinations, even partitions into several groups: they are all this "
                      "one idea.") as tr:
            self.play(Write(a))
            self.play(Write(b))
            self.fill(tr, 3)
