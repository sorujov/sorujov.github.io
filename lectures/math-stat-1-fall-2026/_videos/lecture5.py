"""Lecture 5 intuition video: conditioning as zooming in; P(A|B) vs P(B|A); independence."""
from common import *

S = 5.0          # side of the unit square on screen
WB = 0.30        # P(B): width share of the B column
HA_IN, HA_OUT = 0.50, 0.20   # share of A inside and outside B


class Lecture5(IntuitionScene):
    parts = ("hook", "zoom", "asymmetry", "independence", "closing")

    def square_model(self, ha_in=HA_IN, ha_out=HA_OUT, origin=LEFT * 3.2):
        sq = Square(S, color=WHITE_, stroke_width=2).move_to(origin)
        x0, y0 = sq.get_left()[0], sq.get_bottom()[1]
        B = Rectangle(width=WB * S, height=S, stroke_width=0, fill_color=BLUE_, fill_opacity=0.25)
        B.move_to([x0 + (1 - WB) * S + WB * S / 2, y0 + S / 2, 0])
        A_out = Rectangle(width=(1 - WB) * S, height=ha_out * S, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.55)
        A_out.move_to([x0 + (1 - WB) * S / 2, y0 + ha_out * S / 2, 0])
        A_in = Rectangle(width=WB * S, height=ha_in * S, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.75)
        A_in.move_to([x0 + (1 - WB) * S + WB * S / 2, y0 + ha_in * S / 2, 0])
        Bl = MathTex("B", font_size=40, color=BLUE_).next_to(B, UP, buff=0.15)
        return sq, B, A_out, A_in, Bl

    def hook(self):
        q = T("A bond is from the energy sector.", 40)
        q2 = T("Does that change the chance it gets downgraded?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("You learn that a bond in your portfolio is issued by an energy company. Should "
                      "that change your estimate of the chance that it gets downgraded this year? Almost "
                      "certainly yes. New information changes probabilities. The question is: by how "
                      "much?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Conditional probability", 5,
                        "The answer is one simple picture: conditioning means zooming in.")

    def zoom(self):
        sq, B, A_out, A_in, Bl = self.square_model()
        leg = VGroup(
            VGroup(Square(0.3, fill_color=YELLOW_, fill_opacity=0.7, stroke_width=0), T("A: downgraded", 28, YELLOW_)).arrange(RIGHT, buff=0.25),
            VGroup(Square(0.3, fill_color=BLUE_, fill_opacity=0.4, stroke_width=0), T("B: energy sector", 28, BLUE_)).arrange(RIGHT, buff=0.25),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.8).shift(UP * 2.3)
        with self.say("Draw every bond in the portfolio as a square of area one. The energy bonds are "
                      "this column, thirty percent of the area. The bonds that will be downgraded are "
                      "shaded yellow. Notice there is more yellow inside the energy column than outside "
                      "it.") as tr:
            self.play(Create(sq), FadeIn(B), FadeIn(Bl), FadeIn(leg))
            self.play(FadeIn(A_out), FadeIn(A_in))
            self.fill(tr, 3)
        pa = MathTex(r"P(A)=0.29", font_size=44).next_to(leg, DOWN, buff=0.6).align_to(leg, LEFT)
        with self.say("Before we know anything, the chance of a downgrade is the total yellow area: "
                      "about twenty-nine percent.") as tr:
            self.play(Write(pa))
            self.fill(tr, 1)
        big = Rectangle(width=S * 0.72, height=S, stroke_color=BLUE_, stroke_width=3).move_to(RIGHT * 2.4 + DOWN * 0.3)
        with self.say("Now we learn the bond is an energy bond. Everything outside the column is no "
                      "longer possible. So throw it away, and stretch the column until it is our whole "
                      "world again, with total area one.") as tr:
            self.play(FadeOut(A_out), sq.animate.set_stroke(DIM), run_time=1)
            grp = VGroup(B.copy(), A_in.copy())
            self.play(FadeOut(pa), FadeOut(leg))
            self.play(grp.animate.stretch_to_fit_width(S * 0.72).move_to(big), Create(big), run_time=2)
            self.fill(tr, 4)
        cond = MathTex(r"P(A\mid B)", "=", r"\frac{P(A\cap B)}{P(B)}", "=", r"\frac{0.15}{0.30}", "=", "0.5",
                       font_size=40).next_to(big, UP, buff=0.3)
        cond[6].set_color(YELLOW_)
        with self.say("In this new world, what share is yellow? Half. So given that the bond is an "
                      "energy bond, the chance of a downgrade is fifty percent. That's the definition of "
                      "conditional probability: the probability of A and B together, divided by the "
                      "probability of B. Dividing is just the stretching.") as tr:
            self.play(Write(cond), run_time=2.5)
            self.fill(tr, 2.5)

    def asymmetry(self):
        sq, B, A_out, A_in, Bl = self.square_model(origin=ORIGIN + LEFT * 0.0)
        g = VGroup(sq, B, A_out, A_in, Bl).scale(0.8).shift(LEFT * 3.3 + DOWN * 0.3)
        with self.say("A common mistake is to flip the condition around. The chance that an energy bond "
                      "is downgraded is not the chance that a downgraded bond is an energy bond.") as tr:
            self.play(FadeIn(g))
            self.fill(tr, 1)
        r1 = MathTex(r"P(A\mid B)=\frac{0.15}{0.30}=0.50", font_size=42).shift(RIGHT * 2.8 + UP * 1.2)
        r2 = MathTex(r"P(B\mid A)=\frac{0.15}{0.29}\approx0.52", font_size=42, color=TEAL_).next_to(r1, DOWN, buff=0.8)
        with self.say("Both use the same overlap, the yellow part of the column. But one divides by the "
                      "blue column, the other by all the yellow. Different denominators, different "
                      "answers. Here they happen to be close; in many real problems, like a rare disease "
                      "and a common symptom, they are wildly different.") as tr:
            self.play(Indicate(g[3], color=YELLOW_))
            self.play(Write(r1))
            self.play(Write(r2))
            self.fill(tr, 4)

    def independence(self):
        sq, B, A_out, A_in, Bl = self.square_model(ha_in=0.29, ha_out=0.29)
        g = VGroup(sq, B, A_out, A_in, Bl).scale(0.8).shift(LEFT * 0.2)
        with self.say("Now imagine a different portfolio, where the yellow band has the same height "
                      "inside the energy column as outside it.") as tr:
            self.play(FadeIn(g))
            self.fill(tr, 1)
        t = MathTex(r"P(A\mid B)=P(A)", font_size=48, color=YELLOW_).to_edge(RIGHT, buff=0.6).shift(UP * 1.5)
        t2 = T("independent", 34, YELLOW_).next_to(t, DOWN, buff=0.3)
        with self.say("Then zooming in changes nothing: the share of yellow in the column equals the "
                      "share of yellow overall. Learning B tells you nothing about A. That is exactly "
                      "what independence means.") as tr:
            self.play(Write(t), FadeIn(t2))
            self.fill(tr, 2)
        self.play(FadeOut(g), FadeOut(t), FadeOut(t2))
        sq2 = Square(4, color=WHITE_).shift(LEFT * 2.5)
        a = Rectangle(width=1.6, height=4, stroke_width=0, fill_color=YELLOW_, fill_opacity=0.6).align_to(sq2, LEFT).align_to(sq2, DOWN)
        b = Rectangle(width=1.6, height=4, stroke_width=0, fill_color=BLUE_, fill_opacity=0.5).align_to(sq2, RIGHT).align_to(sq2, DOWN)
        la = MathTex("A", font_size=40, color=YELLOW_).move_to(a)
        lb = MathTex("B", font_size=40, color=BLUE_).move_to(b)
        m = VGroup(T("Mutually exclusive", 34, RED_), T("is the opposite of independent:", 30),
                   MathTex(r"\text{given }B,\ P(A\mid B)=0", font_size=40)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(RIGHT * 3)
        with self.say("One last trap. Events that can't happen together, that don't overlap at all, are "
                      "not independent. They are as dependent as it gets: if B happens, A is ruled out "
                      "completely. Zooming into B leaves no yellow at all.") as tr:
            self.play(Create(sq2), FadeIn(a), FadeIn(b), FadeIn(la), FadeIn(lb))
            self.play(FadeIn(m, shift=LEFT * 0.2))
            self.fill(tr, 3)

    def closing(self):
        a = T("Conditioning on B = zooming into B", 40, BLUE_)
        b = MathTex(r"P(A\mid B)=\frac{P(A\cap B)}{P(B)}", font_size=52).next_to(a, DOWN, buff=0.5)
        c = T("Independent: zooming in changes nothing.", 34, YELLOW_).next_to(b, DOWN, buff=0.6)
        with self.say("So remember the picture. Conditioning on B means throwing away everything outside "
                      "B, and rescaling what's left to have total probability one. And two events are "
                      "independent exactly when that zoom doesn't change the picture.") as tr:
            self.play(Write(a))
            self.play(Write(b))
            self.play(FadeIn(c))
            self.fill(tr, 4)
