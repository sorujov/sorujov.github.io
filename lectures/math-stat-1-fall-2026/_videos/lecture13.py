"""Lecture 13 intuition video: hypergeometric (drawing without replacement) and Poisson (many tiny chances)."""
from common import *
from math import comb, exp, factorial


class Lecture13(IntuitionScene):
    parts = ("hook", "without_replacement", "big_population", "poisson", "closing")

    def hook(self):
        q = T("20 invoices, 4 of them contain errors.", 40)
        q2 = T("An auditor checks 5. How many errors does she find?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("An auditor has a folder of twenty invoices, and four of them contain errors. She "
                      "checks five of them at random. How many errors will she find? It looks like a "
                      "binomial problem. It isn't quite.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Hypergeometric and Poisson", 13,
                        "Two more distributions, each with a clear picture behind it: drawing without "
                        "replacement, and counting rare events.")

    def without_replacement(self):
        inv = VGroup(*[RoundedRectangle(corner_radius=0.06, width=0.5, height=0.7, color=RED_ if i < 4 else TEAL_, fill_opacity=0.35)
                       for i in range(20)]).arrange_in_grid(2, 10, buff=0.18).to_edge(UP, buff=0.8)
        with self.say("The difference is that she doesn't put an invoice back after checking it. The "
                      "first invoice she picks has a four in twenty chance of containing an error.") as tr:
            self.play(LaggedStart(*[FadeIn(x) for x in inv], lag_ratio=0.03))
            self.fill(tr, 1)
        steps = VGroup(MathTex(r"\tfrac{4}{20}=0.20", font_size=40), MathTex(r"\tfrac{3}{19}\approx0.16", font_size=40),
                       MathTex(r"\tfrac{4}{19}\approx0.21", font_size=40)).arrange(RIGHT, buff=2.0).shift(DOWN * 0.2)
        caps = VGroup(T("first pick", 24, GREY_), T("next pick, if the\nfirst had an error", 24, RED_, line_spacing=0.8),
                      T("next pick, if the\nfirst was clean", 24, TEAL_, line_spacing=0.8))
        for c, s in zip(caps, steps):
            c.next_to(s, DOWN, buff=0.25)
        with self.say("But the second pick depends on the first. If the first had an error, three bad "
                      "invoices remain among nineteen. If it was clean, four remain among nineteen. The "
                      "trials are not independent, and p changes as she goes. So it isn't binomial.") as tr:
            self.play(FadeIn(steps[0]), FadeIn(caps[0]))
            self.play(inv[0].animate.shift(DOWN * 0.3).set_opacity(0.2))
            self.play(FadeIn(steps[1]), FadeIn(caps[1]))
            self.play(FadeIn(steps[2]), FadeIn(caps[2]))
            self.fill(tr, 4)
        f = MathTex(r"p(y)=\frac{\binom{r}{y}\binom{N-r}{n-y}}{\binom{N}{n}}", font_size=46, color=YELLOW_).to_edge(DOWN, buff=0.5)
        with self.say("Instead we count directly: choose y of the four bad invoices, n minus y of the "
                      "sixteen good ones, and divide by all the ways to choose five. That is the "
                      "hypergeometric distribution.") as tr:
            self.play(Write(f), run_time=2)
            self.fill(tr, 2)

    def big_population(self):
        def bars(ax, probs, color, dx):
            return VGroup(*[Rectangle(width=0.28, height=p * ax.y_axis.get_unit_size(), stroke_width=0, fill_color=color,
                                      fill_opacity=0.85).move_to(ax.c2p(y + dx + 0.8, 0), aligned_edge=DOWN) for y, p in enumerate(probs)])
        ax = Axes(x_range=[0, 6.3, 1], y_range=[0, 0.5, 0.1], x_length=8, y_length=4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [0.1, 0.2, 0.3, 0.4]}).shift(DOWN * 0.5 + LEFT * 1)
        ax.add(VGroup(*[MathTex(str(y), font_size=28).next_to(ax.c2p(y + 0.8, 0), DOWN, buff=0.15) for y in range(6)]))
        binom = [comb(5, y) * 0.2 ** y * 0.8 ** (5 - y) for y in range(6)]
        hyp = lambda N, r: [comb(r, y) * comb(N - r, 5 - y) / comb(N, 5) if y <= r else 0 for y in range(6)]
        bb = bars(ax, binom, BLUE_, 0.16)
        hb = bars(ax, hyp(20, 4), YELLOW_, -0.16)
        leg = VGroup(VGroup(Square(0.25, fill_color=YELLOW_, fill_opacity=0.85, stroke_width=0), T("hypergeometric", 26, YELLOW_)).arrange(RIGHT, buff=0.2),
                     VGroup(Square(0.25, fill_color=BLUE_, fill_opacity=0.85, stroke_width=0), T("binomial, p = 0.2", 26, BLUE_)).arrange(RIGHT, buff=0.2)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(UR, buff=0.6)
        Nl = MathTex("N=20", font_size=44).next_to(leg, DOWN, buff=0.6).align_to(leg, LEFT)
        with self.say("Here it is next to the binomial we might have used. With only twenty invoices the "
                      "hypergeometric is noticeably tighter: sampling without replacement means each find "
                      "makes the next one a little less likely.") as tr:
            self.play(Create(ax), FadeIn(leg), FadeIn(Nl))
            self.play(LaggedStart(*[GrowFromEdge(x, DOWN) for x in hb], lag_ratio=0.1),
                      LaggedStart(*[GrowFromEdge(x, DOWN) for x in bb], lag_ratio=0.1), run_time=2)
            self.fill(tr, 3)
        with self.say("But make the folder bigger, keeping twenty percent of it faulty. With two hundred "
                      "invoices, then two thousand, removing five barely changes anything, and the two "
                      "distributions become the same. When the population is large compared to the sample, "
                      "the binomial is a fine approximation.") as tr:
            for N in (200, 2000):
                nh = bars(ax, hyp(N, N // 5), YELLOW_, -0.16)
                self.play(Transform(hb, nh), Transform(Nl, MathTex(f"N={N}", font_size=44).move_to(Nl, aligned_edge=LEFT)), run_time=2)
                self.wait(1)
            self.fill(tr, 6)

    def poisson(self):
        lam = 3
        q = T("An ATM: on average 3 customers in 10 minutes.", 34).to_edge(UP, buff=0.6)
        with self.say("Now a different kind of count. An ATM sees on average three customers every ten "
                      "minutes. How many will arrive in the next ten minutes?") as tr:
            self.play(FadeIn(q))
            self.fill(tr, 1)
        line = NumberLine(x_range=[0, 10, 1], length=10, color=GREY_, include_numbers=False).shift(UP * 1.4)
        cuts = ValueTracker(10)
        ticks = always_redraw(lambda: VGroup(*[Line(line.n2p(10 * k / int(cuts.get_value())) + UP * 0.12,
                                                     line.n2p(10 * k / int(cuts.get_value())) + DOWN * 0.12, color=GREY_, stroke_width=1.5)
                                                for k in range(int(cuts.get_value()) + 1)]))
        lbl = always_redraw(lambda: MathTex(f"n={int(cuts.get_value())}\\ \\text{{slices}},\\ p=\\tfrac{{3}}{{{int(cuts.get_value())}}}",
                                            font_size=36, color=BLUE_).next_to(line, DOWN, buff=0.35))
        with self.say("Chop the ten minutes into many tiny slices, so small that at most one customer "
                      "can arrive in each. Then every slice is a trial, with a tiny chance of an arrival, "
                      "and the count is binomial with a huge n and a tiny p.") as tr:
            self.play(Create(line))
            self.add(ticks, lbl)
            self.play(cuts.animate.set_value(60), run_time=3)
            self.fill(tr, 4)
        ax = Axes(x_range=[0, 11.3, 1], y_range=[0, 0.3, 0.1], x_length=9, y_length=3, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [0.1, 0.2]}).shift(DOWN * 2)
        ax.add(VGroup(*[MathTex(str(y), font_size=24).next_to(ax.c2p(y + 0.8, 0), DOWN, buff=0.12) for y in range(11)]))
        nt = ValueTracker(10)
        bb = always_redraw(lambda: VGroup(*[Rectangle(width=0.35, height=comb(int(nt.get_value()), y) * (lam / nt.get_value()) ** y *
                                                      (1 - lam / nt.get_value()) ** (int(nt.get_value()) - y) * ax.y_axis.get_unit_size(),
                                                      stroke_width=0, fill_color=BLUE_, fill_opacity=0.8).move_to(ax.c2p(y + 0.8, 0), aligned_edge=DOWN)
                                            for y in range(11)]))
        pois = VGroup(*[Dot(ax.c2p(y + 0.8, exp(-lam) * lam ** y / factorial(y)), color=YELLOW_, radius=0.07) for y in range(11)])
        f = MathTex(r"p(y)=\frac{\lambda^{y}e^{-\lambda}}{y!}", font_size=42, color=YELLOW_).to_corner(DR, buff=0.5).shift(UP * 2.2)
        with self.say("As the slices get finer, the binomial settles onto a fixed shape: the Poisson "
                      "distribution, marked by the yellow dots. It depends only on lambda, the average "
                      "count, here three. And its mean and its variance are both lambda.") as tr:
            self.play(Create(ax))
            self.add(bb)
            self.play(FadeIn(pois))
            self.play(nt.animate.set_value(200), cuts.animate.set_value(120), run_time=4)
            self.play(Write(f))
            self.fill(tr, 7)

    def closing(self):
        g = VGroup(
            VGroup(T("hypergeometric", 38, YELLOW_), T("draws without replacement; ≈ binomial for large N", 28)).arrange(RIGHT, buff=0.5),
            VGroup(T("Poisson", 38, BLUE_), T("many tiny chances; mean = variance = λ", 28)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: the hypergeometric counts successes when you draw without putting back, and "
                      "it looks binomial when the population is large. The Poisson counts events built "
                      "from many tiny independent chances, like arrivals, claims or outages, and its mean "
                      "equals its variance.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 3)
