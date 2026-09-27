# CLAUDE.md

Working notes for this repository — `sorujov/sorujov.github.io`, the Jekyll site
behind [sorujov.net](https://sorujov.net). Read this before changing anything; it
records the decisions that are not obvious from the code.

## The site

Academicpages/Jekyll, branch `master`, published by GitHub Pages. Local copy on
Sam's machine at `C:\Users\ookla.user\Desktop\GITHUB\sorujov.github.io`.

- **Theme**: `site_theme: editorial` in `_config.yml`. Warm paper background,
  Newsreader display serif, Inter for UI, claret accent (`#8b2635` light,
  `#e0919a` dark).
- **Colours are tokens.** `_sass/theme/_editorial_{light,dark}.scss` define CSS
  custom properties (`--paper`, `--ink`, `--accent`, `--rule`, …). Use the
  tokens in new stylesheets and light/dark works for free. Never hard-code a hex.
- **New stylesheet?** Add the partial to `_sass/layout/` *and* register it in
  `assets/css/main.scss`, which is the only import list.
- **Navigation** is `_data/navigation.yml`. The masthead deliberately uses
  `id="primary-nav"` to avoid the theme's greedy-nav JavaScript, which used to
  hide the dropdown buttons. Do not rename that id.
- **Preview**: `python preview.py` serves the pre-built `_preview/` folder on
  :4000. For a real build, `bundle exec jekyll serve` or `docker compose up`.

### Courses

`_teaching/` holds one file per course. The current one carries `current: true`;
finished ones carry `archived: true` and a `term`. To roll a semester over, flip
those two flags. `/teaching/` renders "Now teaching" and an "Archive"; the home
page shows only current courses.

The Fall 2026 page, `_teaching/2026-fall-mathematical-statistics-I.md`, is the
**single source of truth for course facts**. Dates on it have changed since
earlier notes were written — Quiz I is 17 October, Midterm II is 23 December,
problem sets are two a week. Never copy these into code; read them from the page.

Lecture decks live under `lectures/math-stat-1-fall-2026/<nn-slug>/` as Quarto
`.qmd` plus rendered `.html`. Slides marked `{.quiz-question}` contain the
in-class poll answers in `[…]{.correct}` spans.

## The site assistant

A chatbot that runs entirely in the visitor's browser. It started as a STAT-2311
course assistant and now covers the whole site: on the course page it prefers
the course material, everywhere else it answers about Sam's research,
publications, talks, CV and teaching as well. Nothing is sent to a server,
nothing is logged, and the site stays static.

### Shape

```
question
  ├─ guard      refuse: grades, extensions, worked solutions, exam speculation,
  │             private details (phone, salary, family)
  ├─ facts      deterministic answers extracted from the course page, home page and CV
  ├─ retrieve   BM25 + MiniLM cosine over the corpus, fused by RRF; the page's
  │             scope gets a small bonus; "give me an example" leads with the
  │             topic lecture's worked slides
  └─ floor      refuse when nothing retrieved is close enough
```

Every passage and fact has a `scope`: `course` (STAT-2311 page and lectures) or
`site` (everything else). A page sets `chat_scope: course` in its front matter
to prefer the course; the preference is a ranking nudge, never a filter.

Generation is **optional and strictly downstream**: an opt-in WebLLM model
rewrites retrieved passages into prose and is never allowed to answer from its
own weights. A student who never presses that button still gets every answer.
It only ever writes from **course** material: anything about Sam himself (home
page, CV, publications) is shown as quotes and never paraphrased (`canWrite`).
Nor does it write when the answer *is* a formula ("formula", "definition",
"notation" in the question), and formula-sheet passages (over 40% maths, not a
worked example) are never handed to it: a 0.6B model loops over them. Worked
examples always qualify, since a walkthrough is what it is for.

### Files

| path | what it is |
|---|---|
| `scripts/build_chat_index.py` | builds everything in `assets/chat/` from the course page, the `.qmd` lectures, `_pages/about.md`, `_pages/cv.md`, `_publications/`, `_talks/`, `_portfolio/` and the other `_teaching/` pages |
| `assets/chat/` | generated: `facts.json`, `chunks.json`, `lexical.json`, `embeddings.bin`, `meta.json` (~1.1 MB, fetched on the first question) |
| `assets/js/course-chat-core.js` | retrieval — pure functions, no DOM, shared with the evaluation |
| `assets/js/course-chat.js` | the widget: UI, model loading, optional generation |
| `_sass/layout/_course-chat.scss` | styles, editorial tokens only |
| `_includes/course-chat.html` | the include; `_layouts/default.html` puts it on every page as a bottom-left launcher that never opens by itself. `chat: false` in front matter opts a page out (attendance check-in, `/teaching/ask/`); `chat_scope: course` prefers STAT-2311 |
| `_pages/ask.md` | standalone page at `/teaching/ask/` |
| `scripts/eval/` | golden set, offline harness, browser checks, cluster benchmark |
| `.github/workflows/rebuild-chat-index.yml` | rebuilds and evaluates the index on GitHub after any indexed page changes and after every ORCID run; commits only if every gate passes and the passages or facts changed |
| `scripts/requirements-chat.txt` | Python packages for the index build |

### Rules that matter

1. **Never hand-write a fact.** Every date, weight, room and deadline is
   extracted from the course page by `extract_facts`, and every fact about Sam
   from the home page and CV by `extract_site_facts`. The key lists name
   *phrasings*, never answers. If something is wrong on the site, fix the site
   and rebuild. Other courses' pages give passages only, never facts: their
   dates would collide with the current course's.
2. **The index rebuilds itself.** `rebuild-chat-index.yml` runs on GitHub
   whenever an indexed page, publication or lecture changes, and after every
   ORCID run. Rebuilding locally (`python3 scripts/build_chat_index.py`) is
   still how to check a change before pushing. If the workflow fails, the
   evaluation caught something: the live index is the previous one, and the
   run's summary shows which gate failed.
3. **The two tokenizers must agree.** `tokenize()` exists in both
   `build_chat_index.py` and `course-chat-core.js`. The stop list ships inside
   `lexical.json` so it cannot drift, and `lexical.probe` holds sample
   tokenisations the evaluation asserts against. If you touch one tokenizer,
   touch the other and run the evaluation.
4. **Quiz slides are excluded from the index** — they carry the poll answers.
   The filter keys on `{.quiz-question}`; if the decks adopt a new marker, update
   `QUIZ_HEADING` and `qmd_passages`.
5. **The guard runs before the facts.** Otherwise "give me the answers to week 6"
   matches the week 6 reading and answers helpfully.
6. **Embeddings come from the same quantised ONNX the browser downloads**
   (`Xenova/all-MiniLM-L6-v2`, q8), so build-time and query-time vectors cannot
   diverge. Do not switch the Python side to `sentence-transformers`.
7. **Model weights never enter the repo.** GitHub blocks files over 100 MB and
   the Pages site has a ~1 GB budget; WebLLM and transformers.js fetch from their
   own CDNs, so the site serves only the ~1.1 MB index.
8. **Quotes are verbatim.** A passage's `text` is the site's own words. What a
   passage is about ("Samir Orujov, CV") goes in its `context`, which is
   indexed for search and never shipped. The CV's phone and address lines are
   never indexed (`PRIVATE_LINE`).

### Checks

```bash
python3 scripts/build_chat_index.py        # rebuild the index
python3 scripts/eval/embed_queries.py      # embed the golden questions
node     scripts/eval/run_eval.mjs         # retrieval gates; non-zero on failure
python3  scripts/eval/browser_check.py     # drive the real widget in Chromium
```

`run_eval.mjs` gates at 95% logistics, 85% content, 90% refusal and 90% site,
and exits non-zero, so it is usable as a CI step. Course cases run in course
scope, site cases in site scope; content cases marked `worked` also require the
first passage to be a worked example, and a short list of ordinary questions
("a family with three children") must get past the privacy guard. It imports `course-chat-core.js`
directly: what it measures is what visitors get. As of 26 September 2026 all
117 cases pass, and the 84 course cases also pass when asked in site scope.

### The cluster

`scripts/eval/bench/` benchmarks candidate in-browser models on the only
question that matters for the generation layer — can the model carry an exact
figure through without altering it, invent nothing, and decline when the context
does not contain the answer. Every score is decided by regex, so results are
reproducible and no model judges another.

The IRISA/LMBA tools upload from Sam's Windows machine, so when this session has
no folder connected, drive the cluster from GitHub instead: push the branch,
`git clone` it on the login node, and submit with `sbatch` through
`cluster_run`. Environment: `~/claude_jobs/chatbench/venv`
(torch 2.4.1+cu118, transformers 4.57). Use `cluster_inventory` to find a free
GPU before submitting; sn5 has the A100s.

The widget runs **Qwen3-0.6B** (`Qwen3-0.6B-q4f16_1-MLC`, q4f32 on GPUs without
shader-f16, 335 MB), the only model that declined all 12 out-of-context questions
while keeping 24/24 figures exact. Thinking mode is off, as in the benchmark.

`gemma-3-1b-it` and `Llama-3.2-1B-Instruct` are gated on the Hub and need an
accepted licence plus `HF_TOKEN` to benchmark. Their MLC builds are not gated,
so the browser can still run them.

### History: from course assistant to site assistant (26 September 2026)

Sam asked for the whole site after a live session showed: "Who is Samir
Orujov?" refused; "what is his background" matched the one-line Instructor fact
and the model said it was "not provided in the CONTEXT"; "an example of
conditional probability with calculations" returned the definition four ways;
generated maths came out as raw `$…$`; "Related material" listed a link twice.
Each has a fix and a golden case: site corpus and facts; a prompt that never
names its inputs; `workedFirst` in the core; `texDelimiters` in the widget
(prices such as "$5" are left alone); related material limited to the fact's
own page and deduplicated. Later the same day: `$ r $` with padding now
renders, R comments inside code chunks no longer split slides (`qmd_passages`),
and "example" questions anchor on the lecture whose title names the topic.

## Plan: STAT-2311 deck upgrade (started 27 September 2026)

Sam's brief: the Fall 2026 decks lack the real-data case studies his Math Stat II
decks had; add them, update the `wackerly-slides` skill so every future deck
gets one, add anything else that helps students understand, link each video to
the previous lecture, and offer an Azerbaijani option. Claude works through
this autonomously and ticks items off here.

**Status on 27 September:** 29 decks exist (01–13, 15–30; there is no 14).
Decks 01–19 have a "🎬 The Idea in N Minutes" video slide. Only 01 and 02 have
a case study, and both use simulated data or a live Yahoo call.

### 1. Real-data case study in every deck
- The pattern follows `lectures/math_stat_2_spring_2026/chapter_5/multivariate_lecture1.qmd`.
  It is 2–3 slides titled `## 💰 Case Study: …`, placed after the Think–Pair–Share
  solution and before the quizzes:
  1. **Context.** Two callouts side by side. Left (`callout-note`): the setting and
     2–3 key questions. Right (`callout-tip`): the data source, the series, the
     period and the transformation.
  2. **Data and computation.** An executing `{r}` chunk with `code-fold: true` that
     reads a vendored CSV and prints the numbers that answer the questions.
  3. **Figure + "What the data say".** A figure, followed by 2–3 sentences that
     tie the output back to the lecture's theorem. They must also name where the
     model fits and where it fails.
- **Data is real and vendored.** Each deck has a `data/` folder beside the `.qmd`
  holding a CSV and a one-line `SOURCE.md`. Sources: FRED (S&P 500, VIX, EUR/USD,
  WTI, Treasury yields, claims, CPI), World Bank, and any other public source.
  **There are no network calls at render time.** A `{.r .display-only}` chunk may
  show how to re-download the data.
- Settings vary across the semester and stay finance and economics. Where a real
  series fits the distribution, use it (daily up/down days as Bernoulli trials,
  large-move counts as Poisson, returns vs the normal, and so on).
- Decks 01–02 are switched from simulated or live data to the vendored FRED S&P 500.

### 2. Continuity and retrieval
- The video slide gets a line "⬅ Previous lecture: N−1 · title", linking to the
  previous deck.
- A **"🔁 Warm-up from last time"** quiz slide goes right after the objectives.
  It asks 1–2 retrieval questions on the previous lecture. This uses the existing
  quiz plugin and is evidence-based retrieval practice.

### 3. Videos
- Intuition videos are made for decks 20–30, using the same Manim + ElevenLabs
  pipeline (`_videos/`). The budget is about 2.2k characters per video.
- **Azerbaijani option.** Every video gets an Azerbaijani caption track (`.az.vtt`,
  selectable from CC), translated by hand, not machine-translated. Next comes an
  Azerbaijani narration: re-render with `eleven_v3` in Azerbaijani and add an
  EN/AZ switch on the video slide. This is staged by the ElevenLabs monthly quota.
- **YouTube** (optional mirror): it would add auto-translated captions and native
  multi-audio. It needs Sam's channel sign-in, and the decks keep self-hosted
  video so they don't depend on it.

### 4. Skill
- `.claude/skills/wackerly-slides/SKILL.md` gets the case-study pattern, the
  data-vendoring rule, the warm-up slide, the video slide with the previous-lecture
  link and the Azerbaijani captions. The account copy is updated via a skill
  proposal.

### How it is built
- Decks are rendered in Claude's cloud container: Quarto 1.10.18 (pip `quarto-cli`),
  R 4.3 with the packages the decks use, and the rendered pages are checked
  slide by slide with `qa_slides.py`.
- Pushes go from the sparse clone on ooklapc, as with the videos. Afterwards the
  local copy at `Desktop\GITHUB\sorujov.github.io` is fast-forwarded.

### Progress
- [x] Piloted the case study on deck 11 and settled the pattern (27 Sep)
- [x] Skill updated: repo copy committed; account copy proposed to Sam (27 Sep)
- [x] Case studies for decks 03–30; decks 01–02 moved to vendored FRED data (27 Sep)
- [x] Previous-lecture links and warm-up slides in every deck (27 Sep)
- [x] Azerbaijani captions for videos 01–19 (27 Sep)
- [x] Videos for decks 20–30 (27 Sep)
- [x] Azerbaijani captions for videos 20–30 (27 Sep)
- [ ] Azerbaijani narration: waiting for Sam to choose a voice. The first clone
  (made from his English-plus-poem sample) did not sound like him in
  Azerbaijani. On 27 Sep he recorded about 3.5 min of Azerbaijani, and a
  separate clone, `ELEVENLABS_VOICE_ID_AZ`, was trained on it; samples F (v3)
  and G (multilingual v2) were sent to him.
  - Sam judged Claude's Azerbaijani weak and corrected the lecture 11 text
    with Gemini. Before generating any narration, have Sam or a native reader
    correct the `az_lN.json` scripts.
  - Scripts: one clip per animation block. `common.py` narrates from one when
    `NARRATION_MAP` points at it.
- [ ] Sam's local copy: fast-forward it to origin/master

### Lessons
- A bare `<video>…<track>…</video>` line in a `.qmd` swallows the rest of the
  deck. Wrap it in a ```` ```{=html} ```` block.
- Quarto leaves an orphaned `quarto-syntax-highlighting-*.css` behind on
  re-render, as it does with the theme CSS. Sweep both.

## Conventions

- Prose on this site is written, not generated-sounding. Short sentences, no
  throat-clearing, no "in today's fast-paced world".
- Do not characterise earlier work as wrong in public-facing copy; state what is
  the case now.
- Commit messages: plain imperative, no emoji except the existing ORCID bot's.
- `_config.yml` excludes `lectures/math_stat_2_spring_2026/aa_wackerly-to-qmd`,
  which contains the full textbook PDF. Keep it excluded.

## Known open items

- The generation prompt changed on 26 September 2026 (no "CONTEXT", worked
  examples allowed, `\( \)` maths). Qwen3-0.6B was benchmarked on the old one;
  re-run `scripts/eval/bench/` with the new prompt when the cluster is next free.
- Generation has not been seen end to end on a GPU from this machine; Sam's
  laptop downloads and loads the model.
- The CV shows `Phone: +994 51 xxx xx xx`, a placeholder, publicly. The
  assistant never indexes it.

- The Wackerly textbook PDF is still in git history; `git rm --cached` would
  clean the working tree but not the history.
- Four homework links on the Fall 2025 page point at a `/downloads/` folder that
  does not exist (pre-existing 404s).
- `images/profile.jpg` is a conference photo; a plain portrait would sit better
  in the hero frame.
