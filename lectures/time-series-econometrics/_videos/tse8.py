"""Lecture 8 intuition film: ARMA models and forecasting — the memory of a pendulum."""
from common import *

PHI1, PHI2, SIG = 1.6, -0.9, 0.35


def psi_weights(p1, p2, n):
    psi = np.zeros(n)
    psi[0] = 1.0
    for j in range(1, n):
        psi[j] = p1 * psi[j - 1] + (p2 * psi[j - 2] if j >= 2 else 0.0)
    return psi


def acf_from_psi(psi, lags):
    g = np.array([np.dot(psi[:len(psi) - k], psi[k:]) for k in range(lags + 1)])
    return g / g[0]


def pacf_from_acf(r, lags):
    out, phi = [], np.zeros(0)
    for k in range(1, lags + 1):
        if k == 1:
            a = r[1]
            phi = np.array([a])
        else:
            a = (r[k] - np.dot(phi, r[k - 1:0:-1])) / (1 - np.dot(phi, r[1:k]))
            phi = np.append(phi - a * phi[::-1], a)
        out.append(a)
    return np.array(out)


def ar2_path(n, seed=2026, x0=0.0, x1=0.0, sig=SIG):
    np.random.seed(seed)
    e = np.random.normal(0, sig, n)
    x = np.zeros(n)
    x[0], x[1] = x0, x1
    for t in range(2, n):
        x[t] = PHI1 * x[t - 1] + PHI2 * x[t - 2] + e[t]
    return x, e


def bars(ax, vals, color, x0=1, w=6):
    g = VGroup()
    for i, v in enumerate(vals):
        if abs(v) < 1e-3:
            continue
        g.add(Line(ax.c2p(x0 + i, 0), ax.c2p(x0 + i, v), color=color, stroke_width=w))
    return g


class Tse8(IntuitionScene):
    parts = ("hook", "two_lags", "roots", "fingerprints", "fan", "closing")

    # ------------------------------------------------------------------ cold open
    def hook(self):
        pivot = np.array([-4.9, 2.9, 0])
        L = 2.5
        ax = Axes(x_range=[0, 130, 20], y_range=[-4, 4, 2], x_length=8.4, y_length=4.6, tips=False,
                  axis_config={"color": GREY_}).move_to(RIGHT * 2.45 + DOWN * 0.1)
        # phase 1: one kick, then calm; phase 2: wind, a gust every period
        n1 = 40
        calm = np.zeros(n1)
        calm[1] = 1.2
        for t in range(2, n1):
            calm[t] = PHI1 * calm[t - 1] + PHI2 * calm[t - 2]
        np.random.seed(2026)
        gust = np.random.normal(0, SIG, 90)
        windy = list(calm)
        for t in range(90):
            windy.append(PHI1 * windy[-1] + PHI2 * windy[-2] + gust[t])
        xs = np.array(windy)
        shock = np.concatenate([np.zeros(n1), gust])
        shock[1] = 1.2
        s = ValueTracker(0)

        def xval():
            v = s.get_value()
            i = int(np.floor(v))
            f = v - i
            return xs[i] if i + 1 >= len(xs) else (1 - f) * xs[i] + f * xs[i + 1]

        def bob_pos():
            a = 0.26 * xval()
            return pivot + L * np.array([np.sin(a), -np.cos(a), 0])

        support = Line(pivot + LEFT * 0.7, pivot + RIGHT * 0.7, color=GREY_, stroke_width=5)
        rod = always_redraw(lambda: Line(pivot, bob_pos(), color=WHITE_, stroke_width=3))
        bob = always_redraw(lambda: Dot(bob_pos(), radius=0.2, color=YELLOW_))
        rest = DashedLine(pivot, pivot + DOWN * (L + 0.5), color=DIM)

        def wind():
            i = int(np.floor(s.get_value()))
            e = shock[min(i, len(shock) - 1)] if i >= 1 else 0
            if abs(e) < 0.05:
                return VMobject()
            p = bob_pos() + DOWN * 0.55
            return Arrow(p - RIGHT * 1.4 * e, p + RIGHT * 1.4 * e, buff=0, color=BLUE_, stroke_width=4,
                         max_tip_length_to_length_ratio=0.35)

        gusts = always_redraw(wind)

        def trace():
            v = s.get_value()
            i = int(np.floor(v))
            pts = [ax.c2p(t, xs[t]) for t in range(i + 1)] + [ax.c2p(v, xval())]
            if len(pts) < 2:
                pts = pts + pts
            return VMobject(color=YELLOW_, stroke_width=3).set_points_as_corners(pts)

        tr_ = always_redraw(trace)
        head = always_redraw(lambda: Dot(ax.c2p(s.get_value(), xval()), radius=0.07, color=YELLOW_))
        link = always_redraw(lambda: DashedLine(bob_pos(), ax.c2p(s.get_value(), xval()), color=DIM,
                                                dash_length=0.08))
        with self.say("A pendulum, struck once, swings, and the swing slowly dies away.") as tr:
            self.play(FadeIn(support), FadeIn(rest), Create(ax))
            self.add(rod, bob, gusts, link, tr_, head)
            self.play(s.animate.set_value(n1 - 1), run_time=5, rate_func=linear)
            self.fill(tr, 5.5)
        with self.say("Now put it out in the wind, with a gust every period. It never settles, and it "
                      "never runs away. Its position is a stationary time series, and its memory is "
                      "the pendulum's own: each gust is remembered for a while, and then forgotten.") as tr:
            self.play(s.animate.set_value(len(xs) - 1), run_time=11, rate_func=linear)
            self.fill(tr, 11)
        self.play(FadeOut(Group(*self.mobjects)))
        self.remove(*self.mobjects)
        self.title_card("ARMA models and forecasting", 8,
                        "That memory, how to read it from data, and how to forecast with it, is the "
                        "subject of this lecture.")

    # ------------------------------------------------------------------ why two lags
    def two_lags(self):
        l1 = MathTex(r"x_t", r"=", r"\underbrace{x_{t-1}+(x_{t-1}-x_{t-2})}_{\text{inertia}}",
                     r"\underbrace{-\,k\,x_{t-1}}_{\text{spring}}",
                     r"\underbrace{-\,c\,(x_{t-1}-x_{t-2})}_{\text{friction}}", r"+\,\varepsilon_t",
                     font_size=42).shift(UP * 1.9)
        l1[2].set_color(BLUE_)
        l1[3].set_color(TEAL_)
        l1[4].set_color(RED_)
        l1[5].set_color(YELLOW_)
        l2 = MathTex(r"x_t", r"=", r"(2-k-c)", r"\,x_{t-1}", r"-", r"(1-c)", r"\,x_{t-2}", r"+\,\varepsilon_t",
                     font_size=46).shift(DOWN * 0.3)
        l2[7].set_color(YELLOW_)
        l3 = MathTex(r"x_t", r"=", r"\phi_1", r"\,x_{t-1}", r"+", r"\phi_2", r"\,x_{t-2}", r"+\,\varepsilon_t",
                     font_size=46).shift(DOWN * 0.3)
        l3[2].set_color(PURPLE_)
        l3[5].set_color(PURPLE_)
        l3[7].set_color(YELLOW_)
        nums = MathTex(r"k=0.3,\ c=0.1\ \Rightarrow\ \phi_1=1.6,\ \ \phi_2=-0.9", font_size=40,
                       color=PURPLE_).shift(DOWN * 2.3)
        with self.say("Why should such a series need two lags? Because a pendulum needs two facts: "
                      "where it is, and how fast it is moving. Tomorrow's position is today's plus "
                      "today's velocity, minus a spring pulling it back, minus friction eating the "
                      "velocity, plus a gust.") as tr:
            self.play(Write(l1), run_time=4)
            self.fill(tr, 4)
        with self.say("Collect the terms, and the laws of motion become an autoregression of order two. "
                      "Friction and the spring decide phi one and phi two.") as tr:
            self.play(TransformFromCopy(l1, l2), run_time=2)
            self.play(TransformMatchingTex(l2, l3), run_time=1.5)
            self.play(FadeIn(nums, shift=UP * 0.2))
            self.fill(tr, 4.5)

    # ------------------------------------------------------------------ roots and the length of memory
    def roots(self):
        p2 = ValueTracker(PHI2)
        plane = ComplexPlane(x_range=[-1.6, 1.6, 1], y_range=[-1.6, 1.6, 1], x_length=4.6, y_length=4.6,
                             background_line_style={"stroke_color": DIM, "stroke_width": 1},
                             axis_config={"color": GREY_}).move_to(LEFT * 4.3 + DOWN * 0.45)
        circ = Circle(radius=plane.n2p(1)[0] - plane.n2p(0)[0], color=WHITE_, stroke_width=3).move_to(plane.n2p(0))
        cl = T("unit circle", 24, GREY_).next_to(circ, DOWN, buff=0.1).shift(RIGHT * 1.0)
        ttl = MathTex(r"\text{roots of }\ 1-\phi_1 z-\phi_2 z^2=0", font_size=34).next_to(plane, UP, buff=0.25)
        ax = Axes(x_range=[0, 40, 10], y_range=[-2.6, 2.6, 1], x_length=7.4, y_length=4.4, tips=False,
                  axis_config={"color": GREY_}).move_to(RIGHT * 2.9 + DOWN * 0.3)
        al = MathTex(r"\text{struck once: }\ \psi_j", font_size=34, color=YELLOW_).next_to(ax, UP, buff=0.25)

        def rts():
            r = np.roots([-p2.get_value(), -PHI1, 1])
            inside = np.all(np.abs(r) > 1)
            col = GREEN_ if inside else RED_
            return VGroup(*[Dot(plane.n2p(complex(z)), radius=0.11, color=col) for z in r])

        def irf():
            ps = psi_weights(PHI1, p2.get_value(), 41)
            g = VGroup()
            for j, v in enumerate(ps):
                vv = float(np.clip(v, -2.6, 2.6))
                g.add(Line(ax.c2p(j, 0), ax.c2p(j, vv), color=YELLOW_ if abs(v) < 2.6 else RED_, stroke_width=4))
            return g

        R = always_redraw(rts)
        S = always_redraw(irf)
        val = VGroup(MathTex(r"\phi_2=", font_size=38, color=PURPLE_),
                     DecimalNumber(PHI2, num_decimal_places=2, font_size=38, color=PURPLE_)).arrange(RIGHT, buff=0.12)
        val.to_corner(UR, buff=0.45)
        val[1].add_updater(lambda m: m.set_value(p2.get_value()))
        with self.say("The memory is written in the roots of the polynomial phi of z. Complex roots make "
                      "the response to a single gust swing, and their distance from the unit circle "
                      "sets how fast the swing dies.") as tr:
            self.play(Create(plane), Create(circ), FadeIn(cl), FadeIn(ttl), Create(ax), FadeIn(al))
            self.add(R, S, val)
            self.fill(tr, 1.5)
        with self.say("More friction pushes the roots out and the memory shortens. Let them cross into "
                      "the circle, and the pendulum stops forgetting: each gust is amplified, and the "
                      "series is no longer stationary.") as tr:
            self.play(p2.animate.set_value(-0.68), run_time=2.5)
            self.wait(0.5)
            self.play(p2.animate.set_value(-1.06), run_time=3.5)
            self.wait(1)
            self.play(p2.animate.set_value(PHI2), run_time=2)
            self.fill(tr, 9.5)

    # ------------------------------------------------------------------ ACF / PACF fingerprints
    def fingerprints(self):
        lags = 10
        models = [("AR(1)", psi_weights(0.7, 0.0, 400), BLUE_),
                  ("MA(1)", np.r_[1.0, 0.7, np.zeros(398)], TEAL_),
                  ("AR(2)", psi_weights(PHI1, PHI2, 400), YELLOW_)]
        cut = {"AR(1)": (None, 1), "MA(1)": (1, None), "AR(2)": (None, 2)}
        cards = VGroup()
        for k, (name, psi, col) in enumerate(models):
            r = acf_from_psi(psi, lags)
            pa = pacf_from_acf(r, lags)
            cx = -4.6 + 4.6 * k
            box = RoundedRectangle(width=4.2, height=6.4, corner_radius=0.2, color=DIM, stroke_width=2).move_to([cx, -0.35, 0])
            nm = T(name, 32, col).move_to([cx, 2.45, 0])
            a1 = Axes(x_range=[0, lags + 0.5, 5], y_range=[-1, 1, 1], x_length=3.5, y_length=2.0, tips=False,
                      axis_config={"color": GREY_}).move_to([cx, 0.9, 0])
            a2 = a1.copy().move_to([cx, -2.05, 0])
            t1 = T("ACF", 24, GREY_).next_to(a1, UP, buff=0.05).align_to(a1, LEFT).shift(RIGHT * 0.2)
            t2 = T("PACF", 24, GREY_).next_to(a2, UP, buff=0.05).align_to(a2, LEFT).shift(RIGHT * 0.2)
            b1 = bars(a1, r[1:], col)
            b2 = bars(a2, pa, col)
            cuts = VGroup()
            for ai, c in zip((a1, a2), cut[name]):
                if c is not None:
                    cuts.add(DashedLine(ai.c2p(c + 0.5, -1), ai.c2p(c + 0.5, 1), color=RED_, dash_length=0.08))
            cards.add(VGroup(box, nm, a1, a2, t1, t2, b1, b2, cuts))
        with self.say("Given only data, how do we tell which machine produced it? We read two "
                      "fingerprints. The autocorrelations of a moving average stop dead after q lags; "
                      "those of an autoregression fade away.") as tr:
            for c in cards:
                self.play(FadeIn(c[:6]), run_time=0.6)
            for c in cards:
                self.play(LaggedStart(*[GrowFromEdge(b, DOWN if b.get_end()[1] >= b.get_start()[1] else UP)
                                        for b in c[6]], lag_ratio=0.1), run_time=1.2)
            self.play(Create(cards[1][8]))
            self.fill(tr, 6)
        with self.say("The partial autocorrelations do the opposite: for an autoregression of order p "
                      "they stop dead after p lags. The swinging pendulum leaves exactly two bars.") as tr:
            for c in cards:
                self.play(LaggedStart(*[GrowFromEdge(b, DOWN if b.get_end()[1] >= b.get_start()[1] else UP)
                                        for b in c[7]], lag_ratio=0.1), run_time=1.0)
            self.play(Create(cards[0][8]), Create(cards[2][8]))
            self.play(Indicate(cards[2][7][:2], color=RED_, scale_factor=1.15))
            self.fill(tr, 5)

    # ------------------------------------------------------------------ the forecast fan
    def fan(self):
        n, H, Tn = 60, 40, 59
        xs, _ = ar2_path(160)
        hist = xs[40:40 + n]
        ax = Axes(x_range=[0, n + H, 10], y_range=[-5, 5, 2.5], x_length=12.4, y_length=5.0, tips=False,
                  axis_config={"color": GREY_}).shift(DOWN * 0.85)
        past = series_path(ax, hist, WHITE_, 3)
        now = DashedLine(ax.c2p(Tn, -5), ax.c2p(Tn, 5), color=GREY_, dash_length=0.1)
        nl = T("today", 26, GREY_).next_to(now, UP, buff=0.1)
        psi = psi_weights(PHI1, PHI2, 400)
        g0 = SIG ** 2 * np.sum(psi ** 2)
        futures = VGroup()
        for b in range(30):
            np.random.seed(2026 + 1 + b)
            e = np.random.normal(0, SIG, H)
            f = [hist[-2], hist[-1]]
            for h in range(H):
                f.append(PHI1 * f[-1] + PHI2 * f[-2] + e[h])
            futures.add(series_path(ax, np.clip(f[1:], -4.9, 4.9), BLUE_, 1.6, x0=Tn).set_stroke(opacity=0.45))
        fc = [hist[-2], hist[-1]]
        for h in range(H):
            fc.append(PHI1 * fc[-1] + PHI2 * fc[-2])
        fc = np.array(fc[1:])
        mse = np.r_[0, SIG ** 2 * np.cumsum(psi[:H] ** 2)]
        up = [ax.c2p(Tn + h, fc[h] + 1.96 * np.sqrt(mse[h])) for h in range(H + 1)]
        lo = [ax.c2p(Tn + h, fc[h] - 1.96 * np.sqrt(mse[h])) for h in range(H + 1)]
        band = Polygon(*up, *lo[::-1], stroke_width=0, fill_color=YELLOW_, fill_opacity=0.18)
        fline = series_path(ax, fc, RED_, 4, x0=Tn)
        ub = 1.96 * np.sqrt(g0)
        unc = VGroup(*[DashedLine(ax.c2p(0, y), ax.c2p(n + H, y), color=PURPLE_, dash_length=0.12) for y in (ub, -ub)])
        ul = MathTex(r"\pm1.96\sqrt{\gamma_0}", font_size=34, color=PURPLE_).next_to(ax.c2p(n + H, ub), UP, buff=0.1).shift(LEFT * 0.9)
        with self.say("Now forecast. Stand at the last observation, and let the pendulum run into the "
                      "future thirty times, each time with fresh gusts.") as tr:
            self.play(Create(ax), Create(past), run_time=2)
            self.play(Create(now), FadeIn(nl))
            self.play(LaggedStart(*[Create(f) for f in futures], lag_ratio=0.08), run_time=4)
            self.fill(tr, 7)
        with self.say("At first the copies swing together: they still remember where the pendulum was "
                      "and how it was moving. Then the gusts pull them apart. Their average, the optimal "
                      "forecast, swings back to the mean and stops there.") as tr:
            self.play(futures.animate.set_stroke(opacity=0.18), Create(fline), run_time=3)
            self.fill(tr, 3)
        mf = MathTex(r"MSE(h)=\sigma^2\sum_{j=0}^{h-1}\psi_j^2\ \longrightarrow\ \gamma_0", font_size=40,
                     color=YELLOW_).to_corner(UL, buff=0.35)
        with self.say("The band around it adds up the squared echoes of the gusts still to come. It "
                      "widens, and then it freezes at the unconditional band. Far enough ahead, the "
                      "future has forgotten the present.") as tr:
            self.play(FadeIn(band), Write(mf), run_time=2)
            self.play(Create(unc), FadeIn(ul))
            self.fill(tr, 3)

    # ------------------------------------------------------------------ closing
    def closing(self):
        s = T("A forecast forgets the present at the speed of the echoes.", 36)
        f1 = MathTex(r"\phi(L)(x_t-\mu)=\theta(L)\,\varepsilon_t,\qquad \psi(L)=\frac{\theta(L)}{\phi(L)}",
                     font_size=42, color=YELLOW_)
        f2 = MathTex(r"\hat x_{T+h|T}\to\mu,\qquad MSE(h)=\sigma^2\sum_{j<h}\psi_j^2\to\gamma_0",
                     font_size=42, color=YELLOW_)
        g = VGroup(s, f1, f2).arrange(DOWN, buff=0.6)
        with self.say("So: an ARMA model is a short recipe for the echoes, a ratio of two small "
                      "polynomials. Its fingerprints tell us the orders, and its forecasts forget the "
                      "present at the speed of its echoes.") as tr:
            self.play(FadeIn(s, shift=UP * 0.2))
            self.play(Write(f1), run_time=1.8)
            self.play(Write(f2), run_time=1.8)
            self.fill(tr, 4.6)
        self.wait(1)
