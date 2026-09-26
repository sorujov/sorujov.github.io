"""Lecture 10 intuition video: pmf, expected value as balance point and long-run average, variance, E[g(Y)]."""
from common import *

YS = [0, 1, 2, 3]
PS = [0.50, 0.30, 0.15, 0.05]
MU = sum(y * p for y, p in zip(YS, PS))          # 0.75
X0 = 0.8                                          # screen offset so the y-axis sits left of the bars


class Lecture10(IntuitionScene):
    parts = ("hook", "pmf", "long_run", "spread", "g_of_y", "closing")

    def hook(self):
        q = T("An internet provider logs outages every day.", 40)
        q2 = T("How many outages should it expect per day?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("An internet provider records how many network outages it has each day. Most days "
                      "none, some days one, occasionally two or three. How many outages should it "
                      "expect per day? And what does 'expect' even mean, when the answer isn't a whole "
                      "number?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Discrete random variables", 10,
                        "A discrete random variable is described by a list of values and their "
                        "probabilities. Two numbers summarise it: its mean and its variance.")

    def axes(self):
        ax = Axes(x_range=[0, 4.5, 1], y_range=[0, 0.6, 0.1], x_length=8, y_length=4.5, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [0.1, 0.2, 0.3, 0.4, 0.5]})
        ax.shift(UP * 0.1)
        ax.add(VGroup(*[MathTex(str(y), font_size=30).next_to(ax.c2p(y + X0, 0), DOWN, buff=0.2) for y in YS]))
        return ax

    def bars(self, ax, color=YELLOW_):
        return VGroup(*[Rectangle(width=0.62 * ax.x_axis.get_unit_size(), height=p * ax.y_axis.get_unit_size(),
                                  stroke_width=0, fill_color=color, fill_opacity=0.8).move_to(ax.c2p(y + X0, 0), aligned_edge=DOWN)
                        for y, p in zip(YS, PS)])

    def pmf(self):
        ax = self.axes()
        b = self.bars(ax)
        lab = VGroup(*[MathTex(f"{p:.2f}", font_size=30).next_to(bb, UP, buff=0.1) for p, bb in zip(PS, b)])
        xl = T("outages in a day", 26, GREY_).next_to(ax, DOWN, buff=0.9)
        yl = MathTex(r"p(y)=P(Y=y)", font_size=36, color=YELLOW_).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        with self.say("Here is the probability function: half of all days have no outage, thirty percent "
                      "have one, fifteen percent two, five percent three. The bars add up to one, as they "
                      "must.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(LaggedStart(*[GrowFromEdge(x, DOWN) for x in b], lag_ratio=0.2), FadeIn(lab))
            self.fill(tr, 3)
        tri = Triangle(color=WHITE_, fill_opacity=1).scale(0.2).next_to(ax.c2p(MU + X0, 0), DOWN, buff=0.45)
        m = MathTex(r"E(Y)=\sum_y y\,p(y)=", "0.75", font_size=44).to_corner(UR, buff=0.6)
        m[1].set_color(TEAL_)
        with self.say("Think of each bar as a weight sitting at its value. The expected value is the "
                      "balance point: zero times a half, plus one times point three, plus two times point "
                      "one five, plus three times point zero five. Point seven five outages.") as tr:
            self.play(FadeIn(tri, shift=UP * 0.2))
            self.play(Write(m), run_time=2)
            self.fill(tr, 3)
        self.keep = VGroup(ax, b, lab, xl, yl, tri, m)

    def long_run(self):
        rng = np.random.default_rng(10)
        days = rng.choice(YS, size=365, p=PS)
        avg = np.cumsum(days) / np.arange(1, 366)
        ax = Axes(x_range=[0, 365, 100], y_range=[0, 2, 0.5], x_length=10, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.4)
        xl = T("days observed", 24, GREY_).next_to(ax, DOWN, buff=0.3)
        yl = T("average outages per day so far", 24, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        mu = DashedLine(ax.c2p(0, MU), ax.c2p(365, MU), color=TEAL_)
        k = ValueTracker(1)
        path = always_redraw(lambda: ax.plot_line_graph(np.arange(1, int(k.get_value()) + 1), avg[:int(k.get_value())],
                                                        add_vertex_dots=False, line_color=YELLOW_, stroke_width=3))
        with self.say("Point seven five outages can't happen on any single day. So what does it mean? "
                      "Watch the average number of outages per day, as the days go by.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.add(path)
            self.play(k.animate.set_value(20), run_time=2)
            self.fill(tr, 3)
        with self.say("It jumps around at first, then settles down to point seven five. The expected "
                      "value is the long-run average: what you'd get per day, on average, over a very long "
                      "time.") as tr:
            self.play(k.animate.set_value(365), run_time=6, rate_func=linear)
            self.play(Create(mu))
            self.fill(tr, 7)

    def spread(self):
        ax = self.axes()
        b = self.bars(ax)
        u = ax.x_axis.get_unit_size()
        mu = DashedLine(ax.c2p(MU + X0, 0), ax.c2p(MU + X0, 0.6), color=TEAL_)
        with self.say("The mean tells us the centre. For the spread, we do what we did with data: "
                      "measure each value's distance from the mean, square it, and average. But now the "
                      "average is weighted by the probabilities.") as tr:
            self.play(FadeIn(ax), FadeIn(b), Create(mu))
            sq = VGroup()
            for y, p in zip(YS, PS):
                d = abs(y - MU) * u
                s = Square(d, stroke_color=RED_, stroke_width=2, fill_color=RED_, fill_opacity=0.12 + 0.6 * p)
                s.move_to(ax.c2p((y + MU) / 2 + X0, 0) + UP * d / 2)
                sq.add(s)
            self.play(LaggedStart(*[GrowFromEdge(s, DOWN) for s in sq], lag_ratio=0.3), run_time=2.5)
            self.fill(tr, 3.5)
        v = MathTex(r"V(Y)=E\big[(Y-\mu)^2\big]\approx0.79", font_size=40).to_corner(UR, buff=0.5)
        s = MathTex(r"\sigma\approx0.89", font_size=40, color=RED_).next_to(v, DOWN, buff=0.3).align_to(v, RIGHT)
        with self.say("The rare day with three outages sits far from the mean, so it has a big square, "
                      "but it only counts with weight five percent. The weighted average of the squares is "
                      "the variance, about point seven nine, and its square root, about point eight nine, "
                      "is the standard deviation.") as tr:
            self.play(Write(v))
            self.play(Write(s))
            self.fill(tr, 2)

    def g_of_y(self):
        q = T("Each outage-day costs a fine of 200 × y² manat.", 34).to_edge(UP, buff=0.6)
        with self.say("Last idea. Suppose the regulator fines the provider two hundred times the square "
                      "of the number of outages, each day. What's the expected fine?") as tr:
            self.play(FadeIn(q))
            self.fill(tr, 1)
        wrong = MathTex(r"g\big(E(Y)\big)=200\times0.75^2=112.5", font_size=42, color=GREY_).shift(UP * 1.2)
        cross = Cross(wrong, stroke_color=RED_, stroke_width=4)
        right = MathTex(r"E\big[g(Y)\big]=\sum_y 200\,y^2\,p(y)=", "270", font_size=44).shift(DOWN * 0.3)
        right[1].set_color(YELLOW_)
        why = T("The bad days cost disproportionately more.", 30, TEAL_).next_to(right, DOWN, buff=0.7)
        with self.say("The tempting shortcut is to plug in the average day: two hundred times point seven "
                      "five squared, one hundred and twelve manat. That's wrong. The right way is to apply "
                      "the fine to every possible day and then average: two hundred and seventy manat. "
                      "Because the fine grows with the square, the bad days cost disproportionately more. "
                      "In general, the expected value of g of Y is not g of the expected value.") as tr:
            self.play(Write(wrong))
            self.play(Create(cross))
            self.play(Write(right), run_time=2)
            self.play(FadeIn(why))
            self.fill(tr, 5)

    def closing(self):
        g = VGroup(
            VGroup(T("expected value", 38, TEAL_), T("balance point, and long-run average", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("variance", 38, RED_), T("probability-weighted average square", 30)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"E[g(Y)]", font_size=44, color=YELLOW_), T("average g over the values, not g of the average", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: the expected value is both the balance point of the probability bars and the "
                      "long-run average. The variance is the probability-weighted average square. And to "
                      "find the expectation of a function, average the function over the values; don't "
                      "apply it to the average.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
