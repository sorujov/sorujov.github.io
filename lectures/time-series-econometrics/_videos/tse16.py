"""Lecture 16 intuition film: structural breaks — hunting the break date, and why the hunt needs a higher bar."""
from common import *
from scipy.stats import chi2

# ---------- real data: US CPI inflation, annualised monthly %, 1960 onwards ----------
_D, _C = load_csv("CPIAUCSL.csv")
_y = 1200 * np.diff(np.log(_C))
_d = _D[1:]
_k = next(i for i, d in enumerate(_d) if d >= "1960-01-01")
Y, DATES = _y[_k:], _d[_k:]
N = len(Y)
LO, HI = int(np.ceil(0.15 * N)), int(np.floor(0.85 * N))
CS = np.concatenate([[0], np.cumsum(Y)])
CS2 = np.concatenate([[0], np.cumsum(Y ** 2)])


def wald(T1):
    """Wald statistic for a break in the mean after observation T1 (1-based count before the break)."""
    m1 = CS[T1] / T1
    m2 = (CS[N] - CS[T1]) / (N - T1)
    rss = (CS2[T1] - T1 * m1 ** 2) + (CS2[N] - CS2[T1] - (N - T1) * m2 ** 2)
    s2 = rss / (N - 2)
    return (m2 - m1) ** 2 / (s2 * (1 / T1 + 1 / (N - T1)))


WP = np.array([wald(t) for t in range(LO, HI + 1)])
KBEST = LO + int(np.argmax(WP))           # 1982-07
MOV = np.convolve(Y, np.ones(12) / 12, mode="same")


def idx(date):
    return next(i for i, d in enumerate(DATES) if d >= date)


# ---------- the null: sup of Q(r) for a Brownian bridge, trimmed at 15% ----------
np.random.seed(2026)
_M, _R = 5000, 1000
_r = np.arange(1, _M) / _M
_trim = (_r >= 0.15) & (_r <= 0.85)


def q_path():
    B = np.concatenate([[0], np.cumsum(np.random.randn(_M)) / np.sqrt(_M)])
    br = B[1:_M] - _r * B[_M]
    return br ** 2 / (_r * (1 - _r))


SHOW = [q_path() for _ in range(4)]
SUPS = np.array([q_path()[_trim].max() for _ in range(_R)])
CRIT = float(np.quantile(SUPS, 0.95))


class Tse16(IntuitionScene):
    parts = ("hook", "split", "hunt", "bar", "verdict", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        w = MathTex(r"W = 6.0", font_size=80, color=YELLOW_).to_edge(UP, buff=0.4)
        mk = lambda: Axes(x_range=[0, 14, 2], y_range=[0, 0.5, 0.25], x_length=5.6, y_length=3.0, tips=False,
                          axis_config={"color": GREY_, "font_size": 24},
                          x_axis_config={"numbers_to_include": [0, 4, 8, 12]})
        A1, A2 = mk().move_to(LEFT * 3.45 + DOWN * 0.9), mk().move_to(RIGHT * 3.45 + DOWN * 0.9)
        c1 = A1.plot(lambda x: chi2.pdf(x, 1), x_range=[0.65, 14], color=BLUE_)
        hist, edges = np.histogram(SUPS, bins=np.arange(0, 14.5, 0.7), density=True)
        c2 = VGroup(*[Rectangle(width=A2.c2p(0.7, 0)[0] - A2.c2p(0, 0)[0], height=max(A2.c2p(0, h)[1] - A2.c2p(0, 0)[1], 0.001),
                                stroke_width=1, stroke_color=BG, fill_color=PURPLE_, fill_opacity=0.8)
                      .move_to(A2.c2p(e + 0.35, 0), aligned_edge=DOWN) for h, e in zip(hist, edges[:-1])])
        h1 = T("date fixed in advance", 30, BLUE_).next_to(A1, UP, buff=0.3)
        h2 = T("date found by searching", 30, PURPLE_).next_to(A2, UP, buff=0.3)
        b1 = DashedLine(A1.c2p(3.84, 0), A1.c2p(3.84, 0.45), color=BLUE_)
        b2 = DashedLine(A2.c2p(8.68, 0), A2.c2p(8.68, 0.45), color=PURPLE_)
        bl1 = MathTex("3.84", font_size=32, color=BLUE_).next_to(b1, UP, buff=0.08)
        bl2 = MathTex("8.68", font_size=32, color=PURPLE_).next_to(b2, UP, buff=0.08)
        a1 = Arrow(A1.c2p(6, 0.32), A1.c2p(6, 0.02), buff=0, color=YELLOW_, stroke_width=5)
        a2 = Arrow(A2.c2p(6, 0.32), A2.c2p(6, 0.02), buff=0, color=YELLOW_, stroke_width=5)
        v1 = T("break!", 32, RED_).next_to(A1, DOWN, buff=0.35)
        v2 = T("no evidence", 32, GREEN_).next_to(A2, DOWN, buff=0.35)
        with self.say("Two economists compute the same statistic on the same data, and get six point zero. "
                      "One concludes that the series broke. The other finds no evidence of a break. Both "
                      "are right. The data are the same; what differs is how the date was chosen.") as tr:
            self.play(Write(w))
            self.play(FadeIn(A1), FadeIn(A2), FadeIn(h1), FadeIn(h2))
            self.play(Create(c1), FadeIn(c2, lag_ratio=0.05), run_time=1.5)
            self.play(Create(b1), Create(b2), FadeIn(bl1), FadeIn(bl2))
            self.play(TransformFromCopy(w, a1), TransformFromCopy(w, a2))
            self.play(FadeIn(v1), FadeIn(v2))
            self.fill(tr, 7.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        self.title_card("Hunting the break", 16,
                        "To see why, we go hunting for a break in sixty-five years of American inflation.")

    # ------------------------------------------------------------------ helpers
    def infl_axes(self, h=3.0, y=1.4):
        ax = Axes(x_range=[0, N, 120], y_range=[-6, 18, 6], x_length=12.2, y_length=h, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [0, 6, 12]}).move_to(UP * y + RIGHT * 0.3)
        yrs = VGroup(*[T(str(yr), 24, GREY_).next_to(ax.c2p(idx(f"{yr}-01-01"), -6), DOWN, buff=0.12)
                       for yr in range(1960, 2030, 10)])
        raw = series_path(ax, np.clip(Y, -6, 18), DIM, 1.2)
        smooth = series_path(ax, MOV, BLUE_, 3)
        return ax, yrs, raw, smooth

    # ------------------------------------------------------------------ one split
    def split(self):
        ax, yrs, raw, smooth = self.infl_axes(4.2, 0.9)
        yl = T("US CPI inflation, % a year", 28, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        with self.say("Here is US inflation since nineteen sixty, month by month, with a yearly average in "
                      "blue. Low in the sixties, high in the seventies, low again after the early eighties. "
                      "Did its mean change, and when?") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(yl))
            self.play(Create(raw), Create(smooth), run_time=4, rate_func=linear)
            self.fill(tr, 5)
        T1 = idx("1975-01-01")
        cur = DashedLine(ax.c2p(T1, -6), ax.c2p(T1, 18), color=YELLOW_)
        m1, m2 = CS[T1] / T1, (CS[N] - CS[T1]) / (N - T1)
        s1 = Line(ax.c2p(0, m1), ax.c2p(T1, m1), color=RED_, stroke_width=6)
        s2 = Line(ax.c2p(T1, m2), ax.c2p(N, m2), color=TEAL_, stroke_width=6)
        f = MathTex(r"W(T_1)=\frac{(", r"\bar y_2", "-", r"\bar y_1", r")^2}{\hat\sigma^2\left(\frac1{T_1}+\frac1{T-T_1}\right)}",
                    font_size=40).to_corner(UR, buff=0.4).shift(DOWN * 0.15)
        f[1].set_color(TEAL_); f[3].set_color(RED_)
        bg = BackgroundRectangle(f, color=BG, fill_opacity=0.9, buff=0.12)
        with self.say("Pick a candidate date, T one. Average the months before it and the months after it. "
                      "The Wald statistic is the gap between the two means, squared, measured against its "
                      "standard error. A large W says the two halves do not share one mean.") as tr:
            self.play(Create(cur))
            self.play(Create(s1), Create(s2))
            self.play(FadeIn(bg), Write(f))
            self.fill(tr, 4)

    # ------------------------------------------------------------------ the hunt
    def hunt(self):
        ax, yrs, raw, smooth = self.infl_axes(2.6, 2.05)
        wa = Axes(x_range=[0, N, 120], y_range=[0, 100, 25], x_length=12.2, y_length=2.7, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [25, 50, 75, 100]}).move_to(DOWN * 2.15 + RIGHT * 0.3)
        wl = MathTex(r"W(T_1)", font_size=36, color=YELLOW_).next_to(wa, UP, buff=0.05).align_to(wa, LEFT).shift(RIGHT * 0.3)
        zones = VGroup(*[Rectangle(width=ax.c2p(b, 0)[0] - ax.c2p(a, 0)[0], height=7.0, stroke_width=0,
                                   fill_color=GREY_, fill_opacity=0.18).move_to([(ax.c2p(a, 0)[0] + ax.c2p(b, 0)[0]) / 2, -0.05, 0])
                         for a, b in ((0, LO), (HI, N))])
        zl = VGroup(T("no-search", 24, GREY_), T("zone", 24, GREY_)).arrange(DOWN, buff=0.08).move_to(
            [(ax.c2p(HI, 0)[0] + ax.c2p(N, 0)[0]) / 2, -1.4, 0])
        k = ValueTracker(LO)

        def kk():
            return int(round(k.get_value()))

        cur = always_redraw(lambda: DashedLine(ax.c2p(kk(), -6), ax.c2p(kk(), 18), color=YELLOW_))
        seg = always_redraw(lambda: VGroup(
            Line(ax.c2p(0, CS[kk()] / kk()), ax.c2p(kk(), CS[kk()] / kk()), color=RED_, stroke_width=5),
            Line(ax.c2p(kk(), (CS[N] - CS[kk()]) / (N - kk())), ax.c2p(N, (CS[N] - CS[kk()]) / (N - kk())),
                 color=TEAL_, stroke_width=5)))
        wpath = always_redraw(lambda: series_path(wa, WP[:max(kk() - LO + 1, 2)], YELLOW_, 3, x0=LO))
        dot = always_redraw(lambda: Dot(wa.c2p(kk(), WP[kk() - LO]), color=YELLOW_, radius=0.06))
        with self.say("Now let the cursor hunt. At every admissible date we split, compute W, and draw it "
                      "below. We do not search the first and last fifteen percent: there, one mean would "
                      "rest on a handful of months, and noise alone would produce huge statistics.") as tr:
            self.add(ax, yrs, raw, smooth)
            self.play(FadeIn(zones), FadeIn(zl), Create(wa), FadeIn(wl))
            self.add(cur, seg, wpath, dot)
            self.play(k.animate.set_value(idx("1976-01-01")), run_time=8, rate_func=linear)
            self.fill(tr, 9)
        pk = Dot(wa.c2p(KBEST, WP[KBEST - LO]), color=RED_, radius=0.09)
        pl = T("July 1982:  W = 88", 30, RED_).next_to(pk, RIGHT, buff=0.2)
        with self.say("In the mid seventies W almost vanishes: that split leaves high inflation on both "
                      "sides. Then it climbs, and peaks in July nineteen eighty-two, at the end of the "
                      "Volcker disinflation, with W equal to eighty-eight.") as tr:
            self.play(k.animate.set_value(KBEST), run_time=4, rate_func=linear)
            self.play(FadeIn(pk, scale=3), FadeIn(pl))
            self.play(k.animate.set_value(HI), run_time=4, rate_func=linear)
            self.play(k.animate.set_value(KBEST), run_time=1.5)
            self.fill(tr, 10.5)

    # ------------------------------------------------------------------ why a higher bar
    def bar(self):
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 14, 4], x_length=6.0, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [0.25, 0.5, 0.75]},
                  y_axis_config={"numbers_to_include": [4, 8, 12]}).move_to(LEFT * 3.3 + DOWN * 0.5)
        hd = T("pure noise: no break at all", 30, GREY_).next_to(ax, UP, buff=0.3)
        xl = MathTex(r"r=T_1/T", font_size=32, color=GREY_).next_to(ax.x_axis, DOWN, buff=0.35)
        b384 = DashedLine(ax.c2p(0, 3.84), ax.c2p(1, 3.84), color=BLUE_)
        l384 = MathTex("3.84", font_size=30, color=BLUE_).next_to(b384, RIGHT, buff=0.1)
        cols = [TEAL_, PURPLE_, GREEN_, BLUE_]
        paths, dots = VGroup(), VGroup()
        for q, c in zip(SHOW, cols):
            pts = [ax.c2p(r, min(v, 14)) for r, v in zip(_r[::5], q[::5]) if 0.15 <= r <= 0.85]
            paths.add(VMobject(color=c, stroke_width=2.5).set_points_as_corners(pts))
            j = int(np.argmax(np.where(_trim, q, -1)))
            dots.add(Dot(ax.c2p(_r[j], min(q[j], 14)), color=YELLOW_, radius=0.08))
        with self.say("Why does the hunt need a higher bar? Take series with no break at all, and hunt "
                      "anyway. Each wandering line is W along one noise series. At any one date it crosses "
                      "three point eight four only one time in twenty. But we keep the highest point of "
                      "the whole search, and that lands above it about four times in ten.") as tr:
            self.play(Create(ax), FadeIn(hd), FadeIn(xl), Create(b384), FadeIn(l384))
            for p_, d_ in zip(paths, dots):
                self.play(Create(p_), run_time=1.6, rate_func=linear)
                self.play(FadeIn(d_, scale=2.5), run_time=0.4)
            self.fill(tr, 9)
        H = Axes(x_range=[0, 14, 2], y_range=[0, 0.4, 0.1], x_length=5.6, y_length=4.4, tips=False,
                 axis_config={"color": GREY_, "font_size": 24},
                 x_axis_config={"numbers_to_include": [0, 4, 8, 12]}).move_to(RIGHT * 3.6 + DOWN * 0.5)
        hh = T("the highest point, 1,000 hunts", 30, YELLOW_).next_to(H, UP, buff=0.3)
        bw = 0.5
        edges = np.arange(0, 14 + bw, bw)
        counts = np.zeros(len(edges) - 1)
        bars = VGroup(*[Rectangle(width=H.c2p(bw, 0)[0] - H.c2p(0, 0)[0], height=0.001, stroke_width=0,
                                  fill_color=YELLOW_, fill_opacity=0.75).move_to(H.c2p(e + bw / 2, 0), aligned_edge=DOWN)
                        for e in edges[:-1]])
        chi = H.plot(lambda x: chi2.pdf(x, 1), x_range=[0.9, 14], color=BLUE_, stroke_width=3)
        cl = MathTex(r"\chi^2_1", font_size=34, color=BLUE_).move_to(H.c2p(2.3, 0.33))
        unit = H.c2p(0, 1)[1] - H.c2p(0, 0)[1]
        with self.say("Repeat the hunt a thousand times and collect the highest points. Their histogram "
                      "sits far to the right of the chi squared curve that serves a single date. Its "
                      "ninety-five percent point is about eight point seven, not three point eight four.") as tr:
            self.play(Create(H), FadeIn(hh), FadeIn(bars), Create(chi), FadeIn(cl))
            used = 2
            for chunk in np.array_split(SUPS, 10):
                for s in chunk:
                    j = min(int(s // bw), len(counts) - 1)
                    counts[j] += 1
                anims = [b.animate.stretch_to_fit_height(max(c / (_R * bw) * unit, 0.001)).move_to(
                    H.c2p(edges[i] + bw / 2, 0), aligned_edge=DOWN) for i, (b, c) in enumerate(zip(bars, counts))]
                self.play(*anims, run_time=0.45)
                used += 0.45
            cr = DashedLine(H.c2p(8.68, 0), H.c2p(8.68, 0.36), color=RED_)
            crl = MathTex("8.68", font_size=34, color=RED_).next_to(cr, UP, buff=0.08)
            self.play(Create(cr), FadeIn(crl))
            self.fill(tr, used + 1)

    # ------------------------------------------------------------------ verdict on the real data
    def verdict(self):
        ax, yrs, raw, smooth = self.infl_axes(4.4, 0.6)
        yl = T("US CPI inflation, % a year", 28, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        b1, b2 = idx("1972-08-01"), idx("1982-07-01")
        segs = VGroup()
        for a, b, c in ((0, b1, TEAL_), (b1, b2, RED_), (b2, N, TEAL_)):
            m = Y[a:b].mean()
            segs.add(Line(ax.c2p(a, m), ax.c2p(b, m), color=c, stroke_width=7))
        labs = VGroup(*[MathTex(f"{Y[a:b].mean():.1f}\\%", font_size=34, color=s.get_color()).next_to(s, UP, buff=0.12)
                        for (a, b), s in zip(((0, b1), (b1, b2), (b2, N)), segs)])
        labs[1].shift(UP * 0.3)
        labs[1].move_to(ax.c2p((b1 + b2) / 2, 16)); labs[0].move_to(ax.c2p(b1 / 2, 10.5)); labs[2].move_to(ax.c2p((b2 + N) / 2, 10.5))
        cap = T("two breaks (Bai and Perron): August 1972 and July 1982", 30, GREY_).to_edge(DOWN, buff=0.6)
        v = MathTex(r"\sup W = 88 \gg 8.68", font_size=44, color=YELLOW_).to_corner(UR, buff=0.4)
        with self.say("Our real peak, eighty-eight, clears even the higher bar by a mile: inflation did "
                      "change regime. Allow two breaks, and the hunt finds August nineteen seventy-two and "
                      "July nineteen eighty-two, around a decade averaging eight and a half percent.") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(yl), FadeIn(raw), FadeIn(smooth))
            self.play(Write(v))
            self.play(LaggedStart(*[Create(s) for s in segs], lag_ratio=0.4), run_time=2.5)
            self.play(FadeIn(labs), FadeIn(cap))
            self.fill(tr, 6)

    # ------------------------------------------------------------------ closing
    def closing(self):
        s = T("A statistic you searched for must clear a higher bar.", 36, YELLOW_).shift(UP * 1.7)
        f = MathTex(r"\sup_{\pi T\le T_1\le(1-\pi)T} W(T_1)\ \xrightarrow{d}\ \sup_{\pi\le r\le 1-\pi}\frac{\|B(r)-rB(1)\|^2}{r(1-r)}",
                    font_size=46)
        g = T("k = 1, trimming 15%:  8.68, not 3.84", 30, GREY_).shift(DOWN * 1.6)
        with self.say("So: when the break date is found by searching, the evidence must be judged against "
                      "the best of all the looks we took. The maximum of many chi squared statistics "
                      "needs its own, higher, critical value.") as tr:
            self.play(FadeIn(s))
            self.play(Write(f), run_time=2)
            self.play(FadeIn(g))
            self.fill(tr, 4)
        self.wait(1)
