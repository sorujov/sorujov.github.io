# Wackerly Book Chapter Reference

Mathematical Statistics with Applications, 7th Edition
Authors: Dennis D. Wackerly, William Mendenhall III, Richard L. Scheaffer

## Complete Table of Contents

### Chapter 1: What Is Statistics? (pp. 1-19)
- 1.1 Introduction
- 1.2 Characterizing a Set of Measurements: Graphical Methods
- 1.3 Characterizing a Set of Measurements: Numerical Methods
- 1.4 How Inferences Are Made
- 1.5 Theory and Reality
- 1.6 Summary

**Lecture split:** Single introductory lecture

---

### Chapter 2: Probability (pp. 20-85)
- 2.1 Introduction
- 2.2 Probability and Inference
- 2.3 A Review of Set Notation
- 2.4 A Probabilistic Model for an Experiment: The Discrete Case
- 2.5 Calculating the Probability of an Event: The Sample-Point Method
- 2.6 Tools for Counting Sample Points
- 2.7 Conditional Probability and the Independence of Events
- 2.8 Two Laws of Probability
- 2.9 Calculating the Probability of an Event: The Event-Composition Method
- 2.10 The Law of Total Probability and Bayes' Rule
- 2.11 Numerical Events and Random Variables
- 2.12 Random Sampling
- 2.13 Summary

**Lecture split:**
- Lecture 1: Sections 2.1-2.6 (Probability basics, counting)
- Lecture 2: Sections 2.7-2.10 (Conditional probability, Bayes)
- Lecture 3: Sections 2.11-2.12 (Random variables intro)

---

### Chapter 3: Discrete Random Variables and Their Probability Distributions (pp. 86-156)
- 3.1 Basic Definition
- 3.2 The Probability Distribution for a Discrete Random Variable
- 3.3 The Expected Value of a Random Variable or a Function of a Random Variable
- 3.4 The Binomial Probability Distribution
- 3.5 The Geometric Probability Distribution
- 3.6 The Negative Binomial Probability Distribution (Optional)
- 3.7 The Hypergeometric Probability Distribution
- 3.8 The Poisson Probability Distribution
- 3.9 Moments and Moment-Generating Functions
- 3.10 Probability-Generating Functions (Optional)
- 3.11 Tchebysheff's Theorem
- 3.12 Summary

**Key Definitions:**
- Definition 3.1: Discrete random variable
- Definition 3.2: Probability function p(y)
- Definition 3.3: Distribution function F(y)
- Definition 3.4: Expected value E[Y]
- Definition 3.5: Variance V(Y)

**Key Theorems:**
- Theorem 3.1: Properties of distribution functions
- Theorem 3.2: E[g(Y)] computation
- Theorem 3.3: Variance formula V(Y) = E[Y²] - μ²

**Lecture split:**
- Lecture 1: Sections 3.1-3.3 (Definitions, expected value)
- Lecture 2: Sections 3.4-3.8 (Named distributions)
- Lecture 3: Sections 3.9-3.11 (MGFs, Tchebysheff)

---

### Chapter 4: Continuous Variables and Their Probability Distributions (pp. 157-222)
- 4.1 Introduction
- 4.2 The Probability Distribution for a Continuous Random Variable
- 4.3 Expected Values for Continuous Random Variables
- 4.4 The Uniform Probability Distribution
- 4.5 The Normal Probability Distribution
- 4.6 The Gamma Probability Distribution
- 4.7 The Beta Probability Distribution
- 4.8 Some General Comments
- 4.9 Other Expected Values
- 4.10 Tchebysheff's Theorem
- 4.11 Expectations of Discontinuous Functions and Mixed Probability Distributions (Optional)
- 4.12 Summary

**Key Definitions:**
- Definition 4.1: Probability density function f(y)
- Definition 4.2: Distribution function for continuous RV
- Definition 4.3: Expected value for continuous RV

**Lecture split:**
- Lecture 1: Sections 4.1-4.3 (PDF, CDF, expected values)
- Lecture 2: Sections 4.4-4.7 (Named distributions)
- Lecture 3: Sections 4.8-4.10 (Properties, Tchebysheff)

---

### Chapter 5: Multivariate Probability Distributions (pp. 223-295)
- 5.1 Introduction
- 5.2 Bivariate and Multivariate Probability Distributions
- 5.3 Marginal and Conditional Probability Distributions
- 5.4 Independent Random Variables
- 5.5 The Expected Value of a Function of Random Variables
- 5.6 Special Theorems
- 5.7 The Covariance of Two Random Variables
- 5.8 The Expected Value and Variance of Linear Functions of Random Variables
- 5.9 The Multinomial Probability Distribution
- 5.10 The Bivariate Normal Distribution (Optional)
- 5.11 Conditional Expectations
- 5.12 Summary

**Key Definitions:**
- Definition 5.1: Joint probability function p(y₁, y₂)
- Definition 5.2: Joint distribution function F(y₁, y₂)
- Definition 5.3: Joint probability density function f(y₁, y₂)
- Definition 5.4: Marginal probability functions
- Definition 5.5: Conditional probability function (discrete)
- Definition 5.6: Conditional distribution function
- Definition 5.7: Conditional density function (continuous)
- Definition 5.8: Independent random variables
- Definition 5.9: Expected value E[g(Y₁, Y₂)]
- Definition 5.10: Covariance Cov(Y₁, Y₂)
- Definition 5.11: Correlation coefficient ρ

**Key Theorems:**
- Theorem 5.1: Properties of joint probability functions
- Theorem 5.2: Properties of joint CDFs
- Theorem 5.3: Marginal densities from joint
- Theorem 5.4: Independence equivalent conditions
- Theorem 5.5: Factorization criterion for independence
- Theorem 5.6: E[c] = c
- Theorem 5.7: E[cg(Y)] = cE[g(Y)]
- Theorem 5.8: E[g₁ + g₂] = E[g₁] + E[g₂]
- Theorem 5.9: E[g(Y₁)h(Y₂)] = E[g(Y₁)]E[h(Y₂)] if independent
- Theorem 5.10: Cov(Y₁, Y₂) = E[Y₁Y₂] - μ₁μ₂
- Theorem 5.11: V(aY₁ + bY₂) formula
- Theorem 5.12: Properties of correlation

**Lecture split:** (as implemented in example files)
- Lecture 1: Sections 5.1-5.2 (Joint distributions, marginals) + start of 5.3
- Lecture 2: Sections 5.3-5.4 (Conditional distributions, independence)
- Lecture 3: Sections 5.5-5.8 (Expected values, covariance, correlation)

---

### Chapter 6: Functions of Random Variables (pp. 320-369, PDF pages 320-369)
- 6.1 Introduction (p.320)
- 6.2 Finding the Probability Distribution of a Function of Random Variables (p.321)
- 6.3 The Method of Distribution Functions (p.322)
- 6.4 The Method of Transformations (p.334)
- 6.5 The Method of Moment-Generating Functions (p.342)
- 6.6 Multivariable Transformations Using Jacobians (Optional) (p.349)
- 6.7 Order Statistics (p.357)
- 6.8 Summary (p.365)

**Key Definitions:**
- Definition 6.1: Transformation U = g(Y)
- Definition 6.2: Order statistics Y₍₁₎, Y₍₂₎, ..., Y₍ₙ₎
- Definition 6.3: Sample range R = Y₍ₙ₎ - Y₍₁₎

**Key Theorems:**
- Theorem 6.1: MGF uniqueness theorem (p.342)
- Theorem 6.2: Transformation method (univariate) (p.334)
- Theorem 6.3: Distribution of order statistics (p.357)
- Theorem 6.4: Joint distribution of order statistics (p.361)

**Key Examples from PDF:**
- Example 6.1 (p.323): Sugar refinery profit U = 3Y - 1
- Example 6.2 (p.323): Gasoline U = Y₁ - Y₂ with figure 6.1
- Example 6.3 (p.325): Sum of uniforms U = Y₁ + Y₂ (triangular)
- Example 6.4 (p.327): Min of exponentials
- Example 6.5 (p.329): Chi-square from normal squared
- Example 6.6 (p.335): Transformation method application
- Example 6.7 (p.337): Log-normal from normal
- Example 6.8 (p.343): Sum of independent normals via MGF
- Example 6.9 (p.344): Sum of chi-squares via MGF
- Example 6.10 (p.345): Sum of Poissons via MGF
- Example 6.11 (p.351): Bivariate Jacobian transformation
- Example 6.12 (p.353): Beta distribution derivation
- Example 6.13 (p.358): Order statistics of uniform sample
- Example 6.14 (p.362): Distribution of sample range

**Key Figures:**
- Figure 6.1 (p.324): Region for gasoline problem
- Figure 6.2 (p.325): Distribution and density functions
- Figure 6.3 (p.325): Unit square for sum of uniforms
- Figure 6.4 (p.326): Triangular density for sum
- Figure 6.5 (p.328): Region for minimum
- Figure 6.6 (p.358): Order statistics regions

---

### Chapter 7: Sampling Distributions and the Central Limit Theorem (pp. 346-389)
- 7.1 Introduction
- 7.2 Sampling Distributions Related to the Normal Distribution
- 7.3 The Central Limit Theorem
- 7.4 A Proof of the Central Limit Theorem (Optional)
- 7.5 The Normal Approximation to the Binomial Distribution
- 7.6 Summary

**Key Definitions:**
- Definition 7.1: Chi-square distribution
- Definition 7.2: t-distribution
- Definition 7.3: F-distribution

**Key Theorems:**
- Theorem 7.1: Distribution of sample mean (normal population)
- Theorem 7.2: Chi-square distribution of (n-1)S²/σ²
- Theorem 7.3: Independence of X̄ and S²
- Theorem 7.4: Central Limit Theorem

**Lecture split:**
- Lecture 1: Sections 7.1-7.2 (Sampling distributions, χ², t, F)
- Lecture 2: Sections 7.3-7.5 (CLT and applications)

---

### Chapter 8: Estimation (pp. 390-443)
- 8.1 Introduction
- 8.2 The Bias and Mean Square Error of Point Estimators
- 8.3 Some Common Unbiased Point Estimators
- 8.4 Evaluating the Goodness of a Point Estimator
- 8.5 Confidence Intervals
- 8.6 Large-Sample Confidence Intervals
- 8.7 Selecting the Sample Size
- 8.8 Small-Sample Confidence Intervals for μ and μ₁ - μ₂
- 8.9 Confidence Intervals for σ²
- 8.10 Summary

**Lecture split:**
- Lecture 1: Sections 8.1-8.4 (Point estimation)
- Lecture 2: Sections 8.5-8.7 (Confidence intervals, large sample)
- Lecture 3: Sections 8.8-8.9 (Small sample CIs)

---

### Chapter 9: Properties of Point Estimators and Methods of Estimation (pp. 444-487)
- 9.1 Introduction
- 9.2 Relative Efficiency
- 9.3 Consistency
- 9.4 Sufficiency
- 9.5 The Rao–Blackwell Theorem and Minimum-Variance Unbiased Estimation
- 9.6 The Method of Moments
- 9.7 The Method of Maximum Likelihood
- 9.8 Some Large-Sample Properties of Maximum-Likelihood Estimators (Optional)
- 9.9 Summary

**Lecture split:**
- Lecture 1: Sections 9.1-9.4 (Efficiency, consistency, sufficiency)
- Lecture 2: Sections 9.5-9.7 (MVUE, MoM, MLE)

---

### Chapter 10: Hypothesis Testing (pp. 488-562)
- 10.1 Introduction
- 10.2 Elements of a Statistical Test
- 10.3 Common Large-Sample Tests
- 10.4 Calculating Type II Error Probabilities and Finding the Sample Size for Z Tests
- 10.5 Relationships Between Hypothesis-Testing Procedures and Confidence Intervals
- 10.6 Another Way to Report the Results of a Statistical Test: p-Values
- 10.7 Some Comments on the Theory of Hypothesis Testing
- 10.8 Small-Sample Hypothesis Testing for μ and μ₁ - μ₂
- 10.9 Testing Hypotheses Concerning Variances
- 10.10 Power of Tests and the Neyman–Pearson Lemma
- 10.11 Likelihood Ratio Tests
- 10.12 Summary

**Lecture split:**
- Lecture 1: Sections 10.1-10.4 (Basics, large-sample tests)
- Lecture 2: Sections 10.5-10.9 (p-values, small-sample tests)
- Lecture 3: Sections 10.10-10.11 (Power, NP Lemma, LRT)

---

### Chapter 11: Linear Models and Estimation by Least Squares (pp. 563-639)
**Lecture split:**
- Lecture 1: Simple linear regression model, least squares
- Lecture 2: Inference for regression parameters
- Lecture 3: Multiple regression, matrix approach

---

### Chapter 12: Considerations in Designing Experiments (pp. 640-660)
Single lecture covering experimental design basics

---

### Chapter 13: The Analysis of Variance (pp. 661-728)
**Lecture split:**
- Lecture 1: One-way ANOVA
- Lecture 2: Two-way ANOVA, blocking

---

### Chapter 14: Analysis of Categorical Data (pp. 729-740)
Single lecture on chi-square tests

---

### Chapter 15: Nonparametric Statistics (pp. 741-795)
**Lecture split:**
- Lecture 1: Sign test, Wilcoxon signed-rank
- Lecture 2: Mann-Whitney, Kruskal-Wallis

---

### Chapter 16: Introduction to Bayesian Methods for Inference (pp. 796-820)
**Lecture split:**
- Lecture 1: Bayesian priors, posteriors, estimation
- Lecture 2: Credible intervals, hypothesis testing

---

## Common Probability Distributions Reference

### Discrete Distributions
| Distribution | PMF | Mean | Variance | MGF |
|-------------|-----|------|----------|-----|
| Binomial(n,p) | $\binom{n}{y}p^y(1-p)^{n-y}$ | np | np(1-p) | $[pe^t + (1-p)]^n$ |
| Geometric(p) | $p(1-p)^{y-1}$ | 1/p | (1-p)/p² | $pe^t/[1-(1-p)e^t]$ |
| Poisson(λ) | $\lambda^y e^{-\lambda}/y!$ | λ | λ | $e^{\lambda(e^t-1)}$ |
| Negative Binomial(r,p) | $\binom{y-1}{r-1}p^r(1-p)^{y-r}$ | r/p | r(1-p)/p² | $[pe^t/(1-(1-p)e^t)]^r$ |

### Continuous Distributions
| Distribution | PDF | Mean | Variance | MGF |
|-------------|-----|------|----------|-----|
| Uniform(θ₁,θ₂) | $1/(\theta_2-\theta_1)$ | (θ₁+θ₂)/2 | (θ₂-θ₁)²/12 | $(e^{t\theta_2}-e^{t\theta_1})/[t(\theta_2-\theta_1)]$ |
| Normal(μ,σ²) | $\frac{1}{\sigma\sqrt{2\pi}}e^{-(y-\mu)^2/(2\sigma^2)}$ | μ | σ² | $e^{\mu t + \sigma^2 t^2/2}$ |
| Exponential(β) | $\frac{1}{\beta}e^{-y/\beta}$ | β | β² | $(1-\beta t)^{-1}$ |
| Gamma(α,β) | $\frac{1}{\Gamma(\alpha)\beta^\alpha}y^{\alpha-1}e^{-y/\beta}$ | αβ | αβ² | $(1-\beta t)^{-\alpha}$ |
| Chi-square(ν) | $\frac{y^{(\nu/2)-1}e^{-y/2}}{2^{\nu/2}\Gamma(\nu/2)}$ | ν | 2ν | $(1-2t)^{-\nu/2}$ |
| Beta(α,β) | $\frac{\Gamma(\alpha+\beta)}{\Gamma(\alpha)\Gamma(\beta)}y^{\alpha-1}(1-y)^{\beta-1}$ | α/(α+β) | αβ/[(α+β)²(α+β+1)] | - |
