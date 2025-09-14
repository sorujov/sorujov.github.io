---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

Education
======
* Ph.D in Statistics, [University Name], [Year] 
* M.S. in Mathematics, [University Name], [Year]
* B.S. in Mathematics, [University Name], [Year]

Work Experience
======
* Current: Assistant Professor of Mathematics and Statistics
  * ADA University, Baku, Azerbaijan
  * Duties include: Teaching, research in time series analysis and econometrics
  * Research focus: Statistical modeling, machine learning applications

Research Interests
======
* Time Series Analysis
* Econometrics
* Machine Learning
* Statistical Modeling
* Computational Statistics

Technical Skills
======
* Programming Languages
  * Python (Advanced)
  * R (Advanced)
  * SQL
* Statistical Software
  * STATA
  * SPSS
  * SAS
* Machine Learning
  * Scikit-learn
  * TensorFlow
  * PyTorch

Publications
======
  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Talks
======
  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html  %}
  {% endfor %}</ul>
  
Teaching
======
  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Professional Memberships
======
* [Professional organizations as listed in CV]

Awards and Honors
======
* [Awards and honors from CV]
