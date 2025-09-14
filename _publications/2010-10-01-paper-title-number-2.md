---
title: "VS-LTGARCHX: A Flexible Variable Selection in Log-TGARCHX Models"
collection: publications
category: manuscripts
permalink: /publication/2024-11-05-vs-ltgarchx
excerpt: 'This paper proposes the VS-LTGARCHX algorithm which incorporates variable selection into the log-TGARCHX estimation process, demonstrating superior one-step-ahead forecasting performance on Bitcoin volatility using 42 conditioning variables.'
date: 2024-11-05
venue: 'Journal of Time Series Econometrics'
slidesurl: 'https://sorujov.github.io/files/vs_ltgarchx_slides.pdf'
paperurl: 'https://sorujov.github.io/files/vs_ltgarchx_paper.pdf'
citation: 'Orujov, S., Elvira, V., Poterie, A., Rajabov, F., & Septier, F. (2024). &quot;VS-LTGARCHX: A Flexible Variable Selection in Log-TGARCHX Models.&quot; <i>Journal of Time Series Econometrics</i>. https://doi.org/10.1515/jtse-2023-0035'
---

This paper proposes the VS-LTGARCHX algorithm, a novel three-step methodology that incorporates variable selection procedures into the log-TGARCHX model estimation process. The log-TGARCHX model offers greater flexibility than standard GARCHX models by relaxing non-negativity constraints on parameters and exogenous variables, while maintaining positivity of conditional variance through logarithmic specification.

## Key Contributions

* **Novel Algorithm**: Developed VS-LTGARCHX, a flexible three-step procedure embedding variable selection (LASSO, ABESS, Boruta) into log-TGARCHX estimation
* **Theoretical Foundation**: Established statistical equivalence between penalized ARMAX regression and direct optimization under orthogonality conditions (Proposition 1)
* **Empirical Application**: Applied to Bitcoin market volatility forecasting using 42 exogenous variables from blockchain technology, public opinion, financial markets, and macroeconomic indicators
* **Superior Performance**: Demonstrated improved one-step-ahead forecasting accuracy compared to log-GARCH(1,1) and full log-TGARCHX benchmarks

## Methodology

The VS-LTGARCHX algorithm consists of three steps:
1. **ARMA Fitting**: Estimate base ARMA(p₁,p₂) model and extract residuals
2. **Variable Selection**: Apply LASSO, ABESS, or Boruta to select optimal subset of exogenous variables and asymmetry terms
3. **Final Estimation**: Fit log-TGARCHX model with selected variables using ARMA-based least squares

## Empirical Results

**Dataset**: Bitcoin daily data (Dec 2017 - Jun 2022, 1,643 observations) with 42 conditioning variables

**Performance Metrics** (Test Set):
- **LASSO variant**: RMSE = 1.60, QLIKE = 3.64
- **ABESS variant**: RMSE = 1.59, QLIKE = 3.64  
- **Boruta variant**: RMSE = 1.66, QLIKE = 3.69
- **Log-GARCH benchmark**: RMSE = 2.00, QLIKE = 3.74
- **Log-TGARCHX benchmark**: RMSE = 1.85, QLIKE = 3.82

**Model Confidence Set (MCS)** testing confirmed statistical superiority of VS-LTGARCHX variants over benchmarks.

## Selected Variables

Key variables consistently selected across methods:
- **VIX Index** (first difference): Volatility spillover effects
- **Google Trends** (Bitcoin): Public sentiment proxy  
- **Weekly Realized Volatility**: Short-term persistence patterns

The algorithm successfully identified parsimonious models that outperform both overfitted (full) and underfitted (log-GARCH) alternatives, supporting the bias-variance tradeoff principle in volatility forecasting.

## Code and Data

Supplementary materials, R code, and datasets are available at: https://github.com/salahaddiniayyubi/Log-TGARCHX-Subset-Selection
