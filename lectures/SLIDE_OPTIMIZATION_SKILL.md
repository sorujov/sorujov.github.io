# 🎯 Quarto Revealjs Slide Optimization Skill

## Purpose
This skill optimizes interactive Quarto Revealjs slides based on visual feedback (screenshots). It identifies **empty space** or **overflow issues** and applies systematic adjustments to achieve optimal fit.

---

## � User Preferences (CRITICAL)

### Font Size Requirements
- **Minimum font size: 30pt equivalent** (for students in back rows)
- Always prioritize readability over fitting more content
- When in doubt, go LARGER

### Content Strategy
- **Split slides** when content is dense rather than shrinking text
- One concept per slide is better than cramped content
- Use `{.smaller}` class sparingly, only for interactive slides with controls

### Revealjs Font Size Reference
| CSS em value | Approximate pt | Use Case |
|--------------|----------------|----------|
| `0.6em` | ~24pt | ❌ Too small - avoid |
| `0.75em` | ~30pt | ✅ Minimum acceptable |
| `0.85em` | ~34pt | ✅ Good for dense slides |
| `1.0em` | ~40pt | ✅ Preferred for text |
| `1.2em` | ~48pt | ✅ Great for key points |

---

## �📸 Skill Trigger
**When user provides a screenshot of a slide showing:**
- ❌ Too much empty space at bottom/sides
- ❌ Content overflow or truncation
- ❌ Elements too small for visibility
- ❌ Poor proportions between text and visualizations

---

## 🔧 Optimization Parameters

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

---

## 📋 Optimization Algorithm

### Step 0: Check Content Density
```
IF too_many_words_on_slide (> 80 words):
    → SPLIT into multiple slides
    → Each slide = one concept
    → Never shrink text below 0.75em (30pt)
    
IF using {.smaller} class:
    → Only acceptable for interactive slides with controls
    → Never for pure text/content slides
```

### Step 1: Analyze Screenshot
```
IF significant_empty_space_at_bottom:
    → Increase plot height by 15-25%
    → Increase container font-size by 0.05-0.1em
    
IF empty_space_on_sides:
    → Increase plot width by 10-20%
    → Adjust column ratios (give more to plot)
    
IF content_overflow_or_truncation:
    → Decrease plot dimensions by 10-15%
    → Reduce container font-size by 0.05em
    → Increase negative margin-top
    
IF elements_too_small:
    → Increase font-size in HTML templates
    → Increase dot/marker sizes (r: 5 → 6)
    → Increase axis label font sizes
```

### Step 2: Apply Adjustments

#### For Container Wrapper
```markdown
:::::: {style="font-size: 0.75em; margin-top: -5px;"}
```

#### For Text Panels (HTML in OJS)
```javascript
html`<div style="font-size: 1.1em; line-height: 1.4;">
<p style="font-size: 1.5em; color: #2563eb;">
<strong>Key Value</strong>
</p>
</div>`
```

#### For Observable Plot
```javascript
Plot.plot({
  width: 460,
  height: 460,
  marginLeft: 50,
  marginBottom: 50,
  // ... marks
})
```

#### For Plotly 3D
```javascript
const layout = {
  width: 480, 
  height: 460,
  margin: {l: 0, r: 0, b: 0, t: 0},
  scene: {
    xaxis: {title: 'x', titlefont: {size: 14}},
    yaxis: {title: 'y', titlefont: {size: 14}},
    zaxis: {title: 'z', titlefont: {size: 12}},
    camera: { eye: {x: 1.5, y: 1.5, z: 1.1} },
    aspectmode: 'cube'
  }
};
```

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

---

## ✅ Validation Checklist

After optimization, verify:
- [ ] **Font size ≥ 30pt (0.75em)** - CRITICAL for back-row visibility
- [ ] No content cut off at bottom
- [ ] No horizontal scrollbar
- [ ] Text readable at presentation distance (test from 5+ meters)
- [ ] Interactive elements responsive
- [ ] Plots fill available space proportionally
- [ ] Consistent styling across similar slides
- [ ] If slide feels cramped → SPLIT IT

---

## 🔀 When to Split a Slide

**Split when:**
- More than 80 words on a slide
- More than 5 bullet points
- Need to use font < 0.75em to fit content
- Multiple distinct concepts
- Complex formula + explanation

**Split strategy:**
```
Slide A: Problem Statement + Setup
Slide B: Solution Step 1
Slide C: Solution Step 2 + Conclusion
```

---

## 📝 Example Optimization Session

**User provides screenshot showing:** Empty space at bottom (~100px)

**Analysis:**
- Current plot: 380×380
- Current font: 0.65em
- Available space: ~100px vertical

**Actions:**
1. Increase plot to 460×460 (+80px)
2. Increase font to 0.75em
3. Adjust margins from -10px to -5px
4. Increase dot radius from 5 to 6

**Result:** Optimal fit with improved visibility

---

*Last updated: February 2, 2026*
*Based on: multivariate_lecture1.qmd interactive slides*

---

## 🤖 Autopilot Compile-Check-Fix Workflow

**When user asks for autopilot optimization:**

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

## 💻 R Code Visibility for Students

**Best practice for teaching slides:**

```yaml
#| echo: true           # Show code
#| code-fold: true      # Collapsed by default
#| code-summary: "📊 Show Code"  # Button label
#| message: false
#| warning: false
```

### Folding Options
| Option | Behavior |
|--------|----------|
| `code-fold: true` | Collapsed by default (click to expand) |
| `code-fold: show` | Expanded by default (click to collapse) |
| `code-fold: false` | Always visible, no toggle |

---

## 📏 Callout Box Font Sizing

**For callout boxes with explicit font-size:**

| Content Density | Font Size | Use Case |
|-----------------|-----------|----------|
| Sparse (4 items) | `42-45px` | Practice problems, summaries |
| Medium (6-8 items) | `36-38px` | Definitions, theorems |
| Dense (10+ items) | `32-34px` | Detailed examples |

**Rule:** If bottom 1/3 of slide is empty → increase font by 8-10px

---

## ⏱️ Countdown Timer for Activities

**Package:** `countdown` (R package)

### Installation
```r
install.packages('countdown')
```

### Basic Usage (Think-Pair-Share, Group Work, etc.)
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

### Position Options
| Position | Code |
|----------|------|
| Top-right | `top = 0, right = 0` |
| Top-left | `top = 0, left = 0` |
| Bottom-right | `bottom = 0, right = 0` |
| Bottom-left | `bottom = 0, left = 0` |
| Centered below content | `top = "60%", left = "40%"` |

### Timer Interaction
- **Click** to start/pause
- **Double-click** to reset
- **Alarm sound** plays when timer reaches 0

### Activity Duration Guidelines
| Activity Type | Duration | Timer Setting |
|---------------|----------|---------------|
| Quick Think | 1 min | `minutes = 1` |
| Think-Pair-Share | 4 min | `minutes = 4` |
| Group Problem | 5-8 min | `minutes = 5` or `minutes = 8` |
| Case Study | 10-15 min | `minutes = 10` or `minutes = 15` |
