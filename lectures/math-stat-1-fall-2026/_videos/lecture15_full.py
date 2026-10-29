"""Lecture 15, full lecture video: moments and moment-generating functions (Wackerly §3.9).

A narrated walk through the whole deck, for students who missed the class. The short
intuition clip is lecture15.py; this one follows the slides and works every example.
"""
import csv
import math

from common import *

ORANGE_ = "#FF9F43"


def TX(s, font_size=36, color=WHITE_, max_w=12.8):
    """Tex on one line (no paragraph wrapping), shrunk to fit the frame if needed."""
    t = Tex(r"\mbox{" + s + "}", font_size=font_size, color=color)
    if t.width > max_w:
        t.scale_to_fit_width(max_w)
    return t



def box(title, lines, color=BLUE_, width=11.5, size=36):
    """A callout: coloured title, then lines of Tex, framed."""
    head = T(title, 28, color)
    body = VGroup(*[TX(s, font_size=size) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    g = VGroup(head, body).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    frame = SurroundingRectangle(g, color=color, buff=0.35, corner_radius=0.12, stroke_width=2.5)
    frame.set_fill(color, opacity=0.06)
    return VGroup(frame, g)


class Lecture15Full(IntuitionScene):
    parts = ("intro", "where", "motivate", "definitions", "branch_moments", "mgf_def", "why_name",
             "theorem", "poisson_mgf", "poisson_moments", "binomial", "linear", "curvature",
             "uniqueness", "recognition", "tps", "case_study", "check", "summary", "closing")

    # --------------------------------------------------------------- helpers
    def title_card(self, title, lecture, text):
        t = T(title, 54)
        if t.width > 12.6:
            t.scale_to_fit_width(12.6)
        sub = T(f"Mathematical Statistics I  ·  Lecture {lecture}  ·  Wackerly §3.9", 28, GREY_).next_to(t, DOWN, buff=0.4)
        with self.say(text) as tr:
            self.play(Write(t), run_time=2)
            self.play(FadeIn(sub))
            self.done(tr)

    def done(self, tr):
        self.wait(max(tr.get_remaining_duration(), 0.25))

    def head(self, s, color=YELLOW_):
        h = T(s, 38, color).to_edge(UP, buff=0.4)
        rule = Line(LEFT * 6.6, RIGHT * 6.6, color=DIM, stroke_width=2).next_to(h, DOWN, buff=0.18)
        self.play(FadeIn(h, shift=DOWN * 0.15), Create(rule), run_time=0.7)
        return VGroup(h, rule)

    # --------------------------------------------------------------- 1
    def intro(self):
        self.title_card("Moments and Moment-Generating Functions", 15,
                        "Hello everyone. This is Wednesday's lecture, lecture fifteen, on moments and "
                        "moment-generating functions. It is Wackerly section three point nine. The video "
                        "follows the slides on the course page, so keep them open if you like, and pause "
                        "whenever you want to try a step yourself.")

    def where(self):
        self.head("Where we are")
        rows = VGroup(
            VGroup(T("Binomial", 32, TEAL_), MathTex(r"\mu=np", font_size=42), T("binomial theorem", 28, GREY_)),
            VGroup(T("Geometric", 32, TEAL_), MathTex(r"\mu=1/p", font_size=42), T("geometric series", 28, GREY_)),
            VGroup(T("Poisson", 32, TEAL_), MathTex(r"\sigma^2=\lambda", font_size=42), MathTex(r"\text{first }E[Y(Y-1)]", font_size=34, color=GREY_)),
        )
        for r in rows:
            r[0].move_to(LEFT * 4.2)
            r[1].move_to(LEFT * 0.6)
            r[2].move_to(RIGHT * 3.6)
        rows.arrange(DOWN, buff=0.6).shift(UP * 0.15)
        for r in rows:
            r[0].set_x(-4.2); r[1].set_x(-0.6); r[2].set_x(3.6)
        with self.say("Think back over chapter three. For every distribution we met, the mean and the "
                      "variance cost us a new trick. For the binomial we used the binomial theorem. For the "
                      "geometric, a geometric series. For the Poisson, we first had to compute the expected "
                      "value of Y times Y minus one.") as tr:
            for r in rows:
                self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(1.2)
            self.done(tr)
        goal = T("Today: one function per distribution", 36, YELLOW_).next_to(rows, DOWN, buff=0.8)
        goal2 = T("every moment by differentiation, and the distribution's name", 30).next_to(goal, DOWN, buff=0.3)
        with self.say("Today we build one function per distribution that hands over every moment by "
                      "differentiation. And, more important, that function names the distribution.") as tr:
            self.play(Write(goal))
            self.play(FadeIn(goal2))
            self.done(tr)

    # --------------------------------------------------------------- 2
    def motivate(self):
        self.head("A motivating question")

        def bars(ys, ps, color, label, x):
            ax = Axes(x_range=[-0.5, 4.5, 1], y_range=[0, 0.8, 0.25], x_length=5, y_length=3.4, tips=False,
                      axis_config={"color": GREY_, "font_size": 24},
                      x_axis_config={"numbers_to_include": [0, 1, 2, 3, 4]},
                      y_axis_config={"numbers_to_include": [0.25, 0.5, 0.75]}).move_to([x, -0.6, 0])
            rs = VGroup()
            for y, p in zip(ys, ps):
                top = ax.c2p(y, p)
                bot = ax.c2p(y, 0)
                r = Rectangle(width=0.55, height=top[1] - bot[1], fill_color=color, fill_opacity=0.8, stroke_width=0)
                r.move_to([bot[0], (top[1] + bot[1]) / 2, 0])
                rs.add(r)
            lab = T(label, 30, color).next_to(ax, UP, buff=0.3)
            return VGroup(ax, rs, lab)

        A = bars([1, 3], [0.5, 0.5], BLUE_, "Branch A", -3.4)
        B = bars([0, 2, 4], [0.125, 0.75, 0.125], ORANGE_, "Branch B", 3.4)
        with self.say("Here is the question we started with. A bank's treasury in Baku counts large corporate "
                      "payments, of a million manat or more, cleared per hour at two branches. At branch A "
                      "the count is one or three, each with probability one half. At branch B it is two "
                      "with probability three quarters, and zero or four with probability one eighth each.") as tr:
            self.play(Create(A[0]), FadeIn(A[2]))
            self.play(GrowFromEdge(A[1], DOWN))
            self.wait(2)
            self.play(Create(B[0]), FadeIn(B[2]))
            self.play(GrowFromEdge(B[1], DOWN))
            self.done(tr)
        same = MathTex(r"\mu=2,\qquad \sigma^2=1", r"\quad\text{for both}", font_size=44).to_edge(DOWN, buff=0.45)
        same[0].set_color(YELLOW_)
        with self.say("Both counts have mean two and variance one. Check that yourself; it takes a minute. "
                      "So if two counts share a mean and a variance, is the risk the same? Clearly not. "
                      "Branch B can produce a four, and branch A never can. Which extra numbers would tell "
                      "them apart?") as tr:
            self.play(Write(same))
            self.done(tr)

    def definitions(self):
        self.head("Definitions 3.12 and 3.13")
        d1 = box("Definition 3.12", [r"The $k$th moment of $Y$ about the origin is $E(Y^k)$, denoted $\mu'_k$."], BLUE_)
        d2 = box("Definition 3.13", [r"The $k$th moment of $Y$ about its mean, the $k$th central moment,",
                                     r"is $E\big[(Y-\mu)^k\big]$, denoted $\mu_k$."], TEAL_)
        VGroup(d1, d2).arrange(DOWN, buff=0.45, aligned_edge=LEFT).shift(UP * 0.35)
        with self.say("Those numbers are the moments. Definition three point twelve: the k-th moment of Y "
                      "about the origin is the expected value of Y to the k. We write it mu prime k.") as tr:
            self.play(FadeIn(d1, shift=UP * 0.2))
            self.done(tr)
        with self.say("Definition three point thirteen: the k-th moment about the mean, the k-th central "
                      "moment, is the expected value of Y minus mu, to the k. We write it mu k, with no "
                      "prime.") as tr:
            self.play(FadeIn(d2, shift=UP * 0.2))
            self.done(tr)
        f = MathTex(r"\mu'_1=\mu,\qquad \mu_2=\sigma^2,\qquad", r"\sigma^2=\mu'_2-(\mu'_1)^2", font_size=44)
        f[1].set_color(YELLOW_)
        f.to_edge(DOWN, buff=0.55)
        with self.say("So mu prime one is the mean, and mu two is the variance. Theorem three point six, which "
                      "you know as: the variance is E of Y squared minus mu squared, now reads: sigma squared "
                      "equals mu prime two minus mu prime one, squared.") as tr:
            self.play(Write(f), run_time=2.5)
            self.done(tr)

    def branch_moments(self):
        self.head("Two branches, four moments")
        data = [["1", "2", "2", "0", "0"],
                ["2", "5", "5", "1", "1"],
                ["3", "14", "14", "0", "0"],
                ["4", "41", "44", "1", "4"]]
        tab = MathTable(data,
                        col_labels=[MathTex("k"), MathTex(r"\mu'_k\ (A)"), MathTex(r"\mu'_k\ (B)"),
                                    MathTex(r"\mu_k\ (A)"), MathTex(r"\mu_k\ (B)")],
                        include_outer_lines=False, line_config={"stroke_color": DIM, "stroke_width": 1.5},
                        h_buff=0.9, v_buff=0.35, element_to_mobject_config={"font_size": 40}).scale(0.95)
        tab.shift(UP * 0.1)
        for j in (2, 4):
            tab.get_columns()[j - 1].set_color(BLUE_)
        for j in (3, 5):
            tab.get_columns()[j - 1].set_color(ORANGE_)
        tab.get_columns()[0].set_color(GREY_)
        with self.say("Let's compute the first four moments for both branches, about the origin and about the "
                      "mean, which is two for both. For branch A, Y to the fourth is one or eighty-one, each "
                      "with probability one half, so mu prime four is forty-one. For branch B it is zero, "
                      "sixteen or two hundred and fifty-six, with weights one eighth, three quarters and one "
                      "eighth. That gives forty-four.") as tr:
            self.play(Create(tab.get_horizontal_lines()), Create(tab.get_vertical_lines()),
                      FadeIn(tab.get_col_labels()), run_time=1.2)
            for i in range(1, 5):
                self.play(FadeIn(tab.get_rows()[i]), run_time=0.7)
                self.wait(0.8)
            self.done(tr)
        hl = SurroundingRectangle(tab.get_rows()[4], color=RED_, buff=0.1)
        note = T("Same up to k = 3. The fourth moment separates them: B has fatter tails.", 30, RED_).to_edge(DOWN, buff=0.5)
        with self.say("The two branches agree on the first three moments and separate only at the fourth. The "
                      "central fourth moment is one for A and four for B. Branch B puts more mass far from "
                      "the mean: it has fatter tails. So mean and variance do not pin down a distribution. "
                      "The whole sequence of moments, usually, does.") as tr:
            self.play(Create(hl))
            self.play(FadeIn(note))
            self.done(tr)

    # --------------------------------------------------------------- 3
    def mgf_def(self):
        self.head("Definition 3.14: the moment-generating function")
        d = box("Definition 3.14",
                [r"The moment-generating function of $Y$ is $m(t)=E\left(e^{tY}\right)$.",
                 r"It exists if $m(t)$ is finite for $|t|\le b$, for some constant $b>0$."], YELLOW_)
        d.shift(UP * 1.6)
        with self.say("To collect all the moments at once, we need one more definition. Definition three point "
                      "fourteen: the moment-generating function, m of t, is the expected value of e to the t Y. "
                      "We say the MGF exists if there is a positive constant b such that m of t is finite for "
                      "every t between minus b and b.") as tr:
            self.play(FadeIn(d, shift=UP * 0.2))
            self.done(tr)
        s = MathTex(r"m(t)=\sum_y e^{ty}\,p(y)", r"\qquad m(0)=\sum_y p(y)=1", font_size=46).next_to(d, DOWN, buff=0.55)
        s[1].set_color(TEAL_)
        with self.say("For a discrete Y it is a single sum: the sum over y of e to the t y times p of y. Notice "
                      "two things. It is a function of t, not of y, because the y's have been summed out. And "
                      "at t equals zero every exponential is one, so m of zero is the sum of the probabilities. "
                      "Every MGF passes through the point zero, one.") as tr:
            self.play(Write(s[0]))
            self.wait(4)
            self.play(Write(s[1]))
            self.done(tr)
        ex = VGroup(
            MathTex(r"m_A(t)=\tfrac12 e^{\,t}+\tfrac12 e^{3t}", font_size=44, color=BLUE_),
            MathTex(r"m_B(t)=\tfrac18+\tfrac34 e^{2t}+\tfrac18 e^{4t}", font_size=44, color=ORANGE_),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).next_to(s, DOWN, buff=0.55)
        with self.say("For our two branches, m A of t is one half e to the t, plus one half e to the three t. "
                      "And m B of t is one eighth, plus three quarters e to the two t, plus one eighth e to "
                      "the four t. Read it like this: the numbers multiplying t in the exponents are the "
                      "values of Y, and the coefficients in front are their probabilities.") as tr:
            self.play(Write(ex[0]))
            self.play(Write(ex[1]))
            self.done(tr)

    def why_name(self):
        self.head('Why "moment-generating"?')
        e1 = MathTex(r"e^{ty}", "=", "1", "+", "ty", "+", r"\frac{(ty)^2}{2!}", "+", r"\frac{(ty)^3}{3!}", "+", r"\cdots",
                     font_size=48).shift(UP * 2.0)
        e2 = MathTex(r"m(t)", "=", "1", "+", r"t\,\mu'_1", "+", r"\frac{t^2}{2!}\,\mu'_2", "+", r"\frac{t^3}{3!}\,\mu'_3", "+", r"\cdots",
                     font_size=48).next_to(e1, DOWN, buff=1.0)
        for k, c in zip([4, 6, 8], [TEAL_, RED_, PURPLE_]):
            e2[k].set_color(c)
        with self.say("Why is it called moment-generating? Expand e to the t y as a power series: one, plus t y, "
                      "plus t y squared over two factorial, plus t y cubed over three factorial, and so on.") as tr:
            self.play(Write(e1), run_time=3)
            self.done(tr)
        with self.say("Now take expectations term by term. The expected value of Y is mu prime one, the expected "
                      "value of Y squared is mu prime two, and so on. So m of t is one, plus t times mu prime "
                      "one, plus t squared over two factorial times mu prime two, and so on.") as tr:
            ar = Arrow(e1.get_bottom(), e2.get_top(), color=GREY_, stroke_width=3, buff=0.12,
                       max_tip_length_to_length_ratio=0.3)
            el = MathTex(r"E[\,\cdot\,]\ \text{term by term}", font_size=32, color=GREY_).next_to(ar, RIGHT, buff=0.2)
            self.play(GrowArrow(ar), FadeIn(el), run_time=0.8)
            self.play(Write(e2[0:4]), run_time=1)
            for k in (4, 6, 8):
                self.play(Indicate(e1[k], color=e2[k].get_color(), scale_factor=1.15), run_time=0.8)
                self.play(TransformFromCopy(e1[k], e2[k]), run_time=0.9)
                self.play(FadeIn(e2[k + 1]), run_time=0.3)
            self.play(FadeIn(e2[10]), run_time=0.3)
            self.done(tr)
        self.play(FadeOut(ar), FadeOut(el), run_time=0.5)
        key = box("The point", [r"$\mu'_k$ is the coefficient of $t^k/k!$ in $m(t)$.",
                                r"The MGF is every moment of $Y$ packed into one function."], YELLOW_).to_edge(DOWN, buff=0.5)
        with self.say("The k-th moment is the coefficient of t to the k over k factorial. The MGF is every "
                      "moment of Y packed into one function. Swapping the expectation with the infinite sum "
                      "is justified whenever m of t exists near zero, which is why the definition asks for "
                      "that.") as tr:
            self.play(FadeIn(key, shift=UP * 0.2))
            self.done(tr)

    def theorem(self):
        self.head("Theorem 3.12")
        th = box("Theorem 3.12", [r"If $m(t)$ exists, then for any positive integer $k$,\ \ "
                                  r"$\displaystyle m^{(k)}(0)=\left.\frac{d^k m(t)}{dt^k}\right|_{t=0}=\mu'_k$."], YELLOW_, size=36)
        th.shift(UP * 2.0)
        with self.say("To get a moment back out, we differentiate. Theorem three point twelve: if m of t exists, "
                      "then for any positive integer k, the k-th derivative of m at zero equals mu prime k.") as tr:
            self.play(FadeIn(th, shift=UP * 0.2))
            self.done(tr)
        l0 = MathTex(r"m(t)", "=", "1", "+", r"t\mu'_1", "+", r"\tfrac{t^2}{2!}\mu'_2", "+", r"\tfrac{t^3}{3!}\mu'_3", "+", r"\cdots", font_size=42)
        l1 = MathTex(r"m'(t)", "=", r"\mu'_1", "+", r"t\mu'_2", "+", r"\tfrac{t^2}{2!}\mu'_3", "+", r"\cdots", font_size=42)
        l2 = MathTex(r"m''(t)", "=", r"\mu'_2", "+", r"t\mu'_3", "+", r"\cdots", font_size=42)
        lines = VGroup(l0, l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(th, DOWN, buff=0.5)
        r1 = MathTex(r"\Rightarrow\ m'(0)=\mu'_1", font_size=42, color=TEAL_).next_to(l1, RIGHT, buff=0.6)
        r2 = MathTex(r"\Rightarrow\ m''(0)=\mu'_2", font_size=42, color=RED_).next_to(l2, RIGHT, buff=0.6)
        r1.set_x(4.3); r2.set_x(4.3)
        with self.say("Watch it happen. Start from the series. Differentiate once: the constant one disappears, "
                      "the t mu prime one term leaves mu prime one, and every other term still carries a power "
                      "of t. Set t to zero, and only mu prime one survives.") as tr:
            self.play(Write(l0), run_time=1.5)
            self.wait(1.5)
            x1 = Cross(l0[2], stroke_color=RED_, stroke_width=4).scale(1.6)
            self.play(Create(x1), run_time=0.5)
            self.play(Write(l1), run_time=1.5)
            self.wait(2)
            t0 = T("t = 0:", 26, GREY_).next_to(r1, UP, buff=0.15)
            self.play(l1[4:].animate.set_opacity(0.3), l1[2].animate.set_color(TEAL_), FadeIn(t0), run_time=1)
            self.play(Write(r1))
            self.done(tr)
        with self.say("Differentiate twice, and only mu prime two survives at zero. In general, differentiating "
                      "k times kills every term below t to the k, the t to the k term leaves mu prime k, and "
                      "every higher term still has a t in it, so it dies at zero.") as tr:
            self.play(Write(l2), run_time=1.5)
            self.play(l2[4:].animate.set_opacity(0.3), l2[2].animate.set_color(RED_), run_time=1)
            self.play(Write(r2))
            self.done(tr)
        self.play(FadeOut(VGroup(lines, r1, r2, x1, t0)))
        prac = VGroup(MathTex(r"\mu=m'(0)", font_size=52, color=TEAL_),
                      MathTex(r"\sigma^2=m''(0)-\big[m'(0)\big]^2", font_size=52, color=RED_)).arrange(DOWN, buff=0.5).shift(DOWN * 0.9)
        with self.say("In practice you need only two formulas. The mean is m prime of zero. And the variance is "
                      "m double prime of zero, minus m prime of zero squared. That is theorem three point six "
                      "again, written with derivatives.") as tr:
            self.play(Write(prac[0]))
            self.play(Write(prac[1]))
            self.done(tr)

    # --------------------------------------------------------------- 4
    def poisson_mgf(self):
        self.head("Example 3.23: the Poisson MGF")
        setup = TX(r"Daily motor claims at a Baku insurer: $Y\sim\text{Poisson}(\lambda)$.", font_size=38).shift(UP * 2.3)
        s1 = MathTex(r"m(t)=\sum_{y=0}^{\infty} e^{ty}\,\frac{\lambda^y e^{-\lambda}}{y!}", font_size=46)
        s2 = MathTex(r"=e^{-\lambda}\sum_{y=0}^{\infty}\frac{(\lambda e^{t})^y}{y!}", font_size=46)
        s3 = MathTex(r"=e^{-\lambda}\,e^{\lambda e^{t}}", font_size=46)
        s4 = MathTex(r"=e^{\lambda(e^{t}-1)}", font_size=50, color=YELLOW_)
        g = VGroup(s1, s2, s3, s4).arrange(DOWN, aligned_edge=LEFT, buff=0.32).next_to(setup, DOWN, buff=0.45)
        g.shift(LEFT * 1.2)
        for s in (s2, s3, s4):
            s.shift(RIGHT * 1.3)
        with self.say("Now let's compute some MGFs. Example three point twenty-three. A motor insurer in Baku "
                      "counts its claims per day, and the count is Poisson with mean lambda. By definition, m "
                      "of t is the sum over y, from zero to infinity, of e to the t y times lambda to the y, e "
                      "to the minus lambda, over y factorial.") as tr:
            self.play(FadeIn(setup))
            self.play(Write(s1), run_time=2.5)
            self.done(tr)
        with self.say("Take e to the minus lambda outside the sum. Then e to the t y times lambda to the y is "
                      "lambda e to the t, all to the power y.") as tr:
            self.play(Write(s2), run_time=2)
            self.done(tr)
        hint = VGroup(T("Recall the Taylor series", 24, GREY_),
                      MathTex(r"e^{x}=\sum_{y=0}^{\infty}\frac{x^{y}}{y!}", font_size=36, color=GREY_),
                      MathTex(r"\text{here } x=\lambda e^{t}", font_size=32, color=GREY_)).arrange(DOWN, buff=0.2)
        hint.next_to(VGroup(s2, s3), RIGHT, buff=0.9)
        if hint.get_right()[0] > 6.7:
            hint.shift(LEFT * (hint.get_right()[0] - 6.7))
        with self.say("What remains is the Taylor series of the exponential function, evaluated at lambda e to "
                      "the t. So m of t is e to the minus lambda times e to the lambda e to the t. Combine the "
                      "exponents: m of t equals e to the power lambda times e to the t minus one.") as tr:
            self.play(FadeIn(hint, shift=UP * 0.2), run_time=1)
            self.wait(1.5)
            self.play(Write(s3), run_time=1.5)
            self.wait(2.5)
            self.play(Write(s4), run_time=1.5)
            self.play(Circumscribe(s4, color=YELLOW_))
            self.done(tr)

    def poisson_moments(self):
        self.head("Example 3.24: mean and variance from the MGF")
        a = MathTex(r"m'(t)=e^{\lambda(e^t-1)}\,\lambda e^t", font_size=44)
        b = MathTex(r"m''(t)=e^{\lambda(e^t-1)}(\lambda e^t)^2+e^{\lambda(e^t-1)}\,\lambda e^t", font_size=44)
        VGroup(a, b).arrange(DOWN, aligned_edge=LEFT, buff=0.4).shift(UP * 1.4)
        with self.say("Example three point twenty-four. Differentiate with the chain rule: m prime of t is e to "
                      "the lambda times e to the t minus one, times lambda e to the t. Differentiate again with "
                      "the product rule, and you get two terms.") as tr:
            self.play(Write(a), run_time=2)
            self.play(Write(b), run_time=2.5)
            self.done(tr)
        c = MathTex(r"\mu=m'(0)=\lambda,\qquad \mu'_2=m''(0)=\lambda^2+\lambda", font_size=44, color=TEAL_)
        d = MathTex(r"\sigma^2=\lambda^2+\lambda-\lambda^2=\lambda", font_size=48, color=YELLOW_)
        VGroup(c, d).arrange(DOWN, buff=0.4).next_to(b, DOWN, buff=0.6)
        with self.say("At t equals zero, every e to the something becomes one. So the mean is lambda, and mu "
                      "prime two is lambda squared plus lambda. The variance is lambda squared plus lambda, "
                      "minus lambda squared, which is lambda. That is theorem three point eleven, with no "
                      "detour through the expected value of Y times Y minus one.") as tr:
            self.play(Write(c), run_time=2)
            self.wait(2)
            self.play(Write(d), run_time=2)
            self.done(tr)
        n = TX(r"$\lambda=4.5$ claims a day: $\ \mu'_2=24.75,\ \ \sigma^2=4.5,\ \ \sigma=2.12$", font_size=40).to_edge(DOWN, buff=0.5)
        with self.say("With four point five claims a day, mu prime two is twenty-four point seven five, the "
                      "variance is four point five, and the standard deviation is about two point one two.") as tr:
            self.play(FadeIn(n, shift=UP * 0.2))
            self.done(tr)

    def binomial(self):
        self.head("The binomial MGF: winning trades")
        setup = TX(r"An FX dealer books $n=10$ independent trades a day, each profitable with $p=0.6$.",
                    font_size=36).shift(UP * 2.35)
        m = MathTex(r"m(t)=\sum_{y=0}^{n}\binom{n}{y}(pe^t)^y q^{\,n-y}=(pe^t+q)^n", font_size=46).next_to(setup, DOWN, buff=0.45)
        with self.say("Next, the binomial. An FX dealer books ten independent trades a day, and each is "
                      "profitable with probability point six. Y, the number of winning trades, is binomial "
                      "with n ten and p point six. Its MGF is the sum of n choose y, times p e to the t, to "
                      "the y, times q to the n minus y. By the binomial theorem, that is p e to the t plus q, "
                      "all to the n. This is exercise three point one forty-five.") as tr:
            self.play(FadeIn(setup))
            self.play(Write(m), run_time=3)
            self.done(tr)
        d1 = MathTex(r"m'(t)=n(pe^t+q)^{n-1}pe^t", r"\ \Rightarrow\ m'(0)=np=6", font_size=40)
        d2 = MathTex(r"m''(t)=n(n-1)(pe^t+q)^{n-2}(pe^t)^2+n(pe^t+q)^{n-1}pe^t", font_size=40)
        d3 = MathTex(r"m''(0)=n(n-1)p^2+np=32.4+6=38.4", font_size=40)
        d4 = MathTex(r"V(Y)=38.4-6^2=2.4=npq", font_size=46, color=YELLOW_)
        g = VGroup(d1, d2, d3, d4).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(m, DOWN, buff=0.5)
        d1[1].set_color(TEAL_)
        with self.say("Differentiate once. m prime of t is n times p e to the t plus q, to the n minus one, "
                      "times p e to the t. At zero, p plus q is one, so m prime of zero is n p, which is six "
                      "winning trades.") as tr:
            self.play(Write(d1), run_time=2.5)
            self.done(tr)
        with self.say("Differentiate again, with the product rule. At zero, m double prime is n times n minus "
                      "one times p squared, plus n p. That is ninety times point three six, which is thirty-two "
                      "point four, plus six: thirty-eight point four. So the variance is thirty-eight point four "
                      "minus six squared, which is two point four. And that is n p q, as we found in lecture "
                      "eleven.") as tr:
            self.play(Write(d2), run_time=2.5)
            self.wait(1.5)
            self.play(Write(d3), run_time=2)
            self.wait(2)
            self.play(Write(d4), run_time=1.5)
            self.done(tr)

    def linear(self):
        self.head("From trade count to daily P&L")
        setup = MathTex(r"X=2Y-(10-Y)=3Y-10", r"\quad\text{(thousand AZN)}", font_size=44).shift(UP * 2.3)
        setup[1].set_color(GREY_)
        with self.say("Now suppose each winning trade earns two thousand manat and each losing trade costs one "
                      "thousand. Then the daily profit and loss is X equals two Y minus ten minus Y, which is "
                      "three Y minus ten. What is its MGF?") as tr:
            self.play(Write(setup), run_time=2)
            self.done(tr)
        rule = box("Exercise 3.156", [r"If $X=aY+b$, then $m_X(t)=E\big(e^{t(aY+b)}\big)=e^{bt}\,E\big(e^{(at)Y}\big)=e^{bt}\,m_Y(at)$."],
                   YELLOW_, size=38).next_to(setup, DOWN, buff=0.5)
        with self.say("Exercise three point one fifty-six gives the rule. If X is a Y plus b, then the expected "
                      "value of e to the t times a Y plus b splits into e to the b t, which is a constant, "
                      "times the expected value of e to the a t times Y. That is m Y evaluated at a t. The "
                      "shift comes out as a factor; the scale goes inside.") as tr:
            self.play(FadeIn(rule, shift=UP * 0.2))
            self.done(tr)
        mx = MathTex(r"m_X(t)=e^{-10t}\,(0.6e^{3t}+0.4)^{10}", font_size=46, color=TEAL_).next_to(rule, DOWN, buff=0.5)
        res = MathTex(r"E(X)=b+a\mu=3(6)-10=8,\qquad V(X)=a^2\sigma^2=9(2.4)=21.6", font_size=40).next_to(mx, DOWN, buff=0.45)
        sd = MathTex(r"\sigma_X=\sqrt{21.6}\approx4.65", font_size=40).next_to(res, DOWN, buff=0.3)
        with self.say("Here a is three and b is minus ten, so m X of t is e to the minus ten t, times point six "
                      "e to the three t plus point four, all to the tenth.") as tr:
            self.play(Write(mx), run_time=2)
            self.done(tr)
        with self.say("Differentiate with the product rule and set t to zero. You get b times m Y of zero plus a "
                      "times m Y prime of zero, which is b plus a mu: three times six minus ten, eight thousand "
                      "manat a day. Do the second derivative and the shift drops out of the variance, while the "
                      "scale enters squared: nine times two point four, which is twenty-one point six. The "
                      "standard deviation is about four point six five thousand manat.") as tr:
            self.play(Write(res), run_time=2.5)
            self.wait(4)
            self.play(Write(sd))
            self.done(tr)

    def curvature(self):
        self.head("Same slope, different curvature")
        ax = Axes(x_range=[-0.8, 0.4, 0.2], y_range=[0, 5, 1], x_length=9, y_length=5.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 24, "include_numbers": True}).shift(DOWN * 0.45 + LEFT * 1.2)
        tl = MathTex("t", font_size=34, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.2)
        P = ax.plot(lambda t: math.exp(4.5 * (math.exp(t) - 1)), x_range=[-0.8, 0.305], color=RED_, stroke_width=5)
        B = ax.plot(lambda t: (0.45 * math.exp(t) + 0.55) ** 10, x_range=[-0.8, 0.328], color=BLUE_, stroke_width=5)
        tan = DashedLine(ax.c2p(-0.22, 1 - 0.99), ax.c2p(0.4, 2.8), color=GREY_)
        dot = Dot(ax.c2p(0, 1), color=YELLOW_, radius=0.09)
        lp = TX(r"Poisson$(4.5)$: $\sigma^2=4.5$", font_size=34, color=RED_)
        lb = TX(r"Bin$(10,0.45)$: $\sigma^2=2.475$", font_size=34, color=BLUE_)
        leg = VGroup(lp, lb).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        leg.next_to(ax.c2p(-0.78, 4.9), DR, buff=0)
        with self.say("Here is a picture of theorem three point twelve. Take two counts with the same mean, four "
                      "point five: a Poisson with lambda four point five, and a binomial with n ten and p point "
                      "four five.") as tr:
            self.play(Create(ax), FadeIn(tl))
            self.play(Create(P), FadeIn(lp), run_time=1.5)
            self.play(Create(B), FadeIn(lb), run_time=1.5)
            self.done(tr)
        sl = MathTex(r"\text{slope } m'(0)=\mu=4.5", font_size=30, color=GREY_).next_to(ax.c2p(0.4, 2.8), RIGHT, buff=0.25)
        with self.say("Both curves pass through zero, one, as every MGF must. And both leave that point along "
                      "the same tangent line, with slope four point five, because the slope at zero is the "
                      "mean.") as tr:
            self.play(FadeIn(dot), Create(tan))
            self.wait(2)
            self.play(FadeIn(sl))
            self.done(tr)
        n = VGroup(MathTex(r"m''(0)=E(Y^2)", font_size=38, color=YELLOW_),
                   MathTex(r"24.75\ \text{vs}\ 22.725", font_size=38)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(leg, DOWN, buff=0.6, aligned_edge=LEFT)
        with self.say("They differ in curvature. The second derivative at zero is E of Y squared: twenty-four "
                      "point seven five for the Poisson, twenty-two point seven two five for the binomial. The "
                      "Poisson bends upward faster, because its variance is larger. Slope at zero is the mean; "
                      "curvature at zero carries the spread.") as tr:
            self.play(Write(n))
            self.done(tr)

    # --------------------------------------------------------------- 5
    def uniqueness(self):
        self.head("The primary use: uniqueness")
        u = box("Uniqueness", [r"If $m_Y(t)=m_Z(t)$ for all $|t|<b$, for some $b>0$,",
                               r"then $Y$ and $Z$ have the same distribution."], YELLOW_)
        u.shift(UP * 1.1)
        with self.say("Computing moments is useful, but it is not the main reason we study MGFs. The main reason "
                      "is uniqueness. If an MGF exists, it is unique to its distribution. If Y and Z have the "
                      "same MGF on some interval around zero, then Y and Z have the same distribution. An MGF "
                      "is a fingerprint.") as tr:
            self.play(FadeIn(u, shift=UP * 0.2))
            self.done(tr)
        e1 = TX(r"Monthly operational-loss events at a bank: $m_Y(t)=e^{3.2(e^t-1)}$", font_size=38).next_to(u, DOWN, buff=0.8)
        e2 = MathTex(r"\Rightarrow\ Y\sim\text{Poisson}(3.2):\ \ \mu=\sigma^2=3.2,\ \ P(Y=0)=e^{-3.2}=0.0408",
                     font_size=40, color=TEAL_).next_to(e1, DOWN, buff=0.5)
        with self.say("Example three point twenty-five, in a banking setting. A bank's monthly count of "
                      "operational-loss events has m of t equal to e to the three point two times e to the t "
                      "minus one. We recognise that: it is the Poisson MGF with lambda three point two. So Y is "
                      "Poisson with mean and variance three point two, and a month with no loss events has "
                      "probability e to the minus three point two, about point zero four.") as tr:
            self.play(FadeIn(e1))
            self.wait(3)
            self.play(Write(e2), run_time=2)
            self.done(tr)

    def recognition(self):
        self.head("A recognition table")
        tab = MobjectTable(
            [[T("Binomial(n, p)", 30), MathTex(r"(pe^t+q)^n", font_size=42), T("Exercise 3.145", 26, GREY_)],
             [T("Geometric(p)", 30), MathTex(r"\dfrac{pe^t}{1-qe^t}", font_size=42), T("Exercise 3.147", 26, GREY_)],
             [T("Poisson(λ)", 30), MathTex(r"e^{\lambda(e^t-1)}", font_size=42), T("Example 3.23", 26, GREY_)]],
            col_labels=[T("Distribution", 28, YELLOW_), MathTex("m(t)", font_size=40, color=YELLOW_), T("Source", 28, YELLOW_)],
            include_outer_lines=False, line_config={"stroke_color": DIM, "stroke_width": 1.5}, h_buff=0.9, v_buff=0.35)
        tab.shift(UP * 0.8)
        with self.say("Here are the three MGFs to recognise on sight. Binomial: p e to the t plus q, to the n. "
                      "Geometric: p e to the t over one minus q e to the t, which is exercise three point one "
                      "forty-seven. Poisson: e to the lambda times e to the t minus one.") as tr:
            self.play(Create(tab), run_time=3)
            self.done(tr)
        ex = VGroup(TX(r"12 SME loan applications, $Y$ approved: $m(t)=(0.3e^t+0.7)^{12}$", font_size=38),
                    MathTex(r"Y\sim\text{Bin}(12,0.3):\ \ \mu=3.6,\ \ \sigma^2=2.52,\ \ P(Y=0)=0.7^{12}=0.0138",
                            font_size=38, color=TEAL_)).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.55)
        with self.say("For example, a bank receives twelve loan applications from small businesses, and Y, the "
                      "number approved, has m of t equal to point three e to the t plus point seven, to the "
                      "twelfth. That is the binomial with n twelve and p point three. So the mean is three "
                      "point six, the variance is two point five two, and the chance that none is approved is "
                      "point seven to the twelfth, about point zero one four.") as tr:
            self.play(FadeIn(ex[0]))
            self.wait(4)
            self.play(Write(ex[1]), run_time=2)
            self.done(tr)

    def tps(self):
        self.head("Think–Pair–Share: try it yourself")
        m = MathTex(r"m(t)=0.5+0.3e^{t}+0.2e^{2t}", font_size=52, color=YELLOW_).shift(UP * 1.6)
        ctx = T("Regional network outages per day at a mobile operator", 30, GREY_).next_to(m, UP, buff=0.4)
        qs = VGroup(T("1.  What is the distribution of Y?", 32),
                    T("2.  Find E(Y) and V(Y) from m(t).", 32),
                    T("3.  Check both directly from p(y).", 32)).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(m, DOWN, buff=0.6)
        pause = T("Pause the video and take four minutes.", 34, RED_).to_edge(DOWN, buff=0.6)
        with self.say("In class this was the think, pair, share exercise. A mobile operator's count of regional "
                      "network outages per day has m of t equal to point five, plus point three e to the t, "
                      "plus point two e to the two t. First, what is the distribution of Y? Second, find the "
                      "mean and the variance from m of t. Third, check both directly from p of y. Pause the "
                      "video now and try it, then come back for the solution.") as tr:
            self.play(FadeIn(ctx), Write(m))
            for q in qs:
                self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(1.5)
            self.play(FadeIn(pause))
            self.done(tr)
        self.wait(2)
        self.play(FadeOut(VGroup(qs, pause)))
        s1 = MathTex(r"p(0)=0.5,\quad p(1)=0.3,\quad p(2)=0.2", font_size=44, color=TEAL_).next_to(m, DOWN, buff=0.6)
        with self.say("Here is the solution. Match the MGF term by term with the sum of e to the t y times p of "
                      "y. The constant is e to the zero t, so p of zero is point five. Then p of one is point "
                      "three and p of two is point two. By uniqueness, that is the distribution.") as tr:
            self.play(Write(s1), run_time=2)
            self.done(tr)
        s2 = MathTex(r"m'(t)=0.3e^t+0.4e^{2t}\ \Rightarrow\ E(Y)=0.7", font_size=42).next_to(s1, DOWN, buff=0.4)
        s3 = MathTex(r"m''(t)=0.3e^t+0.8e^{2t}\ \Rightarrow\ E(Y^2)=1.1", font_size=42).next_to(s2, DOWN, buff=0.3)
        s4 = MathTex(r"V(Y)=1.1-0.7^2=0.61", font_size=46, color=YELLOW_).next_to(s3, DOWN, buff=0.35)
        with self.say("m prime of t is point three e to the t plus point four e to the two t, so the mean is "
                      "point seven. m double prime is point three e to the t plus point eight e to the two t, so "
                      "E of Y squared is one point one. The variance is one point one minus point four nine, "
                      "which is point six one. Directly from p of y: zero times point five, plus one times "
                      "point three, plus two times point two, is point seven. Same numbers. The MGF is just a "
                      "disciplined way of doing those sums.") as tr:
            self.play(Write(s2), run_time=2)
            self.wait(2)
            self.play(Write(s3), run_time=2)
            self.wait(1.5)
            self.play(Write(s4))
            self.done(tr)

    # --------------------------------------------------------------- 6
    def case_study(self):
        self.head("Case study: do stock returns have normal moments?")
        rows = [r for r in csv.reader(open("sp500.csv"))][1:]
        c = [float(r[1]) for r in rows if r[1] not in (".", "")]
        r = [math.log(b / a) for a, b in zip(c, c[1:])]
        n = len(r)
        mu = sum(r) / n
        sd = (sum((x - mu) ** 2 for x in r) / (n - 1)) ** 0.5
        z = [(x - mu) / sd for x in r]
        ctx = VGroup(T("S&P 500 daily log returns, FRED, Sep 2016 – Sep 2026: 2,513 days", 28, GREY_),
                     MathTex(r"Z=(Y-\bar Y)/s", font_size=38)).arrange(RIGHT, buff=0.5)
        ctx.scale_to_fit_width(min(ctx.width, 12.6)).to_edge(UP, buff=1.25)
        with self.say("Moments are not only a classroom device. Take ten years of daily log returns on the S and "
                      "P five hundred, from FRED, September twenty sixteen to September twenty twenty-six: two "
                      "thousand five hundred and thirteen trading days. Standardise them, so that Z has mean "
                      "zero and variance one.") as tr:
            self.play(FadeIn(ctx))
            self.done(tr)
        ax = Axes(x_range=[-6, 6, 2], y_range=[0, 0.8, 0.2], x_length=7.4, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).to_edge(LEFT, buff=0.6).shift(DOWN * 0.7)
        bw = 0.2
        edges = [-6 + i * bw for i in range(61)]
        bars = VGroup()
        for lo in edges[:-1]:
            cnt = sum(1 for v in z if lo <= v < lo + bw)
            d = cnt / (n * bw)
            if d <= 0:
                continue
            p0, p1 = ax.c2p(lo, 0), ax.c2p(lo + bw, min(d, 0.8))
            bars.add(Rectangle(width=p1[0] - p0[0], height=p1[1] - p0[1], fill_color="#8BA3C7",
                               fill_opacity=0.85, stroke_color=BG, stroke_width=1).move_to([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0]))
        nc = ax.plot(lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi), x_range=[-6, 6], color=RED_, stroke_width=4)
        nl = T("normal", 26, RED_).next_to(ax.c2p(2.0, 0.25), RIGHT, buff=0.1)
        stats = VGroup(
            MathTex(r"E(Z^3)", r"=-0.68", font_size=40),
            T("normal: 0", 26, GREY_),
            MathTex(r"E(Z^4)", r"=19.7", font_size=40),
            T("normal: 3", 26, GREY_),
            MathTex(r"P(|Z|>3)", r"=1.43\%", font_size=40),
            T("normal: 0.27%", 26, GREY_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(RIGHT, buff=0.7).shift(DOWN * 0.6)
        for k in (0, 2, 4):
            stats[k][1].set_color(YELLOW_)
        with self.say("A normal distribution has third central moment zero and fourth moment three. The data "
                      "give minus point six eight for the third, a left tail, and nineteen point seven for the "
                      "fourth. Not three: nearly twenty.") as tr:
            self.play(Create(ax), FadeIn(bars, lag_ratio=0.02), run_time=2)
            self.play(Create(nc), FadeIn(nl))
            self.play(FadeIn(stats[0:2]))
            self.wait(1.5)
            self.play(FadeIn(stats[2:4]))
            self.done(tr)
        with self.say("And a day beyond three standard deviations happened on one point four percent of days, "
                      "against point two seven percent for the normal: more than five times as often. The worst "
                      "day, the sixteenth of March twenty twenty, was eleven standard deviations below the "
                      "mean. The histogram rises above the normal curve in the middle and in the tails. A "
                      "model with normal moments understates both the quiet days and the crashes. The fourth "
                      "moment is how we measure that.") as tr:
            self.play(FadeIn(stats[4:6]))
            self.wait(5)
            worst = VGroup(T("16 Mar 2020", 24, RED_), MathTex(r"z=-11.2", font_size=30, color=RED_)).arrange(DOWN, buff=0.08)
            worst.move_to(ax.c2p(-4.2, 0.55))
            warr = Arrow(worst.get_bottom(), ax.c2p(-6.1, 0.02), color=RED_, buff=0.1, stroke_width=3,
                         max_tip_length_to_length_ratio=0.12)
            self.play(FadeIn(worst), GrowArrow(warr), run_time=1)
            self.done(tr)

    def check(self):
        self.head("Check yourself: three quick questions")
        qs = [
            (r"Chargebacks per day: $m(t)=e^{2.5(e^t-1)}$. What is $V(Y)$?",
             r"$2.5$: the Poisson MGF with $\lambda=2.5$, and a Poisson variance equals its mean.",
             "First. Daily chargebacks at a card acquirer have m of t equal to e to the two point five times e to "
             "the t minus one. What is the variance of Y? Pause if you want to think.",
             "The answer is two point five. That is the Poisson MGF with lambda two point five, and a Poisson "
             "variance equals its mean."),
            (r"15 shipments, $Y$ held at customs: $m(t)=(0.2e^t+0.8)^{15}$. Distribution of $Y$?",
             r"Bin$(15,\,0.2)$: $p$ is the number multiplying $e^t$; the mean is $3$.",
             "Second. Out of fifteen export shipments, Y are held at customs, and m of t is point two e to the t "
             "plus point eight, to the fifteenth. What is the distribution of Y?",
             "Binomial with n fifteen and p point two. Careful: p is the number multiplying e to the t, not the "
             "other one. The mean is three."),
            (r"A fee schedule charges $W=2Y+3$ AZN. What is $m_W(t)$?",
             r"$e^{3t}\,m_Y(2t)$: the shift comes out as a factor, the scale goes inside.",
             "Third. A fee schedule charges W equals two Y plus three manat. What is the MGF of W?",
             "It is e to the three t times m Y of two t. The shift comes out as a factor, and the scale goes "
             "inside."),
        ]
        prev = None
        for i, (q, a, sq, sa) in enumerate(qs):
            qt = TX(q, font_size=40).shift(UP * 0.9)
            at = TX(a, font_size=38, color=TEAL_).next_to(qt, DOWN, buff=0.8)
            num = T(f"{i + 1} / 3", 28, GREY_).next_to(qt, UP, buff=0.5)
            with self.say(sq) as tr:
                if prev is not None:
                    self.play(FadeOut(prev), run_time=0.5)
                self.play(FadeIn(num), Write(qt), run_time=1.5)
                self.done(tr)
            self.wait(2.5)
            with self.say(sa) as tr:
                self.play(FadeIn(at, shift=UP * 0.2))
                self.done(tr)
            prev = VGroup(qt, at, num)

    def summary(self):
        self.head("Summary")
        items = VGroup(
            TX(r"Mean and variance do not determine a distribution; the moments $\mu'_k=E(Y^k)$ (usually) do.", font_size=36),
            TX(r"$m(t)=E(e^{tY})=\sum_y e^{ty}p(y)$ packs them all: $\mu'_k$ is the coefficient of $t^k/k!$.", font_size=36),
            TX(r"Theorem 3.12: $m^{(k)}(0)=\mu'_k$, so $\mu=m'(0)$ and $\sigma^2=m''(0)-[m'(0)]^2$.", font_size=36),
            TX(r"Linear change: $m_{aY+b}(t)=e^{bt}\,m_Y(at)$.", font_size=36),
            TX(r"Binomial $(pe^t+q)^n$, Poisson $e^{\lambda(e^t-1)}$, geometric $pe^t/(1-qe^t)$.", font_size=36),
            TX(r"Uniqueness: recognise the MGF, and you know the distribution.", font_size=36, color=YELLOW_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.33).shift(DOWN * 0.3)
        with self.say("To sum up. Mean and variance do not determine a distribution; the full sequence of "
                      "moments usually does. The moment-generating function packs every moment into one "
                      "function. Differentiate k times and set t to zero to read off the k-th moment. A linear "
                      "change, a Y plus b, turns the MGF into e to the b t times m Y of a t. And above all, "
                      "uniqueness: recognise the MGF, and you know the distribution.") as tr:
            for it in items:
                self.play(FadeIn(it, shift=RIGHT * 0.2), run_time=0.7)
                self.wait(1.6)
            self.done(tr)

    def closing(self):
        self.head("What to do next")
        g = VGroup(
            TX(r"\textbf{Wackerly \S3.9:} exercises 3.145, 3.146, 3.149, 3.153--3.155, 3.156--3.157", font_size=38),
            TX(r"\textbf{Week 8, Problem Set 1} on WeBWorK: closes Sunday 8 November, 23:59", font_size=38),
            TX(r"\textbf{Next class, 31 October:} probability-generating functions and Tchebysheff's theorem (\S\S3.10--3.11)", font_size=34),
            TX(r"Questions: the course WhatsApp group, or office hours", font_size=38, color=TEAL_),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        with self.say("For practice, do the exercises at the end of section three point nine: start with three "
                      "point one forty-five and one forty-six, then one forty-nine and one fifty-three to one "
                      "fifty-five, and one fifty-six and one fifty-seven for the linear change. Week eight, "
                      "problem set one is open on WeBWorK and closes on Sunday the eighth of November at "
                      "eleven fifty-nine at night. On Saturday, the thirty-first of October, we continue with "
                      "probability-generating functions and Tchebysheff's theorem. If anything here is unclear, "
                      "ask in our WhatsApp group or come to office hours. See you on Saturday.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=UP * 0.2), run_time=0.8)
                self.wait(2.5)
            self.done(tr)
