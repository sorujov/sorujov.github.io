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
// Wait for page to fully load and QRCode library
window.addEventListener('load', function() {
  console.log('Page loaded, checking QRCode library...');
  
  const QR_REFRESH_MS = 30000; // 30 seconds
  const CLASS_ID = 'STAT2311-F25';
  
  const qrEl = document.getElementById('qr');
  const statusEl = document.getElementById('qr-status');
  let qr = null;
  
  // Check if QRCode is available
  if (typeof QRCode === 'undefined') {
    statusEl.textContent = '⚠ QR library not loaded. Check console for errors.';
    console.error('QRCode library not found. Make sure qrcode.min.js is loaded.');
    return;
  }
  
  console.log('QRCode library found!');
  
  function refreshQR() {
    try {
      // Generate simple token for testing
      const timestamp = Date.now();
      const token = btoa(timestamp + '-' + CLASS_ID);
      
      const url = `${location.origin}/attend/math-stat-1/?tok=${encodeURIComponent(token)}`;
      
      console.log('Generating QR for:', url);
      
      if (!qr) {
        qr = new QRCode(qrEl, { 
          width: 256, 
          height: 256,
          colorDark: "#000000",
          colorLight: "#ffffff",
          correctLevel: QRCode.CorrectLevel.H
        });
      }
      qr.clear();
      qr.makeCode(url);
      
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
