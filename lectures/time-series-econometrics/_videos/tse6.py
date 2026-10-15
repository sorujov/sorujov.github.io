"""Lecture 6 intuition film: monkeys at the stock exchange (data snooping, Reality Check / SPA, model confidence set)."""
from common import *
from scipy.stats import norm

GOLD = "#F7B733"
FUR = "#8B5A2B"
SKIN = "#E3C29B"


def monkey(r=0.17):
    head = Circle(r, fill_color=FUR, fill_opacity=1, stroke_width=0)
    ears = VGroup(*[Circle(r * 0.42, fill_color=FUR, fill_opacity=1, stroke_width=0).move_to(head.get_center() + s * RIGHT * r * 1.0 + UP * r * 0.25)
                    for s in (-1, 1)])
    inner = VGroup(*[Circle(r * 0.24, fill_color=SKIN, fill_opacity=1, stroke_width=0).move_to(e) for e in ears])
    face = Ellipse(width=r * 1.35, height=r * 1.05, fill_color=SKIN, fill_opacity=1, stroke_width=0).shift(DOWN * r * 0.2)
    eyes = VGroup(*[Dot(radius=r * 0.12, color=BG).move_to(s * RIGHT * r * 0.28 + UP * r * 0.08) for s in (-1, 1)])
    mouth = Arc(radius=r * 0.3, start_angle=-PI * 0.8, angle=PI * 0.6, color=BG, stroke_width=1.5).shift(DOWN * r * 0.15)
    return VGroup(ears, inner, head, face, eyes, mouth)


def crown(w=0.34):
    pts = [[-w / 2, 0, 0], [w / 2, 0, 0], [w / 2, w * 0.55, 0], [w / 4, w * 0.25, 0], [0, w * 0.6, 0],
           [-w / 4, w * 0.25, 0], [-w / 2, w * 0.55, 0]]
    return Polygon(*pts, fill_color=GOLD, fill_opacity=1, stroke_width=0)


class Tse6(IntuitionScene):
    parts = ("cold_open", "galton", "best_of_m", "bootstrap", "tournament", "closing")

    def setup(self):
        super().setup()
        dates, v = load_csv("SP500.csv")
        r = np.diff(np.log(v))[-500:] * 100
        np.random.seed(2026)
        S = np.random.choice([-1, 1], (500, 100))
        self.X = S * r[:, None]
        self.tstat = np.sqrt(500) * self.X.mean(0) / self.X.std(0, ddof=1)
        self.best = int(np.argmax(self.tstat))

    # ------------------------------------------------------------------ cold open
    def cold_open(self):
        X, t, best = self.X, self.tstat, self.best
        grid = VGroup(*[monkey() for _ in range(100)]).arrange_in_grid(10, 10, buff=0.16).move_to(LEFT * 3.9 + DOWN * 0.3)
        self.grid = grid
        lab = T("100 monkeys, one coin each per day: buy or sell", 28, GREY_).to_edge(UP, buff=0.4)
        with self.say("A hundred monkeys at the stock exchange. Every day, each monkey flips a coin: buy the "
                      "S and P 500, or sell it.") as tr:
            self.play(FadeIn(lab))
            self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in grid], lag_ratio=0.02), run_time=3)
            self.fill(tr, 4)
        cum = np.cumsum(X, axis=0)
        ax = Axes(x_range=[0, 500, 100], y_range=[-80, 80, 40], x_length=5.6, y_length=5.0, tips=False,
                  axis_config={"color": GREY_, "font_size": 24}, y_axis_config={"numbers_to_include": [-80, -40, 0, 40, 80]}).move_to(RIGHT * 3.6 + DOWN * 0.3)
        yl = T("cumulative return, %", 24, GREY_).next_to(ax, UP, buff=0.1)
        xl = T("500 trading days", 24, GREY_).next_to(ax, DOWN, buff=0.15)
        paths = VGroup(*[VMobject(stroke_width=1.5, color=GREY_ if j != best else GOLD, stroke_opacity=0.55).set_points_as_corners(
            [ax.c2p(4 * i, y) for i, y in enumerate(np.clip(cum[::4, j], -80, 80))]) for j in range(100)])
        star = paths[best].copy().set_stroke(GOLD, 4)
        halo = paths[best].copy().set_stroke(GOLD, 12, opacity=0.25)
        with self.say("Five hundred trading days later, on real S and P data, here are their fortunes.") as tr:
            self.play(Create(ax), FadeIn(yl), FadeIn(xl))
            self.play(LaggedStart(*[Create(p) for p in paths], lag_ratio=0.01), run_time=3)
            self.fill(tr, 4)
        cr = crown().next_to(grid[best], UP, buff=-0.02)
        glowm = Circle(0.3, color=GOLD, stroke_width=4).move_to(grid[best])
        info = MathTex(rf"t = {t[best]:.2f},\quad p = {1 - norm.cdf(t[best]):.3f}", font_size=38, color=GOLD).next_to(ax, UP, buff=0.5).shift(LEFT * 0.4)
        with self.say("One of them has earned a t-statistic of two point eight. Taken alone, that is a "
                      "p-value of three in a thousand. Is this monkey a genius?") as tr:
            self.play(FadeOut(lab), Create(halo), Create(star), run_time=1.5)
            self.play(FadeIn(cr, shift=DOWN * 0.2), Create(glowm), Write(info))
            self.fill(tr, 3.5)
        self.play(FadeOut(Group(*self.mobjects)))
        self.title_card("Monkeys at the stock exchange", 6,
                        "The question is not whether the best monkey looks good. It is whether the best of a "
                        "hundred monkeys would look this good anyway.")

    # --------------------------------------------------------------------- galton
    def galton(self):
        t, best = self.tstat, self.best
        grid = self.grid.copy()
        ax = Axes(x_range=[-3.5, 3.5, 1], y_range=[0, 16, 4], x_length=7.6, y_length=4.6, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": [-3, -2, -1, 0, 1, 2, 3]}, y_axis_config={"include_ticks": False}).move_to(RIGHT * 2.5 + DOWN * 0.4)
        grid.scale(0.8).to_edge(LEFT, buff=0.4).shift(DOWN * 0.3)
        xl = T("t-statistic of each monkey", 26, GREY_).next_to(ax, DOWN, buff=0.15)
        self.play(FadeIn(grid))
        self.play(Create(ax), FadeIn(xl))
        bw = 0.25
        h = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        count = {}
        anims = []
        order = np.argsort(t)
        for j in order:
            b = int(np.floor(t[j] / bw))
            k = count.get(b, 0)
            count[b] = k + 1
            pos = ax.c2p((b + 0.5) * bw, 0) + UP * h * (k + 0.5)
            sq = Square(side_length=min(h, ax.c2p(bw, 0)[0] - ax.c2p(0, 0)[0]) * 0.9, stroke_width=0,
                        fill_color=GOLD if j == best else BLUE_, fill_opacity=0.9).move_to(pos)
            anims.append(Transform(grid[j], sq))
        bell = ax.plot(lambda u: 100 * bw * norm.pdf(u), x_range=[-3.5, 3.5], color=WHITE_, stroke_width=3)
        c = DashedLine(ax.c2p(1.645, 0), ax.c2p(1.645, 15), color=RED_, stroke_width=3)
        cl = MathTex("1.645", font_size=32, color=RED_).next_to(c, UP, buff=0.08)
        n_over = int((t > 1.645).sum())
        nl = T(f"{n_over} clear it", 26, RED_).next_to(ax.c2p(1.645, 12.5), RIGHT, buff=0.15)
        with self.say("Turn each monkey into its t-statistic. They pile up into the bell curve of no skill, "
                      "exactly as chance predicts. A handful clear one point six four five, the usual five "
                      "percent bar. The best one clears it easily.") as tr:
            self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=5)
            self.play(Create(bell))
            self.play(Create(c), FadeIn(cl), FadeIn(nl))
            self.fill(tr, 7.5)

    # ------------------------------------------------------------------ best of m
    def best_of_m(self):
        ax = Axes(x_range=[-3.5, 5, 1], y_range=[0, 1.4, 0.5], x_length=11, y_length=4.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": range(-3, 6)}, y_axis_config={"include_ticks": False}).shift(DOWN * 1.0)
        m = ValueTracker(1)
        one = ax.plot(norm.pdf, x_range=[-3.5, 5], color=BLUE_, stroke_width=4)
        ol = T("one monkey", 26, BLUE_).move_to(ax.c2p(-2.3, 0.5))
        best = always_redraw(lambda: ax.plot(lambda u: m.get_value() * norm.pdf(u) * norm.cdf(u) ** (m.get_value() - 1),
                                             x_range=[-3.5, 5, 0.02], color=RED_, stroke_width=4))
        area = always_redraw(lambda: ax.get_area(ax.plot(lambda u: m.get_value() * norm.pdf(u) * norm.cdf(u) ** (m.get_value() - 1),
                                                         x_range=[1.645, 5, 0.02]), x_range=[1.645, 5], color=RED_, opacity=0.3))
        c = DashedLine(ax.c2p(1.645, 0), ax.c2p(1.645, 1.35), color=GREY_, stroke_width=3)
        cl = MathTex("1.645", font_size=30, color=GREY_).next_to(ax.c2p(1.645, 0), DOWN, buff=0.5)
        f = MathTex(r"\Pr\big(\max_j t_j > c\big) = 1-\Phi(c)^m", font_size=44).to_edge(UP, buff=0.4).to_edge(LEFT, buff=0.6)
        ro = always_redraw(lambda: T(f"m = {int(round(m.get_value()))},   P(best > 1.645) = {1 - 0.95 ** round(m.get_value()):.3f}", 32, RED_).next_to(f, DOWN, buff=0.3).align_to(f, LEFT))
        with self.say("Here is why. One monkey's t-statistic is standard normal: it clears one point six "
                      "four five five percent of the time. The best of m monkeys has its own distribution, "
                      "in red, and as m grows it slides to the right.") as tr:
            self.play(Create(ax), Create(one), FadeIn(ol), Create(c), FadeIn(cl), Write(f))
            self.add(area, best, ro)
            self.wait(1)
            self.play(m.animate.set_value(100), run_time=tr.duration - 4, rate_func=lambda s: s ** 2.2)
        hc = DashedLine(ax.c2p(3.28, 0), ax.c2p(3.28, 1.35), color=GOLD, stroke_width=4)
        hl = MathTex(r"3.28", font_size=32, color=GOLD).next_to(ax.c2p(3.28, 0), DOWN, buff=0.5)
        hn = VGroup(T("the honest bar", 26, GOLD), T("for the best of 100", 26, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(ax.c2p(3.35, 1.15), RIGHT, buff=0.1)
        with self.say("With a hundred monkeys, the best one clears the usual bar ninety-nine times in a "
                      "hundred. The honest five percent bar for the best of a hundred independent monkeys is "
                      "three point two eight.") as tr:
            self.play(Create(hc), FadeIn(hl), FadeIn(hn))
            self.fill(tr, 1)

    # ------------------------------------------------------------------ bootstrap
    def bootstrap(self):
        X, t, best = self.X, self.tstat, self.best
        P, L, B = 500, 10, 400
        np.random.seed(2026)
        dbar, om = X.mean(0), X.std(0, ddof=1)
        starts = []
        V = []
        for _ in range(B):
            st = np.random.randint(0, P - L, P // L)
            idx = (st[:, None] + np.arange(L)).ravel()
            V.append((np.sqrt(P) * (X[idx].mean(0) - dbar) / om).max())
            starts.append(st)
        V = np.array(V)
        pval = (V >= t[best]).mean()
        # strip of history
        nb = 50
        cols = [interpolate_color(ManimColor(BLUE_), ManimColor(PURPLE_), i / (nb - 1)) for i in range(nb)]
        W = 11.6
        bwid = W / nb

        def strip(seq, y):
            return VGroup(*[Rectangle(width=bwid, height=0.42, stroke_width=0.8, stroke_color=BG, fill_color=cols[s],
                                      fill_opacity=1).move_to([-W / 2 + bwid * (i + 0.5), y, 0]) for i, s in enumerate(seq)])

        hist_lab = T("history: 500 days in 50 blocks", 26, GREY_).move_to(UP * 3.45)
        orig = strip(range(nb), 2.9)
        with self.say("Real rules are correlated, and returns echo, so in practice we measure the bar by "
                      "bootstrap. Cut history into blocks, keeping the echoes inside each, and reshuffle "
                      "them into a new history.") as tr:
            self.play(FadeIn(hist_lab), FadeIn(orig))
            for k in range(2):
                seq = [int(s // L) for s in starts[k]]
                new = strip(seq, 2.25)
                self.play(*[TransformFromCopy(orig[s], new[i]) for i, s in enumerate(seq)], run_time=1.6)
                self.wait(0.4)
                if k == 0:
                    self.play(FadeOut(new), run_time=0.4)
            self.fill(tr, 4.8)
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 80, 20], x_length=10.4, y_length=3.4, tips=False,
                  axis_config={"color": GREY_, "font_size": 24},
                  x_axis_config={"numbers_to_include": range(6)}, y_axis_config={"numbers_to_include": [20, 40, 60, 80]}).shift(DOWN * 1.75 + RIGHT * 0.2)
        xl = T("best t-statistic in a world with no skill", 26, GREY_).next_to(ax, DOWN, buff=0.12)
        k = ValueTracker(0)
        hb = 0.2
        edges = np.arange(0, 5 + hb, hb)

        def hist():
            n = int(k.get_value())
            cnt, _ = np.histogram(V[:n], bins=edges)
            g = VGroup()
            for i, c in enumerate(cnt):
                if c == 0:
                    continue
                lo = edges[i]
                g.add(Rectangle(width=ax.c2p(hb, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, min(c, 80))[1] - ax.c2p(0, 0)[1],
                                stroke_width=1, stroke_color=BG, fill_color=RED_ if lo >= t[best] - 1e-9 else GREY_, fill_opacity=0.9
                                ).move_to(ax.c2p(lo + hb / 2, 0), aligned_edge=DOWN))
            return g

        def ro():
            n = int(k.get_value())
            p = (V[:n] >= t[best]).mean() if n else 0
            return T(f"worlds = {n},   share beating our monkey = {p:.2f}", 32).move_to(UP * 0.85)

        gl = DashedLine(ax.c2p(t[best], 0), ax.c2p(t[best], 80), color=GOLD, stroke_width=4)
        cr = crown(0.4).next_to(gl, UP, buff=0.05)
        h = always_redraw(hist)
        r = always_redraw(ro)
        with self.say("Re-centre every monkey so that none has skill, and record the best t-statistic. Repeat "
                      "four hundred times, and the crowd of best monkeys builds up.") as tr:
            self.play(Create(ax), FadeIn(xl), Create(gl), FadeIn(cr))
            self.add(h, r)
            self.play(k.animate.set_value(B), run_time=tr.duration - 2, rate_func=lambda s: s ** 1.6)
        with self.say("Our genius lands in the middle of that crowd. About a quarter of the worlds without "
                      "skill produce a best monkey at least this good. That share is the p-value of White's "
                      "Reality Check, and of Hansen's test of superior predictive ability.") as tr:
            self.play(Indicate(r, color=GOLD, scale_factor=1.08), run_time=1.5)
            self.fill(tr, 1.5)

    # ----------------------------------------------------------------- tournament
    def tournament(self):
        names = "ABCD"
        cols = {"A": TEAL_, "B": BLUE_, "C": PURPLE_, "D": RED_}
        cards = {}
        for i, n in enumerate(names):
            box = RoundedRectangle(corner_radius=0.15, width=1.9, height=1.25, stroke_color=cols[n], stroke_width=4,
                                   fill_color=cols[n], fill_opacity=0.15)
            lab = MathTex(n, font_size=56, color=cols[n]).move_to(box)
            cards[n] = VGroup(box, lab).move_to(RIGHT * (-3.6 + 2.4 * i) + UP * 0.9)
        stage = Line(LEFT * 5.2 + UP * 0.05, RIGHT * 5.2 + UP * 0.05, color=GREY_, stroke_width=4)
        head = T("model confidence set: a knockout tournament", 30).to_edge(UP, buff=0.35)
        with self.say("A different question: not whether anyone beats a benchmark, but which models may be "
                      "the best. The model confidence set runs a knockout tournament. In each round we test "
                      "whether the models left are equally good, and if not, the worst one is eliminated.") as tr:
            self.play(FadeIn(head), Create(stage))
            self.play(LaggedStart(*[FadeIn(cards[n], shift=DOWN * 0.3) for n in names], lag_ratio=0.2))
            self.fill(tr, 3)
        state = {"out": 0}

        def rnd(setn, ts, crit, drop, tr):
            tl = VGroup(*[MathTex(f"t={v:+.1f}", font_size=32, color=GOLD if v == max(ts) else WHITE_).next_to(cards[n], UP, buff=0.2)
                          for n, v in zip(setn, ts)])
            rej = max(ts) > crit
            verdict = MathTex(rf"T_{{\max}} = {max(ts):.1f}\ {'>' if rej else '<'}\ \text{{crit}} = {crit}", font_size=38,
                              color=RED_ if rej else GREEN_).move_to(DOWN * 1.2)
            self.play(FadeIn(tl), Write(verdict), run_time=1)
            if drop:
                c = cards[drop]
                cross = VGroup(Line(c.get_corner(UL), c.get_corner(DR)), Line(c.get_corner(UR), c.get_corner(DL))).set_stroke(RED_, 5)
                self.play(Create(cross), run_time=0.5)
                self.play(VGroup(c, cross).animate.scale(0.6).move_to(RIGHT * (4.6 - 1.4 * state["out"]) + DOWN * 2.85).set_opacity(0.45), run_time=1.2)
                state["out"] += 1
            self.fill(tr, 2.7 if drop else 1)
            return VGroup(tl, verdict)

        with self.say("Here D is significantly worse than the average of the field, and leaves.") as tr:
            g = rnd("ABCD", [-1.2, 0.3, 0.5, 2.9], 2.1, "D", tr)
        self.play(FadeOut(g), run_time=0.5)
        with self.say("Then C is eliminated.") as tr:
            g = rnd("ABC", [-1.0, 0.4, 2.3], 1.9, "C", tr)
        self.play(FadeOut(g), run_time=0.5)
        with self.say("With A and B left, the test no longer rejects: the data cannot tell them apart.") as tr:
            g = rnd("AB", [-0.9, 0.9], 1.6, None, tr)
        self.play(FadeOut(g), run_time=0.5)
        surv = VGroup(cards["A"], cards["B"])
        frame = SurroundingRectangle(surv, color=GOLD, buff=0.25, stroke_width=5)
        fl = MathTex(r"\widehat{\mathcal M}^*_{90\%} = \{A,\,B\}", font_size=44, color=GOLD).move_to(DOWN * 1.2)
        with self.say("The survivors form a ninety percent confidence set for the best model. A short list "
                      "means the data discriminate; a long one means they do not.") as tr:
            self.play(Create(frame), Write(fl))
            self.fill(tr, 2)

    # -------------------------------------------------------------------- closing
    def closing(self):
        g = VGroup(
            T("the best of many always looks brilliant;", 32, GOLD),
            T("judge it against the distribution of the best", 32, GOLD),
            MathTex(r"\Pr\big(\max_{j\le m} t_j > c\big) = 1-\Phi(c)^m", font_size=46),
        ).arrange(DOWN, buff=0.5)
        with self.say("So: the best of many always looks brilliant. Judge it, not against the bar for one "
                      "model chosen in advance, but against the distribution of the best.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=UP * 0.2))
                self.wait(0.7)
            self.fill(tr, 4)
