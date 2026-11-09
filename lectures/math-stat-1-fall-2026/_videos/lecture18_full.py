"""Lecture 18, full lecture video: expected values for continuous random variables;
the uniform distribution (Wackerly §§4.3–4.4).

A narrated walk through the whole deck, for students who did not have the class. The short
intuition clip is lecture18.py; this one follows the slides and works every example.
"""
import csv
import math
import random

from common import *

ORANGE_ = "#FF9F43"
STEEL_ = "#8BA3C7"


def TX(s, font_size=36, color=WHITE_, max_w=12.8):
    """Tex on one line (no paragraph wrapping), shrunk to fit the frame if needed."""
    t = Tex(r"\mbox{" + s + "}", font_size=font_size, color=color)
    if t.width > max_w:
        t.scale_to_fit_width(max_w)
    return t


def box(title, lines, color=BLUE_, width=11.5, size=36):
    """A callout: coloured title, then lines of Tex, framed."""
    head = T(title, 28, color)
    body = VGroup(*[TX(s, font_size=size, max_w=12.0) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    g = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    frame = SurroundingRectangle(g, color=color, buff=0.35, corner_radius=0.12, stroke_width=2.5)
    frame.set_fill(color, opacity=0.06)
    return VGroup(frame, g)


def capw(m, w):
    """Shrink a mobject to width w if it is wider."""
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def keep(g, top=2.6, bottom=-3.75, max_w=13.4):
    """Scale and shift a laid-out group so it sits inside the body area of the frame."""
    if g.width > max_w:
        g.scale_to_fit_width(max_w)
    if g.height > top - bottom:
        g.scale_to_fit_height(top - bottom)
    if g.get_top()[1] > top:
        g.shift(DOWN * (g.get_top()[1] - top))
    if g.get_bottom()[1] < bottom:
        g.shift(UP * (bottom - g.get_bottom()[1]))
    if g.get_right()[0] > 6.8:
        g.shift(LEFT * (g.get_right()[0] - 6.8))
    if g.get_left()[0] < -6.8:
        g.shift(RIGHT * (-6.8 - g.get_left()[0]))
    return g


def fit(m, w, h, max_scale=3.0):
    """Scale m (up or down) to the largest size that fits a w x h region."""
    m.scale(min(w / m.width, h / m.height, max_scale))
    return m


def fill(g, top=2.5, bottom=-3.55, max_w=13.2, max_scale=1.6):
    """Scale a laid-out group up to fill the body area below the title rule, and centre it there."""
    fit(g, max_w, top - bottom, max_scale)
    g.move_to([0, (top + bottom) / 2, 0])
    return g


def arect(ax, x0, x1, h, color, opacity=0.6, stroke=0):
    """A filled rectangle over [x0, x1] x [0, h] in the coordinates of ax."""
    p0, p1 = ax.c2p(x0, 0), ax.c2p(x1, h)
    r = Rectangle(width=abs(p1[0] - p0[0]), height=abs(p1[1] - p0[1]), fill_color=color, fill_opacity=opacity,
                  stroke_color=color, stroke_width=stroke)
    return r.move_to([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0])


def worst_day_positions(path="sp500.csv"):
    """Position in (0,1) of each calendar month's largest |log return| (months with >= 5 returns)."""
    rows = [r for r in csv.reader(open(path))][1:]
    d = [(r[0], float(r[1])) for r in rows if len(r) > 1 and r[1] not in (".", "")]
    by = {}
    for (_, a), (day, b) in zip(d, d[1:]):
        by.setdefault(day[:7], []).append(math.log(b / a))
    out = []
    for m in sorted(by):
        x = by[m]
        n = len(x)
        if n < 5:
            continue
        k = max(range(n), key=lambda i: abs(x[i]))
        out.append((k + 1 - 0.5) / n)
    return out


class Lecture18Full(IntuitionScene):
    parts = ("intro", "where", "motivate", "definition", "theorems", "reserve", "computer_check",
             "linear_cost", "window", "length", "theorem46", "low_bid", "rounding", "delayed", "convex",
             "tps", "case_study", "check", "formulas", "summary", "practice", "closing")

    # --------------------------------------------------------------- helpers
    def title_card(self, title, lecture, text):
        t = T(title, 54)
        t.scale_to_fit_width(13.0)
        t.shift(UP * 0.4)
        sub = T(f"Mathematical Statistics I  ·  Lecture {lecture}  ·  Wackerly §§4.3–4.4", 36, GREY_)
        fit(sub, 11.5, 0.6, 1.0).next_to(t, DOWN, buff=0.6)
        with self.say(text) as tr:
            self.play(Write(t), run_time=2)
            self.play(FadeIn(sub))
            self.done(tr)

    def done(self, tr):
        self.wait(max(tr.get_remaining_duration(), 0.25))

    def head(self, s, color=YELLOW_):
        h = T(s, 38, color).to_edge(UP, buff=0.4)
        if h.width > 12.8:
            h.scale_to_fit_width(12.8)
        rule = Line(LEFT * 6.6, RIGHT * 6.6, color=DIM, stroke_width=2).next_to(h, DOWN, buff=0.18)
        self.play(FadeIn(h, shift=DOWN * 0.15), Create(rule), run_time=0.7)
        return VGroup(h, rule)

    # --------------------------------------------------------------- 1
    def intro(self):
        self.title_card("Continuous Expectation and the Uniform Distribution", 18,
                        "Hello everyone. This is lecture eighteen of Mathematical Statistics One: expected "
                        "values for continuous random variables, and the uniform distribution. It covers "
                        "Wackerly sections four point three and four point four. The video follows the "
                        "slides on the course page, so keep them open if you like, and pause whenever you "
                        "want to try a step yourself.")

    def where(self):
        hd = self.head("Where we are")
        last = VGroup(
            T("Last lecture", 28, GREY_),
            MathTex(r"F(y)=P(Y\le y)", font_size=40),
            MathTex(r"f(y)=\frac{dF(y)}{dy}", font_size=40),
            MathTex(r"P(a\le Y\le b)=\int_a^b f(y)\,dy=F(b)-F(a)", font_size=40, color=TEAL_),
        ).arrange(DOWN, buff=0.32)
        rule = MathTex(r"\sum_y\ \longrightarrow\ \int", r"\qquad\qquad", r"p(y)\ \longrightarrow\ f(y)\,dy",
                       font_size=46, color=YELLOW_)
        today = T("Today: the mean and the variance, then the uniform distribution", 30)
        g = VGroup(rule, today).arrange(DOWN, buff=0.4)
        last[0].scale(1.15)
        today.scale(1.15)
        fill(VGroup(last, g).arrange(DOWN, buff=0.6))
        with self.say("Last time we opened chapter four with the distribution function, capital F of y, "
                      "and the density, small f of y, which is its derivative. A density is a height, not "
                      "a probability. Probabilities are areas: the probability that Y lies between a and b "
                      "is F of b minus F of a.") as tr:
            self.play(FadeIn(last[0]))
            self.play(Write(last[1]))
            self.wait(1.5)
            self.play(Write(last[2]))
            self.wait(4)
            self.play(Write(last[3]), run_time=2)
            self.done(tr)
        with self.say("Chapter three went the same way: first the distribution, then the mean and the "
                      "variance that summarise it. Today we take that second step for continuous "
                      "variables. The rule is one substitution: sums become integrals, and p of y becomes "
                      "f of y, d y. Then we meet the first named continuous model, the simplest there is: "
                      "the uniform.") as tr:
            self.wait(7)
            self.play(Write(rule[0]))
            self.wait(1)
            self.play(Write(rule[2]))
            self.wait(2)
            self.play(FadeIn(today, shift=UP * 0.2))
            self.done(tr)

    # --------------------------------------------------------------- 2
    def motivate(self):
        hd = self.head("A motivating question")
        b = box("The procurement desk's problem",
                [r"A plant waits for a replacement turbine part.",
                 r"Delivery takes between 1 and 5 days, any time equally likely.",
                 r"Lost output costs $2000+150\,Y^2$ AZN, where $Y$ is the delay in days.",
                 r"What should the budget line say the part will cost \emph{on average}?"], RED_, size=36)
        plug = MathTex(r"\text{average delay } 3 \text{ days:}\quad 2000+150\times3^2=3350\ \text{AZN}", font_size=42)
        low = T("Too low. By how much?", 34, YELLOW_)
        g = VGroup(plug, low).arrange(DOWN, buff=0.35)
        low.scale(1.15)
        fill(VGroup(b, g).arrange(DOWN, buff=0.5))
        with self.say("Here is the question for today. A plant is waiting for a replacement turbine part. "
                      "Delivery takes between one and five days, and any time in that range is equally "
                      "likely. Lost output costs two thousand manat, plus one hundred and fifty manat "
                      "times the square of the delay in days. What should the budget line say the part "
                      "will cost on average?") as tr:
            self.play(FadeIn(b[0]), FadeIn(b[1][0]))
            for ln in b[1][1]:
                self.play(FadeIn(ln, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(2.6)
            self.done(tr)
        with self.say("The tempting answer plugs in the average delay, three days: two thousand plus one "
                      "hundred and fifty times nine, which is three thousand three hundred and fifty manat. "
                      "By the end of this lecture we will see that this number is too low, and by exactly "
                      "how much.") as tr:
            self.play(Write(plug), run_time=2.5)
            self.wait(6)
            self.play(FadeIn(low, shift=UP * 0.2))
            self.done(tr)

    # --------------------------------------------------------------- 3
    def definition(self):
        self.head("Definition 4.5: expected value")
        d = box("Definition 4.5",
                [r"The expected value of a continuous random variable $Y$ is",
                 r"$\displaystyle E(Y)=\int_{-\infty}^{\infty} y\,f(y)\,dy$,\quad provided that the integral exists."],
                BLUE_)
        fill(d, max_w=12.8)
        with self.say("Definition four point five. The expected value of a continuous random variable Y is "
                      "the integral, over the whole real line, of y times f of y, d y, provided that the "
                      "integral exists.") as tr:
            self.play(FadeIn(d, shift=UP * 0.2))
            self.done(tr)
        self.play(FadeOut(d), run_time=0.6)

        def f(x):
            return x * math.exp(-x / 1.5) / 2.25

        ax = Axes(x_range=[0, 12, 2], y_range=[0, 0.3, 0.1], x_length=7.0, y_length=4.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 30},
                  x_axis_config={"numbers_to_include": [2, 4, 6, 8, 10, 12]}).move_to([-3.0, -0.6, 0])
        yl = MathTex("y", font_size=40, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.15)
        fl = MathTex("f(y)", font_size=40, color=GREY_).next_to(ax.c2p(0, 0.3), RIGHT, buff=0.2)
        ux, uy = ax.x_axis.get_unit_size(), ax.y_axis.get_unit_size()

        def bars(w):
            g = VGroup()
            for i in range(int(round(12 / w))):
                a = i * w
                g.add(Rectangle(width=w * ux, height=max(f(a + w / 2) * uy, 0.002),
                                stroke_width=1 if w > 0.3 else 0, stroke_color=BG, fill_color=BLUE_,
                                fill_opacity=0.8).move_to(ax.c2p(a, 0), aligned_edge=DL))
            return g

        b = bars(1)
        one = b[3].copy().set_fill(YELLOW_, opacity=1)
        s0 = VGroup(T("one slice has probability", 32, GREY_),
                    MathTex(r"\approx f(y_i)\,\Delta y", font_size=50, color=YELLOW_)).arrange(DOWN, buff=0.2)
        s1 = MathTex(r"E(Y)\approx\sum_i y_i\,f(y_i)\,\Delta y", font_size=44)
        s2 = MathTex(r"E(Y)=\int y\,f(y)\,dy", font_size=52, color=YELLOW_)
        s3 = MathTex(r"p(y)\ \leftrightarrow\ f(y)\,dy", font_size=48, color=TEAL_)
        col = VGroup(s0, s1, s2, s3).arrange(DOWN, buff=0.55)
        fit(col, 5.4, 5.6, 1.0).move_to([3.95, -0.5, 0])
        with self.say("Where does it come from? Cut the axis into thin slices. The probability that Y "
                      "lands in one slice is about its area: the height f of y, times the width, delta y. "
                      "So each slice behaves like one value of a discrete variable, and the mean is about "
                      "the sum of value times probability.") as tr:
            self.play(Create(ax), FadeIn(yl), FadeIn(fl))
            self.play(LaggedStart(*[GrowFromEdge(x, DOWN) for x in b], lag_ratio=0.08), run_time=1.8)
            self.play(FadeIn(one), FadeIn(s0), run_time=0.8)
            self.wait(6)
            self.play(Write(s1), run_time=2)
            self.done(tr)
        curve = ax.plot(f, x_range=[0, 12], color=YELLOW_, stroke_width=4)
        with self.say("Now make the slices thinner and thinner. The sum turns into an integral. So f of y, "
                      "d y plays the role that p of y played in chapter three, and the integral adds up "
                      "value times probability over all the slices.") as tr:
            self.play(FadeOut(one), run_time=0.4)
            for w in (0.5, 0.25, 0.1):
                self.play(Transform(b, bars(w)), run_time=1.3)
            self.play(Create(curve), Write(s2), run_time=1.5)
            self.wait(1.5)
            self.play(Write(s3))
            self.done(tr)
        ex = VGroup(T('"Exists" means', 32, GREY_),
                    MathTex(r"\int_{-\infty}^{\infty}|y|\,f(y)\,dy<\infty", font_size=42)).arrange(DOWN, buff=0.18)
        fit(ex, 5.4, s0.height + 0.35, 1.0).move_to(s0)
        with self.say("One remark on the word exists. It means that the integral of the absolute value of "
                      "y, times f of y, is finite. Every model in this course passes that test.") as tr:
            self.play(FadeOut(s0), run_time=0.4)
            self.play(FadeIn(ex, shift=UP * 0.2))
            self.done(tr)

    def theorems(self):
        hd = self.head("Theorems 4.4 and 4.5")
        t1 = box("Theorem 4.4",
                 [r"Let $g(Y)$ be a function of $Y$. Then\ \ $\displaystyle E[g(Y)]=\int_{-\infty}^{\infty} g(y)\,f(y)\,dy$."],
                 YELLOW_, size=36)
        t2 = box("Theorem 4.5",
                 [r"For a constant $c$ and functions $g, g_1,\ldots,g_k$ of $Y$:",
                  r"$E(c)=c,\qquad E[c\,g(Y)]=c\,E[g(Y)],\qquad E\Big[\sum_{i=1}^{k} g_i(Y)\Big]=\sum_{i=1}^{k}E[g_i(Y)]$"],
                 TEAL_, size=34)
        v = MathTex(r"g(Y)=(Y-\mu)^2:\qquad", r"V(Y)=E\big[(Y-\mu)^2\big]=E(Y^2)-\mu^2", font_size=40)
        v[1].set_color(YELLOW_)
        g = fill(VGroup(t1, t2, v).arrange(DOWN, buff=0.4))
        with self.say("Theorem four point four. If g of Y is any function of Y, then its expected value is "
                      "the integral of g of y times f of y. You do not need the distribution of g of Y; "
                      "you weight g by the density of Y.") as tr:
            self.play(FadeIn(t1, shift=UP * 0.2))
            self.done(tr)
        with self.say("Theorem four point five says that expectation is linear. The expected value of a "
                      "constant is that constant. A constant factor comes outside. And the expected value "
                      "of a sum is the sum of the expected values.") as tr:
            self.play(FadeIn(t2, shift=UP * 0.2))
            self.done(tr)
        with self.say("Take g to be Y minus mu, squared, expand it, and these two theorems give the "
                      "shortcut we know from chapter three: the variance is E of Y squared, minus mu "
                      "squared.") as tr:
            self.play(Write(v[0]))
            self.wait(2)
            self.play(Write(v[1]), run_time=2)
            self.done(tr)

    # --------------------------------------------------------------- 4
    def reserve(self):
        hd = self.head("Worked example: reserve power")
        setup = TX(r"Reserve power for $Y$ hours, $0\le Y\le2$, with density $f(y)=\tfrac38\,y^2$ "
                   r"(Wackerly, Example 4.6)", font_size=44)
        fit(setup, 13.0, 0.75, 1.0).next_to(hd, DOWN, buff=0.25)
        ax = Axes(x_range=[0, 2.3, 1], y_range=[0, 1.7, 0.5], x_length=4.2, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 30},
                  x_axis_config={"numbers_to_include": [1, 2]}).move_to([-4.4, -0.95, 0])
        yl = MathTex("y", font_size=38, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.12)
        cur = ax.plot(lambda y: 0.375 * y * y, x_range=[0, 2], color=YELLOW_, stroke_width=4)
        area = ax.get_area(cur, x_range=[0, 2], color=BLUE_, opacity=0.45)
        drop = Line(ax.c2p(2, 0), ax.c2p(2, 1.5), color=YELLOW_, stroke_width=4)
        fl = MathTex(r"f(y)=\tfrac38 y^2", font_size=40, color=YELLOW_).next_to(ax.c2p(0.85, 1.2), UP, buff=0.05)
        l1 = MathTex(r"E(Y)=\int_0^2 y\cdot\tfrac38 y^2\,dy", r"=\tfrac38\cdot\tfrac{y^4}{4}\Big|_0^2", r"=\tfrac38\cdot4",
                     r"=1.5\ \text{hours}", font_size=38)
        l2 = MathTex(r"E(Y^2)=\int_0^2 y^2\cdot\tfrac38 y^2\,dy", r"=\tfrac38\cdot\tfrac{y^5}{5}\Big|_0^2",
                     r"=\tfrac38\cdot\tfrac{32}{5}", r"=2.4", font_size=38)
        l3 = VGroup(MathTex(r"\sigma^2=2.4-1.5^2=0.15", font_size=38),
                    MathTex(r"\sigma=0.387\ \text{hours}\approx23\ \text{minutes}", font_size=38)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        l1[3].set_color(TEAL_)
        l2[3].set_color(TEAL_)
        l3.set_color(YELLOW_)
        lines = VGroup(l1, l2, l3).arrange(DOWN, aligned_edge=LEFT, buff=0.75)
        fit(lines, 8.2, 5.2).move_to([2.55, -0.9, 0])
        with self.say("A worked example; it is Wackerly's example four point six. On a winter evening a "
                      "grid operator must buy reserve power for Y hours, where Y is between zero and two, "
                      "with density three eighths y squared. The density rises, so long shortfalls are the "
                      "likely ones.") as tr:
            self.play(FadeIn(setup))
            self.play(Create(ax), FadeIn(yl))
            self.play(Create(cur), FadeIn(fl), run_time=1.5)
            self.play(FadeIn(area), Create(drop))
            self.done(tr)
        tri = Triangle(color=TEAL_, fill_opacity=1).scale(0.15).next_to(ax.c2p(1.5, 0), DOWN, buff=0.12)
        with self.say("The mean is the integral from zero to two of y times three eighths y squared. That "
                      "is three eighths, times y to the fourth over four, evaluated from zero to two: "
                      "three eighths times four, which is one point five hours.") as tr:
            self.play(Write(l1[0]), run_time=2)
            self.wait(2.5)
            self.play(Write(l1[1]), run_time=1.5)
            self.wait(2.5)
            self.play(Write(l1[2]))
            self.play(Write(l1[3]), FadeIn(tri, shift=UP * 0.15))
            self.done(tr)
        with self.say("For E of Y squared, the integrand is y squared times three eighths y squared. We "
                      "get three eighths, times thirty-two over five, which is two point four.") as tr:
            self.play(Write(l2[0]), run_time=2)
            self.wait(1.5)
            self.play(Write(l2[1]), run_time=1.2)
            self.play(Write(l2[2]))
            self.play(Write(l2[3]))
            self.done(tr)
        sd = Line(ax.c2p(1.5 - 0.387, 0.12), ax.c2p(1.5 + 0.387, 0.12), color=RED_, stroke_width=5)
        sdl = MathTex(r"\mu\pm\sigma", font_size=34, color=RED_).next_to(sd, UP, buff=0.08)
        with self.say("So the variance is two point four minus one point five squared, which is point one "
                      "five. The standard deviation is about point three eight seven hours, roughly "
                      "twenty-three minutes.") as tr:
            self.play(Write(l3[0]), run_time=2)
            self.wait(2)
            self.play(Write(l3[1]), run_time=2)
            self.play(Create(sd), FadeIn(sdl))
            self.done(tr)

    def computer_check(self):
        self.head("Checking it by computer")
        rng = random.Random(2026)
        ys = [2 * rng.random() ** (1 / 3) for _ in range(100000)]
        m = sum(ys) / len(ys)
        v = sum((y - m) ** 2 for y in ys) / (len(ys) - 1)
        ax = Axes(x_range=[0, 2.2, 1], y_range=[0, 1.1, 0.5], x_length=4.6, y_length=3.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 30},
                  x_axis_config={"numbers_to_include": [1, 2]}).move_to([-4.1, -0.9, 0])
        ul = MathTex("u", font_size=40, color=GREY_).next_to(ax.y_axis, UP, buff=0.1)
        yl = MathTex("y", font_size=40, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.12)
        one = MathTex("1", font_size=30, color=GREY_).next_to(ax.c2p(0, 1), LEFT, buff=0.15)
        cur = ax.plot(lambda y: y ** 3 / 8, x_range=[0, 2], color=BLUE_, stroke_width=4)
        cl = MathTex(r"u=F(y)=\tfrac{y^3}{8}", font_size=38, color=BLUE_).next_to(ax, UP, buff=0.12).shift(RIGHT * 0.6)
        a1 = T("Numerical integration", 30, TEAL_)
        a2 = MathTex(r"E(Y)=1.5,\quad E(Y^2)=2.4,\quad V(Y)=0.15", font_size=38)
        b1 = T("Simulation through the quantile function", 30, YELLOW_)
        b2 = VGroup(MathTex(r"\tfrac{y^3}{8}=u\ \ \Rightarrow\ \ y=F^{-1}(u)=2\,u^{1/3}", font_size=38),
                    MathTex(r"U\sim\text{Uniform}(0,1)", font_size=38)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        b3 = MathTex(r"100{,}000\ \text{draws:}\quad \bar y=" + f"{m:.3f}" + r",\qquad s^2=" + f"{v:.3f}",
                     font_size=38, color=YELLOW_)
        col = VGroup(a1, a2, b1, b2, b3).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        b1.shift(DOWN * 0.25)
        b2.shift(DOWN * 0.25)
        b3.shift(DOWN * 0.25)
        fit(col, 7.3, 5.4).move_to([2.65, -0.7, 0])
        with self.say("On the slides we check this in R, in two ways. First, numerical integration returns "
                      "the same three numbers: one point five, two point four, and point one five.") as tr:
            self.play(FadeIn(a1))
            self.play(Write(a2), run_time=2.5)
            self.done(tr)
        with self.say("Second, a simulation. Here the distribution function is y cubed over eight. Set it "
                      "equal to u and solve for y: the quantile function is two times the cube root of u. "
                      "Draw u uniformly between zero and one, push it through that function, and out comes "
                      "a draw of Y.") as tr:
            self.play(FadeIn(b1), Create(ax), FadeIn(ul), FadeIn(yl), FadeIn(one))
            self.play(Create(cur), FadeIn(cl), run_time=1.5)
            self.play(Write(b2), run_time=2.5)
            for u in (0.30, 0.82, 0.08, 0.55, 0.95, 0.68):
                y = 2 * u ** (1 / 3)
                d0 = Dot(ax.c2p(0, u), color=YELLOW_, radius=0.07)
                h = Line(ax.c2p(0, u), ax.c2p(y, u), color=YELLOW_, stroke_width=2.5)
                dn = Line(ax.c2p(y, u), ax.c2p(y, 0), color=YELLOW_, stroke_width=2.5)
                d1 = Dot(ax.c2p(y, 0), color=RED_, radius=0.07)
                self.play(FadeIn(d0, scale=0.5), run_time=0.3)
                self.play(Create(h), run_time=0.45)
                self.play(Create(dn), run_time=0.45)
                self.play(FadeIn(d1), FadeOut(h), FadeOut(dn), d0.animate.set_opacity(0.35), run_time=0.4)
            self.done(tr)
        with self.say("With one hundred thousand draws, the sample mean and the sample variance agree with "
                      "the integrals to two decimal places. Keep this trick in mind. It is why the uniform "
                      "distribution matters: every simulation starts from uniform draws.") as tr:
            self.play(Write(b3), run_time=2)
            self.play(Circumscribe(b3, color=YELLOW_))
            self.done(tr)

    def linear_cost(self):
        hd = self.head("From hours to AZN")
        c0 = MathTex(r"C=500+800\,Y", r"\qquad\text{(AZN)}", font_size=44)
        c0[1].set_color(GREY_)
        c1 = MathTex(r"E(C)=500+800\,E(Y)=500+800(1.5)=", r"1700\ \text{AZN}", font_size=40)
        c2 = MathTex(r"V(C)=800^2\,V(Y)=640000\times0.15=96000,\qquad", r"\sigma_C=309.84\ \text{AZN}", font_size=40)
        c1[1].set_color(TEAL_)
        c2[1].set_color(TEAL_)
        note = box("A linear cost", [r"$E(aY+b)=a\mu+b$:\ \ expected cost = cost of the expected hours",
                                     r"$V(aY+b)=a^2\,V(Y)$:\ \ the constant shifts the mean, not the spread"],
                   YELLOW_, size=38)
        g = fill(VGroup(c0, c1, c2, note).arrange(DOWN, buff=0.5))
        with self.say("Now turn hours into money. Reserve power costs the operator a fixed fee of five "
                      "hundred manat, plus eight hundred manat per hour. So the cost is C equals five "
                      "hundred plus eight hundred Y.") as tr:
            self.play(Write(c0), run_time=2.5)
            self.done(tr)
        with self.say("By theorem four point five we need no new integral. The expected cost is five "
                      "hundred plus eight hundred times one point five: one thousand seven hundred manat. "
                      "The variance is eight hundred squared times point one five, which is ninety-six "
                      "thousand, so the standard deviation is about three hundred and ten manat.") as tr:
            self.play(Write(c1), run_time=3)
            self.wait(5)
            self.play(Write(c2), run_time=3)
            self.done(tr)
        with self.say("Notice two things. The constant five hundred shifts the mean and leaves the spread "
                      "alone. And for a linear cost, the expected cost is simply the cost of the expected "
                      "hours. Hold on to the word linear.") as tr:
            self.play(FadeIn(note, shift=UP * 0.2))
            self.done(tr)

    # --------------------------------------------------------------- 5
    def window(self):
        self.head("Section 4.4: a settlement window")
        ax = Axes(x_range=[0, 30, 5], y_range=[0, 0.05, 0.05], x_length=10.5, y_length=2.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 32},
                  x_axis_config={"numbers_to_include": [0, 5, 10, 15, 20, 25, 30]},
                  y_axis_config={"include_ticks": False})
        xl = T("minutes after 10:00", 30, GREY_).next_to(ax.x_axis, DOWN, buff=0.2)
        rect = arect(ax, 0, 30, 1 / 30, YELLOW_, 0.3, stroke=3)
        hl = MathTex(r"f(y)=\tfrac{1}{30}", font_size=48, color=YELLOW_).next_to(rect, UP, buff=0.15)
        top = VGroup(ax, xl, rect, hl)
        fill(top, top=2.3, bottom=-2.6, max_scale=1.15)
        d46 = box("Definition 4.6",
                  [r"If $\theta_1<\theta_2$, $Y$ has a continuous uniform distribution",
                   r"on $(\theta_1,\theta_2)$ if and only if",
                   r"$f(y)=\dfrac{1}{\theta_2-\theta_1}$ for $\theta_1\le y\le\theta_2$,\quad and $f(y)=0$ elsewhere."],
                  BLUE_, size=40)
        d47 = VGroup(TX(r"\textbf{Definition 4.7:} constants that fix the form of a density,", font_size=40, color=TEAL_),
                     TX(r"here $\theta_1$ and $\theta_2$, are its \emph{parameters}.", font_size=40, color=TEAL_)
                     ).arrange(DOWN, buff=0.18)
        fill(VGroup(d46, d47).arrange(DOWN, buff=0.5), max_scale=1.35)
        with self.say("Section four point four. A correspondent bank promises a large transfer between ten "
                      "o'clock and ten thirty, with no part of the window favoured: it is as likely to "
                      "land in the first five minutes as in the last five. Let Y be the minutes after ten. "
                      "Its density is flat, and since the total area must be one, the height is one over "
                      "thirty.") as tr:
            self.play(Create(ax), FadeIn(xl))
            dot = Dot(ax.c2p(12, 0), color=RED_, radius=0.11)
            self.play(FadeIn(dot, scale=0.5), run_time=0.4)
            for t in (27.5, 3, 19, 8.5, 23, 14):
                self.play(dot.animate.move_to(ax.c2p(t, 0)), run_time=0.7)
                self.wait(0.6)
            self.play(FadeOut(dot), GrowFromEdge(rect, DOWN), run_time=1.2)
            self.wait(3)
            self.play(Write(hl))
            self.done(tr)
        with self.say("Definition four point six makes this general. For theta one less than theta two, Y "
                      "has a continuous uniform distribution on the interval from theta one to theta two "
                      "if its density is one over theta two minus theta one on that interval, and zero "
                      "elsewhere.") as tr:
            self.play(FadeOut(top), run_time=0.6)
            self.play(FadeIn(d46, shift=UP * 0.2))
            self.done(tr)
        with self.say("And definition four point seven gives us a word. The constants that fix the form "
                      "of a density, here theta one and theta two, are called its parameters.") as tr:
            self.play(FadeIn(d47, shift=UP * 0.2))
            self.done(tr)

    def length(self):
        self.head("Probability is length over length")
        ax = Axes(x_range=[0, 30, 5], y_range=[0, 0.05, 0.05], x_length=11, y_length=2.9, tips=False,
                  axis_config={"color": GREY_, "font_size": 30},
                  x_axis_config={"numbers_to_include": [0, 5, 10, 15, 20, 25, 30]},
                  y_axis_config={"include_ticks": False}).move_to([0.2, 0.95, 0])
        xl = T("minutes after 10:00", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.12)
        outline = arect(ax, 0, 30, 1 / 30, YELLOW_, 0.12, stroke=3)
        hl = MathTex(r"\tfrac{1}{30}", font_size=44, color=YELLOW_).next_to(ax.c2p(0, 1 / 30), LEFT, buff=0.15)
        t = ValueTracker(25)
        strip = always_redraw(lambda: arect(ax, t.get_value(), t.get_value() + 5, 1 / 30, RED_, 0.75))
        lab = MathTex(r"\tfrac16", font_size=60).move_to(ax.c2p(27.5, 1 / 60))
        p1 = MathTex(r"P(25\le Y\le30)=\int_{25}^{30}\tfrac{1}{30}\,dy=\tfrac{5}{30}=\tfrac16", font_size=46)
        p2 = MathTex(r"P(a\le Y\le b)=\frac{b-a}{\theta_2-\theta_1}", font_size=46, color=YELLOW_)
        row = VGroup(p1, p2).arrange(RIGHT, buff=0.8)
        fit(row, 13.2, 1.15, 1.0).move_to([0, -2.2, 0])
        ex = TX(r"Example 4.7: given exactly one Poisson arrival in $(0,30)$, its time is uniform on $(0,30)$.",
                font_size=40, color=GREY_)
        fit(ex, 13.0, 0.6, 1.0).move_to([0, -3.3, 0])
        with self.say("For a uniform, probability is length over length. The probability that the transfer "
                      "arrives in the last five minutes is the area of a strip of width five and height "
                      "one over thirty: five over thirty, which is one sixth.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(FadeIn(outline), FadeIn(hl))
            self.add(strip)
            self.play(FadeIn(lab))
            self.wait(2)
            self.play(Write(p1), run_time=3)
            self.done(tr)
        lab.add_updater(lambda mob: mob.move_to(ax.c2p(t.get_value() + 2.5, 1 / 60)))
        with self.say("Slide that strip anywhere inside the window and its area does not change. Every "
                      "five-minute stretch has the same probability, one sixth. In general, the "
                      "probability of an interval is its length divided by the length of the whole "
                      "window.") as tr:
            self.play(t.animate.set_value(0), run_time=3.5)
            self.wait(0.6)
            self.play(t.animate.set_value(13), run_time=2.5)
            self.wait(1)
            self.play(Write(p2), run_time=2)
            self.done(tr)
        with self.say("This is also Wackerly's example four point seven: if exactly one Poisson arrival "
                      "occurred in a thirty-minute period, its time is uniform over that period.") as tr:
            self.play(FadeIn(ex, shift=UP * 0.2))
            self.done(tr)
        lab.clear_updaters()
        strip.clear_updaters()

    def theorem46(self):
        self.head("Theorem 4.6: mean and variance")
        th = box("Theorem 4.6",
                 [r"If $\theta_1<\theta_2$ and $Y$ is uniformly distributed on $(\theta_1,\theta_2)$, then",
                  r"$\mu=E(Y)=\dfrac{\theta_1+\theta_2}{2}$\qquad and\qquad $\sigma^2=V(Y)=\dfrac{(\theta_2-\theta_1)^2}{12}$."],
                 YELLOW_, size=36)
        fill(th, max_w=12.8)
        sm = MathTex(r"\mu=\frac{\theta_1+\theta_2}{2}", r"\qquad\qquad", r"\sigma^2=\frac{(\theta_2-\theta_1)^2}{12}",
                     font_size=44, color=YELLOW_)
        sf = SurroundingRectangle(sm, color=YELLOW_, buff=0.25, corner_radius=0.12, stroke_width=2.5)
        sf.set_fill(YELLOW_, opacity=0.06)
        small = VGroup(sf, sm)
        small.move_to([0, 2.55 - small.height / 2, 0])
        y0 = small.get_bottom()[1] - 0.3          # top of the working area under the theorem
        with self.say("Theorem four point six. If Y is uniform on theta one to theta two, then its mean is "
                      "theta one plus theta two, over two, and its variance is theta two minus theta one, "
                      "squared, over twelve.") as tr:
            self.play(FadeIn(th, shift=UP * 0.2))
            self.done(tr)
        pt = T("Proof of the mean", 32, TEAL_)
        pa = MathTex(r"E(Y)=\int_{\theta_1}^{\theta_2}\frac{y}{\theta_2-\theta_1}\,dy",
                     r"=\frac{\theta_2^2-\theta_1^2}{2(\theta_2-\theta_1)}", font_size=44)
        pb = MathTex(r"=\frac{(\theta_2-\theta_1)(\theta_2+\theta_1)}{2(\theta_2-\theta_1)}",
                     r"=\frac{\theta_1+\theta_2}{2}", font_size=44)
        pb[1].set_color(TEAL_)
        pg = VGroup(pt, pa, pb).arrange(DOWN, buff=0.35)
        pb.align_to(pa[1], LEFT)
        fit(pg, 12.6, y0 + 3.55, 1.25).move_to([0, (y0 - 3.55) / 2, 0])
        with self.say("The proof of the mean is one integral. Integrate y over theta two minus theta one. "
                      "That gives theta two squared minus theta one squared, over two times theta two "
                      "minus theta one. The numerator is a difference of squares, so one factor cancels "
                      "and we are left with the midpoint. A flat block balances at its centre.") as tr:
            self.play(FadeOut(th), FadeIn(small), FadeIn(pt), run_time=1)
            self.play(Write(pa[0]), run_time=2.5)
            self.wait(1.5)
            self.play(Write(pa[1]), run_time=2)
            self.wait(3.5)
            self.play(Write(pb[0]), run_time=2)
            self.wait(2)
            self.play(Write(pb[1]), run_time=1.5)
            self.done(tr)
        self.play(FadeOut(pg), run_time=0.5)
        vt = T("The variance (Exercise 4.41), in outline", 32, RED_)
        v1 = MathTex(r"E(Y^2)=\int_{\theta_1}^{\theta_2}\frac{y^2}{\theta_2-\theta_1}\,dy",
                     r"=\frac{\theta_2^3-\theta_1^3}{3(\theta_2-\theta_1)}",
                     r"=\frac{\theta_1^2+\theta_1\theta_2+\theta_2^2}{3}", font_size=42)
        v2 = MathTex(r"V(Y)=\frac{\theta_1^2+\theta_1\theta_2+\theta_2^2}{3}-\frac{(\theta_1+\theta_2)^2}{4}=",
                     r"\frac{(\theta_2-\theta_1)^2}{12}", font_size=42)
        v2[1].set_color(YELLOW_)
        vg = VGroup(vt, v1, v2).arrange(DOWN, buff=0.4)
        fit(vg, 12.4, y0 + 3.4, 1.25).move_to([0, (y0 - 3.4) / 2, 0])
        frame = SurroundingRectangle(v2[1], color=YELLOW_, buff=0.16, stroke_width=3, corner_radius=0.08)
        with self.say("The variance is exercise four point forty-one, and here is the sketch. E of Y "
                      "squared is theta one squared, plus theta one theta two, plus theta two squared, all "
                      "over three. Subtract mu squared, and it collapses to theta two minus theta one, "
                      "squared, over twelve. It depends only on the width of the interval, not on where "
                      "the interval sits.") as tr:
            self.play(FadeIn(vt))
            self.play(Write(v1), run_time=4)
            self.wait(4)
            self.play(Write(v2[0]), run_time=2.5)
            self.wait(1)
            self.play(Write(v2[1]), run_time=1.5)
            self.play(Create(frame))
            self.done(tr)

    # --------------------------------------------------------------- 6
    def low_bid(self):
        self.head("Worked example: a uniform low bid")
        ax = Axes(x_range=[410, 510, 10], y_range=[0, 0.02, 0.02], x_length=10.0, y_length=1.9, tips=False,
                  axis_config={"color": GREY_, "font_size": 30},
                  x_axis_config={"numbers_to_include": [420, 440, 460, 480, 500]},
                  y_axis_config={"include_ticks": False, "stroke_opacity": 0})
        xl = T("low bid, thousand AZN", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.1)
        rect = arect(ax, 420, 500, 1 / 80, YELLOW_, 0.15, stroke=3)
        fl = MathTex(r"f(y)=\tfrac{1}{80}", font_size=40, color=YELLOW_).next_to(rect, UP, buff=0.1)
        top = VGroup(ax, xl, rect, fl)
        a = MathTex(r"P(Y<440)=\frac{440-420}{80}=0.25,", r"\qquad P(Y>490)=\frac{10}{80}=0.125", font_size=44)
        b = MathTex(r"E(Y)=\frac{420+500}{2}=460,\quad V(Y)=\frac{80^2}{12}=533.33,\quad \sigma=23.09", font_size=44)
        c = MathTex(r"P(Y>480\mid Y>440)=\frac{P(Y>480)}{P(Y>440)}=\frac{20/80}{60/80}=", r"\frac13", font_size=44)
        a[0].set_color(BLUE_)
        a[1].set_color(RED_)
        c[1].set_color(YELLOW_)
        for m in (a, b, c):
            capw(m, 12.9)
        g = VGroup(top, a, b, c).arrange(DOWN, buff=0.3)
        fill(g, top=2.6, bottom=-3.65, max_scale=1.2)
        with self.say("Let's use it. In a municipal road resurfacing tender, the low bid Y is uniform "
                      "between four hundred and twenty and five hundred thousand manat. The width is "
                      "eighty, so the density is one over eighty.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(GrowFromEdge(rect, DOWN), run_time=1.2)
            self.wait(3)
            self.play(Write(fl))
            self.done(tr)
        s1 = arect(ax, 420, 440, 1 / 80, BLUE_, 0.8)
        s2 = arect(ax, 490, 500, 1 / 80, RED_, 0.8)
        with self.say("The probability that the bid is below four hundred and forty is twenty over eighty, "
                      "point two five. The probability that it is above four hundred and ninety is ten "
                      "over eighty, point one two five.") as tr:
            self.play(FadeIn(s1), Write(a[0]), run_time=2)
            self.wait(3.5)
            self.play(FadeIn(s2), Write(a[1]), run_time=2)
            self.done(tr)
        tri = Triangle(color=TEAL_, fill_opacity=1).scale(0.13).move_to(ax.c2p(460, 0) + UP * 0.18)
        with self.say("The mean is the midpoint, four hundred and sixty. The variance is eighty squared "
                      "over twelve, about five hundred and thirty-three, so the standard deviation is "
                      "about twenty-three thousand manat.") as tr:
            self.play(FadeOut(s1), FadeOut(s2), run_time=0.6)
            self.play(Write(b), FadeIn(tri), run_time=3)
            self.done(tr)
        dim = arect(ax, 420, 440, 1 / 80, BG, 0.8)
        left = arect(ax, 440, 500, 1 / 80, TEAL_, 0.35, stroke=3)
        hit = arect(ax, 480, 500, 1 / 80, YELLOW_, 0.85)
        with self.say("Now suppose we learn that the bid is above four hundred and forty. What is the "
                      "probability that it is above four hundred and eighty? Divide: twenty over eighty by "
                      "sixty over eighty, which is one third. Conditioning a uniform on a subinterval "
                      "leaves it uniform on that subinterval: twenty of the remaining sixty.") as tr:
            self.play(FadeOut(tri), FadeIn(dim), FadeIn(left), run_time=1.2)
            self.wait(3)
            self.play(FadeIn(hit))
            self.play(Write(c), run_time=3)
            self.done(tr)

    def rounding(self):
        hd = self.head("Rounding errors at the till")
        setup = VGroup(T("Each cash bill is rounded to the nearest 5 qəpik.", 32),
                       T("The error E, in AZN, is uniform on (−0.025, 0.025).", 32)).arrange(DOWN, buff=0.15)
        fit(setup, 13.0, 1.15, 1.0).next_to(hd, DOWN, buff=0.22)
        ax = Axes(x_range=[-0.035, 0.035, 0.07], y_range=[0, 26, 26], x_length=4.7, y_length=3.3, tips=False,
                  axis_config={"color": GREY_, "include_ticks": False}).move_to([-4.2, -1.35, 0])
        labs = VGroup(*[MathTex(s, font_size=32, color=GREY_).next_to(ax.c2p(x, 0), DOWN, buff=0.15)
                        for s, x in ((r"-0.025", -0.025), ("0", 0), ("0.025", 0.025))])
        rect = arect(ax, -0.025, 0.025, 20, BLUE_, 0.3, stroke=3)
        fl = MathTex(r"f(e)=\tfrac{1}{0.05}=20", font_size=38, color=BLUE_).next_to(rect, UP, buff=0.12)
        vee = VGroup(Line(ax.c2p(-0.025, 20), ax.c2p(0, 0), color=RED_, stroke_width=4),
                     Line(ax.c2p(0, 0), ax.c2p(0.025, 20), color=RED_, stroke_width=4))
        vl = MathTex(r"g(e)=|e|", font_size=36, color=RED_).move_to(ax.c2p(0, 14.5))
        r1 = MathTex(r"\mu=0,\qquad \sigma=\frac{0.05}{\sqrt{12}}=0.0144\ \text{AZN}", font_size=40)
        r2 = MathTex(r"E|E|=\int_{-0.025}^{0.025}|e|\cdot\frac{1}{0.05}\,de", r"=2\int_{0}^{0.025}\frac{e}{0.05}\,de",
                     r"=0.0125\ \text{AZN}", font_size=40)
        r2[2].set_color(YELLOW_)
        r2[1].next_to(r2[0], DOWN, buff=0.3).align_to(r2[0], LEFT).shift(RIGHT * 0.3)
        r2[2].next_to(r2[1], RIGHT, buff=0.15)
        r3 = VGroup(T("Mean zero is not size zero:", 30, YELLOW_),
                    T("1.25 qəpik per bill, one way or the other.", 30, YELLOW_)).arrange(DOWN, buff=0.12)
        col = VGroup(r1, r2, r3).arrange(DOWN, buff=0.5)
        fit(col, 8.0, 4.7).move_to([2.6, -1.3, 0])
        with self.say("Another uniform. A supermarket chain rounds each cash bill to the nearest five "
                      "qapik. The rounding error, in manat, is uniform between minus point zero two five "
                      "and plus point zero two five.") as tr:
            self.play(FadeIn(setup))
            self.play(Create(ax), FadeIn(labs))
            self.play(GrowFromEdge(rect, DOWN), FadeIn(fl))
            self.done(tr)
        with self.say("By theorem four point six the mean is zero, so rounding is unbiased: the chain "
                      "neither gains nor loses on average. The standard deviation is point zero five over "
                      "the square root of twelve, about point zero one four four manat.") as tr:
            self.play(Write(r1), run_time=3)
            self.done(tr)
        with self.say("How large is a typical error? Use theorem four point four with g equal to the "
                      "absolute value. By symmetry it is twice the integral from zero to point zero two "
                      "five, and the answer is point zero one two five manat. Mean zero is not size zero: "
                      "each bill is off by one and a quarter qapik on average, one way or the other.") as tr:
            self.play(Create(vee), FadeIn(vl), run_time=1.5)
            self.play(Write(r2[0]), run_time=2.5)
            self.wait(1.5)
            self.play(Write(r2[1]), run_time=2)
            self.wait(1.5)
            self.play(Write(r2[2]))
            self.wait(2)
            self.play(FadeIn(r3, shift=UP * 0.2))
            self.done(tr)

    # --------------------------------------------------------------- 7
    def delayed(self):
        self.head("Back to the delayed part")
        d0 = MathTex(r"Y\sim\text{Uniform}(1,5)\ \text{days},\qquad C=2000+150\,Y^2", font_size=42)
        d1 = MathTex(r"E(Y)=3,\qquad V(Y)=\frac{4^2}{12}=\frac43", font_size=42)
        d2 = MathTex(r"E(Y^2)=V(Y)+[E(Y)]^2=\frac43+9=\frac{31}{3}\approx10.33", font_size=42, color=TEAL_)
        d3 = MathTex(r"E(C)=2000+150\,E(Y^2)=2000+150\times\tfrac{31}{3}=", r"3550\ \text{AZN}", font_size=44)
        d3[1].set_color(YELLOW_)
        d4 = MathTex(r"\text{plug-in: }2000+150\times3^2=3350,", r"\qquad\text{gap}=150\,V(Y)=150\times\tfrac43=200\ \text{AZN}",
                     font_size=40)
        d4[1].set_color(RED_)
        d5 = MathTex(r"E[g(Y)]\ne g\big(E[Y]\big)\ \ \text{when } g \text{ is not linear}", font_size=44, color=RED_)
        g = VGroup(d0, d1, d2, d3, d4, d5).arrange(DOWN, buff=0.32)
        fill(g, top=2.6, bottom=-3.65, max_scale=1.3)
        with self.say("Back to the delayed turbine part. The delay Y is uniform on one to five days, and "
                      "the cost is two thousand plus one hundred and fifty Y squared. Compare Wackerly's "
                      "exercise four point forty-seven.") as tr:
            self.play(Write(d0), run_time=3)
            self.done(tr)
        with self.say("The mean delay is three days, and the variance is four squared over twelve, which "
                      "is four thirds. So E of Y squared is the variance plus the mean squared: four "
                      "thirds plus nine, thirty-one over three.") as tr:
            self.play(Write(d1), run_time=2.5)
            self.wait(3)
            self.play(Write(d2), run_time=3)
            self.done(tr)
        with self.say("By theorem four point five, the expected cost is two thousand plus one hundred and "
                      "fifty times thirty-one over three: three thousand five hundred and fifty manat.") as tr:
            self.play(Write(d3), run_time=3.5)
            self.play(Indicate(d3[1], color=YELLOW_, scale_factor=1.15))
            self.done(tr)
        with self.say("Plugging in the average delay gave three thousand three hundred and fifty. The gap "
                      "is one hundred and fifty times the variance of Y: two hundred manat. When g is not "
                      "linear, the expected value of g of Y is not g of the expected value.") as tr:
            self.play(Write(d4[0]), run_time=2)
            self.wait(1.5)
            self.play(Write(d4[1]), run_time=2.5)
            self.wait(2.5)
            self.play(Write(d5), run_time=2)
            self.done(tr)

    def convex(self):
        self.head("Why the plug-in undershoots")

        def g(y):
            return 2000 + 150 * y * y

        ax = Axes(x_range=[0, 6, 1], y_range=[2000, 6000, 1000], x_length=7.2, y_length=5.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 28},
                  x_axis_config={"numbers_to_include": [1, 2, 3, 4, 5]},
                  y_axis_config={"numbers_to_include": [3000, 4000, 5000, 6000]}).move_to([-2.0, -0.55, 0])
        xl = T("delay y (days)", 26, GREY_).next_to(ax.c2p(6, 2000), UP, buff=0.2).align_to(ax.x_axis, RIGHT)
        yl = T("cost (AZN)", 26, GREY_).next_to(ax.c2p(0, 6000), RIGHT, buff=0.25)
        faint = ax.plot(g, x_range=[0, 5.15], color=DIM, stroke_width=3)
        cur = ax.plot(g, x_range=[1, 5], color=BLUE_, stroke_width=5)
        base = Dot(ax.c2p(3, 3350), color=BLUE_, radius=0.1)
        vline = DashedLine(ax.c2p(3, 2000), ax.c2p(3, 3350), color=GREY_, stroke_width=2)
        lg = MathTex(r"g\big(E[Y]\big)=3350", font_size=46, color=BLUE_)
        lc = VGroup(T("chord midpoint:", 30, ORANGE_), T("above the curve", 30, ORANGE_)).arrange(DOWN, buff=0.12)
        le = MathTex(r"E[g(Y)]=3550", font_size=46, color=RED_)
        lgap = MathTex(r"\text{gap}=150\,V(Y)=200", font_size=40)
        col = VGroup(le, lc, lg, lgap).arrange(DOWN, buff=0.6)
        fit(col, 4.3, 4.6, 1.0).move_to([4.55, -0.5, 0])
        with self.say("Here is why the plug-in number is too low. Draw the cost against the delay. The "
                      "curve bends upward: it is convex. At the average delay, three days, the curve "
                      "stands at three thousand three hundred and fifty.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(Create(faint), run_time=0.8)
            self.play(Create(cur), run_time=2)
            self.wait(1.5)
            self.play(Create(vline), FadeIn(base, scale=0.5))
            self.play(Write(lg))
            self.done(tr)
        d = ValueTracker(0.05)
        chord = always_redraw(lambda: Line(ax.c2p(3 - d.get_value(), g(3 - d.get_value())),
                                           ax.c2p(3 + d.get_value(), g(3 + d.get_value())),
                                           color=ORANGE_, stroke_width=4))
        ends = always_redraw(lambda: VGroup(
            Dot(ax.c2p(3 - d.get_value(), g(3 - d.get_value())), color=ORANGE_, radius=0.08),
            Dot(ax.c2p(3 + d.get_value(), g(3 + d.get_value())), color=ORANGE_, radius=0.08)))
        mid = always_redraw(lambda: Dot(ax.c2p(3, 3350 + 150 * d.get_value() ** 2), color=ORANGE_, radius=0.1))
        with self.say("Now take two equally likely delays, the same distance either side of three. Their "
                      "average cost is the midpoint of the chord joining them, and a chord of a convex "
                      "curve lies above the curve. The further apart the delays, the higher that "
                      "midpoint.") as tr:
            self.add(chord, ends, mid)
            self.play(d.animate.set_value(1.0), run_time=3)
            self.play(FadeIn(lc))
            self.wait(2)
            self.play(d.animate.set_value(2.0), run_time=3)
            self.wait(1)
            self.play(d.animate.set_value(0.4), run_time=3)
            self.done(tr)
        full = DashedLine(ax.c2p(1, g(1)), ax.c2p(5, g(5)), color=GREY_, stroke_width=2)
        red = Dot(ax.c2p(3, 3550), color=RED_, radius=0.11)
        with self.say("Average over all such pairs and you land at three thousand five hundred and fifty, "
                      "above the curve. Long delays cost disproportionately, and the mean of Y squared "
                      "remembers them. For a convex cost, the plug-in answer is always too low.") as tr:
            self.play(Create(full), d.animate.set_value(2.0), run_time=2.5)
            self.play(d.animate.set_value(0.05), run_time=2.5)
            self.play(FadeIn(red, scale=0.5), Write(le))
            self.wait(2)
            self.play(Write(lgap))
            self.done(tr)
        for mob in (chord, ends, mid):
            mob.clear_updaters()

    # --------------------------------------------------------------- 8
    def tps(self):
        hd = self.head("Think–pair–share: demurrage")
        ctx = VGroup(TX(r"A crude tanker's loading time at a Caspian terminal", font_size=44),
                     TX(r"is $Y\sim\text{Uniform}(18,30)$ hours. The charterer pays demurrage", font_size=44),
                     TX(r"of 2{,}000 AZN per hour beyond 24 hours.", font_size=44)).arrange(DOWN, buff=0.2)
        fit(ctx, 13.0, 1.9, 1.0).next_to(hd, DOWN, buff=0.25)
        qs = VGroup(TX(r"1.\ \ Find $E(Y)$ and $V(Y)$.", font_size=44),
                    TX(r"2.\ \ Loading has already passed 24 hours. What is $P(Y>27\mid Y>24)$?", font_size=44),
                    TX(r"3.\ \ Expected demurrage bill? Is it $2000\times\max\big(E(Y)-24,\,0\big)$?", font_size=44)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        fit(qs, 13.0, 2.3, 1.0).next_to(ctx, DOWN, buff=0.45)
        pause = T("Pause the video and take four minutes.", 40, RED_).to_edge(DOWN, buff=0.4)
        with self.say("Now it is your turn. In class this is the think, pair, share exercise. A crude "
                      "tanker's loading time at a Caspian terminal is uniform between eighteen and thirty "
                      "hours. The charterer pays demurrage of two thousand manat per hour beyond "
                      "twenty-four hours.") as tr:
            self.play(FadeIn(ctx[0]))
            self.wait(5)
            self.play(FadeIn(ctx[1:]))
            self.done(tr)
        with self.say("Three questions. One: find the mean and the variance of Y. Two: loading has already "
                      "passed twenty-four hours; what is the probability that it goes beyond twenty-seven? "
                      "Three: what is the expected demurrage bill, and is it what you get by plugging in "
                      "the mean? Pause the video now, take about four minutes, and then come back.") as tr:
            self.wait(1)
            for q, w in zip(qs, (3.5, 6, 6)):
                self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(w)
            self.play(FadeIn(pause))
            self.done(tr)
        self.wait(2)
        self.play(FadeOut(VGroup(ctx, qs, pause)))

        ax = Axes(x_range=[18, 30, 3], y_range=[0, 12, 4], x_length=4.2, y_length=3.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 28},
                  x_axis_config={"numbers_to_include": [18, 21, 24, 27, 30]},
                  y_axis_config={"numbers_to_include": [4, 8, 12]}).move_to([-4.15, -0.75, 0])
        xl = T("loading time, hours", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.12)
        yl = T("thousand AZN", 26, GREY_).next_to(ax.c2p(18, 12), RIGHT, buff=0.25)
        hinge = VGroup(Line(ax.c2p(18, 0), ax.c2p(24, 0), color=RED_, stroke_width=6),
                       Line(ax.c2p(24, 0), ax.c2p(30, 12), color=RED_, stroke_width=6))
        tri = Polygon(ax.c2p(24, 0), ax.c2p(30, 0), ax.c2p(30, 12), stroke_width=0, fill_color=RED_, fill_opacity=0.3)
        cond = arect(ax, 24, 30, 2.2, TEAL_, 0.35, stroke=2)
        half = arect(ax, 27, 30, 2.2, YELLOW_, 0.8)
        mu = Triangle(color=TEAL_, fill_opacity=1).scale(0.13).move_to(ax.c2p(24, 0) + UP * 0.18)
        s1 = MathTex(r"E(Y)=\tfrac{18+30}{2}=24,\quad V(Y)=\tfrac{12^2}{12}=12,\quad \sigma=3.46\ \text{h}", font_size=40)
        s2 = MathTex(r"P(Y>27\mid Y>24)=\frac{30-27}{30-24}=\frac36=0.5", font_size=40, color=TEAL_)
        s3 = MathTex(r"E[g(Y)]=\int_{24}^{30}2000\,(y-24)\,\tfrac{1}{12}\,dy", r"=\frac{2000}{12}\cdot\frac{6^2}{2}=",
                     r"3000\ \text{AZN}", font_size=40)
        s3[1].next_to(s3[0], DOWN, buff=0.3).align_to(s3[0], LEFT).shift(RIGHT * 1.4)
        s3[2].next_to(s3[1], RIGHT, buff=0.15)
        s3[2].set_color(YELLOW_)
        s4 = MathTex(r"\text{plug-in: }2000\times\max(24-24,\,0)=0", font_size=40, color=RED_)
        col = VGroup(s1, s2, s3, s4).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        fit(col, 7.8, 5.7).move_to([2.4, -0.55, 0])
        with self.say("Here is the solution. By theorem four point six, the mean is eighteen plus thirty "
                      "over two, twenty-four hours. The variance is twelve squared over twelve, which is "
                      "twelve, so the standard deviation is about three point four six hours.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(Write(s1), FadeIn(mu), run_time=3)
            self.done(tr)
        with self.say("Given that Y is above twenty-four, Y is uniform between twenty-four and thirty. The "
                      "part above twenty-seven is three of the remaining six hours: probability one "
                      "half.") as tr:
            self.play(FadeIn(cond))
            self.wait(2.5)
            self.play(FadeIn(half))
            self.play(Write(s2), run_time=2.5)
            self.done(tr)
        with self.say("Demurrage is a hinge: zero up to twenty-four hours, then two thousand manat for "
                      "each extra hour. By theorem four point four, integrate two thousand times y minus "
                      "twenty-four, times one twelfth, from twenty-four to thirty. That gives three "
                      "thousand manat.") as tr:
            self.play(FadeOut(cond), FadeOut(half), FadeOut(mu), FadeIn(yl), run_time=0.8)
            self.play(Create(hinge[0]), run_time=1.2)
            self.play(Create(hinge[1]), run_time=1.2)
            self.play(FadeIn(tri))
            self.play(Write(s3[0]), run_time=3)
            self.wait(1)
            self.play(Write(s3[1]), run_time=1.5)
            self.wait(1.5)
            self.play(Write(s3[2]))
            self.done(tr)
        z = Dot(ax.c2p(24, 0), color=YELLOW_, radius=0.11)
        with self.say("The plug-in answer is two thousand times zero, which is zero. A contract that "
                      "charges only on the bad side has a positive expected cost, even when the average "
                      "outcome costs nothing.") as tr:
            self.play(FadeIn(z, scale=0.5), Write(s4), run_time=2)
            self.play(Flash(z, color=YELLOW_))
            self.done(tr)

    # --------------------------------------------------------------- 9
    def case_study(self):
        hd = self.head("Case study: is the month's worst day uniform?")
        fr = worst_day_positions("sp500.csv")
        n = len(fr)
        mean = sum(fr) / n
        var = sum((a - mean) ** 2 for a in fr) / (n - 1)
        counts = [0] * 8
        for a in fr:
            counts[min(int(a * 8), 7)] += 1
        dens = [c * 8 / n for c in counts]
        q1 = sum(1 for a in fr if a < 0.25) / n
        ctx = VGroup(T("S&P 500 daily close, FRED, Sep 2016 – Sep 2026", 30, GREY_),
                     TX(r"$Y$ = (rank of the month's largest $|\text{log return}|$ $-\ 0.5$) / (trading days in that month)",
                        font_size=42)).arrange(DOWN, buff=0.2)
        fit(ctx, 13.0, 1.2, 1.0).next_to(hd, DOWN, buff=0.22)
        with self.say("A case study with real data. Take the daily close of the S and P five hundred from "
                      "FRED, September twenty sixteen to September twenty twenty-six. In each calendar "
                      "month, find the day with the largest absolute log return, and record its position "
                      "in the month, rescaled to lie between zero and one. Call that Y. Is Y uniform?") as tr:
            self.play(FadeIn(ctx[0]))
            self.wait(6)
            self.play(FadeIn(ctx[1]))
            self.done(tr)
        ymax = max(1.6, math.ceil(max(dens) * 5) / 5)
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, ymax, 0.4], x_length=7.2, y_length=3.3, tips=False,
                  axis_config={"color": GREY_, "font_size": 28},
                  x_axis_config={"numbers_to_include": [0.25, 0.5, 0.75, 1.0]},
                  y_axis_config={"numbers_to_include": [0.4, 0.8, 1.2, 1.6]}).move_to([-2.4, -1.15, 0])
        xl = T("position of the month's worst day (0 = start, 1 = end)", 24, GREY_).next_to(ax.x_axis, DOWN, buff=0.1)
        bars = VGroup()
        for i, dv in enumerate(dens):
            p0, p1 = ax.c2p(i / 8, 0), ax.c2p((i + 1) / 8, dv)
            bars.add(Rectangle(width=p1[0] - p0[0], height=max(p1[1] - p0[1], 0.002), fill_color=STEEL_, fill_opacity=0.85,
                               stroke_color=BG, stroke_width=2).move_to([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0]))
        flat = Line(ax.c2p(0, 1), ax.c2p(1, 1), color=RED_, stroke_width=4)
        fl = T("Uniform(0,1) density", 28, RED_).next_to(ax.c2p(0.5, ymax), DOWN, buff=0.0)
        stats = VGroup(
            MathTex(r"n=", f"{n}", r"\ \text{months}", font_size=44),
            MathTex(r"\bar y", f"={mean:.3f}", font_size=44),
            T("uniform: 0.5", 28, GREY_),
            MathTex(r"s^2", f"={var:.4f}", font_size=44),
            T("uniform: 1/12 = 0.0833", 28, GREY_),
            MathTex(r"\text{first quarter: }", f"{q1 * 100:.0f}" + r"\%", font_size=44),
            T("uniform: 25%", 28, GREY_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        for k in (0, 1, 3, 5):
            stats[k][1].set_color(YELLOW_)
        fit(stats, 4.5, 4.4, 1.0).move_to([4.35, -1.15, 0])
        with self.say("If it were uniform on zero to one, theorem four point six predicts a mean of one "
                      "half and a variance of one twelfth, about point zero eight three. In one hundred "
                      "and twenty months, the sample mean is point four six and the sample variance is "
                      "point zero nine nine. The mean is close to one half, and the variance runs a little "
                      "above one twelfth.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(Create(flat), FadeIn(fl))
            self.wait(4)
            self.play(FadeIn(stats[0]))
            self.play(FadeIn(stats[1:3]))
            self.wait(2)
            self.play(FadeIn(stats[3:5]))
            self.done(tr)
        with self.say("The histogram sits reasonably near the flat line, but not everywhere. In the first "
                      "quarter of the month the bars stand at one point four: thirty-five percent of the "
                      "worst days fall there, where the uniform predicts twenty-five. Jobs and inflation "
                      "releases come early in the month, so real news clusters near the start. The last "
                      "bar is high too, and with only one hundred and twenty months some wobble is "
                      "expected. The uniform is a sensible first model, but the position is not quite free "
                      "of the calendar.") as tr:
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=2.5)
            self.bring_to_front(flat)
            self.wait(3)
            self.play(bars[0].animate.set_fill(ORANGE_), bars[1].animate.set_fill(ORANGE_), FadeIn(stats[5:7]))
            self.wait(11)
            self.play(Indicate(bars[7], color=ORANGE_, scale_factor=1.05))
            self.done(tr)

    def check(self):
        self.head("Check yourself: three quick questions")

        def card(i, q, a):
            qt = VGroup(*[TX(x, font_size=52) for x in q]).arrange(DOWN, buff=0.25)
            fit(qt, 12.8, 2.0, 1.0).move_to([0, 0.75, 0])
            at = VGroup(*[TX(x, font_size=46, color=TEAL_) for x in a]).arrange(DOWN, buff=0.25)
            fit(at, 12.8, 2.0, 1.0).move_to([0, -2.0, 0])
            num = T(f"Question {i} of 3", 32, GREY_).move_to([0, 2.2, 0])
            return qt, at, num

        qt, at, num = card(1, [r"A payment arrives uniformly within a 40-minute window.",
                               r"What is $V(Y)$, in minutes squared?"],
                           [r"$40^2/12=133.3$: the squared width over 12.",
                            r"The position of the window does not matter."])
        with self.say("Three quick questions to check yourself. First. A payment arrives at a uniformly "
                      "distributed time within a forty-minute window. What is the variance of Y, in "
                      "minutes squared? Pause if you want to think.") as tr:
            self.play(FadeIn(num), Write(qt), run_time=1.5)
            self.done(tr)
        self.wait(2.5)
        with self.say("It is forty squared over twelve, about one hundred and thirty-three. The variance "
                      "is the squared width over twelve. Where the window sits does not matter.") as tr:
            self.play(FadeIn(at, shift=UP * 0.2))
            self.done(tr)
        prev = VGroup(qt, at, num)

        qt, at, num = card(2, [r"$Y$ is uniform on $(0,2)$. What is $E(Y^2)$?"],
                           [r"$\tfrac43$:\ \ $\int_0^2 y^2\cdot\tfrac12\,dy=\tfrac86$,\ \ or\ \ $V(Y)+[E(Y)]^2=\tfrac13+1$.",
                            r"Squaring the mean misses the variance."])
        with self.say("Second. Y is uniform on zero to two. What is E of Y squared?") as tr:
            self.play(FadeOut(prev), run_time=0.5)
            self.play(FadeIn(num), Write(qt), run_time=1.5)
            self.done(tr)
        self.wait(2.5)
        with self.say("Four thirds, not one. By theorem four point four, integrate y squared times one "
                      "half from zero to two: eight sixths. Or add the variance, one third, to the mean "
                      "squared, one. Squaring the mean misses the variance.") as tr:
            self.play(FadeIn(at, shift=UP * 0.2))
            self.done(tr)
        prev = VGroup(qt, at, num)

        qt, at, num = card(3, [r"A sealed bid is uniform on $(10,14)$ thousand AZN.",
                               r"Given that it exceeds 11, find $P(Y>13)$."],
                           [r"$\tfrac13$: given $Y>11$, $Y$ is uniform on $(11,14)$,",
                            r"and $(13,14)$ is 1 unit of the remaining 3."])
        with self.say("Third. A sealed bid is uniform between ten and fourteen thousand manat. Given that "
                      "it exceeds eleven, what is the probability that it exceeds thirteen?") as tr:
            self.play(FadeOut(prev), run_time=0.5)
            self.play(FadeIn(num), Write(qt), run_time=1.5)
            self.done(tr)
        self.wait(2.5)
        with self.say("One third. Given that Y is above eleven, it is uniform between eleven and fourteen, "
                      "and the part above thirteen is one unit of the remaining three.") as tr:
            self.play(FadeIn(at, shift=UP * 0.2))
            self.done(tr)

    # --------------------------------------------------------------- 10
    def formulas(self):
        self.head("Key formulas")
        data = [
            ("Definition 4.5", r"E(Y)=\textstyle\int_{-\infty}^{\infty} y\,f(y)\,dy"),
            ("Theorem 4.4", r"E[g(Y)]=\textstyle\int_{-\infty}^{\infty} g(y)\,f(y)\,dy"),
            ("Theorem 4.5", r"E(c)=c,\ \ E[c\,g(Y)]=c\,E[g(Y)],\ \ E\big[\textstyle\sum g_i\big]=\textstyle\sum E[g_i]"),
            ("Variance", r"V(Y)=E(Y^2)-\mu^2"),
            ("Linear cost", r"E(aY+b)=a\mu+b,\qquad V(aY+b)=a^2\,V(Y)"),
            ("Definition 4.6", r"f(y)=\frac{1}{\theta_2-\theta_1}\ \ \text{on}\ \ \theta_1\le y\le\theta_2"),
            ("Theorem 4.6", r"\mu=\frac{\theta_1+\theta_2}{2},\qquad \sigma^2=\frac{(\theta_2-\theta_1)^2}{12}"),
        ]
        rows = VGroup()
        for name, tex in data:
            rows.add(VGroup(T(name, 28, TEAL_), MathTex(tex, font_size=36)))
        for r in rows:
            r[1].next_to(r[0], RIGHT, buff=0.5)
        rows.arrange(DOWN, buff=0.27, aligned_edge=LEFT)
        for r in rows:
            r[1].set_x(rows.get_left()[0] + 2.75 + r[1].width / 2)
        rows[6][1].set_color(YELLOW_)
        fill(rows, top=2.6, bottom=-3.7, max_scale=1.6)
        with self.say("Here are the key formulas on one page. The definition of the mean, and theorem four "
                      "point four for any function g. Linearity, and the variance shortcut. For a linear "
                      "cost a Y plus b, the mean is a mu plus b and the variance is a squared times the "
                      "variance of Y. And for the uniform: flat density, mean at the midpoint, variance "
                      "width squared over twelve.") as tr:
            for r, w in zip(rows, (1.6, 2.4, 1.2, 1.8, 6.0, 2.0, 1.0)):
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(w)
            self.done(tr)

    def summary(self):
        self.head("Summary")
        items = VGroup(
            TX(r"Continuous expectation: $\sum\to\int$ and $p(y)\to f(y)\,dy$", font_size=44),
            TX(r"Theorem 4.4 prices any $g(Y)$; Theorem 4.5 handles linear ones", font_size=44),
            TX(r"Uniform on $(\theta_1,\theta_2)$: probability is length over length", font_size=44),
            TX(r"Conditioned on a subinterval, a uniform stays uniform", font_size=44),
            TX(r"Mean = midpoint;\ \ variance = width$^2/12$", font_size=44),
            TX(r"Non-linear cost: $E[g(Y)]\ne g(E[Y])$; convex $\Rightarrow$ plug-in too low", font_size=44, color=YELLOW_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.72)
        fill(items, max_scale=1.25)
        with self.say("To sum up. Continuous expectation is chapter three with the sum replaced by an "
                      "integral, and p of y by f of y, d y. Theorem four point four prices any function of "
                      "Y, and theorem four point five handles linear ones with no new integral. A uniform "
                      "gives probability proportional to length, and conditioned on a subinterval it stays "
                      "uniform. Its mean is the midpoint and its variance is the width squared over "
                      "twelve. And for a cost that is not linear, the expected cost is not the cost at the "
                      "mean: a convex cost or a one-sided penalty makes the plug-in answer too low.") as tr:
            for it, w in zip(items, (6.5, 7.0, 3.5, 3.0, 5.0, 6.0)):
                self.play(FadeIn(it, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(w)
            self.done(tr)

    def practice(self):
        self.head("Practice problems")
        g = VGroup(
            TX(r"\textbf{Wackerly, 7th edition}", font_size=44, color=TEAL_),
            TX(r"\S4.3: Exercises 4.20--4.33; start with 4.20, 4.26, 4.30, 4.32", font_size=44),
            TX(r"\S4.4: Exercises 4.38--4.53; start with 4.41, 4.45--4.47, 4.51", font_size=44),
            VGroup(TX(r"Redo the delayed part with delivery uniform on $(2,4)$:", font_size=44),
                   TX(r"what happens to the 200 AZN gap?", font_size=44)).arrange(DOWN, aligned_edge=LEFT, buff=0.2),
            VGroup(TX(r"\textbf{Week 9, Problem Set 2} on WeBWorK (\S\S4.3--4.4)", font_size=44, color=YELLOW_),
                   TX(r"closes Sunday 15 November, 23:59", font_size=44, color=YELLOW_)).arrange(DOWN, aligned_edge=LEFT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        fill(g, max_scale=1.25)
        with self.say("For practice, from Wackerly, seventh edition. In section four point three, "
                      "exercises four point twenty to four point thirty-three; start with four point "
                      "twenty, twenty-six, thirty and thirty-two. In section four point four, exercises "
                      "four point thirty-eight to four point fifty-three; start with four point forty-one, "
                      "forty-five to forty-seven, and fifty-one.") as tr:
            self.play(FadeIn(g[0]))
            self.play(FadeIn(g[1], shift=UP * 0.2), run_time=0.8)
            self.wait(9)
            self.play(FadeIn(g[2], shift=UP * 0.2), run_time=0.8)
            self.done(tr)
        with self.say("Also redo the delayed part with delivery uniform on two to four days: the same "
                      "mean, a smaller spread. What happens to the two hundred manat gap? And week nine, "
                      "problem set two is open on WeBWorK. It covers these two sections and closes on "
                      "Sunday the fifteenth of November, at eleven fifty-nine at night.") as tr:
            self.play(FadeIn(g[3], shift=UP * 0.2), run_time=0.8)
            self.wait(8)
            self.play(FadeIn(g[4], shift=UP * 0.2), run_time=0.8)
            self.done(tr)

    def closing(self):
        self.head("Thank you")
        nxt = VGroup(T("Next topic", 30, GREY_),
                     T("The normal probability distribution", 46, YELLOW_),
                     T("Wackerly §4.5", 30, GREY_)).arrange(DOWN, buff=0.25)
        oh = VGroup(T("Dr. Samir Orujov", 38),
                    T("Office hours: Wednesday, 16:00–18:00", 34, TEAL_),
                    T("Building D, Room D325", 34, TEAL_),
                    T("Slides and readings: sorujov.net/teaching", 30, GREY_)).arrange(DOWN, buff=0.25)
        g = VGroup(nxt, oh).arrange(DOWN, buff=0.9)
        fill(g, max_scale=1.4)
        with self.say("Next we turn to the most important continuous model of all: the normal "
                      "distribution, Wackerly section four point five. If anything in this lecture is "
                      "unclear, come to office hours, on Wednesdays from four to six in the afternoon, in "
                      "room D three twenty-five. Thank you for watching.") as tr:
            self.play(FadeIn(nxt, shift=UP * 0.2))
            self.wait(5)
            self.play(FadeIn(oh, shift=UP * 0.2))
            self.done(tr)
