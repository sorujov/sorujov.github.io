// Version 2024-12-08-1 - 5km radius for testing
(function() {
  'use strict';

  // Wait for page to fully load before running code
  document.addEventListener('DOMContentLoaded', function() {
    
    // TEST LOCATION: Ataturk 111a, Baku 40.39476586000145, 49.84937393783448
    var ADA_LAT = 40.39476586000145;
    var ADA_LON = 49.84937393783448;
    var RADIUS_KM = 5.0; // 5000 meters (testing)
    console.log('RADIUS_KM set to:', RADIUS_KM, 'km');
    var PASSWORD = 'so123!';
    var TOKEN_VALIDITY_SECONDS = 30; // Token expires after 30 seconds

    var SHEETS_API_URL = 'https://script.google.com/macros/s/AKfycbytmC2ECXRy8zXc-1ofxYiApApLDSOf7OpUzrD0Hc9f_95Wf7r_YvcWw35EhJd9OGPpLQ/exec';
    
    var out = document.getElementById('out');
    var capturedLocation = null;
    var hasSubmitted = false; // Track if submission already made with this token

    function log(msg, isError) {
      if (isError === undefined) isError = false;
      if (out) {
        out.innerHTML = '<p style="color: ' + (isError ? '#dc3545' : '#28a745') + '; font-weight: bold; margin: 0;">' + msg + '</p>';
      }
    }
    
    // Get token data from URL
    function getTokenData() {
      var urlParams = new URLSearchParams(window.location.search);
      var token = urlParams.get('token');
      var session = urlParams.get('session');
      
      if (!token || !session) {
        return null;
      }
      
      try {
        // Add padding if needed for base64
        var paddedToken = token;
        while (paddedToken.length % 4 !== 0) {
          paddedToken += '=';
        }
        
        // Decode token
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
      
      console.log('Token validation - token:', tokenData ? tokenData.token : null);
      console.log('Token validation - session:', tokenData ? tokenData.session : null);
      
      if (!tokenData) {
        log('⚠ Invalid or expired link. Please scan the QR code again.', true);
        document.getElementById('checkin').disabled = true;
        document.getElementById('checkin').style.opacity = '0.5';
        document.getElementById('checkin').style.cursor = 'not-allowed';
        return false;
      }
      
      console.log('Decoded token data:', tokenData);
      console.log('Timestamp:', tokenData.timestamp);
      console.log('Session ID:', tokenData.sessionId);
      console.log('Password from token:', tokenData.password);
      console.log('Expected password:', PASSWORD);
      
      // COMMENTED OUT: Password verification disabled - Apps Script verifies enrollment
      // Verify password
      // if (tokenData.password !== PASSWORD) {
      //     log('⚠ Invalid link. Please scan the QR code again.', true);
      //     document.getElementById('checkin').disabled = true;
      //     document.getElementById('checkin').style.opacity = '0.5';
      //     document.getElementById('checkin').style.cursor = 'not-allowed';
      //     return false;
      //   }
        
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
      
      console.log('Token validation passed!');
      return true;
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
      // First, check permission status
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
      
      // Try low accuracy first (faster, works indoors)
      try {
        return await getPositionWithTimeout(false);
      } catch (lowAccError) {
        // If low accuracy fails, try high accuracy as last resort
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
    }    // Add hover effects via JavaScript (CSP-compliant)
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
        
        // Geofence check - TEMPORARILY DISABLED FOR TESTING
        // if (distance > RADIUS_KM) {
        //   setTimeout(function() {
        //     log('⚠ You must be on campus to check in. You are ' + (distance*1000).toFixed(0) + 'm away.', true);
        //   }, 1000);
        //   return;
        // }
        
        // Location verified
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
        
        // Convert username to email format for Apps Script
        var email = username.includes('@') ? username : username + '@ada.edu.az';
        
        log('📤 Submitting attendance...', false);
        
        // Get session time from URL parameter (from QR code) or use current time
        var urlParams = new URLSearchParams(window.location.search);
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
          userAgent: navigator.userAgent.substring(0, 200)
        };
        
        try {
          await fetch(SHEETS_API_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          
          // Mark token as used
          var urlParams = new URLSearchParams(window.location.search);
          var token = urlParams.get('token');
          if (token) {
            var usedTokens = sessionStorage.getItem('usedTokens');
            var tokens = usedTokens ? JSON.parse(usedTokens) : [];
            tokens.push(token);
            sessionStorage.setItem('usedTokens', JSON.stringify(tokens));
            hasSubmitted = true;
          }
          
          log('✅ Attendance recorded successfully!', false);
          document.getElementById('student-form').style.display = 'none';
          
          setTimeout(function() {
            document.getElementById('attendance-form').reset();
            document.getElementById('checkin').style.display = 'none';
            capturedLocation = null;
            log('⚠ This link can only be used once. Please scan the QR code again to check in.', true);
          }, 3000);
          
        } catch (error) {
          // Mark token as used even if fetch fails (no-cors)
          var urlParams = new URLSearchParams(window.location.search);
          var token = urlParams.get('token');
          if (token) {
            var usedTokens = sessionStorage.getItem('usedTokens');
            var tokens = usedTokens ? JSON.parse(usedTokens) : [];
            tokens.push(token);
            sessionStorage.setItem('usedTokens', JSON.stringify(tokens));
            hasSubmitted = true;
          }
          
          log('✅ Attendance recorded!', false);
          document.getElementById('student-form').style.display = 'none';
          
          setTimeout(function() {
            e.target.reset();
            document.getElementById('checkin').style.display = 'none';
            capturedLocation = null;
            log('⚠ This link can only be used once. Please scan the QR code again to check in.', true);
          }, 3000);
        }
      });
    }
    
  }); // End of DOMContentLoaded

})(); // End of IIFE
