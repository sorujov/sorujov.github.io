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
    <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px dashed #6c757d;">
        <p style="margin: 0 0 10px 0; font-weight: bold; color: #495057;">📋 Test Link (for local testing):</p>
        <input type="text" id="attendance-link" readonly style="
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            background: white;
        ">
        <button onclick="copyLink()" style="
            margin-top: 10px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        ">📋 Copy Link</button>
    </div>
</div>

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>
<script>
// Version 2024-12-01-2 - Cache busting
(function() {
    'use strict';
    
    var PASSWORD = 'so123!';
    
    // TEST LOCATION: Ataturk 111a, Baku
    var ADA_LAT = 40.4081044;
    var ADA_LON = 49.8461084;
    var RADIUS_KM = 0.5; // 500 meters radius
    
    // Calculate distance between two coordinates (Haversine formula)
    function getDistance(lat1, lon1, lat2, lon2) {
        var R = 6371; // Earth's radius in km
        var dLat = (lat2 - lat1) * Math.PI / 180;
        var dLon = (lon2 - lon1) * Math.PI / 180;
        var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    // Check if user is on campus
    function checkLocation(callback) {
        if (!navigator.geolocation) {
            callback(false, 'Geolocation is not supported by your browser');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                var distance = getDistance(
                    ADA_LAT, ADA_LON,
                    position.coords.latitude,
                    position.coords.longitude
                );
                
                if (distance <= RADIUS_KM) {
                    callback(true, null);
                } else {
                    callback(false, 'You must be on ADA University campus to access attendance. Distance: ' + distance.toFixed(2) + ' km');
                }
            },
            function(error) {
                var errorMsg = 'Location access denied. Please enable location services.';
                if (error.code === error.PERMISSION_DENIED) {
                    errorMsg = 'Location permission denied. Please allow location access to use attendance.';
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    errorMsg = 'Location information unavailable.';
                } else if (error.code === error.TIMEOUT) {
                    errorMsg = 'Location request timed out.';
                }
                callback(false, errorMsg);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }
    
    // Password check (no location check for instructor)
    function checkPassword() {
        var input = document.getElementById('password-input').value;
        var errorDiv = document.getElementById('password-error');
        
        if (input === PASSWORD) {
            // Password correct - show QR code immediately
            errorDiv.style.display = 'none';
            document.getElementById('password-container').style.display = 'none';
            document.getElementById('qrcode-container').style.display = 'block';
            initQRCode();
        } else {
            errorDiv.style.color = '#e74c3c';
            errorDiv.textContent = 'Incorrect password. Please try again.';
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
            
            // Build student check-in page URL with session time parameter
            var baseUrl = window.location.origin + '/attend/math-stat-1/';
            var attendUrl = baseUrl + '?session=' + encodeURIComponent(sessionInfo);
            
            // Show the link in the text box
            document.getElementById('attendance-link').value = attendUrl;
            
            // Generate QR code - LARGE for projection
            var qrSize = Math.min(window.innerWidth * 0.7, window.innerHeight * 0.7, 800);
            new QRCode(qrcodeContainer, {
                text: attendUrl,
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
    
    // Copy link function
    window.copyLink = function() {
        var linkInput = document.getElementById('attendance-link');
        linkInput.select();
        linkInput.setSelectionRange(0, 99999); // For mobile
        document.execCommand('copy');
        alert('Link copied! You can paste it in your browser.');
    };

})();
</script>
