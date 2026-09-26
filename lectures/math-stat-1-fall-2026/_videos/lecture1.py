"""Lecture 1 intuition video: what statistics is (population, sample, parameter, statistic)."""
from common import *


class Lecture1(IntuitionScene):
    parts = ("hook", "population", "many_samples", "sample_size", "frequency", "closing")

    def hook(self):
        q = T("20,000 customers. A new credit card.", 40)
        q2 = T("What share of them would sign up?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("Here's a question a bank faces all the time. It has twenty thousand customers "
                      "and a new credit card. What share of them would sign up? Asking everyone is slow "
                      "and expensive, so instead it asks a few hundred, and hopes the answer carries over.") as tr:
            self.play(FadeIn(q, shift=UP * 0.2))
            self.play(Write(q2), run_time=1.5)
            self.fill(tr, 2.5)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("What is statistics?", 1,
                        "Statistics is the science of when that hope is justified, and how far we can "
                        "trust it.")

    def population(self):
        rng = np.random.default_rng(1)
        self.yes = rng.random(1000) < 0.30
        grid = VGroup(*[Dot(radius=0.055, color=YELLOW_ if y else BLUE_) for y in self.yes])
        grid.arrange_in_grid(25, 40, buff=0.11).move_to(LEFT * 2.2)
        self.grid = grid
        lab = T("the population", 30, GREY_).next_to(grid, UP, buff=0.3)
        key = VGroup(VGroup(Dot(color=YELLOW_), T("would sign up", 26)).arrange(RIGHT, buff=0.2),
                     VGroup(Dot(color=BLUE_), T("would not", 26)).arrange(RIGHT, buff=0.2)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(grid, RIGHT, buff=0.6).shift(UP * 1.2)
        with self.say("Picture the whole population of customers. Each dot is a customer; the yellow "
                      "ones would sign up.") as tr:
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in grid], lag_ratio=0.002, run_time=2.5),
                      FadeIn(lab), FadeIn(key))
            self.fill(tr, 2.5)
        par = MathTex(r"p", "=", r"0.30", font_size=56).next_to(key, DOWN, buff=0.8).align_to(key, LEFT)
        par[2].set_color(YELLOW_)
        pname = T("a parameter", 28, GREY_).next_to(par, DOWN, buff=0.2).align_to(par, LEFT)
        with self.say("The share of yellow dots is one fixed number, here thirty percent. A number "
                      "that describes the whole population is called a parameter.") as tr:
            self.play(Write(par), FadeIn(pname))
            self.fill(tr, 1.5)
        q = MathTex(r"p", "=", r"\,?", font_size=56).move_to(par, aligned_edge=LEFT)
        with self.say("The trouble is that in real life we can't see the colours. The parameter is "
                      "there, but it's hidden from us.") as tr:
            self.play(*[d.animate.set_color(GREY_) for d in grid], FadeOut(key), run_time=1.5)
            self.play(Transform(par, q))
            self.fill(tr, 2.5)
        self.par, self.pname, self.lab = par, pname, lab
        self.sample()

    def sample(self):
        rng = np.random.default_rng(1)
        idx = rng.choice(1000, 50, replace=False)
        k = int(self.yes[idx].sum())
        rings = VGroup(*[Circle(radius=0.1, color=WHITE_, stroke_width=2).move_to(self.grid[i]) for i in idx])
        with self.say("So we pick fifty customers at random, and look only at them.") as tr:
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.03, run_time=2))
            self.play(*[self.grid[i].animate.set_color(YELLOW_ if self.yes[i] else BLUE_) for i in idx])
            self.fill(tr, 3)
        stat = MathTex(r"\hat p", "=", rf"\tfrac{{{k}}}{{50}}", "=", f"{k/50:.2f}", font_size=56)
        stat[4].set_color(YELLOW_)
        stat.next_to(self.pname, DOWN, buff=0.9).align_to(self.pname, LEFT)
        sname = T("a statistic", 28, GREY_).next_to(stat, DOWN, buff=0.2).align_to(stat, LEFT)
        with self.say("Seventeen of them say yes: thirty-four percent. A number computed "
                      "from the sample is called a statistic. It's our window onto the hidden "
                      "parameter.") as tr:
            self.play(Write(stat), FadeIn(sname))
            self.fill(tr, 1.5)

    @staticmethod
    def spoken(k):
        words = {14: "Fourteen", 15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 13: "Thirteen", 12: "Twelve",
                 18: "Eighteen", 19: "Nineteen", 11: "Eleven", 20: "Twenty"}
        return words.get(k, str(k))

    @staticmethod
    def spoken_pct(p):
        words = {22: "twenty-two", 24: "twenty-four", 26: "twenty-six", 28: "twenty-eight", 30: "thirty",
                 32: "thirty-two", 34: "thirty-four", 36: "thirty-six", 38: "thirty-eight", 40: "forty"}
        return words.get(p, str(p))

    def many_samples(self):
        ax = NumberLine(x_range=[0.1, 0.5, 0.1], length=10, include_numbers=True, font_size=28,
                        color=GREY_).shift(DOWN * 2.3)
        cap = T("sample share of yes, from samples of 50", 26, GREY_).next_to(ax, DOWN, buff=0.45)
        rng = np.random.default_rng(3)
        pop = np.random.default_rng(1).random(1000) < 0.30
        vals = [pop[rng.choice(1000, 50, replace=False)].mean() for _ in range(200)]
        with self.say("Now draw another fifty. You get a different answer. And another, and another. "
                      "Each sample tells a slightly different story. The statistic is random. The "
                      "parameter is not.") as tr:
            self.play(Create(ax), FadeIn(cap))
            dots = VGroup()
            counts = {}
            for v in vals[:6]:
                c = counts.get(v, 0)
                d = Dot(ax.n2p(v) + UP * (0.25 + 0.16 * c), radius=0.07, color=YELLOW_)
                counts[v] = c + 1
                lbl = MathTex(f"{v:.2f}", font_size=36, color=YELLOW_).move_to(UP * 1.2)
                self.play(FadeIn(lbl, shift=DOWN * 0.3), run_time=0.35)
                self.play(ReplacementTransform(lbl, d), run_time=0.45)
                dots.add(d)
            self.fill(tr, 6 * 0.8 + 1)
        with self.say("If we repeated this two hundred times, the answers would pile up around one "
                      "value, with some spread.") as tr:
            rest = VGroup()
            for v in vals[6:]:
                c = counts.get(v, 0)
                rest.add(Dot(ax.n2p(v) + UP * (0.25 + 0.16 * c), radius=0.07, color=YELLOW_))
                counts[v] = c + 1
            self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.4) for d in rest], lag_ratio=0.01, run_time=3))
            self.fill(tr, 3)
        true = DashedLine(ax.n2p(0.30) + DOWN * 0.1, ax.n2p(0.30) + UP * 4.3, color=RED_)
        tl = MathTex("p=0.30", font_size=34, color=RED_).next_to(true, UP, buff=0.1)
        with self.say("And the value they pile up around is exactly the hidden parameter, thirty "
                      "percent. A single sample may miss it, but the statistic is aimed at the right "
                      "target.") as tr:
            self.play(Create(true), FadeIn(tl))
            self.fill(tr, 1.5)

    def sample_size(self):
        pop = np.random.default_rng(1).random(20000) < 0.30
        rng = np.random.default_rng(11)

        def pile(n, y0, color):
            ax = NumberLine(x_range=[0.1, 0.5, 0.1], length=10, include_numbers=True, font_size=24,
                            color=GREY_).shift(UP * y0)
            vals = [round(pop[rng.choice(20000, n, replace=False)].mean(), 2) for _ in range(150)]
            counts, g = {}, VGroup()
            for v in vals:
                c = counts.get(v, 0)
                g.add(Dot(ax.n2p(v) + UP * (0.18 + 0.1 * c), radius=0.045, color=color))
                counts[v] = c + 1
            return ax, g
        ax1, g1 = pile(50, 0.6, YELLOW_)
        ax2, g2 = pile(500, -3.0, TEAL_)
        l1 = T("samples of 50", 26, YELLOW_).next_to(ax1, LEFT, buff=0.3).shift(UP * 0.6)
        l2 = T("samples of 500", 26, TEAL_).next_to(ax2, LEFT, buff=0.3).shift(UP * 0.6)
        VGroup(ax1, g1, ax2, g2, l1, l2).move_to(ORIGIN)
        with self.say("Now take bigger samples. Here are a hundred and fifty samples of fifty, and a "
                      "hundred and fifty samples of five hundred.") as tr:
            self.play(Create(ax1), FadeIn(l1), LaggedStart(*[FadeIn(d) for d in g1], lag_ratio=0.01, run_time=2))
            self.play(Create(ax2), FadeIn(l2), LaggedStart(*[FadeIn(d) for d in g2], lag_ratio=0.01, run_time=2))
            self.fill(tr, 4.5)
        rule = MathTex(r"\text{spread}\ \propto\ \frac{1}{\sqrt{n}}", font_size=48, color=WHITE_).to_corner(UL, buff=0.5)
        with self.say("The pile gets much narrower. The spread shrinks roughly like one over the square "
                      "root of the sample size, so four times the data buys you half the uncertainty. "
                      "That is the heart of inferential statistics. A sample can't tell you the "
                      "parameter exactly, but it can tell you how far off you are likely to be.") as tr:
            self.play(Write(rule))
            self.play(Indicate(g2, color=TEAL_, scale_factor=1.05), run_time=1.5)
            self.fill(tr, 3)

    def frequency(self):
        rng = np.random.default_rng(5)
        up = rng.random(400) < 0.53
        rf = np.cumsum(up) / np.arange(1, 401)
        ax = Axes(x_range=[0, 400, 100], y_range=[0, 1, 0.25], x_length=10, y_length=4.5, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.4)
        xl = T("trading days observed", 24, GREY_).next_to(ax, DOWN, buff=0.3)
        yl = T("share of up days so far", 24, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        k = ValueTracker(1)
        path = always_redraw(lambda: ax.plot_line_graph(np.arange(1, int(k.get_value()) + 1),
                                                        rf[:int(k.get_value())], add_vertex_dots=False,
                                                        line_color=YELLOW_, stroke_width=3))
        with self.say("One more idea, which sets up the rest of the course. Count how often something "
                      "happens, say a stock closing up, and divide by the number of days. That's a "
                      "relative frequency.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.add(path)
            self.play(k.animate.set_value(30), run_time=2)
            self.fill(tr, 3)
        line = DashedLine(ax.c2p(0, 0.53), ax.c2p(400, 0.53), color=TEAL_)
        with self.say("Track it as the days pile up. At first it jumps around wildly. Then it wobbles "
                      "less and less, and settles near one value. That settling value is what we will "
                      "call a probability, starting next lecture.") as tr:
            self.play(k.animate.set_value(400), run_time=7, rate_func=linear)
            self.play(Create(line))
            self.fill(tr, 8)

    def closing(self):
        a = VGroup(T("population", 36, BLUE_), MathTex(r"\longrightarrow", font_size=40), T("parameter", 36, BLUE_),
                   T("(fixed, hidden)", 26, GREY_)).arrange(RIGHT, buff=0.35)
        b = VGroup(T("sample", 36, YELLOW_), MathTex(r"\longrightarrow", font_size=40), T("statistic", 36, YELLOW_),
                   T("(random, visible)", 26, GREY_)).arrange(RIGHT, buff=0.35)
        g = VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.6).shift(UP * 0.5)
        q = T("Reason from the part you can see to the whole you can't.", 34, TEAL_).to_edge(DOWN, buff=1.0)
        with self.say("So, two pairs of words to keep. A population has parameters: fixed, but hidden. "
                      "A sample has statistics: random, but visible. Statistics is the art of reasoning "
                      "from the part you can see to the whole you can't.") as tr:
            self.play(FadeIn(a, shift=RIGHT * 0.3))
            self.play(FadeIn(b, shift=RIGHT * 0.3))
            self.play(Write(q), run_time=2)
            self.fill(tr, 4)
