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
document.addEventListener('DOMContentLoaded', function() {
  'use strict';
  
  console.log('DOM ready, starting QR system...');
  
  var QR_REFRESH_MS = 30000;
  var CLASS_ID = 'STAT2311-F25';
  var qrContainer = document.getElementById('qr-container');
  var statusEl = document.getElementById('qr-status');
  
  if (!qrContainer || !statusEl) {
    console.error('Required elements not found');
    return;
  }
  
  function waitForLib(callback) {
    var attempts = 0;
    function check() {
      attempts++;
      console.log('Checking for QRious library, attempt', attempts, '- type:', typeof QRious);
      
      if (typeof QRious !== 'undefined') {
        console.log('✅ QRious found!', QRious);
        callback();
      } else if (attempts < 50) { // Wait up to 5 seconds
        setTimeout(check, 100);
      } else {
        console.error('❌ QRious library failed to load after 5 seconds');
        statusEl.textContent = '❌ Library failed to load';
        statusEl.style.color = '#dc3545';
      }
    }
    check();
  }
  
  function drawQR(text) {
    try {
      console.log('Creating QR with QRious for:', text);
      
      // Create canvas element
      var canvas = document.createElement('canvas');
      
      // Create QR Code using QRious library
      var qr = new QRious({
        element: canvas,
        value: text,
        size: 256,
        level: 'H'
      });
      
      console.log('✅ QR created successfully');
      
      qrContainer.innerHTML = '';
      qrContainer.appendChild(canvas);
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
      
      if (drawQR(url)) {
        statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
        statusEl.style.color = '#28a745';
        console.log('✅ QR refreshed successfully');
      } else {
        statusEl.textContent = '⚠ Generation failed';
        statusEl.style.color = '#dc3545';
      }
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error('Refresh error:', e);
    }
  }
  
  // Wait for library, then start
  waitForLib(function() {
    console.log('✅ Nayuki QR library loaded successfully');
    statusEl.textContent = 'Generating first QR...';
    statusEl.style.color = '#667eea';
    
    // Generate first QR
    setTimeout(function() {
      refreshQR();
      // Set up interval for refreshing
      setInterval(refreshQR, QR_REFRESH_MS);
    }, 100);
  });
});
</script>
