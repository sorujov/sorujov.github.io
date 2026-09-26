"""Lecture 7 intuition video: event composition — series ('and') and parallel ('or') systems."""
from common import *


def box(label, color=TEAL_, w=2.2):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=0.9, color=color, fill_opacity=0.15)
    return VGroup(r, T(label, 22, color).move_to(r))


class Lecture7(IntuitionScene):
    parts = ("hook", "series", "parallel", "compose", "closing")

    def hook(self):
        chain = VGroup(box("terminal"), box("acquirer"), box("card network"), box("issuing bank")).arrange(RIGHT, buff=0.55)
        arrows = VGroup(*[Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.08, color=GREY_) for i in range(3)])
        g = VGroup(chain, arrows).shift(UP * 0.5)
        q = T("Each step works 99% of the time. Does the payment go through?", 32, YELLOW_).next_to(g, DOWN, buff=0.9)
        with self.say("You tap your card at a supermarket in Baku. The payment has to pass through four "
                      "systems: the terminal, the shop's bank, the card network, and your own bank. Each "
                      "one works ninety-nine percent of the time. What's the chance your payment goes "
                      "through?") as tr:
            self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in chain], lag_ratio=0.3), Create(arrows))
            self.play(Write(q), run_time=1.5)
            self.fill(tr, 4)
        self.chain, self.arrows, self.q = chain, arrows, q
        dot = Dot(chain[0].get_left() + LEFT * 0.4, color=YELLOW_, radius=0.12)
        with self.say("The trick of this lecture is to write the event you care about in terms of simpler "
                      "events, and then let the laws of probability do the work.") as tr:
            self.play(FadeIn(dot))
            self.play(dot.animate.move_to(chain[3].get_right() + RIGHT * 0.4), run_time=2.5, rate_func=linear)
            self.fill(tr, 3)

    def series(self):
        self.add(self.chain, self.arrows)
        ev = MathTex(r"\text{success}", "=", "T", r"\cap", "A", r"\cap", "N", r"\cap", "I", font_size=48).to_edge(UP, buff=0.7)
        with self.say("Success means every link works: the terminal and the acquirer and the network and "
                      "the issuer. That's an intersection.") as tr:
            self.play(Write(ev), run_time=2)
            self.fill(tr, 2)
        p = MathTex(r"0.99^4\approx", "0.961", font_size=52).next_to(self.chain, DOWN, buff=0.8)
        p[1].set_color(YELLOW_)
        with self.say("If the links fail independently, multiply: point nine nine to the fourth, about "
                      "ninety-six percent. Every extra link in a chain shaves a little more off.") as tr:
            self.play(Write(p))
            self.fill(tr, 1)
        self.play(FadeOut(VGroup(self.chain, self.arrows, p, ev)))
        ax = Axes(x_range=[0, 50, 10], y_range=[0, 1, 0.25], x_length=8, y_length=4, tips=False,
                  axis_config={"color": GREY_, "include_numbers": True, "font_size": 24}).shift(DOWN * 0.4)
        xl = T("links in series", 24, GREY_).next_to(ax, DOWN, buff=0.3)
        c = ax.plot(lambda n: 0.99 ** n, x_range=[0, 50], color=YELLOW_)
        lab = MathTex(r"0.99^{\,n}", font_size=40, color=YELLOW_).next_to(ax.c2p(50, 0.605), UP, buff=0.2)
        with self.say("Look at what happens as the chain grows. With fifty links, each ninety-nine "
                      "percent reliable, the whole chain works only about sixty percent of the time. In a "
                      "series system, the weakest link isn't the only problem: every link costs you.") as tr:
            self.play(Create(ax), FadeIn(xl))
            self.play(Create(c), FadeIn(lab), run_time=2.5)
            self.fill(tr, 4)

    def parallel(self):
        feeds = VGroup(box("power feed 1", RED_, 2.2), box("power feed 2", RED_, 2.2)).arrange(DOWN, buff=0.7).shift(LEFT * 2.5)
        srv = box("data centre", TEAL_, 2.2).shift(RIGHT * 2.5)
        arr = VGroup(*[Arrow(f.get_right(), srv.get_left(), buff=0.1, color=GREY_) for f in feeds])
        with self.say("Now flip it around. A data centre has two independent power feeds, and it stays up "
                      "as long as at least one of them works. Each feed is up ninety-five percent of the "
                      "time.") as tr:
            self.play(FadeIn(feeds), FadeIn(srv), Create(arr))
            self.fill(tr, 1)
        ev = MathTex(r"\text{up}", "=", "F_1", r"\cup", "F_2", font_size=48).to_edge(UP, buff=0.7)
        f1 = MathTex(r"P(\text{down})=0.05\times0.05=0.0025", font_size=42).next_to(VGroup(feeds, srv), DOWN, buff=0.8)
        f2 = MathTex(r"P(\text{up})=1-0.0025=", "0.9975", font_size=42).next_to(f1, DOWN, buff=0.3)
        f2[1].set_color(YELLOW_)
        with self.say("Now success is a union: feed one or feed two. The easy way in is the complement. "
                      "The centre goes down only if both feeds fail: five percent times five percent, a "
                      "quarter of a percent. So it's up ninety-nine point seven five percent of the time. "
                      "Redundancy turns two mediocre parts into an excellent system.") as tr:
            self.play(Write(ev))
            self.play(Indicate(feeds, color=RED_, scale_factor=1.08), run_time=1)
            self.play(Write(f1), run_time=1.5)
            self.play(Write(f2), run_time=1.5)
            self.fill(tr, 5)

    def compose(self):
        rows = VGroup()
        for k in range(3):
            pair = VGroup(box(f"{k+1}a", BLUE_, 1.1), box(f"{k+1}b", BLUE_, 1.1)).arrange(DOWN, buff=0.35)
            rows.add(pair)
        rows.arrange(RIGHT, buff=1.4).shift(UP * 0.4)
        conns = VGroup(*[Line(rows[i].get_right(), rows[i + 1].get_left(), color=GREY_) for i in range(2)])
        with self.say("Real systems mix the two. Here are three stages in a row, and each stage has a "
                      "backup. Break it down: each stage is a parallel pair, and the stages form a "
                      "series.") as tr:
            self.play(FadeIn(rows), Create(conns))
            self.play(*[Indicate(r, color=YELLOW_, scale_factor=1.08) for r in rows])
            self.fill(tr, 3)
        f = MathTex(r"\big(1-0.1^2\big)^3", "=", r"0.99^3\approx", "0.970", font_size=48).next_to(rows, DOWN, buff=0.8)
        f[3].set_color(YELLOW_)
        n = T("each unit works 90% of the time", 26, GREY_).next_to(f, DOWN, buff=0.3)
        with self.say("If each unit works ninety percent of the time, a stage fails only when both units "
                      "do: one in a hundred. Three stages in series then work point nine nine cubed: about "
                      "ninety-seven percent. From ninety-percent parts! Composition is just this: name "
                      "the simple events, glue them with 'and' and 'or', and compute.") as tr:
            self.play(Write(f), FadeIn(n), run_time=2)
            self.fill(tr, 2)

    def closing(self):
        g = VGroup(
            VGroup(T("series (and)", 38, YELLOW_), T("multiply the chances of success", 30)).arrange(RIGHT, buff=0.6),
            VGroup(T("parallel (or)", 38, RED_), T("multiply the chances of failure", 30)).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: in series, multiply the chances of success. In parallel, multiply the chances "
                      "of failure, and take the complement. Everything else is bookkeeping.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 3)
