"""Lecture 22 intuition video: continuous MGFs (fund value, recognising a kernel) and Tchebysheff (why the bound holds, how loose it is)."""
from common import *
from scipy.stats import gamma, norm


class Lecture22(IntuitionScene):
    parts = ("hook", "fund", "kernel", "proof", "loose", "closing")

    def hook(self):
        q = T("100,000 AZN in an equity fund", 38).to_edge(UP, buff=0.9)
        q2 = MathTex(r"\text{annual log return } R\sim N(0.08,\ 0.20^2)", font_size=40).next_to(q, DOWN, buff=0.4)
        q3 = T("What is the fund worth, on average, in a year?", 38, YELLOW_).next_to(q2, DOWN, buff=0.6)
        with self.say("A hundred thousand manat sits in an equity fund whose annual log return is normal, "
                      "with mean eight percent and standard deviation twenty percent. What is it worth, on "
                      "average, in a year? The tempting answer, a hundred thousand times e to the point zero "
                      "eight, is wrong.") as tr:
            self.play(FadeIn(q), FadeIn(q2))
            self.play(Write(q3))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2), FadeOut(q3))
        self.title_card("Continuous MGFs and Tchebysheff", 22,
                        "The fix is a moment-generating function, now for continuous variables.")

    def fund(self):
        top = Axes(x_range=[-0.6, 0.8, 0.2], y_range=[0, 2.2, 1], x_length=10, y_length=1.8, tips=False,
                   axis_config={"color": GREY_, "font_size": 20},
                   x_axis_config={"numbers_to_include": [-0.4, -0.2, 0, 0.2, 0.4, 0.6]}).shift(UP * 1.7)
        bot = Axes(x_range=[40, 200, 20], y_range=[0, 0.022, 0.01], x_length=10, y_length=1.8, tips=False,
                   axis_config={"color": GREY_, "font_size": 20},
                   x_axis_config={"numbers_to_include": [60, 80, 100, 120, 140, 160, 180]}).shift(DOWN * 2.1)
        cr = top.plot(lambda x: norm.pdf(x, 0.08, 0.2), x_range=[-0.6, 0.8], color=BLUE_, stroke_width=4)
        fv = lambda v: norm.pdf(np.log(v / 100), 0.08, 0.2) / v
        cv = bot.plot(fv, x_range=[40, 200], color=YELLOW_, stroke_width=4)
        lr = MathTex("R", font_size=34, color=BLUE_).next_to(top, LEFT, buff=0.2)
        lv = T("V, fund value in thousand AZN", 22, YELLOW_).next_to(bot, DOWN, buff=0.4)
        with self.say("The log return is a symmetric bell. The fund's value is a hundred thousand times e to "
                      "the R, and pushing the bell through the exponential makes it lopsided, with a long "
                      "right tail.") as tr:
            self.play(Create(top), Create(cr), FadeIn(lr))
            self.play(TransformFromCopy(cr, cv), Create(bot), FadeIn(lv), run_time=2)
            self.fill(tr, 3)
        pts = [(0.28, GREEN_), (-0.12, RED_)]
        arrows, labs = VGroup(), VGroup()
        for r, col in pts:
            v = 100 * np.exp(r)
            arrows.add(Arrow(top.c2p(r, 0), bot.c2p(v, 0.02), color=col, buff=0.05, stroke_width=4))
            labs.add(T(f"{v - 108.33:+.1f}k", 28, col).next_to(bot.c2p(v, 0.02), UP, buff=0.1).shift(RIGHT * (0.7 if r > 0 else -0.7)))
        with self.say("Take a good year and a bad year, one standard deviation either side. Against the middle "
                      "value, the good year adds twenty-four thousand, the bad year takes away only twenty. "
                      "Gains are stretched more than losses are shrunk, so the average sits above the middle.") as tr:
            for a, l in zip(arrows, labs):
                self.play(GrowArrow(a), FadeIn(l), run_time=1.2)
            self.fill(tr, 2.4)
        med = DashedLine(bot.c2p(108.33, 0), bot.c2p(108.33, 0.021), color=GREY_)
        mean = DashedLine(bot.c2p(110.52, 0), bot.c2p(110.52, 0.021), color=TEAL_)
        eq = MathTex(r"E(e^{R})=m_R(1)=e^{\mu+\sigma^2/2}\ \Rightarrow\ E(V)=110{,}517", font_size=36, color=TEAL_).move_to(UP * 0.05)
        ml = VGroup(T("median 108,329", 22, GREY_).next_to(bot.c2p(108.33, 0.022), UL, buff=0.08),
                    T("mean 110,517", 22, TEAL_).next_to(bot.c2p(110.52, 0.022), UR, buff=0.08))
        with self.say("And the average of e to the R is the moment-generating function of R at t equal to "
                      "one: e to the mu plus sigma squared over two. That gives about one hundred and ten and "
                      "a half thousand. The hundred and eight thousand was only the median.") as tr:
            self.play(FadeOut(arrows), FadeOut(labs))
            self.play(Create(med), FadeIn(ml), Create(mean))
            self.play(Write(eq), run_time=2)
            self.fill(tr, 4)

    def kernel(self):
        al, be = 2, 2
        ax = Axes(x_range=[0, 25, 5], y_range=[0, 0.35, 0.1], x_length=10, y_length=3.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 22, "include_numbers": True}).shift(DOWN * 1.2)
        top = MathTex(r"m(t)=\int_0^\infty e^{ty}f(y)\,dy", font_size=40).to_edge(UP, buff=0.4)
        f = ax.plot(lambda y: gamma.pdf(y, al, scale=be), x_range=[0, 25], color=GREY_, stroke_width=3)
        fl = VGroup(MathTex(r"f(y):\ \text{gamma}(2,2)", font_size=30, color=GREY_),
                    MathTex(r"e^{ty}f(y)", font_size=30, color=YELLOW_)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        fl.move_to(ax.c2p(15, 0.3), aligned_edge=LEFT)
        t = ValueTracker(0.0)
        integ = always_redraw(lambda: ax.plot(lambda y: np.exp(t.get_value() * y) * gamma.pdf(y, al, scale=be),
                                              x_range=[0, 25, 0.1], color=YELLOW_, stroke_width=4))
        area = always_redraw(lambda: ax.get_area(integ, x_range=[0, 25], color=YELLOW_, opacity=0.25))
        lab = always_redraw(lambda: MathTex(rf"t={t.get_value():.2f}:\ \ \text{{area}}={(1 - be * t.get_value()) ** -al:.2f}",
                                            font_size=34, color=YELLOW_).move_to(ax.c2p(15, 0.2), aligned_edge=LEFT))
        with self.say("How do you compute an MGF? For a gamma density, multiplying by e to the t y only "
                      "weakens the decay. As t grows, the integrand swells and stretches, but it keeps the "
                      "gamma shape, with a larger scale.") as tr:
            self.play(Write(top), Create(ax), Create(f), FadeIn(fl))
            self.add(area, integ, lab)
            self.play(t.animate.set_value(0.2), run_time=5, rate_func=linear)
            self.fill(tr, 6)
        res = MathTex(r"m(t)=(1-\beta t)^{-\alpha},\quad t<1/\beta", font_size=40, color=TEAL_).next_to(top, DOWN, buff=0.3)
        with self.say("And we already know the area under any gamma shape, so there's nothing to integrate: "
                      "the MGF is one minus beta t, to the power minus alpha, for t below one over beta. "
                      "Recognise the kernel; don't integrate.") as tr:
            self.play(Write(res), run_time=2)
            self.fill(tr, 2)
        self.remove(integ, area, lab)

    def proof(self):
        th = MathTex(r"P\big(|Y-\mu|\ge k\sigma\big)\le\frac{1}{k^2}", font_size=42, color=YELLOW_).to_edge(UP, buff=0.3)
        top = Axes(x_range=[-4, 4, 1], y_range=[0, 8, 4], x_length=10, y_length=2.3, tips=False,
                   axis_config={"color": GREY_, "font_size": 20}).shift(UP * 0.8)
        bot = Axes(x_range=[-4, 4, 1], y_range=[0, 0.45, 0.2], x_length=10, y_length=1.8, tips=False,
                   axis_config={"color": GREY_, "font_size": 20},
                   x_axis_config={"numbers_to_include": [-2, 0, 2]}).shift(DOWN * 2.3)
        par = top.plot(lambda y: y ** 2, x_range=[-2.83, 2.83], color=BLUE_, stroke_width=4)
        pl = MathTex(r"(y-\mu)^2", font_size=30, color=BLUE_).next_to(top.c2p(2.83, 8), RIGHT, buff=0.15)
        d = bot.plot(norm.pdf, x_range=[-4, 4], color=GREY_)
        dl = MathTex("f(y)", font_size=30, color=GREY_).next_to(bot.c2p(0.4, 0.4), RIGHT, buff=0.15)
        mid = bot.get_area(d, x_range=[-2, 2], color=BLUE_, opacity=0.4)
        tails = VGroup(bot.get_area(d, x_range=[-4, -2], color=RED_, opacity=0.8),
                       bot.get_area(d, x_range=[2, 4], color=RED_, opacity=0.8))
        with self.say("Tchebysheff's theorem holds here too, and the proof is a picture. The variance "
                      "averages the squared distance from the mean, weighted by the density.") as tr:
            self.play(Write(th))
            self.play(Create(top), Create(par), FadeIn(pl), Create(bot), Create(d), FadeIn(dl), run_time=2)
            self.play(FadeIn(mid), FadeIn(tails))
            self.fill(tr, 4)
        kl = DashedLine(top.c2p(-4, 4), top.c2p(4, 4), color=RED_)
        kt = MathTex(r"k^2\sigma^2", font_size=30, color=RED_).next_to(top.c2p(-4, 4), LEFT, buff=0.15)
        vl = VGroup(*[DashedLine(top.c2p(s * 2, 0), bot.c2p(s * 2, 0), color=RED_, stroke_opacity=0.6) for s in (-1, 1)])
        mpar = top.plot(lambda y: y ** 2, x_range=[-2, 2], color=BLUE_, stroke_width=4)
        flat = VGroup(Line(top.c2p(-4, 4), top.c2p(-2, 4), color=RED_, stroke_width=6),
                      Line(top.c2p(2, 4), top.c2p(4, 4), color=RED_, stroke_width=6))
        with self.say("Throw two things away. First the middle, within k standard deviations. Second, in the "
                      "tails, replace the squared distance by its floor, k squared sigma squared. Both steps "
                      "only make the total smaller.") as tr:
            self.play(Create(kl), FadeIn(kt), Create(vl))
            self.add(mpar)
            self.play(FadeOut(mid), mpar.animate.set_stroke(opacity=0.15), par.animate.set_stroke(opacity=0.35), run_time=1.5)
            self.play(Create(flat), run_time=1.5)
            self.fill(tr, 4)
        res = MathTex(r"\sigma^2\ \ge\ k^2\sigma^2\,P\big(|Y-\mu|\ge k\sigma\big)", font_size=40, color=TEAL_)
        res.add_background_rectangle(color=BG, opacity=0.9).move_to(UP * 1.9 + RIGHT * 0.2)
        with self.say("What's left, k squared sigma squared times the tail probability, can't exceed sigma "
                      "squared. Divide, and that's the theorem. What we threw away is why it's loose.") as tr:
            self.play(FadeIn(res), run_time=1.5)
            self.fill(tr, 1.5)

    def loose(self):
        L = lambda p: np.log10(p) + 4          # log scale, shifted so 0.0001 sits on the x-axis
        ax = Axes(x_range=[1, 5, 1], y_range=[0, 4, 1], x_length=9, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  x_axis_config={"numbers_to_include": [1, 2, 3, 4, 5]}).shift(DOWN * 0.3 + LEFT * 0.8)
        ylabs = VGroup(*[T(s, 20, GREY_).next_to(ax.c2p(1, v), LEFT, buff=0.15)
                         for s, v in (("1", 4), ("0.1", 3), ("0.01", 2), ("0.001", 1), ("0.0001", 0))])
        xl = T("k, standard deviations from the mean", 24, GREY_).next_to(ax, DOWN, buff=0.45)
        yl = T("tail probability (log scale)", 24, GREY_).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        cb = ax.plot(lambda k: L(1 / k ** 2), x_range=[1, 5], color=RED_, stroke_width=5)
        ce = ax.plot(lambda k: L(np.exp(-(1 + k))), x_range=[1, 5], color=TEAL_, stroke_width=4)
        cn = ax.plot(lambda k: L(2 * norm.cdf(-k)), x_range=[1, 3.72], color=BLUE_, stroke_width=4)
        lb = MathTex(r"1/k^2", font_size=34, color=RED_).next_to(ax.c2p(5, L(1 / 25)), RIGHT, buff=0.15)
        le = T("exponential", 26, TEAL_).next_to(ax.c2p(5, L(np.exp(-6))), RIGHT, buff=0.15)
        ln = T("normal", 26, BLUE_).next_to(ax.c2p(3.72, 0), RIGHT, buff=0.3).shift(UP * 0.3)
        with self.say("How loose? On a log scale: the bound against the true tails of an exponential and a normal.") as tr:
            self.play(Create(ax), FadeIn(ylabs), FadeIn(xl), FadeIn(yl))
            self.play(Create(cb), FadeIn(lb))
            self.play(Create(ce), FadeIn(le), Create(cn), FadeIn(ln), run_time=2)
            self.fill(tr, 4)
        v = DashedLine(ax.c2p(3, 0), ax.c2p(3, 4), color=GREY_)
        nums = VGroup(
            T("0.111", 22, RED_).next_to(ax.c2p(3, L(1 / 9)), UR, buff=0.08),
            T("0.018", 22, TEAL_).next_to(ax.c2p(3, L(np.exp(-4))), UR, buff=0.08),
            T("0.0027", 22, BLUE_).next_to(ax.c2p(3, L(2 * norm.cdf(-3))), DL, buff=0.08))
        with self.say("At three standard deviations the bound allows eleven percent; the exponential has "
                      "under two, the normal a quarter of one. Assuming nothing about shape keeps it safe, "
                      "and costs it precision.") as tr:
            self.play(Create(v))
            for n in nums:
                self.play(FadeIn(n), run_time=0.7)
            self.fill(tr, 3.1)

    def closing(self):
        g = VGroup(
            VGroup(MathTex(r"m(t)=E(e^{tY})", font_size=44, color=YELLOW_), T("now an integral; same uses", 30)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"E(e^{R})=e^{\mu+\sigma^2/2}", font_size=44, color=TEAL_), T("volatility raises the mean value", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("recognise a kernel", 36, BLUE_), T("instead of integrating", 30)).arrange(RIGHT, buff=0.5),
            VGroup(MathTex(r"1/k^2", font_size=44, color=RED_), T("safe for any shape, and loose", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45)
        with self.say("So: the moment-generating function is now an integral doing the same jobs. For a "
                      "normal log return, it gives the average value, and volatility raises it. Recognise "
                      "kernels instead of integrating. And Tchebysheff is safe for every shape, and loose "
                      "for most.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.fill(tr, 5.2)
