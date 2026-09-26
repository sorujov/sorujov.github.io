"""Lecture 12 intuition video: waiting times — geometric (memoryless) and negative binomial."""
from common import *
from math import comb

P = 0.2


class Lecture12(IntuitionScene):
    parts = ("hook", "geometric", "memoryless", "negbin", "closing")

    def hook(self):
        q = T("Each exploration well strikes oil with probability 0.2.", 38)
        q2 = T("How many wells until the first strike?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("An oil company drills exploration wells one after another. Each well strikes oil "
                      "with probability twenty percent, independently. How many wells will it take to "
                      "get the first strike? This time we don't fix the number of trials; we wait.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Waiting for success", 12,
                        "Two distributions describe waiting: the geometric, for the first success, and "
                        "the negative binomial, for the r-th.")

    def axes(self, ymax=0.25):
        return Axes(x_range=[0, 21, 5], y_range=[0, ymax, 0.05], x_length=10, y_length=4.2, tips=False,
                    axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.6)

    def geo_bars(self, ax, start=1, color=YELLOW_):
        return VGroup(*[Rectangle(width=0.32, height=(1 - P) ** (y - 1) * P * ax.y_axis.get_unit_size(), stroke_width=0,
                                  fill_color=color, fill_opacity=0.85).move_to(ax.c2p(y, 0), aligned_edge=DOWN)
                        for y in range(start, 21)])

    def geometric(self):
        path = VGroup(*[T(c, 34, RED_ if c == "F" else GREEN_) for c in "FFFS"]).arrange(RIGHT, buff=0.25).to_edge(UP, buff=0.7)
        pr = MathTex(r"P(Y=4)=0.8\times0.8\times0.8\times0.2", font_size=40).next_to(path, DOWN, buff=0.3)
        with self.say("For the first strike to come on the fourth well, the first three must be dry and "
                      "the fourth must hit: point eight, times point eight, times point eight, times point "
                      "two.") as tr:
            self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in path], lag_ratio=0.4))
            self.play(Write(pr))
            self.fill(tr, 3)
        ax = self.axes()
        b = self.geo_bars(ax)
        f = MathTex(r"p(y)=q^{\,y-1}p", font_size=44, color=YELLOW_).to_corner(UR, buff=0.6).shift(DOWN * 1.3)
        m = MathTex(r"E(Y)=\frac{1}{p}=5", font_size=44, color=TEAL_).next_to(f, DOWN, buff=0.4).align_to(f, LEFT)
        with self.say("In general, the chance the first success comes on well y is q to the y minus one, "
                      "times p. Each bar is eighty percent of the one before it, so the bars decay "
                      "geometrically, which is where the name comes from. On average you wait one over p "
                      "wells: five.") as tr:
            self.play(Create(ax), LaggedStart(*[GrowFromEdge(x, DOWN) for x in b], lag_ratio=0.08), run_time=3)
            self.play(Write(f))
            self.play(Write(m))
            self.fill(tr, 5)

    def memoryless(self):
        ax = self.axes()
        b = self.geo_bars(ax)
        self.add(ax, b)
        q = T("Five dry wells in a row. Is a strike now 'due'?", 34, YELLOW_).to_edge(UP, buff=0.6)
        with self.say("Now a subtle point. Suppose the first five wells have all been dry. Is a strike now "
                      "due? Many people feel it must be.") as tr:
            self.play(FadeIn(q))
            self.play(*[b[k].animate.set_opacity(0.15) for k in range(5)])
            self.fill(tr, 1.5)
        rest = VGroup(*b[5:]).copy()
        with self.say("Throw away the first five bars, and stretch what's left so it adds up to one again. "
                      "That's conditioning. And look: the stretched bars are exactly the original "
                      "distribution, just shifted along by five. The process has no memory. After any "
                      "number of failures, the wait ahead looks exactly like a fresh start.") as tr:
            self.play(rest.animate.shift(LEFT * 5 * ax.x_axis.get_unit_size()).stretch(1 / 0.8 ** 5, 1, about_edge=DOWN).set_color(TEAL_), run_time=3)
            self.play(Indicate(rest, color=TEAL_, scale_factor=1.03))
            self.fill(tr, 5)
        ml = MathTex(r"P(Y>a+b\mid Y>a)=P(Y>b)", font_size=40, color=TEAL_).next_to(q, DOWN, buff=0.4)
        with self.say("In symbols: the chance of waiting b more, given you've already waited a, is just the "
                      "chance of waiting b. For independent trials, luck doesn't accumulate.") as tr:
            self.play(Write(ml))
            self.fill(tr, 1.5)

    def negbin(self):
        r = 3
        ax = Axes(x_range=[0, 41, 5], y_range=[0, 0.08, 0.02], x_length=10, y_length=4, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(DOWN * 0.8)
        b = VGroup(*[Rectangle(width=0.16, height=comb(y - 1, r - 1) * P ** r * (1 - P) ** (y - r) * ax.y_axis.get_unit_size(),
                               stroke_width=0, fill_color=PURPLE_, fill_opacity=0.85).move_to(ax.c2p(y, 0), aligned_edge=DOWN)
                     for y in range(r, 41)])
        path = VGroup(*[T(c, 30, RED_ if c == "F" else GREEN_) for c in "FFSFFFSFS"]).arrange(RIGHT, buff=0.18).to_edge(UP, buff=0.6)
        with self.say("What if the company needs three successful wells, not one? Then it waits for the "
                      "third success. The last well must be a strike, and among the earlier wells exactly "
                      "two are strikes, in any order.") as tr:
            self.play(LaggedStart(*[FadeIn(c) for c in path], lag_ratio=0.15))
            self.play(Indicate(path[-1], color=GREEN_, scale_factor=1.4))
            self.fill(tr, 3)
        f = MathTex(r"p(y)=\binom{y-1}{r-1}p^{r}q^{\,y-r}", font_size=42, color=PURPLE_).next_to(path, DOWN, buff=0.4)
        m = MathTex(r"E(Y)=\frac{r}{p}=15", font_size=40, color=TEAL_).to_corner(UR, buff=0.6).shift(DOWN * 1.8)
        with self.say("That gives the negative binomial. Its shape is a smoother hump, and its mean is r "
                      "over p, fifteen wells. That makes sense: waiting for three successes is like three "
                      "geometric waits, one after another, each averaging five.") as tr:
            self.play(Write(f))
            self.play(Create(ax), LaggedStart(*[GrowFromEdge(x, DOWN) for x in b], lag_ratio=0.03), run_time=3)
            self.play(Write(m))
            self.fill(tr, 5)

    def closing(self):
        g = VGroup(
            VGroup(T("geometric", 38, YELLOW_), T("wait for the first success; mean 1/p", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("memoryless", 38, TEAL_), T("past failures don't make success 'due'", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("negative binomial", 38, PURPLE_), T("wait for the r-th success; mean r/p", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: the geometric counts the wait for a first success, with mean one over p. It "
                      "has no memory, so a success is never 'due'. And the negative binomial counts the "
                      "wait for the r-th success, with mean r over p.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
