"""Lecture 3 intuition video: sample space, events as subsets, probability as mass, the three axioms."""
from common import *


class Lecture3(IntuitionScene):
    parts = ("hook", "grid_part", "mass", "operations", "closing")

    def make_grid(self):
        cells = VGroup()
        for i in range(1, 7):
            for j in range(1, 7):
                sq = Square(side_length=0.78, stroke_color=GREY_, stroke_width=1.5, fill_color=BG, fill_opacity=1)
                sq.move_to(np.array([(j - 3.5) * 0.82, (3.5 - i) * 0.82, 0]))
                lab = T(f"{i},{j}", 20, GREY_).move_to(sq)
                cells.add(VGroup(sq, lab))
        return cells

    def hook(self):
        q = T("Roll two dice. How likely is a total of 7?", 42)
        with self.say("Roll two dice. How likely is it that they add up to seven? You probably have a "
                      "hunch. Let's build the answer from scratch, because the way we build it is the "
                      "whole of probability theory in miniature.") as tr:
            self.play(Write(q), run_time=2)
            self.fill(tr, 2)
        self.play(FadeOut(q))
        self.title_card("Probability of an event", 3,
                        "Three ideas: a sample space, events as subsets of it, and probability as a kind "
                        "of mass spread over it.")

    def grid_part(self):
        cells = self.make_grid().shift(LEFT * 2.6)
        self.cells = cells
        rl = T("first die", 24, GREY_).next_to(cells, LEFT, buff=0.3).rotate(PI / 2)
        cl = T("second die", 24, GREY_).next_to(cells, UP, buff=0.2)
        S = MathTex("S", font_size=52, color=BLUE_).next_to(cells, RIGHT, buff=0.5).shift(UP * 2)
        sl = T("the sample space:\n36 possible outcomes", 28, BLUE_, line_spacing=0.8).next_to(S, DOWN, buff=0.3).align_to(S, LEFT)
        with self.say("First, list everything that can happen. The first die shows one to six, the "
                      "second die one to six, so there are thirty-six outcomes. This complete list is "
                      "the sample space, S.") as tr:
            self.play(LaggedStart(*[FadeIn(c, scale=0.7) for c in cells], lag_ratio=0.02, run_time=2.5),
                      FadeIn(rl), FadeIn(cl))
            self.play(Write(S), FadeIn(sl))
            self.fill(tr, 4)
        seven = [k for k in range(36) if (k // 6 + 1) + (k % 6 + 1) == 7]
        self.seven = seven
        A = MathTex("A", font_size=52, color=YELLOW_).next_to(sl, DOWN, buff=0.7).align_to(S, LEFT)
        al = T("= { total is 7 }", 28, YELLOW_).next_to(A, RIGHT, buff=0.2)
        with self.say("An event is just a collection of outcomes, a subset of S. The event 'the total is "
                      "seven' is these six cells, running along the diagonal.") as tr:
            self.play(*[self.cells[k][0].animate.set_fill(YELLOW_, 0.55) for k in seven], run_time=1.5)
            self.play(Write(A), FadeIn(al))
            self.fill(tr, 2.5)
        p = MathTex(r"P(A)=\frac{6}{36}=\frac16", font_size=50, color=YELLOW_).next_to(A, DOWN, buff=0.6).align_to(A, LEFT)
        with self.say("If the dice are fair, all thirty-six outcomes are equally likely. So the "
                      "probability of the event is the share of cells it covers: six out of thirty-six, "
                      "one in six.") as tr:
            self.play(Write(p))
            self.fill(tr, 1)
        self.side = VGroup(S, sl, A, al, p, rl, cl)

    def mass(self):
        self.cells = self.make_grid().shift(LEFT * 2.6)
        self.add(self.cells)
        with self.say("Here's a more useful way to think about it. Imagine one kilogram of sand, spread "
                      "over the sample space. With fair dice, every cell gets the same pinch: one "
                      "thirty-sixth.") as tr:
            sand = VGroup(*[Rectangle(width=0.6, height=0.22, stroke_width=0, fill_color=TEAL_, fill_opacity=0.9)
                            .move_to(c[0].get_bottom() + UP * 0.14) for c in self.cells])
            self.play(*[c[0].animate.set_fill(BG, 1) for c in self.cells])
            self.play(LaggedStart(*[GrowFromEdge(s, DOWN) for s in sand], lag_ratio=0.02, run_time=2.5))
            self.fill(tr, 3.5)
        ax = VGroup(
            T("1.  Mass is never negative.", 27),
            T("2.  All the mass together is 1.", 27),
            T("3.  Mass in separate pieces adds up.", 27),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(self.cells, RIGHT, buff=0.6).shift(UP * 0.4)
        hd = T("The three axioms", 34, YELLOW_).next_to(ax, UP, buff=0.5).align_to(ax, LEFT)
        with self.say("The probability of any event is simply how much sand sits on its cells. And the "
                      "three axioms of probability are just three facts about sand. There's never a "
                      "negative amount. All of it together weighs one. And if two events share no cells, "
                      "the sand on both is the sand on one plus the sand on the other.") as tr:
            self.play(FadeIn(hd))
            for a in ax:
                self.play(FadeIn(a, shift=RIGHT * 0.2), run_time=0.8)
                self.wait(1.6)
            self.fill(tr, 8)
        loaded = [0.05, 0.1, 0.15, 0.15, 0.2, 0.35]
        with self.say("Nothing requires equal pinches. If the dice were loaded, the sand would pile up "
                      "unevenly, and counting cells would no longer work. But weighing sand still would. "
                      "That's why probability is defined through these axioms, not through counting.") as tr:
            anims = []
            for k, s in enumerate(sand):
                w = loaded[k // 6] * loaded[k % 6] * 36
                anims.append(s.animate.stretch_to_fit_height(0.22 * w * 0.75, about_edge=DOWN))
            self.play(*anims, run_time=2.5)
            self.fill(tr, 2.5)

    def operations(self):
        cells = self.make_grid().shift(LEFT * 2.6)
        self.add(cells)
        seven = [k for k in range(36) if (k // 6 + 1) + (k % 6 + 1) == 7]
        dbl = [k for k in range(36) if k // 6 == k % 6]
        big = [k for k in range(36) if k // 6 + 1 >= 5]
        lab = VGroup(
            VGroup(Square(0.3, fill_color=YELLOW_, fill_opacity=0.6, stroke_width=0), T("A: total is 7", 28, YELLOW_)).arrange(RIGHT, buff=0.25),
            VGroup(Square(0.3, fill_color=BLUE_, fill_opacity=0.6, stroke_width=0), T("B: a double", 28, BLUE_)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(cells, RIGHT, buff=0.7).align_to(cells, UP)
        with self.say("Two events with no cells in common are called mutually exclusive. A total of "
                      "seven, and a double: you can't roll both at once.") as tr:
            self.play(*[cells[k][0].animate.set_fill(YELLOW_, 0.55) for k in seven],
                      *[cells[k][0].animate.set_fill(BLUE_, 0.55) for k in dbl], FadeIn(lab))
            self.fill(tr, 1.5)
        u = MathTex(r"P(A\cup B)=\tfrac{6}{36}+\tfrac{6}{36}=\tfrac13", font_size=44).next_to(lab, DOWN, buff=0.6).align_to(lab, LEFT)
        with self.say("So the chance of one or the other is just the sum: six thirty-sixths plus six "
                      "thirty-sixths, one third. That's axiom three at work.") as tr:
            self.play(Write(u))
            self.fill(tr, 1.5)
        c = MathTex(r"P(\bar A)=1-\tfrac16=\tfrac56", font_size=44, color=GREY_).next_to(u, DOWN, buff=0.5).align_to(u, LEFT)
        with self.say("And the chance of not rolling seven is everything else: one minus a sixth, five "
                      "sixths. The complement always takes the rest of the sand.") as tr:
            self.play(*[cells[k][0].animate.set_fill(GREY_, 0.35) for k in range(36) if k not in seven],
                      *[cells[k][0].animate.set_fill(BG, 1) for k in seven])
            self.play(Write(c))
            self.fill(tr, 2)
        w = T("Overlapping events need care:\nthat comes in a later lecture.", 28, RED_).next_to(c, DOWN, buff=0.6).align_to(c, LEFT)
        with self.say("When events do overlap, simply adding would count the shared cells twice. How to "
                      "fix that is a story for a later lecture.") as tr:
            self.play(*[cells[k][0].animate.set_fill(BG, 1) for k in range(36)])
            self.play(*[cells[k][0].animate.set_fill(TEAL_, 0.45) for k in big],
                      *[cells[k][0].animate.set_fill(YELLOW_, 0.55) for k in seven if k not in big],
                      *[cells[k][0].animate.set_fill(RED_, 0.8) for k in seven if k in big])
            self.play(FadeIn(w))
            self.fill(tr, 2)

    def closing(self):
        g = VGroup(
            VGroup(T("sample space", 36, BLUE_), T("everything that can happen", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("event", 36, YELLOW_), T("a subset of it", 30)).arrange(RIGHT, buff=0.5),
            VGroup(T("probability", 36, TEAL_), T("how much of the mass it holds", 30)).arrange(RIGHT, buff=0.5),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: the sample space is everything that can happen. An event is a subset of it. "
                      "And a probability is how much of the total mass that subset holds. Every rule we "
                      "meet later is a consequence of those three axioms about mass.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(1)
            self.fill(tr, 5)
