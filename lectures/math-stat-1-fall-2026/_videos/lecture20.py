"""Lecture 20 intuition video: gamma as a waiting time, the shape parameter, memoryless exponential, chi-square."""
from common import *
from scipy.stats import gamma, norm, chi2


class Lecture20(IntuitionScene):
    parts = ("hook", "waiting", "memoryless", "chisq", "closing")

    def hook(self):
        q = T("Gaps between large AZN/USD trades: mean 25 min, sd 25 min", 34).to_edge(UP, buff=0.6)
        ax = Axes(x_range=[-50, 100, 25], y_range=[0, 0.02, 0.01], x_length=10.5, y_length=3.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  x_axis_config={"numbers_to_include": [-50, -25, 0, 25, 50, 75, 100]}).shift(DOWN * 0.9)
        c = ax.plot(lambda x: norm.pdf(x, 25, 25), x_range=[-50, 100], color=BLUE_, stroke_width=4)
        neg = ax.get_area(c, x_range=[-50, 0], color=RED_, opacity=0.8)
        lab = T("normal model:\n16% of gaps negative", 24, RED_).move_to(ax.c2p(-50, 0.0165), aligned_edge=LEFT)
        with self.say("On the interbank currency desk, the gap between two large trades averages twenty-five "
                      "minutes, with a standard deviation of about twenty-five minutes. Fit a normal curve with "
                      "those numbers, and look to the left of zero. Sixteen percent of the gaps would be "
                      "negative: the next trade would arrive before the last one.") as tr:
            self.play(FadeIn(q))
            self.play(Create(ax), Create(c), run_time=2)
            self.play(FadeIn(neg), FadeIn(lab))
            self.fill(tr, 4)
        self.play(*[FadeOut(m) for m in (q, ax, c, neg, lab)])
        self.title_card("Gamma, exponential, chi-square", 20,
                        "Waiting times live on zero to infinity and lean to the right. The gamma family is "
                        "built for exactly that.")

    def waiting(self):
        line = NumberLine(x_range=[0, 30, 5], length=11, color=GREY_, include_numbers=True, font_size=22).shift(UP * 2.2)
        tl = T("days", 22, GREY_).next_to(line, RIGHT, buff=0.15).shift(UP * 0.05)
        times = [3.1, 7.4, 13.8]
        dots = VGroup(*[Dot(line.n2p(t), color=YELLOW_, radius=0.1) for t in times])
        nums = VGroup(*[T(s, 24, YELLOW_).next_to(d, UP, buff=0.2) for s, d in zip(("1st", "2nd", "3rd"), dots)])
        br = BraceBetweenPoints(line.n2p(0), line.n2p(times[2]), DOWN, color=TEAL_).shift(DOWN * 0.35)
        bl = MathTex(r"Y=\text{time to the 3rd large claim}", font_size=32, color=TEAL_).next_to(br, DOWN, buff=0.1)
        with self.say("Here's the picture to keep in mind. Large insurance claims arrive at random, about "
                      "one every four days. The time to the first claim is an exponential wait. The time to "
                      "the third claim is three such waits added together, and that is a gamma variable, with "
                      "shape alpha equal to three and scale beta equal to four.") as tr:
            self.play(Create(line), FadeIn(tl))
            for d, n in zip(dots, nums):
                self.play(FadeIn(d, scale=2), FadeIn(n), run_time=0.8)
            self.play(GrowFromCenter(br), FadeIn(bl))
            self.fill(tr, 4)
        ax = Axes(x_range=[0, 40, 10], y_range=[0, 0.25, 0.05], x_length=9.5, y_length=3.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 10, 20, 30, 40]},
                  y_axis_config={"numbers_to_include": [0.1, 0.2]}).shift(DOWN * 1.9 + LEFT * 1.2)
        a = ValueTracker(1.0)
        curve = always_redraw(lambda: ax.plot(lambda x: gamma.pdf(x, a.get_value(), scale=4), x_range=[0.05, 40, 0.1],
                                              color=YELLOW_, stroke_width=4))
        lab = always_redraw(lambda: MathTex(rf"\alpha={a.get_value():.1f},\ \beta=4", font_size=34, color=YELLOW_)
                            .move_to(ax.c2p(34, 0.21)))
        mom = MathTex(r"E(Y)=\alpha\beta", r"\qquad V(Y)=\alpha\beta^2", font_size=34).next_to(ax, RIGHT, buff=0.2).shift(UP * 0.3)
        mom[1].next_to(mom[0], DOWN, buff=0.3, aligned_edge=LEFT)
        with self.say("Now let alpha grow. With alpha equal to one, you wait for a single claim: the "
                      "density starts at its highest point and decays. Wait for two claims, three, five, and "
                      "the hump moves right, spreads out, and becomes more symmetric. The mean is alpha times "
                      "beta, twelve days for the third claim, and the variance is alpha beta squared.") as tr:
            self.play(Create(ax))
            self.add(curve, lab)
            self.play(a.animate.set_value(2), run_time=1.5)
            self.play(a.animate.set_value(3), run_time=1.5)
            self.play(a.animate.set_value(5), run_time=1.5)
            self.play(a.animate.set_value(3), run_time=1)
            self.play(FadeIn(mom))
            self.fill(tr, 7.5)
        self.remove(curve, lab)
        self.add(ax.plot(lambda x: gamma.pdf(x, 3, scale=4), x_range=[0.05, 40, 0.1], color=YELLOW_, stroke_width=4))

    def memoryless(self):
        f = lambda x: 0.25 * np.exp(-x / 4)
        ax = Axes(x_range=[0, 20, 5], y_range=[0, 0.3, 0.1], x_length=10.5, y_length=4, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).shift(DOWN * 0.8)
        xl = T("minutes on hold", 24, GREY_).next_to(ax, DOWN, buff=0.25)
        c = ax.plot(f, x_range=[0, 20], color=YELLOW_, stroke_width=4)
        q = T("Call-centre hold time: exponential, mean 4 minutes", 32).to_edge(UP, buff=0.5)
        with self.say("Alpha equal to one is the exponential, and it has a strange property. A bank's "
                      "call centre has hold times that are exponential with mean four minutes.") as tr:
            self.play(FadeIn(q), Create(ax), FadeIn(xl), Create(c))
            self.fill(tr, 2)
        tail = ax.get_area(c, x_range=[5, 20], color=TEAL_, opacity=0.5)
        cut = DashedLine(ax.c2p(5, 0), ax.c2p(5, 0.2), color=TEAL_)
        cl = T("already waited 5 min", 24, TEAL_).next_to(cut, UP, buff=0.1)
        piece = ax.plot(f, x_range=[5, 20], color=TEAL_, stroke_width=5)
        with self.say("Suppose you have already waited five minutes. All that remains possible is the part "
                      "of the curve beyond five. To condition on it, slide that piece back to zero and stretch "
                      "it until its area is one again.") as tr:
            self.play(FadeIn(tail), Create(cut), FadeIn(cl))
            self.play(Create(piece))
            moved = ax.plot(f, x_range=[0, 15], color=TEAL_, stroke_width=5)
            self.play(FadeOut(tail), piece.animate.shift(ax.c2p(0, 0) - ax.c2p(5, 0)), run_time=1.5)
            self.play(Transform(piece, moved), run_time=1.5)
            self.fill(tr, 5)
        eq = MathTex(r"P(Y>5+2\mid Y>5)=P(Y>2)=e^{-2/4}\approx0.61", font_size=38, color=TEAL_).next_to(q, DOWN, buff=0.45)
        with self.say("It lands exactly on the original curve. The caller who has held for five minutes "
                      "faces the same wait as someone who just dialled in. The exponential has no memory. "
                      "Whether that's realistic is a modelling question: a queue that is served in order "
                      "does remember.") as tr:
            self.play(Indicate(c, color=TEAL_), run_time=1.5)
            self.play(Write(eq), run_time=2)
            self.fill(tr, 3.5)

    def chisq(self):
        ax = Axes(x_range=[0, 16, 2], y_range=[0, 0.6, 0.2], x_length=10, y_length=3.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).shift(DOWN * 1.0)
        top = MathTex(r"\chi^2(\nu)\;=\;\text{gamma with }\alpha=\tfrac{\nu}{2},\ \beta=2", font_size=42).to_edge(UP, buff=0.5)
        mv = MathTex(r"E=\nu,\qquad V=2\nu", font_size=36, color=GREY_).next_to(top, DOWN, buff=0.25)
        cols = [BLUE_, TEAL_, YELLOW_, PURPLE_]
        curves, labs = VGroup(), VGroup()
        for i, (nu, col) in enumerate(zip((1, 2, 4, 8), cols)):
            cv = ax.plot(lambda x, nu=nu: chi2.pdf(x, nu), x_range=[0.35 if nu == 1 else 0.02, 16, 0.05], color=col, stroke_width=4)
            curves.add(cv)
            labs.add(MathTex(rf"\nu={nu}", font_size=34, color=col).move_to(ax.c2p(14, 0.55 - 0.1 * i)))
        with self.say("One more member of the family. Set beta equal to two and alpha equal to nu over two, "
                      "and you get the chi-square distribution with nu degrees of freedom. Its mean is nu and "
                      "its variance is two nu. It gets its own name because statistics uses it constantly: "
                      "it will come back when we test variances later in the course.") as tr:
            self.play(Write(top), FadeIn(mv))
            self.play(Create(ax))
            for cv, lb in zip(curves, labs):
                self.play(Create(cv), FadeIn(lb), run_time=1)
            self.fill(tr, 6)

    def closing(self):
        g = VGroup(
            VGroup(T("gamma(α, β)", 38, YELLOW_), T("waiting for the α-th event; mean αβ", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("exponential", 38, TEAL_), T("α = 1; it has no memory", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("chi-square", 38, PURPLE_), T("α = ν/2, β = 2; mean ν", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        with self.say("So: the gamma is a waiting time. Alpha counts the events you wait for, and beta sets "
                      "the time scale. The exponential waits for one event and forgets how long it has "
                      "waited. And the chi-square is the gamma that statistics will lean on.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
