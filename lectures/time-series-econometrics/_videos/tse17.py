"""Lecture 17 intuition film: realized volatility, RiskMetrics and VaR — a sea wall against the tide."""
from common import *

# ---------- real data: S&P 500 daily log returns (%) and VIX ----------
_D, _P = load_csv("SP500.csv")
R = 100 * np.diff(np.log(_P))
DATES = _D[1:]
N = len(R)
S2 = np.empty(N)                                   # RiskMetrics sigma^2_{t|t-1}
S2[0] = np.mean(R[:60] ** 2)
for _t in range(1, N):
    S2[_t] = 0.94 * S2[_t - 1] + 0.06 * R[_t - 1] ** 2
Z = R / np.sqrt(S2)
EV = np.arange(250, N)                             # evaluation days, as in the lecture
LOSS = -R[EV]
WALL_N = 2.326 * np.sqrt(S2[EV])                   # 99% VaR, normal quantile
WALL_F = np.array([-np.sqrt(S2[t]) * np.quantile(Z[:t], 0.01) for t in EV])   # filtered HS
HIT_N = LOSS > WALL_N
HIT_F = LOSS > WALL_F
NE = len(EV)

_dv, _vx = load_csv("VIXCLS.csv")
_vix = dict(zip(_dv, _vx))
_ok = [i for i in range(N - 21) if DATES[i] in _vix]
VIX = np.array([_vix[DATES[i]] for i in _ok])
RVF = np.array([np.sqrt(252 / 21 * np.sum(R[i + 1:i + 22] ** 2)) for i in _ok])


def year_x(dates, y):
    return next(i for i, d in enumerate(dates) if d >= f"{y}-01-01")


class Tse17(IntuitionScene):
    parts = ("hook", "realized", "footprints", "raise_wall", "vix", "closing")

    # ------------------------------------------------------------------ the sea picture
    def sea(self, wall, hits, h=4.6, y=-0.75):
        ax = Axes(x_range=[0, NE, 250], y_range=[0, 9, 3], x_length=12.4, y_length=h, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [3, 6, 9]}).shift(UP * y + RIGHT * 0.25)
        dts = [DATES[t] for t in EV]
        yrs = VGroup(*[T(str(y), 24, GREY_).next_to(ax.c2p(year_x(dts, y), 0), DOWN, buff=0.12)
                       for y in range(2018, 2027, 2)])
        yl = T("daily loss, %", 26, GREY_).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        waves = VGroup(*[Line(ax.c2p(i, 0), ax.c2p(i, min(l, 9)), stroke_width=1.3,
                              color=RED_ if h else BLUE_) for i, (l, h) in enumerate(zip(LOSS, hits)) if l > 0])
        top = [ax.c2p(i, min(w, 9)) for i, w in enumerate(wall)]
        poly = Polygon(*top, ax.c2p(NE - 1, 0), ax.c2p(0, 0), stroke_width=0, fill_color="#8A7F70", fill_opacity=0.22)
        edge = VMobject(color="#D8CBB5", stroke_width=2).set_points_as_corners(top)
        dots = VGroup(*[Dot(ax.c2p(i, min(l, 9)), color=RED_, radius=0.05) for i, (l, h) in enumerate(zip(LOSS, hits)) if h])
        return ax, yrs, yl, waves, VGroup(poly, edge), dots


    def hook(self):
        ax, yrs, yl, waves, wall, dots = self.sea(WALL_N, HIT_N)
        prom = T("“Our loss will overtop this wall on one day in a hundred.”", 32, YELLOW_).to_edge(UP, buff=0.3)
        cnt = ValueTracker(0)
        exp_ = ValueTracker(0)
        c1 = T("days over the wall:", 28, RED_)
        n1 = DecimalNumber(0, num_decimal_places=0, font_size=36, color=RED_)
        c2 = T("promised:", 28, GREY_)
        n2 = DecimalNumber(0, num_decimal_places=0, font_size=36, color=GREY_)
        row = VGroup(c1, n1, c2, n2).arrange(RIGHT, buff=0.2).next_to(prom, DOWN, buff=0.25)
        c2.shift(RIGHT * 0.6); n2.shift(RIGHT * 0.6)
        n1.add_updater(lambda m: m.set_value(cnt.get_value()))
        n2.add_updater(lambda m: m.set_value(exp_.get_value()))
        x0, x1 = ax.c2p(0, 0)[0] + 0.03, ax.c2p(NE, 0)[0] + 0.3
        yb, yt = ax.c2p(0, 0)[1] + 0.03, ax.c2p(0, 9)[1] + 0.1
        curtain = Rectangle(width=x1 - x0, height=yt - yb, stroke_width=0, fill_color=BG, fill_opacity=1)
        curtain.move_to([(x0 + x1) / 2, (yb + yt) / 2, 0])
        cum = np.cumsum(HIT_N)
        frac = ValueTracker(0)
        curtain.add_updater(lambda m: m.stretch_to_fit_width(max((x1 - x0) * (1 - frac.get_value()), 0.001))
                            .move_to([x1 - m.width / 2, (yb + yt) / 2, 0]))
        n1.clear_updaters(); n2.clear_updaters()
        n1.add_updater(lambda m: m.set_value(cum[min(int(frac.get_value() * (NE - 1)), NE - 1)]))
        n2.add_updater(lambda m: m.set_value(0.01 * frac.get_value() * NE))
        with self.say("Every evening a bank builds a wall: its ninety-nine percent value at risk, a loss it "
                      "expects to exceed on only one day in a hundred. Here is that wall for the S and P "
                      "five hundred, built the textbook way, and nine years of losses rolling in. The "
                      "promise was about twenty-three days over the wall. The sea delivered fifty-three.") as tr:
            self.play(FadeIn(prom))
            self.add(ax, yrs, yl, wall, waves, dots, curtain, row)
            self.play(Create(ax), FadeIn(yrs), FadeIn(yl), run_time=1)
            self.play(frac.animate.set_value(1), run_time=9, rate_func=linear)
            curtain.clear_updaters(); n1.clear_updaters(); n2.clear_updaters()
            self.play(Indicate(n1, color=RED_, scale_factor=1.5))
            self.fill(tr, 11.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        self.title_card("A sea wall against the tide", 17,
                        "To build the wall we need two things: how rough the sea is today, and how tall "
                        "its rare waves can be.")

    # ------------------------------------------------------------------ realized volatility
    def realized(self):
        np.random.seed(2026)
        m = 390
        s = np.arange(m + 1) / m

        def bridge(sd):
            b = np.concatenate([[0], np.cumsum(np.random.randn(m) * sd / np.sqrt(m))])
            return b - s * b[-1]
        calm, storm = 0.5 * s + bridge(0.4), 0.5 * s + bridge(2.0)
        cc, cs = np.concatenate([[0], np.cumsum(np.diff(calm) ** 2)]), np.concatenate([[0], np.cumsum(np.diff(storm) ** 2)])
        A = Axes(x_range=[0, 1, 0.25], y_range=[-3, 3, 1], x_length=11.4, y_length=2.7, tips=False,
                 axis_config={"color": GREY_, "font_size": 24},
                 y_axis_config={"numbers_to_include": [-2, 0, 2]}).move_to(UP * 1.45 + RIGHT * 0.3)
        B = Axes(x_range=[0, 1, 0.25], y_range=[0, 5, 1], x_length=11.4, y_length=2.4, tips=False,
                 axis_config={"color": GREY_, "font_size": 24},
                 y_axis_config={"numbers_to_include": [1, 2, 3, 4]}).move_to(DOWN * 2.15 + RIGHT * 0.3)
        al = T("log price since the open, %", 26, GREY_).next_to(A, UP, buff=0.08).align_to(A, LEFT)
        bl = T("running sum of squared one-minute moves", 26, GREY_).next_to(B, UP, buff=0.08).align_to(B, LEFT)
        u = ValueTracker(0.002)

        def part(ax, ys, c, w=2.5):
            k = max(int(u.get_value() * m), 1)
            return VMobject(color=c, stroke_width=w).set_points_as_corners([ax.c2p(s[i], ys[i]) for i in range(k + 1)])
        pc = always_redraw(lambda: part(A, calm, BLUE_))
        ps = always_redraw(lambda: part(A, storm, RED_))
        qc = always_redraw(lambda: part(B, cc, BLUE_, 4))
        qs = always_redraw(lambda: part(B, cs, RED_, 4))
        close = Dot(A.c2p(1, 0.5), color=YELLOW_, radius=0.08)
        cl = T("both close at +0.5%", 26, YELLOW_).next_to(close, UP, buff=0.12).shift(LEFT * 0.9)
        with self.say("First, how rough is the sea? A daily return sees only two prices, the open and the "
                      "close. Here are two days that both end up half a percent: a calm one, and a stormy "
                      "one. Their daily returns, and so their squared returns, are identical.") as tr:
            self.play(Create(A), FadeIn(al))
            self.add(pc, ps)
            self.play(u.animate.set_value(1), run_time=6, rate_func=linear)
            self.play(FadeIn(close, scale=2), FadeIn(cl))
            self.fill(tr, 8)
        u.set_value(0.002)
        r2 = DashedLine(B.c2p(0, 0.25), B.c2p(1, 0.25), color=YELLOW_)
        r2l = MathTex(r"r_t^2=0.25", font_size=32, color=YELLOW_).next_to(B.c2p(0.02, 0.25), UP, buff=0.08).align_to(B.c2p(0.02, 0), LEFT)
        vc = MathTex(f"RV={cc[-1]:.2f}", font_size=34, color=BLUE_).next_to(B.c2p(1, 0.25), UP, buff=0.15).shift(LEFT * 0.8)
        vs = MathTex(f"RV={cs[-1]:.2f}", font_size=34, color=RED_).next_to(B.c2p(1, min(cs[-1], 5)), LEFT, buff=0.1).shift(UP * 0.2)
        f = MathTex(r"RV_t=\sum_{i=1}^{m} r_{t,i}^2", font_size=40).move_to(B.c2p(0.3, 3.4))
        with self.say("Now sum the squares of the tiny one-minute moves as the day goes on. The calm day "
                      "collects almost nothing; the stormy one collects twenty-five times more. That sum "
                      "is realized volatility: a direct, model-free reading of the day's sea.") as tr:
            self.play(Create(B), FadeIn(bl), Create(r2), FadeIn(r2l), Write(f))
            self.add(qc, qs)
            self.play(u.animate.set_value(1), run_time=6, rate_func=linear)
            self.play(FadeIn(vc), FadeIn(vs))
            self.fill(tr, 9)

    # ------------------------------------------------------------------ RiskMetrics: fading footprints
    def footprints(self):
        eq = MathTex(r"\sigma_{t+1\mid t}^2", "=", r"0.06\,", r"r_t^2", "+", r"0.94\,", r"\sigma_{t\mid t-1}^2", font_size=46).to_edge(UP, buff=0.35)
        eq[3].set_color(YELLOW_); eq[6].set_color(TEAL_)
        sub = T("RiskMetrics: an IGARCH with α + β = 1, nothing estimated", 28, GREY_).next_to(eq, DOWN, buff=0.25)
        start = next(i for i, d in enumerate(DATES) if d >= "2018-01-22")
        j0 = start - 30
        u = ValueTracker(float(start))
        step, xr = 0.33, 2.6
        sand = Line([-6.7, -0.4, 0], [3.2, -0.4, 0], color=DIM, stroke_width=2)
        sl = T("older days", 26, GREY_).move_to([-5.6, -1.6, 0])
        sr = T("today", 26, YELLOW_).move_to([xr, -1.6, 0])

        def prints():
            g = VGroup()
            uu = u.get_value()
            for j in range(j0, int(np.floor(uu)) + 1):
                a = uu - j
                if a > 28:
                    continue
                h = 0.22 + 0.75 * min(abs(R[j]) / 3.5, 1)
                e = Ellipse(width=0.24, height=1.3 * h, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.94 ** a)
                e.move_to([xr - a * step, -0.4 + (0.35 if j % 2 else -0.35), 0])
                g.add(e)
            return g
        fp = always_redraw(prints)
        half = Brace(Line([xr - 11.2 * step, 0, 0], [xr, 0, 0]), UP, buff=0.75, color=TEAL_)
        hl = T("weight halves in 11 days", 26, TEAL_).next_to(half, UP, buff=0.1)
        # gauge
        gx, gy0, gh = 5.3, -2.6, 4.2
        gauge = Rectangle(width=0.5, height=gh, stroke_color=GREY_, stroke_width=2).move_to([gx, gy0 + gh / 2, 0])
        sig = lambda: np.sqrt(252 * S2[int(np.floor(u.get_value())) + 1])
        level = always_redraw(lambda: Rectangle(width=0.46, height=max(min(sig() / 50, 1) * gh, 0.01), stroke_width=0,
                                                fill_color=TEAL_, fill_opacity=0.8).move_to([gx, gy0, 0], aligned_edge=DOWN))
        gl = T("σ for tomorrow,", 24, TEAL_).next_to(gauge, UP, buff=0.35)
        gl2 = T("% a year", 24, TEAL_).next_to(gl, DOWN, buff=0.06)
        gn = DecimalNumber(sig(), num_decimal_places=0, font_size=36, color=TEAL_).next_to(gauge, DOWN, buff=0.15)
        gn.add_updater(lambda m: m.set_value(sig()))
        with self.say("Most days a bank has only closing prices. RiskMetrics then measures the sea from "
                      "footprints: each day's squared return is pressed into the sand, and every evening "
                      "all the older prints fade by six percent. The weight of a day halves in about "
                      "eleven days.") as tr:
            self.play(Write(eq), FadeIn(sub))
            self.play(Create(sand), FadeIn(fp), FadeIn(sl), FadeIn(sr))
            self.play(GrowFromCenter(half), FadeIn(hl))
            self.play(FadeIn(gauge), FadeIn(level), FadeIn(gl), FadeIn(gl2), FadeIn(gn))
            self.play(u.animate.set_value(start + 6), run_time=3.5, rate_func=linear)
            self.fill(tr, 7.5)
        with self.say("February twenty eighteen: a few deep prints, and tomorrow's volatility jumps at once. "
                      "Then the walk goes on, and the deep prints slowly fade. There is no constant, so "
                      "no level to return to: only memory.") as tr:
            self.play(u.animate.set_value(start + 22), run_time=9, rate_func=linear)
            self.fill(tr, 9)

    # ------------------------------------------------------------------ the tails: raise the wall
    def raise_wall(self):
        ax, yrs, yl, waves, wall, dots = self.sea(WALL_N, HIT_N, 3.7, -1.55)
        _, _, _, waves_f, wall_f, dots_f = self.sea(WALL_F, HIT_F, 3.7, -1.55)
        # the standardised-return tail, inset at the top
        H = Axes(x_range=[-6, -2, 1], y_range=[0, 0.06, 0.02], x_length=5.2, y_length=1.7, tips=False,
                 axis_config={"color": GREY_, "font_size": 24},
                 x_axis_config={"numbers_to_include": [-5, -4, -3, -2]}).move_to([-3.4, 2.55, 0])
        bw = 0.25
        edges = np.arange(-6, -2 + bw, bw)
        hist, _ = np.histogram(Z[60:], bins=edges)
        hist = hist / (len(Z[60:]) * bw)
        bars = VGroup(*[Rectangle(width=H.c2p(bw, 0)[0] - H.c2p(0, 0)[0], height=max(H.c2p(0, min(h, 0.06))[1] - H.c2p(0, 0)[1], 0.001),
                                  stroke_width=0.5, stroke_color=BG, fill_color=BLUE_, fill_opacity=0.7)
                        .move_to(H.c2p(e + bw / 2, 0), aligned_edge=DOWN) for h, e in zip(hist, edges[:-1])])
        nrm = H.plot(lambda x: np.exp(-x * x / 2) / np.sqrt(2 * np.pi), x_range=[-6, -2.06], color=YELLOW_)
        qn = DashedLine(H.c2p(-2.326, 0), H.c2p(-2.326, 0.058), color=YELLOW_)
        qe = DashedLine(H.c2p(-3.12, 0), H.c2p(-3.12, 0.058), color=RED_)
        tx = VGroup(T("left tail of r / σ", 26, BLUE_),
                    MathTex(r"\text{normal } 1\%:\ -2.33", font_size=32, color=YELLOW_),
                    MathTex(r"\text{data } 1\%:\ -3.12", font_size=32, color=RED_)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        tx.next_to(H, RIGHT, buff=0.6).shift(UP * 0.2)
        self.add(ax, yrs, yl, wall, waves, dots)
        with self.say("Is the wall too low because RiskMetrics misjudges the roughness? No. Divide each "
                      "return by its forecast sigma and look at the left tail. The normal curve says the "
                      "worst one percent starts at minus two point three three. The data say minus three "
                      "point one two.") as tr:
            self.play(Create(H), FadeIn(bars), Create(nrm))
            self.play(FadeIn(tx[0]), Create(qn), FadeIn(tx[1]))
            self.play(Create(qe), FadeIn(tx[2]))
            self.fill(tr, 4)
        cnt = VGroup(T("days over the wall:", 28, RED_), MathTex("53", font_size=40, color=RED_)).arrange(RIGHT, buff=0.2)
        cnt.next_to(tx, DOWN, buff=0.25).align_to(tx, LEFT)
        cnt2 = VGroup(T("days over the wall:", 28, GREEN_), MathTex("21", font_size=40, color=GREEN_)).arrange(RIGHT, buff=0.2).move_to(cnt)
        pr = T("promised: about 23", 26, GREY_).next_to(cnt, DOWN, buff=0.12).align_to(cnt, LEFT)
        with self.say("So keep the same volatility, but build the wall from the data's own tail: a third "
                      "higher. The overtopping days fall from fifty-three to twenty-one, and Kupiec's test "
                      "is satisfied. The sea was measured right; the wall assumed waves of the wrong "
                      "shape.") as tr:
            self.play(FadeIn(cnt), FadeIn(pr))
            self.play(Transform(wall, wall_f), Transform(waves, waves_f), Transform(dots, dots_f),
                      Transform(cnt, cnt2), run_time=3)
            self.fill(tr, 4)

    # ------------------------------------------------------------------ VIX
    def vix(self):
        n = len(VIX)
        ax = Axes(x_range=[0, n, 250], y_range=[0, 100, 25], x_length=12.4, y_length=4.8, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [25, 50, 75, 100]}).shift(DOWN * 0.7 + RIGHT * 0.25)
        dts = [DATES[i] for i in _ok]
        yrs = VGroup(*[T(str(y), 24, GREY_).next_to(ax.c2p(year_x(dts, y), 0), DOWN, buff=0.12) for y in range(2018, 2027, 2)])
        pv = series_path(ax, VIX, PURPLE_, 2.5)
        pr = series_path(ax, RVF, GREEN_, 2)
        key = VGroup(T("VIX: the sea the options market expects next month", 26, PURPLE_),
                     T("realized volatility over that month", 26, GREEN_)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        key.to_corner(UL, buff=0.35)
        note = T("VIX above realized on 84% of days", 30, YELLOW_).to_corner(UR, buff=0.4).shift(DOWN * 1.2)
        with self.say("The options market also forecasts the sea: the VIX. It moves with the volatility "
                      "that follows, but sits above it on eighty-four percent of days. Investors pay a "
                      "premium to be insured against storms.") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(key))
            self.play(Create(pr), Create(pv), run_time=5, rate_func=linear)
            self.play(FadeIn(note))
            self.fill(tr, 7)

    # ------------------------------------------------------------------ closing
    def closing(self):
        s = T("Measure the sea well, then build the wall from the real tail.", 34, YELLOW_).shift(UP * 1.9)
        f = MathTex(r"\Pr_{t-1}\{r_t\le \mathrm{VaR}_t\}=p,\qquad \widehat{\mathrm{VaR}}_t=\hat\sigma_t\,q_p\big(\hat f\big)",
                    font_size=46)
        g = MathTex(r"RV_t=\sum_i r_{t,i}^2,\qquad \sigma^2_{t+1\mid t}=0.06\,r_t^2+0.94\,\sigma^2_{t\mid t-1}",
                    font_size=38, color=GREY_).shift(DOWN * 1.5)
        with self.say("So: value at risk is a wall, and backtesting counts the days the sea came over it. "
                      "Measure the sea well, from intraday data or fading footprints, and then build the wall "
                      "from the tail the data actually have.") as tr:
            self.play(FadeIn(s))
            self.play(Write(f))
            self.play(FadeIn(g))
            self.fill(tr, 4)
        self.wait(1)
