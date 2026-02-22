// Version 2026-02-22-1 - Math-Stat II Attendance (Multi-Section + Present/Late)
(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {

    var ADA_LAT = 40.39476586000145;
    var ADA_LON = 49.84937393783448;
    var RADIUS_KM = 5; // 5 km (testing — change back to 0.5 for production)
    var PASSWORD = 'so123!';
    var TOKEN_VALIDITY_SECONDS = 120; // Token expires after 2 minutes

    // UPDATE THIS URL after deploying the new Google Apps Script
    var SHEETS_API_URL = 'https://script.google.com/macros/s/AKfycbwLv1WeX52ZwLIqCvMjtdIoYDfS-IVm9VzKrUuBivQ1g_JqBGf5c-PawISzQwgAiQow-Q/exec';

    var out = document.getElementById('out');
    var capturedLocation = null;
    var hasSubmitted = false;

    // Parse section and status from URL params (set by QR code)
    var urlParams = new URLSearchParams(window.location.search);
    var qrSection = urlParams.get('section') || '';  // 'A' or 'B'
    var qrStatus = urlParams.get('status') || 'present';  // 'present' or 'late'
    var attendanceStatus = (qrStatus.toLowerCase() === 'late') ? 'Late' : 'Present';

    // Show section/status info to student
    var infoDiv = document.getElementById('section-status-info');
    if (infoDiv && (qrSection || qrStatus)) {
      var sectionLabel = qrSection ? 'Section ' + qrSection.toUpperCase() : '';
      var statusLabel = attendanceStatus === 'Late' ? '⏰ Late Check-in' : '✓ On-time Check-in';
      var bgColor = attendanceStatus === 'Late' ? '#fff3cd' : '#d4edda';
      var textColor = attendanceStatus === 'Late' ? '#856404' : '#155724';

      infoDiv.style.display = 'block';
      infoDiv.style.background = bgColor;
      infoDiv.style.color = textColor;
      infoDiv.innerHTML = statusLabel + (sectionLabel ? ' &mdash; ' + sectionLabel : '');
    }

    function log(msg, isError) {
      if (isError === undefined) isError = false;
      if (out) {
        out.innerHTML = '<p style="color: ' + (isError ? '#dc3545' : '#28a745') + '; font-weight: bold; margin: 0;">' + msg + '</p>';
      }
    }

    // Get token data from URL
    function getTokenData() {
      var token = urlParams.get('token');
      var session = urlParams.get('session');

      if (!token || !session) {
        return null;
      }

      try {
        var paddedToken = token;
        while (paddedToken.length % 4 !== 0) {
          paddedToken += '=';
        }

        var decoded = atob(paddedToken);
        var parts = decoded.split(':');

        return {
          token: token,
          session: session,
          timestamp: parseInt(parts[0]),
          sessionId: parts[1],
          password: parts[2]
        };
      } catch (e) {
        return null;
      }
    }

    // Check if token is still valid (not expired)
    function isTokenValid(tokenData, showError) {
      if (!tokenData) {
        if (showError) log('⚠ Invalid link format. Please scan the QR code again.', true);
        return false;
      }

      var now = new Date().getTime();
      var ageSeconds = (now - tokenData.timestamp) / 1000;

      if (ageSeconds > TOKEN_VALIDITY_SECONDS) {
        if (showError) {
          log('⚠ This link has expired (' + Math.round(ageSeconds) + ' sec old). Please scan the QR code again.', true);
        }
        return false;
      }

      return true;
    }

    // Validate token from URL
    function validateToken() {
      var tokenData = getTokenData();

      if (!tokenData) {
        log('⚠ Invalid or expired link. Please scan the QR code again.', true);
        document.getElementById('checkin').disabled = true;
        document.getElementById('checkin').style.opacity = '0.5';
        document.getElementById('checkin').style.cursor = 'not-allowed';
        return false;
      }

      // Check if token was already used
      var usedTokens = sessionStorage.getItem('usedTokens');
      if (usedTokens) {
        var tokens = JSON.parse(usedTokens);
        if (tokens.indexOf(tokenData.token) !== -1) {
          log('⚠ This attendance link has already been used. Please scan the QR code again.', true);
          document.getElementById('checkin').disabled = true;
          document.getElementById('checkin').style.opacity = '0.5';
          document.getElementById('checkin').style.cursor = 'not-allowed';
          return false;
        }
      }

      // Verify session ID matches current QR (prevents old QR usage)
      var currentQRSession = sessionStorage.getItem('currentQRSession');
      if (currentQRSession && tokenData.sessionId !== currentQRSession) {
        log('⚠ This QR code is no longer valid. Please scan the latest QR code.', true);
        document.getElementById('checkin').disabled = true;
        document.getElementById('checkin').style.opacity = '0.5';
        document.getElementById('checkin').style.cursor = 'not-allowed';
        return false;
      }

      // Check if token is expired
      if (!isTokenValid(tokenData, true)) {
        document.getElementById('checkin').disabled = true;
        document.getElementById('checkin').style.opacity = '0.5';
        document.getElementById('checkin').style.cursor = 'not-allowed';
        return false;
      }

      return true;
    }

    // Check if this device already submitted today
    var todayKey = 'mathstat2-attend-' + new Date().toISOString().slice(0, 10);
    if (localStorage.getItem(todayKey)) {
      log('⚠ Attendance already submitted from this device today. One check-in per device per day.', true);
      var checkinBtn = document.getElementById('checkin');
      if (checkinBtn) {
        checkinBtn.disabled = true;
        checkinBtn.style.opacity = '0.5';
        checkinBtn.style.cursor = 'not-allowed';
      }
      return;
    }

    // Validate token first
    if (!validateToken()) {
      return;
    }

    log('👆 Click the button above to check in', false);

    function calculateDistance(lat1, lon1, lat2, lon2) {
      var R = 6371;
      var dLat = (lat2 - lat1) * Math.PI / 180;
      var dLon = (lon2 - lon1) * Math.PI / 180;
      var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);
      var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
      return R * c;
    }

    // Fallback geolocation strategy for mobile
    async function getLocationWithFallback() {
      try {
        if (navigator.permissions) {
          var permissionStatus = await navigator.permissions.query({ name: 'geolocation' });
          if (permissionStatus.state === 'denied') {
            throw new Error('Location permission denied. Please enable location in your browser settings.');
          }
        }
      } catch (permError) {
        // Ignore permission check errors
      }

      try {
        return await getPositionWithTimeout(false);
      } catch (lowAccError) {
        try {
          return await getPositionWithTimeout(true);
        } catch (highAccError) {
          throw new Error('Unable to get location. Please ensure location services are enabled and try again.');
        }
      }
    }

    function getPositionWithTimeout(useHighAccuracy) {
      return new Promise(function(resolve, reject) {
        var timeoutMs = useHighAccuracy ? 15000 : 8000;

        var timeoutId = setTimeout(function() {
          reject(new Error('Location request timed out (' + (useHighAccuracy ? 'high' : 'low') + ' accuracy mode)'));
        }, timeoutMs);

        navigator.geolocation.getCurrentPosition(
          function(position) {
            clearTimeout(timeoutId);
            resolve(position);
          },
          function(error) {
            clearTimeout(timeoutId);
            var errorMessages = {
              1: 'Permission denied',
              2: 'Position unavailable',
              3: 'Request timeout'
            };
            reject(new Error(errorMessages[error.code] || error.message));
          },
          {
            enableHighAccuracy: useHighAccuracy,
            timeout: timeoutMs - 2000,
            maximumAge: 0
          }
        );
      });
    }

    var checkinButton = document.getElementById('checkin');

    if (!checkinButton) {
      return;
    }

    checkinButton.addEventListener('mouseover', function() {
      checkinButton.style.transform = 'translateY(-2px)';
    });

    checkinButton.addEventListener('mouseout', function() {
      checkinButton.style.transform = 'translateY(0)';
    });

    // Main click handler
    checkinButton.addEventListener('click', async function() {
      if (!('geolocation' in navigator)) {
        log('⚠ Geolocation not supported on this device', true);
        return;
      }

      log('📍 Getting your location... (this may take a few seconds)', false);

      try {
        var position = await getLocationWithFallback();

        var lat = position.coords.latitude;
        var lon = position.coords.longitude;
        var accuracy = position.coords.accuracy;
        var distance = calculateDistance(lat, lon, ADA_LAT, ADA_LON);

        log('✓ Location: ' + lat.toFixed(6) + ', ' + lon.toFixed(6) + ' (±' + accuracy.toFixed(0) + 'm)', false);

        setTimeout(function() {
          log('Distance from campus: ' + (distance*1000).toFixed(0) + 'm (RADIUS: ' + RADIUS_KM + 'km)', false);
        }, 500);

        if (distance > RADIUS_KM) {
          setTimeout(function() {
            log('⚠ You must be on campus to check in. You are ' + (distance*1000).toFixed(0) + 'm away.', true);
          }, 1000);
          return;
        }

        setTimeout(function() {
          log('✓ Location verified! Please enter your details below.', false);
        }, 1000);

        capturedLocation = {
          latitude: lat,
          longitude: lon,
          distance: distance,
          timestamp: new Date()
        };

        document.getElementById('student-form').style.display = 'block';
        document.getElementById('checkin').style.display = 'none';

      } catch (error) {
        log('⚠ ' + error.message, true);
      }
    });

    var attendanceForm = document.getElementById('attendance-form');

    if (attendanceForm) {
      attendanceForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Check if token has expired before submitting
        var tokenData = getTokenData();
        if (!isTokenValid(tokenData, true)) {
          document.getElementById('student-form').style.display = 'none';
          document.getElementById('checkin').style.display = 'none';
          return;
        }

        if (!capturedLocation) {
          log('⚠ Please verify your location first', true);
          return;
        }

        var username = document.getElementById('student-username').value.trim();

        if (!username) {
          log('⚠ Please enter your username', true);
          return;
        }

        var email = username.includes('@') ? username : username + '@ada.edu.az';

        log('📤 Submitting attendance...', false);

        var sessionTime = urlParams.get('session') || (capturedLocation.timestamp.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }) + ' ' + capturedLocation.timestamp.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        }));

        var data = {
          name: username,
          email: email,
          sessionTime: sessionTime,
          latitude: capturedLocation.latitude.toFixed(6),
          longitude: capturedLocation.longitude.toFixed(6),
          distance: (capturedLocation.distance * 1000).toFixed(0) + 'm',
          userAgent: navigator.userAgent.substring(0, 200),
          section: qrSection,
          attendanceStatus: attendanceStatus
        };

        try {
          var response = await fetch(SHEETS_API_URL, {
            method: 'POST',
            body: JSON.stringify(data)
          });

          var result = await response.json();

          if (result.success) {
            // Mark device as submitted for today
            localStorage.setItem(todayKey, new Date().toISOString());

            // Mark token as used
            var token = urlParams.get('token');
            if (token) {
              var usedTokens = sessionStorage.getItem('usedTokens');
              var tokens = usedTokens ? JSON.parse(usedTokens) : [];
              tokens.push(token);
              sessionStorage.setItem('usedTokens', JSON.stringify(tokens));
              hasSubmitted = true;
            }

            log('✅ ' + result.message, false);
            document.getElementById('student-form').style.display = 'none';

            setTimeout(function() {
              document.getElementById('attendance-form').reset();
              document.getElementById('checkin').style.display = 'none';
              capturedLocation = null;
              log('⚠ This link can only be used once. Please scan the QR code again to check in.', true);
            }, 3000);
          } else {
            var errorMessage = result.message || 'Unknown error occurred';

            if (result.errorType === 'schedule') {
              errorMessage = '🕒 ' + errorMessage;
            } else if (result.errorType === 'location') {
              errorMessage = '📍 ' + errorMessage;
            } else if (result.errorType === 'enrollment') {
              errorMessage = '👤 ' + errorMessage;
            } else if (result.errorType === 'blackboard_sync') {
              errorMessage = '🔄 ' + errorMessage;
            } else if (result.errorType === 'invalid_section') {
              errorMessage = '⚠ ' + errorMessage;
            } else {
              errorMessage = '⚠ ' + errorMessage;
            }

            log(errorMessage, true);

            if (result.errorType === 'schedule' || result.errorType === 'enrollment') {
              document.getElementById('student-form').style.display = 'none';
              document.getElementById('checkin').style.display = 'none';
            }
          }

        } catch (error) {
          var errorMsg = '⚠ ';
          if (error.message.includes('Failed to fetch')) {
            errorMsg += 'Cannot connect to server. Please check your internet connection or try again.';
          } else if (error.message.includes('NetworkError')) {
            errorMsg += 'Network error. Please ensure you have a stable internet connection.';
          } else if (error.message.includes('CORS')) {
            errorMsg += 'Configuration error. Please contact your instructor.';
          } else {
            errorMsg += error.message || 'An error occurred. Please try again.';
          }

          log(errorMsg, true);
        }
      });
    }

  }); // End of DOMContentLoaded

})(); // End of IIFE
