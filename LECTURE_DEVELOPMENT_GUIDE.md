# How to Add New Interactive Lectures

## Quick Start Guide

### Directory Structure
```
lectures/math-stat-1/
├── 01-combinatorics/     ✅ Complete
├── 02-[your-topic]/      📝 Next lecture
├── 03-[your-topic]/      📝 Future
└── _template/            � Copy this for new lectures
```

### Adding a New Lecture (3 Steps)

#### Step 1: Copy Template
```bash
# Copy the template directory
cp -r "lectures/math-stat-1/_template" "lectures/math-stat-1/02-probability"
```

#### Step 2: Edit Content
Edit these files in your new directory:
- **`index.html`** - Replace slide content with your material
- **`app.js`** - Update quiz answers and slide count
- Keep `style.css` and `print-styles.css` unchanged

#### Step 3: Update Master Page
In `_pages/math-stat-1-lectures.md`, add:
```markdown
### Lecture 2: Your Topic Name
**[🚀 Launch Interactive Lecture](/lectures/math-stat-1/02-your-topic/index.html)**
{: .btn .btn--primary .btn--large}
```

#### Step 4: Deploy
```bash
git add -A
git commit -m "Add Lecture 2: Your Topic"
git push origin master
```

## Template Files
- `index.html` - Main presentation structure  
- `app.js` - Interactive functionality
- `style.css` - Consistent styling
- `print-styles.css` - Print formatting

## Key URLs
- Course page: `/teaching/2022-mathematical-statistics`
- Lecture hub: `/teaching/math-stat-1-lectures/`
- Individual lecture: `/lectures/math-stat-1/XX-topic/index.html`

That's it! The system is designed to be simple and systematic.

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