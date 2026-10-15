"""Lecture 2 intuition film: the CLT for dependent data and the long-run variance — echoes inflate uncertainty."""
from common import *

config.tex_dir = "{media_dir}/Tex_tse2"


def inflation():
    """Monthly US CPI inflation, annualised %, Jan 1985 onward (the one missing month interpolated)."""
    import csv
    rows = list(csv.reader(open(Path(__file__).parent / "data" / "CPIAUCSL.csv")))[1:]
    d = [r[0] for r in rows]
    v = np.array([np.nan if r[1] in (".", "") else float(r[1]) for r in rows])
    lp = np.log(v)
    g = np.where(np.isnan(lp))[0]
    lp[g] = (lp[g - 1] + lp[g + 1]) / 2
    i0 = d.index("1984-12-01")
    return 1200 * np.diff(lp[i0:])


def autocov(x):
    u = x - x.mean()
    n = len(u)
    return np.array([u[:n - j] @ u[j:] / n for j in range(n)])


def heat(v):
    """Colour for a standardised value: cold blue to hot red."""
    return interpolate_color(ManimColor(BLUE_), ManimColor(RED_), float(1 / (1 + np.exp(-1.6 * v))))


class Tse2(IntuitionScene):
    parts = ("hook", "beads", "grid", "tower", "naive", "triangle", "closing")

    def hook(self):
        x = inflation()
        ax = Axes(x_range=[0, len(x), 60], y_range=[-20, 16, 4], x_length=12, y_length=5.2, tips=False,
                  axis_config={"color": GREY_, "stroke_width": 2}).move_to(DOWN * 0.5)
        yl = VGroup(*[T(f"{v}%", 24, GREY_).next_to(ax.c2p(0, v), LEFT, buff=0.12) for v in (-16, -8, 0, 8)])
        yrs = VGroup(*[T(str(1985 + k), 24, GREY_).next_to(ax.c2p(12 * k, -20), DOWN, buff=0.12) for k in (0, 10, 20, 30, 40)])
        line = series_path(ax, x, BLUE_, 2.2)
        glow = series_path(ax, x, BLUE_, 7).set_stroke(opacity=0.18)
        mean = DashedLine(ax.c2p(0, x.mean()), ax.c2p(len(x), x.mean()), color=YELLOW_, stroke_width=4)
        ml = MathTex(r"\bar x = 2.78\%", font_size=40, color=YELLOW_).move_to(ax.c2p(len(x) - 40, 13.5))
        q = T("Five hundred months. How many independent facts?", 34).to_edge(UP, buff=0.35)
        with self.say("Five hundred and one months of American inflation, since nineteen eighty-five. They "
                      "average two point seven eight percent. But how many independent facts about that "
                      "average do five hundred months really contain?") as tr:
            self.play(Create(ax), FadeIn(yl), FadeIn(yrs))
            self.play(Create(line), FadeIn(glow), run_time=4)
            self.play(Create(mean), FadeIn(ml))
            self.play(FadeIn(q))
            self.fill(tr, 7)
        self.play(FadeOut(VGroup(ax, yl, yrs, line, glow, mean, ml, q)))
        self.title_card("Echoes inflate uncertainty", 2,
                        "The answer is fewer than you think, because every month echoes the months before it.")

    def beads(self):
        np.random.seed(2026)
        n, rho = 48, 0.8
        a = np.random.randn(n)
        e = np.random.randn(n)
        b = np.zeros(n)
        b[0] = e[0] / np.sqrt(1 - rho ** 2)
        for t in range(1, n):
            b[t] = rho * b[t - 1] + e[t]
        b = b / b.std()

        def row(vals, y):
            return VGroup(*[Dot(radius=0.11, color=heat(v)).move_to([-6.1 + 0.26 * i, y, 0]) for i, v in enumerate(vals)])

        top, bot = row(a, 1.6), row(b, -0.6)
        lt = T("independent months", 30, GREY_).next_to(top, UP, buff=0.3).align_to(top, LEFT)
        lb = T("months with memory,  ρ = 0.8", 30, GREY_).next_to(bot, UP, buff=0.3).align_to(bot, LEFT)
        with self.say("Here are forty-eight months, coloured from cold to hot. On top they are independent: "
                      "hot and cold arrive in no particular order. Below, the same number of months with "
                      "memory, rho equal to point eight. Now hot months come in runs, and so do cold ones.") as tr:
            self.play(FadeIn(lt), LaggedStart(*[GrowFromCenter(d) for d in top], lag_ratio=0.04), run_time=2.5)
            self.play(FadeIn(lb), LaggedStart(*[GrowFromCenter(d) for d in bot], lag_ratio=0.04), run_time=2.5)
            self.fill(tr, 5)
        # merge the remembered row into about five effective beads
        k = 5
        groups = [list(range(i * n // k, (i + 1) * n // k)) for i in range(k)]
        big = VGroup(*[Dot(radius=0.34, color=heat(b[g].mean() * 1.4)).move_to([-6.1 + 0.26 * np.mean(g), -0.6, 0]) for g in groups])
        f = MathTex(r"T_{\text{eff}} = T\,\frac{\Gamma_0}{V_x} = T\,\frac{1-\rho}{1+\rho} \approx 48 \times 0.11 \approx 5",
                    font_size=40, color=YELLOW_).move_to(DOWN * 2.6)
        with self.say("Each run is one surprise, echoed. The forty-eight months carry the information of "
                      "only about five independent ones. The ratio is gamma zero over the long-run variance, "
                      "V x.") as tr:
            self.play(*[ReplacementTransform(VGroup(*[bot[i] for i in g]), big[j]) for j, g in enumerate(groups)], run_time=2.5)
            self.play(Write(f), run_time=2)
            self.fill(tr, 4.5)

    def grid(self):
        N, rho, s = 10, 0.6, 0.38
        sq = {}
        G = VGroup()
        for i in range(N):
            for j in range(N):
                r = Square(side_length=s * 0.94, stroke_width=0, fill_color=YELLOW_ if i == j else BLUE_,
                           fill_opacity=rho ** abs(i - j) * 0.9 + 0.06).move_to([-4.6 + j * s, 1.75 - i * s, 0])
                sq[(i, j)] = r
                G.add(r)
        lab = MathTex(r"\operatorname{Var}\Big(\sum_{t=1}^{T} x_t\Big)=\sum_{s,t}\Gamma_{|s-t|}", font_size=36).next_to(G, DOWN, buff=0.4)
        ghost = G.copy().set_opacity(0.18)
        with self.say("Where does V x come from? The variance of a sum is the sum of every entry in the "
                      "covariance grid. The diagonal holds gamma zero, the next diagonals gamma one, and so "
                      "on outward.") as tr:
            self.play(LaggedStart(*[FadeIn(r) for r in G], lag_ratio=0.01), run_time=2)
            self.play(Write(lab))
            self.fill(tr, 3)
        # each diagonal slides out into a column: the triangle of weights appears
        x0, yb = 0.35, -1.9
        anims = []
        for d in range(-(N - 1), N):
            cells = [sq[(i, i + d)] for i in range(N) if 0 <= i + d < N]
            for k, c in enumerate(cells):
                anims.append(c.animate.move_to([x0 + (d + N - 1) * s * 0.92 + 0.0, yb + (k + 0.5) * s, 0]))
        tri = MathTex(r"\frac1T\operatorname{Var}\Big(\sum x_t\Big)=\sum_{|j|<T}\Big(1-\frac{|j|}{T}\Big)\Gamma_j\ \longrightarrow\ \sum_{j=-\infty}^{\infty}\Gamma_j = V_x",
                      font_size=36, color=YELLOW_).to_edge(UP, buff=0.4)
        with self.say("Slide each diagonal out into a column. Diagonal j has T minus j cells, so the columns "
                      "form a triangle. Divide by T and let T grow, and the triangle flattens: the variance "
                      "of the scaled sum tends to the sum of all autocovariances, the long-run variance.") as tr:
            self.play(FadeOut(lab))
            self.add(ghost)
            self.play(*anims, run_time=3)
            self.play(Write(tri), run_time=2)
            self.fill(tr, 6)

    def tower(self):
        unit, w = 0.62, 0.34
        base_y = -2.2
        rho = ValueTracker(0.6)
        J = 8
        axis = Line([-6.5, base_y, 0], [3.0, base_y, 0], color=GREY_)

        def bar(j, r):
            h = r ** abs(j) * unit
            col = YELLOW_ if j == 0 else (BLUE_ if h >= 0 else RED_)
            rect = Rectangle(width=w, height=max(abs(h), 0.003), stroke_width=0, fill_color=col, fill_opacity=0.9)
            return rect.move_to([-1.75 + j * 0.55, base_y + h / 2, 0])

        bars = always_redraw(lambda: VGroup(*[bar(j, rho.get_value()) for j in range(-J, J + 1)]))
        jl = VGroup(*[MathTex(str(j), font_size=26, color=GREY_).move_to([-1.75 + j * 0.55, base_y - 0.3, 0]) for j in (-8, -4, 0, 4, 8)])
        bl = MathTex(r"\Gamma_j/\Gamma_0", font_size=34, color=BLUE_).move_to([-5.6, base_y + 1.2, 0])
        tx = 5.0

        def tower(r):
            v = (1 + r) / (1 - r)
            return Rectangle(width=0.9, height=v * unit, stroke_width=0, fill_color=TEAL_, fill_opacity=0.9).move_to([tx, base_y + v * unit / 2, 0])

        tw = always_redraw(lambda: tower(rho.get_value()))
        g0 = always_redraw(lambda: DashedLine([tx - 0.8, base_y + unit, 0], [tx + 0.8, base_y + unit, 0], color=YELLOW_))
        g0l = MathTex(r"\Gamma_0", font_size=32, color=YELLOW_).move_to([tx - 1.15, base_y + unit, 0])
        vnum = DecimalNumber(1.6 / 0.4, num_decimal_places=1, font_size=36, color=TEAL_)
        tl = VGroup(MathTex(r"V_x =", font_size=36, color=TEAL_), vnum, MathTex(r"\Gamma_0", font_size=36, color=TEAL_)).arrange(RIGHT, buff=0.12)
        tl.add_updater(lambda m: (vnum.set_value((1 + rho.get_value()) / (1 - rho.get_value())),
                                  m.move_to([tx - 0.3, base_y + (1 + rho.get_value()) / (1 - rho.get_value()) * unit + 0.4, 0])))
        rnum = DecimalNumber(0.6, num_decimal_places=2, font_size=40, include_sign=False)
        rl = VGroup(MathTex(r"\rho =", font_size=40), rnum).arrange(RIGHT, buff=0.15).to_corner(UL, buff=0.6)
        rnum.add_updater(lambda m: m.set_value(rho.get_value()))
        tl.update()
        tbase = Line([tx - 0.8, base_y, 0], [tx + 0.8, base_y, 0], color=GREY_)
        with self.say("For a first-order autoregression the echoes are rho to the j. Stack every one of them "
                      "on top of gamma zero and the tower is V x: one plus rho, over one minus rho, times "
                      "gamma zero.") as tr:
            self.play(Create(axis), FadeIn(jl), FadeIn(bl), FadeIn(rl))
            self.add(bars)
            t0 = tower(0.6)
            self.play(Create(tbase), TransformFromCopy(bars.copy(), t0), run_time=2)
            self.remove(t0)
            self.add(tw, g0, g0l, tl)
            self.fill(tr, 3)
        with self.say("Raise rho and the tower soars. Make rho negative and the echoes alternate in sign and "
                      "cancel: the tower drops below gamma zero, and the mean is known better than with "
                      "independent data.") as tr:
            self.play(rho.animate.set_value(0.75), run_time=2.5)
            self.play(rho.animate.set_value(-0.6), run_time=4)
            self.play(rho.animate.set_value(0.6), run_time=2)
            self.fill(tr, 8.5)

    def naive(self):
        x = inflation()
        G = autocov(x)
        n = len(x)
        r = G / G[0]
        ax = Axes(x_range=[0, 60, 12], y_range=[-0.2, 1, 0.2], x_length=12, y_length=2.6, tips=False,
                  axis_config={"color": GREY_}).move_to(UP * 1.6)
        bars = VGroup(*[Rectangle(width=0.12, height=max(abs(r[j]) * ax.y_length / 1.2, 0.003), stroke_width=0,
                                  fill_color=YELLOW_ if j == 0 else BLUE_, fill_opacity=0.9)
                        .move_to(ax.c2p(j, r[j] / 2)) for j in range(61)])
        l1 = MathTex(r"\hat\Gamma_j/\hat\Gamma_0", font_size=34, color=BLUE_).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        l1b = T("inflation, lags in months", 26, GREY_).next_to(l1, RIGHT, buff=0.4)
        cs = np.cumsum(np.r_[G[0], 2 * G[1:]]) / G[0]
        ax2 = Axes(x_range=[0, n, 100], y_range=[-3, 7, 2], x_length=12, y_length=2.6, tips=False,
                   axis_config={"color": GREY_}).move_to(DOWN * 2.0)
        curve = series_path(ax2, cs, RED_, 4)
        l2 = MathTex(r"\sum_{|j|\le J}\hat\Gamma_j\ \big/\ \hat\Gamma_0", font_size=34, color=RED_).next_to(ax2, UP, buff=0.1).align_to(ax2, LEFT)
        zero = MathTex(r"=0\ \text{at}\ J=T-1", font_size=34, color=RED_).next_to(ax2.c2p(n, 0), UP, buff=0.3).shift(LEFT * 1.6)
        with self.say("In practice we estimate the echoes from the data. Near lags are well measured; far "
                      "lags rest on a handful of pairs and are mostly noise. Now add them all up, the naive "
                      "estimate. The running sum climbs, then slides all the way back to exactly zero. It "
                      "always does: the residuals sum to zero.") as tr:
            self.play(Create(ax), FadeIn(l1), FadeIn(l1b))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.03), run_time=2.5)
            self.play(Create(ax2), FadeIn(l2))
            self.play(Create(curve), run_time=5, rate_func=linear)
            self.play(FadeIn(zero))
            self.fill(tr, 11.5)

    def triangle(self):
        x = inflation()
        G = autocov(x)
        n = len(x)
        r = G / G[0]
        m = 12
        ax = Axes(x_range=[0, 24, 4], y_range=[-0.2, 1, 0.2], x_length=11, y_length=3.0, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).move_to(UP * 1.3)
        h = lambda v: max(abs(v) * ax.y_length / 1.2, 0.003)
        bars = VGroup(*[Rectangle(width=0.3, height=h(r[j]), stroke_width=0, fill_color=YELLOW_ if j == 0 else BLUE_,
                                  fill_opacity=0.9).move_to(ax.c2p(j, r[j] / 2)) for j in range(25)])
        tri = Polygon(ax.c2p(0, 1), ax.c2p(m + 1, 0), ax.c2p(0, 0), stroke_color=YELLOW_, stroke_width=4,
                      fill_color=YELLOW_, fill_opacity=0.08)
        wts = [max(1 - j / (m + 1), 0) for j in range(25)]
        shrunk = VGroup(*[Rectangle(width=0.3, height=h(r[j] * wts[j]), stroke_width=0, fill_color=YELLOW_ if j == 0 else BLUE_,
                                    fill_opacity=0.9).move_to(ax.c2p(j, r[j] * wts[j] / 2)) for j in range(25)])
        nw = MathTex(r"\hat V^{NW}=\sum_{j=-m}^{m}\Big(1-\frac{|j|}{m+1}\Big)\hat\Gamma_j", font_size=42, color=YELLOW_).move_to(DOWN * 1.0)
        with self.say("Newey and West tame the noise with a triangle. Weight lag j by one minus j over m "
                      "plus one: near echoes count almost fully, distant ones fade to nothing. It is the same "
                      "triangle as in the covariance grid, so the estimate can never be negative.") as tr:
            self.play(Create(ax), FadeIn(bars))
            self.play(Create(tri), run_time=1.5)
            self.play(Transform(bars, shrunk), run_time=2)
            self.play(Write(nw))
            self.fill(tr, 7)
        self.play(FadeOut(VGroup(ax, bars, tri)), nw.animate.scale(0.8).to_edge(UP, buff=0.4))
        se0, se5 = np.sqrt(G[0] / n), np.sqrt((G[0] + 2 * sum((1 - j / 6) * G[j] for j in range(1, 6))) / n)
        nl = NumberLine(x_range=[2.0, 3.6, 0.2], length=11, color=GREY_, include_numbers=True, font_size=26,
                        decimal_number_config={"num_decimal_places": 1}).move_to(DOWN * 1.2)
        mu = x.mean()

        def ci(se, y, col):
            a, b = nl.n2p(mu - 1.96 * se), nl.n2p(mu + 1.96 * se)
            return VGroup(Line(a, b, color=col, stroke_width=10), Dot(nl.n2p(mu), color=WHITE_)).shift(UP * y)

        c0, c5 = ci(se0, 2.3, BLUE_), ci(se5, 1.0, YELLOW_)
        t0 = T("ignoring the echoes: s.e. 0.14", 28, BLUE_).next_to(c0, UP, buff=0.15)
        t5 = T("Newey–West, m = 5: s.e. 0.20", 28, YELLOW_).next_to(c5, UP, buff=0.15)
        with self.say("Back to inflation. Ignoring the echoes, the standard error of the mean is point one "
                      "four. Counting them, it is about point two zero, and it keeps growing with m, because "
                      "inflation remembers for years. The interval must widen.") as tr:
            self.play(Create(nl))
            self.play(Create(c0), FadeIn(t0))
            self.play(TransformFromCopy(c0, c5), FadeIn(t5), run_time=1.5)
            self.fill(tr, 5)

    def closing(self):
        s = T("Correlated data carry fewer independent facts;", 34)
        s2 = T("the long-run variance counts the echoes.", 34, TEAL_).next_to(s, DOWN, buff=0.25)
        f = MathTex(r"\sqrt T\,(\bar x_T-\mu)\ \xrightarrow{\;d\;}\ N(0,V_x),\qquad V_x=\sum_{j=-\infty}^{\infty}\Gamma_j",
                    font_size=46, color=YELLOW_)
        g = VGroup(VGroup(s, s2), f).arrange(DOWN, buff=0.9)
        with self.say("So: correlated observations carry fewer independent facts. The central limit theorem "
                      "still holds, but its variance is the long-run variance, the sum of all the echoes.") as tr:
            self.play(FadeIn(s), FadeIn(s2))
            self.play(Write(f), run_time=2)
            self.fill(tr, 3.5)
        self.wait(1)
