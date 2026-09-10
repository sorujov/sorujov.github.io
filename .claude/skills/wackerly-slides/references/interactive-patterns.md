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

### An OJS deck must be opened over HTTP

Quarto compiles this guard into every deck that contains an OJS cell:

```js
if (window.location.protocol === "file:") { alert("The OJS runtime does not
work with file:// URLs. Please use a web server to view this document."); }
```

Two consequences, and both have cost time already:

1. **In class, do not double-click the `.html`.** Over `file://` the sliders
   are inert and the plots never draw — you get a modal alert and a dead
   slide. Present from `quarto preview`, from `python -m http.server` in the
   repository root, or from the published site.
2. **Nothing headless can drive such a deck over `file://`.** An `alert()`
   blocks the renderer's main thread for good, so `--print-to-pdf`,
   `--virtual-time-budget`, `?print-pdf` and bare CDP `Runtime.evaluate` all
   hang and the renderer is eventually killed. `scripts/qa_slides.py` starts
   its own loopback server for exactly this reason. Do not spend time
   re-diagnosing it as "OJS keeps the event loop busy" — it is a dialog.

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

### The binX reducer trap

Lecture 1 shipped this, and it is worth understanding because it fails
*silently and convincingly*:

```js
// WRONG — every bar drawn full height, y-axis showing only 0.00
Plot.rectY(sample, Plot.binX(
  {y: (bin, all) => bin.length / all.length},
  {x: d => d, thresholds: n_bins}
))
```

A custom reducer passed as a function is called as `f(data, extent)`. The
second argument is that bin's `{x1, x2}` extent — **not** the whole dataset.
So `all.length` is `undefined`, every `y` is `NaN`, the y-scale collapses, and
Plot draws a row of identical full-height bars with a single `0.00` tick. It
looks like a rendered chart, so nothing downstream complains.

Use the built-in reducer, which is what it is for:

```js
// RIGHT
Plot.rectY(sample, Plot.binX(
  {y: "proportion"},                  // count in bin / total count
  {x: d => d, thresholds: n_bins}
))
```

`"count"`, `"proportion"` and `"proportion-facet"` cover nearly every histogram
you will want. Reach for a custom reducer only when none of them fit, and then
write it as `{reduce(index, values, extent) {...}}` so the arguments are
explicit.

**A histogram whose bars are all the same height is broken, not uniform.**
Check it in the QA images.

### A fixed axis domain needs comparable spreads

An explorable that switches between generated shapes usually pins the axis —
`x: {domain: [-8, 8]}` — so the picture does not jump when the student moves a
slider. That is right, but it makes the generators' *scales* part of the
design.

Lecture 2 shipped this trio:

```js
if (shape === "mound-shaped")      out.push(0.05 + 1.2 * norm());   // s ~ 1.2
else if (shape === "skewed right") out.push(Math.exp(0.35*norm())-1); // s ~ 0.37
else                               out.push(1.2*norm()*(rng()<0.06?4:1)); // s ~ 1.7
```

On a fixed ±8 axis the skewed case occupied about a tenth of the width — a
narrow spike with no visible tail, on the one slide whose whole purpose was to
show what right skew does to coverage. Every automated check passed: the data
were real, the axis was real, the bars varied in height.

Scale each generator to roughly the same standard deviation:

```js
else if (shape === "skewed right") out.push(2.3 * (Math.exp(0.45*norm()) - 1)); // s ~ 1.2
```

The rule: **if the axis is fixed, the shapes must be comparable in spread.**
Otherwise let the domain follow the data and accept the jump. Either way this
is visible only in the QA images — check every setting of the control, not
just the one the slide loads with.

### Sizing and inputs

- **Observable Inputs need their own font size.** `slide-fit.scss` sets the root
  to 46px, and the Inputs label column is a fixed 120px. "Sample size n:" wraps
  to three lines at that size and shoves the plot off the canvas. The stylesheet
  now scales those controls down and widens the label column; if you build
  inputs some other way, check them in the QA images.

- **Set `style: {fontSize: "18px"}` on every `Plot.plot`.** Plot's default is
  10px. It is fine on a laptop and invisible from the back of a lecture
  theatre, and because the chart is drawn correctly nothing else complains.
  Widen `marginLeft`/`marginBottom` to about 78/58 to fit the larger ticks.

- **Height 330 or less, width up to 1150.** The canvas is 720px tall and the
  content box 1152px wide; a heading, three controls and a 380px plot
  overflow, and reveal.js clips silently rather than scrolling.
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
