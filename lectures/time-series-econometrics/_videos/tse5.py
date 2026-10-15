"""Lecture 5 intuition film: the exam the model did not see (out-of-sample evaluation, windows, Diebold-Mariano)."""
from common import *


def polyfit(x, d, R=40):
    Z = lambda t: np.vander(np.asarray(t) / R, d + 1, increasing=True)
    b = np.linalg.lstsq(Z(np.arange(1, R + 1)), x[:R], rcond=None)[0]
    return lambda t: Z(np.atleast_1d(t)) @ b


class Tse5(IntuitionScene):
    parts = ("cold_open", "price", "windows", "dm", "closing")

    # ------------------------------------------------------------------ cold open
    def cold_open(self):
        np.random.seed(2026)
        x = np.random.randn(45)
        ax = Axes(x_range=[0, 46, 5], y_range=[-4, 4, 2], x_length=11.4, y_length=5.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [-4, -2, 0, 2, 4]}).shift(DOWN * 0.45)
        dots = VGroup(*[Dot(ax.c2p(t + 1, x[t]), radius=0.06, color=GREY_) for t in range(40)])
        lab = T("forty draws of pure noise", 28, GREY_).to_corner(UL, buff=0.45)
        with self.say("Forty observations of pure noise. Nothing in them can be predicted.") as tr:
            self.play(Create(ax), FadeIn(lab))
            self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.05), run_time=2.5)
            self.fill(tr, 3.5)

        def fitcurve(d):
            f = polyfit(x, d)
            ts = np.linspace(1, 40, 160)
            return VMobject(color=RED_, stroke_width=4).set_points_smoothly([ax.c2p(t, f(t)[0]) for t in ts])

        def ins(d):
            f = polyfit(x, d)
            return np.mean((x[:40] - f(np.arange(1, 41))) ** 2)

        cur = fitcurve(0)
        rd = MathTex(r"\text{degree } 0", font_size=36, color=RED_).to_corner(UR, buff=0.45)
        mse = MathTex(rf"\text{{in-sample error}} = {ins(0):.2f}", font_size=36, color=BLUE_).next_to(rd, DOWN, buff=0.2).align_to(rd, RIGHT)
        with self.say("Yet a polynomial in time, of degree zero, one, two, up to six, fits them better and "
                      "better. The in-sample error falls with every degree.") as tr:
            self.play(Create(cur), FadeIn(rd), FadeIn(mse))
            for d in range(1, 7):
                self.play(Transform(cur, fitcurve(d)),
                          Transform(rd, MathTex(rf"\text{{degree }} {d}", font_size=36, color=RED_).move_to(rd, aligned_edge=RIGHT)),
                          Transform(mse, MathTex(rf"\text{{in-sample error}} = {ins(d):.2f}", font_size=36, color=BLUE_).move_to(mse, aligned_edge=RIGHT)),
                          run_time=0.9)
            self.fill(tr, 7)
        curtain = Rectangle(width=ax.c2p(46, 0)[0] - ax.c2p(40.5, 0)[0], height=5.4, fill_color=DIM, fill_opacity=1,
                            stroke_width=0).move_to([(ax.c2p(46, 0)[0] + ax.c2p(40.5, 0)[0]) / 2, ax.c2p(0, 0)[1], 0])
        ct = T("exam", 28, WHITE_).move_to(curtain)
        self.play(FadeIn(curtain), FadeIn(ct))
        f6 = polyfit(x, 6)
        ts = [t for t in np.linspace(40, 46, 200) if abs(f6(t)[0]) < 4.3]
        ext = DashedVMobject(VMobject(color=RED_, stroke_width=4).set_points_smoothly([ax.c2p(t, f6(t)[0]) for t in ts]), num_dashes=24)
        new = VGroup(*[Dot(ax.c2p(t + 1, x[t]), radius=0.08, color=YELLOW_) for t in range(40, 45)])
        zero = DashedLine(ax.c2p(0, 0), ax.c2p(46, 0), color=TEAL_, stroke_width=3)
        zl = T("best forecast: 0", 28, TEAL_).move_to(ax.c2p(2, -3.4), aligned_edge=LEFT)
        oos = np.mean((x[40:45] - f6(np.arange(41, 46))) ** 2)
        big = MathTex(rf"\text{{forecast error}} = {oos:,.0f}", font_size=40, color=YELLOW_).next_to(mse, DOWN, buff=0.25).align_to(mse, RIGHT)
        with self.say("Then come five new observations: the exam the model did not see. The polynomial leaves "
                      "the data behind and shoots off the chart. The best forecast of noise was the flat line "
                      "at zero all along.") as tr:
            self.play(FadeOut(curtain), FadeOut(ct))
            self.play(Create(ext), run_time=1.5)
            self.play(LaggedStart(*[FadeIn(d, scale=2) for d in new], lag_ratio=0.3))
            self.play(Write(big))
            self.play(Create(zero), FadeIn(zl))
            self.fill(tr, 6)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("The exam the model did not see", 5,
                        "Today: how to grade forecasts fairly, and how to tell whether one forecaster really "
                        "beats another.")

    # ---------------------------------------------------------------------- price
    def price(self):
        np.random.seed(2026)
        res = np.zeros((9, 2))
        for _ in range(1000):
            x = np.random.randn(45)
            for d in range(9):
                f = polyfit(x, d)
                res[d] += [np.mean((x[:40] - f(np.arange(1, 41))) ** 2), np.mean((x[40:] - f(np.arange(41, 46))) ** 2)]
        res /= 1000
        top = 5.0
        ax = Axes(x_range=[-0.7, 8.7, 1], y_range=[0, top, 1], x_length=10.4, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": range(9)}, y_axis_config={"numbers_to_include": [1, 2, 3, 4, 5]}).shift(DOWN * 0.35 + LEFT * 0.2)
        xl = T("polynomial degree", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.4)
        sig = DashedLine(ax.c2p(-0.7, 1), ax.c2p(8.7, 1), color=GREY_, stroke_width=2)
        sl = MathTex(r"\sigma^2", font_size=32, color=GREY_).next_to(ax.c2p(8.7, 1), RIGHT, buff=0.1)
        leg = VGroup(VGroup(Square(0.25, fill_color=BLUE_, fill_opacity=1, stroke_width=0), T("in-sample error", 26, BLUE_)).arrange(RIGHT, buff=0.15),
                     VGroup(Square(0.25, fill_color=RED_, fill_opacity=1, stroke_width=0), T("forecast error", 26, RED_)).arrange(RIGHT, buff=0.15)
                     ).arrange(RIGHT, buff=0.6).to_edge(UP, buff=0.45).to_edge(LEFT, buff=0.6)
        w = ax.c2p(0.35, 0)[0] - ax.c2p(0, 0)[0]
        bars, tops = VGroup(), VGroup()
        for d in range(9):
            for j, col, off in ((0, BLUE_, -0.19), (1, RED_, 0.19)):
                v = min(res[d, j], top)
                b = Rectangle(width=w, height=max(ax.c2p(0, v)[1] - ax.c2p(0, 0)[1], 0.01), fill_color=col, fill_opacity=0.85,
                              stroke_width=0).move_to(ax.c2p(d + off, 0), aligned_edge=DOWN)
                bars.add(b)
                if res[d, j] > top:
                    tops.add(MathTex(f"{res[d, j]:,.0f}", font_size=30, color=RED_).rotate(PI / 2).next_to(b, UP, buff=0.12))
        with self.say("Repeat this on a thousand samples and the pattern becomes a law. Each extra degree "
                      "lowers the in-sample error a little, and raises the forecast error a lot, until it "
                      "breaks through the ceiling.") as tr:
            self.play(Create(ax), FadeIn(xl), FadeIn(leg), Create(sig), FadeIn(sl))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12), run_time=5)
            self.play(FadeIn(tops))
            self.fill(tr, 7.5)
        eq = MathTex(r"E(x_{T+1}-\bar x_T)^2 = \sigma^2\Big(1+\frac1T\Big)", font_size=40, color=YELLOW_).to_edge(UP, buff=0.4).to_edge(RIGHT, buff=0.5)
        with self.say("Even one redundant parameter, a constant fitted to noise, costs sigma squared over T. "
                      "In-sample fit measures how well a model explains what it has seen. Only data it has "
                      "not seen can grade a forecast.") as tr:
            self.play(Write(eq))
            self.fill(tr, 1.5)

    # -------------------------------------------------------------------- windows
    def windows(self):
        np.random.seed(2026)
        N, R, Bk = 150, 60, 100
        x = np.random.randn(N) * 0.8 + np.where(np.arange(N) >= Bk, 2.5, 0.0)
        ax = Axes(x_range=[0, N, 30], y_range=[-2.5, 5, 2.5], x_length=11.2, y_length=3.0, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}).shift(UP * 1.75 + RIGHT * 0.6)
        line = series_path(ax, x, GREY_, 2, x0=1)
        rows = {"fixed": (-0.95, PURPLE_), "rolling": (-1.95, TEAL_), "recursive": (-2.95, BLUE_)}
        X = lambda t: ax.c2p(t, 0)[0]
        labels = VGroup(*[T(k, 28, c).move_to([X(0) - 0.9, y, 0]) for k, (y, c) in rows.items()])
        tracks = VGroup(*[Line([X(1), y, 0], [X(N), y, 0], color=DIM, stroke_width=6) for (y, c) in rows.values()])
        split = DashedLine([X(R + 0.5), ax.c2p(0, 5)[1], 0], [X(R + 0.5), -3.4, 0], color=GREY_, stroke_width=2)
        rl = MathTex(r"R", font_size=32, color=GREY_).next_to(split, UP, buff=0.05)
        p = ValueTracker(1)

        def span(kind, pv):
            e = R + int(pv) - 1
            return {"fixed": (1, R), "rolling": (int(pv), e), "recursive": (1, e)}[kind]

        def finder(kind):
            y, c = rows[kind]

            def make():
                a, b = span(kind, p.get_value())
                l, r = X(a) - 0.05, X(b) + 0.05
                h, s = 0.32, 0.18
                g = VGroup(Rectangle(width=r - l, height=2 * h, stroke_width=0, fill_color=c, fill_opacity=0.25).move_to([(l + r) / 2, y, 0]))
                for cx, sx in ((l, 1), (r, -1)):
                    for cy, sy in ((y + h, -1), (y - h, 1)):
                        g.add(VMobject(color=c, stroke_width=4).set_points_as_corners(
                            [[cx + sx * s, cy, 0], [cx, cy, 0], [cx, cy + sy * s, 0]]))
                tgt = R + int(p.get_value())
                g.add(Dot([X(tgt), y, 0], radius=0.09, color=RED_))
                return g
            return always_redraw(make)

        def fpath(kind):
            y, c = rows[kind]

            def make():
                k = int(p.get_value())
                pts = []
                for q in range(1, k + 1):
                    a, b = span(kind, q)
                    pts.append(ax.c2p(R + q, x[a - 1:b].mean()))
                if len(pts) < 2:
                    pts = pts * 2
                return VMobject(color=c, stroke_width=4).set_points_as_corners(pts)
            return always_redraw(make)

        finders = [finder(k) for k in rows]
        with self.say("Split the sample: the first R observations to estimate, the remaining P to forecast, "
                      "one step at a time. How the estimation window moves is the choice of a camera.") as tr:
            self.play(Create(ax), Create(line))
            self.play(FadeIn(labels), FadeIn(tracks), Create(split), FadeIn(rl))
            self.add(*finders)
            self.fill(tr, 3)
        with self.say("The fixed camera never moves. The rolling camera keeps its width and slides along. "
                      "The recursive camera stays anchored at the start, and widens.") as tr:
            self.play(p.animate.set_value(36), run_time=tr.duration - 0.5, rate_func=linear)
        brk = DashedLine(ax.c2p(Bk, -2.5), ax.c2p(Bk, 5), color=YELLOW_, stroke_width=3)
        bl = T("the world changes", 26, YELLOW_).next_to(brk, UP, buff=0.08)
        paths = [fpath(k) for k in rows]
        with self.say("Now let the world change in the middle of the exam, and draw each camera's forecast. "
                      "The rolling window forgets the old regime and catches up. The recursive window averages "
                      "across the break and lags behind. The fixed window never finds out.") as tr:
            self.play(Create(brk), FadeIn(bl))
            self.add(*paths)
            self.play(p.animate.set_value(N - R), run_time=tr.duration - 1.5, rate_func=linear)
        with self.say("Neither moving camera wins everywhere. Rolling buys robustness to breaks with fewer "
                      "observations; recursive buys precision, if the world stands still.") as tr:
            self.wait(tr.duration)

    # ------------------------------------------------------------------------- dm
    def dm(self):
        np.random.seed(2026)
        E = np.random.randn(40, 201)
        e = E[34] * 1.4
        P = 160
        d = -0.35 + (e[1:] + 0.5 * e[:-1])[:P]

        def dmstat(n):
            z = d[:n]
            m = z.mean()
            g = [np.mean((z[j:] - m) * (z[:n - j] - m)) for j in range(3)]
            om = g[0] + 2 * (2 / 3 * g[1] + 1 / 3 * g[2])
            return np.sqrt(n) * m / np.sqrt(om)

        dms = np.array([dmstat(n) if n >= 8 else 0.0 for n in range(1, P + 1)])
        top = Axes(x_range=[0, P, 20], y_range=[-6, 6, 3], x_length=11.0, y_length=2.2, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}).shift(UP * 2.05 + RIGHT * 0.5)
        bot = Axes(x_range=[0, P, 20], y_range=[-4, 3, 1], x_length=11.0, y_length=3.0, tips=False,
                   axis_config={"color": GREY_, "font_size": 24},
                   y_axis_config={"numbers_to_include": [-3, -2, -1, 1, 2]}).shift(DOWN * 2.0 + RIGHT * 0.5)
        dl = MathTex(r"d_t = (e^A_t)^2-(e^B_t)^2", font_size=34).next_to(top, UP, buff=0.05).align_to(top, LEFT).shift(RIGHT * 0.2)
        aw = T("A better", 26, YELLOW_).next_to(top.c2p(0, -3), LEFT, buff=0.15)
        bw = T("B better", 26, PURPLE_).next_to(top.c2p(0, 3), LEFT, buff=0.15)
        n = ValueTracker(0)
        bw_ = top.c2p(0.8, 0)[0] - top.c2p(0, 0)[0]

        def bars():
            k = int(n.get_value())
            g = VGroup()
            for t in range(k):
                v = np.clip(d[t], -6, 6)
                h = abs(top.c2p(0, v)[1] - top.c2p(0, 0)[1])
                if h < 0.005:
                    continue
                g.add(Rectangle(width=bw_, height=h, stroke_width=0, fill_color=YELLOW_ if v < 0 else PURPLE_,
                                fill_opacity=0.85).move_to(top.c2p(t + 0.5, 0), aligned_edge=DOWN if v > 0 else UP))
            return g

        def path():
            k = int(n.get_value())
            if k < 9:
                return VMobject()
            return VMobject(color=WHITE_, stroke_width=4).set_points_as_corners([bot.c2p(t, dms[t - 1]) for t in range(8, k + 1)])

        def readout():
            k = int(n.get_value())
            v = dms[k - 1] if k >= 8 else 0.0
            col = YELLOW_ if v < -1.96 else WHITE_
            return T(f"P = {k},   DM = {v:+.2f}".replace("-", "−"), 32, col).next_to(bot, UP, buff=0.05).align_to(bot, RIGHT)

        band = Polygon(bot.c2p(0, -1.96), bot.c2p(P, -1.96), bot.c2p(P, 1.96), bot.c2p(0, 1.96),
                       stroke_width=0, fill_color=GREY_, fill_opacity=0.18)
        lo = DashedLine(bot.c2p(0, -1.96), bot.c2p(P, -1.96), color=YELLOW_, stroke_width=2)
        hi = DashedLine(bot.c2p(0, 1.96), bot.c2p(P, 1.96), color=PURPLE_, stroke_width=2)
        bandl = T("luck", 26, GREY_).move_to(bot.c2p(150, 1.2))
        with self.say("Two forecasters, A and B, sit the same exam. After each question we record the "
                      "difference of their squared errors, d t. Below the line, A did better; above it, B.") as tr:
            self.play(Create(top), FadeIn(dl), FadeIn(aw), FadeIn(bw))
            self.add(always_redraw(bars))
            self.play(n.animate.set_value(30), run_time=tr.duration - 1.5, rate_func=linear)
        dmf = MathTex(r"DM = \frac{\sqrt P\,\bar d}{\sqrt{\hat\Omega}}", font_size=40).next_to(bot, UP, buff=0.05).align_to(bot, LEFT).shift(RIGHT * 0.3)
        with self.say("The Diebold Mariano statistic is a running tally: the average difference, times root "
                      "P, divided by its long-run standard deviation. Forecast errors echo one another, so "
                      "omega is the long-run variance of lecture two, estimated by Newey and West.") as tr:
            self.play(Create(bot), FadeIn(band), Create(lo), Create(hi), FadeIn(bandl), Write(dmf))
            self.add(always_redraw(path), always_redraw(readout))
            self.play(n.animate.set_value(60), run_time=tr.duration - 2.5, rate_func=linear)
        with self.say("Early on, the tally wanders inside the band of plus or minus one point nine six: the "
                      "exam is too short to tell them apart. As questions accumulate, A's small edge stops "
                      "looking like luck, and the tally crosses minus one point nine six for good.") as tr:
            self.play(n.animate.set_value(P), run_time=tr.duration - 1, rate_func=linear)

    # -------------------------------------------------------------------- closing
    def closing(self):
        g = VGroup(
            T("grade a forecaster only on the exam it did not see;", 36, TEAL_),
            T("crown a winner only when the gap is larger than luck", 36, YELLOW_),
            MathTex(r"DM = \frac{\sqrt P\,\bar d}{\sqrt{\hat\Omega}} \;\xrightarrow[H_0]{d}\; N(0,1),\qquad "
                    r"\hat\Omega = \text{long-run variance of } d_t", font_size=40),
        ).arrange(DOWN, buff=0.55)
        with self.say("So: grade a forecaster only on the exam it did not see. And crown a winner only when "
                      "the gap in scores is larger than luck, measured with the long-run variance of the loss "
                      "differential.") as tr:
            for m in g:
                self.play(FadeIn(m, shift=UP * 0.2))
                self.wait(0.8)
            self.fill(tr, 4.5)
