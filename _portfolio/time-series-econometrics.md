---
title: "Time Series Econometrics: open lecture notes"
excerpt: "Seventeen lectures, from stationarity to Value-at-Risk, with slides that run their own R code on real FRED data and a short narrated film for each idea. Based on my notes from Stanislav Anatolyev's course."
collection: portfolio
classes: wide
share: false
---

<div class="course-header">
  <h1>Time Series Econometrics</h1>
  <p>Open lecture notes. Seventeen lectures that take a single observed path of an economic series and ask what can honestly be learned from it: when averages converge, how to measure the uncertainty of dependent data, how to choose and judge forecasting models, how to test for unit roots, regimes and breaks, and how to model volatility and risk.</p>
</div>

<p>In 2016 I attended Stanislav Anatolyev's graduate course in time series econometrics and took my notes by hand on a tablet. These pages are those notes, reworked into slides. The structure and the choice of results follow his lectures; the slides, the examples, the code and any errors are mine. Lecture 8, and a few individual slides elsewhere, cover material that is missing from my notes; they are written from the standard texts and marked as such on the slide.</p>

<p>Each deck opens with a short film that gives the idea before the formalism; it is narrated by a synthetic copy of my voice. The slides are interactive: sliders redraw the figures, the quiz questions check themselves, and every number comes from R code that runs on real data from FRED, shipped with the deck. Open a deck in a browser; the arrow keys move between slides, and <code>F</code> gives full screen.</p>

<h3 class="tse-part">Foundations</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>1</td>
        <td><strong>Stationarity, Ergodicity and White Noise</strong></td>
        <td>Why one trajectory can stand in for many: strict stationarity, three strengths of white noise, ergodicity, and the law of large numbers that needs both.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/01-stationarity-ergodicity/stationarity_ergodicity_lecture1.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/01-stationarity-ergodicity/video/lecture1_intuition.mp4" target="_blank">Film 2:38 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>2</td>
        <td><strong>Ergodic Theorem, CLT and the Long-Run Variance</strong></td>
        <td>Averages of dependent data: the ergodic theorem, the CLT for martingale differences and in general, the long-run variance, and why the naive estimator fails while Newey–West works.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/02-clt-long-run-variance/clt_long_run_variance_lecture2.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/02-clt-long-run-variance/video/lecture2_intuition.mp4" target="_blank">Film 2:53 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>3</td>
        <td><strong>Time-Series Regression and HAC Inference</strong></td>
        <td>OLS on time series: when White standard errors suffice, when HAC is needed, Mishkin's inflation regressions with overlapping horizons; structural versus non-structural models.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/03-time-series-regression-hac/time_series_regression_hac_lecture3.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/03-time-series-regression-hac/video/lecture3_intuition.mp4" target="_blank">Film 2:32 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h3 class="tse-part">Choosing and judging models</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>4</td>
        <td><strong>What to Model, and How to Choose a Model</strong></td>
        <td>The objects of modelling — conditional mean, variance, quantiles, density — and the tools for choosing a model: diagnostics, general-to-specific testing, AIC, BIC and Hannan–Quinn.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/04-objects-model-selection/objects_model_selection_lecture4.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/04-objects-model-selection/video/lecture4_intuition.mp4" target="_blank">Film 2:34 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>5</td>
        <td><strong>In-Sample Fit, Out-of-Sample Forecasts, Diebold–Mariano</strong></td>
        <td>In-sample fit against out-of-sample forecasting, fixed, rolling and recursive schemes, and the Diebold–Mariano test of equal predictive ability.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/05-forecast-evaluation/forecast_evaluation_lecture5.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/05-forecast-evaluation/video/lecture5_intuition.mp4" target="_blank">Film 2:49 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>6</td>
        <td><strong>Data Snooping, Superior Predictive Ability, Model Confidence Sets</strong></td>
        <td>Searching over many models: data snooping, White's Reality Check, Hansen's SPA test and the model confidence set.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/06-superior-predictive-ability/superior_predictive_ability_lecture6.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/06-superior-predictive-ability/video/lecture6_intuition.mp4" target="_blank">Film 2:41 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h3 class="tse-part">Linear models for the mean</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>7</td>
        <td><strong>Linear Projection, Innovations and the Wold Decomposition</strong></td>
        <td>Linear projection on the infinite past, innovations, the Wold decomposition, impulse responses, and invertibility of moving averages.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/07-wold-decomposition/wold_decomposition_lecture7.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/07-wold-decomposition/video/lecture7_intuition.mp4" target="_blank">Film 2:50 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>8</td>
        <td><strong>ARMA Models: Identification, Estimation, Forecasting</strong></td>
        <td>ARMA models: roots, ACF and PACF, estimation by least squares and likelihood, the Box–Jenkins cycle, and h-step forecasts with their uncertainty.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/08-arma-estimation-forecasting/arma_estimation_forecasting_lecture8.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/08-arma-estimation-forecasting/video/lecture8_intuition.mp4" target="_blank">Film 2:33 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>9</td>
        <td><strong>Trends, Unit Roots and Brownian Motion</strong></td>
        <td>Deterministic and stochastic trends, OLS rates of convergence, the unit-root limit, Brownian motion and the functional CLT.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/09-trends-unit-root-asymptotics/trends_unit_root_asymptotics_lecture9.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/09-trends-unit-root-asymptotics/video/lecture9_intuition.mp4" target="_blank">Film 2:30 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>10</td>
        <td><strong>Dickey–Fuller, Phillips–Perron and ADF Tests</strong></td>
        <td>Testing for a unit root: the Dickey–Fuller distributions, deterministic terms, Phillips–Perron and augmented Dickey–Fuller, and why power is low near one.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/10-dickey-fuller-tests/dickey_fuller_tests_lecture10.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/10-dickey-fuller-tests/video/lecture10_intuition.mp4" target="_blank">Film 2:57 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h3 class="tse-part">Nonlinear models for the mean</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>11</td>
        <td><strong>Nonlinear Models and Threshold Autoregression</strong></td>
        <td>Why nonlinear models; bilinear and threshold autoregressions, regimes, stationarity with an explosive regime, and estimation by concentrated least squares.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/11-threshold-autoregression/threshold_autoregression_lecture11.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/11-threshold-autoregression/video/lecture11_intuition.mp4" target="_blank">Film 2:35 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>12</td>
        <td><strong>Threshold Inference and Smooth Transition</strong></td>
        <td>Inference on the threshold: Hansen's likelihood-ratio confidence set, testing linearity with sup-F and the fixed-regressor bootstrap, and smooth transition (LSTAR, ESTAR).</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/12-tar-inference-star/tar_inference_star_lecture12.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/12-tar-inference-star/video/lecture12_intuition.mp4" target="_blank">Film 2:52 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>13</td>
        <td><strong>Markov Switching and State-Space Models</strong></td>
        <td>Linearity tests against STAR, Markov-switching autoregressions, the Hamilton filter and maximum likelihood, and state-space models.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/13-markov-switching/markov_switching_lecture13.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/13-markov-switching/video/lecture13_intuition.mp4" target="_blank">Film 2:50 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h3 class="tse-part">Several series at once</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>14</td>
        <td><strong>Vector Autoregressions, Impulse Responses and Cointegration</strong></td>
        <td>Vector autoregressions: estimation, impulse responses, variance decompositions, Granger causality, spurious regression and cointegration.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/14-var-irf-cointegration/var_irf_cointegration_lecture14.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/14-var-irf-cointegration/video/lecture14_intuition.mp4" target="_blank">Film 2:35 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h3 class="tse-part">Volatility, stability and risk</h3>
<div class="schedule-table">
  <table>
    <thead><tr><th>&nbsp;</th><th>Lecture</th><th>What it covers</th><th>Materials</th></tr></thead>
    <tbody>
      <tr>
        <td>15</td>
        <td><strong>Volatility — ARCH and GARCH</strong></td>
        <td>Conditional variance: ARCH and GARCH, Gaussian quasi-maximum likelihood with robust standard errors, the ARCH-LM test, multivariate GARCH and stochastic volatility.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/15-arch-garch/arch_garch_lecture15.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/15-arch-garch/video/lecture15_intuition.mp4" target="_blank">Film 2:58 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>16</td>
        <td><strong>Structural Breaks and Parameter Stability</strong></td>
        <td>Breaks at known and unknown dates: Chow and sup-Wald tests, Andrews' critical values, Bai–Perron multiple breaks, and CUSUM monitoring.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/16-structural-breaks/structural_breaks_lecture16.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/16-structural-breaks/video/lecture16_intuition.mp4" target="_blank">Film 2:29 &#9654;</a></div></td>
      </tr>
      <tr>
        <td>17</td>
        <td><strong>Realized Volatility, Durations, Direction and Value-at-Risk</strong></td>
        <td>Measuring risk: RiskMetrics, realized volatility, duration models, direction-of-change models, Value-at-Risk and its backtest, and CAViaR.</td>
        <td><div class="material-links"><a class="slide-link" href="/lectures/time-series-econometrics/17-realized-volatility-var/realized_volatility_var_lecture17.html" target="_blank">Slides &rarr;</a><a class="slide-link" href="/lectures/time-series-econometrics/17-realized-volatility-var/video/lecture17_intuition.mp4" target="_blank">Film 2:37 &#9654;</a></div></td>
      </tr>
    </tbody>
  </table>
</div>

<h2 id="reading">Reading</h2>

<ul>
  <li>Hamilton, J. D. (1994). <em>Time Series Analysis</em>. Princeton University Press.</li>
  <li>Tsay, R. S. (2010). <em>Analysis of Financial Time Series</em>, 3rd ed. Wiley.</li>
  <li>Franses, P. H. and van Dijk, D. (2000). <em>Non-Linear Time Series Models in Empirical Finance</em>. Cambridge University Press.</li>
  <li>Anatolyev, S. Syllabus of <em>Applied Time Series Econometrics</em>, New Economic School, for the current reading list and the original papers.</li>
</ul>
