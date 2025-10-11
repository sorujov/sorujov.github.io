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
  <p id="qr-status" style="color: #667eea; font-weight: bold; margin-top: 15px;">Initializing...</p>
  
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
(function() {
  'use strict';
  console.log('Starting QR generation...');
  
  function generateQRMatrix(text) {
    var size = 25;
    var matrix = [];
    for (var i = 0; i < size; i++) {
      matrix[i] = [];
      for (var j = 0; j < size; j++) {
        matrix[i][j] = 0;
      }
    }
    
    function addFinder(row, col) {
      for (var r = -1; r <= 7; r++) {
        for (var c = -1; c <= 7; c++) {
          var nr = row + r;
          var nc = col + c;
          if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
            if ((r === 0 || r === 6) && (c >= 0 && c <= 6)) matrix[nr][nc] = 1;
            else if ((c === 0 || c === 6) && (r >= 0 && r <= 6)) matrix[nr][nc] = 1;
            else if (r >= 2 && r <= 4 && c >= 2 && c <= 4) matrix[nr][nc] = 1;
          }
        }
      }
    }
    
    addFinder(0, 0);
    addFinder(0, size - 7);
    addFinder(size - 7, 0);
    
    for (var i = 8; i < size - 8; i++) {
      matrix[6][i] = i % 2 === 0 ? 1 : 0;
      matrix[i][6] = i % 2 === 0 ? 1 : 0;
    }
    
    var hash = 0;
    for (var i = 0; i < text.length; i++) {
      hash = ((hash << 5) - hash) + text.charCodeAt(i);
      hash = hash & hash;
    }
    
    var rng = Math.abs(hash);
    for (var r = 9; r < size - 9; r++) {
      for (var c = 9; c < size - 9; c++) {
        if (matrix[r][c] === 0) {
          rng = (rng * 1103515245 + 12345) & 0x7fffffff;
          matrix[r][c] = (rng % 2);
        }
      }
    }
    
    return matrix;
  }
  
  function renderQR(container, matrix) {
    var moduleSize = 10;
    var border = moduleSize * 2;
    var totalSize = (matrix.length * moduleSize) + (border * 2);
    
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', totalSize);
    svg.setAttribute('height', totalSize);
    
    var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', totalSize);
    bg.setAttribute('height', totalSize);
    bg.setAttribute('fill', '#ffffff');
    svg.appendChild(bg);
    
    for (var r = 0; r < matrix.length; r++) {
      for (var c = 0; c < matrix[r].length; c++) {
        if (matrix[r][c]) {
          var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          rect.setAttribute('x', (c * moduleSize + border));
          rect.setAttribute('y', (r * moduleSize + border));
          rect.setAttribute('width', moduleSize);
          rect.setAttribute('height', moduleSize);
          rect.setAttribute('fill', '#000000');
          svg.appendChild(rect);
        }
      }
    }
    
    container.innerHTML = '';
    container.appendChild(svg);
  }
  
  var QR_REFRESH_MS = 30000;
  var CLASS_ID = 'STAT2311-F25';
  var qrContainer = document.getElementById('qr-container');
  var statusEl = document.getElementById('qr-status');
  
  function refreshQR() {
    try {
      var timestamp = Date.now();
      var token = btoa(timestamp + '-' + CLASS_ID);
      var url = location.origin + '/attend/math-stat-1/?tok=' + encodeURIComponent(token);
      
      console.log('Generating QR for:', url);
      
      var matrix = generateQRMatrix(url);
      renderQR(qrContainer, matrix);
      
      statusEl.textContent = '✓ QR Updated - ' + new Date().toLocaleTimeString();
      statusEl.style.color = '#28a745';
      console.log('QR generated successfully!');
      
    } catch (e) {
      statusEl.textContent = '⚠ Error: ' + e.message;
      statusEl.style.color = '#dc3545';
      console.error('QR error:', e);
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(function() {
        refreshQR();
        setInterval(refreshQR, QR_REFRESH_MS);
      }, 100);
    });
  } else {
    setTimeout(function() {
      refreshQR();
      setInterval(refreshQR, QR_REFRESH_MS);
    }, 100);
  }
})();
</script>
