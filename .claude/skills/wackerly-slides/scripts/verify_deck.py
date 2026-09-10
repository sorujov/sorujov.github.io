#!/usr/bin/env python3
"""Check a rendered Quarto RevealJS deck for the failures that are invisible
in the source but obvious to a room full of students.

The deck that prompted this skill rendered without a single error while
shipping R code that never ran: the chunks were fenced ```r (a display
block) instead of ```{r} (an executable cell). Quarto has no opinion about
that, so this script does.

Usage:
    python verify_deck.py lecture.qmd          # .html path is inferred
    python verify_deck.py lecture.qmd --quiet  # exit code only

Exit code is 1 if anything failed, so it chains: verify && git add.
"""

import os
import re
import sys

FONT_FLOOR_PX = 28          # ~28px on the 1280x720 canvas is the back-row limit


class Report:
    def __init__(self):
        self.problems = []
        self.notes = []

    def fail(self, tag, msg):
        self.problems.append((tag, msg))

    def ok(self, msg):
        self.notes.append(msg)


def check_dead_code_fences(qmd_text, rep):
    """```r is a picture of code; ```{r} is code. Same for python and ojs."""
    for lang in ("r", "python", "ojs"):
        pattern = r"^```\{?\.?" + lang + r"\}?\s*$"
        for m in re.finditer(pattern, qmd_text, re.MULTILINE):
            fence = m.group(0).strip()
            if fence == "```{" + lang + "}":
                continue                      # executable, this is the good form
            line = qmd_text[: m.start()].count("\n") + 1
            rep.fail(
                "DEAD CODE",
                "line %d: fence %s renders as static text and never executes. "
                "Change it to ```{%s} so the code runs and its output lands on "
                "the slide." % (line, fence, lang),
            )


def check_engine(qmd_text, rep):
    if re.search(r"^```\{r", qmd_text, re.MULTILINE):
        if not re.search(r"^engine:\s*knitr", qmd_text, re.MULTILINE):
            rep.fail(
                "ENGINE",
                "The deck has executable {r} chunks but no `engine: knitr` in the "
                "frontmatter. Set it explicitly so engine selection cannot drift.",
            )


def check_network_calls(qmd_text, rep):
    """A live download in a slide chunk fails in the lecture hall, not here."""
    patterns = [
        (r"getSymbols\s*\(", "quantmod::getSymbols downloads from Yahoo at render time"),
        (r"read[_.]csv\s*\(\s*[\"']https?://", "read_csv from a URL"),
        (r"download\.file\s*\(", "download.file"),
        (r"\bhttr::|\bcurl::|\bGET\s*\(", "an HTTP client call"),
    ]
    for pat, what in patterns:
        if re.search(pat, qmd_text):
            rep.fail(
                "NETWORK",
                "%s in a slide chunk. The render breaks when the network or the API "
                "does, and the numbers shift under you between renders. Simulate with "
                "a fixed seed, or vendor a CSV next to the .qmd." % what,
            )


def check_r_ran(qmd_text, html, rep):
    n_chunks = len(re.findall(r"^```\{r", qmd_text, re.MULTILINE))
    if not n_chunks:
        return
    n_out = len(re.findall(r"cell-output", html))
    n_fig = len(re.findall(r"figure-revealjs|data:image/png;base64", html))
    if n_out == 0 and n_fig == 0:
        rep.fail(
            "NO R OUTPUT",
            "%d executable R chunk(s) in the source, but the rendered HTML has no "
            "cell output and no figures. The code did not run." % n_chunks,
        )
    else:
        rep.ok("R: %d chunk(s) produced %d output block(s) and %d figure ref(s)"
               % (n_chunks, n_out, n_fig))

    if re.search(r"^\s*#\|\s*eval:\s*false", qmd_text, re.MULTILINE):
        rep.fail("EVAL FALSE",
                 "A chunk carries `eval: false`, so it shows code with no result.")
    if re.search(r"^\s*#\|\s*echo:\s*false", qmd_text, re.MULTILINE) and n_out == 0:
        rep.fail("ECHO FALSE", "Chunks are echo: false and produced no visible output.")


def check_r_errors(html, rep):
    """knitr embeds error text in the page rather than failing the render."""
    signals = [
        (r"cell-output-error", "an error cell"),
        (r"Error in [\w.]+", "an R error message"),
        (r"there is no package called", "a missing R package"),
        (r"could not find function", "a missing R function"),
    ]
    for pat, label in signals:
        if re.search(pat, html):
            rep.fail("R ERROR",
                     "The rendered page contains %s -- students will see it on screen." % label)


def check_ojs(qmd_text, html, rep):
    n = len(re.findall(r"^```\{ojs", qmd_text, re.MULTILINE))
    if not n:
        return
    if "quarto-ojs" not in html and "ojs-runtime" not in html:
        rep.fail("OJS", "%d OJS cell(s) in source but no OJS runtime in the HTML." % n)
        return
    rep.ok("OJS: %d cell(s), runtime present" % n)
    if "viewof" not in qmd_text:
        rep.ok("OJS note: no `viewof` input, so the cells are static rather than interactive")


def check_quiz(qmd_dir, qmd_text, html, rep):
    uses_quiz = ".quiz-question" in qmd_text
    declares = re.search(r"^\s*-\s*quiz\s*$", qmd_text, re.MULTILINE)
    ext = os.path.join(qmd_dir, "_extensions", "parmsam", "quiz")

    if not (uses_quiz or declares):
        return
    if uses_quiz and not declares:
        rep.fail("QUIZ", "Quiz slides are present but `revealjs-plugins: [quiz]` is not declared.")
    if not os.path.isdir(ext):
        rep.fail(
            "QUIZ",
            "The quiz extension is missing at _extensions/parmsam/quiz. The plugin is "
            "declared but absent, so questions render as an inert bullet list. Copy the "
            "_extensions/ folder from a deck that has it, or run: quarto add parmsam/quarto-quiz",
        )
    if uses_quiz and "quiz.js" not in html:
        rep.fail("QUIZ", "quiz.js is not loaded in the rendered HTML; questions will not respond.")
    elif uses_quiz:
        rep.ok("Quiz: %d question slide(s), plugin loaded"
               % len(re.findall(r"quiz-question", qmd_text)))
    if uses_quiz and ".correct" not in qmd_text:
        rep.fail("QUIZ", "No option is marked `{.correct ...}`, so there is nothing to check.")


def check_fonts(qmd_text, rep):
    for m in re.finditer(r"font-size:\s*(\d+(?:\.\d+)?)\s*(px|em|pt)", qmd_text):
        val, unit = float(m.group(1)), m.group(2)
        px = val if unit == "px" else (val * 40 if unit == "em" else val * 1.333)
        if px < FONT_FLOOR_PX:
            line = qmd_text[: m.start()].count("\n") + 1
            rep.fail(
                "FONT",
                "line %d: font-size %s%s (~%dpx) is below the %dpx floor. Split the "
                "slide instead of shrinking the type."
                % (line, m.group(1), unit, px, FONT_FLOOR_PX),
            )


def check_density(qmd_text, rep):
    """A slide that overflows 720px is silently cut off in presentation mode."""
    body = qmd_text.split("---\n", 2)[-1]          # drop YAML frontmatter
    for chunk in re.split(r"^##\s+", body, flags=re.MULTILINE)[1:]:
        title = chunk.split("\n", 1)[0].strip()[:50]
        prose = re.sub(r"```.*?```", "", chunk, flags=re.DOTALL)   # code is not prose
        words = len(prose.split())
        bullets = len(re.findall(r"^\s*[-*]\s+\S", prose, re.MULTILINE))
        if words > 130:
            rep.fail("DENSITY", '~%d words on "%s" -- split the slide.' % (words, title))
        elif bullets > 6:
            rep.fail("DENSITY", '%d bullets on "%s" -- split the slide.' % (bullets, title))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    qmd = sys.argv[1]
    quiet = "--quiet" in sys.argv
    html = os.path.splitext(qmd)[0] + ".html"

    if not os.path.exists(qmd):
        sys.exit("No such file: %s" % qmd)
    with open(qmd, encoding="utf-8", errors="replace") as fh:
        qmd_text = fh.read()

    rep = Report()
    check_dead_code_fences(qmd_text, rep)
    check_engine(qmd_text, rep)
    check_network_calls(qmd_text, rep)
    check_fonts(qmd_text, rep)
    check_density(qmd_text, rep)

    if os.path.exists(html):
        with open(html, encoding="utf-8", errors="replace") as fh:
            html_text = fh.read()
        check_r_ran(qmd_text, html_text, rep)
        check_r_errors(html_text, rep)
        check_ojs(qmd_text, html_text, rep)
        check_quiz(os.path.dirname(os.path.abspath(qmd)), qmd_text, html_text, rep)
    else:
        rep.fail("NOT RENDERED", "%s does not exist. Render the deck before verifying." % html)

    if not quiet:
        print("\n%s" % os.path.basename(qmd))
        for note in rep.notes:
            print("  ok    %s" % note)
        for tag, msg in rep.problems:
            print("  FAIL  [%s] %s" % (tag, msg))
        print("\n%d problem(s), %d check(s) passed." % (len(rep.problems), len(rep.notes)))

    sys.exit(1 if rep.problems else 0)


if __name__ == "__main__":
    main()
