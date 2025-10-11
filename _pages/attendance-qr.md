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
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;"></p>
  
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
window.addEventListener('load', function() {
  console.log('Initializing simple QR system...');
  
  const QR_REFRESH_MS = 30000;
  const CLASS_ID = 'STAT2311-F25';
  const qrContainer = document.getElementById('qr-container');
  const statusEl = document.getElementById('qr-status');
  
  if (typeof SimpleQR === 'undefined') {
    statusEl.textContent = '⚠ QR module loading...';
    console.error('SimpleQR not found');
    return;
  }
  
  console.log('SimpleQR found!');
  
  function refreshQR() {
    try {
      const timestamp = Date.now();
      const token = btoa(timestamp + '-' + CLASS_ID);
      const url = location.origin + '/attend/math-stat-1/?tok=' + encodeURIComponent(token);
      
      console.log('Generating QR:', url);
      
      SimpleQR.generate(qrContainer, url, 256);
      statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
      console.log('QR generated successfully');
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      console.error('QR error:', e);
    }
  }
  
  refreshQR();
  setInterval(refreshQR, QR_REFRESH_MS);
});
</script>
