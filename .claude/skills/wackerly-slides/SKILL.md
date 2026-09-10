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

Then open the HTML and check what no script can: that the figures say what the
text claims, that the timer is where you expect, and that nothing is clipped.

### 5. Link it from the course plan

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
`countdown`; Python 3.14 with PyMuPDF.

**Not** installed: `quantmod`, `tidyverse`, `xts`, `patchwork`, `gt`. Do not
write chunks that depend on them without installing them first and saying so —
an uninstalled package is an error message on the projector.
