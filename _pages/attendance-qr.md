---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>

  <div id="qr-container" style="margin: 20px auto; padding: 10px; border: 3px solid #667eea; border-radius: 10px; display: inline-block; background: white;">
    <img id="qr-image" src="" alt="QR Code" style="display: block;">
  </div>
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
  
  var QR_REFRESH_MS = 30000;
  var qrImage = document.getElementById('qr-image');
  var statusEl = document.getElementById('qr-status');
  
  if (!qrImage || !statusEl) {
    console.error('Required elements not found');
    return;
  }
  
  function generateQR(url) {
    // Use Google Chart API to generate QR code
    var encodedUrl = encodeURIComponent(url);
    var qrUrl = 'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=' + encodedUrl + '&choe=UTF-8';
    qrImage.src = qrUrl;
    qrImage.style.width = '300px';
    qrImage.style.height = '300px';
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
      
      generateQR(formUrl);
      statusEl.textContent = '✓ QR Updated - ' + timeStr;
      statusEl.style.color = '#28a745';
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error('Refresh error:', e);
    }
  }
  
  // Generate first QR immediately
  statusEl.textContent = 'Generating QR...';
  refreshQR();
  
  // Set up interval for refreshing every 30 seconds
  setInterval(refreshQR, QR_REFRESH_MS);
});
</script>
