"""Lecture 9 intuition film: unit roots and Brownian motion — zoom into a random walk."""
from common import *

FW, FH = config.frame_width, config.frame_height


def step_path(ax, S, T):
    """S_T(r) = S_floor(Tr) / sqrt(T) as a staircase on axes ax (r in [0, 1])."""
    pts = []
    for t in range(T):
        y = S[t] / np.sqrt(T)
        pts += [ax.c2p(t / T, y), ax.c2p((t + 1) / T, y)]
    pts.append(ax.c2p(1, S[T] / np.sqrt(T)))
    return VMobject().set_points_as_corners(pts)


def car(color):
    body = RoundedRectangle(width=1.0, height=0.36, corner_radius=0.12, color=color, fill_color=color,
                            fill_opacity=1, stroke_width=0)
    cab = RoundedRectangle(width=0.5, height=0.26, corner_radius=0.1, color=color, fill_color=color,
                           fill_opacity=1, stroke_width=0).next_to(body, UP, buff=-0.04).shift(LEFT * 0.08)
    w1 = Circle(radius=0.12, color=WHITE_, fill_color=BG, fill_opacity=1, stroke_width=3).move_to(body.get_bottom() + LEFT * 0.28)
    w2 = w1.copy().move_to(body.get_bottom() + RIGHT * 0.28)
    return VGroup(body, cab, w1, w2)


class Tse9(ZoomScene):
    parts = ("hook", "staircase", "trick", "race", "closing")

    # -------------------------------------------------------------- camera helpers
    def frame_text(self, mob, corner=UL, buff=0.4):
        """Size and place a label relative to the current camera frame."""
        fr = self.camera.frame
        k = fr.width / FW
        mob.scale(k)
        mob.move_to(fr.get_center() + np.array([corner[0] * (fr.width / 2 - buff * k), corner[1] * (fr.height / 2 - buff * k), 0])
                    - np.array([corner[0] * mob.width / 2, corner[1] * mob.height / 2, 0]))
        return mob

    def zoom(self, lines, widths, center, width, yc=0.0, squash=1.0, run_time=3.0):
        """Move the camera to (center, width) while squashing lines vertically about yc; strokes keep their look."""
        fr = self.camera.frame
        c0, w0 = fr.get_center().copy(), fr.width
        c1 = np.array(center, dtype=float)
        p = (c0 * width - c1 * w0) / (width - w0) if abs(width - w0) > 1e-9 else c0
        base = [l.points.copy() for l in lines]

        def upd(m, a):
            w = w0 * (width / w0) ** a
            fr.scale_to_fit_width(w)
            fr.move_to(p - (p - c0) * w / w0 if abs(width - w0) > 1e-9 else c0 + (c1 - c0) * a)
            s = 1 + (squash - 1) * a
            for l, b, sw in zip(lines, base, widths):
                q = b.copy()
                q[:, 1] = yc + (b[:, 1] - yc) * s
                l.points = q
                l.set_stroke(width=sw * w / FW)

        self.play(UpdateFromAlphaFunc(VMobject(), upd, rate_func=smooth), run_time=run_time)

    def reset_camera(self):
        self.camera.frame.scale_to_fit_width(FW).move_to(ORIGIN)

    # -------------------------------------------------------------- cold open
    def hook(self):
        dates, v = load_csv("DEXUSEU.csv")
        n = len(v)
        ax = Axes(x_range=[0, n], y_range=[0.8, 1.65], x_length=13.4, y_length=5.4, tips=False,
                  axis_config={"color": GREY_}).shift(DOWN * 0.3)
        pts = np.array([ax.c2p(i, y) for i, y in enumerate(v)])
        core = VMobject().set_points_as_corners(pts).set_stroke(BLUE_, 2.2)
        halo = core.copy().set_stroke(BLUE_, 9, opacity=0.18)
        lines, widths = [halo, core], [9, 2.2]
        lab = self.frame_text(T("Euro in dollars, every trading day, 1999–2026", 28, GREY_), UL)

        # choose three nested windows, each 1/4 as wide, squashing height by 1/2 each time
        xs, ys = pts[:, 0].copy(), pts[:, 1].copy()
        plan, cx, w = [], 0.0, FW
        for k in range(3):
            w1, h1 = w / 4, FH * (w / 4) / FW
            best = None
            for c in np.linspace(cx - w / 2 + w1 / 2, cx + w / 2 - w1 / 2, 41):
                m = (xs >= c - w1 / 2) & (xs <= c + w1 / 2)
                if m.sum() < 20:
                    continue
                yc = (ys[m].max() + ys[m].min()) / 2
                score = abs((ys[m].max() - ys[m].min()) / 2 / h1 - 0.55)
                if best is None or score < best[0]:
                    best = (score, c, yc, m)
            _, c, yc, m = best
            ys = yc + (ys - yc) / 2
            idx = np.where(m)[0]
            plan.append((c, yc, w1, dates[idx[0]][:7], dates[idx[-1]][:7]))
            cx, w = c, w1

        with self.say("The euro in dollars, every trading day for twenty-seven years.") as tr:
            self.play(Create(core), FadeIn(halo), FadeIn(lab), run_time=3, rate_func=linear)
            self.fill(tr, 3)
        with self.say("Zoom in to seven years. Then to two. Then to half a year. The line never turns "
                      "smooth: at every scale it looks the same. Which of these pictures is a quarter "
                      "of a century, and which is half a year?") as tr:
            for c, yc, w1, d0, d1 in plan:
                self.play(FadeOut(lab), run_time=0.4)
                self.zoom(lines, widths, [c, yc, 0], w1, yc=yc, squash=0.5, run_time=2.2)
                lab = self.frame_text(T(f"{d0}  to  {d1}", 28, GREY_), UL)
                self.play(FadeIn(lab), run_time=0.5)
                self.wait(1.2)
            self.fill(tr, 12.9)
        self.play(FadeOut(VGroup(core, halo, lab)))
        self.reset_camera()
        self.title_card("Unit roots and Brownian motion", 9,
                        "Lines like this are random walks, and this lecture is about what they look like "
                        "when we step far back.")

    # -------------------------------------------------------------- staircase to Brownian motion
    def staircase(self):
        np.random.seed(2026)
        coin = np.random.choice([-1.0, 1.0], 10000)
        S = np.r_[0, np.cumsum(coin)]
        ax = Axes(x_range=[0, 1, 0.25], y_range=[-2.5, 2.5, 1], x_length=9.6, y_length=5.2, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"include_numbers": True}).shift(LEFT * 1.4 + DOWN * 0.45)
        rl = VGroup(*[MathTex(s_, font_size=32, color=GREY_).next_to(ax.c2p(x_, -2.5), DOWN, buff=0.12)
                      for s_, x_ in ((r"r=0", 0), (r"r=1", 1))])
        env = VGroup(*[ax.plot(lambda r, s=s: s * 1.96 * np.sqrt(r), x_range=[0, 1], color=PURPLE_,
                               stroke_width=2).set_stroke(opacity=0.8) for s in (1, -1)])
        for e in env:
            e.become(DashedVMobject(e, num_dashes=40))
        f = MathTex(r"S_T(r)=\frac{1}{\sigma\sqrt T}\,S_{\lfloor Tr\rfloor}", font_size=42).to_corner(UL, buff=0.45)
        Tl = VGroup(MathTex(r"T=", font_size=40, color=YELLOW_), Integer(10, font_size=40, color=YELLOW_)).arrange(RIGHT, buff=0.12)
        Tl.to_corner(UR, buff=0.5).shift(LEFT * 2.0)
        p = step_path(ax, S, 10).set_stroke(YELLOW_, 4)
        with self.say("Take a fair coin: up one step for heads, down one for tails. Ten tosses make a "
                      "staircase. Now squeeze time so that the T steps fit into the unit interval, and "
                      "shrink the height by sigma root T.") as tr:
            self.play(Create(ax), FadeIn(rl), Write(f))
            self.play(Create(p), FadeIn(Tl), run_time=2)
            self.fill(tr, 4)
        with self.say("A hundred tosses, a thousand, ten thousand. The steps become invisible, and what is "
                      "left is a continuous, endlessly jagged curve: Brownian motion.") as tr:
            for T_ in (100, 1000, 10000):
                q = step_path(ax, S, T_).set_stroke(YELLOW_, 4 if T_ < 1000 else 2.5)
                self.play(Transform(p, q), Tl[1].animate.set_value(T_), run_time=1.6)
                self.wait(0.6)
            self.play(Create(env))
            self.fill(tr, 7.3)

        # the ordinary CLT is only the end point; the FCLT is the whole path
        hx = Axes(x_range=[0, 1.6, 1], y_range=[-2.5, 2.5, 1], x_length=2.0, y_length=5.2, tips=False,
                  axis_config={"color": GREY_}).next_to(ax, RIGHT, buff=0.15)
        np.random.seed(2026)
        paths = VGroup()
        ends = []
        for b in range(24):
            e = np.random.normal(0, 1, 2000)
            Sb = np.r_[0, np.cumsum(e)] / np.sqrt(2000)
            ends.append(Sb[-1])
            pts = [ax.c2p(t / 2000, Sb[t]) for t in range(0, 2001, 4)]
            paths.add(VMobject().set_points_as_corners(pts).set_stroke(BLUE_, 1.4, opacity=0.5))
        ends = np.r_[ends, np.random.normal(0, 1, 600)]
        edges = np.linspace(-2.5, 2.5, 21)
        cnt, _ = np.histogram(ends, edges)
        dens = cnt / cnt.sum() / (edges[1] - edges[0])
        hist = VGroup(*[Rectangle(width=hx.x_length * d / 1.6 + 1e-3, height=hx.y_length / 20, stroke_width=1,
                                  stroke_color=BG, fill_color=TEAL_, fill_opacity=0.8)
                        .move_to(hx.c2p(0, (a + b_) / 2), aligned_edge=LEFT)
                        for a, b_, d in zip(edges[:-1], edges[1:], dens)])
        bell = hx.plot_parametric_curve(lambda y: np.array([np.exp(-y * y / 2) / np.sqrt(2 * np.pi), y, 0]),
                                        t_range=[-2.5, 2.5], color=WHITE_, stroke_width=3)
        lbl = MathTex(r"N(0,1)", font_size=34, color=TEAL_).next_to(hx, UP, buff=0.1)
        with self.say("Many such paths, and their end points pile up into the bell curve. That bell is "
                      "the ordinary central limit theorem. The functional version says more: the whole "
                      "path converges, to the same Brownian motion, whatever coin we toss.") as tr:
            self.play(FadeOut(p), LaggedStart(*[Create(x) for x in paths], lag_ratio=0.1), run_time=3.5)
            self.play(LaggedStart(*[GrowFromEdge(h, LEFT) for h in hist], lag_ratio=0.05), FadeIn(lbl), run_time=2)
            self.play(Create(bell))
            self.fill(tr, 6.5)

    # -------------------------------------------------------------- why the square root
    def trick(self):
        np.random.seed(2026)
        e = np.random.normal(0, 1, 4096)
        S = np.r_[0, np.cumsum(e)]
        sc = 5.0 / (S.max() - S.min())
        x0 = -6.6
        pts = np.array([[x0 + 13.2 * t / 4096, (S[t] - (S.max() + S.min()) / 2) * sc, 0] for t in range(4097)])
        core = VMobject().set_points_as_corners(pts).set_stroke(YELLOW_, 2.4)
        lines, widths = [core], [2.4]
        with self.say("The opening zoom hid a trick. Here is a random walk. Zoom honestly into its first "
                      "quarter, by four in both directions.") as tr:
            self.play(Create(core), run_time=2.5, rate_func=linear)
            q = pts[:1025]
            cy = (q[:, 1].max() + q[:, 1].min()) / 2
            self.zoom(lines, widths, [x0 + 13.2 / 8, cy, 0], FW / 4, run_time=2.5)
            self.fill(tr, 5)
        def boxed(t):
            return VGroup(BackgroundRectangle(t, color=BG, fill_opacity=0.85, buff=0.12), t)

        warn = self.frame_text(boxed(T("time ÷ 4, height ÷ 4: far too wild", 30, RED_)), UL)
        with self.say("The path no longer fits the window. It is too wild. To make it look like the "
                      "original, we must squeeze its height, but only by two.") as tr:
            self.play(FadeIn(warn))
            self.wait(2)
            self.play(FadeOut(warn))
            self.zoom(lines, widths, [x0 + 13.2 / 8, cy, 0], FW / 4, yc=cy, squash=0.5, run_time=2.2)
            ok = self.frame_text(boxed(T("time ÷ 4, height ÷ 2", 30, GREEN_)), UL)
            self.play(FadeIn(ok))
            self.fill(tr, 5.7)
        self.play(FadeOut(VGroup(core, ok)))
        self.reset_camera()
        a = MathTex(r"\operatorname{Var}(S_t)=t\,\sigma^2", r"\quad\Longrightarrow\quad",
                    r"\operatorname{sd}(S_t)=\sigma\sqrt t", font_size=46)
        b = MathTex(r"B(c\,r)\ \overset{d}{=}\ \sqrt c\;B(r)", font_size=50, color=YELLOW_)
        g = VGroup(a, b).arrange(DOWN, buff=0.8)
        with self.say("Time by four, height by two. Variances add up, so the spread of a random walk "
                      "grows like the square root of time. That is why we divide by root T, and why "
                      "Brownian motion is self-similar: speed up time by c, and it looks the same, "
                      "only root c times larger.") as tr:
            self.play(Write(a), run_time=2)
            self.play(Write(b), run_time=2)
            self.fill(tr, 4)

    # -------------------------------------------------------------- three rates as a race
    def race(self):
        lanes = [(r"\sqrt T", 0.5, BLUE_, "sample mean", r"\textstyle\sum 1 = T"),
                 (r"T", 1.0, RED_, "unit-root coefficient", r"\textstyle\sum y_{t-1}^2\sim T^2"),
                 (r"T^{3/2}", 1.5, GREEN_, "trend slope", r"\textstyle\sum t^2\sim T^3")]
        lt = ValueTracker(1.0)
        start, k = -3.4, 1.45
        ys = [1.5, -0.3, -2.1]
        title = T("how fast each estimate sharpens (log scale)", 28, GREY_).to_edge(UP, buff=0.4)
        Tl = VGroup(MathTex(r"T=", font_size=40), Integer(10, font_size=40)).arrange(RIGHT, buff=0.12)
        Tl.next_to(title, DOWN, buff=0.2)
        Tl[1].add_updater(lambda m: m.set_value(int(round(10 ** lt.get_value()))))
        objs = VGroup()
        cars = []
        for (rate, a, col, name, why), y in zip(lanes, ys):
            track = Line([start, y - 0.3, 0], [6.8, y - 0.3, 0], color=DIM, stroke_width=3)
            nm = T(name, 26, col).move_to([-5.3, y + 0.17, 0])
            rt = MathTex(rate, font_size=40, color=col).move_to([-5.3, y - 0.33, 0])
            c = car(col)
            c.add_updater(lambda m, a=a, y=y: m.move_to([start + 0.5 + k * a * lt.get_value(), y - 0.02, 0]))
            objs.add(track, nm, rt)
            cars.append((c, why, col, y))
        with self.say("Three estimators, three speeds. Each car's distance is how much sharper its "
                      "estimate has become, on a log scale, as the sample grows. The sample mean "
                      "improves like root T. The coefficient of a unit root like T: superconsistent. "
                      "The slope of a linear trend like T to the three halves.") as tr:
            self.play(FadeIn(title), FadeIn(objs), FadeIn(Tl))
            for c, *_ in cars:
                c.update()
                self.add(c)
            self.play(lt.animate.set_value(4.0), run_time=7, rate_func=linear)
            self.fill(tr, 8)
        whys = VGroup(*[MathTex(w, font_size=34, color=col).next_to(c, UP, buff=0.12) for c, w, col, y in cars])
        with self.say("The reason is how fast each regressor piles up information, its sum of squares. "
                      "A constant adds one each period. A random walk wanders away like root t, so its "
                      "squares grow like T squared. A trend grows like T cubed. The rate is the square "
                      "root of that growth.") as tr:
            for w in whys:
                self.play(FadeIn(w, shift=UP * 0.15), run_time=1.2)
                self.wait(1.4)
            self.fill(tr, 7.8)
        for c, *_ in cars:
            c.clear_updaters()
        Tl[1].clear_updaters()

    # -------------------------------------------------------------- closing
    def closing(self):
        s = VGroup(T("Squeeze time by T and height by √T:", 34),
                   T("every random walk becomes Brownian motion.", 34)).arrange(DOWN, buff=0.2)
        f1 = MathTex(r"\frac{1}{\sigma\sqrt T}\,S_{\lfloor Tr\rfloor}\ \xrightarrow{d}\ B(r)", font_size=48, color=YELLOW_)
        f2 = MathTex(r"\sqrt T(\bar x-\mu),\qquad T(\hat\rho-1),\qquad T^{3/2}(\hat\delta-\delta)",
                     font_size=40, color=TEAL_)
        g = VGroup(s, f1, f2).arrange(DOWN, buff=0.65)
        with self.say("So: squeeze time by T and height by root T, and every random walk becomes the "
                      "same Brownian motion. It is the lens through which we will read the unit root "
                      "tests of the next lecture.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f1), run_time=1.8)
            self.play(FadeIn(f2))
            self.fill(tr, 4)
        self.wait(1)
