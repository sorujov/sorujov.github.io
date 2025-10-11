---
layout: single
title: "QR Test - Jekyll"
permalink: /test-qr-jekyll/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h1>Jekyll QR Test</h1>
  
  <div id="qr-container" style="margin: 20px auto; padding: 10px; border: 3px solid #667eea; border-radius: 10px; display: inline-block; background: white;"></div>
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;">Loading...</p>
  
  <button onclick="testQR()">Generate Test QR</button>
  
  <div style="margin-top: 20px;">
    <h3>Debug Info:</h3>
    <div id="debug-info" style="background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; text-align: left; max-width: 600px; margin: 0 auto;"></div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  'use strict';
  
  var qrContainer = document.getElementById('qr-container');
  var statusEl = document.getElementById('qr-status');
  var debugEl = document.getElementById('debug-info');
  
  function debug(msg) {
    console.log(msg);
    if (debugEl) {
      debugEl.innerHTML += msg + '<br>';
    }
  }
  
  debug('Script started');
  debug('Current URL: ' + window.location.href);
  
  function waitForLib(callback) {
    var attempts = 0;
    function check() {
      attempts++;
      debug('Checking for qrcodegen... attempt ' + attempts + ' - type: ' + typeof qrcodegen);
      if (typeof qrcodegen !== 'undefined') {
        debug('✅ qrcodegen found!');
        debug('QrCode available: ' + (qrcodegen.QrCode ? 'YES' : 'NO'));
        debug('Ecc available: ' + (qrcodegen.QrCode && qrcodegen.QrCode.Ecc ? 'YES' : 'NO'));
        callback();
      } else if (attempts < 50) {
        setTimeout(check, 100);
      } else {
        debug('❌ qrcodegen not found after 5 seconds');
        if (statusEl) {
          statusEl.textContent = '❌ Library failed to load';
          statusEl.style.color = '#dc3545';
        }
      }
    }
    check();
  }
  
  // Create global testQR function
  window.testQR = function() {
    debug('=== Testing QR Generation ===');
    try {
      if (typeof qrcodegen === 'undefined') {
        debug('❌ qrcodegen not available');
        return;
      }
      
      var testUrl = 'https://sorujov.github.io/attend/math-stat-1/?tok=' + btoa(Date.now() + '-STAT2311-F25');
      debug('Test URL: ' + testUrl);
      
      var qr = qrcodegen.QrCode.encodeText(testUrl, qrcodegen.QrCode.Ecc.HIGH);
      debug('✅ QR created successfully, size: ' + qr.size);
      
      // Simple rendering
      var cellSize = 8;
      var border = 4;
      var size = qr.size;
      var totalSize = (size + border * 2) * cellSize;
      
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('width', totalSize);
      svg.setAttribute('height', totalSize);
      
      // White background
      var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      bg.setAttribute('width', totalSize);
      bg.setAttribute('height', totalSize);
      bg.setAttribute('fill', '#ffffff');
      svg.appendChild(bg);
      
      // Draw modules
      for (var y = 0; y < size; y++) {
        for (var x = 0; x < size; x++) {
          if (qr.getModule(x, y)) {
            var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', (x + border) * cellSize);
            rect.setAttribute('y', (y + border) * cellSize);
            rect.setAttribute('width', cellSize);
            rect.setAttribute('height', cellSize);
            rect.setAttribute('fill', '#000000');
            svg.appendChild(rect);
          }
        }
      }
      
      if (qrContainer) {
        qrContainer.innerHTML = '';
        qrContainer.appendChild(svg);
      }
      
      if (statusEl) {
        statusEl.textContent = '✅ QR Generated Successfully!';
        statusEl.style.color = '#28a745';
      }
      debug('✅ SVG rendered successfully');
      
    } catch (e) {
      debug('❌ ERROR: ' + e.message);
      if (statusEl) {
        statusEl.textContent = '❌ Error: ' + e.message;
        statusEl.style.color = '#dc3545';
      }
    }
  };
  
  // Wait for library load
  setTimeout(function() {
    debug('Checking for script after 1 second...');
    waitForLib(function() {
      debug('✅ Library ready!');
      if (statusEl) {
        statusEl.textContent = 'Library loaded! Click button to test.';
        statusEl.style.color = '#28a745';
      }
    });
  }, 1000);
});
</script>