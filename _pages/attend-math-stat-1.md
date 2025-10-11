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
    ✓ Confirm Attendance
  </button>
  
  <div id="out" style="
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    min-height: 50px;
    background: #f8f9fa;
  "></div>
  
  <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
    <p style="margin: 0; font-size: 0.9rem;"><strong>Note:</strong> You must be on ADA University campus to check in. Location access is required.</p>
  </div>
</div>

<script>
// ADA University approximate geofence (adjust coordinates as needed)
const ADA_LAT = 40.3775; // ADA University latitude
const ADA_LON = 49.8491; // ADA University longitude
const RADIUS_KM = 0.5; // 500 meters

const BACKEND_CHECKIN_URL = 'YOUR_BACKEND_CHECKIN_ENDPOINT';

const out = document.getElementById('out');
const params = new URLSearchParams(location.search);
const token = params.get('tok');

function log(msg, isError = false) {
  out.innerHTML = `<p style="color: ${isError ? '#dc3545' : '#28a745'}; font-weight: bold; margin: 0;">${msg}</p>`;
}

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

document.getElementById('checkin').addEventListener('click', () => {
  if (!token) {
    log('⚠ Invalid QR code. Please scan again.', true);
    return;
  }
  
  if (!('geolocation' in navigator)) {
    log('⚠ Geolocation not supported on this device', true);
    return;
  }
  
  log('📍 Checking location...', false);
  
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const lat = pos.coords.latitude;
    const lon = pos.coords.longitude;
    const distance = calculateDistance(lat, lon, ADA_LAT, ADA_LON);
    
    // Client-side geofence check
    if (distance > RADIUS_KM) {
      log(`⚠ You must be on ADA campus to check in (${(distance*1000).toFixed(0)}m away)`, true);
      return;
    }
    
    const body = {
      token,
      lat,
      lon,
      ts: Date.now(),
      ua: navigator.userAgent.substring(0, 100),
      course: 'STAT2311'
    };
    
    try {
      // For testing without backend:
      log('✓ Attendance recorded successfully!', false);
      console.log('Would send:', body);
      
      // Replace with actual backend call:
      // const r = await fetch(BACKEND_CHECKIN_URL, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(body)
      // });
      // const result = await r.text();
      // log(result, !r.ok);
      
    } catch(e) {
      log('⚠ Network error. Please try again.', true);
      console.error(e);
    }
  }, (err) => {
    log('⚠ Location access required. Please enable location services.', true);
    console.error(err);
  }, { 
    enableHighAccuracy: true, 
    maximumAge: 0, 
    timeout: 15000 
  });
});

// Auto-show message if no token
if (!token) {
  log('⚠ No valid token found. Please scan the QR code.', true);
}
</script>
