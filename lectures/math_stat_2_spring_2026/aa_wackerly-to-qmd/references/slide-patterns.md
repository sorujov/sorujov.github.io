# Slide Patterns Reference

## ⚠️ Common Mistakes to Avoid

### 1. OJS Conditional Marks - Use Ternary, Not &&
**WRONG:**
```javascript
marks: [
  Plot.contour(data, {...}),
  condition && Plot.line(boundary, {...}),  // ❌ Returns false → Error
  Plot.frame()
]
```

**CORRECT:**
```javascript
marks: [
  Plot.contour(data, {...}),
  condition ? Plot.line(boundary, {...}) : null,  // ✅ Returns null
  Plot.frame()
].filter(Boolean)  // Remove null values
```

### 2. Fragmentation - Use {.fragment} Divs, Not `. . .` in Style Blocks
**WRONG:**
```markdown
::: {style="font-size: 36px;"}
. . .

Some content

. . .

More content
:::
```

**CORRECT:**
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

### 3. Countdown Position - Bottom-Right for Slides with Top Content
**WRONG (blocks top content):**
```r
countdown(minutes = 4, top = 0, right = 0, ...)
```

**CORRECT:**
```r
countdown(minutes = 4, bottom = 0, right = 0, ...)  # Better positioning
```

### 4. OJS LaTeX Interpolation - Use HTML for Superscripts
**WRONG (LaTeX compilation error):**
```javascript
formula = `f(y₁, y₂) = c · y₁^{${power_a}} · y₂^{${power_b}}`
```

**CORRECT:**
```javascript
formula_html = html`<span style="font-size: 1.05em;">
  f(y₁, y₂) = c · y₁<sup>${power_a}</sup> · y₂<sup>${power_b}</sup>
</span>`;

md`**Formula:** ${formula_html}`
```

---

## OJS Interactive Visualization

### Basic Pattern with Smartboard Compatibility

```markdown
## 🎮 Interactive: [Title] {.smaller}

:::::: {style="font-size: 0.72em; margin-top: -8px;"}

**Key insight:** [What students should learn from this visualization]

::::: columns
::: {.column width="30%"}

```{ojs}
//| echo: false

viewof parameter_name = {
  const input = Inputs.range([min, max], {
    value: default, 
    step: step_size, 
    label: "Parameter label:"
  });
  
  // Smartboard compatibility - ALWAYS add these
  input.addEventListener('pointerdown', e => e.stopPropagation());
  input.addEventListener('touchstart', e => e.stopPropagation());
  input.addEventListener('mousedown', e => e.stopPropagation());
  input.addEventListener('click', e => e.stopPropagation());
  input.addEventListener('wheel', e => e.stopPropagation());
  input.addEventListener('pointermove', e => e.stopPropagation());
  input.addEventListener('touchmove', e => e.stopPropagation());
  
  return input;
}

// Computation based on parameter
computed_value = {
  // JavaScript computation
  return result;
}

// Dynamic text with educational context
explanation_html = condition
  ? html`<div style="background: #d4edda; padding: 6px; border-radius: 5px;">
      <strong>Result:</strong> [Explain what this means]
    </div>`
  : html`<div style="background: #f8d7da; padding: 6px; border-radius: 5px;">
      <strong>Result:</strong> [Explain alternative case]
    </div>`;

md`**Current Value:** ${computed_value.toFixed(3)}

${explanation_html}`
```

:::

::: {.column width="70%"}

```{ojs}
//| echo: false

// Visualization using Plot
Plot.plot({
  width: 600,
  height: 380,
  marginLeft: 55,
  marginBottom: 45,
  x: { domain: [xmin, xmax], label: "X Label" },
  y: { domain: [ymin, ymax], label: "Y Label" },
  title: "Descriptive title that changes with parameters",
  marks: [
    Plot.line(data, {x: "x", y: "y", stroke: "steelblue", strokeWidth: 2}),
    Plot.ruleY([0], {stroke: "#ccc"})
  ].filter(Boolean)
})
```

:::
:::
::::::
```

### Contour Plot with Triangular Support (Prevent Bleeding)

```markdown
## 🎮 Interactive: Density Visualization {.smaller}

```{ojs}
//| echo: false

jointData = {
  const n = 80;  // Higher resolution for smoother contours
  const data = [];
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const y1 = i / (n - 1);
      const y2 = j / (n - 1);
      
      // Define support region
      const inRegion = (region_type === "Triangular") ? (y2 <= y1) : true;
      
      if (inRegion) {
        const density = Math.pow(y1 + 0.01, power_a) * Math.pow(y2 + 0.01, power_b);
        data.push({y1, y2, density});
      }
    }
  }
  
  // CRITICAL: Add zero-density boundary points to prevent contour bleeding
  if (region_type === "Triangular") {
    for (let i = 0; i < n; i++) {
      const y1 = i / (n - 1);
      for (let j = Math.ceil(y1 * (n-1)) + 1; j < n; j++) {
        const y2 = j / (n - 1);
        data.push({y1, y2, density: 0});  // Zero density in forbidden region
      }
    }
  }
  
  return data;
}

Plot.plot({
  width: 600,
  height: 380,
  color: {scheme: "YlOrRd", legend: true, label: "Density"},
  x: {domain: [0, 1], label: "Y₁"},
  y: {domain: [0, 1], label: "Y₂"},
  title: region_type === "Rectangular" 
    ? "Rectangle: Support is 0<Y₁<1, 0<Y₂<1" 
    : "Triangle: Support is 0<Y₂≤Y₁<1 (LOWER triangle)",
  marks: [
    Plot.contour(jointData, {x: "y1", y: "y2", fill: "density", blur: 1, thresholds: 14}),
    Plot.frame()
  ]
})
```
```

### Conditional Slice Visualization (Improved)

```markdown
```{ojs}
//| echo: false

// Vertical band to highlight conditioning slice
sliceBand = {
  const bandwidth = 0.015;
  const ymax = region_type === "Triangular" ? sliceY1 : 1;
  
  return [{
    x1: sliceY1 - bandwidth,
    x2: sliceY1 + bandwidth,
    y1: 0,
    y2: ymax
  }];
};

// Dots showing feasible conditional range
conditionalDots = {
  const points = [];
  const ymax = region_type === "Triangular" ? sliceY1 : 1;
  for (let i = 0; i <= 35; i++) {
    points.push({y1: sliceY1, y2: (i / 35) * ymax});
  }
  return points;
};

// Constraint boundary line
constraintLine = region_type === "Triangular"
  ? Array.from({length: 100}, (_, i) => ({y1: i / 99, y2: i / 99}))
  : [];

plot = Plot.plot({
  width: 600,
  height: 380,
  marks: [
    Plot.contour(jointData, {x: "y1", y: "y2", fill: "density", blur: 1}),
    // Semi-transparent vertical band
    Plot.rect(sliceBand, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", 
                          fill: "#3b82f6", fillOpacity: 0.12}),
    // Constraint boundary
    constraintLine.length 
      ? Plot.line(constraintLine, {x: "y1", y: "y2", stroke: "#1f2937", 
                                   strokeWidth: 3, strokeDasharray: "8,4"}) 
      : null,
    // Conditional range dots
    Plot.dot(conditionalDots, {x: "y1", y: "y2", r: 3, fill: "#1d4ed8", opacity: 0.9}),
    // Vertical slice marker
    Plot.ruleX([sliceY1], {stroke: "#1d4ed8", strokeWidth: 3}),
    Plot.frame()
  ].filter(Boolean)
});

html`<div>
  ${plot}
  <div style="margin-top: 5px; font-size: 0.9em; line-height: 1.3;">
    <strong style="color: #1d4ed8;">Blue band at Y₁=${sliceY1.toFixed(2)}:</strong> 
    Shows Y₂'s feasible range. ${region_type === "Triangular" 
      ? `Only [0, ${sliceY1.toFixed(2)}] allowed.` 
      : "Always [0, 1] allowed."}
  </div>
</div>`
```
```

--- R Case Study - Data Loading

```markdown
## 💰 Case Study: [Title] {.smaller}

::: {style="font-size: 30px"}
```{r}
#| echo: true
#| code-fold: true
#| code-summary: "📊 Show Data Loading Code"
#| message: false
#| warning: false
#| eval: true

# Load required packages
library(tidyverse)
library(tidyquant)
library(knitr)

# Download stock data
symbols <- c("AAPL", "MSFT", "SPY")
prices <- tq_get(symbols,
                 from = "2020-01-01",
                 to = Sys.Date())

# Calculate daily returns
returns <- prices %>%
  group_by(symbol) %>%
  tq_transmute(select = adjusted,
               mutate_fun = periodReturn,
               period = "daily",
               col_rename = "ret")

# Pivot to wide format
returns_wide <- returns %>%
  pivot_wider(names_from = symbol,
              values_from = ret) %>%
  na.omit()

# Summary statistics
summary_stats <- returns_wide %>%
  summarise(across(-date, list(
    Mean = ~mean(.) * 100,
    StdDev = ~sd(.) * 100
  )))

kable(summary_stats, digits = 3,
      caption = "Daily Return Statistics (%)")
```
:::
```

### Case Study - Visualization Slide (separate slide)

```markdown
## 💰 Case Study: [Title] - Visualization {.smaller}

::: {style="font-size: 30px"}
```{r}
#| echo: true
#| code-fold: true
#| code-summary: "📊 Show Plot Code"
#| message: false
#| warning: false
#| eval: true
#| fig-width: 8
#| fig-height: 5

# Create visualization
ggplot(returns_wide, aes(x = AAPL, y = MSFT)) +
  geom_point(alpha = 0.5, color = "steelblue") +
  geom_smooth(method = "lm", color = "red", se = TRUE) +
  labs(title = "Joint Distribution of Returns",
       subtitle = "Daily returns with regression line",
       x = "AAPL Daily Return",
       y = "MSFT Daily Return") +
  theme_minimal(base_size = 14)
```
:::
```

## R Case Study - Analysis

```markdown
## 💰 Case Study: [Analysis Title] {.smaller}

::: {style="font-size: 30px"}
::: {.columns}
::: {.column width="50%"}

```{r}
#| echo: true
#| code-fold: true
#| code-summary: "📊 Show Analysis Code"
#| message: false
#| warning: false
#| eval: true

# Correlation matrix
cor_matrix <- cor(returns_wide %>% select(-date))
kable(cor_matrix, digits = 3, caption = "Correlation Matrix")

# Covariance matrix
cov_matrix <- cov(returns_wide %>% select(-date))
kable(cov_matrix, digits = 6, caption = "Covariance Matrix")
```

:::

::: {.column width="50%"}

```{r}
#| echo: true
#| code-fold: true
#| code-summary: "📊 Show Plot Code"
#| message: false
#| warning: false
#| eval: true
#| fig-width: 6
#| fig-height: 5

# Correlation heatmap
library(reshape2)
cor_melted <- melt(cor_matrix)

ggplot(cor_melted, aes(Var1, Var2, fill = value)) +
  geom_tile() +
  geom_text(aes(label = round(value, 2)),
            color = "white", size = 5) +
  scale_fill_gradient2(low = "blue", mid = "white",
                       high = "red", midpoint = 0,
                       limits = c(-1, 1)) +
  labs(title = "Correlation Matrix Heatmap",
       x = "", y = "", fill = "Correlation") +
  theme_minimal(base_size = 14) +
  coord_fixed()
```

:::
:::
:::
```

## Quiz Question Pattern

```markdown
## 📝 Quiz #N: [Topic] {.smaller .quiz-question}

[Question text]

- [[Correct answer text]]{.correct data-explanation="✅ Correct! [Explanation of why this is correct]"}
- [Wrong answer 1]
- [Wrong answer 2]
- [Wrong answer 3]
```

### Quiz Examples by Type

**Computation Quiz:**
```markdown
## 📝 Quiz #1: Computing Expected Value {.smaller .quiz-question}

If $E[Y_1] = 5$, $E[Y_2] = 10$, what is $E[3Y_1 + 2Y_2 - 7]$?

- [28]{.correct data-explanation="✅ Correct! By linearity: E[3Y₁ + 2Y₂ - 7] = 3E[Y₁] + 2E[Y₂] - 7 = 3(5) + 2(10) - 7 = 28"}
- 35
- 22
- 15
```

**Conceptual Quiz:**
```markdown
## 📝 Quiz #2: Independence Property {.smaller .quiz-question}

If $Y_1$ and $Y_2$ are independent, what is true about the conditional distribution $f(y_1|y_2)$?

- [It equals the marginal distribution $f_1(y_1)$]{.correct data-explanation="✅ Correct! If independent, f(y₁|y₂) = f(y₁,y₂)/f₂(y₂) = f₁(y₁)·f₂(y₂)/f₂(y₂) = f₁(y₁)."}
- It equals zero
- It equals the joint distribution $f(y_1, y_2)$
- It depends on the specific value of $y_2$
```

**Identification Quiz:**
```markdown
## 📝 Quiz #3: Testing Independence {.smaller .quiz-question}

Let $f(y_1, y_2) = 2e^{-y_1}e^{-2y_2}$ for $y_1 > 0$ and $y_2 > 0$. Are $Y_1$ and $Y_2$ independent?

- [Yes, because the joint density factors and the support is rectangular]{.correct data-explanation="✅ Correct! The density factors as g(y₁)·h(y₂) and the support (0,∞)×(0,∞) is rectangular."}
- Yes, because the density is positive everywhere
- No, because the density depends on both $y_1$ and $y_2$
- Cannot determine without computing marginals
```

## Summary Slide

```markdown
## 📝 Summary

::: {style="font-size: 30px"}
::: {.summary-box}
**✅ Key Takeaways**

- **[Concept 1]** [brief description matching learning objective 1]

- **[Concept 2]** [brief description matching learning objective 2]

- **[Concept 3]** [brief description matching learning objective 3]

- **[Concept 4]** [brief description matching learning objective 4]

- **[Concept 5]** [brief description matching learning objective 5]
:::
:::
```

## Practice Problems Slide

```markdown
## 📚 Practice Problems

::: {.callout-tip}
## 📝 Homework Problems

**Problem 1 ([Type]):** [Problem statement]

**Problem 2 ([Type]):** [Problem statement]

**Problem 3 ([Type]):** [Problem statement]

**Problem 4 (Financial Application):** [Problem with finance context]
:::
```

## Key Findings Slide (for Case Studies)

```markdown
## 💰 Case Study: Key Findings

::: {style="font-size: 45px"}
::: {.callout-important}
## 📊 Analysis Results

::: {.columns}

::: {.column width="33%"}
::: {.fragment}
**[Finding Category 1]:**

- [Point 1]

- [Point 2]

- [Point 3]
:::
:::

::: {.column width="33%"}
::: {.fragment}
**[Finding Category 2]:**

- [Point 1]

- [Point 2]

- [Point 3]
:::
:::

::: {.column width="33%"}
::: {.fragment}
**[Finding Category 3]:**

1. **[Implication 1]**: [Description]

2. **[Implication 2]**: [Description]

3. **[Implication 3]**: [Description]
:::
:::

:::
:::
:::
```

## 3D Surface Plot (OJS)

```markdown
## 🎮 3D Visualization {.smaller}

::: {style="font-size: 0.75em;"}

```{ojs}
//| echo: false

// Import Plotly
Plotly = require("https://cdn.plot.ly/plotly-2.24.1.min.js")

// Generate surface data
surfaceData = {
  const n = 50;
  const x = Array.from({length: n}, (_, i) => i / (n-1) * 2);
  const y = Array.from({length: n}, (_, i) => i / (n-1) * 2);
  const z = [];
  
  for (let j = 0; j < n; j++) {
    const row = [];
    for (let i = 0; i < n; i++) {
      // Example: f(x,y) = x*y for 0 < x,y < 2
      row.push(x[i] * y[j] / 2);
    }
    z.push(row);
  }
  return {x, y, z};
}

// Create 3D plot
viewof plot3d = {
  const div = document.createElement("div");
  div.style.width = "100%";
  div.style.height = "450px";
  
  Plotly.newPlot(div, [{
    type: 'surface',
    x: surfaceData.x,
    y: surfaceData.y,
    z: surfaceData.z,
    colorscale: 'Viridis'
  }], {
    title: 'Joint PDF Surface',
    scene: {
      xaxis: {title: 'Y₁'},
      yaxis: {title: 'Y₂'},
      zaxis: {title: 'f(y₁, y₂)'}
    },
    margin: {l: 0, r: 0, b: 0, t: 40}
  });
  
  return div;
}
```

:::
```

## Emoji Reference

| Section | Emoji |
|---------|-------|
| Learning Objectives | 🎯 |
| Overview | 📋 |
| Definition | 📖 📝 |
| Theorem | 🧮 |
| Example | 📌 |
| Interactive | 🎮 |
| Case Study | 💰 |
| Quiz | 📝 |
| Summary | 📝 ✅ |
| Practice | 📚 |
| Thank You | 👋 |
| Questions | ❓ 💬 |
| Important | ⚠️ |
| Tip | 💡 |
| Note | 📌 |
