"""Lecture 3 intuition film: time-series regression and HAC standard errors — overlapping forecasts share mistakes."""
from common import *

config.tex_dir = "{media_dir}/Tex_tse3"


def mishkin():
    """Mishkin's regression on FRED data: 3-month inflation on the 3-month T-bill rate, 1960 onward."""
    import csv

    def rd(p):
        return {a: (np.nan if b in (".", "") else float(b)) for a, b in list(csv.reader(open(p)))[1:]}

    here = Path(__file__).parent
    c = rd(here / "data" / "CPIAUCSL.csv")
    t = rd(here.parent / "03-time-series-regression-hac" / "data" / "TB3MS.csv")
    ds = sorted(set(c) & set(t))
    lp = np.log([c[d] for d in ds])
    i = np.array([t[d] for d in ds])
    g = np.where(np.isnan(lp))[0]
    lp[g] = (lp[g - 1] + lp[g + 1]) / 2
    pi3 = 400 * (np.r_[lp[3:], [np.nan] * 3] - lp)
    k = np.array([d >= "1960-01-01" for d in ds]) & ~np.isnan(pi3)
    y, x = pi3[k], i[k]
    n = len(y)
    X = np.c_[np.ones(n), x]
    b = np.linalg.solve(X.T @ X, X.T @ y)
    e = y - X @ b
    Q = np.linalg.inv(X.T @ X)

    def se(m):
        gg = X * e[:, None]
        S = gg.T @ gg
        for j in range(1, m + 1):
            G = gg[j:].T @ gg[:-j]
            S += (1 - j / (m + 1)) * (G + G.T)
        return np.sqrt(np.diag(Q @ S @ Q))[1]

    u = e - e.mean()
    acf = np.array([u[:-j] @ u[j:] / (u @ u) for j in range(1, 13)])
    return dict(y=y, x=x, b=b[1], se_ols=np.sqrt(e @ e / (n - 2) * Q[1, 1]), se2=se(2), se12=se(12), acf=acf)


class Tse3(IntuitionScene):
    parts = ("hook", "question", "overlap", "nine", "reality", "closing")

    def hook(self):
        x0, dx = -6.0, 0.92
        months = VGroup(*[Line([x0 + k * dx, -1.8, 0], [x0 + k * dx, -1.6, 0], color=GREY_) for k in range(14)])
        axis = Line([x0, -1.7, 0], [x0 + 13 * dx, -1.7, 0], color=GREY_)
        mlab = T("months", 26, GREY_).next_to(axis, DOWN, buff=0.25).align_to(axis, RIGHT)
        tiles = VGroup()
        for m in range(10):
            r = RoundedRectangle(width=3 * dx - 0.08, height=0.42, corner_radius=0.08, stroke_color=BLUE_, stroke_width=2,
                                 fill_color=BLUE_, fill_opacity=0.25)
            r.move_to([x0 + (m + 2.5) * dx, -1.1 + 0.55 * (m % 3), 0])
            tiles.add(r)
        q = T("Each month, a forecast of inflation over the next three months.", 32).to_edge(UP, buff=0.5)
        with self.say("Every month a forecaster predicts inflation over the next three months. Each forecast "
                      "is a tile covering three months, and the tiles overlap like roof tiles.") as tr:
            self.play(Create(axis), FadeIn(months), FadeIn(mlab), FadeIn(q))
            self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in tiles], lag_ratio=0.25), run_time=3.5)
            self.fill(tr, 5)
        k = 6
        shock = Rectangle(width=dx, height=2.4, stroke_width=0, fill_color=RED_, fill_opacity=0.35).move_to([x0 + (k + 0.5) * dx, -0.4, 0])
        bolt = T("oil shock", 28, RED_).next_to(shock, UP, buff=0.15)
        hit = [m for m in range(10) if m + 1 <= k < m + 4]
        q2 = T("One surprise. How many wrong forecasts?", 34, YELLOW_).next_to(q, DOWN, buff=0.35)
        with self.say("Now one surprise lands in a single month: an oil shock. Every tile that covers that month "
                      "is wrong, and wrong in the same direction. One surprise, three mistakes.") as tr:
            self.play(FadeIn(shock), FadeIn(bolt))
            self.play(*[tiles[m].animate.set_fill(RED_, 0.7).set_stroke(RED_) for m in hit], run_time=1.2)
            self.play(Indicate(VGroup(*[tiles[m] for m in hit]), color=RED_, scale_factor=1.05))
            self.play(FadeIn(q2))
            self.fill(tr, 4)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("Overlapping forecasts share mistakes", 3,
                        "That shared mistake is what this lecture is about: regression with time-series errors, "
                        "and standard errors that remember.")

    def question(self):
        d = mishkin()
        y, x = d["y"], d["x"]
        ax = Axes(x_range=[0, len(y), 120], y_range=[-8, 20, 4], x_length=12, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "stroke_width": 2}).move_to(DOWN * 1.1)
        yrs = VGroup(*[T(str(1960 + 10 * k), 24, GREY_).next_to(ax.c2p(120 * k, -8), DOWN, buff=0.12) for k in range(7)])
        yl = VGroup(*[T(f"{v}%", 24, GREY_).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v in (0, 8, 16)])
        pl = series_path(ax, np.clip(y, -8, 20), BLUE_, 2)
        il = series_path(ax, x, YELLOW_, 3.5)
        glow = series_path(ax, x, YELLOW_, 9).set_stroke(opacity=0.2)
        lp = T("inflation over the next three months", 26, BLUE_).move_to(ax.c2p(560, 17.5))
        li = T("three-month T-bill rate", 26, YELLOW_).move_to(ax.c2p(560, 14.5))
        eq = MathTex(r"\pi_{t,3}", r"=", r"\alpha", r"+", r"\beta", r"\, i_{t,3}", r"+", r"e_{t+3}", font_size=46).to_edge(UP, buff=0.4)
        eq[0].set_color(BLUE_); eq[4].set_color(TEAL_); eq[5].set_color(YELLOW_); eq[7].set_color(RED_)
        with self.say("Mishkin asked whether the Treasury bill rate knows future inflation. Regress inflation "
                      "over the next three months on today's three-month rate. If the market forecasts well, "
                      "beta is one. Since nineteen sixty, ordinary least squares gives point five two.") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(yl))
            self.play(Create(pl), FadeIn(lp), run_time=3)
            self.play(Create(il), FadeIn(glow), FadeIn(li), run_time=3)
            self.play(Write(eq))
            bh = MathTex(rf"\hat\beta = {d['b']:.2f}", font_size=44, color=TEAL_).next_to(eq, DOWN, buff=0.25)
            self.play(FadeIn(bh))
            self.fill(tr, 9)
        q = T("But how precise is it? The errors overlap.", 32, RED_).move_to(bh)
        with self.say("But how precise is that number? Here the overlap returns.") as tr:
            self.play(ReplacementTransform(bh, q))
            self.fill(tr, 1)

    def overlap(self):
        n, s, gap = 10, 0.78, 0.98
        xs = [-5.0 + k * gap for k in range(n)]
        np.random.seed(2026)
        heat = np.random.rand(n)
        blocks = VGroup(*[Square(side_length=s, stroke_color=GREY_, stroke_width=2, fill_color=PURPLE_,
                                 fill_opacity=0.25 + 0.35 * heat[k]).move_to([xs[k], 1.5, 0]) for k in range(n)])
        labs = VGroup(*[MathTex(rf"\eta_{{t+{k + 1}}}", font_size=28).move_to(blocks[k]).set_z_index(3) for k in range(n)])
        ml = T("monthly surprises", 26, PURPLE_).next_to(blocks, UP, buff=0.95).align_to(blocks, LEFT)
        e3 = MathTex(r"e_{t+3}", r"=", r"\eta_{t+1}", r"+", r"\eta_{t+2}", r"+", r"\eta_{t+3}", font_size=40, color=YELLOW_).to_edge(UP, buff=0.35).shift(RIGHT * 2.2)
        A = SurroundingRectangle(VGroup(*blocks[0:3]), color=YELLOW_, buff=0.1, stroke_width=5)
        Al = MathTex(r"e_{t+3}", font_size=34, color=YELLOW_).next_to(A, UP, buff=0.12)
        with self.say("The forecast error over three months is the sum of three monthly surprises, eta. "
                      "Next month's error is the sum of the next three.") as tr:
            self.play(LaggedStart(*[FadeIn(VGroup(b, l)) for b, l in zip(blocks, labs)], lag_ratio=0.08), FadeIn(ml))
            self.play(Create(A), FadeIn(Al), Write(e3))
            self.fill(tr, 3.5)
        j = ValueTracker(1)
        B = always_redraw(lambda: SurroundingRectangle(VGroup(*blocks[int(j.get_value()):int(j.get_value()) + 3]),
                                                       color=TEAL_, buff=0.22, stroke_width=5))
        Bl = always_redraw(lambda: MathTex(rf"e_{{t+{3 + int(j.get_value())}}}", font_size=34, color=TEAL_).next_to(B, DOWN, buff=0.12))
        shared = always_redraw(lambda: VGroup(*[blocks[k].copy().set_fill(YELLOW_, 0.85) for k in range(int(j.get_value()), 3)]))
        base_y, unit, bx = -2.6, 0.55, 2.6
        axis = Line([bx - 0.6, base_y, 0], [bx + 4.0, base_y, 0], color=GREY_)
        gl = MathTex(r"\Gamma_j(e)", font_size=34).move_to([bx - 1.4, base_y + 0.8, 0])

        def bar(k):
            r = Rectangle(width=0.6, height=max((3 - k) * unit, 0.003), stroke_width=0,
                          fill_color=YELLOW_ if k == 0 else TEAL_, fill_opacity=0.9)
            r.move_to([bx + k * 1.0, base_y + (3 - k) * unit / 2, 0])
            lab = MathTex(rf"{3 - k}\sigma^2" if k < 2 else (r"\sigma^2" if k == 2 else "0"), font_size=30).next_to(r, UP, buff=0.1)
            jl = MathTex(rf"j={k}", font_size=26, color=GREY_).next_to([bx + k * 1.0, base_y, 0], DOWN, buff=0.15)
            return VGroup(r, lab, jl)

        bars = [bar(k) for k in range(4)]
        e4 = MathTex(r"e_{t+4}", r"=", r"\eta_{t+2}", r"+", r"\eta_{t+3}", r"+", r"\eta_{t+4}", font_size=40, color=TEAL_).next_to(e3, DOWN, buff=0.2).align_to(e3, LEFT)
        with self.say("The two errors share two surprises, so they are correlated. Count the shared months: "
                      "three with itself, two one month apart, one two months apart, none after that. That "
                      "count is the autocovariance. The errors are a moving average of order two.") as tr:
            self.play(Create(B), FadeIn(Bl), FadeIn(shared), Write(e4), Create(axis), FadeIn(gl))
            self.play(GrowFromEdge(bars[0], DOWN), FadeIn(bars[1]))
            self.wait(1)
            for k in (2, 3):
                self.play(j.animate.set_value(k), run_time=1.2)
                self.play(FadeIn(bars[k]))
                self.wait(0.6)
            self.fill(tr, 7.5)

    def nine(self):
        f1 = MathTex(r"V", r"=", r"\Gamma_0", r"+", r"2", r"(", r"\Gamma_1", r"+", r"\Gamma_2", r")", font_size=52)
        f2 = MathTex(r"V", r"=", r"3\sigma^2", r"+", r"2", r"(", r"2\sigma^2", r"+", r"\sigma^2", r")", font_size=52)
        f3 = MathTex(r"V", r"=", r"9\sigma^2", r"=", r"3\,\Gamma_0", font_size=52)
        for f in (f1, f2, f3):
            f.to_edge(UP, buff=0.6)
        unit, by = 0.36, -3.4
        segs = [(3, YELLOW_), (2, TEAL_), (2, TEAL_), (1, TEAL_), (1, TEAL_)]
        tower = VGroup()
        h = 0
        for v, c in segs:
            r = Rectangle(width=1.0, height=v * unit, stroke_color=BG, stroke_width=3, fill_color=c, fill_opacity=0.9)
            r.move_to([-3.5, by + h + v * unit / 2, 0])
            tower.add(r)
            h += v * unit
        ols = Rectangle(width=1.0, height=3 * unit, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.9).move_to([-5.5, by + 1.5 * unit, 0])
        lo = T("OLS assumes", 26, YELLOW_).next_to(ols, UP, buff=0.15)
        lt = T("truth", 26, TEAL_).next_to(tower, UP, buff=0.15)
        with self.say("Last lecture's tower tells us the variance that matters: gamma zero plus twice gamma "
                      "one plus twice gamma two. That is three plus four plus two, nine sigma squared, three "
                      "times what ordinary least squares assumes.") as tr:
            self.play(Write(f1))
            self.play(FadeIn(ols), FadeIn(lo))
            self.play(TransformMatchingTex(f1, f2), LaggedStart(*[GrowFromEdge(r, DOWN) for r in tower], lag_ratio=0.3), run_time=2.5)
            self.play(FadeIn(lt))
            self.play(TransformMatchingTex(f2, f3))
            self.fill(tr, 7)
        nl = NumberLine(x_range=[-1, 1, 0.5], length=6, color=GREY_).move_to([3.4, -0.6, 0])
        c1 = Line(nl.n2p(-0.3), nl.n2p(0.3), color=YELLOW_, stroke_width=12).shift(UP * 0.9)
        c2 = Line(nl.n2p(-0.3 * np.sqrt(3)), nl.n2p(0.3 * np.sqrt(3)), color=TEAL_, stroke_width=12).shift(DOWN * 0.0)
        c2.shift(UP * 0.0)
        l1 = T("OLS interval", 26, YELLOW_).next_to(c1, UP, buff=0.15)
        l2 = MathTex(r"\times\sqrt3 \approx 1.73", font_size=36, color=TEAL_).next_to(nl, DOWN, buff=0.35)
        c2.move_to(nl.n2p(0) + UP * 0.35)
        with self.say("Notice that every surprise has the same variance: nothing here is heteroskedastic. "
                      "The correction comes from the overlap alone. So the honest standard error is root "
                      "three, about one point seven three, times larger, and the interval must stretch to "
                      "match.") as tr:
            self.play(Create(nl), Create(c1), FadeIn(l1))
            self.play(TransformFromCopy(c1, c2), FadeIn(l2), run_time=1.5)
            self.fill(tr, 3)

    def reality(self):
        d = mishkin()
        ax = Axes(x_range=[0, 12, 1], y_range=[0, 1, 0.25], x_length=5.6, y_length=3.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [1, 3, 6, 9, 12]},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).move_to([-3.6, -0.6, 0])
        bars = VGroup(*[Rectangle(width=0.28, height=d["acf"][j - 1] * ax.y_length, stroke_width=0, fill_color=BLUE_,
                                  fill_opacity=0.85).move_to(ax.c2p(j, d["acf"][j - 1] / 2)) for j in range(1, 13)])
        th = VGroup(*[Dot(ax.c2p(j, max(1 - j / 3, 0)), radius=0.09, color=RED_) for j in range(1, 13)])
        t1 = T("residual autocorrelation", 26, BLUE_).next_to(ax, UP, buff=0.5).align_to(ax, LEFT)
        t2 = T("overlap alone (MA(2))", 26, RED_).next_to(t1, DOWN, buff=0.1).align_to(t1, LEFT)
        nl = NumberLine(x_range=[0, 1.2, 0.2], length=5.6, color=GREY_, include_numbers=True, font_size=24,
                        decimal_number_config={"num_decimal_places": 1}).move_to([3.6, -2.0, 0])
        one = DashedLine(nl.n2p(1) + DOWN * 0.1, nl.n2p(1) + UP * 3.4, color=RED_)
        onel = MathTex(r"\beta=1", font_size=32, color=RED_).next_to(one, UP, buff=0.1)
        rows = [("OLS", d["se_ols"], YELLOW_), ("NW, m = 2", d["se2"], TEAL_), ("NW, m = 12", d["se12"], GREEN_)]
        cis = VGroup()
        for k, (name, se, col) in enumerate(rows):
            y = 0.9 - 1.0 * k
            ln = Line(nl.n2p(d["b"] - 1.96 * se), nl.n2p(d["b"] + 1.96 * se), color=col, stroke_width=10).set_y(y)
            dot = Dot(nl.n2p(d["b"]), color=WHITE_).set_y(y)
            lab = T(f"{name}: s.e. {se:.3f}", 24, col).next_to(ln, UP, buff=0.2)
            cis.add(VGroup(ln, dot, lab))
        with self.say("On the real data the residuals echo for longer than the overlap alone predicts: "
                      "the blue bars stay high long after the red MA two pattern has died.") as tr:
            self.play(Create(ax), FadeIn(t1), FadeIn(t2))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), FadeIn(th), run_time=2.5)
            self.fill(tr, 3.5)
        with self.say("So the standard error grows: point zero three for least squares, twice that with "
                      "Newey and West at two lags, three and a half times with twelve. Even so, one stays "
                      "outside: the bill rate knows something about inflation, but it is not an unbiased "
                      "forecast.") as tr:
            self.play(Create(nl), Create(one), FadeIn(onel))
            for c in cis:
                self.play(FadeIn(c), run_time=1)
                self.wait(1.2)
            self.fill(tr, 7)

    def closing(self):
        s = T("Overlapping forecasts share mistakes:", 34)
        s2 = T("the errors echo, and the standard errors must count the echoes.", 32, TEAL_)
        f = MathTex(r"\hat V_{OLS}=\Big(\tfrac{X'X}{T}\Big)^{-1}\,\hat V_{HAC}\,\Big(\tfrac{X'X}{T}\Big)^{-1}",
                    font_size=50, color=YELLOW_)
        g = VGroup(s, s2, f).arrange(DOWN, buff=0.35)
        f.shift(DOWN * 0.6)
        with self.say("So: when forecast windows overlap, the mistakes are shared. The errors echo, and the "
                      "standard errors must count those echoes, with the HAC sandwich.") as tr:
            self.play(FadeIn(s), FadeIn(s2))
            self.play(Write(f), run_time=2)
            self.fill(tr, 3.5)
        self.wait(1)
