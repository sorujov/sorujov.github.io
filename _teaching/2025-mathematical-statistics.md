---
title: "Discrete Random Variables"
subtitle: "Mathematical Statistics"
author:
  - name: "Samir Orujov, PhD"
    affiliations:
      - name: "ADA University, School of Business"
      - name: "Information Communication Technologies Agency, Statistics Unit"
date: 2025-10-18
format:
  revealjs:
    theme: default
    logo: ADA.png
    transition: slide
    slide-number: true
    chalkboard: true
    controls: true
    navigation-mode: vertical
    width: 1280
    height: 720
    footer: "Mathematical Statistics - Discrete Random Variables"
    incremental: false
    highlight-style: tango
    code-fold: true
    menu: true
    progress: true
    history: true
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

## {.title-slide}

# Discrete Random Variables
### Mathematical Statistics
#### Samir Orujov, PhD
#### ADA University, School of Business
#### Information Communication Technologies Agency, Statistics Unit
#### October 18, 2025

---

## Course Objectives {.center}

:::: {.columns}
::: {.column width="50%"}
- Understand the role of statistics in science and decision-making
- Define and work with random variables
- Master discrete probability distributions
- Apply probability functions to real problems
:::
::: {.column width="50%"}
- Develop intuition for sampling and inference
- Solve problems using probability tables and graphs
- Engage in collaborative learning and critical thinking
:::
::::

---

## Course Outline {.center}

- Introduction to Statistics
- Random Variables
- Discrete Random Variables
- Probability Functions and Distributions
- Examples and Applications
- Student Engagement Activities
- Homework and Practice Problems

---

## Think-Pair-Share: What is Statistics? {.center}

::: {.fragment .fade-in}
**🤔 Think (1 minute):**  
In your own words, what does "statistics" mean to you? How do you use it in daily life?
:::

::: {.fragment .fade-in}
**👥 Pair (2 minutes):**  
Share your definition with a neighbor. Find common themes.
:::

::: {.fragment .fade-in}
**🗣️ Share:**  
Let's hear some definitions before we explore formal ones!
:::

---

## Definitions of Statistics {.center}

::: {.callout-note icon=false}
**Webster's New Collegiate Dictionary:**  
Statistics is "a branch of mathematics dealing with the collection, analysis, interpretation, and presentation of masses of numerical data."
:::

::: {.fragment .fade-in}
**Stuart and Ord (1991):**  
"Statistics is the branch of the scientific method which deals with the data obtained by counting or measuring the properties of populations."
:::

---

## Definitions of Statistics (cont.) {.center}

::: {.callout-note icon=false}
**Rice (1995):**  
Statistics is "essentially concerned with procedures for analyzing data, especially data that in some vague sense have a random character."
:::

::: {.fragment .fade-in}
**Key Insight:**  
All definitions emphasize data and uncertainty!
:::

---

## Definitions of Statistics (cont.) {.center}

::: {.callout-note icon=false}
**Freund and Walpole (1987):**  
Statistics encompasses "the science of basing inferences on observed data and the entire problem of making decisions in the face of uncertainty."
:::

::: {.fragment .fade-in}
**Mood, Graybill, and Boes (1974):**  
Statistics is "the technology of the scientific method" and is concerned with:
1. The design of experiments and investigations
2. Statistical inference
:::

---

## The Core Objective {.center}

::: {.callout-important}
**Central Goal of Statistics:**  
The objective of statistics is to make an inference about a population based on information contained in a sample from that population and to provide an associated measure of goodness for the inference.
:::

::: {.fragment .fade-in}
