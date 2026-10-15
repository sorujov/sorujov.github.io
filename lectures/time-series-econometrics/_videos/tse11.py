"""Lecture 11 intuition film: threshold autoregression -- a ball in a valley with a domed floor
(the PPP band), a seismograph trail of the series, and the staircase sigma^2(gamma) whose lowest
step is gamma hat."""
from common import *

config.tex_dir = str(Path(__file__).parent / "media" / "videos" / "tse11" / "Tex")   # private: parallel renders share media/Tex

G_BAND, R_IN, R_OUT, S_BAND = 0.10, 1.06, 0.92, 0.03


def sim_band(n):
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = (R_IN if abs(x[t - 1]) <= G_BAND else R_OUT) * x[t - 1] + S_BAND * np.random.randn()
    return x


def dft(x):
    y = x[1:]
    X = np.column_stack([np.ones(len(y)), x[:-1]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ b
    s2 = r @ r / (len(y) - 2)
    return (b[1] - 1) / np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])


class Tse11(IntuitionScene):
    parts = ("hook", "valley", "staircase", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        np.random.seed(2026)
        self.xb = sim_band(420)
        x = self.xb[:160]
        ax = Axes(x_range=[0, 160, 40], y_range=[-0.25, 0.25, 0.1], x_length=11.5, y_length=4.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [-0.2, -0.1, 0, 0.1, 0.2]}).shift(DOWN * 0.5)
        yl = T("log deviation from parity", 26, GREY_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        xl = T("quarter", 26, GREY_).next_to(ax.x_axis, DOWN, buff=0.15).align_to(ax, RIGHT)
        path = series_path(ax, x, WHITE_, 3)
        verdict = MathTex(rf"\tau={dft(x):.2f}\ >\ -2.86", r"\ \Rightarrow\ \text{cannot reject a unit root}",
                          font_size=38, color=RED_).to_edge(UP, buff=0.4)
        with self.say("A real exchange rate, measured as its distance from purchasing power parity. Forty "
                      "years of quarterly data. The Dickey Fuller test cannot reject a unit root, and on "
                      "series like this one it fails four times in five.") as tr:
            self.play(Create(ax), FadeIn(yl), FadeIn(xl))
            self.play(Create(path), run_time=5, rate_func=linear)
            self.play(Write(verdict))
            self.fill(tr, 7.5)
        band = Rectangle(width=ax.x_length, height=ax.c2p(0, 0.1)[1] - ax.c2p(0, -0.1)[1], stroke_width=0,
                         fill_color=BLUE_, fill_opacity=0.15).move_to(ax.c2p(80, 0))
        walls = VGroup(*[DashedLine(ax.c2p(0, s * 0.1), ax.c2p(160, s * 0.1), color=BLUE_) for s in (1, -1)])
        q = T("Yet it never leaves a narrow corridor.", 34, YELLOW_).next_to(ax, DOWN, buff=0.55)
        with self.say("Yet the series never escapes a narrow corridor. A random walk would have "
                      "wandered off long ago. How can both be true?") as tr:
            self.play(FadeIn(band), Create(walls), FadeIn(q))
            self.fill(tr, 1.5)
        self.play(*[FadeOut(m) for m in (ax, yl, xl, path, verdict, band, walls, q)])
        self.title_card("Threshold autoregression", 11,
                        "The answer is a model whose rule changes with the state of the series: a "
                        "threshold autoregression.")

    # ------------------------------------------------------------------ the valley
    def valley(self):
        xs = self.xb
        sc = 4.0 / 0.25                       # display units per unit of x; x in [-0.25, 0.25]
        k1, k2, base = 25.0, 42.0, 1.35

        def V(x):
            a = abs(x)
            if a <= G_BAND:
                return base + 0.25 - k1 * x * x
            return base + 0.25 - k1 * G_BAND ** 2 + k2 * (x * x - G_BAND ** 2)

        def P(x):
            return np.array([sc * x, V(x), 0])

        floor = VGroup(
            VMobject(stroke_width=5, color=TEAL_).set_points_smoothly([P(x) for x in np.linspace(-0.25, -G_BAND, 40)]),
            VMobject(stroke_width=5, color=YELLOW_).set_points_smoothly([P(x) for x in np.linspace(-G_BAND, G_BAND, 40)]),
            VMobject(stroke_width=5, color=TEAL_).set_points_smoothly([P(x) for x in np.linspace(G_BAND, 0.25, 40)]))
        top, bot = 3.35, -3.25
        band = Rectangle(width=2 * sc * G_BAND, height=top - bot, stroke_width=0, fill_color=BLUE_,
                         fill_opacity=0.08).move_to([0, (top + bot) / 2, 0])
        edges = VGroup(*[DashedLine([s * sc * G_BAND, top, 0], [s * sc * G_BAND, bot, 0], color=BLUE_,
                                    stroke_width=2) for s in (-1, 1)])
        glab = VGroup(MathTex(r"-\gamma", font_size=34, color=BLUE_).move_to([-sc * G_BAND, -3.6, 0]),
                      MathTex(r"\gamma", font_size=34, color=BLUE_).move_to([sc * G_BAND, -3.6, 0]),
                      MathTex("0", font_size=30, color=GREY_).move_to([0, -3.6, 0]))
        n = ValueTracker(1)
        W, y0, dy = 150, 0.75, 4.0 / 150

        def ball():
            i = int(n.get_value())
            return Dot(P(xs[i]) + UP * 0.17, radius=0.17, color=WHITE_).set_sheen(-0.4, DR)

        def trail():
            i = int(n.get_value())
            g = VGroup()
            for s in range(max(1, i - W), i + 1):
                a = [sc * xs[s - 1], y0 - (i - s + 1) * dy, 0]
                b = [sc * xs[s], y0 - (i - s) * dy, 0]
                col = YELLOW_ if abs(xs[s - 1]) <= G_BAND else TEAL_
                g.add(Line(a, b, color=col, stroke_width=3))
            return g

        B, Tr = always_redraw(ball), always_redraw(trail)
        tlab = T("time", 26, GREY_).rotate(PI / 2).move_to([-4.85, -1.3, 0])
        tarr = Arrow([-4.4, 0.4, 0], [-4.4, -3.0, 0], color=GREY_, stroke_width=3, buff=0)
        with self.say("Picture a ball in a valley. Its position is the deviation from parity. Near parity "
                      "the floor is not a bowl: it is slightly domed. Transaction costs make arbitrage "
                      "unprofitable, nothing pulls the ball back, and it rolls away from the centre. "
                      "Beyond the band edges, plus and minus gamma, the walls rise: arbitrage pays, and "
                      "the ball is pushed back. Below, its path leaves a trail through time.") as tr:
            self.play(FadeIn(band), Create(edges), FadeIn(glab), Create(floor), run_time=2)
            self.add(Tr, B)
            self.play(FadeIn(tlab), GrowArrow(tarr))
            self.play(n.animate.set_value(170), run_time=14, rate_func=linear)
            self.fill(tr, 17)
        left = VGroup(MathTex(r"|x_{t-1}|\le\gamma", font_size=34, color=YELLOW_),
                      MathTex(r"\rho_1=1.06", font_size=40, color=YELLOW_),
                      T("drifts away", 26, YELLOW_)).arrange(DOWN, buff=0.22)
        right = VGroup(MathTex(r"|x_{t-1}|>\gamma", font_size=34, color=TEAL_),
                       MathTex(r"\rho_2=0.92", font_size=40, color=TEAL_),
                       T("pulled back", 26, TEAL_)).arrange(DOWN, buff=0.22)
        left.move_to([-5.5, 2.3, 0])
        right.move_to([5.5, 2.3, 0])
        model = MathTex(r"x_t=\rho_j\,x_{t-1}+\varepsilon_t", font_size=30).move_to([5.45, 0.4, 0])
        with self.say("In equations, the threshold variable is the size of the last deviation. Inside "
                      "the band, rho one is one point zero six: locally explosive. Outside, rho two is "
                      "zero point nine two: mean reverting. The trail is yellow on the floor and teal "
                      "on the walls.") as tr:
            self.play(FadeIn(left, shift=RIGHT * 0.2), FadeIn(right, shift=LEFT * 0.2), FadeIn(model))
            self.play(n.animate.set_value(330), run_time=10, rate_func=linear)
            self.fill(tr, 11)
        aha = VGroup(MathTex(r"\rho_1>1", font_size=40, color=YELLOW_),
                     T("and still", 26), T("stationary", 26)).arrange(DOWN, buff=0.2).move_to([5.5, -1.4, 0])
        with self.say("Here is the surprise. One regime is explosive, yet the process is globally "
                      "stationary. The switch is endogenous: the explosive regime pushes the series out "
                      "of itself, into the regime that pulls it back. And a unit root test, which fits one "
                      "line to both, sees only the persistence.") as tr:
            self.play(FadeIn(aha, shift=UP * 0.2))
            self.play(n.animate.set_value(419), run_time=8, rate_func=linear)
            self.fill(tr, 8.7)

    # ------------------------------------------------------------------ estimation staircase
    def staircase(self):
        np.random.seed(2026)
        Tn = 120
        x = np.zeros(Tn + 1)
        for t in range(1, Tn + 1):
            x[t] = (0.5 + 0.6 * x[t - 1] if x[t - 1] <= 0 else -0.4 + 0.5 * x[t - 1]) + 0.5 * np.random.randn()
        xl, y = x[:-1], x[1:]
        lo, hi = np.quantile(xl, 0.15), np.quantile(xl, 0.85)
        grid = np.sort(xl)
        grid = grid[(grid >= lo) & (grid <= hi)]

        def fit(gg):
            I = xl <= gg
            Z = np.column_stack([I, I * xl, ~I, (~I) * xl]).astype(float)
            b = np.linalg.lstsq(Z, y, rcond=None)[0]
            r = y - Z @ b
            return b, r @ r / Tn

        s2 = np.array([fit(gg)[1] for gg in grid])
        ih = int(np.argmin(s2))
        gh = grid[ih]
        X0 = -1.5
        A0, A1 = -1.6, 1.6
        keep = (abs(xl) <= A1) & (abs(y) <= 1.75)
        sax = Axes(x_range=[A0, A1, 1], y_range=[-2, 1.75, 1], x_length=8.2, y_length=3.0, tips=False,
                   axis_config={"color": GREY_, "font_size": 22}).move_to([X0, 1.85, 0])
        s2lo, s2hi = 0.22, 0.28
        tax = Axes(x_range=[A0, A1, 0.5], y_range=[s2lo, s2hi, 0.02], x_length=8.2, y_length=2.6, tips=False,
                   axis_config={"color": GREY_, "font_size": 22},
                   x_axis_config={"numbers_to_include": [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]}).move_to([X0, -2.0, 0])
        tax.y_axis.set_opacity(0)
        slx = MathTex(r"\text{points: }(x_{t-1},\,x_t)", font_size=30, color=GREY_)
        sly = VMobject()
        tly = MathTex(r"\hat\sigma^2(\gamma)", font_size=36).next_to(tax, RIGHT, buff=0.3).shift(UP * 0.6)
        trim = VGroup(*[Rectangle(width=abs(tax.c2p(b, 0)[0] - tax.c2p(a, 0)[0]), height=tax.y_length,
                                  stroke_width=0, fill_color=DIM, fill_opacity=0.6)
                        .move_to(tax.c2p((a + b) / 2, (s2lo + s2hi) / 2)) for a, b in ((A0, lo), (hi, A1))])
        trl = T("trimmed", 24, GREY_).move_to(tax.c2p((A0 + lo) / 2, s2hi - 0.006))
        g = ValueTracker(grid[0])

        def dots():
            gg = g.get_value()
            return VGroup(*[Dot(sax.c2p(a, b), radius=0.045, color=BLUE_ if a <= gg else PURPLE_)
                            for a, b in zip(xl[keep], y[keep])])

        def lines():
            gg = g.get_value()
            b, _ = fit(gg)
            return VGroup(Line(sax.c2p(A0, b[0] + A0 * b[1]), sax.c2p(gg, b[0] + gg * b[1]), color=BLUE_, stroke_width=4),
                          Line(sax.c2p(gg, b[2] + gg * b[3]), sax.c2p(A1, b[2] + A1 * b[3]), color=PURPLE_,
                               stroke_width=4))

        def cursor():
            gg = g.get_value()
            return DashedLine(sax.c2p(gg, 1.75), tax.c2p(gg, s2lo), color=WHITE_, stroke_width=2)

        def stairs():
            gg = g.get_value()
            k = int(np.searchsorted(grid, gg, side="right"))
            if k < 1:
                return VGroup()
            pts = []
            for i in range(k):
                right = grid[i + 1] if i + 1 < k else gg
                v = min(max(s2[i], s2lo), s2hi)
                pts += [tax.c2p(grid[i], v), tax.c2p(right, v)]
            return VMobject(color=WHITE_, stroke_width=3).set_points_as_corners(pts)

        D, L, C, S = (always_redraw(f) for f in (dots, lines, cursor, stairs))
        glab = always_redraw(lambda: MathTex(r"\gamma", font_size=34).next_to(sax.c2p(g.get_value(), 1.75), UP, buff=0.08))
        leg = VGroup(slx, MathTex(r"q_{t-1}=x_{t-1}\le\gamma", font_size=32, color=BLUE_),
                     MathTex(r"q_{t-1}=x_{t-1}>\gamma", font_size=32, color=PURPLE_)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        leg.next_to(sax, RIGHT, buff=0.3)
        with self.say("How do we find gamma from data? Fix a candidate gamma and the model is linear: "
                      "split the points at gamma and run least squares on each side. Record the residual "
                      "variance, then slide gamma along, keeping fifteen percent of the data in each "
                      "regime.") as tr:
            self.play(Create(sax), Create(tax), FadeIn(tly), FadeIn(trim), FadeIn(trl))
            self.add(D, L, C, S, glab)
            self.play(FadeIn(leg))
            self.play(g.animate.set_value(grid[len(grid) // 2]), run_time=6, rate_func=linear)
            self.fill(tr, 7.5)
        with self.say("Between two neighbouring observations nothing changes, so the objective is a "
                      "staircase: flat, then a jump each time the cursor crosses a data point. Gamma hat "
                      "is the lowest step.") as tr:
            self.play(g.animate.set_value(grid[-1]), run_time=6, rate_func=linear)
            self.fill(tr, 6)
        ball = Dot(tax.c2p(gh, s2hi - 0.004), radius=0.14, color=WHITE_)
        land = tax.c2p((gh + grid[ih + 1]) / 2, s2[ih]) + UP * 0.14
        low = Line(tax.c2p(gh, s2[ih]), tax.c2p(grid[ih + 1], s2[ih]), color=RED_, stroke_width=7)
        gl = MathTex(rf"\hat\gamma={gh:.2f},\ \ \gamma_0=0", font_size=34, color=RED_).next_to(tly, DOWN, aligned_edge=LEFT, buff=0.45)
        rate = MathTex(r"\hat\gamma-\gamma_0=O_p(T^{-1})", font_size=34, color=RED_).next_to(gl, DOWN, aligned_edge=LEFT, buff=0.35)
        with self.say("Drop a ball on the staircase and it settles there, close to the true value, zero. "
                      "Because the dip is a cliff, not a gentle slope, gamma hat converges at rate T, "
                      "faster than root T, and we may treat it as known when we study the slopes.") as tr:
            self.play(g.animate.set_value(gh), run_time=1.5)
            self.play(FadeIn(ball))
            self.play(ball.animate.move_to(land), rate_func=rate_functions.ease_out_bounce, run_time=1.5)
            self.play(Create(low), FadeIn(gl))
            self.play(Write(rate))
            self.fill(tr, 6)

    # ------------------------------------------------------------------ closing card
    def closing(self):
        s = VGroup(T("Let the rule depend on the state:", 36, YELLOW_),
                   T("drift inside the band, reversion outside it.", 36, YELLOW_)).arrange(DOWN, buff=0.25)
        f = MathTex(r"x_t=\begin{cases}\mu_1+\rho_1x_{t-1} & q_{t-1}\le\gamma\\ \mu_2+\rho_2x_{t-1} & "
                    r"q_{t-1}>\gamma\end{cases}+\varepsilon_t", font_size=46)
        g2 = MathTex(r"\hat\gamma=\arg\min_{\gamma}\hat\sigma^2(\gamma)", font_size=42, color=RED_)
        VGroup(s, f, g2).arrange(DOWN, buff=0.6)
        with self.say("So: a threshold autoregression lets the rule depend on the state. Persistence "
                      "inside the band and reversion outside it give a series that looks like a random "
                      "walk and is not one. And the threshold is found at the lowest step of the "
                      "staircase.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f), run_time=2)
            self.play(FadeIn(g2))
            self.fill(tr, 4)
