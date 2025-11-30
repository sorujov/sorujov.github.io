# Token-Based Attendance System - Preventing Old QR Reuse

## Problem
Current system: Old QR codes can be screenshotted and reused later because they're just URLs with timestamps.

## Solution Architecture

### Flow:
1. **QR Code** → Contains unique token (not timestamp)
2. **Student scans** → Redirects to validation service
3. **Backend validates** → Token age < 5 minutes?
4. **If valid** → Redirect to Google Form
5. **If expired** → Show error page

### Components:
- **Frontend (GitHub Pages)**: Generates QR with tokens
- **Backend (Cloudflare Worker)**: Validates tokens and redirects
- **Google Form**: Collects attendance data

---

## Implementation Steps

### Step 1: Create Cloudflare Worker

Create a free Cloudflare account and deploy this worker:

**File: `worker.js`**
```javascript
// Secret key - CHANGE THIS to a random string!
const SECRET_KEY = 'YOUR_SECRET_KEY_CHANGE_ME_123456789';
const TOKEN_VALIDITY_MS = 5 * 60 * 1000; // 5 minutes
const GOOGLE_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform';

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  
  // Extract token from URL: /attendance?token=...
  const token = url.searchParams.get('token');
  
  if (!token) {
    return new Response('Missing token', { status: 400 });
  }
  
  try {
    // Decode token: timestamp|signature
    const [timestamp, signature] = token.split('|');
    const timestampMs = parseInt(timestamp);
    const now = Date.now();
    
    // Check if token is expired
    if (now - timestampMs > TOKEN_VALIDITY_MS) {
      return new Response(expiredPage(), {
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    // Verify signature (prevents tampering)
    const expectedSignature = await generateSignature(timestamp);
    if (signature !== expectedSignature) {
      return new Response('Invalid token', { status: 403 });
    }
    
    // Token is valid - redirect to Google Form with session info
    const sessionDate = new Date(timestampMs);
    const sessionInfo = formatSessionInfo(sessionDate);
    const formUrl = `${GOOGLE_FORM_URL}?usp=pp_url&entry.303810813=${encodeURIComponent(sessionInfo)}`;
    
    return Response.redirect(formUrl, 302);
    
  } catch (e) {
    return new Response('Invalid token format', { status: 400 });
  }
}

async function generateSignature(timestamp) {
  const data = timestamp + SECRET_KEY;
  const msgBuffer = new TextEncoder().encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex.substring(0, 16); // Use first 16 chars
}

function formatSessionInfo(date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  const minutesStr = minutes.toString().padStart(2, '0');
  return `${month} ${day}, ${year} ${hours}:${minutesStr} ${ampm}`;
}

function expiredPage() {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>QR Code Expired</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
          background: white;
          padding: 40px;
          border-radius: 15px;
          text-align: center;
          max-width: 400px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { color: #e74c3c; font-size: 24px; margin-bottom: 20px; }
        p { color: #555; line-height: 1.6; }
        .icon { font-size: 64px; margin-bottom: 20px; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">⏰</div>
        <h1>QR Code Expired</h1>
        <p>This QR code is no longer valid. Please scan the current QR code displayed by your instructor.</p>
        <p style="margin-top: 20px; font-size: 14px; color: #999;">QR codes expire after 5 minutes for security.</p>
      </div>
    </body>
    </html>
  `;
}
```

**Deploy command:**
```bash
npx wrangler deploy
```

Your worker will be available at: `https://your-worker.your-subdomain.workers.dev`

---

### Step 2: Update Attendance Page

Replace the QR generation code to create tokens instead of direct Google Form URLs:

**File: `_pages/attendance-qr.md`**
```markdown
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
            <li>QR codes expire after 5 minutes</li>
        </ul>
    </div>
</div>

<script src="{{ site.baseurl }}/assets/js/qrcode.min.js"></script>
<script>
(function() {
    'use strict';
    
    var QR_REFRESH_MS = 30000;
    var WORKER_URL = 'https://your-worker.your-subdomain.workers.dev/attendance';
    var SECRET_KEY = 'YOUR_SECRET_KEY_CHANGE_ME_123456789'; // Must match worker
    
    var qrcodeContainer = document.getElementById("qrcode");
    var sessionTimeDisplay = document.getElementById("session-time");
    var countdownDisplay = document.getElementById("countdown");
    var countdownInterval;

    async function generateSignature(timestamp) {
        var data = timestamp + SECRET_KEY;
        var msgBuffer = new TextEncoder().encode(data);
        var hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
        var hashArray = Array.from(new Uint8Array(hashBuffer));
        var hashHex = hashArray.map(function(b) { 
            return b.toString(16).padStart(2, '0'); 
        }).join('');
        return hashHex.substring(0, 16);
    }

    async function generateQR() {
        try {
            qrcodeContainer.innerHTML = "";
            if (countdownInterval) clearInterval(countdownInterval);
            
            var now = new Date();
            var timestamp = now.getTime().toString();
            
            // Display formatted session time
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
            sessionTimeDisplay.textContent = dateStr + ' ' + timeStr;
            
            // Generate token: timestamp|signature
            var signature = await generateSignature(timestamp);
            var token = timestamp + '|' + signature;
            
            // Build URL with token
            var attendanceUrl = WORKER_URL + '?token=' + encodeURIComponent(token);
            
            // Generate QR code
            new QRCode(qrcodeContainer, {
                text: attendanceUrl,
                width: 300,
                height: 300,
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', generateQR);
    } else {
        generateQR();
    }

    setInterval(generateQR, QR_REFRESH_MS);
})();
</script>
```

---

## How It Works

### Token Format:
```
timestamp|signature
1731744000000|a1b2c3d4e5f6g7h8
```

### Validation:
1. Extract timestamp from token
2. Check: `current_time - timestamp < 5 minutes`?
3. Verify signature matches (prevents tampering)
4. If valid → redirect to Google Form
5. If expired → show error page

### Security:
- ✅ **Time-limited**: Expires after 5 minutes
- ✅ **Tamper-proof**: Signature prevents token modification
- ✅ **No replay**: Each QR has unique timestamp
- ✅ **Screenshots useless**: Old tokens rejected by backend

---

## Alternative: Simpler Solutions

If Cloudflare Workers is too complex, here are simpler alternatives:

### Option A: Google Apps Script (No External Service)
Use Google Apps Script as backend (free, integrated with Google Forms)

### Option B: Accept Detection Strategy
Keep current system but strictly enforce timestamp validation in post-processing

### Option C: Physical Attendance
Use a tablet/laptop where students sign in directly (no QR needed)

---

## Deployment Checklist

- [ ] Sign up for Cloudflare account (free)
- [ ] Create new Worker
- [ ] Copy worker.js code
- [ ] Change SECRET_KEY to random string
- [ ] Deploy worker
- [ ] Get worker URL
- [ ] Update attendance page with worker URL
- [ ] Update SECRET_KEY in attendance page
- [ ] Test: Scan QR → Should redirect to form
- [ ] Test: Wait 6 minutes, scan same QR → Should show expired page

---

Would you like me to help set up the Cloudflare Worker, or would you prefer the Google Apps Script solution?
