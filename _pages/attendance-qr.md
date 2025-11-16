---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>

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
  var currentQR = null;
  
  if (!qrContainer || !statusEl) {
    console.error('Required elements not found');
    return;
  }
  
  function waitForLib(callback) {
    var attempts = 0;
    function check() {
      attempts++;
      console.log('Checking for QRCode library, attempt', attempts, '- type:', typeof QRCode);
      
      if (typeof QRCode !== 'undefined') {
        console.log('✅ QRCode found!', QRCode);
        callback();
      } else if (attempts < 50) {
        setTimeout(check, 100);
      } else {
        console.error('❌ QRCode library failed to load after 5 seconds');
        statusEl.textContent = '❌ Library failed to load';
        statusEl.style.color = '#dc3545';
      }
    }
    check();
  }
  
  function drawQR(text) {
    try {
      console.log('Creating QR for:', text);
      
      // Clear previous QR
      qrContainer.innerHTML = '';
      
      // Create new QR Code
      currentQR = new QRCode(qrContainer, {
        text: text,
        width: 256,
        height: 256,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
      });
      
      console.log('✅ QR created successfully');
      return true;
      
    } catch (e) {
      console.error('QR generation error:', e);
      return false;
    }
  }
  
  function refreshQR() {
    try {
      var now = new Date();
      var dateStr = now.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
      var timeStr = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
      var sessionInfo = dateStr + ' ' + timeStr;
      
      // Google Form URL with timestamp (entry.303810813 is Session Date/Time field)
      var formUrl = 'https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform?usp=pp_url&entry.303810813=' + encodeURIComponent(sessionInfo);
      
      if (drawQR(formUrl)) {
        statusEl.textContent = '✓ QR Updated - ' + timeStr;
        statusEl.style.color = '#28a745';
        console.log('✅ QR refreshed successfully for session:', sessionInfo);
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
    console.log('✅ QRCode library loaded successfully');
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
