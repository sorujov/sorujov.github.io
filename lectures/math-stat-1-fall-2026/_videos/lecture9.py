"""Lecture 9 intuition video: a random variable is a function on S; simple random sampling and n/N."""
from common import *
from itertools import product

P_D = 0.2


class Lecture9(IntuitionScene):
    parts = ("hook", "mapping", "distribution", "sampling", "closing")

    def hook(self):
        q = T("Three small-business loans. Each may default.", 40)
        q2 = T("How many defaults will there be?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A bank holds three loans to small businesses. Each one may default this year, "
                      "independently, with probability twenty percent. The bank doesn't care exactly "
                      "which loans default. It cares how many.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Random variables", 9,
                        "Turning outcomes into numbers is what a random variable does. And despite the "
                        "name, it is neither random nor a variable.")

    def mapping(self):
        outs = ["".join(p) for p in product("ND", repeat=3)]
        self.outs = outs
        cells = VGroup()
        for o in outs:
            r = RoundedRectangle(corner_radius=0.1, width=1.35, height=0.62, color=GREY_)
            txt = VGroup(*[T(c, 26, RED_ if c == "D" else TEAL_) for c in o]).arrange(RIGHT, buff=0.12).move_to(r)
            cells.add(VGroup(r, txt))
        cells.arrange(DOWN, buff=0.13).shift(LEFT * 4.2)
        S = T("S: 8 outcomes", 28, BLUE_).next_to(cells, UP, buff=0.25)
        key = T("D = default,  N = no default", 22, GREY_).next_to(cells, DOWN, buff=0.2)
        with self.say("The sample space lists which loans default: no defaults, the first only, and so "
                      "on, eight outcomes in all.") as tr:
            self.play(FadeIn(S), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in cells], lag_ratio=0.08), FadeIn(key))
            self.fill(tr, 2)
        nl = NumberLine(x_range=[0, 3, 1], length=1, rotation=0, include_numbers=False).set_opacity(0)
        vals = VGroup(*[Circle(radius=0.38, color=YELLOW_).move_to([2.3, 2.1 - 1.4 * y, 0]) for y in range(4)])
        vl = VGroup(*[MathTex(str(y), font_size=40, color=YELLOW_).move_to(v) for y, v in enumerate(vals)])
        Y = MathTex("Y", font_size=48, color=YELLOW_).next_to(vals, UP, buff=0.3)
        arrows = VGroup(*[Arrow(c.get_right(), vals[o.count("D")].get_left(), buff=0.08, stroke_width=2,
                                color=GREY_, max_tip_length_to_length_ratio=0.05) for c, o in zip(cells, outs)])
        with self.say("A random variable Y is a rule that sends each outcome to a number: here, the "
                      "number of D's. Every outcome gets exactly one arrow. That's all it is: a function "
                      "from the sample space to the real line. The randomness comes from the outcome, not "
                      "from the rule.") as tr:
            self.play(FadeIn(vals), FadeIn(vl), Write(Y))
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.2), run_time=3)
            self.fill(tr, 4)
        self.cells, self.vals, self.arrows, self.vl, self.Y, self.S, self.key = cells, vals, arrows, vl, Y, S, key

    def distribution(self):
        self.add(self.cells, self.vals, self.arrows, self.vl, self.Y, self.S, self.key)
        probs = [(P_D ** o.count("D")) * ((1 - P_D) ** (3 - o.count("D"))) for o in self.outs]
        plab = VGroup(*[MathTex(f"{p:.3f}", font_size=24, color=GREY_).next_to(c, LEFT, buff=0.15)
                        for p, c in zip(probs, self.cells)])
        with self.say("Each outcome carries a probability. No defaults at all: point eight cubed, about "
                      "point five one. Any single default pattern: point one two eight. And so on.") as tr:
            self.play(FadeIn(plab, shift=RIGHT * 0.1))
            self.fill(tr, 1)
        py = [sum(p for p, o in zip(probs, self.outs) if o.count("D") == y) for y in range(4)]
        bars = VGroup()
        for y in range(4):
            b = Rectangle(width=py[y] * 4, height=0.55, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.8)
            b.next_to(self.vals[y], RIGHT, buff=0.3)
            bars.add(b)
        bl = VGroup(*[MathTex(f"{py[y]:.3f}", font_size=30).next_to(bars[y], RIGHT, buff=0.15) for y in range(4)])
        cap = MathTex(r"P(Y=y)", font_size=40, color=YELLOW_).next_to(bars, UP, buff=0.3).align_to(bars, LEFT)
        with self.say("To get the probability that Y equals a particular value, follow the arrows "
                      "backwards and add up the probability of every outcome that lands there. Three "
                      "outcomes land on one, so P of Y equals one is three times point one two eight: "
                      "about point three eight. That list of values and probabilities is the distribution "
                      "of Y.") as tr:
            for y in range(4):
                idx = [k for k, o in enumerate(self.outs) if o.count("D") == y]
                self.play(*[Indicate(self.cells[k], color=YELLOW_, scale_factor=1.05) for k in idx],
                          *[self.arrows[k].animate.set_color(YELLOW_) for k in idx], run_time=0.8)
                self.play(GrowFromEdge(bars[y], LEFT), FadeIn(bl[y]), run_time=0.8)
                self.play(*[self.arrows[k].animate.set_color(GREY_) for k in idx], run_time=0.3)
            self.play(FadeIn(cap))
            self.fill(tr, 8.5)
        loss = MathTex(r"L=50{,}000\times Y\ \text{AZN}", font_size=36, color=TEAL_).to_edge(DOWN, buff=0.4).shift(RIGHT * 2.5)
        with self.say("And nothing stops us defining other functions on the same sample space, like the "
                      "loss in manat, fifty thousand for each default. Same outcomes, a different "
                      "random variable.") as tr:
            self.play(Write(loss))
            self.fill(tr, 1.5)

    def sampling(self):
        N, n = 20, 5
        br = VGroup(*[Square(0.62, color=BLUE_, fill_opacity=0.15) for _ in range(N)]).arrange_in_grid(4, 5, buff=0.18).shift(LEFT * 3.6)
        brl = VGroup(*[T(str(i + 1), 20, BLUE_).move_to(b) for i, b in enumerate(br)])
        cap = T("20 branches; audit 5", 28, BLUE_).next_to(br, UP, buff=0.3)
        with self.say("Randomness also enters through how we collect data. An auditor must visit five of "
                      "a bank's twenty branches. A simple random sample means every set of five branches "
                      "is equally likely to be the one chosen.") as tr:
            self.play(FadeIn(br), FadeIn(brl), FadeIn(cap))
            self.fill(tr, 1)
        rng = np.random.default_rng(9)
        counts = np.zeros(N)
        ax = Axes(x_range=[0, 21, 5], y_range=[0, 0.5, 0.25], x_length=6.2, y_length=3.2, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(RIGHT * 3.4 + UP * 0.2)
        yl = T("share of samples containing each branch", 22, GREY_).next_to(ax, UP, buff=0.2)
        quarter = DashedLine(ax.c2p(0, 0.25), ax.c2p(21, 0.25), color=YELLOW_)
        k = ValueTracker(0)
        hist = [np.zeros(N)]

        def bars():
            m = max(int(k.get_value()), 1)
            return VGroup(*[Rectangle(width=0.2, height=max(hist[0][i] / m, 0.001) * 3.2 / 0.5, stroke_width=0,
                                      fill_color=BLUE_, fill_opacity=0.8).move_to(ax.c2p(i + 1, 0), aligned_edge=DOWN)
                            for i in range(N)])
        with self.say("Draw such a sample a few times, and keep track of how often each branch gets "
                      "picked.") as tr:
            self.play(Create(ax), FadeIn(yl))
            for rep in range(4):
                s = rng.choice(N, n, replace=False)
                hist[0][s] += 1
                k.set_value(rep + 1)
                self.play(*[br[i].animate.set_fill(YELLOW_, 0.7) for i in s], run_time=0.4)
                b = bars()
                self.add(b)
                self.wait(0.4)
                self.remove(b)
                self.play(*[br[i].animate.set_fill(BLUE_, 0.15) for i in s], run_time=0.3)
            self.fill(tr, 4.4)
        for rep in range(4, 2000):
            hist[0][rng.choice(N, n, replace=False)] += 1
        k.set_value(2000)
        b = bars()
        lbl = MathTex(r"\frac{n}{N}=\frac{5}{20}=0.25", font_size=40, color=YELLOW_).next_to(ax, DOWN, buff=0.5)
        with self.say("After two thousand samples, every branch has been chosen in about a quarter of "
                      "them. That's no accident: under simple random sampling, each unit's chance of "
                      "being included is n over N, five out of twenty. No branch is favoured, which is "
                      "exactly what makes the sample fair.") as tr:
            self.play(FadeIn(b), Create(quarter))
            self.play(Write(lbl))
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("random variable", 38, YELLOW_), T("a function from outcomes to numbers", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("its distribution", 38, TEAL_), T("follow the arrows back and add", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("simple random sample", 38, BLUE_), T("each unit included with chance n/N", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: a random variable is a function that turns outcomes into numbers. Its "
                      "distribution comes from following the arrows back and adding up probability. And a "
                      "simple random sample gives every unit the same chance, n over N, of being "
                      "included.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
