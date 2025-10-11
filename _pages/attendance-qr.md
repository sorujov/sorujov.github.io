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
  console.log('Page loaded, checking CSP-safe QR library...');
  
  const QR_REFRESH_MS = 30000; // 30 seconds
  const CLASS_ID = 'STAT2311-F25';
  
  const qrContainer = document.getElementById('qr-container');
  const statusEl = document.getElementById('qr-status');
  
  // Check if our CSP-safe library is available
  if (typeof CSPSafeQR === 'undefined') {
    statusEl.textContent = '⚠ QR library not loaded. Check console.';
    console.error('CSP-safe QR library not found.');
    return;
  }
  
  console.log('CSP-safe QR library found!');
  
  function generateQR(text) {
    try {
      // Clear previous QR
      qrContainer.innerHTML = '';
      
      // Generate QR code using our CSP-safe library
      console.log('Creating QR for text:', text);
      const qr = CSPSafeQR.create(text, { errorCorrectLevel: 'H' });
      
      // Create SVG element
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      const size = 256;
      const border = 4;
      const qrSize = qr.size;
      const scale = (size - border * 2) / qrSize;
      
      svg.setAttribute('width', size);
      svg.setAttribute('height', size);
      svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
      svg.style.display = 'block';
      
      // White background
      const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      bg.setAttribute('width', size);
      bg.setAttribute('height', size);
      bg.setAttribute('fill', '#ffffff');
      svg.appendChild(bg);
      
      // Draw QR modules
      for (let y = 0; y < qrSize; y++) {
        for (let x = 0; x < qrSize; x++) {
          if (qr.isDark(y, x)) {
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', (x * scale + border).toString());
            rect.setAttribute('y', (y * scale + border).toString());
            rect.setAttribute('width', scale.toString());
            rect.setAttribute('height', scale.toString());
            rect.setAttribute('fill', '#000000');
            svg.appendChild(rect);
          }
        }
      }
      
      qrContainer.appendChild(svg);
      console.log('QR SVG created successfully');
      return true;
    } catch (e) {
      console.error('QR generation error:', e);
      return false;
    }
  }
  
  function refreshQR() {
    try {
      // Generate token
      const timestamp = Date.now();
      const token = btoa(timestamp + '-' + CLASS_ID);
      const url = `${location.origin}/attend/math-stat-1/?tok=${encodeURIComponent(token)}`;
      
      console.log('Generating QR for URL:', url);
      
      if (generateQR(url)) {
        statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
        console.log('QR code generated successfully');
      } else {
        statusEl.textContent = '⚠ Error generating QR';
      }
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      console.error('Refresh error:', e);
    }
  }
  
  // Initial generation
  refreshQR();
  
  // Refresh every 30 seconds
  setInterval(refreshQR, QR_REFRESH_MS);
});
</script>
