"""Lecture 4 intuition film: one tomorrow, many lenses (objects of modelling) and the AIC/BIC tug of war."""
from common import *
from scipy.stats import norm, gamma, chi2


def glow(path, color, width=3):
    halo = path.copy().set_stroke(color, width=width * 4, opacity=0.18)
    return VGroup(halo, path.set_stroke(color, width=width))


class Tse4(IntuitionScene):
    parts = ("cold_open", "riding_density", "lenses", "tug_of_war", "closing")

    # ------------------------------------------------------------------ cold open
    def cold_open(self):
        dates, v = load_csv("UNRATE.csv")
        keep = [i for i, d in enumerate(dates) if "1990-01" <= d[:7] <= "2019-12"]
        ys = v[keep]
        ax = Axes(x_range=[0, len(ys) + 14, 60], y_range=[2, 11, 2], x_length=8.6, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  y_axis_config={"numbers_to_include": [4, 6, 8, 10]}).shift(LEFT * 2.3 + DOWN * 0.4)
        yrs = VGroup(*[T(str(1990 + 10 * k), 24, GREY_).next_to(ax.c2p(120 * k, 2), DOWN, buff=0.2) for k in range(3)])
        lab = T("US unemployment rate, %", 28, GREY_).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        line = glow(series_path(ax, ys, BLUE_, 3), BLUE_)
        now = ax.c2p(len(ys) - 1, ys[-1])
        nxt = ax.c2p(len(ys) + 8, ys[-1])
        q = T("?", 56, YELLOW_).move_to(nxt)
        with self.say("Here is the US unemployment rate. Three people ask what it will do next month.") as tr:
            self.play(Create(ax), FadeIn(yrs), FadeIn(lab))
            self.play(Create(line), run_time=3)
            self.play(FadeIn(q, scale=1.6))
            self.fill(tr, 4.5)
        who = VGroup(
            VGroup(T("economist", 28, YELLOW_), T("the expected value", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.12),
            VGroup(T("risk manager", 28, RED_), T("how large a jump is possible", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.12),
            VGroup(T("trader", 28, GREEN_), T("the probability of a rise", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.12),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.3)
        arrows = VGroup(*[Arrow(q.get_right() + RIGHT * 0.05, w.get_left() + LEFT * 0.1, buff=0.1, stroke_width=3,
                                color=w[0].get_color(), max_tip_length_to_length_ratio=0.12) for w in who])
        with self.say("The economist wants its expected value. The risk manager wants to know how large a "
                      "jump is possible. The trader wants the probability that it rises at all. Three "
                      "different answers, and none of them is wrong.") as tr:
            for a, w in zip(arrows, who):
                self.play(GrowArrow(a), FadeIn(w, shift=RIGHT * 0.2), run_time=1.2)
                self.wait(1.2)
            self.fill(tr, 7.2)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("One tomorrow, many lenses", 4,
                        "They are looking at one object through different lenses: the distribution of "
                        "tomorrow, given today.")

    # ------------------------------------------------------------- riding density
    def riding_density(self):
        np.random.seed(2026)
        n = 112
        x, e, s2 = np.zeros(n), np.zeros(n), np.full(n, 0.5)
        for t in range(1, n):
            s2[t] = 0.25 + 0.7 * e[t - 1] ** 2
            e[t] = np.sqrt(s2[t]) * np.random.randn()
            x[t] = 0.3 * x[t - 1] + e[t]
        x = np.clip(x, -5.5, 5.5)
        ax = Axes(x_range=[0, 120, 20], y_range=[-6, 6, 2], x_length=11.6, y_length=5.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}).shift(DOWN * 0.45)
        tt = ValueTracker(12)

        def cond(t):
            i = int(t)
            mu = 0.3 * x[i]
            sg = np.sqrt(0.25 + 0.7 * e[i] ** 2)
            return mu, sg

        def path():
            i = int(tt.get_value())
            return series_path(ax, x[:i + 1], BLUE_, 3)

        def density():
            i = int(tt.get_value())
            mu, sg = cond(i)
            x0 = ax.c2p(i + 1.5, 0)[0]
            ys = np.linspace(mu - 4 * sg, mu + 4 * sg, 120)
            ys = ys[(ys > -6) & (ys < 6)]
            pts = [np.array([x0 + 1.9 * norm.pdf(y, mu, sg), ax.c2p(0, y)[1], 0]) for y in ys]
            curve = VMobject(color=WHITE_, stroke_width=3).set_points_smoothly(pts)
            q = mu - 1.645 * sg
            tail_y = [y for y in ys if y <= q]
            g = VGroup(curve)
            if len(tail_y) > 2:
                tp = [np.array([x0, ax.c2p(0, tail_y[0])[1], 0])] + \
                     [np.array([x0 + 1.9 * norm.pdf(y, mu, sg), ax.c2p(0, y)[1], 0]) for y in tail_y] + \
                     [np.array([x0, ax.c2p(0, tail_y[-1])[1], 0])]
                g.add(Polygon(*tp, stroke_width=0, fill_color=RED_, fill_opacity=0.6))
            base = Line([x0, ax.c2p(0, ys[0])[1], 0], [x0, ax.c2p(0, ys[-1])[1], 0], color=GREY_, stroke_width=2)
            mline = Line([x0 - 0.15, ax.c2p(0, mu)[1], 0], [x0 + 2.1, ax.c2p(0, mu)[1], 0], color=YELLOW_, stroke_width=5)
            qline = Line([x0 - 0.15, ax.c2p(0, max(q, -6))[1], 0], [x0 + 1.2, ax.c2p(0, max(q, -6))[1], 0], color=RED_, stroke_width=5)
            return VGroup(base, g, mline, qline)

        p = always_redraw(path)
        d = always_redraw(density)
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=YELLOW_, stroke_width=5), T("conditional mean", 26, YELLOW_)).arrange(RIGHT, buff=0.2),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=RED_, stroke_width=5), T("5% quantile", 26, RED_)).arrange(RIGHT, buff=0.2),
        ).arrange(RIGHT, buff=0.7).to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.6)
        fx = MathTex(r"f(x_{t+1}\mid x_t, x_{t-1},\dots)", font_size=36).to_edge(UP, buff=0.35).to_edge(RIGHT, buff=0.5)
        with self.say("Let us make that object visible. At each date, the distribution of the next value, "
                      "given the past, is a density riding just ahead of the path.") as tr:
            self.play(Create(ax), FadeIn(fx))
            self.add(p, d)
            self.play(tt.animate.set_value(40), run_time=4, rate_func=linear)
            self.fill(tr, 5)
        with self.say("Its centre, the conditional mean, hardly moves. Its five percent quantile, in red, "
                      "plunges every time the series turns turbulent, and recovers when it calms. Same "
                      "mean, very different risk.") as tr:
            self.play(FadeIn(leg))
            self.play(tt.animate.set_value(108), run_time=tr.duration - 1.5, rate_func=linear)

    # --------------------------------------------------------------------- lenses
    def lenses(self):
        k = 2.0
        top = Axes(x_range=[0, 9, 1], y_range=[0, 0.42, 0.1], x_length=11, y_length=2.6, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"include_ticks": False}).shift(UP * 1.75)
        bot = Axes(x_range=[0, 9, 1], y_range=[0, 1.05, 0.5], x_length=11, y_length=2.4, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"include_ticks": False}).shift(DOWN * 2.05)
        dens = top.plot(lambda u: gamma.pdf(u, k), x_range=[0.01, 9], color=WHITE_, stroke_width=4)
        area = top.get_area(dens, x_range=[0.01, 9], color=BLUE_, opacity=0.18)
        tl = T("tomorrow's distribution", 26, GREY_).next_to(top, UP, buff=0.1).align_to(top, RIGHT)
        bl = T("expected loss of guess m", 26, GREY_).next_to(bot, UP, buff=0.1).align_to(bot, RIGHT)
        grid = np.linspace(0.01, 12, 3000)
        w = gamma.pdf(grid, k) * (grid[1] - grid[0])
        ms = np.linspace(0.05, 8.8, 300)

        def curve_of(loss):
            L = np.array([np.sum(w * loss(grid - m)) for m in ms])
            L = 0.05 + 0.95 * (L - L.min()) / (L.max() - L.min())
            return L

        a = 0.05
        losses = [
            (lambda u: u ** 2, YELLOW_, r"(x-m)^2", "mean", gamma.mean(k)),
            (lambda u: np.abs(u), TEAL_, r"|x-m|", "median", gamma.median(k)),
            (lambda u: u * (a - (u < 0)), RED_, r"\rho_{0.05}(x-m)", "5% quantile", gamma.ppf(a, k)),
        ]
        mt = ValueTracker(0.05)

        def build(i):
            loss, col, tex, name, target = losses[i]
            L = curve_of(loss)
            mt.set_value(ms[0])
            o = {"lab": MathTex(r"E\," + tex, font_size=40, color=col).move_to(bot.c2p(2.2, 0.8))}

            def traced():
                j = max(int(np.searchsorted(ms, mt.get_value())), 2)
                return VMobject(color=col, stroke_width=4).set_points_smoothly([bot.c2p(m, y) for m, y in zip(ms[:j], L[:j])])

            o["cur"] = always_redraw(traced)
            o["vline"] = always_redraw(lambda: DashedLine(top.c2p(mt.get_value(), 0), top.c2p(mt.get_value(), 0.4), color=col, stroke_width=2))
            o["dot"] = always_redraw(lambda: Dot(bot.c2p(mt.get_value(), np.interp(mt.get_value(), ms, L)), color=col, radius=0.08))
            j0 = int(np.argmin(L))
            mk = VGroup(Line(top.c2p(ms[j0], 0), top.c2p(ms[j0], gamma.pdf(ms[j0], k)), color=col, stroke_width=5),
                        VGroup(Line(ORIGIN, RIGHT * 0.45, color=col, stroke_width=5), T(name, 26, col)).arrange(RIGHT, buff=0.15)
                        .move_to(top.c2p(5.6, 0.34 - 0.075 * i), aligned_edge=LEFT))
            o["mk"] = mk
            o["drop"] = DashedLine(bot.c2p(ms[j0], L[j0]), top.c2p(ms[j0], 0), color=col, stroke_width=2)
            return o

        def sweep(o, rt):
            self.play(Write(o["lab"]), run_time=0.8)
            self.add(o["cur"], o["vline"], o["dot"])
            self.play(mt.animate.set_value(8.7), run_time=rt, rate_func=linear)

        def land(o):
            self.play(Create(o["drop"]), FadeIn(o["mk"]))

        def clear(o):
            self.remove(o["vline"], o["dot"])
            stat = o["cur"].copy().clear_updaters()
            self.remove(o["cur"])
            self.add(stat)
            self.play(FadeOut(stat), FadeOut(o["lab"]), FadeOut(o["drop"]), run_time=0.6)

        o = build(0)
        with self.say("The forecast is not a number, it is a whole distribution, and each target is a lens "
                      "on it. Slide a guess m along the axis and record the expected squared error.") as tr:
            self.play(Create(top), Create(dens), FadeIn(area), FadeIn(tl))
            self.play(Create(bot), FadeIn(bl))
            sweep(o, max(tr.duration - 4, 3))
        with self.say("The lowest point sits exactly at the mean. That is why the conditional mean is the "
                      "forecast that minimises the mean squared prediction error.") as tr:
            land(o)
            self.fill(tr, 1)
        clear(o)
        o = build(1)
        with self.say("Change the loss to the absolute error, and the lowest point moves to the median.") as tr:
            sweep(o, 3.5)
            land(o)
            self.fill(tr, 5.3)
        clear(o)
        o = build(2)
        with self.say("Make over-prediction nineteen times as costly as under-prediction, the check loss, and "
                      "the lowest point slides down to the five percent quantile: the value at risk.") as tr:
            sweep(o, 3.5)
            land(o)
            self.fill(tr, 5.3)
        clear(o)
        mu = gamma.mean(k)
        sd = np.sqrt(gamma.var(k))
        yb = -0.06
        br = VGroup(Line(top.c2p(mu - sd, yb), top.c2p(mu + sd, yb), color=BLUE_, stroke_width=5),
                    Line(top.c2p(mu - sd, yb - 0.025), top.c2p(mu - sd, yb + 0.025), color=BLUE_, stroke_width=5),
                    Line(top.c2p(mu + sd, yb - 0.025), top.c2p(mu + sd, yb + 0.025), color=BLUE_, stroke_width=5))
        brl = T("spread: the variance", 26, BLUE_).next_to(br, RIGHT, buff=0.3)
        msg = MathTex(r"\text{each object} = \arg\min_m\; E_{t-1}\,L(x_t - m)", font_size=42).move_to(bot.get_center() + UP * 0.25)
        with self.say("And the variance measures the spread. Each object is the best forecast under its own "
                      "loss. Choosing the object means choosing the loss.") as tr:
            self.play(Create(br), FadeIn(brl))
            self.play(FadeOut(bot), FadeOut(bl), Write(msg))
            self.fill(tr, 3)

    # ---------------------------------------------------------------- tug of war
    def tug_of_war(self):
        ic = MathTex(r"IC(k)", r"=", r"T\log\hat\sigma^2_k", r"+", r"f(k)", font_size=48)
        ic[2].set_color(GREEN_)
        ic[4].set_color(RED_)
        ic.to_edge(UP, buff=0.45)
        b1 = Brace(ic[2], DOWN, color=GREEN_)
        b2 = Brace(ic[4], DOWN, color=RED_)
        t1 = T("fit: falls with every lag", 26, GREEN_).next_to(b1, DOWN, buff=0.1).shift(LEFT * 1.1)
        t2 = T("penalty: rises", 26, RED_).next_to(b2, DOWN, buff=0.1).shift(RIGHT * 0.9)
        with self.say("Now the second question of the lecture: how many lags? Every information criterion "
                      "is a tug of war. Fit pulls towards more lags, the penalty pulls back.") as tr:
            self.play(Write(ic))
            self.play(GrowFromCenter(b1), FadeIn(t1), GrowFromCenter(b2), FadeIn(t2))
            self.fill(tr, 3)
        self.play(FadeOut(VGroup(b1, b2, t1, t2)))

        price = ValueTracker(2.0)
        # rope
        y0 = 1.35
        knot_x = ValueTracker(0)
        rope = always_redraw(lambda: Line(LEFT * 5 + UP * y0, RIGHT * 5 + UP * y0, color=GREY_,
                                          stroke_width=4 + 0.8 * (price.get_value() - 2)))
        knot = always_redraw(lambda: Dot(RIGHT * knot_x.get_value() + UP * y0, radius=0.13, color=WHITE_))
        mid = DashedLine(UP * (y0 + 0.5), UP * (y0 - 0.5), color=GREY_, stroke_width=2)
        pull_fit = Arrow(RIGHT * 2.2 + UP * y0, RIGHT * 3.6 + UP * y0, buff=0, color=GREEN_, stroke_width=8)
        fl = T("fit gain of a useless lag", 26, GREEN_).next_to(pull_fit, UP, buff=0.15)
        pull_pen = always_redraw(lambda: Arrow(LEFT * 2.2 + UP * y0, LEFT * (2.2 + 0.9 * np.sqrt(price.get_value())) + UP * y0,
                                               buff=0, color=RED_, stroke_width=8 + 0.6 * (price.get_value() - 2),
                                               max_tip_length_to_length_ratio=0.35))
        pl = always_redraw(lambda: T("price per lag", 26, RED_).next_to(LEFT * 3.4 + UP * y0, UP, buff=0.3))
        # chi-square picture
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 0.8, 0.4], x_length=11, y_length=2.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [0, 2, 4, 6, 8, 10, 12]}, y_axis_config={"include_ticks": False}).shift(DOWN * 2.2)
        c = ax.plot(lambda u: chi2.pdf(u, 1), x_range=[0.25, 12], color=GREEN_, stroke_width=4)
        cl = MathTex(r"\chi^2_1", font_size=38, color=GREEN_).move_to(ax.c2p(1.0, 0.65))
        tail = always_redraw(lambda: ax.get_area(c, x_range=[price.get_value(), 12], color=RED_, opacity=0.65))
        bar = always_redraw(lambda: Line(ax.c2p(price.get_value(), 0), ax.c2p(price.get_value(), 0.72), color=RED_, stroke_width=5))
        prob = always_redraw(lambda: T(f"P(useless lag kept) = {1 - chi2.cdf(price.get_value(), 1):.3f}", 28, RED_).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.15))
        with self.say("Suppose the extra lag is useless. Its gain in fit is still random: a chi-square with "
                      "one degree of freedom. That is the strength of the green team.") as tr:
            self.play(Create(rope), FadeIn(knot), Create(mid))
            self.play(GrowArrow(pull_fit), FadeIn(fl))
            self.play(Create(ax), Create(c), FadeIn(cl))
            self.fill(tr, 4)
        aic = T("AIC:  price 2", 28, RED_).to_edge(LEFT, buff=0.5).shift(DOWN * 0.15)
        with self.say("Akaike charges a price of two per lag. The useless lag wins the tug whenever its gain "
                      "exceeds two, which happens about sixteen percent of the time, at every sample size.") as tr:
            self.play(FadeIn(pull_pen), FadeIn(pl), FadeIn(aic))
            self.play(FadeIn(tail), Create(bar), Write(prob))
            for _ in range(2):
                self.play(knot_x.animate.set_value(0.5), run_time=0.5)
                self.play(knot_x.animate.set_value(-0.3), run_time=0.5)
            self.play(knot_x.animate.set_value(0), run_time=0.4)
            self.fill(tr, 4.4)
        bic = always_redraw(lambda: T(f"BIC:  log T = {price.get_value():.2f}  (T = {np.exp(price.get_value()):,.0f})", 28, RED_).to_edge(LEFT, buff=0.5).shift(DOWN * 0.15))
        with self.say("Schwarz charges log T. As the sample grows, his rope gets thicker, the red line "
                      "moves right, and the chance of keeping a useless lag shrinks towards zero. That is "
                      "why BIC is consistent, and AIC is not.") as tr:
            self.play(FadeOut(aic), price.animate.set_value(np.log(100)), run_time=1.5)
            self.add(bic)
            self.play(price.animate.set_value(np.log(100000)), knot_x.animate.set_value(-1.2), run_time=6, rate_func=smooth)
            self.fill(tr, 7.5)

    # -------------------------------------------------------------------- closing
    def closing(self):
        g = VGroup(
            VGroup(T("the forecast is a distribution;", 36, YELLOW_), T("the loss chooses the lens", 36, YELLOW_)).arrange(DOWN, buff=0.15),
            MathTex(r"\hat x_{t} = \arg\min_m\, E_{t-1}\,L(x_t - m)", font_size=44),
            VGroup(T("lags are a tug of war: fit against price", 36, GREEN_)).arrange(DOWN),
            MathTex(r"IC(k) = -2\log\hat{\mathcal L}_k + f(k),\qquad f_{AIC}=2k,\ \ f_{BIC}=k\log T", font_size=40),
        ).arrange(DOWN, buff=0.45)
        with self.say("So: tomorrow is a distribution, and the loss you care about decides which feature of "
                      "it to forecast. And the number of lags is settled by a tug of war, in which only a "
                      "price that grows with the sample keeps the useless ones out.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=UP * 0.2))
                self.wait(0.7)
            self.fill(tr, 6)
