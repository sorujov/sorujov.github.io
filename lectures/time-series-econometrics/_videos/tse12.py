"""Lecture 12 intuition film: TAR inference and STAR -- where is the switch (LR(gamma) as a mountain
range flooded to 7.35), is there a switch at all (sup F), and is it a switch or a dimmer (STAR)."""
from common import *

config.tex_dir = str(Path(__file__).parent / "media" / "videos" / "tse12" / "Tex")   # private: parallel renders share media/Tex
from scipy.stats import chi2

CRIT = -2 * np.log(1 - np.sqrt(0.95))     # 7.35


def s2_grid(q, y):
    g = np.sort(q)
    g = g[(g >= np.quantile(q, 0.15)) & (g <= np.quantile(q, 0.85))]
    out = []
    for gg in g:
        I = q <= gg
        Z = np.column_stack([I, I * q, ~I, (~I) * q]).astype(float)
        r = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
        out.append(r @ r / len(y))
    return g, np.array(out)


def lr_sample():
    """Ninth SETAR(1) draw after seeding 2026: its LR(gamma) set comes in several pieces."""
    np.random.seed(2026)
    for _ in range(9):
        n = 300
        x = np.zeros(n + 1)
        for t in range(1, n + 1):
            x[t] = (0.4 + 0.6 * x[t - 1] if x[t - 1] <= 0 else -0.2 + 0.3 * x[t - 1]) + 0.5 * np.random.randn()
    g, s2 = s2_grid(x[:-1], x[1:])
    return g, n * (s2 - s2.min()) / s2.min()


def supf_null(R=500, n=150):
    np.random.seed(2026)
    fix, sup, first = [], [], None
    for r in range(R):
        z = np.zeros(n + 1)
        for t in range(1, n + 1):
            z[t] = 0.5 * z[t - 1] + np.random.randn()
        q, y = z[:-1], z[1:]
        Z = np.column_stack([np.ones(n), q])
        rl = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
        s2l = rl @ rl / n
        g, s2 = s2_grid(q, y)
        F = n * (s2l - s2) / s2
        if first is None:
            first = (g, F)
        fix.append(F[len(F) // 2])
        sup.append(F.max())
    return first, np.array(fix), np.array(sup)


def bulb(level, pos, scale=1.0):
    """A light bulb whose glow follows level in [0, 1]."""
    lv = float(np.clip(level, 0, 1))
    glow = VGroup(*[Circle(radius=scale * (0.55 + 0.18 * k), stroke_width=0, fill_color=YELLOW_,
                           fill_opacity=0.10 * lv * (1 - k / 6)) for k in range(6)])
    glass = Circle(radius=0.55 * scale, color=GREY_, stroke_width=3,
                   fill_color=interpolate_color(ManimColor(DIM), ManimColor(YELLOW_), lv), fill_opacity=1)
    base = VGroup(*[RoundedRectangle(width=0.5 * scale, height=0.12 * scale, corner_radius=0.05 * scale,
                                     color=GREY_, fill_color=GREY_, fill_opacity=1)
                    .move_to(DOWN * scale * (0.62 + 0.15 * k)) for k in range(3)])
    return VGroup(glow, glass, base).move_to(pos)


class Tse12(IntuitionScene):
    parts = ("hook", "where", "whether", "dimmer", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        sw, dm = ValueTracker(0), ValueTracker(0)
        L, R = LEFT * 3.4 + UP * 1.3, RIGHT * 3.4 + UP * 1.3
        b1 = always_redraw(lambda: bulb(sw.get_value(), L))
        b2 = always_redraw(lambda: bulb(dm.get_value(), R))
        plate = RoundedRectangle(width=0.8, height=1.3, corner_radius=0.1, color=GREY_).move_to(L + DOWN * 2.6)
        knob = always_redraw(lambda: RoundedRectangle(width=0.4, height=0.45, corner_radius=0.08, color=WHITE_,
                                                      fill_opacity=1).move_to(plate.get_center() + UP * (0.25 if sw.get_value() > 0.5 else -0.25)))
        track = Line(R + DOWN * 2.6 + LEFT * 1.3, R + DOWN * 2.6 + RIGHT * 1.3, color=GREY_, stroke_width=6)
        slider = always_redraw(lambda: Circle(radius=0.2, color=WHITE_, fill_opacity=1)
                               .move_to(track.point_from_proportion(dm.get_value())))
        l1 = T("switch", 30, GREY_).next_to(plate, DOWN, buff=0.25)
        l2 = T("dimmer", 30, GREY_).next_to(track, DOWN, buff=0.45)
        cap = T("Unemployment starts to rise:  a switch, or a dimmer?", 32, YELLOW_).move_to(DOWN * 3.2)
        with self.say("When unemployment starts to rise, does the economy change its rules at once, like a "
                      "light switch? Or does it slide from one regime into the other, like a dimmer? And if "
                      "there is a switch, where exactly is it on the wall, and is it there at all?") as tr:
            self.add(b1, b2)
            self.play(FadeIn(plate), FadeIn(knob), Create(track), FadeIn(slider), FadeIn(l1), FadeIn(l2), FadeIn(cap))
            for _ in range(2):
                self.play(sw.animate.set_value(1), run_time=0.15)
                self.play(dm.animate.set_value(1), run_time=2.2, rate_func=smooth)
                self.wait(0.4)
                self.play(sw.animate.set_value(0), run_time=0.15)
                self.play(dm.animate.set_value(0), run_time=2.2, rate_func=smooth)
                self.wait(0.4)
            self.fill(tr, 11.8)
        self.play(*[FadeOut(m) for m in (b1, b2, plate, knob, track, slider, l1, l2, cap)])
        self.title_card("TAR inference and STAR", 12,
                        "Three questions about regimes: where, whether, and how sharply.")

    # ------------------------------------------------------------------ where is the switch
    def where(self):
        g, LR = lr_sample()
        lo, hi = g[0], g[-1]
        ax = Axes(x_range=[lo, hi, 0.2], y_range=[0, 20, 5], x_length=11.6, y_length=3.9, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  y_axis_config={"numbers_to_include": [5, 10, 15, 20]}).move_to(DOWN * 1.25)
        xl = MathTex(r"\gamma", font_size=32, color=GREY_).next_to(ax.x_axis, RIGHT, buff=0.12)
        yl = MathTex(r"LR(\gamma)", font_size=32).next_to(ax.y_axis, UP, buff=0.1).shift(RIGHT * 0.4)
        top = np.minimum(LR, 20)
        edges = np.append(g, hi)
        pts = [ax.c2p(lo, 0)]
        for i in range(len(g)):
            pts += [ax.c2p(edges[i], top[i]), ax.c2p(edges[i + 1], top[i])]
        pts += [ax.c2p(hi, 0)]
        land = Polygon(*pts, stroke_color=WHITE_, stroke_width=2, fill_color=PURPLE_, fill_opacity=0.35)
        lrdef = MathTex(r"LR(\gamma)=T\,\frac{\hat\sigma^2(\gamma)-\hat\sigma^2}{\hat\sigma^2}",
                        font_size=40).to_edge(UP, buff=0.45)
        with self.say("Where is the switch? For every candidate threshold gamma, compare its residual "
                      "variance with the best one. The result, the likelihood ratio LR of gamma, is a "
                      "jagged mountain range, zero at gamma hat and rough everywhere, because the "
                      "residual variance is a staircase.") as tr:
            self.play(Write(lrdef), Create(ax), FadeIn(xl), FadeIn(yl))
            self.play(DrawBorderThenFill(land), run_time=3)
            self.fill(tr, 5.5)
        e1 = MathTex(r"LR(\gamma_0)\ \xrightarrow{d}\ \xi=\max_{r}\{2B(r)-|r|\}", font_size=38)
        e2 = MathTex(r"P(\xi\le u)", "=", r"\big(1-e^{-u/2}\big)^2", font_size=40)
        e3 = MathTex(r"0.95", "=", r"\big(1-e^{-c/2}\big)^2", font_size=40)
        e4 = MathTex(r"c", "=", r"-2\ln\big(1-\sqrt{0.95}\big)", r"=7.35", font_size=40)
        e4[3].set_color(BLUE_)
        for e in (e1, e2, e3, e4):
            e.move_to(UP * 1.75)
        with self.say("Hansen showed that at the true threshold this statistic converges to the maximum "
                      "of a two sided Brownian motion pulled down by a tent. Its distribution has a closed "
                      "form with no unknown parameter. Set it equal to zero point nine five, solve, and "
                      "the critical value appears: seven point three five.") as tr:
            self.play(FadeIn(e1))
            self.wait(2.5)
            self.play(FadeOut(e1), FadeIn(e2))
            self.wait(1.5)
            self.play(TransformMatchingTex(e2, e3))
            self.wait(1)
            self.play(TransformMatchingTex(e3, e4))
            self.fill(tr, 8.3)
        lvl = ValueTracker(0)

        def water():
            c = lvl.get_value()
            grp = VGroup()
            for i in range(len(g)):
                if top[i] < c:
                    grp.add(Polygon(ax.c2p(edges[i], top[i]), ax.c2p(edges[i + 1], top[i]),
                                    ax.c2p(edges[i + 1], c), ax.c2p(edges[i], c),
                                    stroke_width=0, fill_color=BLUE_, fill_opacity=0.75))
            return grp

        def ci():
            c = lvl.get_value()
            grp = VGroup()
            for i in range(len(g)):
                if top[i] < c:
                    grp.add(Line(ax.c2p(edges[i], 0), ax.c2p(edges[i + 1], 0), color=RED_, stroke_width=10))
            return grp

        Wt, C = always_redraw(water), always_redraw(ci)
        line = always_redraw(lambda: DashedLine(ax.c2p(lo, lvl.get_value()), ax.c2p(hi, lvl.get_value()),
                                                color=BLUE_, stroke_width=2))
        self.add(Wt, C, line)
        with self.say("Now flood the landscape up to that level. The lakes are the ninety five percent "
                      "confidence set: every gamma the test does not reject. Look at it. It is not "
                      "symmetric around gamma hat, and it comes in separate pieces, because the "
                      "mountains are jagged.") as tr:
            self.play(lvl.animate.set_value(CRIT), run_time=6, rate_func=linear)
            inside = g[top < CRIT]
            nl = T("95% confidence set", 28, RED_).next_to(ax.c2p((inside.min() + inside.max()) / 2, 0), DOWN, buff=0.2)
            self.play(FadeIn(nl))
            self.fill(tr, 7)
        self.remove(Wt, C, line)
        self.add(water(), ci(), line.copy())

    # ------------------------------------------------------------------ is there a switch at all
    def whether(self):
        (g, F), fix, sup = supf_null()
        tax = Axes(x_range=[g[0], g[-1], 1], y_range=[0, 14, 7], x_length=11, y_length=2.4, tips=False,
                   axis_config={"color": GREY_, "font_size": 22},
                   y_axis_config={"numbers_to_include": [7, 14]}).move_to(UP * 1.55 + RIGHT * 0.3)
        fl = MathTex(r"F(\gamma)", font_size=32).next_to(tax.y_axis, UP, buff=0.1)
        head = T("Is there a switch at all?  Data with no threshold:", 30).to_edge(UP, buff=0.35)
        k = ValueTracker(1)

        def fcurve():
            m = max(int(k.get_value()), 2)
            return VMobject(color=WHITE_, stroke_width=3).set_points_as_corners(
                [tax.c2p(g[i], min(F[i], 14)) for i in range(m)])

        Fc = always_redraw(fcurve)
        imax = int(np.argmax(F))
        with self.say("Is there a switch at all? Here are data with no threshold. Under linearity, gamma "
                      "does not exist, so we try every candidate and keep the best F statistic. The "
                      "search always finds something.") as tr:
            self.play(FadeIn(head), Create(tax), FadeIn(fl))
            self.add(Fc)
            self.play(k.animate.set_value(len(g)), run_time=4, rate_func=linear)
            pk = Dot(tax.c2p(g[imax], min(F[imax], 14)), color=RED_, radius=0.1)
            pl = MathTex(r"\sup F", font_size=32, color=RED_).next_to(pk, UP, buff=0.1)
            mid = Dot(tax.c2p(g[len(g) // 2], F[len(g) // 2]), color=GREY_, radius=0.09)
            ml = MathTex(r"F(\text{one fixed }\gamma)", font_size=28, color=GREY_).next_to(mid, DOWN, buff=0.15)
            self.play(FadeIn(pk), FadeIn(pl), FadeIn(mid), FadeIn(ml))
            self.fill(tr, 5.5)
        hax = Axes(x_range=[0, 24, 4], y_range=[0, 0.5, 0.25], x_length=11, y_length=2.6, tips=False,
                   axis_config={"color": GREY_, "font_size": 22},
                   x_axis_config={"numbers_to_include": [0, 4, 8, 12, 16, 20, 24]}).move_to(DOWN * 2.3 + RIGHT * 0.3)
        m = ValueTracker(2)
        bins = np.arange(0, 24.01, 1.0)

        def hist(data, col, op):
            d = data[: int(m.get_value())]
            h, _ = np.histogram(d, bins)
            h = h / max(len(d), 1)
            return VGroup(*[Rectangle(width=hax.x_length / 24, height=hax.y_length * min(v, 0.5) / 0.5,
                                      stroke_width=1, stroke_color=BG, fill_color=col, fill_opacity=op)
                            .move_to(hax.c2p(bins[i] + 0.5, 0), aligned_edge=DOWN) for i, v in enumerate(h) if v > 0])

        H1 = always_redraw(lambda: hist(fix, GREY_, 0.6))
        H2 = always_redraw(lambda: hist(sup, RED_, 0.55))
        q1, q2 = chi2.ppf(0.95, 2), np.quantile(sup, 0.95)
        v1 = DashedLine(hax.c2p(q1, 0), hax.c2p(q1, 0.45), color=GREY_, stroke_width=3)
        v2 = DashedLine(hax.c2p(q2, 0), hax.c2p(q2, 0.45), color=RED_, stroke_width=3)
        t1 = MathTex(r"\chi^2(2):\ 5.99", font_size=30, color=GREY_).next_to(v1.get_top(), RIGHT, buff=0.1)
        t2 = MathTex(rf"\sup F:\ {q2:.1f}", font_size=30, color=RED_).next_to(v2.get_top(), RIGHT, buff=0.1)
        with self.say("Repeat on five hundred such samples. At one fixed gamma, F behaves like chi square "
                      "with two degrees of freedom, with ninety five percent point six. The maximum over "
                      "the search has its ninety five percent point near twelve: searching doubles the "
                      "bar. So critical values come from the fixed regressor bootstrap, which keeps the "
                      "regressors and redraws only the left hand side.") as tr:
            self.play(Create(hax))
            self.add(H1, H2)
            self.play(m.animate.set_value(500), run_time=6, rate_func=rate_functions.ease_in_quad)
            self.play(Create(v1), FadeIn(t1))
            self.play(Create(v2), FadeIn(t2))
            self.fill(tr, 8)
        self.remove(H1, H2)
        self.add(hist(fix, GREY_, 0.6), hist(sup, RED_, 0.55))

    # ------------------------------------------------------------------ switch or dimmer
    def dimmer(self):
        d = ValueTracker(0.3)
        u = ValueTracker(-2.5)
        esh = ValueTracker(0)        # 0 logistic, 1 exponential
        ax = Axes(x_range=[-3, 3, 1], y_range=[0, 1, 0.5], x_length=8.2, y_length=3.0, tips=False,
                  axis_config={"color": GREY_, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).move_to(LEFT * 2.1 + DOWN * 1.9)
        xl = MathTex(r"q_{t-1}-\gamma", font_size=30, color=GREY_).next_to(ax.x_axis, DOWN, buff=0.2).align_to(ax, RIGHT)

        def Gf(v):
            dd = d.get_value()
            lg = 1 / (1 + np.exp(-dd * v))
            ex = 1 - np.exp(-dd * v * v)
            return (1 - esh.get_value()) * lg + esh.get_value() * ex

        curve = always_redraw(lambda: ax.plot(Gf, x_range=[-3, 3, 0.01], color=YELLOW_, stroke_width=5))
        dot = always_redraw(lambda: Dot(ax.c2p(u.get_value(), Gf(u.get_value())), color=WHITE_, radius=0.1))
        B = always_redraw(lambda: bulb(Gf(u.get_value()), RIGHT * 4.6 + DOWN * 1.6, 1.15))
        dl = always_redraw(lambda: MathTex(rf"\delta={d.get_value():.1f}", font_size=40, color=YELLOW_)
                           .next_to(ax, UP, buff=0.15).align_to(ax, LEFT))
        model = MathTex(r"x_t=(\mu_1+\rho_1x_{t-1})", r"\big(1-G\big)", "+", r"(\mu_2+\rho_2x_{t-1})", r"\,G", r"+\varepsilon_t",
                        font_size=38).to_edge(UP, buff=0.4)
        model[1].set_color(YELLOW_)
        model[4].set_color(YELLOW_)
        gdef = MathTex(r"G=\frac{1}{1+e^{-\delta(q_{t-1}-\gamma)}}", font_size=38, color=YELLOW_).next_to(model, DOWN, buff=0.3)
        with self.say("Finally, switch or dimmer. A smooth transition model blends the two regimes with "
                      "a weight G between zero and one. In the logistic version the parameter delta sets "
                      "the speed. With delta small the weight barely moves: the bulb glows at half "
                      "strength, and the model is one linear autoregression.") as tr:
            self.play(Write(model))
            self.play(FadeIn(gdef))
            self.play(Create(ax), FadeIn(xl), FadeIn(dl))
            self.add(curve, dot, B)
            self.play(u.animate.set_value(2.5), run_time=3, rate_func=there_and_back)
            self.fill(tr, 6)
        with self.say("Turn delta up and the ramp steepens into a step. The dimmer becomes a light "
                      "switch, and in the limit the model is exactly the threshold autoregression.") as tr:
            self.play(d.animate.set_value(3), run_time=2)
            self.play(u.animate.set_value(2.5), run_time=2.5)
            self.play(d.animate.set_value(40), u.animate.set_value(-2.5), run_time=3)
            self.play(u.animate.set_value(2.5), run_time=2.5)
            self.fill(tr, 10)
        g2 = MathTex(r"G=1-e^{-\delta(q_{t-1}-\gamma)^2}", font_size=38, color=YELLOW_).move_to(gdef)
        with self.say("Change the shape to an exponential and the regimes become near and far: the bulb "
                      "is dark at gamma and lights up on both sides. That is a smooth version of last "
                      "lecture's band.") as tr:
            self.play(Transform(gdef, g2), esh.animate.set_value(1), d.animate.set_value(1.2), run_time=2)
            self.play(u.animate.set_value(-2.5), run_time=4, rate_func=linear)
            self.play(u.animate.set_value(0), run_time=2, rate_func=linear)
            self.fill(tr, 8)

    # ------------------------------------------------------------------ closing card
    def closing(self):
        s = VGroup(T("Locate the switch by flooding LR to 7.35,", 34, YELLOW_),
                   T("test it with sup F, and let delta say switch or dimmer.", 34, YELLOW_)).arrange(DOWN, buff=0.22)
        f = MathTex(r"CI_{0.95}(\gamma_0)=\{\gamma:\ LR(\gamma)\le 7.35\}", font_size=44, color=BLUE_)
        f2 = MathTex(r"G(u)=\frac{1}{1+e^{-\delta(u-\gamma)}}:\quad \delta\to0\ \text{linear},\ \ "
                     r"\delta\to\infty\ \text{TAR}", font_size=40, color=YELLOW_)
        VGroup(s, f, f2).arrange(DOWN, buff=0.6)
        with self.say("So: the threshold is located by flooding the likelihood ratio to seven point three "
                      "five, its existence is tested with sup F and bootstrap critical values, and delta "
                      "tells us whether the regimes switch like a light or fade like a dimmer.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f))
            self.play(Write(f2))
            self.fill(tr, 4)
