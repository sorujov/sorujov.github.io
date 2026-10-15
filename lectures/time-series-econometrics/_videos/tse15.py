"""Lecture 15 intuition film: ARCH/GARCH — aftershocks, the leaky bucket, half-life of a shock."""
from common import *

# ---------- real data: S&P 500 daily log returns (%), Oct 2016 - Oct 2026 ----------
_D, _P = load_csv("SP500.csv")
R = 100 * np.diff(np.log(_P))
DATES = _D[1:]
N = len(R)
# Gaussian QMLE of GARCH(1,1) on these data (computed once, offline): mu, omega, alpha, beta
MU, OM, AL, BE = 0.0854, 0.03397, 0.16026, 0.81310


def garch_s2(r):
    e = r - MU
    s = np.empty_like(r)
    s[0] = e.var()
    for t in range(1, len(r)):
        s[t] = OM + AL * e[t - 1] ** 2 + BE * s[t - 1]
    return s


S2 = garch_s2(R)


def acf(x, L):
    x = x - x.mean()
    v = x @ x
    return np.array([x[k:] @ x[:-k] / v for k in range(1, L + 1)])


def year_idx(y):
    return next(i for i, d in enumerate(DATES) if d >= f"{y}-01-01")


def bar_path(ax, ys, color, width=1.4):
    """Vertical needles from 0 to ys[i] (seismograph look)."""
    g = VGroup(*[Line(ax.c2p(i, 0), ax.c2p(i, y), stroke_width=width, color=color) for i, y in enumerate(ys)])
    return g


class Tse15(IntuitionScene):
    parts = ("hook", "clusters", "bucket", "halflife", "real", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        np.random.seed(2026)
        shuffled = np.random.permutation(R)
        mk = lambda y: Axes(x_range=[0, N, 500], y_range=[-13, 10, 5], x_length=11.6, y_length=2.4,
                            tips=False, axis_config={"color": DIM, "stroke_width": 1}).move_to(UP * y + RIGHT * 0.45)
        a1, a2 = mk(1.45), mk(-1.85)
        p1 = series_path(a1, R, GREY_, 1.2)
        p2 = series_path(a2, shuffled, GREY_, 1.2)
        la, lb = T("A", 40).next_to(a1, LEFT, buff=0.3), T("B", 40).next_to(a2, LEFT, buff=0.3)
        q = T("The same 2,511 daily returns. Which order is the real one?", 32, YELLOW_).to_edge(UP, buff=0.35)
        with self.say("Here are two lines made of exactly the same numbers: two thousand five hundred and "
                      "eleven daily returns of the S and P five hundred. The same mean, the same spread, the "
                      "same histogram. Only one of them is in the order history produced. Which one?") as tr:
            self.play(FadeIn(q), FadeIn(la), FadeIn(lb))
            self.play(Create(p1), Create(p2), run_time=5, rate_func=linear)
            self.fill(tr, 6)
        i20 = year_idx(2020)
        box = SurroundingRectangle(VGroup(p1), color=RED_, buff=0.08)
        ra = T("real: storms come in clusters", 28, RED_).next_to(a1, DOWN, buff=0.2).align_to(a1, RIGHT)
        rb = T("shuffled: storms scattered at random", 28, BLUE_).next_to(a2, DOWN, buff=0.05).align_to(a2, RIGHT)
        with self.say("It is A. In the real market a violent day is followed by more violent days, as an "
                      "earthquake is followed by aftershocks. Shuffling keeps every number and destroys "
                      "exactly that.") as tr:
            self.play(p1.animate.set_color(RED_).set_stroke(width=1.6), Create(box))
            self.play(p2.animate.set_color(BLUE_), FadeIn(ra), FadeIn(rb))
            self.fill(tr, 2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.6)
        self.title_card("Aftershocks", 15,
                        "So the size of tomorrow's move is predictable, even when its sign is not. "
                        "This is the idea behind ARCH and GARCH.")

    # ------------------------------------------------------------------ returns vs squares
    def clusters(self):
        L = 20
        a_r, a_s = acf(R, L), acf((R - R.mean()) ** 2, L)
        mk = lambda: Axes(x_range=[0, L + 1, 5], y_range=[-0.1, 0.5, 0.1], x_length=5.6, y_length=3.6, tips=False,
                          axis_config={"color": GREY_, "font_size": 24},
                          x_axis_config={"numbers_to_include": [5, 10, 15, 20]},
                          y_axis_config={"numbers_to_include": [0, 0.2, 0.4]})
        A1, A2 = mk().move_to(LEFT * 3.4 + DOWN * 0.6), mk().move_to(RIGHT * 3.4 + DOWN * 0.6)
        for A in (A1, A2):      # tick labels below the negative bars
            A.x_axis.numbers.shift(DOWN * (A.c2p(0, 0)[1] - A.c2p(0, -0.1)[1]))
        b1 = VGroup(*[Line(A1.c2p(k + 1, 0), A1.c2p(k + 1, v), color=BLUE_, stroke_width=9) for k, v in enumerate(a_r)])
        b2 = VGroup(*[Line(A2.c2p(k + 1, 0), A2.c2p(k + 1, v), color=RED_, stroke_width=9) for k, v in enumerate(a_s)])
        t1 = MathTex(r"\operatorname{corr}(r_t,\ r_{t-j})", font_size=38, color=BLUE_).next_to(A1, UP, buff=0.35)
        t2 = MathTex(r"\operatorname{corr}(r_t^2,\ r_{t-j}^2)", font_size=38, color=RED_).next_to(A2, UP, buff=0.35)
        x1 = T("lag j (days)", 24, GREY_).next_to(A1, DOWN, buff=0.15)
        x2 = T("lag j (days)", 24, GREY_).next_to(A2, DOWN, buff=0.15)
        with self.say("Measure it. The correlation of today's return with the return j days ago is "
                      "essentially zero: the direction has no memory. The correlation of the squared "
                      "returns is positive, and it is still there a month later. Quiet follows quiet, "
                      "storm follows storm.") as tr:
            self.play(FadeIn(A1), FadeIn(t1), FadeIn(x1))
            self.play(LaggedStart(*[Create(b) for b in b1], lag_ratio=0.08), run_time=2.5)
            self.play(FadeIn(A2), FadeIn(t2), FadeIn(x2))
            self.play(LaggedStart(*[Create(b) for b in b2], lag_ratio=0.08), run_time=2.5)
            self.fill(tr, 7)

    # ------------------------------------------------------------------ the leaky bucket
    def bucket(self):
        eq = MathTex(r"\sigma_t^2", "=", r"\omega", "+", r"\alpha\,\varepsilon_{t-1}^2", "+", r"\beta\,\sigma_{t-1}^2",
                     font_size=48).to_edge(UP, buff=0.35)
        eq[2].set_color(TEAL_); eq[4].set_color(YELLOW_); eq[6].set_color(BLUE_)
        # bucket on the left
        cx, yb, W, H = -4.6, -3.3, 2.6, 4.6
        walls = VMobject(color=WHITE_, stroke_width=5).set_points_as_corners(
            [[cx - W / 2, yb + H, 0], [cx - W / 2, yb, 0], [cx + W / 2, yb, 0], [cx + W / 2, yb + H, 0]])
        vmax = 3.5
        lv = ValueTracker(1.0)
        water = always_redraw(lambda: Rectangle(width=W - 0.08, height=max(lv.get_value() / vmax * H, 0.02),
                                                stroke_width=0, fill_color=BLUE_, fill_opacity=0.55)
                              .move_to([cx, yb + max(lv.get_value() / vmax * H, 0.02) / 2, 0]))
        tap = VGroup(Line([cx - 0.9, yb + H + 0.5, 0], [cx - 0.3, yb + H + 0.5, 0], color=TEAL_, stroke_width=8),
                     Line([cx - 0.3, yb + H + 0.5, 0], [cx - 0.3, yb + H + 0.25, 0], color=TEAL_, stroke_width=8))
        tapl = MathTex(r"\omega", font_size=40, color=TEAL_).next_to(tap, LEFT, buff=0.15)
        hole = Dot([cx + W / 2 - 0.25, yb, 0], color=RED_, radius=0.07)
        leak = MathTex(r"\text{leaks }1-\beta", font_size=32, color=RED_).next_to(hole, DOWN, buff=0.12).shift(RIGHT * 0.2)
        lvl = always_redraw(lambda: MathTex(r"\sigma_t^2", font_size=36, color=BLUE_)
                            .next_to([cx + W / 2, yb + lv.get_value() / vmax * H, 0], RIGHT, buff=0.12))
        # history on the right
        ax = Axes(x_range=[0, 40, 10], y_range=[0, vmax, 1], x_length=7.4, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [10, 20, 30, 40]},
                  y_axis_config={"numbers_to_include": [1, 2, 3]}).move_to([2.9, yb + H / 2 + 0.05, 0])
        ax.shift(UP * (yb - ax.c2p(0, 0)[1]))
        xl = T("day", 24, GREY_).next_to(ax.x_axis, DOWN, buff=0.1).align_to(ax, RIGHT)
        # simulate 40 days of GARCH with the fitted parameters and one big shock on day 8
        np.random.seed(2026)
        eta = np.clip(np.random.randn(41), -1.4, 1.4)
        eta[8] = -3.4
        s2 = np.empty(41); e = np.empty(41)
        s2[0] = OM / (1 - AL - BE)
        for t in range(41):
            if t > 0:
                s2[t] = OM + AL * e[t - 1] ** 2 + BE * s2[t - 1]
            e[t] = np.sqrt(s2[t]) * eta[t]
        lv.set_value(s2[0])
        with self.say("Think of tomorrow's variance, sigma squared, as the water in a leaky bucket. A tap "
                      "drips a constant omega into it every day. Each night it leaks, keeping only a "
                      "fraction beta of what it held. And yesterday's shock is thrown in as a splash, "
                      "alpha times the squared surprise.") as tr:
            self.play(Write(eq))
            self.play(Create(walls), FadeIn(water), FadeIn(lvl))
            self.play(Indicate(eq[2], color=TEAL_), FadeIn(tap), FadeIn(tapl))
            self.play(Indicate(eq[6], color=BLUE_), FadeIn(hole), FadeIn(leak))
            self.play(Indicate(eq[4], color=YELLOW_))
            self.fill(tr, 5)
        trace = VMobject(color=BLUE_, stroke_width=4)
        trace.set_points_as_corners([ax.c2p(0, s2[0]), ax.c2p(0, s2[0])])
        splashes = VGroup()
        with self.say("Watch a calm spell. Then, on day eight, a bad day: the splash is large, the level "
                      "jumps, and the bucket takes weeks to drain back. Those are the aftershocks.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.add(trace)
            used = 1
            for t in range(1, 41):
                sp = AL * e[t - 1] ** 2
                drop = Dot([cx + 0.6, yb + H + 0.6, 0], color=YELLOW_, radius=0.05 + 0.12 * min(sp, 2.5))
                bar = Line(ax.c2p(t, 0), ax.c2p(t, min(sp, vmax)), color=YELLOW_, stroke_width=6)
                new = trace.copy().add_points_as_corners([ax.c2p(t, s2[t])])
                rt = 0.9 if t in (8, 9) else 0.32
                self.play(drop.animate.move_to([cx + 0.6, yb + s2[t - 1] / vmax * H, 0]),
                          lv.animate.set_value(s2[t]), Create(bar), Transform(trace, new),
                          run_time=rt, rate_func=linear)
                self.remove(drop)
                splashes.add(bar)
                used += rt
            self.fill(tr, used)
        sb = OM / (1 - AL - BE)
        dl = DashedLine(ax.c2p(0, sb), ax.c2p(40, sb), color=TEAL_)
        dlb = DashedLine([cx - W / 2, yb + sb / vmax * H, 0], [cx + W / 2, yb + sb / vmax * H, 0], color=TEAL_)
        s1 = MathTex(r"\bar\sigma^2", "=", r"\omega", "+", r"(\alpha+\beta)", r"\bar\sigma^2", font_size=46).move_to([2.9, 2.35, 0])
        s3 = MathTex(r"\bar\sigma^2", "=", r"{\omega", r"\over", r"1-(\alpha+\beta)}", font_size=46).move_to([2.9, 2.35, 0])
        for s in (s1, s3):
            s[0].set_color(TEAL_)
        with self.say("Where does the level settle? Where the water coming in, the drip plus the average "
                      "splash, equals what the bucket keeps. Solve, and the long run variance is omega "
                      "over one minus alpha plus beta. It exists only while alpha plus beta stays below "
                      "one.") as tr:
            self.play(Create(dl), Create(dlb))
            self.play(Write(s1))
            self.wait(1.5)
            self.play(TransformMatchingTex(s1, s3), run_time=1.8)
            self.play(Circumscribe(s3[4], color=YELLOW_))
            self.fill(tr, 6.5)

    # ------------------------------------------------------------------ half-life
    def halflife(self):
        ax = Axes(x_range=[0, 120, 20], y_range=[0, 1.05, 0.5], x_length=10.5, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [20, 40, 60, 80, 100, 120]},
                  y_axis_config={"numbers_to_include": [0.5, 1]}).shift(DOWN * 0.9 + RIGHT * 0.3)
        xl = T("days after the shock", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.15)
        yl = T("share of the shock left", 26, GREY_).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.15)
        f = MathTex(r"\sigma_{t+h\mid t}^2-\bar\sigma^2=(\alpha+\beta)^{h-1}\,\big(\sigma_{t+1}^2-\bar\sigma^2\big)",
                    font_size=40).to_edge(UP, buff=0.4)
        p = ValueTracker(0.80)
        curve = always_redraw(lambda: ax.plot(lambda h: p.get_value() ** h, x_range=[0, 120, 0.5], color=YELLOW_, stroke_width=4))
        hl = lambda: np.log(0.5) / np.log(p.get_value())
        vline = always_redraw(lambda: DashedLine(ax.c2p(hl(), 0), ax.c2p(hl(), 0.5), color=RED_))
        hline = DashedLine(ax.c2p(0, 0.5), ax.c2p(120, 0.5), color=DIM)
        l1 = MathTex(r"\alpha+\beta=", font_size=38, color=YELLOW_)
        n1 = DecimalNumber(0.8, num_decimal_places=3, font_size=38, color=YELLOW_)
        l2 = T("half-life =", 30, RED_)
        n2 = DecimalNumber(3, num_decimal_places=0, font_size=38, color=RED_)
        l3 = T("days", 30, RED_)
        lab = VGroup(l1, n1, l2, n2, l3).arrange(RIGHT, buff=0.18).move_to([1.4, 1.85, 0])
        l2.shift(RIGHT * 0.5); n2.shift(RIGHT * 0.5); l3.shift(RIGHT * 0.5)
        n1.add_updater(lambda m: m.set_value(p.get_value()))
        n2.add_updater(lambda m: m.set_value(hl()))
        l3.add_updater(lambda m: m.next_to(n2, RIGHT, buff=0.15))
        with self.say("How long do the aftershocks last? Forecast the variance further and further ahead: "
                      "its excess over the long run level shrinks by the factor alpha plus beta per day. At zero point eight, a "
                      "shock is half forgotten in three days.") as tr:
            self.play(FadeIn(f), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(hline))
            self.add(curve, vline, lab)
            self.fill(tr, 2)
        hl_ = T("S&P 500, fitted", 28, RED_).move_to([4.6, 1.1, 0])
        with self.say("For the S and P five hundred, alpha plus beta is about zero point nine seven. "
                      "Push it that close to one and the memory lengthens sharply: half of a shock is "
                      "still there after twenty-six trading days, about a month. Near one, it barely "
                      "fades at all.") as tr:
            self.play(p.animate.set_value(AL + BE), run_time=3)
            self.play(FadeIn(hl_))
            self.wait(1.5)
            self.play(FadeOut(hl_), p.animate.set_value(0.995), run_time=2.5)
            self.wait(1)
            self.play(p.animate.set_value(AL + BE), FadeIn(hl_), run_time=1.5)
            self.fill(tr, 9.5)

    # ------------------------------------------------------------------ real fit, zoom into March 2020
    def real(self):
        ax = Axes(x_range=[0, N, 250], y_range=[0, 125, 25], x_length=12.4, y_length=5.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [25, 50, 75, 100]}).shift(DOWN * 0.45 + RIGHT * 0.25)
        yrs = VGroup(*[T(str(y), 24, GREY_).next_to(ax.c2p(year_idx(y), 0), DOWN, buff=0.15)
                       for y in range(2018, 2027, 2)])
        yl = T("annualised volatility, %", 26, GREY_).next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
        data = bar_path(ax, np.minimum(np.sqrt(252) * np.abs(R - MU), 125), GREY_, 1.0).set_opacity(0.5)
        sig = series_path(ax, np.sqrt(252 * S2), RED_, 3)
        key = VGroup(T("grey: the day's absolute move", 26, GREY_), T("red: GARCH sigma", 26, RED_)
                     ).arrange(RIGHT, buff=0.6).to_edge(UP, buff=0.3)
        with self.say("Now fit the model to ten years of data. Grey needles are each day's absolute move; "
                      "the red line is the GARCH volatility, computed only from the past. It rises with "
                      "every storm and drains away after it.") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(yl), FadeIn(key))
            self.play(FadeIn(data, lag_ratio=0.002), run_time=3)
            self.play(Create(sig), run_time=4, rate_func=linear)
            self.fill(tr, 8)
        ip = int(np.argmax(S2))
        pk = Dot(ax.c2p(ip, np.sqrt(252 * S2[ip])), color=YELLOW_, radius=0.08)
        pl = T("17 March 2020: 120% a year", 30, YELLOW_).next_to(pk, RIGHT, buff=0.25).shift(DOWN * 0.15)
        lr = DashedLine(ax.c2p(0, 17.8), ax.c2p(N, 17.8), color=TEAL_, stroke_width=3)
        ll = T("long run: 18%", 28, TEAL_).move_to(ax.c2p(N * 0.66, 95))
        la = Arrow(ll.get_bottom(), ax.c2p(N * 0.66, 20), buff=0.1, color=TEAL_, stroke_width=3)
        with self.say("In March twenty twenty the bucket overflows: one hundred and twenty percent a year, "
                      "against a long run level of eighteen. Then it drains, exactly as the leak predicts.") as tr:
            self.play(FadeIn(pk, scale=3), FadeIn(pl))
            self.play(Create(lr), FadeIn(ll), GrowArrow(la))
            self.fill(tr, 2)

    # ------------------------------------------------------------------ closing
    def closing(self):
        s = T("Big moves predict big moves; the sign stays a coin toss.", 34, YELLOW_).shift(UP * 1.8)
        f = MathTex(r"\sigma_t^2", "=", r"\omega", "+", r"\alpha\,\varepsilon_{t-1}^2", "+", r"\beta\,\sigma_{t-1}^2",
                    font_size=54)
        f[2].set_color(TEAL_); f[4].set_color(YELLOW_); f[6].set_color(BLUE_)
        g = MathTex(r"\bar\sigma^2=\frac{\omega}{1-\alpha-\beta},\qquad h_{1/2}=\frac{\ln 0.5}{\ln(\alpha+\beta)}",
                    font_size=42, color=GREY_).shift(DOWN * 1.6)
        with self.say("So: big moves predict big moves, while the sign stays a coin toss. Variance is a "
                      "leaky bucket, filled by a drip and by yesterday's splash. Alpha plus beta tells us "
                      "how long the aftershocks ring.") as tr:
            self.play(FadeIn(s))
            self.play(Write(f))
            self.play(FadeIn(g))
            self.fill(tr, 4)
        self.wait(1)
