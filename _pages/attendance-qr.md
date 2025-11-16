---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>

  <div id="qrcode" style="margin: 20px auto; padding: 20px; border: 3px solid #667eea; border-radius: 10px; display: inline-block; background: white;"></div>
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;">Generating...</p>

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
  
  var QR_REFRESH_MS = 30000;
  var qrcodeContainer = document.getElementById('qrcode');
  var statusEl = document.getElementById('qr-status');
  
  if (!qrcodeContainer || !statusEl) {
    console.error('Required elements not found');
    return;
  }
  
  function generateQR() {
    try {
      // Clear previous QR
      qrcodeContainer.innerHTML = '';
      
      // Get current timestamp
      var now = new Date();
      var dateStr = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
      var timeStr = now.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
      var sessionInfo = dateStr + ' ' + timeStr;
      
      // Build Google Form URL with pre-filled session time
      var formUrl = 'https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform?usp=pp_url&entry.303810813=' + encodeURIComponent(sessionInfo);
      
      // Generate QR code using locally hosted QRCode.js
      new QRCode(qrcodeContainer, {
        text: formUrl,
        width: 300,
        height: 300,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
      });
      
      statusEl.textContent = '✓ QR Updated - ' + timeStr;
      statusEl.style.color = '#28a745';
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error('QR generation error:', e);
    }
  }
  
  // Generate first QR immediately
  generateQR();
  
  // Refresh every 30 seconds
  setInterval(generateQR, QR_REFRESH_MS);
});
</script>
