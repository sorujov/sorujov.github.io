---
layout: minimal
title: "Mathematical Statistics II - Attendance"
permalink: /attendance/math-stat-2/
---

<div id="qrcode-container" style="display: block; text-align: center; padding: 20px;">

  <h2 style="margin-bottom: 10px;">📊 Math Stat II — Attendance QR</h2>

  <!-- Section Selector -->
  <div id="section-selector" style="margin: 15px 0; display: flex; justify-content: center; gap: 10px;">
    <button id="btn-section-a" onclick="selectSection('A')" style="
      padding: 12px 24px;
      border: 2px solid #667eea;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s;
      background: #667eea;
      color: white;
    ">Section A (10:00-11:30)</button>
    <button id="btn-section-b" onclick="selectSection('B')" style="
      padding: 12px 24px;
      border: 2px solid #764ba2;
      border-radius: 10px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s;
      background: white;
      color: #764ba2;
    ">Section B (11:30-13:00)</button>
  </div>

  <!-- Status Toggle -->
  <div id="status-toggle" style="margin: 10px 0; display: flex; justify-content: center; gap: 10px;">
    <button id="btn-present" onclick="selectStatus('present')" style="
      padding: 8px 20px;
      border: 2px solid #28a745;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s;
      background: #28a745;
      color: white;
    ">✓ Present</button>
    <button id="btn-late" onclick="selectStatus('late')" style="
      padding: 8px 20px;
      border: 2px solid #ffc107;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: bold;
      cursor: pointer;
      transition: all 0.2s;
      background: white;
      color: #856404;
    ">⏰ Late</button>
  </div>

  <button id="fullscreen-btn" title="Toggle Fullscreen (F11)" style="
    position: fixed;
    top: 10px;
    right: 10px;
    font-size: 24px;
    background: rgba(0,0,0,0.1);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    z-index: 9999;
  ">⛶</button>

  <div id="qrcode" style="margin: 20px auto;"></div>
  <div id="timer" style="font-size: 1.1rem; color: #666;">Next refresh in: <span id="countdown">120</span>s</div>
  <p class="session-info" style="color: #888; font-size: 0.9rem;">
    Session: <span id="session-time"></span>
  </p>
</div>

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>
<script>
(function() {
  'use strict';

  var PASSWORD = 'so123!';
  var QR_REFRESH_MS = 120000; // 2 minutes

  var currentSection = 'A';
  var currentStatus = 'present';

  var qrcodeContainer = document.getElementById('qrcode');
  var sessionTimeDisplay = document.getElementById('session-time');
  var countdownDisplay = document.getElementById('countdown');
  var countdownInterval;
  var refreshInterval;

  // Auto-detect section based on current time (Baku = UTC+4)
  function autoDetectSection() {
    var now = new Date();
    // Get Baku time
    var utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    var bakuTime = new Date(utc + (4 * 3600000));
    var hours = bakuTime.getHours();
    var minutes = bakuTime.getMinutes();
    var totalMinutes = hours * 60 + minutes;

    if (totalMinutes >= 600 && totalMinutes <= 690) {
      // 10:00 - 11:30
      return 'A';
    } else if (totalMinutes >= 690 && totalMinutes <= 780) {
      // 11:30 - 13:00
      return 'B';
    }
    return 'A'; // Default
  }

  currentSection = autoDetectSection();
  updateSectionButtons();

  function selectSection(sec) {
    currentSection = sec;
    updateSectionButtons();
    generateQR();
  }

  function selectStatus(status) {
    currentStatus = status;
    updateStatusButtons();
    generateQR();
  }

  // Make functions available globally for onclick handlers
  window.selectSection = selectSection;
  window.selectStatus = selectStatus;

  function updateSectionButtons() {
    var btnA = document.getElementById('btn-section-a');
    var btnB = document.getElementById('btn-section-b');

    if (currentSection === 'A') {
      btnA.style.background = '#667eea';
      btnA.style.color = 'white';
      btnB.style.background = 'white';
      btnB.style.color = '#764ba2';
    } else {
      btnA.style.background = 'white';
      btnA.style.color = '#667eea';
      btnB.style.background = '#764ba2';
      btnB.style.color = 'white';
    }
  }

  function updateStatusButtons() {
    var btnPresent = document.getElementById('btn-present');
    var btnLate = document.getElementById('btn-late');

    if (currentStatus === 'present') {
      btnPresent.style.background = '#28a745';
      btnPresent.style.color = 'white';
      btnLate.style.background = 'white';
      btnLate.style.color = '#856404';
    } else {
      btnPresent.style.background = 'white';
      btnPresent.style.color = '#28a745';
      btnLate.style.background = '#ffc107';
      btnLate.style.color = '#856404';
    }
  }

  function generateQR() {
    try {
      qrcodeContainer.innerHTML = '';
      if (countdownInterval) clearInterval(countdownInterval);

      var now = new Date();
      var dateStr = now.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
      var timeStr = now.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
      var sessionInfo = dateStr + ' ' + timeStr;
      sessionTimeDisplay.textContent = sessionInfo + ' | Section ' + currentSection + ' | ' + (currentStatus === 'late' ? 'Late' : 'Present');

      var currentSessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      var timestamp = now.getTime();
      var token = btoa(timestamp + ':' + currentSessionId + ':' + PASSWORD).replace(/[+/=]/g, '');

      sessionStorage.setItem('currentQRSession', currentSessionId);

      var baseUrl = window.location.origin + '/attend/math-stat-2/';
      var attendUrl = baseUrl + '?session=' + encodeURIComponent(sessionInfo) +
                      '&token=' + token +
                      '&section=' + currentSection +
                      '&status=' + currentStatus;

      var qrSize = Math.min(window.innerWidth * 0.7, window.innerHeight * 0.55, 800);
      new QRCode(qrcodeContainer, {
        text: attendUrl,
        width: qrSize,
        height: qrSize,
        correctLevel: QRCode.CorrectLevel.H
      });

      var secondsLeft = 120;
      countdownDisplay.textContent = secondsLeft;

      countdownInterval = setInterval(function() {
        secondsLeft--;
        countdownDisplay.textContent = secondsLeft;
        if (secondsLeft <= 0) {
          clearInterval(countdownInterval);
        }
      }, 1000);

    } catch (e) {
      console.error('QR generation error:', e);
      sessionTimeDisplay.textContent = 'Error: ' + e.message;
    }
  }

  // Initial QR generation
  generateQR();

  // Auto-refresh every 2 minutes
  refreshInterval = setInterval(generateQR, QR_REFRESH_MS);

  // Fullscreen toggle
  document.getElementById('fullscreen-btn').addEventListener('click', function() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  });

})();
</script>

<style>
  body { background: #fafafa; }
  #qrcode-container { max-width: 900px; margin: 0 auto; }
  #qrcode canvas, #qrcode img { margin: 0 auto; display: block !important; }
</style>
