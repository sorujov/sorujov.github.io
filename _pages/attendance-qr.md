---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<!-- Cache buster: v2.0 - Inline QR Generator -->
<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>
  
  <div id="qr-container" style="margin: 20px auto; padding: 10px; border: 3px solid #667eea; border-radius: 10px; display: inline-block; background: white; min-width: 256px; min-height: 256px;"></div>
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;">Initializing...</p>
  
  <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; max-width: 400px; margin-left: auto; margin-right: auto;">
    <p><strong>Instructions:</strong></p>
    <ul style="text-align: left;">
      <li>Display this page in fullscreen (F11)</li>
      <li>Students scan the QR code</li>
      <li>QR refreshes every 30 seconds</li>
      <li>Ensure you're on ADA campus WiFi</li>
    </ul>
  </div>
</div>

<script>
(function() {
  'use strict';
  
  var QR_REFRESH_MS = 30000;
  var CLASS_ID = 'STAT2311-F25';
  var qrContainer = document.getElementById('qr-container');
  var statusEl = document.getElementById('qr-status');
  
  function waitForLibrary(callback) {
    if (typeof qrcode !== 'undefined') {
      callback();
    } else {
      setTimeout(function() { waitForLibrary(callback); }, 100);
    }
  }
  
  function generateQR(text) {
    try {
      // Create QR using qrcode-generator library
      var qr = qrcode(0, 'H'); // Type 0 (auto), High error correction
      qr.addData(text);
      qr.make();
      
      // Create image from QR
      var cellSize = 8;
      var margin = cellSize * 2;
      var size = qr.getModuleCount();
      var totalSize = size * cellSize + margin * 2;
      
      // Create SVG
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', totalSize);
      svg.setAttribute('height', totalSize);
      svg.setAttribute('viewBox', '0 0 ' + totalSize + ' ' + totalSize);
      
      // White background
      var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      bg.setAttribute('width', totalSize);
      bg.setAttribute('height', totalSize);
      bg.setAttribute('fill', '#ffffff');
      svg.appendChild(bg);
      
      // Draw QR modules
      for (var row = 0; row < size; row++) {
        for (var col = 0; col < size; col++) {
          if (qr.isDark(row, col)) {
            var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', (col * cellSize + margin).toString());
            rect.setAttribute('y', (row * cellSize + margin).toString());
            rect.setAttribute('width', cellSize.toString());
            rect.setAttribute('height', cellSize.toString());
            rect.setAttribute('fill', '#000000');
            svg.appendChild(rect);
          }
        }
      }
      
      qrContainer.innerHTML = '';
      qrContainer.appendChild(svg);
      return true;
    } catch (e) {
      console.error('QR generation error:', e);
      return false;
    }
  }
  
  function refreshQR() {
    try {
      var timestamp = Date.now();
      var token = btoa(timestamp + '-' + CLASS_ID);
      var url = location.origin + '/attend/math-stat-1/?tok=' + encodeURIComponent(token);
      
      console.log('Generating QR for:', url);
      
      if (generateQR(url)) {
        statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
        statusEl.style.color = '#28a745';
        console.log('QR generated successfully!');
      } else {
        statusEl.textContent = '⚠ Error generating QR';
        statusEl.style.color = '#dc3545';
      }
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error('Refresh error:', e);
    }
  }
  
  // Wait for library to load, then start
  waitForLibrary(function() {
    console.log('QR library loaded!');
    refreshQR();
    setInterval(refreshQR, QR_REFRESH_MS);
  });
})();
</script>
