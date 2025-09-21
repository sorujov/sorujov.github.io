/* Statistics Presentation - Interactive Slides JavaScript */

class StatisticsPresentation {
    constructor() {
        this.currentSlide = 1;
        this.slides = []; // Array to store slide elements in order
        this.totalSlides = 0;
        this.timerInterval = null;
        this.timerSeconds = 0;
        
        // Quiz answers (correct answers for each question)
        this.quizAnswers = {
            1: 'b', // Descriptive statistics
            2: 'c', // Cluster sampling
            3: 'd'  // Stratification (not a principle)
        };
        this.userAnswers = {};
        
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
        console.log(`${this.totalSlides}-slide Statistics Presentation loaded!`);
    }

    // Discover all slide elements in the order they appear in the DOM
    discoverSlides() {
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
        document.addEventListener('mozfullscreenchange', () => this.handleFullscreenChange());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // Calculator inputs
        this.setupCalculatorListeners();
    }

    setupCalculatorListeners() {
        // Population/Sample calculator
        ['popSize', 'sampleSize'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateSamplePercent());
            }
        });
        
        // Stratified sampling calculator
        ['stratTotal', 'strat1', 'strat2', 'strat3'].forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.calculateStratified());
            }
        });
    }

    setupSlideDots() {
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => this.goToSlide(index + 1));
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
        if (slideNumber < 1 || slideNumber > this.totalSlides) return;

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
        if (window.MathJax) {
            window.MathJax.typesetPromise ? 
                window.MathJax.typesetPromise([newSlideElement]).catch(err => console.warn('MathJax rendering error:', err)) :
                window.MathJax.Hub?.Queue(['Typeset', window.MathJax.Hub, newSlideElement]);
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
        
        if (prevBtn) prevBtn.disabled = this.currentSlide === 1;
        if (nextBtn) nextBtn.disabled = this.currentSlide === this.totalSlides;
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
        if (timerDisplay) timerDisplay.classList.remove('active');
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
                timerText.textContent = 'Timer:';
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

    // Calculator functions
    initializeCalculators() {
        this.calculateSamplePercent();
        this.calculateStratified();
    }

    calculateSamplePercent() {
        const popInput = document.getElementById('popSize');
        const sampleInput = document.getElementById('sampleSize');
        const resultElement = document.getElementById('samplePercent');
        
        if (!popInput || !sampleInput || !resultElement) return;
        
        const pop = parseInt(popInput.value) || 0;
        const sample = parseInt(sampleInput.value) || 0;
        
        if (pop === 0) {
            resultElement.textContent = 'Enter population size';
            return;
        }
        
        const percent = (sample / pop * 100).toFixed(1);
        resultElement.textContent = `Sample represents ${percent}% of population`;
    }

    calculateStratified() {
        const totalInput = document.getElementById('stratTotal');
        const strat1Input = document.getElementById('strat1');
        const strat2Input = document.getElementById('strat2');
        const strat3Input = document.getElementById('strat3');
        const resultElement = document.getElementById('stratResult');
        
        if (!totalInput || !strat1Input || !strat2Input || !strat3Input || !resultElement) return;
        
        const total = parseInt(totalInput.value) || 0;
        const strat1 = parseInt(strat1Input.value) || 0;
        const strat2 = parseInt(strat2Input.value) || 0;
        const strat3 = parseInt(strat3Input.value) || 0;
        
        const population = strat1 + strat2 + strat3;
        
        if (population === 0) {
            resultElement.textContent = 'Enter stratum sizes';
            return;
        }
        
        const sample1 = Math.round(total * strat1 / population);
        const sample2 = Math.round(total * strat2 / population);
        const sample3 = Math.round(total * strat3 / population);
        
        resultElement.innerHTML = `
            Stratum 1: ${sample1} samples<br>
            Stratum 2: ${sample2} samples<br>
            Stratum 3: ${sample3} samples<br>
            Total: ${sample1 + sample2 + sample3} samples
        `;
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

    // Random sample generator
    generateRandomSample() {
        const nInput = document.getElementById('randomN');
        const sampleInput = document.getElementById('randomn');
        const resultElement = document.getElementById('randomResult');
        
        if (!nInput || !sampleInput || !resultElement) return;
        
        const N = parseInt(nInput.value) || 0;
        const n = parseInt(sampleInput.value) || 0;
        
        if (N <= 0 || n <= 0 || n > N) {
            resultElement.textContent = 'Invalid input values';
            return;
        }
        
        // Generate random sample without replacement
        const population = Array.from({length: N}, (_, i) => i + 1);
        const sample = [];
        
        for (let i = 0; i < n; i++) {
            const randomIndex = Math.floor(Math.random() * population.length);
            sample.push(population.splice(randomIndex, 1)[0]);
        }
        
        sample.sort((a, b) => a - b);
        resultElement.textContent = `Selected numbers: ${sample.join(', ')}`;
    }

    // Quiz Functions
    selectQuizAnswer(questionNum, selectedAnswer) {
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
        feedback.innerHTML = `<strong>${isCorrect ? 'Correct!' : 'Incorrect.'}</strong> ${this.getQuizExplanation(questionNum)}`;
    }

    getQuizExplanation(questionNum) {
        const explanations = {
            1: 'The researcher is summarizing data from the sample (65% study >2 hours), which is descriptive statistics.',
            2: 'The pollster selects entire neighborhoods (clusters) and surveys all voters in those clusters.',
            3: 'The three basic principles are control, randomization, and replication. Stratification is a sampling technique.'
        };
        return explanations[questionNum];
    }

    showAllQuizAnswers() {
        for (let i = 1; i <= 3; i++) {
            if (!this.userAnswers[i]) {
                this.selectQuizAnswer(i, this.quizAnswers[i]);
            }
        }
    }

    // Drag and drop matching exercise
    checkMatching() {
        const feedback = document.getElementById('matchingFeedback');
        const dropZones = document.querySelectorAll('.drop-zone');
        let correct = 0;
        let total = 4;
        
        dropZones.forEach(zone => {
            const expectedType = zone.getAttribute('data-accepts');
            const droppedCard = zone.querySelector('.scenario-card');
            
            if (droppedCard && droppedCard.getAttribute('data-type') === expectedType) {
                zone.style.backgroundColor = 'var(--color-success, #28a745)';
                zone.style.color = 'white';
                correct++;
            } else {
                zone.style.backgroundColor = 'var(--color-error, #dc3545)';
                zone.style.color = 'white';
            }
        });
        
        feedback.innerHTML = `<strong>${correct}/${total} correct!</strong><br>`;
        if (correct === total) {
            feedback.innerHTML += 'Excellent! You understand the different types of statistical studies.';
        } else {
            feedback.innerHTML += 'Review the definitions and try again.';
        }
        feedback.style.display = 'block';
    }

    addKeyboardHint() {
        const hint = document.createElement('div');
        hint.className = 'keyboard-nav';
        hint.innerHTML = '← → Navigate • F11 Fullscreen • ESC Exit';
        document.body.appendChild(hint);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            hint.style.opacity = '0.3';
        }, 10000);
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
            } else if (container.mozRequestFullScreen) {
                await container.mozRequestFullScreen();
            }
            
            container.classList.add('fullscreen');
            this.updateFullscreenButton(true);
            
            // Hide cursor after inactivity
            this.setupCursorHiding();
        } catch (error) {
            console.warn('Fullscreen request failed:', error);
            // Fallback: manually apply fullscreen styles
            const container = document.querySelector('.presentation-container');
            container.classList.add('fullscreen');
            this.updateFullscreenButton(true);
            this.setupCursorHiding();
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
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            }
            
            const container = document.querySelector('.presentation-container');
            container.classList.remove('fullscreen');
            this.updateFullscreenButton(false);
            
            // Clear cursor hiding
            this.clearCursorHiding();
        } catch (error) {
            console.warn('Exit fullscreen failed:', error);
            // Fallback: manually remove fullscreen styles
            const container = document.querySelector('.presentation-container');
            container.classList.remove('fullscreen');
            this.updateFullscreenButton(false);
            this.clearCursorHiding();
        }
    }

    updateFullscreenButton(isFullscreen) {
        const btn = document.getElementById('fullscreenBtn');
        if (btn) {
            btn.innerHTML = isFullscreen ? '⛶' : '⛶';
            btn.title = isFullscreen ? 'Exit Fullscreen (ESC or F11)' : 'Enter Fullscreen (F11)';
        }
    }

    setupCursorHiding() {
        let cursorTimeout;
        const container = document.querySelector('.presentation-container');
        
        const hideCursor = () => {
            container.classList.add('hide-cursor');
        };
        
        const showCursor = () => {
            container.classList.remove('hide-cursor');
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
        container.classList.remove('hide-cursor');
        
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
        let isMouseNearTop = false;
        
        const showNav = () => {
            if (document.fullscreenElement) {
                navControls.style.opacity = '1';
                navControls.style.pointerEvents = 'all';
                
                // Show other UI elements (but not timer - it stays visible when active)
                if (slideDots) slideDots.style.opacity = '1';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '1';
                
                // Clear existing timeout and set new one
                if (hideTimeout) clearTimeout(hideTimeout);
                hideTimeout = setTimeout(hideNav, isMouseNearTop ? 5000 : 3000); // Longer delay if mouse near top
            }
        };
        
        const hideNav = () => {
            if (document.fullscreenElement && !isMouseNearTop) {
                navControls.style.opacity = '0';
                navControls.style.pointerEvents = 'none';
                
                // Hide other UI elements (but not timer - it stays visible when active)
                if (slideDots) slideDots.style.opacity = '0';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '0';
            }
        };
        
        const onMouseMove = (e) => {
            if (document.fullscreenElement) {
                // Check if mouse is in top area (first 100px)
                isMouseNearTop = e.clientY < 100;
                showNav();
            }
        };
        
        const onKeyDown = (e) => {
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
                isMouseNearTop = false;
            } else {
                // Start with nav visible when entering fullscreen
                showNav();
            }
        };
        
        // Add event listeners
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('keydown', onKeyDown);
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('msfullscreenchange', onFullscreenChange);
        document.addEventListener('mozfullscreenchange', onFullscreenChange);
        
        // Store references for potential cleanup
        this.navControlsMouseMove = onMouseMove;
        this.navControlsKeyDown = onKeyDown;
        this.navControlsFullscreenChange = onFullscreenChange;
        this.navHideTimeout = hideTimeout;
    }

    handleFullscreenChange() {
        const container = document.querySelector('.presentation-container');
        const isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement || document.mozFullScreenElement);
        
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
}

// Global functions for HTML onclick handlers
let presentation;

function startTimer(seconds) {
    if (presentation) presentation.startTimer(seconds);
}

function calculateSamplePercent() {
    if (presentation) presentation.calculateSamplePercent();
}

function calculateStratified() {
    if (presentation) presentation.calculateStratified();
}

function revealAnswer(answerId) {
    if (presentation) presentation.revealAnswer(answerId);
}

function generateRandomSample() {
    if (presentation) presentation.generateRandomSample();
}

function selectQuizAnswer(questionNum, selectedAnswer) {
    if (presentation) presentation.selectQuizAnswer(questionNum, selectedAnswer);
}

function showAllQuizAnswers() {
    if (presentation) presentation.showAllQuizAnswers();
}

function checkMatching() {
    if (presentation) presentation.checkMatching();
}

// Initialize drag and drop functionality
function initializeDragAndDrop() {
    const scenarios = document.querySelectorAll('.scenario-card');
    const dropZones = document.querySelectorAll('.drop-zone');

    scenarios.forEach(scenario => {
        scenario.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', scenario.getAttribute('data-type'));
            scenario.style.opacity = '0.5';
        });

        scenario.addEventListener('dragend', () => {
            scenario.style.opacity = '1';
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.backgroundColor = 'var(--color-bg-1)';
        });

        zone.addEventListener('dragleave', () => {
            zone.style.backgroundColor = '';
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            const cardType = e.dataTransfer.getData('text/plain');
            const expectedType = zone.getAttribute('data-accepts');
            
            // Remove any existing card
            const existingCard = zone.querySelector('.scenario-card');
            if (existingCard) {
                document.querySelector('.scenarios').appendChild(existingCard);
            }
            
            // Find and move the dragged card
            const draggedCard = document.querySelector(`[data-type="${cardType}"]`);
            if (draggedCard) {
                zone.appendChild(draggedCard);
            }
            
            zone.style.backgroundColor = '';
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main presentation
    presentation = new StatisticsPresentation();
    
    // Make presentation available globally for onclick handlers
    window.presentation = presentation;
    
    // Initialize drag and drop
    initializeDragAndDrop();
    
    console.log('Statistics Presentation Ready!');
    console.log('35 comprehensive slides covering The Nature of Statistics');
    console.log('Use arrow keys to navigate, F11 for fullscreen');
});

// Error handling
window.addEventListener('error', (e) => {
    console.error('Presentation error:', e.error);
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StatisticsPresentation };
}