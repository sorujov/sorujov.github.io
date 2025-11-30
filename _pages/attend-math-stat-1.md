---
layout: single
title: "Check-in - Mathematical Statistics I"
permalink: /attend/math-stat-1/
classes: wide
---


<div style="max-width: 500px; margin: 2rem auto; text-align: center;">
  <h2>📊 Confirm Your Attendance</h2>
  <p>Course: Mathematical Statistics I (STAT 2311)</p>
  
  <button id="checkin" style="
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 2rem;
    border: none;
    border-radius: 25px;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    margin: 20px 0;
    transition: transform 0.2s;
  " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
    ✓ Verify Location
  </button>
  
  <div id="student-form" style="display: none; margin-top: 20px;">
    <form id="attendance-form">
      <input type="text" id="student-name" placeholder="Full Name" required style="
        width: 100%;
        padding: 12px;
        margin: 10px 0;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 16px;
        box-sizing: border-box;
      ">
      <input type="email" id="student-email" placeholder="Email or Student ID" required style="
        width: 100%;
        padding: 12px;
        margin: 10px 0;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 16px;
        box-sizing: border-box;
      ">
      <button type="submit" style="
        background: linear-gradient(45deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 10px;
      ">Submit Attendance</button>
    </form>
  </div>
  
  <div id="out" style="
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    min-height: 50px;
    background: #f8f9fa;
  "></div>
  
  <div id="debug-log" style="
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    background: #e9ecef;
    font-family: monospace;
    font-size: 12px;
    max-height: 300px;
    overflow-y: auto;
  "></div>
  
  <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
    <p style="margin: 0; font-size: 0.9rem;"><strong>Note:</strong> You must be on ADA University campus to check in. Location access is required.</p>
  </div>
</div>


<script>
// Wait for page to fully load before running code
document.addEventListener('DOMContentLoaded', function() {
  
  // TEST LOCATION: Ataturk 111a, Baku
  const ADA_LAT = 40.4081044;
  const ADA_LON = 49.8461084;
  const RADIUS_KM = 0.5;

  const SHEETS_API_URL = 'https://script.google.com/macros/s/AKfycbxQnYUuKy6fwD8Ymuy8JjbuDwRgfdDv7s20fRgaelrV-QHthecOuCwsbImzNsQgGouB/exec';

  function debugLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    const debugDiv = document.getElementById('debug-log');
    if (debugDiv) {
      debugDiv.innerHTML += `<div>${timestamp}: ${message}</div>`;
      debugDiv.scrollTop = debugDiv.scrollHeight;
    }
    console.log(message);
  }

  debugLog('Page loaded and script initialized');
  
  const out = document.getElementById('out');
  let capturedLocation = null;

  function log(msg, isError = false) {
    if (out) {
      out.innerHTML = `<p style="color: ${isError ? '#dc3545' : '#28a745'}; font-weight: bold; margin: 0;">${msg}</p>`;
    }
  }
  
  function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// CRITICAL FIX: Fallback geolocation strategy for mobile
async function getLocationWithFallback() {
  debugLog('getLocationWithFallback() started');
  
  // First, check permission status
  try {
    if (navigator.permissions) {
      const permissionStatus = await navigator.permissions.query({ name: 'geolocation' });
      debugLog(`Permission status: ${permissionStatus.state}`);
      
      if (permissionStatus.state === 'denied') {
        throw new Error('Location permission denied. Please enable location in your browser settings.');
      }
    }
  } catch (permError) {
    debugLog(`Permission check error: ${permError.message}`);
  }
  
  // Try low accuracy first (faster, works indoors)
  debugLog('Trying LOW accuracy mode (mobile-friendly)...');
  try {
    return await getPositionWithTimeout(false);
  } catch (lowAccError) {
    debugLog(`Low accuracy failed: ${lowAccError.message}`);
    
    // If low accuracy fails, try high accuracy as last resort
    debugLog('Retrying with HIGH accuracy mode...');
    try {
      return await getPositionWithTimeout(true);
    } catch (highAccError) {
      debugLog(`High accuracy also failed: ${highAccError.message}`);
      throw new Error('Unable to get location. Please ensure location services are enabled and try again.');
    }
  }
}

function getPositionWithTimeout(useHighAccuracy) {
  return new Promise((resolve, reject) => {
    const timeoutMs = useHighAccuracy ? 15000 : 8000;
    debugLog(`Calling getCurrentPosition (highAccuracy=${useHighAccuracy}, timeout=${timeoutMs}ms)`);
    
    const timeoutId = setTimeout(() => {
      debugLog(`TIMEOUT after ${timeoutMs}ms`);
      reject(new Error(`Location request timed out (${useHighAccuracy ? 'high' : 'low'} accuracy mode)`));
    }, timeoutMs);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        debugLog(`SUCCESS: Got position (accuracy: ${position.coords.accuracy}m)`);
        clearTimeout(timeoutId);
        resolve(position);
      },
      (error) => {
        debugLog(`ERROR: Code ${error.code} - ${error.message}`);
        clearTimeout(timeoutId);
        const errorMessages = {
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

  const checkinButton = document.getElementById('checkin');
  
  if (!checkinButton) {
    debugLog('ERROR: Check-in button not found!');
    console.error('Button with id="checkin" not found in DOM');
    return;
  }
  
  debugLog('Check-in button found, attaching listener...');
  
  checkinButton.addEventListener('click', async () => {
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
    const position = await getLocationWithFallback();
    
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const accuracy = position.coords.accuracy;
    const distance = calculateDistance(lat, lon, ADA_LAT, ADA_LON);
    
    debugLog(`Position: ${lat}, ${lon}, accuracy: ${accuracy}m, distance: ${distance*1000}m`);
    
    log(`✓ Location: ${lat.toFixed(6)}, ${lon.toFixed(6)} (±${accuracy.toFixed(0)}m)`, false);
    
    setTimeout(() => {
      log(`Distance from campus: ${(distance*1000).toFixed(0)}m`, false);
    }, 500);
    
    // Geofence check
    if (distance > RADIUS_KM) {
      setTimeout(() => {
        log(`⚠ You must be on campus to check in. You are ${(distance*1000).toFixed(0)}m away.`, true);
      }, 1000);
      return;
    }
    
    // Location verified
    setTimeout(() => {
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
    debugLog(`Final error: ${error.message}`);
    console.error('Geolocation error:', error);
    log('⚠ ' + error.message, true);
  }
  });

  const attendanceForm = document.getElementById('attendance-form');
  
  if (attendanceForm) {
    attendanceForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  if (!capturedLocation) {
    log('⚠ Please verify your location first', true);
    return;
  }
  
  const name = document.getElementById('student-name').value.trim();
  const email = document.getElementById('student-email').value.trim();
  
  if (!name || !email) {
    log('⚠ Please fill in all fields', true);
    return;
  }
  
  log('📤 Submitting attendance...', false);
  
  // Get session time from URL parameter (from QR code) or use current time
  const urlParams = new URLSearchParams(window.location.search);
  const sessionTime = urlParams.get('session') || (capturedLocation.timestamp.toLocaleDateString('en-US', {
    month: 'short', 
    day: 'numeric', 
    year: 'numeric'
  }) + ' ' + capturedLocation.timestamp.toLocaleTimeString('en-US', {
    hour: 'numeric', 
    minute: '2-digit', 
    hour12: true
  }));
  
  const data = {
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
    
    setTimeout(() => {
      document.getElementById('attendance-form').reset();
      document.getElementById('checkin').style.display = 'inline-block';
      capturedLocation = null;
      log('👆 Click the button above to check in', false);
    }, 3000);
    
  } catch (error) {
    console.error('Submission error:', error);
    log('✅ Attendance recorded!', false);
    document.getElementById('student-form').style.display = 'none';
    
    setTimeout(() => {
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
</script>
