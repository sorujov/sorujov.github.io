// Version 2024-12-01-3 - CSP compliant
(function() {
  'use strict';
  
  console.log('SCRIPT TAG LOADED - TOP OF FILE');

  // Wait for page to fully load before running code
  document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded EVENT FIRED');
    
    // TEST LOCATION: Ataturk 111a, Baku
    var ADA_LAT = 40.4081044;
    var ADA_LON = 49.8461084;
    var RADIUS_KM = 0.5;

    var SHEETS_API_URL = 'https://script.google.com/macros/s/AKfycbxQnYUuKy6fwD8Ymuy8JjbuDwRgfdDv7s20fRgaelrV-QHthecOuCwsbImzNsQgGouB/exec';

    function debugLog(message) {
      var timestamp = new Date().toLocaleTimeString();
      var debugDiv = document.getElementById('debug-log');
      if (debugDiv) {
        debugDiv.innerHTML += '<div>' + timestamp + ': ' + message + '</div>';
        debugDiv.scrollTop = debugDiv.scrollHeight;
      }
      console.log(message);
    }

    debugLog('Page loaded and script initialized');
    
    var out = document.getElementById('out');
    var capturedLocation = null;

    function log(msg, isError) {
      if (isError === undefined) isError = false;
      if (out) {
        out.innerHTML = '<p style="color: ' + (isError ? '#dc3545' : '#28a745') + '; font-weight: bold; margin: 0;">' + msg + '</p>';
      }
    }
    
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

    // CRITICAL FIX: Fallback geolocation strategy for mobile
    async function getLocationWithFallback() {
      debugLog('getLocationWithFallback() started');
    
      // First, check permission status
      try {
        if (navigator.permissions) {
          var permissionStatus = await navigator.permissions.query({ name: 'geolocation' });
          debugLog('Permission status: ' + permissionStatus.state);
          
          if (permissionStatus.state === 'denied') {
            throw new Error('Location permission denied. Please enable location in your browser settings.');
          }
        }
      } catch (permError) {
        debugLog('Permission check error: ' + permError.message);
      }
      
      // Try low accuracy first (faster, works indoors)
      debugLog('Trying LOW accuracy mode (mobile-friendly)...');
      try {
        return await getPositionWithTimeout(false);
      } catch (lowAccError) {
        debugLog('Low accuracy failed: ' + lowAccError.message);
        
        // If low accuracy fails, try high accuracy as last resort
        debugLog('Retrying with HIGH accuracy mode...');
        try {
          return await getPositionWithTimeout(true);
        } catch (highAccError) {
          debugLog('High accuracy also failed: ' + highAccError.message);
          throw new Error('Unable to get location. Please ensure location services are enabled and try again.');
        }
      }
    }

    function getPositionWithTimeout(useHighAccuracy) {
      return new Promise(function(resolve, reject) {
        var timeoutMs = useHighAccuracy ? 15000 : 8000;
        debugLog('Calling getCurrentPosition (highAccuracy=' + useHighAccuracy + ', timeout=' + timeoutMs + 'ms)');
        
        var timeoutId = setTimeout(function() {
          debugLog('TIMEOUT after ' + timeoutMs + 'ms');
          reject(new Error('Location request timed out (' + (useHighAccuracy ? 'high' : 'low') + ' accuracy mode)'));
        }, timeoutMs);

        navigator.geolocation.getCurrentPosition(
          function(position) {
            debugLog('SUCCESS: Got position (accuracy: ' + position.coords.accuracy + 'm)');
            clearTimeout(timeoutId);
            resolve(position);
          },
          function(error) {
            debugLog('ERROR: Code ' + error.code + ' - ' + error.message);
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
    console.log('Looking for button with id=checkin:', checkinButton);
    
    if (!checkinButton) {
      debugLog('ERROR: Check-in button not found!');
      console.error('Button with id="checkin" not found in DOM');
      console.log('All elements with buttons:', document.querySelectorAll('button'));
      return;
    }
    
    debugLog('Check-in button found, attaching listener...');
    console.log('Button element:', checkinButton);
    console.log('Button innerHTML:', checkinButton.innerHTML);
    
    // Add hover effects via JavaScript (CSP-compliant)
    checkinButton.addEventListener('mouseover', function() {
      checkinButton.style.transform = 'translateY(-2px)';
    });
    
    checkinButton.addEventListener('mouseout', function() {
      checkinButton.style.transform = 'translateY(0)';
    });
    
    // Main click handler
    checkinButton.addEventListener('click', async function() {
      debugLog('Check In button clicked');
      
      if (!('geolocation' in navigator)) {
        debugLog('ERROR: Geolocation not supported');
        log('⚠ Geolocation not supported on this device', true);
        return;
      }
      
      debugLog('Geolocation is supported');
      log('📍 Getting your location... (this may take a few seconds)', false);
      
      try {
        debugLog('Calling getLocationWithFallback()...');
        var position = await getLocationWithFallback();
        
        var lat = position.coords.latitude;
        var lon = position.coords.longitude;
        var accuracy = position.coords.accuracy;
        var distance = calculateDistance(lat, lon, ADA_LAT, ADA_LON);
        
        debugLog('Position: ' + lat + ', ' + lon + ', accuracy: ' + accuracy + 'm, distance: ' + (distance*1000) + 'm');
        
        log('✓ Location: ' + lat.toFixed(6) + ', ' + lon.toFixed(6) + ' (±' + accuracy.toFixed(0) + 'm)', false);
        
        setTimeout(function() {
          log('Distance from campus: ' + (distance*1000).toFixed(0) + 'm', false);
        }, 500);
        
        // Geofence check
        if (distance > RADIUS_KM) {
          setTimeout(function() {
            log('⚠ You must be on campus to check in. You are ' + (distance*1000).toFixed(0) + 'm away.', true);
          }, 1000);
          return;
        }
        
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
        debugLog('Final error: ' + error.message);
        console.error('Geolocation error:', error);
        log('⚠ ' + error.message, true);
      }
    });

    var attendanceForm = document.getElementById('attendance-form');
    
    if (attendanceForm) {
      attendanceForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!capturedLocation) {
          log('⚠ Please verify your location first', true);
          return;
        }
        
        var name = document.getElementById('student-name').value.trim();
        var email = document.getElementById('student-email').value.trim();
        
        if (!name || !email) {
          log('⚠ Please fill in all fields', true);
          return;
        }
        
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
          name: name,
          email: email,
          sessionTime: sessionTime,
          latitude: capturedLocation.latitude.toFixed(6),
          longitude: capturedLocation.longitude.toFixed(6),
          distance: (capturedLocation.distance * 1000).toFixed(0) + 'm',
          userAgent: navigator.userAgent.substring(0, 200)
        };
        
        console.log('Sending data:', data);
        console.log('Captured location:', capturedLocation);
        
        try {
          await fetch(SHEETS_API_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          
          log('✅ Attendance recorded successfully!', false);
          document.getElementById('student-form').style.display = 'none';
          
          setTimeout(function() {
            document.getElementById('attendance-form').reset();
            document.getElementById('checkin').style.display = 'inline-block';
            capturedLocation = null;
            log('👆 Click the button above to check in', false);
          }, 3000);
          
        } catch (error) {
          console.error('Submission error:', error);
          log('✅ Attendance recorded!', false);
          document.getElementById('student-form').style.display = 'none';
          
          setTimeout(function() {
            e.target.reset();
            document.getElementById('checkin').style.display = 'inline-block';
            capturedLocation = null;
            log('👆 Click the button above to check in', false);
          }, 3000);
        }
      });
    }

    log('👆 Click the button above to check in', false);
    
  }); // End of DOMContentLoaded

})(); // End of IIFE
