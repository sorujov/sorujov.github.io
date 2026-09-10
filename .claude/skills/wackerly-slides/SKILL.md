---
name: wackerly-slides
description: Build one Mathematical Statistics I lecture deck from a course-plan session — resolve the session's Wackerly sections, extract that text from the book, and write, render and verify an interactive Quarto RevealJS deck with executing R, an R-native think-pair-share timer, OJS explorables and quiz questions. Use when asked to make, build or fix slides for a Math Stat I session, a date on the course plan, or a Wackerly section range.
---

# Wackerly section → lecture deck

Builds **one lecture deck per course-plan session** for Mathematical Statistics I
(STAT-2311, ADA University). The unit of work is a row of the course plan, not a
chapter: the plan says what each session covers, and the deck matches it exactly.

Students are Finance and Economics majors. Every example, exercise and case study
gets a financial or economic setting — default counts, portfolio variance,
waiting times, insurance claims. Wackerly's abstract urns and dice get rewritten.

---

## Inputs and where things live

| Thing | Path |
|---|---|
| Course plan (source of truth) | `_teaching/2026-fall-mathematical-statistics-I.md` |
| Wackerly 7th ed. PDF | `local/books/wackerly-7e.pdf` |
| Deck output | `lectures/math-stat-1-fall-2026/NN-topic-slug/` |
| Shared slide theme | `lectures/math-stat-1-fall-2026/slide-fit.scss` |
| Template | `references/deck-template.qmd` |
| Interactive patterns | `references/interactive-patterns.md` |

The book sits in `local/`, which is gitignored: it is a copyrighted textbook and
this repository is a public GitHub Pages site. **Never move it back under a
tracked path, and never commit extracted book text.** Extract to the scratchpad.

---

## Workflow

### 1. Resolve the session

```bash
python .claude/skills/wackerly-slides/scripts/course_plan.py            # list all 30
python .claude/skills/wackerly-slides/scripts/course_plan.py "16 September"
```

This reads the teaching page directly, so it never drifts from what students see.
It reports the date, topic, reading, the Wackerly sections, whether slides exist,
and flags assessment days.

If the user names a section range instead of a date, use it directly — but still
check the plan, because the topic sentence there is the deck's actual brief.

Stop and ask if: the session is an **assessment day** with no teaching, the plan
row has no sections, or slides already exist and it is unclear whether to replace
them.

### 2. Extract the book text

```bash
python .claude/skills/wackerly-slides/scripts/extract_section.py \
  local/books/wackerly-7e.pdf 2.1-2.5 --out "$SCRATCH/2.1-2.5.txt"
```

Resolves sections through the PDF's embedded bookmarks, so a range ends at the
start of the next section rather than mid-argument. `--toc 3` lists a chapter's
sections; `--images DIR` pulls the figures out.

Write it to the scratchpad and read it there. Do not put book text in the repo.

Then **read the extracted text** before writing anything. The deck must follow
the book's actual definitions, notation and theorem numbering — students have the
book open. Note which of Wackerly's examples to re-set in a financial context.

### 3. Write the deck

Copy `references/deck-template.qmd` into
`lectures/math-stat-1-fall-2026/NN-topic-slug/` as `topic_slug.qmd`, numbering
`NN` to continue the existing sequence. Then, in that folder:

```bash
cp ../01-what-is-statistics/ADA.png .
cp -r ../01-what-is-statistics/_extensions .   # the quiz plugin; required
```

Shape of a 75-minute session:

1. Learning objectives (4–5, each a verb)
2. Motivating question in economic terms, before any notation
3. Definitions and theorems, stated as the book states them
4. A worked example done in full at the board's pace
5. An executing R computation, then its figure
6. **Think–Pair–Share with the timer** — roughly at the two-thirds mark
7. An OJS explorable, where a *shape* is the lesson
8. Two to four quiz questions
9. Key formulas, summary, next session's reading

Read `references/interactive-patterns.md` before writing any interactive slide.
It is short, and every pattern in it was rendered and checked on this machine.

The four rules that matter most:

- **R chunks are ` ```{r} `, never ` ```r `.** The latter is a picture of code
  that never runs. This is the defect that prompted this skill.
- **No network calls at render time.** Simulate with `set.seed(2026)`, or vendor
  a CSV beside the `.qmd`.
- **The timer is R-native**: `countdown::countdown(minutes = 3, top = 0, right = 0)`,
  on its own slide with the question visible.
- **28px font floor, ~130 words or 6 bullets per slide.** Split rather than shrink.

### 4. Render and verify

```bash
cd lectures/math-stat-1-fall-2026/NN-topic-slug
quarto render topic_slug.qmd --to revealjs
cd - && python .claude/skills/wackerly-slides/scripts/verify_deck.py \
  lectures/math-stat-1-fall-2026/NN-topic-slug/topic_slug.qmd
```

The verifier exits non-zero on: code fenced as dead text, a missing knitr engine,
network calls, R chunks that produced no output, R errors embedded in the page,
OJS with no runtime, a declared-but-missing quiz extension, quiz questions with no
correct answer marked, fonts under 28px, and overfull slides.

**A render that succeeds is not a deck that works.** The broken deck rendered
cleanly. Fix every finding and re-render until it exits 0.

### 5. Look at every slide

Passing step 4 is still not a deck that works. Lecture 1 passed every automated
check while shipping a histogram whose y-scale had collapsed — every bar drawn
full height, the axis showing only `0.00` — and a slider whose label wrapped to
three lines and shoved the plot off the canvas. Nothing that reads the source or
the HTML can see either. **This step is not optional.**

```bash
python .claude/skills/wackerly-slides/scripts/qa_slides.py \
  lectures/math-stat-1-fall-2026/NN-topic-slug/topic_slug.html
```

Flags: `--out DIR` (default `<deck>_qa/`), `--settle SECONDS` (default 1.2),
`--only 12,13`, `--no-interact`. It exits **1** if anything was measured wrong,
so it can be run in a loop until it exits 0.

It serves the repository over a throwaway loopback HTTP server, opens the deck
in headless Chromium through Playwright, steps every slide with
`Reveal.slide()` with fragments flattened, and writes `slide-01.png`,
`slide-02.png` … to `<deck>_qa/`.

**A deck with OJS must be served over HTTP, never opened as `file://`.**
Quarto emits this into every OJS deck:

```js
if (window.location.protocol === "file:") { alert("The OJS runtime does not
work with file:// URLs. Please use a web server to view this document."); }
```

That `alert()` blocks the renderer's main thread permanently. It is why every
earlier attempt at this step hung: `chrome --print-to-pdf`, `--virtual-time-budget`,
`?print-pdf` through `Page.printToPDF`, and plain `Runtime.evaluate` over CDP
all wait forever on a renderer that is sitting on a modal dialog, and the
renderer is eventually killed with "Abnormal renderer termination". None of
that is OJS being slow, and none of it is fixed by disabling script execution
or by dropping `Runtime.enable` — the diagnosis is a single
`Page.javascriptDialogOpening` event in the CDP stream. **Do not retry those
approaches.**

The same fact matters in the lecture theatre: double-clicking a deck's `.html`
gives dead sliders and dead plots. Open it from `quarto preview`, from
`python -m http.server`, or from the published site.

The script then flags what can be measured: blank or flooded slides, content
past the canvas edge, prose under 28px, chart and control text under 18px, an
Observable Plot y-axis collapsed to one tick, a set of bars all drawn the same
height, an OJS cell that produced nothing, an OJS or page error, and any
JavaScript dialog the deck opens.

**It also drives the deck.** A screenshot of a slider proves the slider was
drawn, not that moving it redraws anything. The interaction pass moves every
range and select to the far end of its scale, clicks the first option of every
quiz and presses Check, and screenshots again as `slide-NN-controls.png` and
`slide-NN-quiz.png`. A control that moves fewer than 0.2% of the pixels is
reported as dead. Read the before/after pair — that is the only evidence the
explorable actually works.

**Then read the images — every one of them.** The flags are a starting point,
not the review. A collapsed y-scale looks perfectly healthy to a pixel counter.
Ask of each slide:

- Does the chart show the shape the text claims? Is the y-axis a real scale with
  real ticks, or has it collapsed to a single value?
- Do the bars vary in height? A histogram of uniform full-height bars is broken,
  not uniform data.
- Do control labels sit on one line, and is the plot fully on the canvas?
- Is the R output actually printed under its chunk?
- Is the timer in the top-right corner where you put it?
- Is anything clipped at an edge?

Fix, re-render, re-run, and look again. The QA images are build artefacts —
write them to the scratchpad with `--out`, or leave `_qa/` untracked.

Two practical notes on running it:

- **Run it a moment after `quarto render`, not in the same breath.** Quarto
  rewrites the whole `_files/` tree, and a browser that arrives mid-write gets
  a deck where reveal.js never initialises. The script reloads once by itself
  and prints `reveal.js not ready -- reloading once`; if you see that, nothing
  is wrong. A second failure is real.
- **A wrong answer in a `slide-NN-quiz.png` is not a defect.** These decks set
  `shuffleOptions: true`, so the first option — the one the interaction pass
  clicks — is a different one each run. What the image proves is that the
  option responded and the feedback appeared, not which option was right.

Two things the measurements deliberately do **not** flag, so that they stay
quiet enough to be worth reading:

- A closed `<details>` — Quarto's `code-fold` — still reports layout boxes for
  its hidden children in Chromium, so a folded code block looks like it is
  hanging 100px off the slide when nothing is drawn there. Ignored.
- Code blocks, slider labels and chart axes are held to 18px rather than 28px.
  They are furniture; 28px tick labels would swamp the plot.

### What this step has already caught

Every one of these passed `verify_deck.py` and rendered without a warning.
They are fixed in `slide-fit.scss` and worth checking for in any new deck:

| Symptom on screen | Cause | Fix |
|---|---|---|
| Histogram bars all full height, y-axis reading only `0.00` | `Plot.binX` given a reducer it does not take | `Plot.binX({y: "proportion"}, …)` |
| Axis numbers unreadable from the back | Observable Plot's default 10px type | `style: {fontSize: "18px"}` in `Plot.plot` |
| Quiz options run off the right edge | `.option-button` is `width: 100%` plus `padding: 10px` with no `box-sizing` | `box-sizing: border-box` |
| Running score printed on top of the deck footer | `.score` is `position: absolute; bottom: 10px` | return it to the flow |
| A definition rendered at 22px beside 46px prose | Quarto sizes callout type from its own scale, and the title is a `<p>` inside `.callout-title` that must be targeted separately | pin both to 30px |
| Code at 15px | reveal sizes `pre` at `0.55em` of whatever the slide runs at, then `pre code { font-size: inherit }` | pin `pre` to 22px, with a selector specific enough to win |
| A frequency table showing eight near-zero classes from the far tail | `head(rel_freq, 8)` on a 50-class table | print the classes around the mode |

Overriding Quarto's or an extension's CSS needs a selector carrying
`.reveal .slides section` — a plain `.reveal pre` ties on specificity and then
loses on source order. That failure is silent.

### Before committing: sweep the stale theme CSS

Every edit to `slide-fit.scss` makes Quarto emit a **new** hashed stylesheet
into each deck's `_files/libs/revealjs/dist/theme/` and leave the previous one
behind. A few rounds of fix-and-re-render and there are a dozen orphans per
deck, all of them untracked junk that will otherwise be committed. Keep only
the one the HTML actually references:

```bash
cd lectures/math-stat-1-fall-2026
for d in NN-topic-slug/topic_slug; do
  keep=$(grep -oE 'quarto-[0-9a-f]{32}\.css' "$d.html" | sort -u)
  for f in "${d}_files/libs/revealjs/dist/theme/"quarto-*.css; do
    [ "$(basename "$f")" != "$keep" ] && rm "$f"
  done
done
```

Decks sharing `slide-fit.scss` end up referencing the *same* hash, so run this
across every deck after a theme change, not just the one you were editing.

### 6. Link it from the course plan

Replace that session's `<td class="muted-cell">&mdash;</td>` in
`_teaching/2026-fall-mathematical-statistics-I.md` with:

```html
<td><a class="slide-link" href="/lectures/math-stat-1-fall-2026/NN-topic-slug/topic_slug.html" target="_blank">Slides &rarr;</a></td>
```

Confirm with `course_plan.py "<date>"` that the session now reports `[slides]`.

---

## Toolchain

Verified present on this machine: Quarto 1.10.18, R 4.6.0 with `knitr`,
`rmarkdown`, `ggplot2`, `dplyr`, `tidyr`, `zoo`, `readr`, `kableExtra` and
`countdown`; Python 3.14 with PyMuPDF (for `extract_section.py`) and
Playwright + Pillow with the Chromium build installed (for `qa_slides.py`).

If Playwright is missing on another machine:

```bash
python -m pip install playwright pillow
python -m playwright install chromium
```

**Not** installed: `quantmod`, `tidyverse`, `xts`, `patchwork`, `gt`. Do not
write chunks that depend on them without installing them first and saying so —
an uninstalled package is an error message on the projector.
