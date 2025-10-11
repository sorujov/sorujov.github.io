---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>
  
  <canvas id="qr" style="margin: 20px auto; border: 3px solid #667eea; padding: 10px; border-radius: 10px; display: block;"></canvas>
  <p id="qr-status" style="color: #667eea; font-weight: bold;"></p>
  
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
  console.log('Page loaded, checking QRious library...');
  
  const QR_REFRESH_MS = 30000; // 30 seconds
  const CLASS_ID = 'STAT2311-F25';
  
  const qrCanvas = document.getElementById('qr');
  const statusEl = document.getElementById('qr-status');
  let qr = null;
  
  // Check if QRious is available
  if (typeof QRious === 'undefined') {
    statusEl.textContent = '⚠ QR library not loaded. Check console for errors.';
    console.error('QRious library not found. Make sure qrious.min.js is loaded.');
    return;
  }
  
  console.log('QRious library found!');
  
  // Initialize QRious (CSP-safe, no eval)
  qr = new QRious({
    element: qrCanvas,
    size: 256,
    level: 'H'
  });
  
  function refreshQR() {
    try {
      // Generate simple token for testing
      const timestamp = Date.now();
      const token = btoa(timestamp + '-' + CLASS_ID);
      
      const url = `${location.origin}/attend/math-stat-1/?tok=${encodeURIComponent(token)}`;
      
      console.log('Generating QR for:', url);
      
      // Update QR code value
      qr.value = url;
      
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
