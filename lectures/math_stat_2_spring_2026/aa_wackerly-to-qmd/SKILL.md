---
name: wackerly-to-qmd
description: Convert Wackerly Mathematical Statistics textbook chapters into interactive Quarto RevealJS lecture slides. Use when creating QMD presentation files from Wackerly book content, including splitting chapters into 2-3 logical lecture units with learning objectives, interactive visualizations, R/OJS code examples, quizzes, and financial case studies. Input is book chapter content (PDF pages or text); output is multiple .qmd files following Dr. Samir Orujov's lecture format for ADA University.
---

# Wackerly to QMD Lecture Converter

Convert Wackerly's "Mathematical Statistics and Applications" (7th Edition) textbook chapters into interactive RevealJS lecture presentations.

## 🎓 Target Audience

**Students:** Finance and Economics majors at ADA University

**Implication:** ALL examples, case studies, and practice problems should have **financial or economic context**. Abstract mathematical examples from Wackerly should be transformed into relatable finance/econ scenarios.

---

## Quick Start Workflow

When creating lectures from a chapter:

1. **Extract the chapter content** from the uploaded PDF using pymupdf
2. **Read the chapter text** to identify definitions, theorems, examples, and figures
3. **Split into 2-3 lectures** based on logical content breaks
4. **Transform content** into QMD slides following the templates
5. **Transform examples** into finance/economics contexts
6. **Add interactive elements**: OJS visualizations, R case studies, quizzes
7. **Include financial applications** relevant to each topic
8. **Run autopilot optimization**: compile → check fonts → fix → recompile

---

## 🎯 Critical Design Requirements

### Font Size Requirements (MANDATORY)
- **Minimum font size: 30pt equivalent (0.75em)** for back-row visibility
- Always prioritize readability over fitting more content
- When in doubt, go LARGER

### Revealjs Font Size Reference
| CSS em value | Approximate pt | Use Case |
|--------------|----------------|----------|
| `0.6em` | ~24pt | ❌ Too small - NEVER use |
| `0.75em` | ~30pt | ✅ Minimum acceptable |
| `0.85em` | ~34pt | ✅ Good for dense slides |
| `1.0em` | ~40pt | ✅ Preferred for text |
| `1.2em` | ~48pt | ✅ Great for key points |

### Case Study Font Sizes
| Slide Type | Font Size | Notes |
|------------|-----------|-------|
| Data loading | `30px` | One R chunk per slide with `code-fold: true` |
| Visualization | `30px` | Separate slide for plots, `code-fold: true` |
| Analysis | `30px` | Two-column layout OK with `code-fold: true` |
| Key Findings | `45px` | `callout-important`, three 33% columns with fragments, NO `{.smaller}` class |
| Summary | `30px` | No `{.smaller}` class needed |

### Content Strategy
- **Split slides** when content is dense rather than shrinking text
- One concept per slide is better than cramped content
- Use `{.smaller}` class sparingly, only for interactive slides with controls
- Maximum 80 words per slide
- Maximum 5 bullet points per slide

---

## Accessing the Book

### Method 1: Uploaded PDF (Preferred)

When the user uploads the Wackerly PDF (`Mathematical_Statistics_-_7th_Edition_-_Wackerly.pdf`):

1. **Use the extraction script** to get chapter content:
```bash
python scripts/extract_wackerly.py /path/to/wackerly.pdf ch6
# Or specific pages:
python scripts/extract_wackerly.py /path/to/wackerly.pdf 320 340
```

2. **Or extract directly with pymupdf**:
```python
import fitz
doc = fitz.open('/mnt/user-data/uploads/Mathematical_Statistics_-_7th_Edition_-_Wackerly.pdf')
# Extract pages (0-indexed)
for page_num in range(start-1, end):
    text = doc[page_num].get_text()
```

3. **Check `references/wackerly-chapters.md`** for page numbers and content structure

### Chapter Page Numbers (PDF pages)
| Chapter | Title | Pages |
|---------|-------|-------|
| 1 | What Is Statistics? | 25-43 |
| 2 | Probability | 44-109 |
| 3 | Discrete Random Variables | 110-180 |
| 4 | Continuous Variables | 181-246 |
| 5 | Multivariate Distributions | 247-319 |
| 6 | Functions of Random Variables | 320-369 |
| 7 | Sampling Distributions & CLT | 370-413 |
| 8 | Estimation | 414-467 |
| 9 | Point Estimators & Estimation Methods | 468-511 |
| 10 | Hypothesis Testing | 512-586 |
| 11 | Linear Models | 587-663 |
| 12 | Designing Experiments | 664-684 |
| 13 | Analysis of Variance | 685-736 |
| 14 | Categorical Data | 737-764 |
| 15 | Nonparametric Statistics | 765-819 |
| 16 | Bayesian Methods | 820-844 |

### Method 2: Web Search (Fallback)
If PDF not available, use web_search: `"Wackerly Mathematical Statistics" "Definition X.Y"`

---

## YAML Frontmatter Template

```yaml
---
title: "Mathematical Statistics"
subtitle: "Topic Name Here"
author:
  - name: "Samir Orujov, PhD"
    affiliations:
      - name: "ADA University, School of Business"
      - name: "Information Communication Technologies Agency, Statistics Unit"
date: today
format:
  revealjs:
    theme: default
    logo: ../ADA.png
    transition: slide
    slide-number: c/t
    chalkboard: true
    controls: true
    navigation-mode: linear
    width: 1280
    height: 720
    margin: 0.04
    min-scale: 0.2
    max-scale: 2.0
    footer: "Mathematical Statistics - Topic Name"
    incremental: false
    highlight-style: tango
    code-fold: true
    menu: true
    progress: true
    history: true
    mouse-wheel: true
    overview: true
    zoom: true
    quiz:
      checkKey: 'c'
      resetKey: 'r'
      shuffleKey: 's'
      allowNumberKeys: true
      disableOnCheck: false
      disableReset: false
      shuffleOptions: true
      defaultCorrect: "✅ Correct! Well done."
      defaultIncorrect: "❌ Not quite. Try again or check the explanation."
      includeScore: true
revealjs-plugins:
  - quiz
---
```

---

## Workflow

### 0. Extract Chapter Content from PDF

Before creating lectures, extract the relevant chapter content:

```python
import fitz
doc = fitz.open('/mnt/user-data/uploads/Mathematical_Statistics_-_7th_Edition_-_Wackerly.pdf')

# Get chapter pages from references/wackerly-chapters.md
start_page, end_page = 320, 369  # Chapter 6 example

for page_num in range(start_page - 1, end_page):
    page = doc[page_num]
    text = page.get_text()
    print(f"=== PAGE {page_num + 1} ===")
    print(text)
```

**Key elements to extract:**
- Definition numbers and text (e.g., "DEFINITION 6.1")
- Theorem statements and proofs
- Example problems with solutions
- Figure descriptions (recreate with R/OJS)
- Exercise problems for practice/quiz questions

### 1. Analyze Chapter Content

Split each Wackerly chapter into 2-3 logical lectures based on:
- **Conceptual boundaries**: Group related definitions and theorems
- **Complexity**: ~45-60 min teaching content per lecture
- **Dependencies**: Earlier concepts before those that build on them

Example split for Chapter 5 (Multivariate Distributions):
- Lecture 1: Joint distributions, marginal distributions
- Lecture 2: Conditional distributions, independence
- Lecture 3: Expected values, covariance, correlation

### 2. Generate QMD Files

For each lecture, create a .qmd file following the template in `references/qmd-template.md`.

### 3. Transform Content

| Wackerly Element | QMD Transformation |
|------------------|-------------------|
| Definition X.Y | `{.callout-note}` with 📝 Definition X.Y header |
| Theorem X.Y | `{.callout-important}` with Theorem X.Y header |
| Example X.Y | Example slide with `. . .` progressive reveals |
| Proof | Collapsible proof or separate slide if important |
| Exercise | Practice Problems section or Quiz question |

### 4. Add Interactive Elements

Each lecture MUST include:
- **1-2 OJS visualizations** demonstrating key concepts
- **1 R case study** with real financial data (use tidyquant for stock data)
- **3-4 quiz questions** testing key concepts
- **Practice problems** adapted from chapter exercises
- **1 Think-Pair-Share activity** with countdown timer

---

## 📐 Slide Layout Parameters

### Slide Dimensions Reference
- **Standard Revealjs**: 1280×720 pixels
- **Usable content area**: ~1200×620 (after margins/headers)

### Container Font Sizes
| Layout Type | Optimal Font Size | Margin Top |
|-------------|-------------------|------------|
| Dense interactive | `0.72em - 0.75em` | `-5px to -10px` |
| Standard content | `0.8em - 0.85em` | `0px` |
| Sparse content | `0.9em - 1em` | `5px` |

### Column Width Ratios
| Layout | Left (Controls/Text) | Right (Plot) |
|--------|---------------------|--------------|
| Single plot | 20-25% | 75-80% |
| Dual plots | 20% | 40% / 40% |
| Text-heavy | 32-35% | 65-68% |

### Plot Dimensions (for 1280×720 slides)
| Plot Type | Small | Medium | Large | Max |
|-----------|-------|--------|-------|-----|
| Single 2D | 400×400 | 500×500 | 600×600 | 720×600 |
| Single 3D | 420×380 | 500×450 | 580×520 | 650×580 |
| Dual plots | 380×380 | 460×460 | 520×520 | - |
| Contour | 600×400 | 720×480 | 820×520 | 900×580 |

### Callout Box Font Sizing
| Content Density | Font Size | Use Case |
|-----------------|-----------|----------|
| Sparse (4 items) | `42-45px` | Practice problems, summaries |
| Medium (6-8 items) | `36-38px` | Definitions, theorems |
| Dense (10+ items) | `32-34px` | Detailed examples |

**Rule:** If bottom 1/3 of slide is empty → increase font by 8-10px

---

## 🎮 Smartboard Compatibility

**Always add event propagation prevention to interactive elements:**

```javascript
viewof mySlider = {
  const input = Inputs.range([0, 10], {value: 5, step: 0.1, label: "Parameter:"});
  
  // Prevent slide navigation on touch/click
  input.addEventListener('pointerdown', e => e.stopPropagation());
  input.addEventListener('touchstart', e => e.stopPropagation());
  input.addEventListener('mousedown', e => e.stopPropagation());
  input.addEventListener('click', e => e.stopPropagation());
  input.addEventListener('wheel', e => e.stopPropagation());
  input.addEventListener('pointermove', e => e.stopPropagation());
  input.addEventListener('touchmove', e => e.stopPropagation());
  input.addEventListener('mousemove', e => e.stopPropagation());
  
  return input;
}
```

**For Plotly 3D containers:**
```javascript
// After creating the plot
const plotDiv = container.querySelector('.js-plotly-plot');
if (plotDiv) {
  ['pointerdown', 'touchstart', 'mousedown', 'click', 'wheel', 
   'pointermove', 'touchmove', 'mousemove'].forEach(eventType => {
    plotDiv.addEventListener(eventType, e => e.stopPropagation());
  });
}
```

---

## 💻 R Code Visibility for Students

**Best practice for teaching slides:**

```yaml
#| echo: true           # Show code
#| code-fold: true      # Collapsed by default
#| code-summary: "📊 Show Code"  # Button label
#| message: false
#| warning: false
```

### Statistics Output: Always Use `kable()` Tables
**NEVER** use `cat()`, `print()`, or `sprintf()` to display statistics. Always use `kable()` from the `knitr` package to produce formatted tables.

| Wrong | Correct |
|-------|---------|
| `cat("Mean:", mean(x))` | `kable(summary_df, digits = 3)` |
| `print(round(cor_matrix, 3))` | `kable(cor_matrix, digits = 3, caption = "Correlation Matrix")` |
| `sprintf("SD: %.4f", sd(x))` | Build a `data.frame()` and pass to `kable()` |

### Folding Options
| Option | Behavior |
|--------|----------|
| `code-fold: true` | Collapsed by default (click to expand) |
| `code-fold: show` | Expanded by default (click to collapse) |
| `code-fold: false` | Always visible, no toggle |

---

## ⏱️ Countdown Timer for Activities

**Package:** `countdown` (R package)

### Basic Usage (Think-Pair-Share, Group Work)
```r
#| echo: false
library(countdown)
countdown(minutes = 4, seconds = 0,
          top = 0, right = 0,           # Position: top-right corner
          font_size = "1.5em",
          color_running_background = "#31b09e",   # Green while running
          color_running_text = "white",
          color_finished_background = "#cc3311",  # Red when done
          color_finished_text = "white",
          color_warning_background = "#f7dc6f",   # Yellow warning
          warn_when = 60,               # Warn at 60 seconds left
          play_sound = TRUE)            # 🔊 Alarm when finished
```

### Activity Duration Guidelines
| Activity Type | Duration | Timer Setting |
|---------------|----------|---------------|
| Quick Think | 1 min | `minutes = 1` |
| Think-Pair-Share | 4 min | `minutes = 4` |
| Group Problem | 5-8 min | `minutes = 5` or `minutes = 8` |
| Case Study | 10-15 min | `minutes = 10` or `minutes = 15` |

---

## 🤖 Autopilot Compile-Check-Fix Workflow

**After creating each lecture, run this workflow:**

```
CYCLE 1: Compilation Check
1. COMPILE: quarto render "file.qmd" 2>&1
2. CHECK: Analyze output for errors/warnings
3. FIX: Apply fixes based on error type
4. REPEAT: Until clean compilation

CYCLE 2: Font Size Audit (Code Analysis)
1. SCAN: grep for font-size < 30px or em < 0.75
2. SCAN: grep for {.smaller} class usage
3. FIX: Increase fonts to minimum 30px/0.75em
4. SPLIT: If slide too dense, split into multiple

CYCLE 3: Visual Check (if user provides screenshots)
1. ANALYZE: Empty space → increase fonts
2. ANALYZE: Overflow → split slide or reduce slightly
3. FIX: Apply adjustments
4. RECOMPILE: Verify changes
```

### Grep Patterns for Font Audit
```bash
# Find fonts below 30px
grep -E "font-size:\s*(2[0-9]|1[0-9])px" file.qmd

# Find fonts below 0.75em  
grep -E "font-size:\s*0\.[56]" file.qmd

# Find .smaller class usage
grep "{.smaller}" file.qmd
```

### Common Quarto Errors & Fixes
| Error | Fix |
|-------|-----|
| `no package called 'X'` | `install.packages('X')` |
| `object not found` | Check variable scope in R chunks |
| `unexpected token` | Check OJS syntax, missing brackets |
| `duplicate attribute` | Merge `width` into `style` attribute |
| `weight=` typo | Change to `width=` |
| Overfull content | Split slide or reduce font by 2-4px |
| Empty space | Increase font by 4-10px |

---

## 📐 Quick Reference Templates

### Two-Column: Controls + Single Large Plot
```markdown
## 🎮 Interactive: [Title] {.smaller}

:::::: {style="font-size: 0.72em; margin-top: -8px;"}

::::: columns
::: {.column width="25%"}
```{ojs}
// Slider controls + text panel
```
:::

::: {.column width="75%"}
```{ojs}
// Large plot (width: 820, height: 520)
```
:::
:::::
::::::
```

### Three-Column: Controls + 2D + 3D Plots
```markdown
## 🎮 Interactive: [Title] {.smaller}

:::::: {style="font-size: 0.75em; margin-top: -5px;"}

::::: columns
::: {.column width="20%"}
```{ojs}
// Controls + text
```
:::

::: {.column width="40%"}
```{ojs}
// 2D plot (width: 460, height: 460)
```
:::

::: {.column width="40%"}
```{ojs}
// 3D plot (width: 480, height: 460)
```
:::
:::::
::::::
```

### Think-Pair-Share Activity
```markdown
## 🤝 Think-Pair-Share: [Topic] {.larger}

::::: {style="font-size: 38px;"}
:::: callout-note
## 💭 Activity (4 minutes)

**Problem setup here**

::: columns
::: {.column width="33%"}
**🧠 Think (1 min):**
- Task 1
- Task 2
:::

::: {.column width="33%"}
**👫 Pair (2 min):**
- Discussion point 1
- Discussion point 2
:::

::: {.column width="33%"}
**🗣️ Share (1 min):**
- Synthesis question
:::
:::
::::
:::::

```{r}
#| echo: false
library(countdown)
countdown(minutes = 4, seconds = 0,
          top = 0, right = 0,
          font_size = "1.5em",
          color_running_background = "#31b09e",
          color_running_text = "white",
          color_finished_background = "#cc3311",
          color_finished_text = "white",
          warn_when = 60,
          play_sound = TRUE)
```
```

---

## File Naming

```
{topic}_lecture{N}.qmd
```

Examples:
- `multivariate_lecture1.qmd`
- `hypothesis_testing_lecture2.qmd`
- `regression_lecture1.qmd`

## Required Sections (in order)

1. **YAML frontmatter** (see template above)
2. **Learning Objectives** (5 bullet points with action verbs)
3. **Overview** (topics covered today)
4. **Motivation** (why this topic matters)
5. **Content slides** (definitions, theorems, examples)
6. **Interactive visualization** (OJS with smartboard compatibility)
7. **Think-Pair-Share activity** (with countdown timer)
8. **Case Study** (R with financial data, code-fold: true)
9. **Quizzes** (3-4 questions)
10. **Summary** (key takeaways)
11. **Practice Problems** (4-5 problems)
12. **Thank You** (contact info, next class)
13. **Questions** (discussion prompts)

## Slide Design Guidelines

- Use `{.smaller}` class ONLY for interactive slides with controls
- Use `. . .` for progressive reveal in solutions
- Use `{.columns}` with `{.column width="50%"}` for side-by-side content
- Use `{.fragment}` for animated reveals within columns
- Keep math in display mode (`$$...$$`) for important equations
- Use inline math (`$...$`) for references within text
- **Always use `width=` not `weight=`** in column definitions

## 💰 Financial & Economic Applications (CRITICAL)

**ALL examples must have finance/economics context.** Students are finance/econ majors and learn better with relevant applications.

### Concept Transformation Table
| Mathematical Concept | Finance/Economics Application |
|---------------------|-------------------------------|
| Random variables | Asset returns, GDP growth, inflation rates |
| Discrete distributions | Number of defaults, trading days, customer arrivals |
| Continuous distributions | Stock prices, interest rates, exchange rates |
| Joint distributions | Portfolio returns (multiple stocks) |
| Independence | Diversification benefits, uncorrelated assets |
| Conditional probability | Default given recession, returns given market state |
| Covariance/Correlation | Portfolio risk analysis, asset co-movement |
| Expected value | Expected portfolio return, fair price |
| Variance | Volatility, risk measurement |
| Moment generating functions | Option pricing, risk-neutral valuation |
| Order statistics | Best/worst performing assets, VaR |
| Sampling distributions | Estimating market parameters |
| Hypothesis testing | Testing market efficiency, comparing strategies |
| Regression | CAPM, factor models, forecasting |

### Example Transformations
| Wackerly Example | Finance Version |
|------------------|----------------|
| "Balls in urns" | "Stocks in a portfolio" |
| "Defective items" | "Defaulting loans" |
| "Waiting time" | "Time between trades" |
| "Heights of people" | "Daily returns of S&P 500" |
| "Machine failure" | "Market crash probability" |
| "Dice experiment" | "Economic scenarios (boom/recession/stable)" |

### Real Data Sources
- **Stock tickers:** AAPL, MSFT, GOOGL, AMZN, SPY, QQQ, TLT, GLD
- **R packages:** `quantmod`, `tidyquant`, `fredr` (FRED economic data)
- **Economic indicators:** GDP, CPI, unemployment rate, Fed funds rate

### Case Study Ideas by Topic
| Chapter | Case Study |
|---------|------------|
| Probability | Portfolio allocation under uncertainty |
| Discrete RV | Loan default modeling |
| Continuous RV | Stock return distributions |
| Multivariate | Two-asset portfolio optimization |
| Sampling | Estimating market beta |
| Estimation | Confidence intervals for expected returns |
| Hypothesis Testing | Testing CAPM, market efficiency |
| Regression | Factor models, risk decomposition |

## ✅ Quality Checklist

Before finalizing each lecture:
- [ ] YAML frontmatter complete with quiz plugin and scaling settings
- [ ] 5 clear learning objectives with action verbs
- [ ] All Wackerly definitions/theorems properly numbered
- [ ] **All fonts ≥ 30pt (0.75em)** - CRITICAL
- [ ] **All examples have finance/economics context** - CRITICAL
- [ ] Examples have progressive reveal (`. . .`)
- [ ] At least 1 interactive OJS visualization with smartboard compatibility
- [ ] R case study with real financial data and `code-fold: true`
- [ ] Think-Pair-Share activity with countdown timer
- [ ] 3-4 quiz questions with finance/econ scenarios
- [ ] Summary matches learning objectives
- [ ] Next class preview in Thank You slide
- [ ] **Autopilot workflow completed** (compile → check → fix)
- [ ] No slides with > 80 words or > 5 bullet points (split if needed)
- [ ] No abstract "balls in urns" type examples (transform to finance)

## Reference Files

- `references/qmd-template.md` - Complete YAML and slide templates
- `references/slide-patterns.md` - Patterns for different slide types (OJS, R, quizzes)
- `references/wackerly-chapters.md` - Chapter structure, definitions, theorems, page numbers
- `scripts/extract_wackerly.py` - Python script to extract PDF content

---

## 🎮 Interactive Visualization Best Practices

### OJS Plot Errors & Fixes

#### Error: "missing channel value: x1"
**Problem:** Using conditional marks with `&&` operator returns `false` when condition not met, and `false` is not a valid mark.

**Wrong:**
```javascript
marks: [
  Plot.contour(data, {...}),
  region === "Triangular" && Plot.line(boundary, {...}),  // ❌ Returns false
  Plot.frame()
]
```

**Correct:**
```javascript
marks: [
  Plot.contour(data, {...}),
  region === "Triangular" ? Plot.line(boundary, {...}) : null,  // ✅ Returns null
  Plot.frame()
].filter(Boolean)  // Remove null values
```

#### Contour Plot Bleeding Across Boundaries
**Problem:** When support is triangular (e.g., y₂ ≤ y₁), contour interpolation can bleed into forbidden region.

**Solution:** Add explicit zero-density points in the forbidden region:
```javascript
jointData = {
  const data = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const y1 = i / (n - 1);
      const y2 = j / (n - 1);
      const inRegion = (region === "Triangular") ? (y2 <= y1) : true;
      
      if (inRegion) {
        data.push({y1, y2, density: computeDensity(y1, y2)});
      }
    }
  }
  
  // Add zero-density boundary points for triangular case
  if (region === "Triangular") {
    for (let i = 0; i < n; i++) {
      const y1 = i / (n - 1);
      for (let j = Math.ceil(y1 * (n-1)) + 1; j < n; j++) {
        const y2 = j / (n - 1);
        data.push({y1, y2, density: 0});  // Prevent bleeding
      }
    }
  }
  
  return data;
}
```

### Conditional Slice Visualization
**Best practice:** Show vertical band + dots instead of dashed line alone

**Wrong (hard to see):**
```javascript
marks: [
  Plot.ruleX([sliceY1], {stroke: "blue", strokeDasharray: "3,3"})  // ❌ Too subtle
]
```

**Correct (clear visual):**
```javascript
// Create vertical band data
sliceBand = {
  const bandwidth = 0.015;
  const ymax = region === "Triangular" ? sliceY1 : 1;
  return [{x1: sliceY1 - bandwidth, x2: sliceY1 + bandwidth, y1: 0, y2: ymax}];
};

// Create conditional range dots
conditionalDots = {
  const points = [];
  const ymax = region === "Triangular" ? sliceY1 : 1;
  for (let i = 0; i <= 35; i++) {
    points.push({y1: sliceY1, y2: (i / 35) * ymax});
  }
  return points;
};

marks: [
  // Semi-transparent band
  Plot.rect(sliceBand, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", 
                        fill: "#3b82f6", fillOpacity: 0.12}),
  // Dots showing feasible range
  Plot.dot(conditionalDots, {x: "y1", y: "y2", r: 3, fill: "#1d4ed8", opacity: 0.9}),
  // Solid vertical line
  Plot.ruleX([sliceY1], {stroke: "#1d4ed8", strokeWidth: 3})
]
```

### Support Region Notation
**Always explicitly state support constraints** in both text and plot title:

```javascript
// In control panel
lesson_html = region === "Rectangular"
  ? html`<div style="..."><strong>Support:</strong> 0 < Y₁ < 1, 0 < Y₂ < 1<br>Y₂'s range never changes with Y₁.</div>`
  : html`<div style="..."><strong>Support:</strong> 0 < Y₂ ≤ Y₁ < 1<br>Knowing Y₁ restricts Y₂ (lower triangle!).</div>`;

// In plot title
title: region === "Rectangular"
  ? "Rectangle: Support is 0<Y₁<1, 0<Y₂<1 (full square)"
  : "Triangle: Support is 0<Y₂≤Y₁<1 (LOWER triangle)"
```

### Educational Context for Interactive Slides
**Problem:** Plots that just "change" without explanation teach nothing.

**Solution:** Frame with clear question + educational insight

```markdown
## 🎮 Interactive: Why Support Shape Determines Independence {.smaller}

**Key insight:** Independence needs both (1) density factors AND (2) rectangular support.

[Controls here]

**Verdict:** [INDEPENDENT or DEPENDENT]

**The Lesson:**
- Rectangle: Knowing Y₁ tells you *nothing* about Y₂'s range
- Triangle: Knowing Y₁ *restricts* Y₂ → information flows between variables
```

**Caption below plot:**
```javascript
html`<div>
  ${plot}
  <div style="margin-top: 5px; font-size: 0.9em;">
    <strong>Blue band at Y₁=${sliceY1.toFixed(2)}:</strong> Shows Y₂'s feasible range.
    ${region === "Triangular" 
      ? `Only [0, ${sliceY1.toFixed(2)}] allowed.` 
      : "Always [0, 1] allowed."}
  </div>
</div>`
```

### OJS Superscripts in Formulas
**Problem:** `${power}` interpolation inside LaTeX breaks compilation

**Wrong:**
```javascript
formula = `f(y₁, y₂) = c · y₁^{${power_a}} · y₂^{${power_b}}`  // ❌ LaTeX error
```

**Correct - Use HTML:**
```javascript
formula_html = html`<span style="font-size: 1.05em;">
  f(y₁, y₂) = c · y₁<sup>${power_a}</sup> · y₂<sup>${power_b}</sup>
</span>`;

md`**Formula:** ${formula_html}`
```

---

## 🎯 Countdown Timer Positioning

**Default:** Top-right corner
```r
countdown(minutes = 4, top = 0, right = 0, ...)
```

**Bottom-right (better for slides with top content):**
```r
countdown(minutes = 4, bottom = 0, right = 0, ...)
```

---

## ⚠️ Common Fragmentation Issues

### Problem: `. . .` Not Working Inside Style Blocks
**Wrong:**
```markdown
::: {style="font-size: 36px;"}
. . .

Some content

. . .

More content
:::
```

**Correct - Use {.fragment} divs:**
```markdown
::: {style="font-size: 36px;"}
::: {.fragment}
Some content
:::

::: {.fragment}
More content
:::
:::
```

---

*Last updated: February 3, 2026*
*Based on: Dr. Samir Orujov's lecture format for ADA University*
*Lessons from: multivariate_lecture2.qmd debugging session*
