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
const QR_REFRESH_MS = 30000; // 30 seconds
const CLASS_ID = 'STAT2311-F25'; // Change per class/semester
const BACKEND_MINT_URL = 'YOUR_BACKEND_MINT_ENDPOINT?class=' + CLASS_ID;

const qrEl = document.getElementById('qr');
const statusEl = document.getElementById('qr-status');
let qr = null;

async function refreshQR() {
  try {
    // For testing without backend, generate a simple token
    const token = btoa(Date.now() + '-' + CLASS_ID);
    
    // Replace with actual backend call:
    // const r = await fetch(BACKEND_MINT_URL, { credentials: 'omit' });
    // const data = await r.json();
    // const token = data.token;
    
    const url = `${location.origin}/attend/math-stat-1/?tok=${encodeURIComponent(token)}`;
    
    if (!qr) {
      qr = new QRCode(qrEl, { width: 256, height: 256 });
    }
    qr.clear();
    qr.makeCode(url);
    statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
  } catch (e) {
    statusEl.textContent = '⚠ Error updating QR';
    console.error(e);
  }
}

// Initial load and refresh interval
if (typeof QRCode !== 'undefined') {
  refreshQR();
  setInterval(refreshQR, QR_REFRESH_MS);
} else {
  statusEl.textContent = '⚠ QR library not loaded';
}
</script>
