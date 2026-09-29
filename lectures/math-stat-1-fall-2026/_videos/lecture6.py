"""Lecture 6 intuition video: multiplicative law (zoom twice), additive law (don't double count), complement."""
from common import *


class Lecture6(IntuitionScene):
    parts = ("hook", "multiply", "add_law", "complement", "closing")

    def hook(self):
        q = T("10 loans in a pool. 3 will default.", 40)
        q2 = T("Pick two at random. Chance both default?", 40, YELLOW_).next_to(q, DOWN, buff=0.5)
        with self.say("A pool holds ten loans, and three of them are going to default. An auditor picks "
                      "two loans at random. What's the chance that both are bad ones?") as tr:
            self.play(FadeIn(q))
            self.play(Write(q2))
            self.fill(tr, 2)
        self.play(FadeOut(q), FadeOut(q2))
        self.title_card("Two laws of probability", 6,
                        "Two laws answer questions like this: one for 'and', one for 'or'. Plus a trick "
                        "for 'at least one'.")

    def multiply(self):
        loans = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.8, height=1.1,
                                          color=RED_ if i < 3 else TEAL_, fill_opacity=0.35) for i in range(10)])
        loans.arrange(RIGHT, buff=0.25).to_edge(UP, buff=0.9)
        with self.say("First pick: three of the ten loans are bad, so the chance the first one is bad is "
                      "three tenths.") as tr:
            self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.2) for l in loans], lag_ratio=0.08))
            self.play(Indicate(VGroup(*loans[:3]), color=RED_))
            self.fill(tr, 2.5)
        S = 4.0
        sq = Square(S, color=WHITE_).shift(DOWN * 1.15 + LEFT * 3.3)
        x0, y0 = sq.get_left()[0], sq.get_bottom()[1]
        def box(x, y, w, h, color, op):
            return Rectangle(width=S * w, height=S * h, stroke_width=1, stroke_color=BG, fill_color=color,
                             fill_opacity=op).move_to([x0 + S * (x + w / 2), y0 + S * (y + h / 2), 0])
        lab_all = T("all ways the two picks can go: area = 1", 22, GREY_).next_to(sq, UP, buff=0.15)
        with self.say("Picture every possible outcome of the two picks as this square, with total area "
                      "one. Its width stands for the first pick.") as tr:
            self.play(Create(sq), FadeIn(lab_all))
            self.fill(tr, 1.5)
        colA = box(0, 0, 0.3, 1, RED_, 0.25)
        colG = box(0.3, 0, 0.7, 1, TEAL_, 0.12)
        bx = T("1st bad: 0.3", 22, RED_).next_to(colA, DOWN, buff=0.2)
        gx = T("1st good: 0.7", 22, TEAL_).next_to(colG, DOWN, buff=0.2)
        l1 = MathTex(r"P(A)=\tfrac{3}{10}", font_size=40, color=RED_).move_to([-0.2, 0.9, 0], aligned_edge=LEFT)
        with self.say("The left thirty percent of the width is where the first loan is bad; the rest is "
                      "where it is good.") as tr:
            self.play(FadeIn(colA), FadeIn(colG), FadeIn(bx), FadeIn(gx), Write(l1))
            self.fill(tr, 1.5)
        inner = box(0, 0, 0.3, 2 / 9, RED_, 0.95)
        good2 = box(0.3, 0, 0.7, 3 / 9, TEAL_, 0.35)
        by = MathTex(r"\tfrac{2}{9}", font_size=36, color=YELLOW_).next_to(inner, LEFT, buff=0.15)
        ylab = T("height = 2nd pick", 22, GREY_).rotate(PI / 2).next_to(sq, LEFT, buff=0.55)
        g2 = MathTex(r"\tfrac{3}{9}", font_size=38, color=WHITE_).move_to(good2)
        l2 = MathTex(r"P(B\mid A)=\tfrac{2}{9}", font_size=40, color=YELLOW_).next_to(l1, DOWN, buff=0.4).align_to(l1, LEFT)
        with self.say("Its height stands for the second pick, and inside each strip the pool is different. "
                      "If the first loan was bad, two bad loans remain among nine, so only the bottom two "
                      "ninths of the left strip has a bad second loan as well. On the right, after a good "
                      "first loan, it would be three ninths.") as tr:
            self.play(loans[0].animate.shift(DOWN * 0.4).set_opacity(0.15), FadeIn(ylab))
            self.play(GrowFromEdge(inner, DOWN), FadeIn(by), Write(l2))
            self.play(GrowFromEdge(good2, DOWN), FadeIn(g2))
            self.fill(tr, 3.5)
        res = MathTex(r"P(A\cap B)=\tfrac{3}{10}\cdot\tfrac{2}{9}=\tfrac{1}{15}", font_size=40
                      ).next_to(l2, DOWN, buff=0.6).align_to(l1, LEFT)
        res2 = T("= area of the red corner (width x height)", 26, GREY_).next_to(res, DOWN, buff=0.3).align_to(res, LEFT)
        arrow = Arrow(res.get_left() + LEFT * 0.2, inner.get_right() + RIGHT * 0.05, color=YELLOW_, buff=0.1, stroke_width=4)
        with self.say("Both loans are bad only in the red corner: three tenths wide and two ninths tall. "
                      "Its area, three tenths times two ninths, one in fifteen, is the chance of both. "
                      "That's the multiplicative law: a fraction of a fraction. The second factor is "
                      "conditional, because the first pick changed the pool. If the events were "
                      "independent, it would just be the ordinary probability.") as tr:
            self.play(Indicate(inner, color=YELLOW_, scale_factor=1.15), GrowArrow(arrow))
            self.play(Write(res), run_time=2)
            self.play(FadeIn(res2))
            self.fill(tr, 4.5)

    def add_law(self):
        A = Circle(radius=2.0, color=BLUE_, fill_opacity=0.3).shift(LEFT * 4.3 + DOWN * 0.3)
        B = Circle(radius=1.6, color=YELLOW_, fill_opacity=0.3).shift(LEFT * 1.9 + DOWN * 0.3)
        la = T("credit card\n0.60", 28, BLUE_, line_spacing=0.8).move_to(A.get_center() + LEFT * 0.8)
        lb = T("mortgage\n0.30", 28, YELLOW_, line_spacing=0.8).move_to(B.get_center() + RIGHT * 0.55)
        ov = Intersection(A, B, color=RED_, fill_opacity=0.8, stroke_width=0)
        lo = T("both\n0.20", 24, WHITE_, line_spacing=0.8).move_to(ov)
        with self.say("Now 'or'. Sixty percent of a bank's customers have its credit card, thirty "
                      "percent have its mortgage. What share has at least one of the two?") as tr:
            self.play(DrawBorderThenFill(A), FadeIn(la))
            self.play(DrawBorderThenFill(B), FadeIn(lb))
            self.fill(tr, 3)
        naive = MathTex(r"0.60+0.30=0.90\ ?", font_size=44).to_edge(RIGHT, buff=0.7).shift(UP * 1.8)
        with self.say("Adding gives ninety percent. But look at the overlap. Customers with both "
                      "products were counted once in the first circle and again in the second.") as tr:
            self.play(Write(naive))
            self.play(FadeIn(ov), FadeIn(lo))
            self.play(Indicate(ov, color=RED_, scale_factor=1.1), run_time=1.5)
            self.fill(tr, 3)
        law = MathTex(r"P(A\cup B)=P(A)+P(B)-P(A\cap B)", font_size=36).next_to(naive, DOWN, buff=0.6).align_to(naive, RIGHT)
        num = MathTex(r"=0.60+0.30-0.20=", "0.70", font_size=40).next_to(law, DOWN, buff=0.35).align_to(law, RIGHT)
        num[1].set_color(YELLOW_)
        with self.say("So subtract the overlap once: sixty plus thirty minus twenty, seventy percent. "
                      "That's the additive law. The subtraction isn't a fudge; it just repairs the double "
                      "count.") as tr:
            self.play(Write(law), run_time=2)
            self.play(Write(num))
            self.fill(tr, 3.5)

    def complement(self):
        q = T("10 independent payment servers, each fails with probability 5%.", 32).to_edge(UP, buff=0.6)
        q2 = T("Chance that at least one fails today?", 34, YELLOW_).next_to(q, DOWN, buff=0.3)
        with self.say("Finally, 'at least one'. A payment system runs on ten independent servers, and "
                      "each one fails on a given day with probability five percent. What's the chance at "
                      "least one fails?") as tr:
            self.play(FadeIn(q), FadeIn(q2))
            self.fill(tr, 1)
        with self.say("'At least one' is a mess: exactly one, or exactly two, or exactly three, and so "
                      "on. Its opposite is clean: none fail. And none failing is an 'and' of ten "
                      "independent events, so we just multiply.") as tr:
            bars = VGroup()
            base = LEFT * 5.5 + DOWN * 2.8
            for k in range(11):
                h = 0.95 ** k * 3.6
                b = Rectangle(width=0.5, height=h, stroke_width=0, fill_color=TEAL_, fill_opacity=0.8)
                b.move_to(base + RIGHT * k * 0.65 + UP * h / 2)
                bars.add(b)
            lbl = VGroup(*[MathTex(str(k), font_size=26, color=GREY_).next_to(bars[k], DOWN, buff=0.15) for k in range(11)])
            cap = T("P(no failure among the first k servers)", 24, TEAL_).next_to(bars, UP, buff=0.25).align_to(bars, LEFT)
            self.play(FadeIn(cap), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15), FadeIn(lbl), run_time=3)
            self.fill(tr, 3)
        f = VGroup(MathTex(r"P(\text{at least one})", font_size=42),
                   MathTex(r"=1-0.95^{10}\approx", "0.40", font_size=42)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.5)
        f[1][1].set_color(RED_)
        with self.say("After ten servers, the chance nothing fails is point nine five to the tenth, about "
                      "sixty percent. So the chance that at least one fails is one minus that: about forty "
                      "percent. Small risks, repeated, add up fast.") as tr:
            self.play(Indicate(bars[10], color=TEAL_))
            self.play(Write(f), run_time=2)
            self.fill(tr, 3)

    def closing(self):
        g = VGroup(
            VGroup(T("and", 40, RED_), MathTex(r"P(A\cap B)=P(A)\,P(B\mid A)", font_size=44)).arrange(RIGHT, buff=0.6),
            VGroup(T("or", 40, YELLOW_), MathTex(r"P(A\cup B)=P(A)+P(B)-P(A\cap B)", font_size=44)).arrange(RIGHT, buff=0.6),
            VGroup(T("at least one", 40, TEAL_), MathTex(r"1-P(\text{none})", font_size=44)).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6)
        with self.say("So: for 'and', multiply, zooming in as you go. For 'or', add, but subtract what "
                      "you counted twice. And for 'at least one', go through the complement.") as tr:
            for x in g:
                self.play(FadeIn(x, shift=RIGHT * 0.3))
                self.wait(0.8)
            self.fill(tr, 4.5)
