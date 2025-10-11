---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>

  <div id="qr-container" style="margin: 20px auto; padding: 10px; border: 3px solid #667eea; border-radius: 10px; display: inline-block; background: white;"></div>
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;">Loading...</p>

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
  
  function waitForLib(callback) {
    if (typeof qrcode !== 'undefined') {
      callback();
    } else {
      setTimeout(function() { waitForLib(callback); }, 100);
    }
  }
  
  function drawQR(text) {
    try {
      // Create QR Code using qrcode-generator library
      var qr = qrcode(0, 'H'); // Type 0 (auto-detect), High error correction
      qr.addData(text);
      qr.make();
      
      // Render as SVG
      var cellSize = 8;
      var border = 4;
      var size = qr.getModuleCount();
      var totalSize = (size + border * 2) * cellSize;
      
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
      for (var y = 0; y < size; y++) {
        for (var x = 0; x < size; x++) {
          if (qr.isDark(y, x)) {
            var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', ((x + border) * cellSize).toString());
            rect.setAttribute('y', ((y + border) * cellSize).toString());
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
      
      console.log('Generating QR:', url);
      
      if (drawQR(url)) {
        statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
        statusEl.style.color = '#28a745';
      } else {
        statusEl.textContent = '⚠ Generation failed';
        statusEl.style.color = '#dc3545';
      }
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error(e);
    }
  }
  
  // Wait for library, then start
  waitForLib(function() {
    console.log('QR library loaded successfully');
    refreshQR();
    setInterval(refreshQR, QR_REFRESH_MS);
  });
})();
</script>
