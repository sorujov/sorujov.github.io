"""Lecture 13 intuition film: Markov switching as hidden weather; the Hamilton filter as a belief needle."""
from common import *
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import norm

SUN = YELLOW_      # expansion state
STORM = RED_       # recession state, and the filtered probability of it


# ---------- data and the Hamilton (1989) fit, 1952Q1-1984Q4 ----------
def _gdp_growth():
    d, g = load_csv("GDPC1.csv")
    x = 100 * np.diff(np.log(g))
    return d[1:], x


def hamilton(th, x, filtered=False):
    m1, m2, r1, r2, ls, a, b = th
    s, p, q = np.exp(ls), expit(a), expit(b)
    P = np.array([[p, 1 - p], [1 - q, q]])
    pr = np.array([(1 - q) / (2 - p - q), (1 - p) / (2 - p - q)])
    ll, out = 0.0, []
    for t in range(1, len(x)):
        f = np.array([norm.pdf(x[t], m1 + r1 * x[t - 1], s), norm.pdf(x[t], m2 + r2 * x[t - 1], s)])
        j = f * pr
        ll += np.log(j.sum())
        post = j / j.sum()
        out.append(post)
        pr = post @ P
    return np.array(out) if filtered else -ll


def fit_hamilton():
    d, x = _gdp_growth()
    i0, i1 = d.index("1951-10-01"), d.index("1984-10-01")
    x, d = x[i0:i1 + 1], d[i0:i1 + 1]
    th = minimize(hamilton, [1, -0.5, 0.3, 0.3, np.log(0.8), 2.2, 0.85], args=(x,), method="BFGS").x
    filt = hamilton(th, x, filtered=True)
    rec = int(np.argmin(th[:2]))
    return d[1:], x[1:], filt[:, rec], th


def yr(date):
    y, m, _ = date.split("-")
    return int(y) + (int(m) - 1) / 12


# ---------- little pictures ----------
def sun_icon(r=0.32):
    core = Circle(radius=r, color=SUN, fill_color=SUN, fill_opacity=1, stroke_width=0)
    rays = VGroup(*[Line(ORIGIN, RIGHT * 0.2, color=SUN, stroke_width=4)
                    .shift(RIGHT * (r + 0.08)).rotate(k * PI / 4, about_point=ORIGIN) for k in range(8)])
    return VGroup(core, rays)


def storm_icon(s=1.0):
    puffs = VGroup(Circle(0.26), Circle(0.34).shift(RIGHT * 0.32 + UP * 0.1), Circle(0.24).shift(RIGHT * 0.66))
    puffs.set_style(fill_color="#8C8C8C", fill_opacity=1, stroke_width=0)
    bolt = Polygon([0.36, -0.2, 0], [0.22, -0.52, 0], [0.34, -0.52, 0], [0.24, -0.82, 0],
                   [0.5, -0.44, 0], [0.38, -0.44, 0], [0.48, -0.2, 0],
                   color=STORM, fill_color=STORM, fill_opacity=1, stroke_width=0)
    return VGroup(bolt, puffs).scale(s).move_to(ORIGIN)


def gauge(center, radius, prob):
    """Semicircular dial: left = expansion (sun), right = recession (storm); needle at prob."""
    arc_bg = Arc(radius=radius, start_angle=0, angle=PI, color=DIM, stroke_width=10).move_arc_center_to(center)
    left = Arc(radius=radius, start_angle=PI / 2, angle=PI / 2, color=SUN, stroke_width=10, stroke_opacity=0.6).move_arc_center_to(center)
    right = Arc(radius=radius, start_angle=0, angle=PI / 2, color=STORM, stroke_width=10, stroke_opacity=0.6).move_arc_center_to(center)
    s = sun_icon(0.18).move_to(center + LEFT * (radius + 0.55) + UP * 0.15)
    c = storm_icon(0.65).move_to(center + RIGHT * (radius + 0.6) + UP * 0.15)
    hub = Dot(center, radius=0.08, color=WHITE_)

    def needle():
        a = PI * (1 - prob.get_value())
        return Line(center, center + radius * 0.9 * np.array([np.cos(a), np.sin(a), 0]), color=WHITE_, stroke_width=6)

    lab = MathTex(r"\Pr(\text{recession})=", font_size=34, color=STORM)
    num = DecimalNumber(prob.get_value(), num_decimal_places=2, font_size=34, color=STORM)
    rd = VGroup(lab, num).arrange(RIGHT, buff=0.12).next_to(hub, DOWN, buff=0.3)
    num.add_updater(lambda m: m.set_value(prob.get_value()))
    return VGroup(arc_bg, left, right, s, c, hub), always_redraw(needle), rd


class Tse13(IntuitionScene):
    parts = ("hook", "machine", "filter", "real", "closing")

    # cold open: the fog of 2008
    def hook(self):
        d, x = _gdp_growth()
        i0 = d.index("2007-01-01")
        ys, ds = x[i0:i0 + 10], d[i0:i0 + 10]
        ax = Axes(x_range=[0, 10, 1], y_range=[-2.5, 1.5, 1], x_length=10, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [-2, -1, 0, 1]}).shift(DOWN * 0.5)
        ylab = T("US real GDP growth, % per quarter", 28, GREY_).to_edge(UP, buff=0.45).align_to(ax, LEFT)
        bars, labs = VGroup(), VGroup()
        for i, (dd, y) in enumerate(zip(ds, ys)):
            b = Rectangle(width=0.62, height=abs(ax.c2p(0, y)[1] - ax.c2p(0, 0)[1]), stroke_width=0,
                          fill_color=WHITE_, fill_opacity=0.85)
            b.move_to(ax.c2p(i + 0.5, y / 2))
            bars.add(b)
            q = (int(dd[5:7]) - 1) // 3 + 1
            labs.add(T(f"{dd[2:4]}Q{q}", 24, GREY_).next_to(ax.c2p(i + 0.5, -2.5), DOWN, buff=0.15))
        fog = Rectangle(width=14.4, height=8.2, stroke_width=0, fill_color=BG, fill_opacity=0.0)
        with self.say("December two thousand and eight. The committee that dates American recessions "
                      "announces that one has begun. It began a year earlier. All year the quarterly numbers "
                      "had argued: a bad quarter, a good one, then worse.") as tr:
            self.play(Create(ax), FadeIn(ylab))
            for b, l in zip(bars, labs):
                self.play(GrowFromEdge(b, DOWN if b.get_center()[1] > ax.c2p(0, 0)[1] else UP), FadeIn(l), run_time=0.45)
            start = ax.c2p(4, 1.5)
            mark = DashedLine(start, ax.c2p(4, -2.5), color=STORM)
            t1 = T("recession begins", 26, STORM).next_to(mark, UP, buff=0.15)
            ann = ax.c2p(8, 1.5)
            mark2 = DashedLine(ann, ax.c2p(8, -2.5), color=BLUE_)
            t2 = T("it is announced", 26, BLUE_).next_to(mark2, UP, buff=0.15)
            self.play(Create(mark), FadeIn(t1))
            self.play(Create(mark2), FadeIn(t2))
            self.fill(tr, 7.5)
        self.add(fog)
        q = T("Nobody announces a recession while you are in it.", 36, YELLOW_).to_edge(DOWN, buff=0.35)
        with self.say("Nobody tells us the state of the economy while we are in it. We have to infer it.") as tr:
            self.play(fog.animate.set_fill(opacity=0.7), FadeIn(q))
            self.fill(tr, 1)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("Hidden weather: Markov switching", 13,
                        "The state of the economy is hidden weather. Today we learn to read it from a thermometer.")

    # the invisible two-state machine
    def machine(self):
        p, q, m1, m2, s = 0.90, 0.70, 1.07, -0.27, 0.88
        box = RoundedRectangle(width=6.0, height=3.2, corner_radius=0.2, color=GREY_).move_to(LEFT * 3.7 + UP * 1.7)
        sun = sun_icon().move_to(box.get_center() + LEFT * 1.75)
        cloud = storm_icon().move_to(box.get_center() + RIGHT * 1.75)
        a12 = CurvedArrow(sun.get_right() + RIGHT * 0.25 + UP * 0.2, cloud.get_left() + LEFT * 0.2 + UP * 0.2, angle=-PI / 3, color=GREY_)
        a21 = CurvedArrow(cloud.get_left() + LEFT * 0.2 + DOWN * 0.2, sun.get_right() + RIGHT * 0.25 + DOWN * 0.2, angle=-PI / 3, color=GREY_)
        l12 = MathTex("1-p", font_size=30, color=GREY_).next_to(a12, UP, buff=0.08)
        l21 = MathTex("1-q", font_size=30, color=GREY_).next_to(a21, DOWN, buff=0.08)
        names = VGroup(T("expansion", 28, SUN).next_to(sun, UP, buff=0.3),
                       T("recession", 28, STORM).next_to(cloud, UP, buff=0.3))
        lp = MathTex(r"\text{stay: }p\approx0.90", font_size=30, color=SUN).next_to(sun, DOWN, buff=0.35)
        lq = MathTex(r"\text{stay: }q\approx0.70", font_size=30, color=STORM).next_to(cloud, DOWN, buff=0.35)
        mach = VGroup(box, sun, cloud, a12, a21, l12, l21, lp, lq, names)
        with self.say("Picture a machine behind a curtain, with two states: expansion and recession. Each "
                      "quarter it stays or switches. From expansion it stays with probability p, about "
                      "nought point nine; from recession with probability q, about nought point seven.") as tr:
            self.play(Create(box), FadeIn(sun, scale=0.5), FadeIn(cloud, scale=0.5), FadeIn(names))
            self.play(Create(a12), Create(a21), FadeIn(l12), FadeIn(l21))
            self.play(FadeIn(lp), FadeIn(lq))
            self.fill(tr, 3)
        dur = MathTex(r"\tfrac{1}{1-p}\approx10\ \text{quarters}", r"\qquad", r"\tfrac{1}{1-q}\approx3\ \text{quarters}",
                      font_size=34).next_to(box, DOWN, buff=0.3)
        dur[0].set_color(SUN); dur[2].set_color(STORM)
        with self.say("So an expansion lasts about ten quarters on average, and a recession about three.") as tr:
            self.play(Write(dur))
            self.fill(tr, 1)

        bax = Axes(x_range=[-3, 4, 1], y_range=[0, 0.5, 0.25], x_length=5.6, y_length=2.6, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, x_axis_config={"numbers_to_include": [-2, 0, 2, 4]}).move_to(RIGHT * 3.75 + UP * 1.6)
        b1 = bax.plot(lambda z: norm.pdf(z, m1, s), x_range=[-3, 4, 0.03], color=SUN, stroke_width=4)
        b2 = bax.plot(lambda z: norm.pdf(z, m2, s), x_range=[-3, 4, 0.03], color=STORM, stroke_width=4)
        bl = T("growth in each state", 24, GREY_).next_to(bax, UP, buff=0.1)
        with self.say("Each state has its own distribution for GDP growth: centred near one percent a "
                      "quarter in expansion, slightly below zero in recession.") as tr:
            self.play(FadeOut(dur), Create(bax), FadeIn(bl))
            self.play(Create(b1), Create(b2))
            self.fill(tr, 2)

        np.random.seed(2026)
        n = 44
        st = [0]
        for _ in range(n - 1):
            st.append(st[-1] if np.random.rand() < (p if st[-1] == 0 else q) else 1 - st[-1])
        ys = np.array([np.random.normal(m1 if k == 0 else m2, s) for k in st])
        sax = Axes(x_range=[0, n, 4], y_range=[-2.5, 3, 1], x_length=12.4, y_length=2.6, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}).move_to(DOWN * 2.3)
        dots = VGroup(*[Dot(sax.c2p(i + 0.5, y), radius=0.07, color=SUN if k == 0 else STORM) for i, (y, k) in enumerate(zip(ys, st))])
        path = series_path(sax, ys, color=GREY_, width=2, x0=0.5)
        ring = Circle(radius=0.62, color=WHITE_, stroke_width=4).move_to(sun)
        with self.say("Let it run. Each quarter the machine hops, then draws one number from the bell of "
                      "its current state.") as tr:
            self.play(Create(sax), Create(ring))
            for i in range(n):
                tgt = sun if st[i] == 0 else cloud
                rt = 0.28 if i < 16 else 0.08
                self.play(ring.animate.move_to(tgt), FadeIn(dots[i], scale=2), run_time=rt)
            self.add(path, dots)
            self.fill(tr, 1.5 + 16 * 0.28 + (n - 16) * 0.08)
        curtain = box.copy().set_style(fill_color=BG, fill_opacity=1, stroke_color=GREY_)
        hid = T("hidden", 40, GREY_).move_to(box)
        with self.say("Now draw the curtain. The colours vanish, and this grey series is all we ever see. "
                      "How far should each number move our belief?") as tr:
            self.play(FadeIn(curtain), FadeOut(ring), Write(hid), dots.animate.set_color(WHITE_), Create(path))
            self.fill(tr, 1)

    # the Hamilton filter as a belief needle
    def filter(self):
        p, q, m1, m2, s = 0.90, 0.70, 1.07, -0.27, 0.88
        ax = Axes(x_range=[-3, 4, 1], y_range=[0, 0.5, 0.25], x_length=7.2, y_length=3.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, x_axis_config={"numbers_to_include": [-2, -1, 0, 1, 2, 3]}).move_to(LEFT * 3.0 + UP * 0.9)
        b1 = ax.plot(lambda z: norm.pdf(z, m1, s), x_range=[-3, 4, 0.03], color=SUN, stroke_width=4)
        b2 = ax.plot(lambda z: norm.pdf(z, m2, s), x_range=[-3, 4, 0.03], color=STORM, stroke_width=4)
        prob = ValueTracker(0.10)
        dial, needle, rd = gauge(RIGHT * 4.0 + UP * 0.6, 1.5, prob)
        with self.say("Hold a belief: a needle between the two states. Before the next quarter, the needle "
                      "relaxes toward the long-run mix, because the weather can change. That is the predict "
                      "step: multiply by the transition matrix.") as tr:
            self.play(Create(ax), Create(b1), Create(b2), FadeIn(dial), FadeIn(needle), FadeIn(rd))
            pred = MathTex(r"\Pr(s_{t}=j\mid I_{t-1})=\sum_i P_{ij}\,\Pr(s_{t-1}=i\mid I_{t-1})", font_size=34, color=BLUE_).to_edge(DOWN, buff=0.45)
            self.play(Write(pred))
            pr = 0.10 * q + 0.90 * (1 - p)
            self.play(prob.animate.set_value(pr), run_time=2)
            self.fill(tr, 5)

        def update(xv, prior):
            f1, f2 = norm.pdf(xv, m1, s), norm.pdf(xv, m2, s)
            w1, w2 = (1 - prior) * f1, prior * f2
            drop = Dot(ax.c2p(xv, 0.62), radius=0.1, color=WHITE_)
            vl = DashedLine(ax.c2p(xv, 0), ax.c2p(xv, 0.48), color=WHITE_, stroke_width=2)
            h1 = Line(ax.c2p(xv, 0), ax.c2p(xv, f1), color=SUN, stroke_width=10).shift(LEFT * 0.07)
            h2 = Line(ax.c2p(xv, 0), ax.c2p(xv, f2), color=STORM, stroke_width=10).shift(RIGHT * 0.07)
            xl = MathTex(rf"x_t={xv:.1f}", font_size=34).next_to(drop, RIGHT if xv > 0 else LEFT, buff=0.15)
            rows = VGroup(
                MathTex(rf"{1-prior:.2f}", r"\times", rf"{f1:.2f}", "=", rf"{w1:.3f}", font_size=32, color=SUN),
                MathTex(rf"{prior:.2f}", r"\times", rf"{f2:.2f}", "=", rf"{w2:.3f}", font_size=32, color=STORM),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 4.0 + DOWN * 1.6)
            hdr = T("prior × height", 24, GREY_).next_to(rows, UP, buff=0.15)
            return drop, vl, h1, h2, xl, rows, hdr, w2 / (w1 + w2)

        prior = prob.get_value()
        drop, vl, h1, h2, xl, rows, hdr, post = update(1.2, prior)
        with self.say("Then a number arrives, and we read the height of each bell at that point. Growth of "
                      "one point two percent is four times more likely under expansion, so the needle swings "
                      "toward the sun.") as tr:
            self.play(FadeIn(drop, shift=DOWN * 0.5), FadeIn(xl))
            self.play(drop.animate.move_to(ax.c2p(1.2, 0)), xl.animate.next_to(ax.c2p(1.2, 0.48), RIGHT, buff=0.1), Create(vl))
            self.play(Create(h1), Create(h2))
            self.play(FadeIn(hdr), FadeIn(rows))
            self.play(prob.animate.set_value(post), run_time=1.5)
            self.fill(tr, 5.5)
        new_prior = post * q + (1 - post) * (1 - p)
        self.play(FadeOut(VGroup(drop, vl, h1, h2, xl, rows, hdr)), prob.animate.set_value(new_prior), run_time=1.2)
        drop, vl, h1, h2, xl, rows, hdr, post = update(-1.0, new_prior)
        bayes = MathTex(r"\Pr(s_t=j\mid I_t)=\frac{f(x_t\mid s_t=j,I_{t-1})\,\Pr(s_t=j\mid I_{t-1})}{\sum_i f(x_t\mid s_t=i,I_{t-1})\,\Pr(s_t=i\mid I_{t-1})}",
                        font_size=32, color=BLUE_).to_edge(DOWN, buff=0.3)
        with self.say("Minus one percent is the opposite case: there the recession bell is far taller. "
                      "Multiply each height by its prior weight, divide by the total, and the needle swings "
                      "past the middle. One bad quarter is strong evidence, not proof. This is Bayes' rule, "
                      "and it is the whole of the Hamilton filter.") as tr:
            self.play(FadeIn(drop, shift=DOWN * 0.5), FadeIn(xl))
            self.play(drop.animate.move_to(ax.c2p(-1.0, 0)), xl.animate.next_to(ax.c2p(-1.0, 0.48), LEFT, buff=0.1), Create(vl))
            self.play(Create(h1), Create(h2))
            self.play(FadeIn(hdr), FadeIn(rows))
            self.play(prob.animate.set_value(post), run_time=1.5)
            self.play(ReplacementTransform(pred, bayes))
            self.fill(tr, 7.5)

    # the real thing: US GDP 1952-1984 against NBER recessions
    def real(self):
        d, x, pr, th = fit_hamilton()
        tx = np.array([yr(z) + 1.5 / 12 for z in d])
        top = Axes(x_range=[1952, 1985, 5], y_range=[-3, 4, 1], x_length=12.6, y_length=2.7, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [-2, 0, 2]}).move_to(UP * 1.55 + RIGHT * 0.2)
        bot = Axes(x_range=[1952, 1985, 5], y_range=[0, 1, 0.5], x_length=12.6, y_length=2.3, tips=False,
                   axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [0, 0.5, 1]},
                   x_axis_config={"numbers_to_include": list(range(1955, 1986, 5)), "decimal_number_config": {"group_with_commas": False, "num_decimal_places": 0}}).move_to(DOWN * 1.75 + RIGHT * 0.2)
        ud, uv = load_csv("USREC.csv")
        shades = VGroup()
        y_hi, y_lo = top.c2p(0, 4)[1], bot.c2p(0, 0)[1]
        for z, v in zip(ud, uv):
            t0 = yr(z)
            if v == 1 and 1952 <= t0 < 1985:
                xa, xb = top.c2p(t0, 0)[0], top.c2p(t0 + 1 / 12, 0)[0]
                shades.add(Rectangle(width=xb - xa + 0.005, height=y_hi - y_lo, stroke_width=0, fill_color=GREY_,
                                     fill_opacity=0.35).move_to([(xa + xb) / 2, (y_hi + y_lo) / 2, 0]))
        bars = VGroup()
        for t, y in zip(tx, x):
            h = abs(top.c2p(0, y)[1] - top.c2p(0, 0)[1])
            bars.add(Rectangle(width=0.06, height=max(h, 0.01), stroke_width=0, fill_color=WHITE_, fill_opacity=0.85)
                     .move_to(top.c2p(t, y / 2)))
        l1 = T("US real GDP growth, % per quarter", 24, WHITE_).next_to(top, UP, buff=0.12).align_to(top, LEFT)
        l2 = T("NBER recessions", 24, GREY_).next_to(top, UP, buff=0.12).align_to(top, RIGHT)
        l3 = MathTex(r"\Pr(\text{recession}\mid \text{data up to } t)", font_size=30, color=STORM).next_to(bot, UP, buff=0.12).align_to(bot, LEFT)
        with self.say("Now the real thing: quarterly US GDP growth from nineteen fifty-two to nineteen "
                      "eighty-four, Hamilton's sample, with the official recessions shaded in grey. We fit the "
                      "model by maximum likelihood and run the filter forward, one quarter at a time, never "
                      "looking ahead.") as tr:
            self.play(FadeIn(shades), Create(top), Create(bot), FadeIn(l1), FadeIn(l2))
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.02), run_time=3)
            self.play(FadeIn(l3))
            self.fill(tr, 5.5)
        k = ValueTracker(0)
        pts = [bot.c2p(t, v) for t, v in zip(tx, pr)]

        def line():
            n = max(2, int(k.get_value()) + 1)
            return VMobject(color=STORM, stroke_width=4).set_points_as_corners(pts[:n])

        def cursor():
            i = min(int(k.get_value()), len(tx) - 1)
            return Line([pts[i][0], y_lo, 0], [pts[i][0], y_hi, 0], color=STORM, stroke_width=2, stroke_opacity=0.6)

        lm, cm = always_redraw(line), always_redraw(cursor)
        with self.say("Watch the red line. It finds every recession in the sample, usually within a "
                      "quarter, from GDP alone. It was never told the committee's dates; it only reads the "
                      "thermometer.") as tr:
            self.add(lm, cm)
            self.play(k.animate.set_value(len(tx) - 1), run_time=9, rate_func=linear)
            self.remove(cm)
            self.fill(tr, 9)
        est = MathTex(rf"\hat\mu_{{\text{{rec}}}}={th[1]:.2f}", r",\quad", rf"\hat p={expit(th[5]):.2f}", r",\quad", rf"\hat q={expit(th[6]):.2f}",
                      font_size=32).to_edge(DOWN, buff=0.3)
        est[0].set_color(STORM); est[2].set_color(SUN); est[4].set_color(STORM)
        with self.say("After nineteen eighty-four the economy grew calmer, and the model then needs a "
                      "separate variance for each state. The idea does not change.") as tr:
            self.play(FadeIn(est))
            self.fill(tr, 1)

    def closing(self):
        a = T("The regime is hidden, but every observation is evidence.", 36, YELLOW_)
        f1 = MathTex(r"\text{predict:}\quad \Pr(s_{t}\mid I_{t-1})=P'\,\Pr(s_{t-1}\mid I_{t-1})", font_size=38, color=BLUE_)
        f2 = MathTex(r"\text{update:}\quad \Pr(s_t=j\mid I_t)\ \propto\ f(x_t\mid s_t=j,I_{t-1})\,\Pr(s_t=j\mid I_{t-1})", font_size=38, color=STORM)
        g = VGroup(a, f1, f2).arrange(DOWN, buff=0.7)
        with self.say("So: the regime is hidden, but every observation is evidence. Predict with the "
                      "transition matrix, update with Bayes' rule, and the filtered probability tells us, in "
                      "real time, how likely it is that we are already in the storm.") as tr:
            self.play(FadeIn(a, shift=UP * 0.2))
            self.play(Write(f1))
            self.play(Write(f2))
            self.fill(tr, 4)
