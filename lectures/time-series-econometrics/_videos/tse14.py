"""Lecture 14 intuition film: VAR impulse responses as dominoes; spurious regression vs the drunk and her dog."""
from common import *

MONEY = BLUE_      # money growth, and the drunk (the "x" series)
PRICE = PURPLE_    # inflation
SHOCK = RED_       # the shock, and the stranger / spurious partner
DOG = YELLOW_      # the dog
LEASH = GREEN_     # the stationary combination

A = np.array([[0.5, 0.2], [0.3, 0.4]])
L = np.array([[1.0, 0.0], [0.5, 1.0]])


def ols_t(x, y):
    X = np.c_[np.ones(len(x)), x]
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    se = np.sqrt(e @ e / (len(x) - 2) * np.linalg.inv(X.T @ X)[1, 1])
    return b[1] / se, 1 - e @ e / ((y - y.mean()) @ (y - y.mean()))


def coin_pair():
    """The most convincing-looking of 200 independent random-walk pairs (T = 200)."""
    np.random.seed(2026)
    best = None
    for _ in range(200):
        x, y = np.cumsum(np.random.randn(200)), np.cumsum(np.random.randn(200))
        t, r2 = ols_t(x, y)
        if t > 0 and (best is None or r2 > best[3]):
            best = (x, y, t, r2)
    return best


def domino(base, ang, color):
    """A domino standing on point base, tilted clockwise (to the right) by ang radians."""
    w, h = 0.24, 1.1
    r = Rectangle(width=w, height=h, stroke_width=2, stroke_color=WHITE_, fill_color=color, fill_opacity=0.85)
    r.move_to(base + UP * h / 2)
    r.rotate(-ang, about_point=base + RIGHT * w / 2)
    return r


def top_of(base, ang):
    h, w = 1.1, 0.24
    return base + np.array([w / 2 - w / 2 * np.cos(ang) + h * np.sin(ang), w / 2 * np.sin(ang) + h * np.cos(ang), 0])


class Tse14(IntuitionScene):
    parts = ("hook", "dominoes", "spurious", "leash", "closing")

    def freeze(self):
        for m in self.mobjects:
            for f in m.get_family():
                f.clear_updaters()

    def hook(self):
        x, y, t, r2 = coin_pair()
        lo, hi = min(x.min(), y.min()) - 1, max(x.max(), y.max()) + 1
        ax = Axes(x_range=[0, 200, 50], y_range=[lo, hi, 10], x_length=12.2, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}).shift(DOWN * 0.3)
        px, py = series_path(ax, x, MONEY, 4), series_path(ax, y, SHOCK, 4)
        la = T("series A", 28, MONEY).to_corner(UL, buff=0.5)
        lb = T("series B", 28, SHOCK).next_to(la, RIGHT, buff=0.6)
        stat = MathTex(rf"t={t:.1f}", r",\quad", rf"R^2={r2:.2f}", font_size=40, color=YELLOW_).to_corner(UR, buff=0.5)
        with self.say("Two series, two hundred quarters. They rise together and fall together, and a "
                      "regression of one on the other gives a t statistic of twenty-five, far beyond one "
                      "point nine six. A discovery?") as tr:
            self.play(Create(ax), FadeIn(la), FadeIn(lb))
            self.play(Create(px), Create(py), run_time=5, rate_func=linear)
            self.play(Write(stat))
            self.fill(tr, 7)
        coins = VGroup(*[Circle(0.22, color=YELLOW_, fill_color=YELLOW_, fill_opacity=0.3).add(T(s, 24, YELLOW_))
                         for s in ("H", "T", "T", "H", "T", "H")]).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.3)
        msg = T("two independent coin-flip walks", 32, YELLOW_).next_to(coins, LEFT, buff=0.4)
        g = VGroup(msg, coins).move_to(DOWN * 3.5)
        with self.say("Both were made by flipping coins, independently. Nothing connects them.") as tr:
            self.play(LaggedStart(*[FadeIn(c, scale=0.3) for c in coins], lag_ratio=0.15), FadeIn(msg))
            self.fill(tr, 1.5)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("Dominoes and a leash", 14,
                        "Today: how a shock travels from one series to another, and when moving together "
                        "means something.")

    def dominoes(self):
        H = 8
        xs = [-5.0 + 1.35 * h for h in range(H)]
        yt, yb = 1.0, -1.5
        psi = [np.linalg.matrix_power(A, h) @ L for h in range(H)]
        resp = np.array([p[:, 0] for p in psi])          # response to a money shock
        k = np.deg2rad(70)
        lm = T("money growth", 28, MONEY).move_to([-6.6, yt + 1.6, 0], aligned_edge=LEFT)
        lp = T("inflation", 28, PRICE).move_to([-6.6, yb + 1.6, 0], aligned_edge=LEFT)
        up_m = VGroup(*[domino(np.array([x, yt, 0]), 0, MONEY) for x in xs])
        up_p = VGroup(*[domino(np.array([x, yb, 0]), 0, PRICE) for x in xs])
        floor = VGroup(Line([-5.5, yt, 0], [5.3, yt, 0], color=DIM), Line([-5.5, yb, 0], [5.3, yb, 0], color=DIM))
        hl = VGroup(*[MathTex(rf"h={h}" if h == 0 else rf"{h}", font_size=28, color=GREY_).move_to([x, yb - 0.75, 0]) for h, x in enumerate(xs)])
        var = MathTex(r"x_t=A\,x_{t-1}+\varepsilon_t", font_size=36).to_corner(UR, buff=0.45)
        with self.say("Start with a vector autoregression: money growth and inflation, each regressed on "
                      "last quarter's values of both. Stand them up as two rows of dominoes, one domino per "
                      "quarter.") as tr:
            self.play(FadeIn(lm), FadeIn(lp), Create(floor), Write(var))
            self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.3) for d in [*up_m, *up_p]], lag_ratio=0.05), FadeIn(hl))
            self.fill(tr, 4)

        fist = Arrow([-6.9, yt + 0.8, 0], [-5.15, yt + 0.8, 0], color=SHOCK, stroke_width=8, buff=0)
        fl = MathTex(r"v_t", font_size=36, color=SHOCK).next_to(fist, UP, buff=0.1)
        nums_m, nums_p = VGroup(), VGroup()
        for h, x in enumerate(xs):
            nums_m.add(MathTex(f"{resp[h, 0]:.2f}", font_size=26, color=MONEY).move_to([x + 0.35, yt - 0.3, 0]))
            nums_p.add(MathTex(f"{resp[h, 1]:.2f}", font_size=26, color=PRICE).move_to([x + 0.35, yb - 0.3, 0]))

        def tip(h, rt):
            dm = domino(np.array([xs[h], yt, 0]), k * resp[h, 0], MONEY)
            dp = domino(np.array([xs[h], yb, 0]), k * resp[h, 1], PRICE)
            self.play(Transform(up_m[h], dm), Transform(up_p[h], dp), FadeIn(nums_m[h]), FadeIn(nums_p[h]), run_time=rt)

        with self.say("A money shock tips the first domino. Because we let money move first, inflation "
                      "tips too, by a half, in the same quarter.") as tr:
            self.play(GrowArrow(fist), FadeIn(fl))
            tip(0, 0.8)
            self.fill(tr, 2)
        with self.say("That ordering is an assumption, not a fact found in the data.") as tr:
            self.play(Indicate(nums_p[0], color=YELLOW_))
            self.fill(tr, 1)
        b0m, b0p = np.array([xs[0], yt, 0]), np.array([xs[0], yb, 0])
        b1m, b1p = np.array([xs[1], yt, 0]), np.array([xs[1], yb, 0])
        pushes = VGroup(
            Arrow(top_of(b0m, k * resp[0, 0]), b1m + UP * 0.6, color=MONEY, buff=0.05, stroke_width=4),
            Arrow(top_of(b0p, k * resp[0, 1]), b1m + UP * 0.25 + LEFT * 0.05, color=PRICE, buff=0.05, stroke_width=4),
            Arrow(top_of(b0m, k * resp[0, 0]) + DOWN * 0.3, b1p + UP * 0.8, color=MONEY, buff=0.05, stroke_width=4),
            Arrow(top_of(b0p, k * resp[0, 1]), b1p + UP * 0.5, color=PRICE, buff=0.05, stroke_width=4),
        )
        with self.say("Then each domino pushes the next one in its own row, and the one diagonally across. "
                      "The ripple fades as it travels.") as tr:
            self.play(LaggedStart(*[GrowArrow(a) for a in pushes], lag_ratio=0.2), run_time=1.2)
            tip(1, 0.7)
            self.play(FadeOut(pushes), run_time=0.4)
            for h in range(2, H):
                tip(h, 0.45)
            self.fill(tr, 1.6 + 0.4 + 0.45 * (H - 2))

        sc = 1.25
        bars_m = VGroup(*[Rectangle(width=0.24, height=sc * resp[h, 0], stroke_width=0, fill_color=MONEY, fill_opacity=0.9)
                          .move_to([x, yt + sc * resp[h, 0] / 2, 0]) for h, x in enumerate(xs)])
        bars_p = VGroup(*[Rectangle(width=0.24, height=sc * resp[h, 1], stroke_width=0, fill_color=PRICE, fill_opacity=0.9)
                          .move_to([x, yb + sc * resp[h, 1] / 2, 0]) for h, x in enumerate(xs)])
        tm = VMobject(color=MONEY, stroke_width=5).set_points_smoothly([[x, yt + sc * resp[h, 0], 0] for h, x in enumerate(xs)])
        tp = VMobject(color=PRICE, stroke_width=5).set_points_smoothly([[x, yb + sc * resp[h, 1], 0] for h, x in enumerate(xs)])
        f1 = MathTex(r"\Psi_h", "=", r"A\,\Psi_{h-1}", font_size=40).to_edge(DOWN, buff=0.3)
        f2 = MathTex(r"\Psi_h", "=", r"A^h L", r"=\frac{\partial x_{t+h}}{\partial v_t'}", font_size=40).to_edge(DOWN, buff=0.2)
        with self.say("Stand each tilt up as a height, and the dominoes become the impulse responses. The "
                      "numbers show what the ripple is: each column is the previous one multiplied by the "
                      "matrix A.") as tr:
            self.play(*[ReplacementTransform(a, b) for a, b in zip([*up_m, *up_p], [*bars_m, *bars_p])], run_time=1.5)
            self.play(Create(tm), Create(tp), run_time=1.5)
            self.play(Write(f1))
            for h in (1, 2, 3):
                ar = CurvedArrow([xs[h - 1] + 0.45, 0.05, 0], [xs[h] + 0.25, 0.05, 0], angle=-PI / 2.5, color=YELLOW_)
                al = MathTex(r"\times A", font_size=28, color=YELLOW_).next_to(ar, UP, buff=0.05)
                self.play(Create(ar), FadeIn(al), Indicate(nums_m[h]), Indicate(nums_p[h]), run_time=0.8)
                self.play(FadeOut(ar), FadeOut(al), run_time=0.3)
            self.fill(tr, 7.3)
        eig = MathTex(r"\text{eigenvalues of }A:\ 0.7,\ 0.2", font_size=34, color=YELLOW_).next_to(var, DOWN, buff=0.25).align_to(var, RIGHT)
        with self.say("Multiply eight times and you have the whole response. Both eigenvalues of A, nought "
                      "point seven and nought point two, are below one, so the shock dies away.") as tr:
            self.play(TransformMatchingTex(f1, f2))
            self.play(FadeIn(eig))
            self.fill(tr, 2)
        self.freeze()

    def spurious(self):
        np.random.seed(2026)
        ts = []
        for _ in range(1000):
            x, y = np.cumsum(np.random.randn(100)), np.cumsum(np.random.randn(100))
            ts.append(ols_t(x, y)[0])
        ts = np.clip(np.array(ts), -29.9, 29.9)
        edges = np.arange(-30, 32, 2)
        ax = Axes(x_range=[-30, 30, 10], y_range=[0, 160, 40], x_length=12, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, x_axis_config={"include_numbers": True}).shift(DOWN * 0.6)
        band = Rectangle(width=ax.c2p(1.96, 0)[0] - ax.c2p(-1.96, 0)[0], height=4.4, stroke_width=0,
                         fill_color=SHOCK, fill_opacity=0.25).move_to(ax.c2p(0, 80))
        dl = VGroup(*[DashedLine(ax.c2p(v, 0), ax.c2p(v, 160), color=SHOCK) for v in (-1.96, 1.96)])
        bl = T("the textbook says: inside ±1.96, 95% of the time", 26, SHOCK).next_to(ax, UP, buff=0.15)
        xl = T("t statistic in the levels regression, T = 100", 24, GREY_).next_to(ax, DOWN, buff=0.15)
        n = ValueTracker(1)

        def hist():
            m = int(n.get_value())
            c, _ = np.histogram(ts[:m], edges)
            g = VGroup()
            for i, cc in enumerate(c):
                if cc:
                    p0, p1 = ax.c2p(edges[i], 0), ax.c2p(edges[i + 1], cc)
                    g.add(Rectangle(width=p1[0] - p0[0] - 0.03, height=p1[1] - p0[1], stroke_width=0,
                                    fill_color=MONEY, fill_opacity=0.8).move_to((p0 + p1) / 2))
            return g

        h = always_redraw(hist)
        cnt = DecimalNumber(1, num_decimal_places=0, font_size=32, color=WHITE_)
        rej = DecimalNumber(0, num_decimal_places=0, font_size=32, color=SHOCK, unit=r"\%")
        cnt.add_updater(lambda m: m.set_value(int(n.get_value())))
        rej.add_updater(lambda m: m.set_value(100 * np.mean(np.abs(ts[:int(n.get_value())]) > 1.96)))
        board = VGroup(VGroup(T("regressions:", 28), cnt).arrange(RIGHT, buff=0.2),
                       VGroup(T("\"significant\":", 28, SHOCK), rej).arrange(RIGHT, buff=0.2)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        board.move_to(ax.c2p(19, 120))
        with self.say("Back to the coin-flip pairs. Repeat the experiment a thousand times and collect the t "
                      "statistics. The textbook says they should sit inside the red band. They don't. The "
                      "test declares a relation that is not there nearly four times in five, and more data "
                      "only makes the illusion stronger.") as tr:
            self.play(Create(ax), FadeIn(band), Create(dl), FadeIn(bl), FadeIn(xl))
            self.add(h, board)
            self.play(n.animate.set_value(1000), run_time=9, rate_func=rate_functions.ease_in_quad)
            self.fill(tr, 11)
        fd = T("in differences: 5%", 28, LEASH).next_to(board, DOWN, buff=0.3).align_to(board, LEFT)
        with self.say("Take first differences and the problem disappears: the same test then rejects five "
                      "percent of the time, as it should.") as tr:
            self.play(FadeIn(fd, shift=UP * 0.2))
            self.fill(tr, 1)
        self.freeze()

    def leash(self):
        np.random.seed(2026)
        N = 200
        drunk = np.cumsum(np.random.randn(N))
        gap = np.zeros(N)
        e = np.random.randn(N) * 0.8
        for t in range(1, N):
            gap[t] = 0.7 * gap[t - 1] + e[t]
        dog = drunk + gap
        stranger = np.cumsum(np.random.randn(N))
        lo = min(drunk.min(), dog.min(), stranger.min()) - 1
        hi = max(drunk.max(), dog.max(), stranger.max()) + 1
        top = Axes(x_range=[0, N, 50], y_range=[lo, hi, 10], x_length=12.2, y_length=3.5, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}).move_to(UP * 1.3 + RIGHT * 0.3)
        bot = Axes(x_range=[0, N, 50], y_range=[-20, 20, 10], x_length=12.2, y_length=2.3, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [-10, 0, 10]}).move_to(DOWN * 2.35 + RIGHT * 0.3)
        k = ValueTracker(1)

        def part(ax, ys, col, w=4):
            return lambda: series_path(ax, ys[:max(2, int(k.get_value()) + 1)], col, w)

        pd, pg = always_redraw(part(top, drunk, MONEY)), always_redraw(part(top, dog, DOG))
        gl = always_redraw(part(bot, dog - drunk, LEASH))

        def leash_line():
            i = int(k.get_value())
            return Line(top.c2p(i, drunk[i]), top.c2p(i, dog[i]), color=LEASH, stroke_width=5)

        def heads():
            i = int(k.get_value())
            return VGroup(Dot(top.c2p(i, drunk[i]), radius=0.09, color=MONEY), Dot(top.c2p(i, dog[i]), radius=0.08, color=DOG))

        lab = VGroup(T("drunk  x", 26, MONEY), T("dog  y", 26, DOG), T("leash  y − x", 26, LEASH)).arrange(RIGHT, buff=0.6).to_edge(UP, buff=0.3)
        with self.say("Now a drunk walks home with her dog. Each of them wanders at random; neither path is "
                      "stationary. But the leash keeps the distance between them bounded. That is "
                      "cointegration: y minus beta x is stationary, although x and y are not.") as tr:
            self.play(Create(top), Create(bot), FadeIn(lab))
            self.add(pd, pg, gl, always_redraw(leash_line), always_redraw(heads))
            self.play(k.animate.set_value(N - 1), run_time=10, rate_func=linear)
            self.fill(tr, 11)
        ps = series_path(top, stranger, SHOCK, 3)
        sg = series_path(bot, stranger - drunk, SHOCK, 3)
        sl = T("stranger − x", 26, SHOCK).next_to(lab, RIGHT, buff=0.6)
        with self.say("Put a stranger beside her, walking independently. Their distance wanders off without "
                      "limit; any leash between them would snap. In economics the leashes are consumption "
                      "and income, long and short interest rates, prices at home and abroad. Engle and Granger's "
                      "test asks exactly this: is the residual of the levels regression stationary?") as tr:
            self.play(VGroup(lab, sl).animate.arrange(RIGHT, buff=0.45).to_edge(UP, buff=0.3), FadeIn(sl))
            self.play(Create(ps), Create(sg), run_time=4)
            self.fill(tr, 5)
        self.freeze()

    def closing(self):
        a = T("A shock travels like dominoes; a leash makes co-movement real.", 34, YELLOW_)
        f1 = MathTex(r"\mathrm{IRF}(h)=\Psi_h=A^hL", font_size=44, color=MONEY)
        f2 = MathTex(r"x_t,\ y_t\sim I(1),\qquad y_t-\beta x_t\sim I(0)", font_size=44, color=LEASH)
        g = VGroup(a, f1, f2).arrange(DOWN, buff=0.7)
        with self.say("So: in a VAR, a shock travels like a line of dominoes, and the impulse response is "
                      "the trace it leaves. Two random walks can look related and mean nothing; they are "
                      "cointegrated only when a leash holds them together.") as tr:
            self.play(FadeIn(a, shift=UP * 0.2))
            self.play(Write(f1))
            self.play(Write(f2))
            self.fill(tr, 4)
