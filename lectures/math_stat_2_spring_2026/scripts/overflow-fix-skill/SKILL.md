# Skill: Fix Overflow in Quarto RevealJS Slides

## Purpose
Given a Quarto RevealJS `.qmd` lecture file, maximize font sizes on every slide subject to the no-overflow constraint. Minimum allowed font size: **28px**. Starting point for optimization: **50px**.

The skill prepares the QMD for the local `optimize_slides.py` script, which does the actual browser-based overflow detection and reduction.

---

## Inputs
- A `.qmd` file (pasted or attached) using the Quarto RevealJS format
- Slide separator: `\n---\n`
- Slide 0 = YAML front matter; slides 1..N = content slides (each starts with `## Title`)

---

## Procedure

### Step 1 — Parse the QMD
Split the file on `\n---\n`. The result is a list of sections:
- `sections[0]` = YAML front matter (do NOT modify)
- `sections[1..N]` = RevealJS slides

### Step 2 — For each content slide, set font size to 50px

Apply these rules **in order**:

**Rule A — Skip these slides unchanged:**
- Slides whose heading contains `{.center}` only (Thank You, Questions slides)
- Slides containing R/Python code chunks that produce plots or tables as primary content (Case Study code slides — they are controlled by code output sizing, not text wrappers)
- Slides whose only font-size uses a relative unit like `0.72em` (Interactive/widget slides)

**Rule B — Bump existing non-`!important` inline font-sizes to 50px:**
Find every occurrence of `font-size:\s*\d+px` that is NOT followed by `\s*!important` and replace the numeric value with `50`.

Example:
- `font-size:32px` → `font-size:50px`
- `font-size: 28px;` → `font-size: 50px;`
- `font-size: 38px !important` → leave unchanged

**Rule C — Add a wrapper to slides with no inline font-size:**
If after Rule B a slide still has no `font-size:\d+px` (non-important), wrap its entire body (everything after the `## Heading` line) in:
```
::: {style="font-size:50px;"}
[original body content]
:::
```

The wrapper goes immediately after the blank line following the `## Heading` line, and its closing `:::` goes immediately before the trailing `\n` of the section (before the `---`).

**Important nesting rules for Rule C:**
- If the body already starts with a `::: {.callout-*}` or `::: {.columns}` block, wrap the entire body (including those blocks).
- Do NOT add a wrapper to the YAML section (sections[0]).
- Do NOT add a wrapper to slides that were skipped in Rule A.

### Step 3 — Output the modified QMD
Rejoin sections with `\n---\n` and output the full modified `.qmd` content.

### Step 4 — Instruct the user to run the optimizer
After outputting the QMD, tell the user:

> **Next step:** Save the file, then run:
> ```
> quarto render your_file.qmd
> python optimize_slides.py your_file.qmd --no-render --min-font 28 --max-iter 50
> quarto render your_file.qmd
> python optimize_slides.py your_file.qmd --no-render --min-font 28
> ```
> The optimizer will reduce each slide from 50px down to the largest size that fits without overflow.
> Slides that hit 28px and still overflow need to be split (see splitting rules below).

---

## Splitting Rules (apply when optimizer reports "hit min font 28px")

When the optimizer says a slide hit the 28px minimum and still overflows, split it into two slides.

**Split strategy:**
1. Move the first `:::{.fragment}` block and everything before it to **Slide A** (the problem/setup)
2. Move remaining fragments to **Slide B** (the solution/detail)
3. Give **Slide B** the same heading but append `: Solution` or `: Continued`
4. Set both new slides to `font-size:50px` and re-run the optimizer

**Example — before split:**
```markdown
## Example 1: Some Derivation {.smaller}

::: {style="font-size:28px;"}
**Problem:** Long problem statement with equations...

$$\text{lots of math}$$

:::{.fragment}
**Solution:** More equations...

$$\text{more math}$$
:::
:::
```

**Example — after split:**
```markdown
## Example 1: Some Derivation {.smaller}

::: {style="font-size:50px;"}
**Problem:** Long problem statement with equations...

$$\text{lots of math}$$
:::

---

## Example 1: Solution {.smaller}

::: {style="font-size:50px;"}
**Solution:** More equations...

$$\text{more math}$$
:::
```

---

## Fragment Rules

Use `:::{.fragment}` ... `:::` divs for step-by-step reveals. Do NOT use `. . .` (Pandoc pause markers) — they interact poorly with nested divs and column layouts in Quarto RevealJS.

**Correct:**
```markdown
:::{.fragment}
**Solution:**

$$E(\hat{\theta}) = \theta$$
:::
```

**Incorrect:**
```markdown
. . .

**Solution:**

$$E(\hat{\theta}) = \theta$$
```

---

## Font-size Exceptions

These patterns use `!important` or relative units and must NOT be modified by Step 2:
- `font-size: 38px !important` — callout boxes, definition boxes
- `font-size: 36px !important` — definition/tip callouts
- `font-size: 50px !important` — overview/summary callouts
- `font-size: 0.72em` — interactive/widget slides

---

## Quiz Slides

Slides with `.quiz-question` class are handled by the quiz plugin and must NOT be modified. The `optimize_slides.py` script automatically skips them. Leave their font-size wrappers at whatever the current value is (typically 32–50px is fine since quiz content is short).

---

## Reference: optimize_slides.py behavior

The bundled `optimize_slides.py` script:
- Opens the rendered HTML in headless Chromium (via Playwright)
- For each slide: checks if any element's bottom exceeds the slide boundary by >8px
- If overflow: iteratively reduces all inline `font-size: Xpx` by 1px until no overflow or min-font reached
- Patches the QMD source with discovered reductions
- Skips `.quiz-question` slides entirely (quiz plugin causes false positives)

**Setup (one-time):**
```
pip install playwright
python -m playwright install chromium
```

**Usage:**
```
python optimize_slides.py lecture.qmd --min-font 28 --max-iter 50
python optimize_slides.py lecture.qmd --no-render --min-font 28 --max-iter 50  # reuse HTML
python optimize_slides.py lecture.qmd --dry-run --min-font 28                   # preview only
```
