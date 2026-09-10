# Interactive patterns that actually work

Every pattern here was rendered and inspected on this machine before being
written down. Anything not on this list has not been tested — test it in a
scratch deck before it reaches a lecture.

---

## 1. R that runs (the mistake to never repeat)

The first Fall 2026 deck shipped an R "case study" that never executed. The
chunk was fenced:

<pre>
```r
library(quantmod)
getSymbols("^GSPC", ...)
```
</pre>

A fence of ` ```r ` is a **display block**: Quarto syntax-highlights it and
renders nothing else. There is no error, no warning, and the slide looks
finished. The executable form is ` ```{r} `.

```
```r        -> a picture of code          WRONG
```{.r}     -> a picture of code          WRONG
```{r}      -> code that runs             RIGHT
```

Two supporting requirements:

- `engine: knitr` in the frontmatter. Without it Quarto infers the engine, and
  a deck that also contains OJS can end up on a path where R is not run.
- `execute: echo: true`. Students should see the code beside its output.
  Use `#| echo: false` per chunk for figures, where the code is noise.

Verify with `scripts/verify_deck.py`, which fails the build if executable
chunks produced no output.

---

## 2. Never call the network from a slide chunk

The same case study called `getSymbols("^GSPC")` — a live Yahoo download at
render time. Three separate problems:

1. It fails whenever the network, the VPN or the API is having a bad day, and
   it fails during the render before class, not now.
2. The numbers change between renders, so what you said last year about "the
   mean is 0.05" silently stops being true.
3. `quantmod` is not installed here anyway.

Use one of these instead:

**Simulate with a fixed seed** — best for illustrating a distribution:

```{r}
set.seed(2026)
returns <- rnorm(500, mean = 0.05, sd = 1.2)
```

**Vendor the data** — best when real data is the point. Download once, save a
CSV next to the `.qmd`, and commit it:

```{r}
returns <- readr::read_csv("data/sp500-returns.csv", show_col_types = FALSE)
```

If students should see how the data was obtained, show the download code in a
**non-executing** block, clearly labelled, and load the vendored copy in the
executing one. That is the one legitimate use of ` ```r `.

---

## 3. Think–Pair–Share timer (R-native, top right)

`countdown` generates a self-contained HTML/JS timer from R, so it renders
into the deck and runs offline — no switching to a phone or a browser tab.

```{r}
#| echo: false
countdown::countdown(
  minutes = 3, seconds = 0,
  top = 0, right = 0,       # top-right corner of the slide
  font_size = "2em",
  warn_when = 30            # turns amber for the last 30 seconds
)
```

Click the timer to start it; click again to pause. Verified: it emits
`class="countdown"` plus `countdown.js`/`countdown.css` into the deck's
`_files/libs/countdown-0.6.0/` folder.

Install once if missing: `install.packages("countdown")`.

Timings that work in a 75-minute session: 1 min think, 1 min pair, 1 min
share. Set `minutes = 3` and let the whole cycle run on one timer, or place
separate timers on separate slides for a longer activity.

Give the timer its own slide with the question visible. A timer on a slide
the class has already moved past is a timer nobody starts.

---

## 4. Quiz questions

The `parmsam/quiz` extension. It requires **both** of:

- `revealjs-plugins: [quiz]` in the frontmatter, and
- an `_extensions/parmsam/quiz/` folder beside the `.qmd`.

Declaring the plugin without the folder renders the question as an inert
bullet list — it looks like a quiz and does nothing. `verify_deck.py` checks
for both, and that `quiz.js` reached the HTML.

Syntax (the correct option is a bracketed span with `.correct`):

```markdown
## Q1: Which of these is a statistic? {.quiz-question}

- The population mean μ
- [The sample mean x̄]{.correct data-explanation="A statistic is computed from the sample; μ is a fixed unknown parameter of the population."}
- The population variance σ²
- The true default rate
```

`data-explanation` is worth writing properly: it is what a student reads at
the moment they are most receptive, having just been wrong.

Copy the extension into a new deck folder with:

```bash
cp -r ../01-what-is-statistics/_extensions .
```

---

## 5. OJS for exploration

OJS runs in the browser, so students can drag a slider during the lecture.
Use it where the *shape* of a change is the lesson (sample size, a rate
parameter, the number of histogram classes) — not where a single number is.

```{ojs}
//| echo: false
viewof n = Inputs.range([5, 200], {step: 1, value: 30, label: "Sample size n"})
```

```{ojs}
//| echo: false
sample = Array.from({length: n}, d3.randomNormal(0, 1))
```

```{ojs}
//| echo: false
Plot.plot({
  width: 1050, height: 320, marginLeft: 60,
  x: {label: "Value"}, y: {label: "Density"},
  marks: [
    Plot.rectY(sample, Plot.binX({y: "proportion"}, {x: d => d, fill: "#8ba3c7"})),
    Plot.ruleY([0])
  ]
})
```

Rules learned the hard way:

- **Height 320 or less.** The canvas is 720px tall; a heading, a slider and a
  380px plot overflow, and reveal.js clips silently rather than scrolling.
- `viewof` is what makes it interactive. OJS cells with no `viewof` are just a
  slower way to draw a static chart — use R for those.
- OJS cells are reactive and order-independent, but keep the definition above
  the use anyway; a reader of the source is not a reactive runtime.
- R and OJS do not share variables. Data must be defined in the OJS block, or
  passed with `ojs_define()`.

---

## 6. Fitting the canvas

`../slide-fit.scss` is applied by every Fall 2026 deck. It sets the root font
to 46px and centres content vertically inside the full-height section, which
is why sparse slides no longer sit in the top third.

Consequences for authoring:

- The floor is **28px**. Below that the back row cannot read it. Split the
  slide instead of shrinking the type — `verify_deck.py` enforces this.
- Budget roughly **130 words or 6 bullets** per slide. Also enforced.
- A genuinely long slide gets `{.scrollable}`, which the stylesheet switches
  back to top-aligned so the first line is not clipped.
- `r-stretch` and columns work unchanged; the flex centring only touches the
  vertical axis.
