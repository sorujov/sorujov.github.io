---
layout: minimal
title: "Mathematical Statistics I - Attendance"
permalink: /attendance/math-stat-1/
---

<div id="qrcode-container">
    <h2>📊 Scan for Attendance</h2>
    <div id="qrcode"></div>
    <div id="timer">Next refresh in: <span id="countdown">30</span>s</div>
    <p class="session-info">
        Session: <span id="session-time"></span>
    </p>
    <div class="instructions">
        <strong>Instructions:</strong>
        <ul>
            <li>Display this page in fullscreen (F11)</li>
            <li>Students scan the QR code with phone</li>
            <li>QR auto-refreshes every 30 seconds</li>
            <li>Form opens with session time pre-filled</li>
        </ul>
    </div>
</div>

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>
<script>
(function() {
    'use strict';
    
    var QR_REFRESH_MS = 30000;
    var qrcodeContainer = document.getElementById("qrcode");
    var sessionTimeDisplay = document.getElementById("session-time");
    var countdownDisplay = document.getElementById("countdown");
    var countdownInterval;

    function generateQR() {
        try {
            // Clear previous QR and countdown
            qrcodeContainer.innerHTML = "";
            if (countdownInterval) clearInterval(countdownInterval);
            
            // Get current timestamp
            var now = new Date();
            var dateStr = now.toLocaleDateString('en-US', {
                month: 'short', 
                day: 'numeric', 
                year: 'numeric'
            });
            var timeStr = now.toLocaleTimeString('en-US', {
                hour: 'numeric', 
                minute: '2-digit', 
                hour12: true
            });
            var sessionInfo = dateStr + ' ' + timeStr;
            
            // Update display
            sessionTimeDisplay.textContent = sessionInfo;
            
            // Build Google Form URL with pre-filled session time
            var formUrl = 'https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform?usp=pp_url&entry.303810813=' + encodeURIComponent(sessionInfo);
            
            // Generate QR code - LARGE for projection
            var qrSize = Math.min(window.innerWidth * 0.7, window.innerHeight * 0.7, 800);
            new QRCode(qrcodeContainer, {
                text: formUrl,
                width: qrSize,
                height: qrSize,
                correctLevel: QRCode.CorrectLevel.H
            });
            
            // Countdown timer
            var secondsLeft = 30;
            countdownDisplay.textContent = secondsLeft;
            
            countdownInterval = setInterval(function() {
                secondsLeft--;
                countdownDisplay.textContent = secondsLeft;
                if (secondsLeft <= 0) {
                    clearInterval(countdownInterval);
                }
            }, 1000);
            
        } catch (e) {
            console.error('QR generation error:', e);
            sessionTimeDisplay.textContent = 'Error: ' + e.message;
        }
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', generateQR);
    } else {
        generateQR();
    }

    // Refresh every 30 seconds
    setInterval(generateQR, QR_REFRESH_MS);
})();
</script>
