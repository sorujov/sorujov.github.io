/* Organizing Data - Interactive Slides (fixed) */

class OrganizingDataPresentation {
  constructor() {
    this.currentSlide = 1;
    this.slides = [];
    this.totalSlides = 0;
    this.timerInterval = null;
    this.timerSeconds = 0;
    this.chartInstances = {};

    this.sampleData = {
      politicalParty: ['Democratic','Republican','Other','Democratic','Republican','Democratic','Other','Republican','Democratic','Republican'],
      tvData: [1,1,1,2,6,3,3,4,2,4,3,2,1,5,2,1,3,6,2,2,3,1,1,4,3,2,2,2,2,3,0,3,1,2,1,2,3,1,1,3,3,2,1,2,1,1,3,1,5,1],
      daysToMaturity: [70,64,99,55,64,89,87,65,62,38,67,70,60,69,78,39,75,56,71,51,99,68,95,86,57,53,47,50,55,81,80,98,51,36,63,66,85,79,83,70],
      dvdPrices: [210,219,214,197,224,219,199,199,208,209,215,199,212,212,219,210],
      billionairesAge: [73,57,77,82,68,77,73,84,90,64,58,65,71,65,79,63,69,93,49,40,39,56,88,85,55],
      billionairesWealth: [73,67,57,53.5,43,34,34,31,30,29,28.2,28,27,26.7,26.5,26.3,26.1,26,25.2,23,22.8,21.5,20.4,20.3,20.3],
      citizenship: ['Mexico','United States','Spain','United States','United States','United States','United States','Hong Kong','France','France','United States','Sweden','United States','United States','United States','United States','United States','Germany','United States','United States','United States','India','Italy','Hong Kong','Canada']
    };
  }

  init() {
    this.discoverSlides();
    this.setupEventListeners();
    this.updateSlideCounter();
    this.updateNavigationButtons();
    this.setupSlideDots();
    this.initializeCharts();
    this.goToSlide(1);
    console.log(`${this.totalSlides} slides loaded`);
  }

  discoverSlides() {
    this.slides = Array.from(document.querySelectorAll('.slide'));
    this.totalSlides = this.slides.length;

    // Ensure only the first slide is active at start
    this.slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === 0);
      slide.setAttribute('aria-hidden', i === 0 ? 'false' : 'true');
    });
  }

  setupEventListeners() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const fullscreenBtn = document.getElementById('fullscreenBtn');

    if (prevBtn) prevBtn.addEventListener('click', () => this.previousSlide());
    if (nextBtn) nextBtn.addEventListener('click', () => this.nextSlide());
    if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

    // Keyboard navigation
    document.addEventListener('keydown', (e) => this.handleKeyPress(e));

    // Chart controls (IDs optional; also keep global wrappers)
    document.getElementById('animatePieBtn')?.addEventListener('click', () => this.animatePieChart());
    document.getElementById('togglePieLabelsBtn')?.addEventListener('click', () => this.togglePieLabels());

    document.getElementById('animateBarBtn')?.addEventListener('click', () => this.animateBarChart());

    document.getElementById('buildHistogramBtn')?.addEventListener('click', () => this.buildHistogram());
    document.getElementById('binSlider')?.addEventListener('input', () => this.updateBins());

    document.getElementById('animateDotplotBtn')?.addEventListener('click', () => this.animateDotplot());
    document.getElementById('highlightOutliersBtn')?.addEventListener('click', () => this.highlightOutliers());

    // Classification
    document.querySelectorAll('.classify-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const item = e.currentTarget.closest('.classification-item');
        const selectedType = e.currentTarget.getAttribute('data-type');
        const correctAnswer = item?.getAttribute('data-answer') || '';
        item?.querySelectorAll('.classify-btn').forEach(b => b.classList.remove('correct','incorrect'));
        if (selectedType === correctAnswer) e.currentTarget.classList.add('correct'); else e.currentTarget.classList.add('incorrect');
        this.showClassificationFeedback(item, selectedType, correctAnswer);
      });
    });
    document.getElementById('checkAllBtn')?.addEventListener('click', () => this.checkAllClassifications());

    // Fullscreen change
    document.addEventListener('fullscreenchange', () => this.handleFullscreenChange());
  }

  setupSlideDots() {
    document.querySelectorAll('.dot').forEach((dot, idx) => {
      dot.addEventListener('click', () => this.goToSlide(idx + 1));
      dot.setAttribute('tabindex', '0');
      dot.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.goToSlide(idx + 1);
        }
      });
    });
  }

  handleKeyPress(e) {
    switch (e.key) {
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault(); this.previousSlide(); break;
      case 'ArrowRight':
      case 'ArrowDown':
      case ' ':
        e.preventDefault(); this.nextSlide(); break;
      case 'Home':
        e.preventDefault(); this.goToSlide(1); break;
      case 'End':
        e.preventDefault(); this.goToSlide(this.totalSlides); break;
      case 'Escape':
        this.stopTimer();
        if (document.fullscreenElement) this.exitFullscreen();
        break;
      case 'F11':
        e.preventDefault(); this.toggleFullscreen(); break;
    }
  }

  nextSlide() { if (this.currentSlide < this.totalSlides) this.goToSlide(this.currentSlide + 1); }
  previousSlide() { if (this.currentSlide > 1) this.goToSlide(this.currentSlide - 1); }

  goToSlide(n) {
    if (n < 1 || n > this.totalSlides) return;
    const currentEl = this.slides[this.currentSlide - 1];
    const nextEl = this.slides[n - 1];
    if (currentEl) {
      currentEl.classList.remove('active');
      currentEl.setAttribute('aria-hidden','true');
    }
    if (nextEl) {
      nextEl.classList.add('active');
      nextEl.setAttribute('aria-hidden','false');
    }
    this.currentSlide = n;
    this.updateSlideCounter();
    this.updateNavigationButtons();
    this.updateSlideDots();
    this.initializeSlideFeatures(n);
    this.stopTimer();
  }

  updateSlideCounter() {
    const cur = document.getElementById('currentSlide');
    const tot = document.getElementById('totalSlides');
    if (cur) cur.textContent = String(this.currentSlide);
    if (tot) tot.textContent = String(this.totalSlides);
  }

  updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    if (prevBtn) prevBtn.disabled = this.currentSlide === 1;
    if (nextBtn) nextBtn.disabled = this.currentSlide === this.totalSlides;
  }

  updateSlideDots() {
    document.querySelectorAll('.dot').forEach((dot, idx) => {
      dot.classList.toggle('active', idx + 1 === this.currentSlide);
    });
  }

  initializeSlideFeatures(n) {
    if (n === 8) this.initializePieChart();
    if (n === 9) this.initializeBarChart();
    if (n === 11) this.initializeHistogramChart();
    if (n === 12) this.initializeDotplot();
    if (n === 13) this.initializeStemLeaf();
    if (n === 14) this.initializeShapeGenerator();
    if (n === 15) this.initializeSkewnessAnalyzer();
    if (n === 16) this.initializeHouseholdChart();
    if (n === 17) this.initializeMisleadingCharts();
    if (n === 22) this.initializeBillionairesAnalysis();
  }

  // Charts
  initializeCharts() {
    // no-op: initialized per slide for performance
  }

  calculateFrequencyDistribution(arr) {
    const map = new Map();
    arr.forEach(v => map.set(v, (map.get(v) || 0) + 1));
    const labels = Array.from(map.keys());
    const freqs = Array.from(map.values());
    return { labels, frequencies: freqs, relativeFrequencies: freqs.map(f => f / arr.length) };
  }

  initializePieChart() {
    const ctx = document.getElementById('pieChart');
    if (!ctx || typeof Chart === 'undefined') return;
    if (this.chartInstances.pieChart) this.chartInstances.pieChart.destroy();
    const data = this.calculateFrequencyDistribution(this.sampleData.politicalParty);
    this.chartInstances.pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: data.labels,
        datasets: [{ data: data.frequencies, backgroundColor: ['#148F77','#F39C12','#16A085'], borderWidth: 2, borderColor: '#fff' }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
        animation: { animateRotate: true, duration: 800 }
      }
    });
  }

  togglePieLabels() {
    const chart = this.chartInstances.pieChart;
    if (!chart) return;
    const show = !(chart.options.plugins?.legend?.display === false);
    chart.options.plugins = chart.options.plugins || {};
    chart.options.plugins.legend = chart.options.plugins.legend || {};
    chart.options.plugins.legend.display = !show;
    chart.update();
  }

  animatePieChart() { this.chartInstances.pieChart?.update('active'); }

  initializeBarChart() {
    const ctx = document.getElementById('barChart');
    if (!ctx || typeof Chart === 'undefined') return;
    if (this.chartInstances.barChart) this.chartInstances.barChart.destroy();
    const data = this.calculateFrequencyDistribution(this.sampleData.politicalParty);
    this.chartInstances.barChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{ label: 'Frequency', data: data.frequencies, backgroundColor: '#148F77', borderColor: '#117A65', borderWidth: 2 }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
        animation: { duration: 600, easing: 'easeOutQuart' }
      }
    });
  }

  animateBarChart() { this.chartInstances.barChart?.update('active'); }

  initializeHistogramChart() { this.buildHistogram(); }

  getBinsFromSlider() {
    const slider = document.getElementById('binSlider');
    const n = slider ? parseInt(slider.value, 10) || 7 : 7;
    const label = document.getElementById('binValue');
    if (label) label.textContent = String(n);
    return n;
  }

  createHistogramBins(data, numBins) {
    const min = Math.min(...data), max = Math.max(...data);
    const width = (max - min) / numBins;
    const labels = [], freqs = new Array(numBins).fill(0);
    for (let i = 0; i < numBins; i++) {
      const a = Math.floor(min + i * width), b = Math.floor(min + (i + 1) * width);
      labels.push(`${a}-${b}`);
    }
    data.forEach(v => {
      const idx = Math.min(numBins - 1, Math.floor((v - min) / width));
      freqs[idx]++;
    });
    return { labels, frequencies: freqs };
    }

  buildHistogram() {
    const ctx = document.getElementById('histogramChart');
    if (!ctx || typeof Chart === 'undefined') return;
    if (this.chartInstances.histogramChart) this.chartInstances.histogramChart.destroy();
    const bins = this.createHistogramBins(this.sampleData.daysToMaturity, this.getBinsFromSlider());
    this.chartInstances.histogramChart = new Chart(ctx, {
      type: 'bar',
      data: { labels: bins.labels, datasets: [{ label: 'Frequency', data: bins.frequencies, backgroundColor: 'rgba(20,143,119,0.7)', borderColor: '#148F77' }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });
  }

  updateBins() { this.buildHistogram(); }

  // Dotplot (requires d3)
  initializeDotplot() {
    if (typeof d3 === 'undefined') return; // guard if d3 not loaded
    this.createDotplot(this.sampleData.dvdPrices);
  }

  createDotplot(data) {
    if (typeof d3 === 'undefined') return;
    const svg = d3.select('#dotplotSVG');
    if (svg.empty()) return;
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = +svg.attr('width') - margin.left - margin.right;
    const height = +svg.attr('height') - margin.top - margin.bottom;

    const x = d3.scaleLinear().domain([d3.min(data) - 5, d3.max(data) + 5]).range([0, width]);
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    g.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x));

    const map = new Map();
    data.forEach(v => map.set(v, (map.get(v) || 0) + 1));
    map.forEach((count, v) => {
      for (let i = 0; i < count; i++) {
        g.append('circle')
          .attr('cx', x(v))
          .attr('cy', height - i * 18 - 10)
          .attr('r', 5)
          .attr('fill', '#148F77')
          .attr('stroke', '#fff');
      }
    });
  }

  animateDotplot() { this.initializeDotplot(); }

  highlightOutliers() {
    if (typeof d3 === 'undefined') return;
    d3.select('#dotplotSVG').selectAll('circle')
      .attr('fill', (d, i, nodes) => {
        const cx = +nodes[i].getAttribute('cx');
        // naive tails: 10% at left and right ends
        const svg = d3.select('#dotplotSVG');
        const width = +svg.attr('width');
        return (cx < width * 0.2 || cx > width * 0.8) ? '#E74C3C' : '#148F77';
      });
  }

  // Stem & leaf
  initializeStemLeaf() { this.buildStemLeafTable(); }

  buildStemLeafTable() {
    const tbody = document.getElementById('stemleafBody');
    if (!tbody) return;
    const grouped = {};
    this.sampleData.daysToMaturity.slice(0, 20).forEach(v => {
      const stem = Math.floor(v / 10);
      const leaf = v % 10;
      (grouped[stem] ||= []).push(leaf);
    });
    const rows = Object.keys(grouped).map(k => [k, grouped[k].sort((a,b)=>a-b)]).sort((a,b)=>a[0]-b[0]);
    tbody.innerHTML = rows.map(([stem, leaves]) =>
      `<tr><td class="stem">${stem}</td><td class="separator">|</td><td class="leaves">${leaves.join(' ')}</td></tr>`
    ).join('');
  }

  // Misleading graphs and cases
  initializeMisleadingCharts() {
    const tr = document.getElementById('truncatedChart');
    const fs = document.getElementById('fullScaleChart');
    if (!tr || !fs || typeof Chart === 'undefined') return;
    const labels = ['Jan','Feb','Mar','Apr'];
    const data = [7.9,7.8,7.7,7.6];
    this.chartInstances.truncatedChart?.destroy();
    this.chartInstances.fullScaleChart?.destroy();
    this.chartInstances.truncatedChart = new Chart(tr, {
      type: 'bar', data: { labels, datasets: [{ data, backgroundColor: '#E74C3C' }] },
      options: { scales: { y: { min: 7, max: 8 } }, plugins: { legend: { display: false } } }
    });
    this.chartInstances.fullScaleChart = new Chart(fs, {
      type: 'bar', data: { labels, datasets: [{ data, backgroundColor: '#16A085' }] },
      options: { scales: { y: { min: 0, max: 10 } }, plugins: { legend: { display: false } } }
    });
  }

  initializeHouseholdChart() {
    const ctx = document.getElementById('householdChart');
    if (!ctx || typeof Chart === 'undefined') return;
    this.chartInstances.householdChart?.destroy();
    const labels = ['1','2','3','4','5','6','7+'];
    const freqs = [0.273,0.340,0.158,0.137,0.062,0.021,0.009];
    this.chartInstances.householdChart = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets: [{ label: 'Relative Frequency', data: freqs, backgroundColor: 'rgba(20,143,119,0.7)' }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });
  }

  initializeBillionairesAnalysis() { this.createCitizenshipChart(); }

  createCitizenshipChart() {
    const ctx = document.getElementById('citizenshipChart');
    if (!ctx || typeof Chart === 'undefined') return;
    this.chartInstances.citizenshipChart?.destroy();
    const freq = this.calculateFrequencyDistribution(this.sampleData.citizenship);
    this.chartInstances.citizenshipChart = new Chart(ctx, {
      type: 'pie',
      data: { labels: freq.labels, datasets: [{ data: freq.frequencies, backgroundColor: ['#148F77','#F39C12','#16A085','#2874A6','#884EA0','#D35400'] }] },
      options: { responsive: true, plugins: { legend: { position: 'right' } } }
    });
  }

  // Timer (optional use on activity slides)
  startTimer(seconds) {
    this.stopTimer();
    this.timerSeconds = seconds;
    const disp = document.getElementById('timerDisplay');
    const val = document.getElementById('timerValue');
    if (disp) disp.classList.add('active');
    const tick = () => {
      const m = Math.floor(this.timerSeconds / 60).toString().padStart(2,'0');
      const s = (this.timerSeconds % 60).toString().padStart(2,'0');
      if (val) val.textContent = `${m}:${s}`;
    };
    tick();
    this.timerInterval = setInterval(() => {
      this.timerSeconds--;
      tick();
      if (this.timerSeconds <= 0) this.stopTimer();
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = null;
    document.getElementById('timerDisplay')?.classList.remove('active');
  }

  // Fullscreen
  toggleFullscreen() {
    const el = document.querySelector('.presentation-container');
    if (!document.fullscreenElement) el?.requestFullscreen?.(); else document.exitFullscreen?.();
  }
  exitFullscreen() { document.exitFullscreen?.(); }
  handleFullscreenChange() {
    document.querySelector('.presentation-container')?.classList.toggle('fullscreen', !!document.fullscreenElement);
  }

  // Classification helpers
  showClassificationFeedback(item, selected, correct) {
    if (!item) return;
    const fb = item.querySelector('.feedback');
    if (!fb) return;
    fb.classList.remove('hidden');
    const correctText = correct.replace('-', ' - ').replace(/\b\w/g, c => c.toUpperCase());
    if (selected === correct) {
      fb.textContent = `Correct!`;
      fb.style.background = 'rgba(34,197,94,0.1)';
      fb.style.color = '#16A34A';
    } else {
      fb.textContent = `Incorrect. The correct answer is ${correctText}.`;
      fb.style.background = 'rgba(239,68,68,0.1)';
      fb.style.color = '#DC2626';
    }
  }

  checkAllClassifications() {
    document.querySelectorAll('.classification-item').forEach(item => {
      const correct = item.getAttribute('data-answer');
      const btn = item.querySelector(`[data-type="${correct}"]`);
      btn?.click();
    });
  }

  // Shape Generator Functions
  generateShape() {
    const peakSelect = document.getElementById('peakSelect');
    const shapeSelect = document.getElementById('shapeSelect');
    const canvas = document.getElementById('shapeCanvas');
    
    if (!canvas || !peakSelect || !shapeSelect) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const width = canvas.width;
    const height = canvas.height;
    const peaks = parseInt(peakSelect.value) || 1;
    const shapeType = shapeSelect.value || 'normal';
    
    // Set up drawing
    ctx.strokeStyle = '#148F77';
    ctx.fillStyle = 'rgba(20, 143, 119, 0.3)';
    ctx.lineWidth = 3;
    
    // Generate shape based on selection
    this.drawDistributionShape(ctx, width, height, peaks, shapeType);
  }

  drawDistributionShape(ctx, width, height, peaks, shapeType) {
    const padding = 40;
    const graphWidth = width - (padding * 2);
    const graphHeight = height - (padding * 2);
    
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    
    if (shapeType === 'normal') {
      this.drawNormalDistribution(ctx, padding, graphWidth, graphHeight, height, peaks);
    } else if (shapeType === 'uniform') {
      this.drawUniformDistribution(ctx, padding, graphWidth, graphHeight, height);
    } else if (shapeType === 'exponential') {
      this.drawExponentialDistribution(ctx, padding, graphWidth, graphHeight, height);
    }
    
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Fill area under curve
    ctx.globalAlpha = 0.3;
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  drawNormalDistribution(ctx, padding, graphWidth, graphHeight, height, peaks) {
    const points = 200;
    const peakSpacing = graphWidth / (peaks + 1);
    
    for (let i = 0; i <= points; i++) {
      const x = padding + (i / points) * graphWidth;
      let y = height - padding;
      
      // Calculate combined height from all peaks
      for (let peak = 1; peak <= peaks; peak++) {
        const peakCenter = padding + (peak * peakSpacing);
        const distance = Math.abs(x - peakCenter);
        const sigma = peakSpacing / 4; // Standard deviation
        const peakHeight = Math.exp(-(distance * distance) / (2 * sigma * sigma));
        y -= (peakHeight * graphHeight * 0.8) / peaks;
      }
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
  }

  drawUniformDistribution(ctx, padding, graphWidth, graphHeight, height) {
    const uniformHeight = height - padding - (graphHeight * 0.6);
    ctx.lineTo(padding, uniformHeight);
    ctx.lineTo(padding + graphWidth, uniformHeight);
  }

  drawExponentialDistribution(ctx, padding, graphWidth, graphHeight, height) {
    const points = 100;
    for (let i = 0; i <= points; i++) {
      const x = padding + (i / points) * graphWidth;
      const t = i / points * 3; // Scale for exponential
      const expValue = Math.exp(-t * 2);
      const y = height - padding - (expValue * graphHeight * 0.8);
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
  }

  // Initialize shape generator
  initializeShapeGenerator() {
    // Set initial values and generate first shape
    const peakSelect = document.getElementById('peakSelect');
    const shapeSelect = document.getElementById('shapeSelect');
    
    if (peakSelect) peakSelect.value = '1';
    if (shapeSelect) shapeSelect.value = 'normal';
    
    // Generate initial shape
    setTimeout(() => this.generateShape(), 100);
  }

  // Skewness Functions
  updateSkewness() {
    const slider = document.getElementById('skewSlider');
    const valueDisplay = document.getElementById('skewValue');
    const canvas = document.getElementById('skewCanvas');
    
    if (!slider || !valueDisplay || !canvas) {
      console.log('Skewness elements not found');
      return;
    }
    
    const skewValue = parseFloat(slider.value) || 0;
    
    // Update display text with proper formatting
    let skewText = skewValue.toFixed(1);
    if (skewValue === 0) skewText += ' (Symmetric)';
    else if (skewValue > 0) skewText += ' (Right Skewed)';
    else skewText += ' (Left Skewed)';
    
    valueDisplay.textContent = skewText;
    
    // Draw the distribution with improved algorithm
    this.drawSkewedDistribution(canvas, skewValue);
    
    console.log('Skewness updated:', skewValue);
  }

  drawSkewedDistribution(canvas, skewValue) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas with white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;
    const graphWidth = width - (2 * padding);
    const graphHeight = height - (2 * padding);
    
    // Set up drawing styles
    ctx.strokeStyle = '#148F77';
    ctx.fillStyle = 'rgba(20, 143, 119, 0.3)';
    ctx.lineWidth = 3;
    
    // Draw axes
    ctx.beginPath();
    ctx.strokeStyle = '#666666';
    ctx.lineWidth = 1;
    
    // X-axis
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    
    // Y-axis
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(padding, padding);
    ctx.stroke();
    
    // Draw the skewed distribution curve
    ctx.beginPath();
    ctx.strokeStyle = '#148F77';
    ctx.lineWidth = 3;
    
    const points = 200;
    const pathPoints = [];
    
    for (let i = 0; i <= points; i++) {
      const t = (i / points - 0.5) * 8; // Range from -4 to 4
      
      // Generate skewed normal distribution using better math
      let y;
      const normalValue = Math.exp(-(t * t) / 2); // Standard normal
      
      if (Math.abs(skewValue) < 0.1) {
        // Nearly symmetric
        y = normalValue;
      } else {
        // Apply skewness transformation
        const alpha = skewValue * 2; // Amplify skewness effect
        y = normalValue * (1 + skewValue * this.sign(t) * Math.abs(t) * 0.5);
        y = Math.max(0.01, y); // Ensure positive values
      }
      
      const x = padding + (i / points) * graphWidth;
      const yPos = height - padding - (y * graphHeight * 0.7);
      
      pathPoints.push({ x, y: yPos });
      
      if (i === 0) {
        ctx.moveTo(x, height - padding);
        ctx.lineTo(x, yPos);
      } else {
        ctx.lineTo(x, yPos);
      }
    }
    
    // Complete the path for filling
    ctx.lineTo(width - padding, height - padding);
    ctx.closePath();
    
    // Draw and fill
    ctx.globalAlpha = 0.3;
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.stroke();
    
    // Add labels
    ctx.fillStyle = '#333333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    
    // X-axis label
    ctx.fillText('Values', width / 2, height - 10);
    
    // Y-axis label
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Frequency', 0, 0);
    ctx.restore();
    
    // Skewness indicator
    ctx.fillStyle = '#148F77';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(`Skewness: ${skewValue.toFixed(1)}`, width - padding, padding + 20);
  }

  // Helper function for skewness calculation
  sign(x) {
    return x > 0 ? 1 : x < 0 ? -1 : 0;
  }

  // Initialize skewness analyzer  
  initializeSkewnessAnalyzer() {
    console.log('Initializing skewness analyzer...');
    
    const slider = document.getElementById('skewSlider');
    const canvas = document.getElementById('skewCanvas');
    
    if (!slider || !canvas) {
      console.warn('Skewness elements not found');
      return;
    }
    
    // Remove any existing event listeners
    slider.oninput = null;
    slider.onchange = null;
    
    // Add fresh event listeners
    slider.addEventListener('input', (e) => {
      console.log('Slider input event:', e.target.value);
      this.updateSkewness();
    });
    slider.addEventListener('change', (e) => {
      console.log('Slider change event:', e.target.value);
      this.updateSkewness();
    });
    
    // Set initial value
    slider.value = '0';
    
    // Force initial draw with delay to ensure DOM is ready
    setTimeout(() => {
      this.updateSkewness();
    }, 150);
    
    console.log('Skewness analyzer initialized with event listeners');
  }
}

// Global wrappers to support inline onclick
let presentation;
function startTimer(s){ presentation?.startTimer(s); }
function animatePieChart(){ presentation?.animatePieChart(); }
function togglePieLabels(){ presentation?.togglePieLabels(); }
function animateBarChart(){ presentation?.animateBarChart(); }
function buildHistogram(){ presentation?.buildHistogram(); }
function updateBins(){ presentation?.updateBins(); }
function animateDotplot(){ presentation?.animateDotplot(); }
function highlightOutliers(){ presentation?.highlightOutliers(); }
function checkAllClassifications(){ presentation?.checkAllClassifications(); }
function generateShape(){ presentation?.generateShape(); }
function updateSkewness() { 
  if (presentation && presentation.updateSkewness) {
    presentation.updateSkewness();
  } else {
    console.warn('Presentation or updateSkewness not available');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  presentation = new OrganizingDataPresentation();
  presentation.init();
});
