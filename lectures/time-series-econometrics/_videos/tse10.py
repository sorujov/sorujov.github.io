"""Lecture 10 intuition film: Dickey-Fuller tests -- identical twins, the squares behind rho hat,
the DF histogram building up left of the bell, and why no test can separate 1 from 0.999."""
from common import *

config.tex_dir = str(Path(__file__).parent / "media" / "videos" / "tse10" / "Tex")   # private: parallel renders share media/Tex
from scipy.stats import norm


def ar_path(e, rho):
    x = np.empty_like(e)
    x[0] = e[0]
    for t in range(1, len(e)):
        x[t] = rho * x[t - 1] + e[t]
    return x


def batched_tau(X, y, j):
    """t-statistic for (coef_j - 1) in R regressions at once; X (R,n,k), y (R,n)."""
    XtX = np.einsum("rnk,rnl->rkl", X, X)
    Xty = np.einsum("rnk,rn->rk", X, y)
    b = np.linalg.solve(XtX, Xty[..., None])[..., 0]
    res = y - np.einsum("rnk,rk->rn", X, b)
    s2 = (res ** 2).sum(1) / (X.shape[1] - X.shape[2])
    inv = np.linalg.inv(XtX)
    return (b[:, j] - 1) / np.sqrt(s2 * inv[:, j, j])


def df_draws(R=6000, n=250):
    np.random.seed(2026)
    x = np.cumsum(np.random.randn(R, n + 1), axis=1)
    y, xl = x[:, 1:], x[:, :-1]
    one = np.ones_like(xl)
    tr = np.broadcast_to(np.arange(1, n + 1, dtype=float), xl.shape)
    t0 = batched_tau(xl[..., None], y, 0)
    t1 = batched_tau(np.stack([one, xl], -1), y, 1)
    t2 = batched_tau(np.stack([one, tr, xl], -1), y, 2)
    return t0, t1, t2


class Tse10(IntuitionScene):
    parts = ("hook", "far_future", "squares", "histogram", "power", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        np.random.seed(2026)
        e = np.random.randn(300)
        self.xa, self.xb = np.cumsum(e), ar_path(e, 0.999)
        ax = Axes(x_range=[0, 300, 50], y_range=[-10, 30, 10], x_length=11.5, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}).shift(DOWN * 0.7)
        a = series_path(ax, self.xa, RED_, 7)
        b = series_path(ax, self.xb, BLUE_, 3)
        la = MathTex(r"x_t = x_{t-1}+\varepsilon_t", font_size=40, color=RED_)
        lb = MathTex(r"x_t = 0.999\,x_{t-1}+\varepsilon_t", font_size=40, color=BLUE_)
        labs = VGroup(la, lb).arrange(RIGHT, buff=1.0).to_edge(UP, buff=0.55)
        q = T("Which one remembers every shock for ever?", 34, YELLOW_).next_to(ax, DOWN, buff=0.3)
        with self.say("Two series, driven by the same shocks. One is a random walk: every shock "
                      "stays in it for ever. The other forgets each shock, very slowly, at rate zero point "
                      "nine nine nine. For three hundred periods they draw what is practically one line. "
                      "Which one is the random walk?") as tr:
            self.play(FadeIn(labs[0]), FadeIn(labs[1]), Create(ax), run_time=1.2)
            self.play(Create(a), Create(b), run_time=6, rate_func=linear)
            self.play(Write(q))
            self.fill(tr, 8.2)
        self.hook_mobs = (ax, a, b, labs)
        self.play(FadeOut(q))
        self.play(*[FadeOut(m) for m in self.hook_mobs])
        self.title_card("Dickey–Fuller tests", 10,
                        "This is the problem of testing for a unit root. The twins will stay with us "
                        "throughout.")

    # ------------------------------------------------------------------ the twins part
    def far_future(self):
        xmax = ValueTracker(300)
        H = 3000
        xa, xb = self.xa, self.xb

        def mk_ax():
            return Axes(x_range=[0, xmax.get_value(), xmax.get_value()], y_range=[-10, 30, 10],
                        x_length=11.5, y_length=4.6, tips=False,
                        axis_config={"color": GREY_, "font_size": 24}).shift(DOWN * 0.7)

        ax = always_redraw(mk_ax)

        def paths():
            A = mk_ax()
            h_end = int(min(H, max(0, xmax.get_value() - 300)))
            g = VGroup(series_path(A, xa, RED_, 5), series_path(A, xb, BLUE_, 3))
            if h_end > 2:
                hs = np.arange(0, h_end + 1, 5)
                g.add(VMobject(color=RED_, stroke_width=5).set_points_as_corners(
                    [A.c2p(300 + h, xa[-1]) for h in hs]))
                g.add(VMobject(color=BLUE_, stroke_width=5).set_points_as_corners(
                    [A.c2p(300 + h, 0.999 ** h * xb[-1]) for h in hs]))
            g.add(DashedLine(A.c2p(300, -10), A.c2p(300, 30), color=GREY_, stroke_width=2))
            return g

        P = always_redraw(paths)
        today = always_redraw(lambda: T("today", 26, GREY_).next_to(mk_ax().c2p(300, 30), UP, buff=0.12))
        head = T("Same past. Now forecast the future.", 34).to_edge(UP, buff=0.45)
        self.add(ax, P, today)
        with self.say("Standing at the last observation, we forecast three thousand periods ahead. The"
                      " random walk's forecast is flat: today's "
                      "value, for ever. The other forecast decays like zero point nine nine nine to the h, "
                      "and slides back to its mean.") as tr:
            self.play(FadeIn(head))
            self.play(xmax.animate.set_value(300 + H), run_time=7, rate_func=smooth)
            self.fill(tr, 7.8)
        A = mk_ax()
        hl = DashedLine(A.c2p(993, -10), A.c2p(993, 0.5 * xb[-1]), color=YELLOW_, stroke_width=3)
        dot = Dot(A.c2p(993, 0.5 * xb[-1]), color=YELLOW_)
        hlt = MathTex(r"\text{half-life}=\frac{\ln 0.5}{\ln 0.999}\approx 693", font_size=36,
                      color=YELLOW_).next_to(dot, UR, buff=0.2)
        same = T("They agree about next year and disagree about the next century.", 28, GREY_).next_to(A, DOWN, buff=0.3)
        with self.say("Its half-life is about six hundred and ninety three periods. So the twins agree "
                      "on next year and disagree completely about the next century. That is the whole "
                      "difficulty: the data live in the left corner, the answer lives on the right.") as tr:
            self.play(Create(hl), FadeIn(dot), Write(hlt))
            self.play(FadeIn(same))
            self.fill(tr, 2.5)
        self.remove(ax, P, today)
        self.add(A, paths())

    # ------------------------------------------------------------------ aha: squares
    def squares(self):
        e1 = MathTex(r"\hat\rho-1", "=", r"\frac{\sum x_{t-1}\varepsilon_t}{\sum x_{t-1}^2}",
                     font_size=42).to_edge(UP, buff=0.4)
        with self.say("Under the unit root, the least squares estimate minus one is a ratio. Its "
                      "numerator hides a picture.") as tr:
            self.play(Write(e1))
            self.fill(tr, 1)
        e2 = MathTex(r"x_T^2", "=", r"2\sum x_{t-1}\varepsilon_t", "+", r"\sum\varepsilon_t^2",
                     font_size=42).to_edge(UP, buff=0.4)
        e3 = MathTex(r"\sum x_{t-1}\varepsilon_t", "=", r"\tfrac12\Big(", r"x_T^2", "-",
                     r"\sum\varepsilon_t^2", r"\Big)", font_size=42).to_edge(UP, buff=0.4)
        e3[3].set_color(YELLOW_)
        e3[5].set_color(GREY_)
        with self.say("Square the walk at its end point and the cross terms rearrange themselves: the "
                      "numerator is half the difference between two squares. Yellow: the end point "
                      "squared. Grey: the sum of all squared shocks.") as tr:
            self.play(FadeOut(e1, shift=UP * 0.3), FadeIn(e2, shift=UP * 0.3))
            self.wait(1.2)
            self.play(TransformMatchingTex(e2, e3), run_time=1.6)
            self.fill(tr, 3.6)
        np.random.seed(2026)
        E = np.random.randn(6, 100)
        panels = VGroup()
        for k in range(6):
            r, c = divmod(k, 3)
            cen = np.array([-4.5 + 4.5 * c, 1.15 - 2.85 * r, 0])
            x = np.concatenate([[0], np.cumsum(E[k])])
            m = max(abs(x).max(), 1)
            pax = Axes(x_range=[0, 100, 100], y_range=[-m, m, m], x_length=1.9, y_length=1.7, tips=False,
                       axis_config={"color": DIM, "stroke_width": 2}).move_to(cen + LEFT * 1.05)
            path = series_path(pax, x, WHITE_, 2)
            s0 = 1.15
            corner = cen + RIGHT * 0.15 + DOWN * 0.85
            grey = Square(s0, color=GREY_, stroke_width=2, fill_opacity=0.25).move_to(corner, aligned_edge=DL)
            side = min(s0 * abs(x[-1]) / np.sqrt((E[k] ** 2).sum()), 2.0)
            yel = Square(side, color=YELLOW_, stroke_width=3, fill_color=YELLOW_, fill_opacity=0.35)
            yel.move_to(corner, aligned_edge=DL)
            neg = side < s0
            verdict = MathTex(r"\hat\rho<1" if neg else r"\hat\rho>1", font_size=32,
                              color=RED_ if neg else TEAL_).move_to(cen + DOWN * 1.2 + LEFT * 1.05)
            panels.add(VGroup(pax, path, grey, yel, verdict))
        with self.say("Draw six random walks. Most of the time the end point squared is the smaller "
                      "square, so the numerator is negative and rho hat falls below one, even though the "
                      "truth is exactly one.") as tr:
            for p in panels:
                self.play(FadeIn(p[0]), Create(p[1]), FadeIn(p[2]), run_time=0.6)
                self.play(GrowFromPoint(p[3], p[3].get_corner(DL)), FadeIn(p[4]), run_time=0.6)
            self.fill(tr, 7.2)
        cnt = MathTex(r"P(\hat\rho<1)\ \to\ P\big(\chi^2(1)<1\big)\approx0.68", font_size=42,
                      color=RED_).move_to(DOWN * 3.55)
        with self.say("In the limit this happens with probability zero point six eight. Rho hat "
                      "is biased downwards, and leans left.") as tr:
            self.play(Write(cnt))
            self.fill(tr, 1.5)

    # ------------------------------------------------------------------ histogram builds up
    def histogram(self):
        taus = df_draws()
        bins = np.arange(-5, 3.01, 0.25)
        bw = 0.25
        ax = Axes(x_range=[-5, 3, 1], y_range=[0, 0.65, 0.2], x_length=11.5, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [-4, -3, -2, -1, 0, 1, 2]}).shift(DOWN * 0.9)
        bell = ax.plot(norm.pdf, x_range=[-4, 3], color=GREY_, stroke_width=3)
        bl = MathTex(r"N(0,1)", font_size=34, color=GREY_).move_to(ax.c2p(1.9, 0.38))
        m = ValueTracker(1)
        which = [0]

        def bars():
            d = taus[which[0]][: int(m.get_value())]
            h, _ = np.histogram(d, bins)
            h = h / max(len(d), 1) / bw
            g = VGroup()
            for i, hh in enumerate(h):
                if hh <= 0:
                    continue
                g.add(Rectangle(width=ax.x_length * bw / 8, height=ax.y_length * min(hh, 0.65) / 0.65,
                                stroke_width=1, stroke_color=BG, fill_color=RED_, fill_opacity=0.75)
                      .move_to(ax.c2p(bins[i] + bw / 2, 0), aligned_edge=DOWN))
            return g

        B = always_redraw(bars)
        cnt = always_redraw(lambda: T(f"random walks simulated: {int(m.get_value()):,}", 28, RED_)
                            .to_corner(UL, buff=0.5))
        head = MathTex(r"\tau=\frac{\hat\rho-1}{SE(\hat\rho)}", font_size=42).to_corner(UR, buff=0.45)
        self.play(Create(ax), Create(bell), FadeIn(bl), FadeIn(head))
        self.add(B, cnt)
        with self.say("So the usual t ratio cannot be compared with the bell curve. Watch its true "
                      "distribution build up, one simulated random walk at a time. The histogram settles "
                      "to the left of the bell, with a long left tail.") as tr:
            self.play(m.animate.set_value(60), run_time=2.5, rate_func=linear)
            self.play(m.animate.set_value(6000), run_time=5, rate_func=rate_functions.ease_in_quad)
            self.fill(tr, 7.5)
        self.remove(B)
        B0 = bars()
        self.add(B0)
        cn = DashedLine(ax.c2p(-1.645, 0), ax.c2p(-1.645, 0.55), color=GREY_, stroke_width=3)
        cnl = MathTex("-1.645", font_size=30, color=GREY_).next_to(cn.get_top(), RIGHT, buff=0.1)
        cvals = (-1.94, -2.86, -3.41)
        names = (r"\text{no constant}", r"\text{constant}", r"\text{constant + trend}")
        cd = DashedLine(ax.c2p(cvals[0], 0), ax.c2p(cvals[0], 0.62), color=YELLOW_, stroke_width=4)
        cdl = MathTex(f"{cvals[0]}", font_size=34, color=YELLOW_).next_to(cd, UP, buff=0.08)
        nm = MathTex(names[0], font_size=34, color=RED_).next_to(cnt, DOWN, aligned_edge=LEFT, buff=0.2)
        with self.say("The bell's five percent point is minus one point six four five; the "
                      "Dickey Fuller five percent point is minus one point nine four. Add a constant to "
                      "the regression and it moves to minus two point eight six; add a trend, minus "
                      "three point four one. Each deterministic term pushes the critical value further "
                      "left.") as tr:
            self.play(Create(cn), FadeIn(cnl), FadeIn(nm))
            self.play(Create(cd), FadeIn(cdl))
            self.wait(1.5)
            for k in (1, 2):
                which[0] = k
                newB = bars()
                cd2 = DashedLine(ax.c2p(cvals[k], 0), ax.c2p(cvals[k], 0.62), color=YELLOW_, stroke_width=4)
                cdl2 = MathTex(f"{cvals[k]}", font_size=34, color=YELLOW_).next_to(cd2, UP, buff=0.08)
                nm2 = MathTex(names[k], font_size=34, color=RED_).move_to(nm, aligned_edge=LEFT)
                self.play(Transform(B0, newB), Transform(cd, cd2), Transform(cdl, cdl2), Transform(nm, nm2),
                          run_time=1.8)
                self.wait(1.2)
            self.fill(tr, 9.6)
        self.remove(cnt)
        self.add(T(f"random walks simulated: 6,000", 28, RED_).to_corner(UL, buff=0.5))

    # ------------------------------------------------------------------ the twins again: power
    def power(self):
        rates = (0.057, 0.054, 0.617)
        labs = (r"\rho=1", r"\rho=0.999", r"\rho=0.95")
        cols = (RED_, BLUE_, TEAL_)
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 0.8, 0.2], x_length=7, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [0.2, 0.4, 0.6, 0.8]}).shift(DOWN * 0.7)
        head = T("How often does the test reject the unit root?  (5% level, T = 300)", 30).to_edge(UP, buff=0.45)
        five = DashedLine(ax.c2p(0, 0.05), ax.c2p(3, 0.05), color=YELLOW_, stroke_width=3)
        fl = MathTex(r"5\%", font_size=32, color=YELLOW_).next_to(five, RIGHT, buff=0.15)
        bars = VGroup()
        for i, (r, l, c) in enumerate(zip(rates, labs, cols)):
            bar = Rectangle(width=1.4, height=ax.y_length * r / 0.8, color=c, fill_opacity=0.8, stroke_width=0)
            bar.move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN)
            lab = MathTex(l, font_size=36, color=c).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.3)
            val = MathTex(f"{100 * r:.1f}\\%", font_size=34, color=c).next_to(bar, UP, buff=0.12)
            bars.add(VGroup(bar, lab, val))
        with self.say("Ask the test about the twins. With three hundred observations it rejects the "
                      "random walk about five percent of the time, as designed. Against the twin with "
                      "rho equal to zero point nine nine nine it also rejects about five percent of the "
                      "time: the power of the test equals its size. Even rho equal to zero point nine "
                      "five is missed four times in ten.") as tr:
            self.play(FadeIn(head), Create(ax), Create(five), FadeIn(fl))
            for b in bars:
                self.play(FadeIn(b[1]), GrowFromEdge(b[0], DOWN), run_time=1.1)
                self.play(FadeIn(b[2]), run_time=0.4)
                self.wait(0.8)
            self.fill(tr, 7.3)
        msg = VGroup(T("Not rejecting means:", 28, YELLOW_), T("shocks are very persistent,", 28, YELLOW_),
                     T("not that rho is exactly one.", 28, YELLOW_)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        with self.say("This is not a defect of one test. It is in the problem. When we fail to reject, "
                      "we learn that shocks are very persistent, not that rho is exactly one.") as tr:
            self.play(VGroup(ax, five, fl, bars).animate.shift(LEFT * 2.0), run_time=1)
            msg.to_edge(RIGHT, buff=0.5).shift(UP * 0.6)
            self.play(FadeIn(msg))
            self.fill(tr, 2)

    # ------------------------------------------------------------------ closing card
    def closing(self):
        s = VGroup(T("Under a unit root, rho hat leans left.", 36, YELLOW_),
                   T("Test with Dickey–Fuller, not with the bell.", 36, YELLOW_)).arrange(DOWN, buff=0.25)
        f = MathTex(r"\tau=\frac{\hat\rho-1}{SE(\hat\rho)}\ \xrightarrow{d}\ "
                    r"\frac{\int_0^1\mathcal B\,d\mathcal B}{\big(\int_0^1\mathcal B(r)^2dr\big)^{1/2}}",
                    font_size=48)
        g = VGroup(s, f).arrange(DOWN, buff=0.8)
        with self.say("So: under a unit root the estimate of rho leans to the left, and the "
                      "t ratio follows the Dickey Fuller distribution, a functional of Brownian motion, "
                      "not the bell curve.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f), run_time=2)
            self.fill(tr, 3)
