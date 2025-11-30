---
layout: minimal
title: "Mathematical Statistics I - Attendance"
permalink: /attendance/math-stat-1/
---

<div id="password-container" style="
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
">
    <div style="
        background: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        text-align: center;
        max-width: 400px;
    ">
        <div style="font-size: 64px; margin-bottom: 20px;">🔒</div>
        <h2 style="color: #667eea; margin-bottom: 20px;">Instructor Access Required</h2>
        <p style="color: #666; margin-bottom: 20px;">Please enter the password to access the attendance QR code.</p>
        <input type="password" id="password-input" placeholder="Enter password" style="
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
            box-sizing: border-box;
        " />
        <button id="password-submit" style="
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
        ">Access Attendance</button>
        <div id="password-error" style="
            color: #e74c3c;
            margin-top: 15px;
            font-size: 14px;
            display: none;
        ">Incorrect password. Please try again.</div>
    </div>
</div>

<div id="qrcode-container" style="display: none;">
    <button id="fullscreen-btn" title="Toggle Fullscreen (F11)">⛶</button>
    <h2>📊 Scan for Attendance</h2>
    <div id="qrcode"></div>
    <div id="timer">Next refresh in: <span id="countdown">30</span>s</div>
    <p class="session-info">
        Session: <span id="session-time"></span>
    </p>
</div>

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>
<script>
(function() {
    'use strict';
    
    var PASSWORD = 'so123!';
    
    // Password check
    function checkPassword() {
        var input = document.getElementById('password-input').value;
        var errorDiv = document.getElementById('password-error');
        
        if (input === PASSWORD) {
            document.getElementById('password-container').style.display = 'none';
            document.getElementById('qrcode-container').style.display = 'block';
            initQRCode();
        } else {
            errorDiv.style.display = 'block';
            document.getElementById('password-input').value = '';
        }
    }
    
    document.getElementById('password-submit').addEventListener('click', checkPassword);
    document.getElementById('password-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            checkPassword();
        }
    });
    
    var QR_REFRESH_MS = 30000;
    var qrcodeContainer = document.getElementById("qrcode");
    var sessionTimeDisplay = document.getElementById("session-time");
    var countdownDisplay = document.getElementById("countdown");
    var countdownInterval;

    function initQRCode() {
        generateQR();
        document.getElementById('fullscreen-btn').addEventListener('click', toggleFullscreen);
        setInterval(generateQR, QR_REFRESH_MS);
    }

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

    // Fullscreen toggle
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

})();
</script>
