---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>
  
  <div id="qr" style="width:256px; height:256px; margin:20px auto; border: 3px solid #667eea; padding: 10px; border-radius: 10px;"></div>
  <p id="qr-status" style="color: #667eea; font-weight: bold;"></p>
  
  <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
    <p><strong>Instructions:</strong></p>
    <ul style="text-align: left; display: inline-block;">
      <li>Display this page in fullscreen (F11)</li>
      <li>Students scan the QR code</li>
      <li>QR refreshes every 30 seconds</li>
      <li>Ensure you're on ADA campus WiFi</li>
    </ul>
  </div>
</div>

<script>
// Wait for page to fully load and QRious library
window.addEventListener('load', function() {
  console.log('Page loaded, checking QRious library...');
  
  const QR_REFRESH_MS = 30000; // 30 seconds
  const CLASS_ID = 'STAT2311-F25';
  
  const qrEl = document.getElementById('qr');
  const statusEl = document.getElementById('qr-status');
  let qr = null;
  
  // Check if QRious library is available
  if (typeof QRious === 'undefined') {
    statusEl.textContent = '⚠ QRious library not loaded. Check console for errors.';
    console.error('QRious library not found. Make sure qrious.min.js is loaded.');
    return;
  }
  
  console.log('QRious library found!');
  
  function refreshQR() {
    try {
      // Generate simple token for testing
      const timestamp = Date.now();
      const token = btoa(timestamp + '-' + CLASS_ID);
      
      const url = `${location.origin}/attend/math-stat-1/?tok=${encodeURIComponent(token)}`;
      
      console.log('Generating QR for:', url);
      
      // Clear previous QR and create new one
      qrEl.innerHTML = '';
      
      // Create canvas element for QRious
      const canvas = document.createElement('canvas');
      qrEl.appendChild(canvas);
      
      qr = new QRious({
        element: canvas,
        size: 256,
        level: 'H',
        background: 'white',
        foreground: 'black',
        value: url
      });
      
      statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
      console.log('QR code generated successfully');
    } catch (e) {
      statusEl.textContent = '⚠ Error generating QR';
      console.error('QR generation error:', e);
    }
  }
  
  // Initial generation
  refreshQR();
  
  // Refresh every 30 seconds
  setInterval(refreshQR, QR_REFRESH_MS);
});
</script>
