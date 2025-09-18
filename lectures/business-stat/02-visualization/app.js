/* Organizing Data - Interactive Slides JavaScript */

class OrganizingDataPresentation {
    constructor() {
        this.currentSlide = 1;
        this.slides = [];
        this.totalSlides = 42;
        this.timerInterval = null;
        this.timerSeconds = 0;
        
        // Chart instances for cleanup
        this.chartInstances = {};
        
        // Sample data for demonstrations
        this.sampleData = {
            politicalParty: ['Democratic', 'Republican', 'Other', 'Democratic', 'Republican', 'Democratic', 'Other', 'Republican', 'Democratic', 'Republican'],
            tvData: [1, 1, 1, 2, 6, 3, 3, 4, 2, 4, 3, 2, 1, 5, 2, 1, 3, 6, 2, 2, 3, 1, 1, 4, 3, 2, 2, 2, 2, 3, 0, 3, 1, 2, 1, 2, 3, 1, 1, 3, 3, 2, 1, 2, 1, 1, 3, 1, 5, 1],
            daysToMaturity: [70, 64, 99, 55, 64, 89, 87, 65, 62, 38, 67, 70, 60, 69, 78, 39, 75, 56, 71, 51, 99, 68, 95, 86, 57, 53, 47, 50, 55, 81, 80, 98, 51, 36, 63, 66, 85, 79, 83, 70],
            dvdPrices: [210, 219, 214, 197, 224, 219, 199, 199, 208, 209, 215, 199, 212, 212, 219, 210],
            billionairesAge: [73, 57, 77, 82, 68, 77, 73, 84, 90, 64, 58, 65, 71, 65, 79, 63, 69, 93, 49, 40, 39, 56, 88, 85, 55],
            billionairesWealth: [73, 67, 57, 53.5, 43, 34, 34, 31, 30, 29, 28.2, 28, 27, 26.7, 26.5, 26.3, 26.1, 26, 25.2, 23, 22.8, 21.5, 20.4, 20.3, 20.3],
            citizenship: ['Mexico', 'United States', 'Spain', 'United States', 'United States', 'United States', 'United States', 'Hong Kong', 'France', 'France', 'United States', 'Sweden', 'United States', 'United States', 'United States', 'United States', 'United States', 'Germany', 'United States', 'United States', 'United States', 'India', 'Italy', 'Hong Kong', 'Canada']
        };
        
        this.init();
    }

    init() {
        this.discoverSlides();
        this.setupEventListeners();
        this.updateSlideCounter();
        this.updateNavigationButtons();
        this.setupSlideDots();
        this.addKeyboardHint();
        this.setupAutoHideNavControls();
        this.initializeCharts();
        console.log(`${this.totalSlides}-slide Organizing Data Presentation loaded!`);
    }

    discoverSlides() {
        this.slides = Array.from(document.querySelectorAll('.slide'));
        this.totalSlides = this.slides.length;
        console.log(`Discovered ${this.totalSlides} slides`);
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
        
        // Chart controls
        this.setupChartControls();
        
        // Classification exercise
        this.setupClassificationExercise();
    }

    setupChartControls() {
        // Pie chart controls
        const animatePieBtn = document.querySelector('[onclick="animatePieChart()"]');
        if (animatePieBtn) {
            animatePieBtn.onclick = () => this.animatePieChart();
        }
        
        // Bar chart controls
        const animateBarBtn = document.querySelector('[onclick="animateBarChart()"]');
        if (animateBarBtn) {
            animateBarBtn.onclick = () => this.animateBarChart();
        }
        
        // Histogram controls
        const buildHistogramBtn = document.querySelector('[onclick="buildHistogram()"]');
        if (buildHistogramBtn) {
            buildHistogramBtn.onclick = () => this.buildHistogram();
        }
        
        const binSlider = document.getElementById('binSlider');
        if (binSlider) {
            binSlider.addEventListener('input', () => this.updateBins());
        }
    }

    setupClassificationExercise() {
        const classifyBtns = document.querySelectorAll('.classify-btn');
        classifyBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const item = e.target.closest('.classification-item');
                const selectedType = e.target.getAttribute('data-type');
                const correctAnswer = item.getAttribute('data-answer');
                
                // Clear previous selections
                item.querySelectorAll('.classify-btn').forEach(b => {
                    b.classList.remove('correct', 'incorrect');
                });
                
                // Add appropriate class
                if (selectedType === correctAnswer) {
                    e.target.classList.add('correct');
                } else {
                    e.target.classList.add('incorrect');
                }
                
                // Show feedback
                this.showClassificationFeedback(item, selectedType, correctAnswer);
            });
        });
    }

    showClassificationFeedback(item, selected, correct) {
        const feedback = item.querySelector('.feedback');
        if (!feedback) return;
        
        feedback.classList.remove('hidden');
        
        if (selected === correct) {
            feedback.innerHTML = '<strong>Correct!</strong> This variable type is properly classified.';
            feedback.style.background = 'var(--color-bg-3)';
        } else {
            feedback.innerHTML = `<strong>Incorrect.</strong> The correct answer is ${correct.replace('-', ' - ')}.`;
            feedback.style.background = 'var(--color-bg-4)';
        }
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

        // Initialize slide-specific features
        this.initializeSlideFeatures(slideNumber);

        // Re-render MathJax for new slide
        if (window.MathJax) {
            window.MathJax.typesetPromise ? 
                window.MathJax.typesetPromise([newSlideElement]).catch(err => console.warn('MathJax rendering error:', err)) :
                window.MathJax.Hub?.Queue(['Typeset', window.MathJax.Hub, newSlideElement]);
        }

        // Stop any running timer when changing slides
        this.stopTimer();
    }

    initializeSlideFeatures(slideNumber) {
        switch(slideNumber) {
            case 8:
                this.initializePieChart();
                break;
            case 9:
                this.initializeBarChart();
                break;
            case 11:
                this.initializeHistogramChart();
                break;
            case 12:
                this.initializeDotplot();
                break;
            case 13:
                this.initializeStemLeaf();
                break;
            case 16:
                this.initializeHouseholdChart();
                break;
            case 17:
                this.initializeMisleadingCharts();
                break;
            case 22:
                this.initializeBillionairesAnalysis();
                break;
        }
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

    // Chart Initialization Methods
    initializeCharts() {
        // Initialize charts that need to be ready on load
        setTimeout(() => {
            if (this.currentSlide === 8) this.initializePieChart();
            if (this.currentSlide === 9) this.initializeBarChart();
        }, 100);
    }

    initializePieChart() {
        const ctx = document.getElementById('pieChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.chartInstances.pieChart) {
            this.chartInstances.pieChart.destroy();
        }

        const data = this.calculateFrequencyDistribution(this.sampleData.politicalParty);
        
        this.chartInstances.pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.frequencies,
                    backgroundColor: [
                        'var(--color-primary)',
                        'var(--color-accent)',
                        'var(--color-success)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 2000
                }
            }
        });
    }

    initializeBarChart() {
        const ctx = document.getElementById('barChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.chartInstances.barChart) {
            this.chartInstances.barChart.destroy();
        }

        const data = this.calculateFrequencyDistribution(this.sampleData.politicalParty);
        
        this.chartInstances.barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Frequency',
                    data: data.frequencies,
                    backgroundColor: [
                        'var(--color-primary)',
                        'var(--color-accent)', 
                        'var(--color-success)'
                    ],
                    borderColor: [
                        'var(--color-primary)',
                        'var(--color-accent)',
                        'var(--color-success)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Political Party'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    initializeHistogramChart() {
        const ctx = document.getElementById('histogramChart');
        if (!ctx) return;

        this.buildHistogram();
    }

    buildHistogram() {
        const ctx = document.getElementById('histogramChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.chartInstances.histogramChart) {
            this.chartInstances.histogramChart.destroy();
        }

        const bins = this.createHistogramBins(this.sampleData.daysToMaturity, 7);
        
        this.chartInstances.histogramChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bins.labels,
                datasets: [{
                    label: 'Frequency',
                    data: bins.frequencies,
                    backgroundColor: 'rgba(var(--color-teal-500-rgb), 0.7)',
                    borderColor: 'var(--color-primary)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Days to Maturity - Histogram'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Days to Maturity'
                        }
                    }
                },
                animation: {
                    duration: 1500
                }
            }
        });
    }

    initializeDotplot() {
        const svg = document.getElementById('dotplotSVG');
        if (!svg) return;

        this.createDotplot(this.sampleData.dvdPrices);
    }

    createDotplot(data) {
        const svg = document.getElementById('dotplotSVG');
        if (!svg) return;

        // Clear existing content
        svg.innerHTML = '';

        const margin = {top: 20, right: 30, bottom: 40, left: 50};
        const width = 700 - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        // Create scales
        const xScale = d3.scaleLinear()
            .domain([d3.min(data) - 5, d3.max(data) + 5])
            .range([0, width]);

        // Count frequencies
        const frequencies = {};
        data.forEach(d => {
            frequencies[d] = (frequencies[d] || 0) + 1;
        });

        // Create SVG group
        const g = d3.select(svg)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Add x-axis
        g.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));

        // Add axis label
        g.append('text')
            .attr('transform', `translate(${width/2},${height + 35})`)
            .style('text-anchor', 'middle')
            .text('Price ($)');

        // Add dots
        Object.keys(frequencies).forEach(price => {
            const count = frequencies[price];
            for (let i = 0; i < count; i++) {
                g.append('circle')
                    .attr('cx', xScale(+price))
                    .attr('cy', height - (i + 1) * 20)
                    .attr('r', 5)
                    .attr('fill', 'var(--color-primary)')
                    .attr('stroke', 'white')
                    .attr('stroke-width', 1);
            }
        });
    }

    initializeStemLeaf() {
        this.buildStemLeafTable();
    }

    buildStemLeafTable() {
        const tableBody = document.getElementById('stemleafBody');
        if (!tableBody) return;

        const data = this.sampleData.daysToMaturity.slice(0, 20); // Use subset for clarity
        const stemLeafData = this.createStemLeafData(data);
        
        tableBody.innerHTML = '';
        
        stemLeafData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="stem">${row.stem}</td>
                <td class="separator">|</td>
                <td class="leaves">${row.leaves.join(' ')}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    createStemLeafData(data) {
        const stemLeaf = {};
        
        // Group data by stem
        data.forEach(value => {
            const stem = Math.floor(value / 10);
            const leaf = value % 10;
            
            if (!stemLeaf[stem]) {
                stemLeaf[stem] = [];
            }
            stemLeaf[stem].push(leaf);
        });
        
        // Sort leaves and create final structure
        const result = [];
        Object.keys(stemLeaf).sort((a, b) => +a - +b).forEach(stem => {
            result.push({
                stem: stem,
                leaves: stemLeaf[stem].sort((a, b) => a - b)
            });
        });
        
        return result;
    }

    initializeHouseholdChart() {
        const ctx = document.getElementById('householdChart');
        if (!ctx) return;

        const householdData = {
            labels: ['1', '2', '3', '4', '5', '6', '7+'],
            frequencies: [0.273, 0.340, 0.158, 0.137, 0.062, 0.021, 0.009]
        };

        this.chartInstances.householdChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: householdData.labels,
                datasets: [{
                    label: 'Relative Frequency',
                    data: householdData.frequencies,
                    backgroundColor: 'rgba(var(--color-teal-500-rgb), 0.7)',
                    borderColor: 'var(--color-primary)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'U.S. Household Size Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Relative Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Number of People'
                        }
                    }
                }
            }
        });
    }

    initializeMisleadingCharts() {
        this.createTruncatedChart();
        this.createFullScaleChart();
    }

    createTruncatedChart() {
        const ctx = document.getElementById('truncatedChart');
        if (!ctx) return;

        const unemploymentData = [7.9, 7.8, 7.7, 7.6];
        const labels = ['Jan', 'Feb', 'Mar', 'Apr'];

        this.chartInstances.truncatedChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: unemploymentData,
                    backgroundColor: 'var(--color-error)',
                    borderColor: 'var(--color-error)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Truncated (Misleading)'
                    }
                },
                scales: {
                    y: {
                        min: 7.0,
                        max: 8.0,
                        title: {
                            display: true,
                            text: 'Unemployment Rate (%)'
                        }
                    }
                }
            }
        });
    }

    createFullScaleChart() {
        const ctx = document.getElementById('fullScaleChart');
        if (!ctx) return;

        const unemploymentData = [7.9, 7.8, 7.7, 7.6];
        const labels = ['Jan', 'Feb', 'Mar', 'Apr'];

        this.chartInstances.fullScaleChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: unemploymentData,
                    backgroundColor: 'var(--color-success)',
                    borderColor: 'var(--color-success)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Full Scale (Accurate)'
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Unemployment Rate (%)'
                        }
                    }
                }
            }
        });
    }

    initializeBillionairesAnalysis() {
        this.showAnalysisTab('citizenship');
    }

    showAnalysisTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[onclick="showAnalysisTab('${tabName}')"]`)?.classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabName}-panel`)?.classList.add('active');

        // Initialize appropriate chart
        switch(tabName) {
            case 'citizenship':
                this.createCitizenshipChart();
                break;
            case 'age':
                this.createAgeChart();
                break;
            case 'wealth':
                this.createWealthChart();
                break;
        }
    }

    createCitizenshipChart() {
        const ctx = document.getElementById('citizenshipChart');
        if (!ctx) return;

        if (this.chartInstances.citizenshipChart) {
            this.chartInstances.citizenshipChart.destroy();
        }

        const citizenshipFreq = this.calculateFrequencyDistribution(this.sampleData.citizenship);

        this.chartInstances.citizenshipChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: citizenshipFreq.labels,
                datasets: [{
                    data: citizenshipFreq.frequencies,
                    backgroundColor: [
                        'var(--color-primary)',
                        'var(--color-accent)',
                        'var(--color-success)',
                        'var(--color-warning)',
                        'var(--color-red-400)',
                        'var(--color-orange-400)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    createAgeChart() {
        const ctx = document.getElementById('ageChart');
        if (!ctx) return;

        if (this.chartInstances.ageChart) {
            this.chartInstances.ageChart.destroy();
        }

        const ageBins = this.createHistogramBins(this.sampleData.billionairesAge, 6);

        this.chartInstances.ageChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ageBins.labels,
                datasets: [{
                    label: 'Frequency',
                    data: ageBins.frequencies,
                    backgroundColor: 'rgba(var(--color-accent-rgb), 0.7)',
                    borderColor: 'var(--color-accent)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Age Distribution of Billionaires'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Age (years)'
                        }
                    }
                }
            }
        });
    }

    createWealthChart() {
        const ctx = document.getElementById('wealthChart');
        if (!ctx) return;

        if (this.chartInstances.wealthChart) {
            this.chartInstances.wealthChart.destroy();
        }

        const wealthBins = this.createHistogramBins(this.sampleData.billionairesWealth, 8);

        this.chartInstances.wealthChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: wealthBins.labels,
                datasets: [{
                    label: 'Frequency',
                    data: wealthBins.frequencies,
                    backgroundColor: 'rgba(var(--color-success-rgb), 0.7)',
                    borderColor: 'var(--color-success)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Wealth Distribution of Top 25 Billionaires'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Wealth (Billions USD)'
                        }
                    }
                }
            }
        });
    }

    // Utility Methods
    calculateFrequencyDistribution(data) {
        const frequencies = {};
        data.forEach(item => {
            frequencies[item] = (frequencies[item] || 0) + 1;
        });

        const labels = Object.keys(frequencies);
        const freqValues = Object.values(frequencies);

        return {
            labels: labels,
            frequencies: freqValues,
            relativeFrequencies: freqValues.map(f => f / data.length)
        };
    }

    createHistogramBins(data, numBins) {
        const min = Math.min(...data);
        const max = Math.max(...data);
        const binWidth = (max - min) / numBins;
        
        const bins = [];
        const frequencies = new Array(numBins).fill(0);
        
        // Create bin labels
        for (let i = 0; i < numBins; i++) {
            const binStart = min + i * binWidth;
            const binEnd = min + (i + 1) * binWidth;
            bins.push(`${binStart.toFixed(0)}-${binEnd.toFixed(0)}`);
        }
        
        // Count frequencies
        data.forEach(value => {
            const binIndex = Math.min(Math.floor((value - min) / binWidth), numBins - 1);
            frequencies[binIndex]++;
        });
        
        return {
            labels: bins,
            frequencies: frequencies
        };
    }

    updateBins() {
        const slider = document.getElementById('binSlider');
        const valueDisplay = document.getElementById('binValue');
        if (slider && valueDisplay) {
            valueDisplay.textContent = slider.value;
            this.buildHistogram();
        }
    }

    // Animation Methods
    animatePieChart() {
        if (this.chartInstances.pieChart) {
            this.chartInstances.pieChart.update('active');
        }
    }

    animateBarChart() {
        if (this.chartInstances.barChart) {
            this.chartInstances.barChart.update('active');
        }
    }

    animateDotplot() {
        this.createDotplot(this.sampleData.dvdPrices);
    }

    animateStemLeaf() {
        this.buildStemLeafTable();
    }

    // Practice Problems
    buildFrequencyTable() {
        const tableBody = document.getElementById('tvTableBody');
        if (!tableBody) return;

        const tvData = this.sampleData.tvData;
        const freqDist = this.calculateFrequencyDistribution(tvData);
        
        tableBody.innerHTML = '';
        
        // Sort by TV count
        const sortedEntries = freqDist.labels.map((label, i) => ({
            tvs: parseInt(label),
            freq: freqDist.frequencies[i],
            relFreq: freqDist.relativeFrequencies[i]
        })).sort((a, b) => a.tvs - b.tvs);
        
        sortedEntries.forEach(entry => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${entry.tvs}</td>
                <td>${entry.freq}</td>
                <td>${entry.relFreq.toFixed(3)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    createTVHistogram() {
        const ctx = document.getElementById('tvHistogram');
        if (!ctx) return;

        if (this.chartInstances.tvHistogram) {
            this.chartInstances.tvHistogram.destroy();
        }

        const freqDist = this.calculateFrequencyDistribution(this.sampleData.tvData);
        
        // Sort by TV count
        const sortedEntries = freqDist.labels.map((label, i) => ({
            tvs: parseInt(label),
            freq: freqDist.frequencies[i]
        })).sort((a, b) => a.tvs - b.tvs);

        this.chartInstances.tvHistogram = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedEntries.map(e => e.tvs.toString()),
                datasets: [{
                    label: 'Frequency',
                    data: sortedEntries.map(e => e.freq),
                    backgroundColor: 'rgba(var(--color-primary-rgb), 0.7)',
                    borderColor: 'var(--color-primary)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'TV Sets per Household'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Number of TVs'
                        }
                    }
                }
            }
        });
    }

    showRelativeFreq() {
        this.buildFrequencyTable();
    }

    checkAllClassifications() {
        document.querySelectorAll('.classification-item').forEach((item, index) => {
            const correctAnswer = item.getAttribute('data-answer');
            const correctBtn = item.querySelector(`[data-type="${correctAnswer}"]`);
            if (correctBtn && !correctBtn.classList.contains('correct')) {
                correctBtn.click();
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

    addKeyboardHint() {
        const hint = document.createElement('div');
        hint.className = 'keyboard-nav';
        hint.innerHTML = 'Use ← → keys to navigate, F11 for fullscreen';
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
            this.clearCursorHiding();
        } catch (error) {
            console.warn('Exit fullscreen failed:', error);
        }
    }

    updateFullscreenButton(isFullscreen) {
        const btn = document.getElementById('fullscreenBtn');
        if (btn) {
            btn.innerHTML = isFullscreen ? '🗗' : '⛶';
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
        
        cursorTimeout = setTimeout(hideCursor, 3000);
        container.addEventListener('mousemove', showCursor);
        container.addEventListener('click', showCursor);
        
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
                
                if (slideDots) slideDots.style.opacity = '1';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '1';
                
                if (hideTimeout) clearTimeout(hideTimeout);
                hideTimeout = setTimeout(hideNav, 3000);
            }
        };
        
        const hideNav = () => {
            if (document.fullscreenElement) {
                navControls.style.opacity = '0';
                navControls.style.pointerEvents = 'none';
                
                if (slideDots) slideDots.style.opacity = '0';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '0';
            }
        };
        
        const onMouseMove = (e) => {
            if (document.fullscreenElement) {
                showNav();
            }
        };
        
        const onFullscreenChange = () => {
            if (!document.fullscreenElement) {
                navControls.style.opacity = '';
                navControls.style.pointerEvents = '';
                if (slideDots) slideDots.style.opacity = '';
                if (fullscreenBtn) fullscreenBtn.style.opacity = '';
                
                if (hideTimeout) {
                    clearTimeout(hideTimeout);
                    hideTimeout = null;
                }
            } else {
                hideNav();
            }
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('fullscreenchange', onFullscreenChange);
    }

    handleFullscreenChange() {
        const container = document.querySelector('.presentation-container');
        const isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
        
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

function animatePieChart() {
    if (presentation) presentation.animatePieChart();
}

function animateBarChart() {
    if (presentation) presentation.animateBarChart();
}

function buildHistogram() {
    if (presentation) presentation.buildHistogram();
}

function updateBins() {
    if (presentation) presentation.updateBins();
}

function animateDotplot() {
    if (presentation) presentation.animateDotplot();
}

function buildStemLeaf() {
    if (presentation) presentation.buildStemLeafTable();
}

function animateStemLeaf() {
    if (presentation) presentation.animateStemLeaf();
}

function showAnalysisTab(tabName) {
    if (presentation) presentation.showAnalysisTab(tabName);
}

function buildFrequencyTable() {
    if (presentation) presentation.buildFrequencyTable();
}

function showRelativeFreq() {
    if (presentation) presentation.showRelativeFreq();
}

function createTVHistogram() {
    if (presentation) presentation.createTVHistogram();
}

function checkAllClassifications() {
    if (presentation) presentation.checkAllClassifications();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    presentation = new OrganizingDataPresentation();
    window.presentation = presentation;
    
    console.log('Organizing Data Presentation Ready!');
    console.log('42 comprehensive slides covering Chapter 2: Organizing Data');
    console.log('Use arrow keys to navigate, F11 for fullscreen');
});

// Error handling
window.addEventListener('error', (e) => {
    console.error('Presentation error:', e.error);
});

// D3.js simulation for advanced visualizations
const d3 = {
    scaleLinear: () => ({
        domain: () => ({ range: () => ({}) }),
        range: () => ({})
    }),
    min: (arr) => Math.min(...arr),
    max: (arr) => Math.max(...arr),
    select: (selector) => ({
        append: () => ({ 
            attr: () => ({ call: () => ({}) }),
            style: () => ({}),
            text: () => ({})
        })
    }),
    axisBottom: () => ({})
};

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OrganizingDataPresentation };
}