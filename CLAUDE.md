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

## The course assistant

A chatbot for STAT-2311 that runs entirely in the student's browser. Nothing is
sent to a server, nothing is logged, and the site stays static.

### Shape

```
question
  ├─ guard      refuse: grades, extensions, worked solutions, exam speculation
  ├─ facts      deterministic answers extracted from the course page
  ├─ retrieve   BM25 + MiniLM cosine over the corpus, fused by RRF
  └─ floor      refuse when nothing retrieved is close enough
```

Generation is **optional and strictly downstream**: an opt-in WebLLM model
rewrites retrieved passages into prose and is never allowed to answer from its
own weights. A student who never presses that button still gets every answer.

### Files

| path | what it is |
|---|---|
| `scripts/build_chat_index.py` | builds everything in `assets/chat/` from the course pages and `.qmd` sources |
| `assets/chat/` | generated: `facts.json`, `chunks.json`, `lexical.json`, `embeddings.bin`, `meta.json` (~270 KB) |
| `assets/js/course-chat-core.js` | retrieval — pure functions, no DOM, shared with the evaluation |
| `assets/js/course-chat.js` | the widget: UI, model loading, optional generation |
| `_sass/layout/_course-chat.scss` | styles, editorial tokens only |
| `_includes/course-chat.html` | drop-in include |
| `_pages/ask.md` | standalone page at `/teaching/ask/` |
| `scripts/eval/` | golden set, offline harness, browser checks, cluster benchmark |

### Rules that matter

1. **Never hand-write a fact.** Every date, weight, room and deadline is
   extracted from the course page by `build_chat_index.py`. The synonym lists in
   `extract_facts` name *phrasings*, never answers. If a date is wrong on the
   site, fix the site and rebuild.
2. **Rebuild after editing a course page or a lecture**:
   `python3 scripts/build_chat_index.py`.
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
   own CDNs, so the site serves only the ~270 KB index.

### Checks

```bash
python3 scripts/build_chat_index.py        # rebuild the index
python3 scripts/eval/embed_queries.py      # embed the golden questions
node     scripts/eval/run_eval.mjs         # retrieval gates; non-zero on failure
python3  scripts/eval/browser_check.py     # drive the real widget in Chromium
```

`run_eval.mjs` gates at 95% logistics, 85% content, 90% refusal and exits
non-zero, so it is usable as a CI step. It imports `course-chat-core.js`
directly: what it measures is what students get.

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

`gemma-3-1b-it` and `Llama-3.2-1B-Instruct` are gated on the Hub and need an
accepted licence plus `HF_TOKEN` to benchmark. Their MLC builds are not gated,
so the browser can still run them.

## Conventions

- Prose on this site is written, not generated-sounding. Short sentences, no
  throat-clearing, no "in today's fast-paced world".
- Do not characterise earlier work as wrong in public-facing copy; state what is
  the case now.
- Commit messages: plain imperative, no emoji except the existing ORCID bot's.
- `_config.yml` excludes `lectures/math_stat_2_spring_2026/aa_wackerly-to-qmd`,
  which contains the full textbook PDF. Keep it excluded.

## Known open items

- The Wackerly textbook PDF is still in git history; `git rm --cached` would
  clean the working tree but not the history.
- Four homework links on the Fall 2025 page point at a `/downloads/` folder that
  does not exist (pre-existing 404s).
- `images/profile.jpg` is a conference photo; a plain portrait would sit better
  in the hero frame.
