"""Lecture 7 intuition film: the Wold decomposition — every stationary series is a choir of echoes."""
from common import *


def stems(ax, xs, ys, color, width=5, dot=0.07):
    g = VGroup()
    for x, y in zip(xs, ys):
        ln = Line(ax.c2p(x, 0), ax.c2p(x, y), color=color, stroke_width=width)
        d = Dot(ax.c2p(x, y), radius=dot, color=color)
        g.add(VGroup(ln, d))
    return g


def glow(path, color, w=3):
    halo = path.copy().set_stroke(color, width=w * 4, opacity=0.18)
    return VGroup(halo, path.set_stroke(color, width=w))


class Tse7(IntuitionScene):
    parts = ("hook", "choir", "innovation", "echo_length", "twins", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        dates, v = load_csv("GDPC1.csv")
        g = 400 * np.diff(np.log(v))[:291]
        ax = Axes(x_range=[0, 291, 40], y_range=[-12, 16, 4], x_length=12.4, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"include_numbers": True})
        ax.shift(DOWN * 0.7)
        years = VGroup(*[T(str(1947 + k // 4), 24, GREY_).next_to(ax.c2p(k, -12), DOWN, buff=0.15)
                         for k in (12, 92, 172, 252)])
        line = glow(series_path(ax, g, TEAL_, 2.5), TEAL_, 2.5)
        cap = T("US real GDP growth, annualised %, 1947–2019", 26, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        k = int(np.argmin(g))  # 1958 Q1, the deepest quarter before 2020
        hit = Circle(radius=0.28, color=YELLOW_, stroke_width=4).move_to(ax.c2p(k, g[k]))
        q = T("A quarter like this one: how long is it still felt?", 32, YELLOW_).to_edge(UP, buff=0.45)
        with self.say("Seventy years of American output growth. Every quarter brings news nobody "
                      "expected: a strike, an oil shock, a good harvest. Take one bad quarter, like "
                      "this one in nineteen fifty-eight. How long is it still felt?") as tr:
            self.play(Create(ax), FadeIn(years), FadeIn(cap))
            self.play(Create(line), run_time=4, rate_func=linear)
            self.play(Create(hit), Write(q))
            self.fill(tr, 7.5)
        self.play(FadeOut(VGroup(ax, years, line, cap, hit, q)))
        self.title_card("The Wold decomposition", 7,
                        "Herman Wold answered in nineteen thirty-eight. Every stationary series is a "
                        "choir of echoes of its own past surprises.")

    # ------------------------------------------------------------------ the choir
    def choir(self):
        rho = 0.72
        top = Axes(x_range=[0, 24, 2], y_range=[-1.8, 1.8, 1], x_length=12.4, y_length=2.7, tips=False,
                   axis_config={"color": GREY_}).shift(UP * 1.85)
        bot = Axes(x_range=[0, 24, 2], y_range=[-2.4, 2.4, 1], x_length=12.4, y_length=2.9, tips=False,
                   axis_config={"color": GREY_}).shift(DOWN * 2.1)
        lt = T("surprises and their echoes", 26, GREY_).next_to(top, UP, buff=0.05).align_to(top, LEFT)
        bells = [(2, 1.5, YELLOW_), (7, -1.3, BLUE_), (11, 1.1, RED_), (15, -0.9, PURPLE_)]
        offs = [-0.21, -0.07, 0.07, 0.21]

        t0, e0, c0 = bells[0]
        strike = stems(top, [t0], [e0], c0, width=7, dot=0.09)
        ring = Circle(radius=0.15, color=c0, stroke_width=4).move_to(top.c2p(t0, e0))
        js = np.arange(1, 24 - t0)
        echo0 = stems(top, t0 + js + offs[0], e0 * rho ** js, c0, width=4, dot=0.05)
        psi = MathTex(r"\psi_1,\ \psi_2,\ \psi_3,\ \dots", font_size=36, color=c0).move_to(top.c2p(9, 1.45))
        with self.say("Think of each surprise as a bell being struck. It rings loudest at the moment it "
                      "is struck, and then it fades: a fraction psi one of it is still heard one period "
                      "later, psi two after two periods, and so on.") as tr:
            self.play(Create(top), FadeIn(lt))
            self.play(GrowFromPoint(strike, top.c2p(t0, 0)), run_time=0.6)
            self.play(ring.animate.scale(6).set_opacity(0), run_time=0.9)
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in echo0], lag_ratio=0.25), run_time=3.5)
            self.play(Write(psi))
            self.fill(tr, 6)

        voices = [(strike, echo0)]
        with self.say("Strike more bells, each with its own force and sign. At any date, many of them "
                      "are still ringing at once.") as tr:
            for (t, e, c), o in zip(bells[1:], offs[1:]):
                s = stems(top, [t + o], [e], c, width=7, dot=0.09)
                js = np.arange(1, 24 - t)
                ec = stems(top, t + o + js, e * rho ** js, c, width=4, dot=0.05)
                self.play(GrowFromPoint(s, top.c2p(t, 0)), run_time=0.4)
                self.play(LaggedStart(*[FadeIn(x) for x in ec], lag_ratio=0.1), run_time=1.0)
                voices.append((s, ec))
            self.play(FadeOut(psi))
            self.fill(tr, 4.6)

        # stack every voice at each date: the series is the sum of what is still ringing
        contrib = {t: [] for t in range(25)}
        for (t, e, c) in bells:
            for j in range(0, 24 - t):
                contrib[t + j].append((e * rho ** j, c))
        segs, tops = VGroup(), []
        for t in range(25):
            base = 0.0
            for val, c in contrib[t]:
                segs.add(Line(bot.c2p(t, base), bot.c2p(t, base + val), color=c, stroke_width=6))
                base += val
            tops.append(base)
        srcs = VGroup()
        for (s, ec) in voices:
            srcs.add(*[m[0].copy() for m in s], *[m[0].copy() for m in ec])
        series = series_path(bot, tops, WHITE_, 3)
        dots = VGroup(*[Dot(bot.c2p(t, y), radius=0.06, color=WHITE_) for t, y in enumerate(tops)])
        lb = T("the series = what is still ringing", 26, GREY_).next_to(bot, UP, buff=0.05).align_to(bot, LEFT)
        with self.say("Now add up, date by date, everything that is still sounding. Stack the echoes on "
                      "top of one another, and the tops trace out a time series.") as tr:
            self.play(Create(bot), FadeIn(lb))
            self.play(ReplacementTransform(srcs, segs), run_time=3)
            self.play(FadeIn(dots), Create(series), run_time=1.5)
            self.fill(tr, 5.5)
        wold = MathTex(r"x_t", r"=", r"\mu", r"+", r"\sum_{j=0}^{\infty}", r"\psi_j", r"\,\varepsilon_{t-j}",
                       font_size=46).move_to(top)
        wold[5].set_color(YELLOW_)
        wold[6].set_color(TEAL_)
        box = SurroundingRectangle(wold, color=YELLOW_, buff=0.2, corner_radius=0.1)
        old = VGroup(*[m for v in voices for m in v], lt, top)
        with self.say("That is the Wold decomposition. The series is its mean plus every past surprise, "
                      "epsilon t minus j, weighted by how much of its echo is left, psi j, with psi zero "
                      "equal to one.") as tr:
            self.play(FadeOut(old), run_time=0.8)
            self.play(Write(wold), run_time=2)
            self.play(Create(box))
            self.fill(tr, 3.8)

    # ------------------------------------------------------------------ what is a surprise
    def innovation(self):
        np.random.seed(2026)
        rho, n = 0.7, 16
        e = np.random.normal(0, 1, n)
        e[n - 1] = 1.9
        x = np.zeros(n)
        for t in range(1, n):
            x[t] = rho * x[t - 1] + e[t]
        ax = Axes(x_range=[0, n, 2], y_range=[-3, 3, 1], x_length=9.0, y_length=4.6, tips=False,
                  axis_config={"color": GREY_}).shift(DOWN * 0.6 + LEFT * 1.6)
        k = n - 1
        past = series_path(ax, x[:k], BLUE_, 3)
        pd = VGroup(*[Dot(ax.c2p(t, x[t]), radius=0.06, color=BLUE_) for t in range(k)])
        fc = rho * x[k - 1]
        hollow = Circle(radius=0.12, color=GREY_, stroke_width=4).move_to(ax.c2p(k, fc))
        dash = DashedLine(ax.c2p(k - 1, x[k - 1]), ax.c2p(k, fc), color=GREY_)
        act = Dot(ax.c2p(k, x[k]), radius=0.11, color=WHITE_)
        gap = Line(ax.c2p(k, fc), ax.c2p(k, x[k]), color=YELLOW_, stroke_width=7)
        lab_f = VGroup(T("best forecast", 26, GREY_), T("from the whole past", 26, GREY_)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        lab_f.next_to(hollow, RIGHT, buff=0.3).align_to(hollow, UP)
        lab_a = T("what happened", 26).next_to(act, RIGHT, buff=0.3)
        lab_e = MathTex(r"\varepsilon_t", font_size=44, color=YELLOW_).next_to(Line(ax.c2p(k, fc), ax.c2p(k, x[k])), LEFT, buff=0.2)
        eq = MathTex(r"\varepsilon_t", r"=", r"x_t-\operatorname{Proj}(x_t\mid x_{t-1},x_{t-2},\dots)",
                     font_size=40).to_edge(UP, buff=0.5)
        eq[0].set_color(YELLOW_)
        with self.say("Which surprises, exactly? Not any shocks we please. Stand at date t with the "
                      "whole past in hand, and make the best linear forecast. The surprise is the gap "
                      "between what happens and that forecast: the innovation. By construction no "
                      "function of the past can predict it, which is why it deserves the name.") as tr:
            self.play(Create(ax), Create(past), FadeIn(pd), run_time=2)
            self.play(Create(dash), FadeIn(hollow), FadeIn(lab_f))
            self.play(FadeIn(act, scale=2), FadeIn(lab_a))
            self.play(Create(gap), FadeIn(lab_e), Write(eq))
            self.fill(tr, 7)

    # ------------------------------------------------------------------ the length of the echo
    def echo_length(self):
        np.random.seed(2026)
        e = np.random.normal(0, 1, 160)
        r = ValueTracker(0.3)
        left = Axes(x_range=[0, 15, 5], y_range=[0, 1.1, 0.5], x_length=4.6, y_length=3.6, tips=False,
                    axis_config={"color": GREY_, "font_size": 24, "include_numbers": True}).move_to(LEFT * 4.2 + DOWN * 0.4)
        right = Axes(x_range=[0, 160, 40], y_range=[-6, 6, 3], x_length=7.2, y_length=3.6, tips=False,
                     axis_config={"color": GREY_}).move_to(RIGHT * 2.9 + DOWN * 0.4)
        ll = MathTex(r"\text{one bell: }\psi_j=\rho^j", font_size=34, color=YELLOW_).next_to(left, UP, buff=0.25)
        rl = T("the choir, same strikes", 26, TEAL_).next_to(right, UP, buff=0.25)

        def irf():
            p = r.get_value()
            return stems(left, np.arange(16), p ** np.arange(16), YELLOW_, width=4, dot=0.05)

        def path():
            p, x, xs = r.get_value(), 0.0, []
            for v in e:
                x = p * x + v * np.sqrt(1 - p * p) * 1.6
                xs.append(x)
            return series_path(right, xs, TEAL_, 2.5)

        S = always_redraw(irf)
        P = always_redraw(path)
        rv = VGroup(MathTex(r"\rho=", font_size=40, color=YELLOW_),
                    DecimalNumber(0.3, num_decimal_places=2, font_size=40, color=YELLOW_)).arrange(RIGHT, buff=0.12)
        rv.move_to(LEFT * 4.2 + UP * 2.9)
        rv[1].add_updater(lambda m: m.set_value(r.get_value()))
        lr = VGroup(MathTex(r"\psi(1)=\textstyle\sum_j\psi_j=", font_size=38, color=PURPLE_),
                    DecimalNumber(1 / 0.1, num_decimal_places=1, font_size=38, color=PURPLE_)).arrange(RIGHT, buff=0.12)
        lr.move_to(RIGHT * 2.9 + DOWN * 3.3)
        lr[1].add_updater(lambda m: m.set_value(1 / (1 - r.get_value())))
        with self.say("The weights psi j carry the whole personality of a series. Let the echo last "
                      "longer, and the same strikes sing a slower, smoother, more persistent tune.") as tr:
            self.play(Create(left), Create(right), FadeIn(ll), FadeIn(rl))
            self.add(S, P, rv)
            self.play(r.animate.set_value(0.9), run_time=5, rate_func=smooth)
            self.fill(tr, 6)
        with self.say("Add up all the echoes of one bell and you get psi of one, the total effect of a "
                      "surprise. Squared and times sigma squared, it is the long-run variance of "
                      "lecture two.") as tr:
            self.play(FadeIn(lr))
            self.play(r.animate.set_value(0.5), run_time=3)
            self.fill(tr, 4)

    # ------------------------------------------------------------------ mirror twins
    def twins(self):
        u = 0.75
        mirror = DashedLine(UP * 3.3, DOWN * 0.5, color=GREY_, dash_length=0.12)

        def panel(cx, hs, col, eqtex):
            ax = Axes(x_range=[-0.5, 2.5, 1], y_range=[0, 2.4, 1], x_length=4.2, y_length=2.4, tips=False,
                      axis_config={"color": GREY_}).move_to([cx, 0.85, 0])
            st = stems(ax, [0, 1], hs, col, width=8, dot=0.1)
            lags = VGroup(*[MathTex(rf"\psi_{j}", font_size=30, color=GREY_).next_to(ax.c2p(j, 0), DOWN, buff=0.15)
                            for j in (0, 1)])
            eq = MathTex(eqtex, font_size=36, color=col).move_to([cx, 2.95, 0])
            return ax, st, lags, eq

        axL, stL, lgL, eqL = panel(-3.6, [1, 2], RED_, r"x_t=\varepsilon_t+2\,\varepsilon_{t-1},\ \ \sigma=1")
        axR, stR, lgR, eqR = panel(3.6, [2, 1], GREEN_, r"x_t=\tilde\varepsilon_t+\tfrac12\tilde\varepsilon_{t-1},\ \ \sigma=2")
        with self.say("Here is a puzzle. Two moving averages of order one: theta equal to two with unit "
                      "noise, and theta equal to one half with noise of standard deviation two.") as tr:
            self.play(Create(mirror))
            self.play(FadeIn(eqL), Create(axL), FadeIn(stL), FadeIn(lgL))
            self.play(FadeIn(eqR), Create(axR), FadeIn(stR), FadeIn(lgR))
            self.fill(tr, 3)
        ghost = stL.copy()
        with self.say("Hold the first echo up to a mirror, reversing time, and it lands exactly on the "
                      "second. Autocovariances cannot see the direction of time, so the twins have the "
                      "same ones: five, then two, then zero.") as tr:
            self.play(ghost.animate.flip(UP).move_to(stR), run_time=2.2)
            self.play(Indicate(stR, color=YELLOW_), FadeOut(ghost))
            acf = MathTex(r"\gamma_0=5,\quad\gamma_1=2,\quad\gamma_k=0\ (k\ge2)", font_size=40,
                          color=YELLOW_).move_to(DOWN * 1.05)
            self.play(Write(acf))
            self.fill(tr, 4.5)

        # recovering the surprise: a starting error is multiplied by -theta every period
        axE = Axes(x_range=[-0.5, 6.5, 1], y_range=[0, 2.0, 1], x_length=5.2, y_length=1.7, tips=False,
                   axis_config={"color": GREY_})
        axE1 = axE.copy().move_to([-3.6, -2.75, 0])
        axE2 = axE.copy().move_to([3.6, -2.75, 0])
        bl = stems(axE1, np.arange(7), 2.0 ** np.arange(7) / 32, RED_, width=6, dot=0.06)
        br = stems(axE2, np.arange(7), 0.5 ** np.arange(7) * 1.6, GREEN_, width=6, dot=0.06)
        tL = T("error ×2 each period", 24, RED_).next_to(axE1, DOWN, buff=0.12)
        tR = T("error ×½ each period", 24, GREEN_).next_to(axE2, DOWN, buff=0.12)
        with self.say("Yet only one of them can be recovered from the data. Rebuild the surprises "
                      "from the past of x, starting from a wrong guess. With theta two the error doubles "
                      "every period and explodes; with theta one half it dies away. Wold always picks "
                      "the invertible twin, the one whose surprises the past can reveal.") as tr:
            div = DashedLine(DOWN * 1.7, DOWN * 3.7, color=GREY_, dash_length=0.12)
            self.play(FadeOut(acf), Create(axE1), Create(axE2), Create(div))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bl], lag_ratio=0.3),
                      LaggedStart(*[GrowFromEdge(b, DOWN) for b in br], lag_ratio=0.3), run_time=3.5)
            self.play(FadeIn(tL), FadeIn(tR))
            cross = Cross(VGroup(eqL), stroke_color=RED_, stroke_width=5)
            tick = SurroundingRectangle(eqR, color=GREEN_, buff=0.12, corner_radius=0.08)
            self.play(Create(cross), Create(tick))
            self.fill(tr, 7)

    # ------------------------------------------------------------------ closing
    def closing(self):
        s = T("Every stationary series is a sum of echoes of its own surprises.", 34)
        f = MathTex(r"x_t=E\,x_t+\sum_{j=0}^{\infty}\psi_j\,\varepsilon_{t-j},\qquad \psi_0=1,\quad "
                    r"\sum_j\psi_j^2<\infty", font_size=44, color=YELLOW_)
        g = VGroup(s, f).arrange(DOWN, buff=0.7)
        with self.say("So: every stationary series is a sum of echoes of its own surprises. The "
                      "surprises are the innovations, the echoes are the impulse response, and the "
                      "models of the next lecture are just economical ways to describe them.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f), run_time=2.5)
            self.fill(tr, 4)
        self.wait(1)
