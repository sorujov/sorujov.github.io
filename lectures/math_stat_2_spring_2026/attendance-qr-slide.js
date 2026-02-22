/**
 * Attendance QR Code Generator for Reveal.js Lecture Slides
 * Math Stat II - Spring 2026 (Dual Section: A & B)
 *
 * Usage in QMD:
 *   Open lecture with ?section=A or ?section=B
 *   QR codes are generated on slides containing .attendance-qr elements
 *
 * Slide markup:
 *   <div class="attendance-qr" data-status="present"></div>
 *   <div class="attendance-qr" data-status="late"></div>
 */
(function() {
  'use strict';

  var PASSWORD = 'so123!';
  var QR_REFRESH_MS = 120000; // 2 minutes
  var BASE_URL = 'https://sorujov.github.io/attend/math-stat-2/';

  // Section schedules (Baku time, UTC+4)
  var SECTION_TIMES = {
    A: { start: 600, end: 690, label: 'Section A (10:00-11:30)' },
    B: { start: 690, end: 780, label: 'Section B (11:30-13:00)' }
  };

  var currentSection = null;
  var activeQRIntervals = {};

  // Get section from URL parameter
  function getSectionFromURL() {
    var params = new URLSearchParams(window.location.search);
    var sec = params.get('section');
    if (sec) return sec.toUpperCase();
    return null;
  }

  // Auto-detect section based on current Baku time
  function autoDetectSection() {
    var now = new Date();
    var utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    var bakuTime = new Date(utc + (4 * 3600000));
    var totalMinutes = bakuTime.getHours() * 60 + bakuTime.getMinutes();

    if (totalMinutes >= SECTION_TIMES.A.start && totalMinutes < SECTION_TIMES.B.start) {
      return 'A';
    } else if (totalMinutes >= SECTION_TIMES.B.start && totalMinutes <= SECTION_TIMES.B.end) {
      return 'B';
    }
    return null;
  }

  // Determine section: URL param > auto-detect > prompt
  currentSection = getSectionFromURL() || autoDetectSection();

  // Generate token (same scheme as standalone QR page)
  function generateToken() {
    var now = new Date();
    var timestamp = now.getTime();
    var sessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    var token = btoa(timestamp + ':' + sessionId + ':' + PASSWORD).replace(/[+/=]/g, '');

    var dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    var timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });

    return {
      token: token,
      sessionId: sessionId,
      sessionInfo: dateStr + ' ' + timeStr,
      timestamp: timestamp
    };
  }

  // Build check-in URL
  function buildAttendURL(status) {
    var tokenData = generateToken();
    var section = currentSection || 'A';

    return BASE_URL + '?session=' + encodeURIComponent(tokenData.sessionInfo) +
           '&token=' + tokenData.token +
           '&section=' + section +
           '&status=' + status;
  }

  // Generate or refresh a QR code in a container
  function renderQR(container) {
    var status = container.getAttribute('data-status') || 'present';
    var qrDiv = container.querySelector('.qr-image');
    var infoDiv = container.querySelector('.qr-info');
    var timerDiv = container.querySelector('.qr-timer');

    if (!qrDiv) {
      // First-time setup: create inner elements
      qrDiv = document.createElement('div');
      qrDiv.className = 'qr-image';
      qrDiv.style.cssText = 'margin: 10px auto; display: flex; justify-content: center;';

      infoDiv = document.createElement('div');
      infoDiv.className = 'qr-info';
      infoDiv.style.cssText = 'text-align: center; font-size: 20px; margin-top: 8px; color: #555;';

      timerDiv = document.createElement('div');
      timerDiv.className = 'qr-timer';
      timerDiv.style.cssText = 'text-align: center; font-size: 16px; color: #888; margin-top: 4px;';

      container.appendChild(qrDiv);
      container.appendChild(infoDiv);
      container.appendChild(timerDiv);
    }

    // Clear previous QR
    qrDiv.innerHTML = '';

    var url = buildAttendURL(status);
    var sectionLabel = currentSection ? SECTION_TIMES[currentSection].label : 'Section ?';
    var statusLabel = status === 'late' ? '⏰ Late Check-in' : '✓ On-time Check-in';

    // Generate QR
    var qrSize = Math.min(450, window.innerWidth * 0.4, window.innerHeight * 0.45);
    new QRCode(qrDiv, {
      text: url,
      width: qrSize,
      height: qrSize,
      correctLevel: QRCode.CorrectLevel.H
    });

    infoDiv.textContent = sectionLabel + ' — ' + statusLabel;

    // Countdown
    var secondsLeft = 120;
    timerDiv.textContent = 'Refreshes in ' + secondsLeft + 's';

    var countdownId = setInterval(function() {
      secondsLeft--;
      if (secondsLeft > 0) {
        timerDiv.textContent = 'Refreshes in ' + secondsLeft + 's';
      } else {
        timerDiv.textContent = 'Refreshing...';
        clearInterval(countdownId);
      }
    }, 1000);

    // Store interval IDs for cleanup
    var containerId = container.id || ('qr-' + status);
    if (activeQRIntervals[containerId]) {
      clearInterval(activeQRIntervals[containerId].countdown);
      clearInterval(activeQRIntervals[containerId].refresh);
    }

    var refreshId = setInterval(function() {
      renderQR(container);
    }, QR_REFRESH_MS);

    activeQRIntervals[containerId] = {
      countdown: countdownId,
      refresh: refreshId
    };
  }

  // Stop all QR refresh intervals
  function stopAllIntervals() {
    var keys = Object.keys(activeQRIntervals);
    for (var i = 0; i < keys.length; i++) {
      clearInterval(activeQRIntervals[keys[i]].countdown);
      clearInterval(activeQRIntervals[keys[i]].refresh);
    }
    activeQRIntervals = {};
  }

  // Handle slide changes — only generate QR when the slide is active
  function onSlideChanged(event) {
    stopAllIntervals();

    var currentSlide = event.currentSlide || (Reveal && Reveal.getCurrentSlide ? Reveal.getCurrentSlide() : null);
    if (!currentSlide) return;

    var qrContainers = currentSlide.querySelectorAll('.attendance-qr');
    for (var i = 0; i < qrContainers.length; i++) {
      renderQR(qrContainers[i]);
    }
  }

  // Show section selector if no section detected
  function showSectionPrompt() {
    if (currentSection) return;

    // Create overlay prompt
    var overlay = document.createElement('div');
    overlay.id = 'section-prompt-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';

    overlay.innerHTML = '<div style="background:white;padding:40px;border-radius:15px;text-align:center;max-width:400px;">' +
      '<h2 style="margin-bottom:20px;color:#2c3e50;">Select Section</h2>' +
      '<p style="color:#666;margin-bottom:20px;">Which section are you teaching?</p>' +
      '<button id="pick-section-a" style="padding:15px 30px;margin:8px;border:none;border-radius:10px;font-size:1.1rem;font-weight:bold;cursor:pointer;background:linear-gradient(45deg,#667eea,#764ba2);color:white;">Section A<br><small>10:00 - 11:30</small></button>' +
      '<button id="pick-section-b" style="padding:15px 30px;margin:8px;border:none;border-radius:10px;font-size:1.1rem;font-weight:bold;cursor:pointer;background:linear-gradient(45deg,#28a745,#20c997);color:white;">Section B<br><small>11:30 - 13:00</small></button>' +
      '</div>';

    document.body.appendChild(overlay);

    document.getElementById('pick-section-a').addEventListener('click', function() {
      currentSection = 'A';
      overlay.remove();
    });
    document.getElementById('pick-section-b').addEventListener('click', function() {
      currentSection = 'B';
      overlay.remove();
    });
  }

  // Initialize when Reveal.js is ready
  function init() {
    showSectionPrompt();

    if (typeof Reveal !== 'undefined') {
      if (Reveal.isReady && Reveal.isReady()) {
        // Already ready
        Reveal.on('slidechanged', onSlideChanged);
        // Check current slide
        onSlideChanged({ currentSlide: Reveal.getCurrentSlide() });
      } else {
        Reveal.on('ready', function() {
          Reveal.on('slidechanged', onSlideChanged);
          onSlideChanged({ currentSlide: Reveal.getCurrentSlide() });
        });
      }
    }
  }

  // Wait for DOM and QRCode library
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // Small delay to ensure Reveal.js is initialized
    setTimeout(init, 500);
  }

})();
