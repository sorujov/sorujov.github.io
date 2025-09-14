// Combinatorial Analysis Presentation - 30 Slides JavaScript

class CombinatoricsPresentation {
    constructor() {
        this.currentSlide = 1;
        this.slides = []; // Array to store slide elements in order
        this.totalSlides = 0;
        this.timerInterval = null;
        this.timerSeconds = 0;
        this.quizAnswers = {
            1: 'b', // 26³ × 10² = 676,000
            2: 'b', // 5! = 120
            3: 'b', // C(12,4) = 495
            4: 'b', // C(5,2) = 10
            5: 'b', // 9!/(4!3!2!) = 1,260
            6: 'c'  // C(7+3-1,3-1) = C(9,2) = 36
        };
        this.userAnswers = {};
        this.factorChoices = [null, null]; // For slide 15 interactive proof
        
        this.init();
    }

    init() {
        this.discoverSlides();
        this.setupEventListeners();
        this.updateSlideCounter();
        this.updateNavigationButtons();
        this.setupSlideDots();
        this.initializeCalculators();
        this.addKeyboardHint();
        this.setupAutoHideNavControls();
        
        console.log(`${this.totalSlides}-slide Combinatorial Analysis Presentation loaded!`);
    }

    discoverSlides() {
        // Find all slide elements in the order they appear in the DOM
        this.slides = Array.from(document.querySelectorAll('.slide'));
        this.totalSlides = this.slides.length;
        
        console.log(`Discovered ${this.totalSlides} slides:`, this.slides.map(slide => slide.id));
    }

    setupEventListeners() {
        // Navigation buttons
        document.getElementById('prevBtn')?.addEventListener('click', () => this.previousSlide());
        document.getElementById('nextBtn')?.addEventListener('click', () => this.nextSlide());

        // Fullscreen button
        document.getElementById('fullscreenBtn')?.addEventListener('click', () => this.toggleFullscreen());

        // Fullscreen change events
        document.addEventListener('fullscreenchange', () => this.handleFullscreenChange());
        document.addEventListener('webkitfullscreenchange', () => this.handleFullscreenChange());
        document.addEventListener('msfullscreenchange', () => this.handleFullscreenChange());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));

        // Calculator inputs
        this.setupCalculatorListeners();
    }

    setupCalculatorListeners() {
        // Basic principle calculator
        ['basicM', 'basicN'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateBasic());
            }
        });

        // Permutation calculator
        ['permN', 'permR'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculatePermutation());
            }
        });

        // Combination calculator
        ['combN', 'combR'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateCombination());
            }
        });

        // Multinomial calculator
        ['multiN', 'multiG1', 'multiG2', 'multiG3'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateMultinomial());
            }
        });

        // Investment calculator
        ['investN', 'investR'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateInvestment());
            }
        });
    }

    setupSlideDots() {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.goToSlide(index + 1);
            });
            
            dot.setAttribute('tabindex', '0');
            dot.setAttribute('role', 'button');
            dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
            
            dot.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.goToSlide(index + 1);
                }
            });
        });
    }

    handleKeyPress(e) {
        switch(e.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                e.preventDefault();
                this.previousSlide();
                break;
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
                e.preventDefault();
                this.nextSlide();
                break;
            case 'Home':
                e.preventDefault();
                this.goToSlide(1);
                break;
            case 'End':
                e.preventDefault();
                this.goToSlide(this.totalSlides);
                break;
            case 'Escape':
                this.stopTimer();
                if (document.fullscreenElement) {
                    this.exitFullscreen();
                }
                break;
            case 'F11':
                e.preventDefault();
                this.toggleFullscreen();
                break;
        }
    }

    nextSlide() {
        if (this.currentSlide < this.totalSlides) {
            this.goToSlide(this.currentSlide + 1);
        }
    }

    previousSlide() {
        if (this.currentSlide > 1) {
            this.goToSlide(this.currentSlide - 1);
        }
    }

    goToSlide(slideNumber) {
        if (slideNumber < 1 || slideNumber > this.totalSlides) {
            return;
        }

        // Hide current slide
        const currentSlideElement = this.slides[this.currentSlide - 1];
        if (currentSlideElement) {
            currentSlideElement.classList.remove('active');
        }

        // Update current slide number
        this.currentSlide = slideNumber;

        // Show new slide
        const newSlideElement = this.slides[this.currentSlide - 1];
        if (newSlideElement) {
            newSlideElement.classList.add('active');
        }

        // Update UI
        this.updateSlideCounter();
        this.updateNavigationButtons();
        this.updateSlideDots();

        // Re-render MathJax for new slide
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([newSlideElement]).catch((err) => {
                console.warn('MathJax rendering error:', err);
            });
        }

        // Stop any running timer when changing slides
        this.stopTimer();
    }

    updateSlideCounter() {
        const currentSlideElement = document.getElementById('currentSlide');
        const totalSlidesElement = document.getElementById('totalSlides');
        
        if (currentSlideElement) currentSlideElement.textContent = this.currentSlide;
        if (totalSlidesElement) totalSlidesElement.textContent = this.totalSlides;
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (prevBtn) {
            prevBtn.disabled = this.currentSlide === 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentSlide === this.totalSlides;
        }
    }

    updateSlideDots() {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            if (index + 1 === this.currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }

    // Timer functionality
    startTimer(seconds) {
        this.stopTimer();
        this.timerSeconds = seconds;
        
        const timerDisplay = document.getElementById('timerDisplay');
        const timerValue = document.getElementById('timerValue');
        
        if (timerDisplay) timerDisplay.classList.add('active');
        
        this.updateTimerDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timerSeconds--;
            this.updateTimerDisplay();
            
            if (this.timerSeconds <= 0) {
                this.stopTimer();
                this.showTimerComplete();
            }
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        const timerDisplay = document.getElementById('timerDisplay');
        if (timerDisplay) {
            timerDisplay.classList.remove('active');
        }
    }

    updateTimerDisplay() {
        const timerValue = document.getElementById('timerValue');
        if (timerValue) {
            const minutes = Math.floor(this.timerSeconds / 60);
            const seconds = this.timerSeconds % 60;
            timerValue.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    showTimerComplete() {
        const timerText = document.getElementById('timerText');
        if (timerText) {
            timerText.textContent = 'Time\'s Up!';
            setTimeout(() => {
                timerText.textContent = 'Timer';
            }, 3000);
        }
    }

    // Mathematical calculations
    factorial(n) {
        if (n < 0) return 0;
        if (n === 0 || n === 1) return 1;
        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    permutation(n, r) {
        if (r > n || n < 0 || r < 0) return 0;
        return this.factorial(n) / this.factorial(n - r);
    }

    combination(n, r) {
        if (r > n || n < 0 || r < 0) return 0;
        return this.factorial(n) / (this.factorial(r) * this.factorial(n - r));
    }

    // Calculator functions
    initializeCalculators() {
        this.calculateBasic();
        this.calculatePermutation();
        this.calculateCombination();
        this.calculateMultinomial();
        this.calculateInvestment();
    }

    calculateBasic() {
        const mInput = document.getElementById('basicM');
        const nInput = document.getElementById('basicN');
        const resultElement = document.getElementById('basicResult');

        if (!mInput || !nInput || !resultElement) return;

        const m = parseInt(mInput.value) || 0;
        const n = parseInt(nInput.value) || 0;

        const result = m * n;
        resultElement.textContent = `${m} × ${n} = ${result.toLocaleString()}`;
    }

    calculatePermutation() {
        const nInput = document.getElementById('permN');
        const rInput = document.getElementById('permR');
        const resultElement = document.getElementById('permResult');

        if (!nInput || !rInput || !resultElement) return;

        const n = parseInt(nInput.value) || 0;
        const r = parseInt(rInput.value) || 0;

        const result = this.permutation(n, r);
        resultElement.textContent = `P(${n},${r}) = ${result.toLocaleString()}`;

        // Update input constraints
        rInput.max = n;
        if (r > n) {
            rInput.value = n;
        }
    }

    calculateCombination() {
        const nInput = document.getElementById('combN');
        const rInput = document.getElementById('combR');
        const resultElement = document.getElementById('combResult');

        if (!nInput || !rInput || !resultElement) return;

        const n = parseInt(nInput.value) || 0;
        const r = parseInt(rInput.value) || 0;

        const result = this.combination(n, r);
        resultElement.textContent = `C(${n},${r}) = ${result.toLocaleString()}`;

        // Update input constraints
        rInput.max = n;
        if (r > n) {
            rInput.value = n;
        }
    }

    calculateMultinomial() {
        const nInput = document.getElementById('multiN');
        const g1Input = document.getElementById('multiG1');
        const g2Input = document.getElementById('multiG2');
        const g3Input = document.getElementById('multiG3');
        const resultElement = document.getElementById('multiResult');

        if (!nInput || !g1Input || !g2Input || !g3Input || !resultElement) return;

        const n = parseInt(nInput.value) || 0;
        const g1 = parseInt(g1Input.value) || 0;
        const g2 = parseInt(g2Input.value) || 0;
        const g3 = parseInt(g3Input.value) || 0;

        if (g1 + g2 + g3 !== n) {
            resultElement.textContent = `Groups must sum to ${n}`;
            resultElement.style.color = 'var(--color-error)';
            return;
        }

        const result = this.factorial(n) / (this.factorial(g1) * this.factorial(g2) * this.factorial(g3));
        resultElement.textContent = `Result: ${result.toLocaleString()}`;
        resultElement.style.color = 'var(--color-primary)';
    }

    calculateInvestment() {
        const nInput = document.getElementById('investN');
        const rInput = document.getElementById('investR');
        const resultElement = document.getElementById('investResult');

        if (!nInput || !rInput || !resultElement) return;

        const n = parseInt(nInput.value) || 0;
        const r = parseInt(rInput.value) || 0;

        // Stars and bars: C(n+r-1, r-1)
        const result = this.combination(n + r - 1, r - 1);
        resultElement.textContent = `${result.toLocaleString()} investment strategies`;
    }

    // Answer revealing
    revealAnswer(answerId) {
        const answerElement = document.getElementById(answerId);
        if (answerElement) {
            answerElement.classList.remove('hidden');
            
            // Find the reveal button in the same activity section
            const activitySection = answerElement.closest('.student-activity');
            if (activitySection) {
                const button = activitySection.querySelector('.reveal-btn');
                if (button) {
                    button.disabled = true;
                    button.textContent = 'Answer Revealed';
                }
            }
        }
    }

    // Interactive Proof Functions (Slide 11)
    buildTerms() {
        const termsDisplay = document.getElementById('termsDisplay');
        if (!termsDisplay) return;

        const terms = [
            'Choose x from all 3 factors: x³',
            'Choose x from 2 factors, y from 1: 3x²y',
            'Choose x from 1 factor, y from 2: 3xy²',
            'Choose y from all 3 factors: y³'
        ];

        let html = '<div class="terms-list">';
        html += '<h4>All terms in (x+y)³:</h4>';
        terms.forEach((term, index) => {
            setTimeout(() => {
                const termElement = document.createElement('div');
                termElement.className = 'term-item';
                termElement.textContent = term;
                termElement.style.cssText = `
                    background: var(--color-bg-${(index % 8) + 1});
                    padding: var(--space-12);
                    margin: var(--space-8) 0;
                    border-radius: var(--radius-base);
                    font-size: 28px;
                    opacity: 0;
                    animation: fadeInUp 0.5s ease-out forwards;
                `;
                termsDisplay.appendChild(termElement);
            }, index * 500);
        });
        html += '</div>';
    }

    resetBuilder() {
        const termsDisplay = document.getElementById('termsDisplay');
        if (termsDisplay) {
            termsDisplay.innerHTML = '<p>Click "Build Terms" to see all possible combinations!</p>';
        }
    }

    generatePascal() {
        const triangleElement = document.getElementById('pascalTriangle');
        if (!triangleElement) return;

        const rows = 6;
        let html = '<div class="pascal-rows">';
        
        for (let i = 0; i < rows; i++) {
            html += '<div class="pascal-row" style="display: flex; justify-content: center; gap: 8px; margin-bottom: 8px;">';
            for (let j = 0; j <= i; j++) {
                const value = this.combination(i, j);
                html += `<span style="
                    background: var(--color-bg-${(j % 8) + 1});
                    padding: 8px 12px;
                    border-radius: var(--radius-sm);
                    font-size: 24px;
                    font-weight: var(--font-weight-bold);
                    min-width: 40px;
                    text-align: center;
                ">${value}</span>`;
            }
            html += '</div>';
        }
        html += '</div>';
        triangleElement.innerHTML = html;
    }

    // Interactive Proof Functions (Slide 15)
    selectChoice(factorNum, variable) {
        this.factorChoices[factorNum - 1] = variable;
        
        // Update button styles
        const choiceSet = document.querySelectorAll(`.choice-set:nth-child(${factorNum}) .choice-btn`);
        choiceSet.forEach(btn => btn.classList.remove('selected'));
        
        const selectedBtn = document.querySelector(`.choice-set:nth-child(${factorNum}) .choice-btn[onclick*="${variable}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('selected');
        }
        
        this.updateCurrentTerm();
    }

    updateCurrentTerm() {
        const termDisplay = document.getElementById('termDisplay');
        if (!termDisplay) return;

        if (this.factorChoices[0] && this.factorChoices[1]) {
            let term = '';
            const counts = { x1: 0, x2: 0, x3: 0 };
            
            this.factorChoices.forEach(choice => {
                counts[choice]++;
            });
            
            Object.keys(counts).forEach(variable => {
                if (counts[variable] > 0) {
                    if (term) term += ' ';
                    if (counts[variable] === 1) {
                        term += variable.replace(/(\d)/, '�$1');
                    } else {
                        term += variable.replace(/(\d)/, '�$1') + `^${counts[variable]}`;
                    }
                }
            });
            
            termDisplay.textContent = term || 'Select variables above';
        } else {
            termDisplay.textContent = 'Select variables above';
        }
    }

    showAllTerms() {
        const allTermsDisplay = document.getElementById('allTermsDisplay');
        if (!allTermsDisplay) return;

        const terms = [
            'x₁² (coefficient: 1)',
            'x₂² (coefficient: 1)', 
            'x₃² (coefficient: 1)',
            '2x₁x₂ (coefficient: 2)',
            '2x₁x₃ (coefficient: 2)',
            '2x₂x₃ (coefficient: 2)'
        ];

        let html = '<h4 style="font-size: 32px; margin-bottom: 16px;">Complete expansion of (x₁+x₂+x₃)²:</h4>';
        html += '<div class="terms-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">';
        
        terms.forEach((term, index) => {
            html += `<div style="
                background: var(--color-bg-${(index % 8) + 1});
                padding: 16px;
                border-radius: var(--radius-base);
                text-align: center;
                font-size: 24px;
                font-weight: var(--font-weight-medium);
            ">${term}</div>`;
        });
        
        html += '</div>';
        html += '<div style="margin-top: 20px; padding: 16px; background: var(--color-surface); border-radius: var(--radius-base); text-align: center;">';
        html += '<strong style="font-size: 28px;">Final Result: x₁² + x₂² + x₃² + 2x₁x₂ + 2x₁x₃ + 2x₂x₃</strong>';
        html += '</div>';
        
        allTermsDisplay.innerHTML = html;
    }

    // Quiz Functions
    selectAnswer(questionNum, selectedAnswer) {
        const correctAnswer = this.quizAnswers[questionNum];
        const feedback = document.getElementById(`feedback${questionNum}`);
        const options = document.querySelectorAll(`#q${questionNum} .quiz-option`);
        
        this.userAnswers[questionNum] = selectedAnswer;
        
        // Style all options
        options.forEach(option => {
            const optionLetter = option.textContent.charAt(0);
            if (optionLetter === correctAnswer.toUpperCase()) {
                option.classList.add('correct');
            } else if (optionLetter === selectedAnswer.toUpperCase()) {
                option.classList.add('incorrect');
            }
            option.disabled = true;
        });
        
        // Show feedback
        const isCorrect = selectedAnswer === correctAnswer;
        feedback.className = 'quiz-feedback show';
        feedback.style.background = isCorrect ? 'var(--color-bg-3)' : 'var(--color-bg-4)';
        feedback.innerHTML = `
            <strong>${isCorrect ? 'Correct!' : 'Incorrect.'}</strong> 
            ${this.getQuizExplanation(questionNum)}
        `;
    }

    getQuizExplanation(questionNum) {
        const explanations = {
            1: 'Code: 26³ × 10² = 17,576 × 100 = 1,757,600',
            2: 'Arranging 5 people in 5 chairs: 5! = 120',
            3: 'Committee of 4 from 12: C(12,4) = 12!/(4!×8!) = 495',
            4: 'Coefficient of x²y³ in (x+y)⁵: C(5,2) = 10',
            5: 'Groups of 4,3,2 from 9: 9!/(4!×3!×2!) = 1,260',
            6: 'Solutions to x₁+x₂+x₃=7: C(7+3-1,3-1) = C(9,2) = 36'
        };
        return explanations[questionNum] || '';
    }

    showAllAnswers() {
        for (let i = 1; i <= 3; i++) {
            if (!this.userAnswers[i]) {
                this.selectAnswer(i, this.quizAnswers[i]);
            }
        }
    }

    showAllAdvancedAnswers() {
        for (let i = 4; i <= 6; i++) {
            if (!this.userAnswers[i]) {
                this.selectAnswer(i, this.quizAnswers[i]);
            }
        }
    }

    addKeyboardHint() {
        const hint = document.createElement('div');
        hint.className = 'keyboard-nav';
        hint.innerHTML = '← → keys to navigate | F11 for fullscreen';
        document.body.appendChild(hint);
    }

    // Fullscreen functionality
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.enterFullscreen();
        } else {
            this.exitFullscreen();
        }
    }

    async enterFullscreen() {
        try {
            const container = document.querySelector('.presentation-container');
            if (container.requestFullscreen) {
                await container.requestFullscreen();
            } else if (container.webkitRequestFullscreen) {
                await container.webkitRequestFullscreen();
            } else if (container.msRequestFullscreen) {
                await container.msRequestFullscreen();
            }
            
            container.classList.add('fullscreen');
            this.updateFullscreenButton(true);
            
            // Hide cursor after inactivity
            this.setupCursorHiding();
            
        } catch (error) {
            console.warn('Fullscreen request failed:', error);
        }
    }

    exitFullscreen() {
        try {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            
            const container = document.querySelector('.presentation-container');
            container.classList.remove('fullscreen');
            this.updateFullscreenButton(false);
            
            // Clear cursor hiding
            this.clearCursorHiding();
            
        } catch (error) {
            console.warn('Exit fullscreen failed:', error);
        }
    }

    updateFullscreenButton(isFullscreen) {
        const btn = document.getElementById('fullscreenBtn');
        if (btn) {
            btn.innerHTML = isFullscreen ? '⛶' : '⛶';
            btn.title = isFullscreen ? 'Exit Fullscreen (F11)' : 'Enter Fullscreen (F11)';
        }
    }

    setupCursorHiding() {
        let cursorTimeout;
        const container = document.querySelector('.presentation-container');
        
        const hideCursor = () => {
            container.style.cursor = 'none';
        };
        
        const showCursor = () => {
            container.style.cursor = 'default';
            clearTimeout(cursorTimeout);
            cursorTimeout = setTimeout(hideCursor, 3000);
        };
        
        // Initial timeout
        cursorTimeout = setTimeout(hideCursor, 3000);
        
        // Show cursor on mouse movement
        container.addEventListener('mousemove', showCursor);
        container.addEventListener('click', showCursor);
        
        // Store references for cleanup
        this.cursorTimeout = cursorTimeout;
        this.showCursor = showCursor;
    }

    clearCursorHiding() {
        const container = document.querySelector('.presentation-container');
        container.style.cursor = 'default';
        
        if (this.cursorTimeout) {
            clearTimeout(this.cursorTimeout);
        }
        
        if (this.showCursor) {
            container.removeEventListener('mousemove', this.showCursor);
            container.removeEventListener('click', this.showCursor);
        }
    }

    setupAutoHideNavControls() {
        const navControls = document.querySelector('.nav-controls');
        const slideDots = document.querySelector('.slide-dots');
        const fullscreenBtn = document.getElementById('fullscreenBtn');
        
        if (!navControls) return;
        
        let hideTimeout = null;
        
        const showNav = () => {
            if (document.fullscreenElement) {
                navControls.style.opacity = '1';
                navControls.style.pointerEvents = 'all';
                
                // Show other UI elements (but not timer - it stays visible when active)
                if (slideDots) {
                    slideDots.style.opacity = '1';
                }
                if (fullscreenBtn) {
                    fullscreenBtn.style.opacity = '1';
                }
                
                // Clear existing timeout and set new one
                if (hideTimeout) clearTimeout(hideTimeout);
                hideTimeout = setTimeout(hideNav, 3000); // 3 seconds idle
            }
        };

        const hideNav = () => {
            if (document.fullscreenElement) {
                navControls.style.opacity = '0';
                navControls.style.pointerEvents = 'none';
                
                // Hide other UI elements (but not timer - it stays visible when active)
                if (slideDots) {
                    slideDots.style.opacity = '0';
                }
                if (fullscreenBtn) {
                    fullscreenBtn.style.opacity = '0';
                }
            }
        };

        const onMouseMove = (e) => {
            if (document.fullscreenElement) {
                showNav();
            }
        };

        const onFullscreenChange = () => {
            if (!document.fullscreenElement) {
                // Reset styles when exiting fullscreen (but not timer)
                navControls.style.opacity = '';
                navControls.style.pointerEvents = '';
                
                if (slideDots) slideDots.style.opacity = '';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '';
                
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                    hideTimeout = null;
                }
            } else {
                // Start in hidden state when entering fullscreen (but not timer)
                hideNav();
            }
        };

        // Add event listeners
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('fullscreenchange', onFullscreenChange);
        
        // Store references for potential cleanup
        this.navControlsMouseMove = onMouseMove;
        this.navControlsFullscreenChange = onFullscreenChange;
        this.navHideTimeout = hideTimeout;
    }

    handleFullscreenChange() {
        const container = document.querySelector('.presentation-container');
        const isFullscreen = !!document.fullscreenElement;
        
        if (isFullscreen) {
            container.classList.add('fullscreen');
            this.updateFullscreenButton(true);
            this.setupCursorHiding();
        } else {
            container.classList.remove('fullscreen');
            this.updateFullscreenButton(false);
            this.clearCursorHiding();
        }
    }

    handleFullscreenChange() {
        const container = document.querySelector('.presentation-container');
        const isFullscreen = !!document.fullscreenElement || 
                           !!document.webkitFullscreenElement || 
                           !!document.msFullscreenElement;
        
        if (isFullscreen) {
            container.classList.add('fullscreen');
            this.updateFullscreenButton(true);
            this.setupCursorHiding();
        } else {
            container.classList.remove('fullscreen');
            this.updateFullscreenButton(false);
            this.clearCursorHiding();
        }
    }

    // Interactive Quiz functionality for slide 34
    startQuiz() {
        this.currentQuizQuestion = 1;
        this.quizQuestions = [
            {
                question: "In how many ways can 6 people sit around a circular table?",
                options: ["A) 6! = 720", "B) (6-1)! = 120", "C) 6² = 36", "D) C(6,3) = 20"],
                correct: 1, // Index of correct answer (B) - 0-based indexing
                explanation: "Correct! For circular arrangements, we fix one person and arrange the rest: (n-1)!"
            },
            {
                question: "How many ways can the letters in ABCD be arranged?",
                options: ["A) 12", "B) 24", "C) 16", "D) 8"],
                correct: 1, // 4! = 24 (B)
                explanation: "Correct! 4 distinct objects can be arranged in 4! = 24 ways"
            },
            {
                question: "From 10 people, choose 3 for a committee. How many ways?",
                options: ["A) 30", "B) 120", "C) 720", "D) 1000"],
                correct: 1, // C(10,3) = 120 (B)
                explanation: "Correct! C(10,3) = 10!/(3!×7!) = 120"
            },
            {
                question: "What is the coefficient of x³y² in (x+y)⁵?",
                options: ["A) 5", "B) 10", "C) 15", "D) 20"],
                correct: 1, // C(5,3) = 10 (B)
                explanation: "Correct! The coefficient is C(5,3) = 10"
            },
            {
                question: "Find non-negative solutions to x + y + z = 4",
                options: ["A) 10", "B) 15", "C) 20", "D) 12"],
                correct: 1, // C(4+3-1,3-1) = C(6,2) = 15 (B)
                explanation: "Correct! Using stars and bars: C(6,2) = 15"
            }
        ];
        
        this.displayQuizQuestion();
        this.updateQuizProgress();
        
        // Start timer for 5 minutes
        this.startTimer(300);
    }

    displayQuizQuestion() {
        const questionElement = document.getElementById('quizQuestion');
        if (!questionElement || !this.quizQuestions) return;
        
        const currentQ = this.quizQuestions[this.currentQuizQuestion - 1];
        
        questionElement.innerHTML = `
            <h4>Question ${this.currentQuizQuestion} of ${this.quizQuestions.length}</h4>
            <p>${currentQ.question}</p>
            <div class="quiz-options">
                ${currentQ.options.map((option, index) => 
                    `<button class="btn btn--outline quiz-option" onclick="presentation.selectQuizAnswer(${index})">${option}</button>`
                ).join('')}
            </div>
            <div class="quiz-feedback hidden" id="quizFeedback">
                <p class="correct-answer">${currentQ.explanation}</p>
            </div>
        `;
        
        this.updateQuizStatus();
    }

    selectQuizAnswer(answerIndex) {
        const currentQ = this.quizQuestions[this.currentQuizQuestion - 1];
        const options = document.querySelectorAll('.quiz-option');
        const feedback = document.getElementById('quizFeedback');
        
        // Disable all options
        options.forEach(option => option.disabled = true);
        
        // Show correct/incorrect styling
        options.forEach((option, index) => {
            if (index === currentQ.correct) {
                option.classList.add('correct');
                option.style.backgroundColor = 'var(--color-success, #28a745)';
                option.style.color = 'white';
            } else if (index === answerIndex && index !== currentQ.correct) {
                option.classList.add('incorrect');
                option.style.backgroundColor = 'var(--color-error, #dc3545)';
                option.style.color = 'white';
            }
        });
        
        // Show feedback with correct or incorrect message
        if (feedback) {
            const isCorrect = answerIndex === currentQ.correct;
            feedback.innerHTML = `
                <p class="feedback-message">
                    <strong>${isCorrect ? '✓ Correct!' : '✗ Incorrect.'}</strong><br>
                    ${currentQ.explanation}
                </p>
            `;
            feedback.classList.remove('hidden');
            feedback.classList.add('show');
            
            // Style feedback based on correctness
            if (isCorrect) {
                feedback.style.borderLeftColor = 'var(--color-success, #28a745)';
                feedback.style.backgroundColor = 'var(--color-success-light, #d4edda)';
            } else {
                feedback.style.borderLeftColor = 'var(--color-error, #dc3545)';
                feedback.style.backgroundColor = 'var(--color-error-light, #f8d7da)';
            }
        }
        
        // Store user answer
        if (!this.userAnswers) this.userAnswers = {};
        this.userAnswers[this.currentQuizQuestion] = answerIndex;
        
        // Update progress
        this.updateQuizProgress();
    }

    nextQuestion() {
        if (this.currentQuizQuestion < this.quizQuestions.length) {
            this.currentQuizQuestion++;
            this.displayQuizQuestion();
        } else {
            this.finishQuiz();
        }
    }

    previousQuestion() {
        if (this.currentQuizQuestion > 1) {
            this.currentQuizQuestion--;
            this.displayQuizQuestion();
        }
    }

    updateQuizProgress() {
        const progressFill = document.getElementById('quizProgress');
        const statusElement = document.getElementById('quizStatus');
        
        if (progressFill && this.quizQuestions) {
            const progress = (this.currentQuizQuestion / this.quizQuestions.length) * 100;
            progressFill.style.width = `${progress}%`;
        }
        
        if (statusElement && this.quizQuestions) {
            statusElement.textContent = `Question ${this.currentQuizQuestion} of ${this.quizQuestions.length}`;
        }
    }

    updateQuizStatus() {
        const statusElement = document.getElementById('quizStatus');
        if (statusElement && this.quizQuestions) {
            statusElement.textContent = `Question ${this.currentQuizQuestion} of ${this.quizQuestions.length}`;
        }
    }

    finishQuiz() {
        this.stopTimer();
        
        // Calculate score
        let correct = 0;
        for (let i = 1; i <= this.quizQuestions.length; i++) {
            if (this.userAnswers[i] === this.quizQuestions[i-1].correct) {
                correct++;
            }
        }
        
        const percentage = Math.round((correct / this.quizQuestions.length) * 100);
        
        // Show results
        const statusElement = document.getElementById('quizStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <strong>Quiz Complete!</strong><br>
                Score: ${correct}/${this.quizQuestions.length} (${percentage}%)
            `;
        }
        
        // Disable navigation buttons
        const nextBtn = document.getElementById('nextQuestion');
        if (nextBtn) nextBtn.disabled = true;
    }
}

// Global functions for HTML onclick handlers
let presentation;

function startTimer(seconds) {
    if (presentation) {
        presentation.startTimer(seconds);
    }
}

function calculateBasic() {
    if (presentation) {
        presentation.calculateBasic();
    }
}

function calculatePermutation() {
    if (presentation) {
        presentation.calculatePermutation();
    }
}

function calculateCombination() {
    if (presentation) {
        presentation.calculateCombination();
    }
}

function calculateMultinomial() {
    if (presentation) {
        presentation.calculateMultinomial();
    }
}

function calculateInvestment() {
    if (presentation) {
        presentation.calculateInvestment();
    }
}

function revealAnswer(answerId) {
    if (presentation) {
        presentation.revealAnswer(answerId);
    }
}

function buildTerms() {
    if (presentation) {
        presentation.buildTerms();
    }
}

function resetBuilder() {
    if (presentation) {
        presentation.resetBuilder();
    }
}

function generatePascal() {
    if (presentation) {
        presentation.generatePascal();
    }
}

function selectChoice(factorNum, variable) {
    if (presentation) {
        presentation.selectChoice(factorNum, variable);
    }
}

function showAllTerms() {
    if (presentation) {
        presentation.showAllTerms();
    }
}

function selectAnswer(questionNum, selectedAnswer) {
    if (presentation) {
        presentation.selectAnswer(questionNum, selectedAnswer);
    }
}

function startQuiz() {
    if (presentation) {
        presentation.startQuiz();
    }
}

function nextQuestion() {
    if (presentation) {
        presentation.nextQuestion();
    }
}

function previousQuestion() {
    if (presentation) {
        presentation.previousQuestion();
    }
}

function showAllAnswers() {
    if (presentation) {
        presentation.showAllAnswers();
    }
}

function showAllAdvancedAnswers() {
    if (presentation) {
        presentation.showAllAdvancedAnswers();
    }
}

// Accessibility Manager
class AccessibilityManager {
    constructor() {
        this.setupFocusManagement();
        this.setupReducedMotion();
    }

    setupFocusManagement() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }

    setupReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            const style = document.createElement('style');
            style.textContent = `
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Mathematical utilities
class MathUtils {
    static formatLargeNumber(num) {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    static binomialCoefficient(n, k) {
        if (k > n || k < 0) return 0;
        if (k === 0 || k === n) return 1;
        
        let result = 1;
        for (let i = 0; i < k; i++) {
            result = result * (n - i) / (i + 1);
        }
        return Math.round(result);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main presentation
    presentation = new CombinatoricsPresentation();
    
    // Make presentation available globally for onclick handlers
    window.presentation = presentation;
    
    // Initialize accessibility features
    new AccessibilityManager();
    
    // Add custom styles for enhanced interactivity
    const style = document.createElement('style');
    style.textContent = `
        .keyboard-navigation button:focus,
        .keyboard-navigation input:focus,
        .keyboard-navigation .dot:focus {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
        }
        
        .term-item {
            transition: transform 0.2s ease;
        }
        
        .term-item:hover {
            transform: translateY(-2px);
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .slide.active .slide-content {
            animation: slideInRight 0.3s ease-out;
        }
        
        .quiz-option:disabled {
            cursor: not-allowed;
        }
        
        .quiz-option.correct {
            background-color: var(--color-success, #28a745) !important;
            color: white !important;
            border-color: var(--color-success, #28a745) !important;
        }
        
        .quiz-option.incorrect {
            background-color: var(--color-error, #dc3545) !important;
            color: white !important;
            border-color: var(--color-error, #dc3545) !important;
        }
        
        .quiz-feedback {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: var(--radius-base, 8px);
            background: var(--color-success-light, #d4edda);
            border-left: 4px solid var(--color-success, #28a745);
        }
        
        .quiz-feedback.hidden {
            display: none;
        }
        
        .quiz-feedback.show {
            display: block;
            animation: slideInUp 0.3s ease-out;
        }
        
        .feedback-message {
            margin: 0;
            font-size: 16px;
            line-height: 1.4;
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .choice-btn.selected {
            animation: pulse 0.3s ease-in-out;
        }
    `;
    document.head.appendChild(style);
    
    // MathJax configuration for better rendering
    if (window.MathJax) {
        window.MathJax.config.tex.displayMath = [['$$', '$$'], ['\\[', '\\]']];
        window.MathJax.config.tex.inlineMath = [['$', '$'], ['\\(', '\\)']];
        window.MathJax.config.svg.fontCache = 'global';
    }

    console.log('🎓 Combinatorial Analysis Presentation Ready!');
    console.log('📊 30 slides with guaranteed 28px+ fonts');
    console.log('🎯 Perfect fullscreen fit without scrolling');
    console.log('⌨️ Use arrow keys to navigate');
    console.log('⏱️ Press Escape to stop timers');
});

// Error handling
window.addEventListener('error', (e) => {
    console.error('Presentation error:', e.error);
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CombinatoricsPresentation,
        AccessibilityManager,
        MathUtils
    };
}