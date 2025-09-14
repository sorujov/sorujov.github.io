# Mathematical Statistics Interactive Lectures - Development Guide

## 📁 Directory Structure

```
assets/teaching/math-stat-1/
├── lecture-01-combinatorics/     # ✅ Completed
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── print-styles.css
├── lecture-02-probability/       # 📝 Next to add
├── lecture-03-random-variables/  # 📝 Future
└── ...
```

## 🛠️ How to Add a New Interactive Lecture

### Step 1: Create Directory Structure
```bash
# Create new lecture directory
mkdir "assets/teaching/math-stat-1/lecture-XX-[topic-name]/"
cd "assets/teaching/math-stat-1/lecture-XX-[topic-name]/"
```

### Step 2: Copy Template Files
Copy these files from `lecture-01-combinatorics` as templates:
- `index.html` - Main presentation structure
- `app.js` - Interactive functionality  
- `style.css` - Styling (usually consistent)
- `print-styles.css` - Print formatting

### Step 3: Update HTML Content
In `index.html`:
1. Update `<title>` tag
2. Update presenter information
3. Replace slide content (keep the slide structure)
4. Update slide counter total: `<span id="totalSlides">XX</span>`

### Step 4: Update JavaScript
In `app.js`:
1. Update class name and constructor
2. Update `totalSlides` count
3. Modify quiz answers if applicable
4. Update any topic-specific interactive elements

### Step 5: Update Master Lecture List
Edit `_pages/math-stat-1-lectures.md`:
1. Add new lecture entry under appropriate unit
2. Update the launch button link
3. List topics covered
4. Update "Last Updated" date

### Step 6: Test and Deploy
```bash
git add -A
git commit -m "Add Lecture XX: [Topic Name] to Mathematical Statistics"
git push origin master
```

## 📋 Lecture Template Checklist

When creating a new lecture, ensure:
- [ ] Directory follows naming convention: `lecture-XX-[topic-name]`
- [ ] All 4 core files present (HTML, JS, CSS, print-CSS)
- [ ] Title and content updated in HTML
- [ ] Slide count matches in both HTML and JS
- [ ] Interactive elements work properly
- [ ] MathJax renders mathematical notation correctly
- [ ] Print styles are functional
- [ ] Master lecture list page updated
- [ ] Proper navigation between slides
- [ ] Quiz answers updated if applicable

## 🎯 Recommended Lecture Topics (Future)

### Unit 2: Probability Theory
- Lecture 2: Probability Axioms and Properties
- Lecture 3: Random Variables and Distributions

### Unit 3: Special Distributions  
- Lecture 4: Discrete Distributions (Binomial, Poisson)
- Lecture 5: Continuous Distributions (Normal, Exponential)

### Unit 4: Sampling and Estimation
- Lecture 6: Sampling Distributions
- Lecture 7: Central Limit Theorem
- Lecture 8: Point and Interval Estimation

### Unit 5: Hypothesis Testing
- Lecture 9: Fundamentals of Hypothesis Testing
- Lecture 10: Specific Test Procedures

## 💡 Best Practices

1. **Consistent Styling**: Use the same CSS framework across lectures
2. **Interactive Elements**: Include calculators, quizzes, or simulations where appropriate
3. **Mathematical Notation**: Ensure proper MathJax configuration
4. **Self-Contained**: Each lecture should be independent
5. **Mobile Responsive**: Test on different screen sizes
6. **Accessibility**: Include alt text and proper headings

## 📞 Support

For questions about adding new lectures:
**Dr. Samir Orujov** - sorujov@ada.edu.az

---
*Created: September 15, 2025*