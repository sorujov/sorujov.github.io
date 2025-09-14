---
layout: archive
title: "Mathematical Statistics - Interactive Lectures"
permalink: /teaching/math-stat-1-lectures/
author_profile: true
---

{% include base_path %}

# Mathematical Statistics I - Interactive Lecture Series

**Course**: MATH 315 - Mathematical Statistics  
**Instructor**: Dr. Samir Orujov  
**Department**: Mathematics and Statistics, ADA University  

---

## Available Lectures

### Lecture 1: Combinatorial Analysis
**[🚀 Launch Interactive Lecture](/lectures/math-stat-1/01-combinatorics/index.html)**
{: .btn .btn--primary .btn--large}

**Topics:** Counting principles, permutations, combinations, arrangements with repetition  
**Features:** 30 interactive slides, built-in calculators, quizzes, mathematical visualizations  
**Duration:** Self-paced (approximately 45-60 minutes)

---

## Adding New Lectures

To add a new lecture, follow this simple process:

### 1. Create Lecture Directory
```bash
# Copy the template
cp -r "lectures/math-stat-1/_template" "lectures/math-stat-1/02-your-topic"
```

### 2. Edit Content
- Update `index.html` with your slides
- Modify `app.js` for interactive elements
- Keep `style.css` and `print-styles.css` as-is

### 3. Add to This Page
Add a new lecture entry above with the format:
```markdown
### Lecture X: Your Topic
**[🚀 Launch Interactive Lecture](/lectures/math-stat-1/0X-your-topic/index.html)**
{: .btn .btn--primary .btn--large}
```

### 4. Deploy
```bash
git add -A
git commit -m "Add Lecture X: Your Topic"
git push origin master
```

---

## Technical Notes
- **Fullscreen**: Press F11 for optimal viewing
- **Navigation**: Arrow keys or buttons
- **Requirements**: Modern browser with JavaScript enabled
- **Printing**: All lectures include print-friendly styles

---

*For questions: [sorujov@ada.edu.az](mailto:sorujov@ada.edu.az)*