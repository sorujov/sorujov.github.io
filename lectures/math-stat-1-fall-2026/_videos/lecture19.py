"""Lecture 19 intuition video: the normal distribution — shift and stretch, standardising, the 68-95-99.7 rule, VaR."""
from common import *
from scipy.stats import norm


class Lecture19(IntuitionScene):
    parts = ("hook", "shift_stretch", "standardise", "rule", "var", "closing")

    def hook(self):
        q = T("Daily returns, credit scores, measurement errors ...", 38)
        q2 = T("Why does the same bell shape keep appearing?", 38, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("Daily portfolio returns, credit scores, measurement errors, heights. Plot them and "
                      "the same bell shape keeps appearing. It appears so often because adding up many "
                      "small independent effects tends to produce it, a story we'll make precise later in "
                      "the course. Today: how to work with it.") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("The normal distribution", 19,
                        "The key fact about the normal family is that there's really only one normal "
                        "curve, shifted and stretched.")

    def shift_stretch(self):
        ax = Axes(x_range=[-6, 6, 2], y_range=[0, 0.8, 0.2], x_length=11, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.6)
        mu, sg = ValueTracker(0), ValueTracker(1)
        curve = always_redraw(lambda: ax.plot(lambda x: norm.pdf(x, mu.get_value(), sg.get_value()), x_range=[-6, 6, 0.03], color=YELLOW_, stroke_width=4))
        lab = always_redraw(lambda: MathTex(f"\\mu={mu.get_value():.1f},\\ \\sigma={sg.get_value():.1f}", font_size=40, color=YELLOW_).to_corner(UR, buff=0.6))
        with self.say("The normal density has two parameters. Mu locates it: change mu and the whole "
                      "curve slides left or right without changing shape.") as tr:
            self.play(Create(ax))
            self.add(curve, lab)
            self.play(mu.animate.set_value(2), run_time=2)
            self.play(mu.animate.set_value(-1.5), run_time=2)
            self.play(mu.animate.set_value(0), run_time=1.5)
            self.fill(tr, 5.5)
        with self.say("Sigma spreads it: make sigma bigger and the curve gets wider and flatter, smaller "
                      "and it gets narrow and tall. The area underneath always stays one.") as tr:
            self.play(sg.animate.set_value(2), run_time=2)
            self.play(sg.animate.set_value(0.6), run_time=2)
            self.play(sg.animate.set_value(1), run_time=1.5)
            self.fill(tr, 5.5)

    def standardise(self):
        top = Axes(x_range=[550, 850, 50], y_range=[0, 0.01, 0.005], x_length=11, y_length=2.2, tips=False,
                   axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"numbers_to_include": [600, 650, 700, 750, 800]}).shift(UP * 1.9)
        bot = Axes(x_range=[-3, 3, 1], y_range=[0, 0.5, 0.25], x_length=11, y_length=2.2, tips=False,
                   axis_config={"color": GREY_, "include_numbers": True, "font_size": 22}).shift(DOWN * 2.4)
        c1 = top.plot(lambda x: norm.pdf(x, 700, 50), x_range=[550, 850], color=BLUE_)
        c2 = bot.plot(norm.pdf, x_range=[-3, 3], color=TEAL_)
        l1 = T("credit scores: μ = 700, σ = 50", 26, BLUE_).next_to(top, UP, buff=0.1).align_to(top, LEFT)
        l2 = T("Z = (Y − 700) / 50: standard normal", 26, TEAL_).next_to(bot, UP, buff=0.1).align_to(bot, LEFT)
        with self.say("Credit scores at a bank are roughly normal, with mean seven hundred and standard "
                      "deviation fifty. Subtract the mean and divide by the standard deviation, and you get "
                      "the standard normal, Z, with mean zero and standard deviation one.") as tr:
            self.play(Create(top), Create(c1), FadeIn(l1))
            self.play(TransformFromCopy(c1, c2), Create(bot), FadeIn(l2), run_time=2)
            self.fill(tr, 3)
        a1 = top.get_area(c1, x_range=[775, 850], color=RED_, opacity=0.7)
        a2 = bot.get_area(c2, x_range=[1.5, 3], color=RED_, opacity=0.7)
        eq = MathTex(r"P(Y>775)=P(Z>1.5)\approx0.067", font_size=40, color=RED_).move_to(DOWN * 0.25 + RIGHT * 2.8)
        with self.say("And the areas match. The chance of a score above seven seventy-five is exactly the "
                      "chance that Z is above one point five: about six point seven percent. So one table, "
                      "or one R function, answers questions about every normal distribution there is.") as tr:
            self.play(FadeIn(a1), FadeIn(a2))
            self.play(Write(eq))
            self.fill(tr, 2)

    def rule(self):
        ax = Axes(x_range=[-4, 4, 1], y_range=[0, 0.45, 0.1], x_length=11, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"numbers_to_include": [-3, -2, -1, 0, 1, 2, 3]}).shift(DOWN * 0.8)
        c = ax.plot(norm.pdf, x_range=[-4, 4], color=YELLOW_)
        with self.say("Because every normal is the same curve, three numbers are worth knowing by heart.") as tr:
            self.play(Create(ax), Create(c))
            self.fill(tr, 1)
        with self.say("Within one standard deviation of the mean: about sixty-eight percent. Within two: "
                      "about ninety-five percent. Within three: ninety-nine point seven. Compare that with "
                      "Tchebysheff, who could only promise seventy-five and eighty-nine percent: knowing the "
                      "shape buys you much sharper answers.") as tr:
            for k, pct, col in ((3, r"99.7\%", BLUE_), (2, r"95\%", TEAL_), (1, r"68\%", YELLOW_)):
                a = ax.get_area(c, x_range=[-k, k], color=col, opacity=0.35)
                t = MathTex(rf"\pm{k}\sigma:\ {pct}", font_size=36, color=col).move_to(ax.c2p(0, 0.47 - 0.06 * k) + RIGHT * (2.2 + 1.2 * k))
                self.play(FadeIn(a), FadeIn(t), run_time=1.2)
                self.wait(1.3)
            self.fill(tr, 7.5)

    def var(self):
        ax = Axes(x_range=[-4, 4, 1], y_range=[0, 0.45, 0.1], x_length=11, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22}, x_axis_config={"numbers_to_include": [-3, -2, -1, 0, 1, 2, 3]}).shift(DOWN * 0.8)
        c = ax.plot(norm.pdf, x_range=[-4, 4], color=YELLOW_)
        q = T("Daily return ~ normal, μ = 0.05%, σ = 1.2%", 32).to_edge(UP, buff=0.5)
        z = norm.ppf(0.05)
        tail = ax.get_area(c, x_range=[-4, z], color=RED_, opacity=0.8)
        line = DashedLine(ax.c2p(z, 0), ax.c2p(z, 0.35), color=RED_)
        lab = MathTex(r"z_{0.05}=-1.645", font_size=34, color=RED_).next_to(line, UP, buff=0.1)
        with self.say("One last use, straight from the risk desk. A portfolio's daily return is roughly "
                      "normal. What loss is exceeded only on the worst five percent of days? Find the point "
                      "that cuts off five percent of area in the left tail: minus one point six four five "
                      "standard deviations.") as tr:
            self.play(FadeIn(q), Create(ax), Create(c))
            self.play(FadeIn(tail), Create(line), FadeIn(lab))
            self.fill(tr, 3)
        v = MathTex(r"\text{VaR}_{95\%}=-(\mu+z_{0.05}\,\sigma)\approx1.92\%", font_size=42, color=RED_).to_corner(UR, buff=0.5).shift(DOWN * 1.1)
        with self.say("Translate back to returns: mean plus minus one point six four five times sigma, "
                      "about minus one point nine percent. That's the ninety-five percent value at risk. It "
                      "rests entirely on the normal assumption, which real returns, with their fatter tails, "
                      "don't always honour.") as tr:
            self.play(Write(v), run_time=2)
            self.fill(tr, 2)

    def closing(self):
        g = VGroup(
            VGroup(T("μ shifts, σ stretches", 38, YELLOW_), T("one curve, many disguises", 30)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"Z=\frac{Y-\mu}{\sigma}", font_size=44, color=TEAL_), T("turns any normal into the standard one", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("68 · 95 · 99.7", 38, BLUE_), T("within 1, 2, 3 standard deviations", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: there is really one normal curve. Mu shifts it and sigma stretches it. "
                      "Standardising turns any normal into the standard one, so one table answers every "
                      "question. And sixty-eight, ninety-five, ninety-nine point seven tell you, at a "
                      "glance, how the probability is spread.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
