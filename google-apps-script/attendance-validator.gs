/**
 * QR Attendance Token Validator
 * Google Apps Script Web App
 * 
 * Deploy as: Web app
 * Execute as: Me
 * Access: Anyone (no authentication required)
 */

// CONFIGURATION - Change these values
const SECRET_KEY = 'YOUR_SECRET_KEY_CHANGE_ME_' + Math.random(); // Change this!
const TOKEN_VALIDITY_MS = 5 * 60 * 1000; // 5 minutes
const GOOGLE_FORM_URL = 'https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform';
const SESSION_TIME_ENTRY = 'entry.303810813'; // Your session date/time field

/**
 * Handle GET requests (when QR code is scanned)
 */
function doGet(e) {
  try {
    // Get token from URL parameter
    const token = e.parameter.token;
    
    if (!token) {
      return HtmlService.createHtmlOutput(errorPage('Missing token'));
    }
    
    // Parse token: timestamp|signature
    const parts = token.split('|');
    if (parts.length !== 2) {
      return HtmlService.createHtmlOutput(errorPage('Invalid token format'));
    }
    
    const timestamp = parts[0];
    const signature = parts[1];
    const timestampMs = parseInt(timestamp);
    
    // Check if token is expired
    const now = Date.now();
    const age = now - timestampMs;
    
    if (age > TOKEN_VALIDITY_MS) {
      return HtmlService.createHtmlOutput(expiredPage(Math.floor(age / 60000)));
    }
    
    // Verify signature (prevents tampering)
    const expectedSignature = generateSignature(timestamp);
    if (signature !== expectedSignature) {
      return HtmlService.createHtmlOutput(errorPage('Invalid signature'));
    }
    
    // Token is valid - redirect to Google Form with session info
    const sessionInfo = formatSessionInfo(new Date(timestampMs));
    const formUrl = `${GOOGLE_FORM_URL}?usp=pp_url&${SESSION_TIME_ENTRY}=${encodeURIComponent(sessionInfo)}`;
    
    // Redirect to Google Form
    return HtmlService.createHtmlOutput(redirectPage(formUrl));
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    return HtmlService.createHtmlOutput(errorPage('Processing error: ' + error.message));
  }
}

/**
 * Generate signature for timestamp
 */
function generateSignature(timestamp) {
  const data = timestamp + SECRET_KEY;
  const signature = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    data,
    Utilities.Charset.UTF_8
  );
  
  // Convert to hex string and take first 16 characters
  const hexString = signature.map(function(byte) {
    return ('0' + (byte & 0xFF).toString(16)).slice(-2);
  }).join('');
  
  return hexString.substring(0, 16);
}

/**
 * Format timestamp as human-readable session info
 */
function formatSessionInfo(date) {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months[date.getMonth()];
  const day = date.getDate();
  const year = date.getFullYear();
  let hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  const minutesStr = ('0' + minutes).slice(-2);
  return `${month} ${day}, ${year} ${hours}:${minutesStr} ${ampm}`;
}

/**
 * HTML page for expired QR codes
 */
function expiredPage(ageMinutes) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>QR Code Expired</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
        p { color: #555; line-height: 1.6; margin: 10px 0; }
        .icon { font-size: 64px; margin-bottom: 20px; }
        .age { color: #e74c3c; font-weight: bold; }
        .note { font-size: 14px; color: #999; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">⏰</div>
        <h1>QR Code Expired</h1>
        <p>This QR code is <span class="age">${ageMinutes} minutes old</span> and is no longer valid.</p>
        <p>Please scan the <strong>current QR code</strong> displayed by your instructor.</p>
        <p class="note">QR codes expire after 5 minutes for security.</p>
      </div>
    </body>
    </html>
  `;
}

/**
 * HTML page for errors
 */
function errorPage(message) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Error</title>
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
        <div class="icon">❌</div>
        <h1>Invalid Request</h1>
        <p>${message}</p>
        <p style="margin-top: 20px; font-size: 14px; color: #999;">Please contact your instructor if this problem persists.</p>
      </div>
    </body>
    </html>
  `;
}

/**
 * Redirect page (with auto-redirect)
 */
function redirectPage(url) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Redirecting...</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <meta http-equiv="refresh" content="0;url=${url}">
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
        h1 { color: #28a745; font-size: 24px; margin-bottom: 20px; }
        p { color: #555; line-height: 1.6; }
        .icon { font-size: 64px; margin-bottom: 20px; }
        a { color: #667eea; text-decoration: none; font-weight: 600; }
        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #667eea;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 20px auto;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">✅</div>
        <h1>Valid QR Code</h1>
        <p>Redirecting to attendance form...</p>
        <div class="spinner"></div>
        <p style="font-size: 14px; color: #999; margin-top: 20px;">
          If you're not redirected, <a href="${url}">click here</a>.
        </p>
      </div>
      <script>
        setTimeout(function() {
          window.location.href = '${url}';
        }, 1000);
      </script>
    </body>
    </html>
  `;
}

/**
 * Test function - run this to test signature generation
 */
function testSignature() {
  const timestamp = Date.now().toString();
  const signature = generateSignature(timestamp);
  Logger.log('Timestamp: ' + timestamp);
  Logger.log('Signature: ' + signature);
  Logger.log('Token: ' + timestamp + '|' + signature);
}
