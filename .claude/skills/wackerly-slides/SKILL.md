---
name: wackerly-slides
description: "Build one Mathematical Statistics I (STAT-2311, ADA University) lecture deck from a course-plan session — resolve the session's Wackerly sections, extract that text from the book, then write, render, screenshot-verify and publish an interactive Quarto RevealJS deck with executing R, an R-native think–pair–share timer, OJS explorables and quiz questions. Use this whenever slides, a deck or a lecture are wanted for Math Stat I — a date on the course plan (\"Wednesday's lecture\", \"16 September\"), a Wackerly section range (\"§3.4–3.7\"), \"the next two sessions\" — and equally when fixing an existing Fall 2026 deck: a slide that overflows, a dead slider, a chart that looks wrong, a quiz that does not respond. It governs every deck under lectures/math-stat-1-fall-2026/, in preference to the older 50px-then-optimize font pass, which fights the shared slide-fit.scss."
---

# Wackerly section → lecture deck

Builds **one lecture deck per course-plan session** for Mathematical Statistics I
(STAT-2311, ADA University). The unit of work is a row of the course plan, not a
chapter: the plan says what each session covers, and the deck matches it exactly.

Students are Finance and Economics majors. Every example, exercise and case study
gets a financial or economic setting — default counts, portfolio variance,
waiting times, insurance claims. Wackerly's abstract urns and dice get rewritten.

A deck is finished when it is **rendered, looked at, pushed, and reachable from
the course page** — not when it renders. The lecture is given from the classroom
screen over a URL, so a deck sitting correct on disk has not yet arrived.

## This workflow owns the Fall 2026 decks

Decks under `lectures/math-stat-1-fall-2026/` are sized by the shared
`../slide-fit.scss` (46px root, 28px floor) and checked by `verify_deck.py`. Do
not put them through the older "set every slide to 50px, then run the optimizer"
pass. That pass writes per-slide font sizes onto slides whose sizing the
stylesheet is designed to supply, and it shrinks type towards the floor where
this workflow splits the slide instead. The two approaches undo each other, and
the stylesheet loses silently because inline styles win. If a Fall 2026 slide
overflows, that is a **content** finding: split it.

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
python .claude/skills/wackerly-slides/scripts/course_plan.py --todo     # only the ones with no slides
python .claude/skills/wackerly-slides/scripts/course_plan.py "16 September"
```

This reads the teaching page directly, so it never drifts from what students see.
It reports the date, topic, reading, the Wackerly sections, whether slides exist,
and flags assessment days.

If the user names a section range instead of a date, use it directly — but still
check the plan, because the topic sentence there is the deck's actual brief.

`NN` in the folder name is the session's **position in the plan**, not the number
of decks built so far. Building 14 before 13 is normal when a week is prepared
out of order; numbering by plan position keeps the folders sorting the way the
semester runs.

Then open the **previous** session's `.qmd` and read its Summary and Next Session
slides. Two consecutive lectures are one argument in two sittings, and the
opening slide of this one should pick up the sentence the last one ended on.
Skipping this is how a semester turns into thirty unrelated decks.

Stop and ask if: the session is an **assessment day** with no teaching, the plan
row has no sections, or slides already exist and it is unclear whether to replace
them.

When a whole week is requested, build the two decks **in plan order, one
finished before the next is started** — the continuity read above depends on the
earlier one being done.

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

A wide range — five or six sections in one sitting — is the plan telling you this
is a survey, not an invitation to cover everything. Find the two or three results
the rest depend on, build the session around those, and let the objectives slide
say plainly which are the load-bearing ones and which the class is meeting only
by name. Seventy-five minutes of complete coverage teaches less than fifty
minutes of one theorem understood.

### 3. Write the deck

Copy `references/deck-template.qmd` into
`lectures/math-stat-1-fall-2026/NN-topic-slug/` as `topic_slug.qmd`. Then, in
that folder:

```bash
cp ../01-what-is-statistics/ADA.png .
cp -r ../01-what-is-statistics/_extensions .   # the quiz plugin; required
```

Shape of a 75-minute session — a spine, not a checklist:

1. 🎬 Video slide: the lecture's intuition video, plus a link to the previous deck (see *3b*)
2. Learning objectives (4–5, each a verb)
3. 🔁 Warm-up from last time: one retrieval quiz question on the previous lecture
4. Where we are: pick up the sentence the last lecture ended on
5. Motivating question in economic terms, before any notation
6. Definitions and theorems, stated as the book states them
7. A worked example done in full at the board's pace
8. An executing R computation, then its figure
9. **Think–Pair–Share with the timer**, roughly at the two-thirds mark
10. An OJS explorable, where a *shape* is the lesson
11. **💰 Case study on real data**: 3 slides, mandatory (see *3a*)
12. Two to four quiz questions
13. Key formulas, summary, next session's reading

Budget **24–32 slides**. Item 10 is the one to drop when nothing in the session
turns on a shape: an explorable built because the list has a slot for one is a
slider students watch you move once. A second worked example is usually the
better use of those three minutes.

On the finance settings: they are the reason the room stays awake, so vary them.
Thirty decks of the same two-asset portfolio stops being a context and becomes
wallpaper. Deposit insurance, loan defaults, ATM queues, claim severities, call
arrivals at a bank branch, exchange-rate moves, ISP outage counts — and keep the
magnitudes ones a Baku student can sanity-check, because a portfolio with an
implausible number in it invites arithmetic instead of statistics. Where a local
setting fits without strain, use it; where it strains, don't force it.

Read `references/interactive-patterns.md` before writing any interactive slide.
It is short, and every pattern in it was rendered and checked on this machine.

The four rules that matter most:

- **R chunks are ` ```{r} `, never ` ```r `.** The latter is a picture of code
  that never runs. This is the defect that prompted this skill. When code is
  meant to be shown rather than run — "this is how you would download the real
  series" beside a chunk that loads the vendored copy — mark it
  ` ```{.r .display-only} `, which `verify_deck.py` recognises and leaves alone.
- **No network calls at render time.** Vendor real data as a CSV in `data/`
  beside the `.qmd` (see *3a*). Simulate with `set.seed(2026)` only for
  illustrations that are not the case study.
- **The timer is R-native**: `countdown::countdown(minutes = 3, top = 0, right = 0)`,
  on its own slide with the question visible.
- **28px font floor, ~130 words or 6 bullets per slide.** Split rather than shrink.

### 3a. The real-data case study (every deck)

This is how Sam's Math Stat II decks worked (see
`lectures/math_stat_2_spring_2026/chapter_5/multivariate_lecture1.qmd`), and the
Fall 2026 decks do the same. A theorem that has never met a real series is a
theorem the class will not recognise at work. The case study is three slides,
titled `## 💰 Case Study: …`. They go after the Think–Pair–Share solution (or
the explorable) and before the quizzes.

1. **Context.** Use a `:::: columns` pair. On the left, a `{.callout-note}` headed
   `## 📈 The question` gives the setting in one sentence and 2–3 numbered
   questions the data will answer. On the right, a `{.callout-tip}` headed
   `## 📊 The data` gives the series, the source, the period and the
   transformation (for example "daily log returns" or "claims per week").
2. **Computation.** One executing `{r}` chunk with `#| code-summary: "📦 …"`. It
   reads the vendored CSV, builds the quantity the lecture is about, and prints
   the few numbers that answer the questions, each estimate beside the model's
   prediction (`mean_Y` next to `np`). Under the chunk, add one 28px sentence
   saying what to look at.
3. **Figure, then "What the data say".** Use a ggplot figure that puts the data
   against the model: `theme_minimal(base_size = 20)`, `fig-width: 10`,
   `fig-height: 3.9`, `echo: false`, with the legend on top. Under it, write two
   sentences starting with **What the data say:**. Say where the model fits, and
   where and why it fails (clustering, fat tails, dependence). An honest "fails
   here" teaches more than a perfect fit.

**Data rules.** The data is real and vendored.

- Put the CSV in a `data/` folder beside the `.qmd`. Add a `SOURCE.md` with one
  line giving the series, publisher, URL, period and download date.
- Trim the CSV to what the chunk uses, under ~300 KB.
- **Never download at render time.** A `{.r .display-only}` chunk may show the
  download so students can repeat it at home.

Reachable, citable sources:

- FRED, via `https://fred.stlouisfed.org/graph/fredgraph.csv?id=…`: SP500,
  VIXCLS, DEXUSEU, DCOILWTICO, DGS10, ICSA, CPIAUCSL, UNRATE and others.
- The World Bank API, for Azerbaijan and its neighbours.
- CBAR's daily AZN rates, at `https://www.cbar.az/currencies/DD.MM.YYYY.xml`.
- ECB euro reference rates.

**Match the series to the distribution:**

| Distribution | Series |
|---|---|
| Bernoulli / binomial | up and down days |
| Geometric | days to the first large loss |
| Poisson | counts of large moves or claims per period |
| Exponential | gaps between large moves |
| Normal vs fat tails | returns |
| Joint / marginal / covariance | two assets |
| Beta / gamma fits | rates and levels |

Vary the setting across the semester. Use an Azerbaijani series (AZN rates, the
World Bank's data for Azerbaijan) where it fits without strain.

### 3b. Continuity and video

- **Video slide.** The slide straight after the title is `## 🎬 The Idea in N Minutes`.
  Write the `<video>` element inside a ```` ```{=html} ```` raw block. A bare
  `<video>…<track …></video>` line makes Pandoc swallow the rest of the deck,
  which then renders as one giant slide.
  - Tracks: English captions (`video/lectureN_intuition.vtt`, `srclang="en"`), and
    Azerbaijani captions once they exist (`video/lectureN_intuition.az.vtt`,
    `srclang="az"`, `label="Azərbaycanca"`).
  - Under the video, add a link line:
    `[⬅ Previous lecture: N−1 · Title](../NN-slug/file.html)`.
  - Videos come from the `lecture-intuition-video` skill. If a deck has no video
    yet, leave the video slide out rather than linking a missing file.
- **Warm-up.** Right after the objectives comes `## 🔁 Warm-up from last time
  {.quiz-question}`. Ask one question that a student can answer only if they
  remember the previous lecture's central result, and give it a
  `data-explanation` that restates that result. Retrieval at the start of class
  is the cheapest well-evidenced gain in retention.


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

The loopback server is not a convenience. Quarto compiles a `file://` guard into
every OJS deck whose `alert()` blocks the renderer's main thread permanently,
which is why `chrome --print-to-pdf`, `--virtual-time-budget`, `?print-pdf` and
bare CDP `Runtime.evaluate` all hang forever on these decks. That diagnosis is
settled and written up in `references/interactive-patterns.md` §5 — **do not
re-derive it, and do not retry those approaches.** The same fact governs the
lecture theatre: double-clicking a deck's `.html` gives dead sliders and dead
plots. Present from the published URL, from `quarto preview`, or from
`python -m http.server`.

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

The deck is driven by a finger on a classroom screen, not by a mouse: a slide
carrying three sliders is a slide nobody adjusts mid-lecture. One control, large,
is worth more than three that are precise.

#### Triage, and when to stop

Not every finding is worth a render. Sort them:

- **Blocking** — anything that puts an error message, a dead control, an
  unreadable line or a chart contradicting its own caption in front of the room.
  Fix all of these.
- **Worth a second pass** — content clipped at an edge, a label wrapping, a
  figure that is right but cramped. Fix while the loop is already running.
- **Cosmetic** — a few pixels of asymmetry, a legend you would place elsewhere.
  Leave them. The deck is for a 75-minute lecture, not a print journal.

If a finding survives **three** render-and-look cycles, stop tuning and change
the approach instead: split the slide, drop the explorable, draw the figure in R
rather than OJS, or cut the slide. Continuing to adjust CSS past that point has
never once been the shorter path, and the sunk time is invisible until it is
large.

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

#### What this step has already caught

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

### 6. Publish it

The lecture is given from a URL on the classroom screen, so this step is what
turns a correct deck into a usable one.

**First, sweep the stale theme CSS.** Every edit to `slide-fit.scss` makes Quarto
emit a **new** hashed stylesheet into each deck's
`_files/libs/revealjs/dist/theme/` and leave the previous one behind. A few
rounds of fix-and-re-render and there are a dozen orphans per deck, all of them
untracked junk that will otherwise be committed. Keep only the one the HTML
actually references:

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

**Then commit the rendered deck, not just its source.** The site serves the
built HTML, so the commit carries `topic_slug.qmd`, `topic_slug.html`, the whole
`topic_slug_files/` tree, `ADA.png`, `_extensions/`, and any vendored `data/`
CSV. It must not carry `<deck>_qa/`, the extracted book text, or anything out of
`local/`. Check `git status` before staging rather than after.

**Then push, and open the published URL once.** A deck that works on loopback can
still be broken by the site build — a static-site generator that ignores
underscore-prefixed paths is the classic way for a deck's assets to vanish
between `git push` and Wednesday morning. Load the published page, step to a
slide with a slider, and move it. Thirty seconds now, or a dead explorable in
front of three sections later.

### 7. Link it from the course plan

Replace that session's `<td class="muted-cell">&mdash;</td>` in
`_teaching/2026-fall-mathematical-statistics-I.md` with:

```html
<td><a class="slide-link" href="/lectures/math-stat-1-fall-2026/NN-topic-slug/topic_slug.html" target="_blank">Slides &rarr;</a></td>
```

Confirm with `course_plan.py "<date>"` that the session now reports `[slides]`.

---

## Toolchain

Check rather than assume — an uninstalled package is an error message on the
projector:

```bash
quarto --version && Rscript --version
Rscript -e 'for (p in c("knitr","rmarkdown","ggplot2","dplyr","tidyr","zoo",
  "readr","kableExtra","countdown")) if (!requireNamespace(p, quietly=TRUE)) cat("MISSING:",p,"\n")'
python -c "import fitz, playwright, PIL; print('python deps ok')"
```

Last verified on this machine: Quarto 1.10.18, R 4.6.0 with all of the above,
Python 3.14 with PyMuPDF (for `extract_section.py`) and Playwright + Pillow with
the Chromium build installed (for `qa_slides.py`).

If Playwright is missing on another machine:

```bash
python -m pip install playwright pillow
python -m playwright install chromium
```

Claude's cloud container also renders these decks (`pip install quarto-cli` gives Quarto 1.10.18; R from apt; packages from the Posit binary repo).

**Not** installed on ooklapc: `quantmod`, `tidyverse`, `xts`, `patchwork`, `gt`. Either
install one and say so, or write the chunk in base R and `ggplot2` — a slide
that needs a package the lecture machine does not have fails at the worst
possible moment, in front of the room.