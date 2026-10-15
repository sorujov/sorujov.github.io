"""Lecture 1 intuition film: stationarity and ergodicity — one life versus many worlds."""
from common import *
from scipy.stats import norm

config.tex_dir = "{media_dir}/Tex_tse1"

RHO = 0.7
SD = 1 / np.sqrt(1 - RHO ** 2)          # stationary sd of the AR(1)
EDGES = np.arange(-4.5, 4.51, 0.5)      # histogram bins on the value axis


def ar1_worlds(n, T, rho=RHO, sig=1.0, start_sd=None):
    np.random.seed(2026)
    x = np.zeros((n, T))
    x[:, 0] = np.random.randn(n) * (sig / np.sqrt(1 - rho ** 2) if start_sd is None else start_sd)
    e = np.random.randn(n, T) * sig
    for t in range(1, T):
        x[:, t] = rho * x[:, t - 1] + e[:, t]
    return x


def world_axes(width=8.6, height=5.4, xmax=100):
    return Axes(x_range=[0, xmax, xmax / 5], y_range=[-4.5, 4.5, 1.5], x_length=width, y_length=height, tips=False,
                axis_config={"color": GREY_, "stroke_width": 2}).to_edge(LEFT, buff=0.5).shift(DOWN * 0.35)


def side_hist(ax, vals, x0, scale, color, opacity=0.75):
    """Sideways histogram sharing the y axis of ax: bars grow to the right from x = x0."""
    vals = np.asarray(vals)
    dens, _ = np.histogram(vals, bins=EDGES)
    dens = dens / max(len(vals), 1) / 0.5
    g = VGroup()
    h = ax.c2p(0, 0.5)[1] - ax.c2p(0, 0)[1]
    for d, a in zip(dens, EDGES[:-1]):
        w = max(d * scale, 0.001)
        r = Rectangle(width=w, height=h * 0.92, stroke_width=0, fill_color=color, fill_opacity=opacity)
        r.move_to([x0 + w / 2, ax.c2p(0, a + 0.25)[1], 0])
        g.add(r)
    return g


def side_density(ax, x0, scale, sd, color=YELLOW_):
    return ParametricFunction(lambda y: np.array([x0 + norm.pdf(y, 0, sd) * scale, ax.c2p(0, y)[1], 0]),
                              t_range=[-4.4, 4.4, 0.05], color=color, stroke_width=4)


class Tse1(IntuitionScene):
    parts = ("hook", "column", "window", "one_life", "coin", "closing")

    def hook(self):
        ax = world_axes(width=12.4, height=6.2).move_to(DOWN * 0.3)
        X = ar1_worlds(30, 101)
        greys = VGroup(*[series_path(ax, X[i], GREY_, 1.6).set_stroke(opacity=0.55) for i in range(1, 30)])
        red = series_path(ax, X[0], RED_, 4.5)
        q = T("Thirty possible histories. We are allowed to watch one.", 32).to_edge(UP, buff=0.35)
        with self.say("Imagine thirty parallel worlds, each living through the same hundred years of an "
                      "economy. They share the rules, but not the luck. We are allowed to watch exactly one "
                      "of them, the red one, and from it alone we must learn about all the others.") as tr:
            self.play(LaggedStart(*[Create(g) for g in greys], lag_ratio=0.08), run_time=4)
            self.play(Create(red), run_time=3)
            self.play(greys.animate.set_stroke(opacity=0.15), FadeIn(q))
            self.fill(tr, 8)
        self.play(FadeOut(VGroup(greys, red, q)))
        self.title_card("One life, many worlds", 1,
                        "When can one life stand in for many worlds? That is the question of stationarity "
                        "and ergodicity.")

    def column(self):
        ax = world_axes()
        X = ar1_worlds(400, 101)
        greys = VGroup(*[series_path(ax, X[i], GREY_, 1.4).set_stroke(opacity=0.3) for i in range(1, 30)])
        red = series_path(ax, X[0], RED_, 4)
        x0 = ax.get_right()[0] + 0.35
        base = Line([x0, ax.get_bottom()[1], 0], [x0, ax.get_top()[1], 0], color=GREY_, stroke_width=2)
        self.add(greys, red)
        t = ValueTracker(40)
        vline = always_redraw(lambda: DashedLine(ax.c2p(t.get_value(), -4.5), ax.c2p(t.get_value(), 4.5),
                                                 color=BLUE_, stroke_width=3))
        dots = always_redraw(lambda: VGroup(*[Dot(ax.c2p(t.get_value(), X[i, int(round(t.get_value()))]),
                                                  radius=0.05, color=BLUE_) for i in range(30)]))
        hist = always_redraw(lambda: side_hist(ax, X[:, int(round(t.get_value()))], x0, 9.0, BLUE_))
        lab = MathTex(r"E(x_t)", font_size=40, color=BLUE_).next_to(base, UP, buff=0.15).shift(RIGHT * 1.2)
        with self.say("Freeze the clock at one date and look down the column. Across the many worlds, the "
                      "value at that date has a distribution, and its centre is the expectation, E of x t. "
                      "It is an average across worlds, not across time.") as tr:
            self.play(Create(vline), FadeIn(dots), Create(base))
            self.play(FadeIn(hist), Write(lab))
            self.fill(tr, 3)
        self.play(FadeOut(VGroup(lab)))
        top = T("same law at every date", 30, BLUE_).next_to(ax, UP, buff=0.15).shift(RIGHT * 2.5)
        with self.say("Now let the date slide. The column histogram barely moves. That is stationarity: "
                      "the law of the process does not depend on when you look.") as tr:
            self.play(FadeIn(top))
            self.play(t.animate.set_value(95), run_time=4, rate_func=linear)
            self.play(t.animate.set_value(15), run_time=4, rate_func=linear)
            self.fill(tr, 9)

    def window(self):
        ax = world_axes()
        x0 = ax.get_right()[0] + 0.35
        np.random.seed(2026)
        W = np.cumsum(np.random.randn(400, 101) * 0.36, axis=1)
        W[:, 0] = 0
        greys = VGroup(*[series_path(ax, np.clip(W[i], -4.5, 4.5), GREY_, 1.4).set_stroke(opacity=0.3) for i in range(1, 30)])
        red = series_path(ax, np.clip(W[0], -4.5, 4.5), RED_, 4)
        name = T("a random walk: every shock is remembered", 30, RED_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        t = ValueTracker(4)
        band = always_redraw(lambda: Rectangle(width=ax.c2p(8, 0)[0] - ax.c2p(0, 0)[0], height=ax.y_length,
                                               stroke_width=0, fill_color=BLUE_, fill_opacity=0.18)
                             .move_to(ax.c2p(t.get_value() + 4, 0)))
        hist = always_redraw(lambda: side_hist(ax, W[:, int(t.get_value()):int(t.get_value()) + 8].ravel(), x0, 9.0, RED_))
        with self.say("Compare a random walk, where every shock is remembered forever. Slide a window along "
                      "time and collect what the worlds do inside it. The histogram spreads wider and wider. "
                      "The variance is t sigma squared: the date matters, so this process is not "
                      "stationary.") as tr:
            self.play(Create(greys, lag_ratio=0.05), Create(red), FadeIn(name), run_time=2.5)
            self.add(band, hist)
            self.play(t.animate.set_value(92), run_time=7, rate_func=linear)
            self.fill(tr, 9.5)

    def one_life(self):
        Tn = 1200
        ax = world_axes(xmax=Tn)
        x0 = ax.get_right()[0] + 0.35
        np.random.seed(2026)
        e = np.random.randn(Tn + 1)
        x = np.zeros(Tn + 1)
        for k in range(1, Tn + 1):
            x[k] = RHO * x[k - 1] + e[k]
        n = ValueTracker(2)
        path = always_redraw(lambda: series_path(ax, x[:int(n.get_value()) + 1], RED_, 1.6))
        hist = always_redraw(lambda: side_hist(ax, x[1:int(n.get_value()) + 1], x0, 9.0, RED_))
        outline = side_density(ax, x0, 9.0, SD)
        olab = T("the many worlds", 26, YELLOW_).next_to(outline, UP, buff=0.1).shift(RIGHT * 0.3)
        hlab = T("one life", 26, RED_).next_to(ax, UP, buff=0.3).align_to(ax, LEFT)
        cnt = always_redraw(lambda: T(f"T = {int(n.get_value())}", 28, RED_).next_to(hlab, RIGHT, buff=0.5))
        with self.say("Back to the stationary world, and now follow a single life for a long time. Its "
                      "shocks are remembered for a while and then forgotten. Every value it visits drops "
                      "into a histogram. In yellow, the outline of what the many worlds show at one date.") as tr:
            self.play(Create(outline), FadeIn(olab), FadeIn(hlab))
            self.add(path, hist, cnt)
            self.play(n.animate.set_value(150), run_time=5, rate_func=linear)
            self.fill(tr, 6)
        lln = MathTex(r"\frac1T\sum_{t=1}^{T}x_t\ \xrightarrow{\;p\;}\ E(x_t)", font_size=38, color=YELLOW_)
        lln.move_to([ax.get_center()[0] + 1.6, 3.25, 0])
        box = SurroundingRectangle(lln, color=YELLOW_, buff=0.15, corner_radius=0.1).set_fill(BG, 0.9)
        with self.say("The one life fills the outline of the many worlds. That is ergodicity: because memory "
                      "fades, a single history eventually visits every region the ensemble occupies, and as "
                      "often. So the average along time converges to the average across worlds. That is the "
                      "law of large numbers.") as tr:
            self.play(n.animate.set_value(Tn), run_time=9, rate_func=linear)
            self.play(FadeIn(box), Write(lln))
            self.fill(tr, 11)

    def coin(self):
        coin = VGroup(Circle(radius=0.55, color=YELLOW_, fill_opacity=1, fill_color="#C9A227"),
                      MathTex("z", font_size=48, color=BG)).move_to(UP * 2.2)
        cap = T("tossed once, at the beginning of time", 30, YELLOW_).next_to(coin, DOWN, buff=0.3)
        with self.say("Now let us break it. At the beginning of time a coin is tossed, once. Heads, the "
                      "world lives around plus two; tails, around minus two.") as tr:
            self.play(FadeIn(coin))
            self.play(Rotate(coin, angle=6 * PI, axis=UP), run_time=2.2)
            self.play(FadeIn(cap))
            self.fill(tr, 3.5)
        self.play(FadeOut(cap), coin.animate.scale(0.6).to_corner(UR, buff=0.45))
        ax = world_axes()
        x0 = ax.get_right()[0] + 0.35
        np.random.seed(2026)
        z = np.where(np.random.rand(400) < 0.5, 2.0, -2.0)
        z[0] = 2.0
        X = ar1_worlds(400, 101, rho=0.3, sig=0.55) + z[:, None]
        cols = [TEAL_ if zi > 0 else PURPLE_ for zi in z]
        greys = VGroup(*[series_path(ax, X[i], cols[i], 1.4).set_stroke(opacity=0.35) for i in range(1, 30)])
        red = series_path(ax, X[0], RED_, 4)
        hist = side_hist(ax, X[:, 60], x0, 9.0, BLUE_)
        stat = T("the same two humps at every date: stationary", 28, BLUE_).next_to(ax, UP, buff=0.15).align_to(ax, LEFT)
        with self.say("Every date shows the same two humps, so the process is stationary.") as tr:
            self.play(Create(greys, lag_ratio=0.05), run_time=2.5)
            self.play(FadeIn(hist), FadeIn(stat))
            self.fill(tr, 3.5)
        rm = np.cumsum(X[0]) / np.arange(1, 102)
        run = series_path(ax, rm, YELLOW_, 5)
        zero = DashedLine(ax.c2p(0, 0), ax.c2p(100, 0), color=WHITE_, stroke_width=3)
        zl = MathTex(r"E(x_t)=0", font_size=34).next_to(ax.c2p(100, 0), UP, buff=0.12).shift(LEFT * 0.9)
        rl = MathTex(r"\bar x_T\to z=2", font_size=34, color=YELLOW_).move_to(ax.c2p(84, 4.0))
        ne = T("but not ergodic", 28, RED_).next_to(stat, RIGHT, buff=0.3)
        with self.say("But the coin is never tossed again. Our one life stays in its world forever. Its "
                      "running average settles on plus two, not on zero, and no amount of patience reveals "
                      "the other hump. Stationary, but not ergodic: the memory of the coin never fades.") as tr:
            self.play(greys.animate.set_stroke(opacity=0.12), Create(red), run_time=2)
            self.play(Create(zero), FadeIn(zl))
            self.play(Create(run), run_time=2.5)
            self.play(FadeIn(rl), FadeIn(ne))
            self.fill(tr, 7)

    def closing(self):
        g = VGroup(
            VGroup(T("Stationary:", 36, BLUE_), T("every date obeys the same law", 32)).arrange(RIGHT, buff=0.35),
            VGroup(T("Ergodic:", 36, YELLOW_), T("memory fades, so one life sees all the worlds", 32)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(UP * 1.1)
        f = MathTex(r"\frac1T\sum_{t=1}^{T}x_t\ \xrightarrow{\;p\;}\ E(x_t)", font_size=54, color=YELLOW_).shift(DOWN * 1.6)
        with self.say("So two conditions let one history speak for all. Stationarity: every date obeys the "
                      "same law. Ergodicity: memory fades, so one long life sees everything the many worlds "
                      "can show. Together, the time average converges to the expectation.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.6)
            self.play(Write(f), run_time=2)
            self.fill(tr, 5)
        self.wait(1)
