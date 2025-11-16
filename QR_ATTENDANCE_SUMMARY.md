# QR Attendance System - Implementation Summary

## Project Goal
Create a dynamic QR code attendance system for Mathematical Statistics I course that:
- Generates QR codes that refresh every 30 seconds
- Links to a Google Form for attendance tracking
- Pre-fills session date/time to identify which class period
- Works on GitHub Pages hosting

---

## Attempts & Issues

### Attempt 1: QRious Library
- **Approach**: Used QRious JavaScript library from CDN
- **Result**: ❌ Failed on GitHub Pages
- **Issue**: Library not loading due to GitHub Pages security restrictions

### Attempt 2: QRCode.js Library
- **Approach**: Switched to QRCode.js from jsDelivr CDN
- **Result**: ❌ Failed on GitHub Pages (worked locally)
- **Issue**: External JavaScript blocked by Content Security Policy (CSP)

### Attempt 3: Google Chart API
- **Approach**: Server-side QR generation via Google's Chart API
- **Result**: ❌ Failed
- **Issue**: CSP blocks eval in JavaScript (error: "Content Security Policy blocks eval")

### Attempt 4: QR Server API
- **Approach**: Using api.qrserver.com for server-side QR generation
- **Result**: ❌ Failed
- **Issue**: Still blocked by GitHub Pages CSP

### Attempt 5: Self-Hosted QRCode.js (SOLUTION ✅)
- **Approach**: Downloaded qrcode.min.js and hosted locally in `/assets/js/`
- **Result**: ✅ SUCCESS - Works on GitHub Pages!
- **Why It Works**: 
  - GitHub Pages CSP allows scripts from 'self' origin
  - QRCode.js uses Canvas/DOM manipulation (no eval)
  - Library is CSP-compliant and has no dependencies

---

## Technical Details

### Google Form Configuration
- **Form URL**: https://docs.google.com/forms/d/e/1FAIpQLScCWzzIGI1AFbSLlahBNl18_eWGPChIXNyGkx2ej7joGwnfEQ/viewform
- **Fields**:
  - Session Date/Time: `entry.303810813` (pre-filled by QR)
  - First Name: `entry.685767776`
  - Last Name: `entry.802336020`
  - Email: Automatically collected by Google Forms
- **Design Decision**: Removed manual email field since Google collects it automatically

### Current Implementation
```javascript
// QR refreshes every 30 seconds
var QR_REFRESH_MS = 30000;

// Format: "Nov 16, 2025 10:00 AM"
var sessionInfo = dateStr + ' ' + timeStr;

// Pre-fill session time in Google Form
var formUrl = 'https://docs.google.com/forms/d/e/.../viewform?usp=pp_url&entry.303810813=' + encodeURIComponent(sessionInfo);
```

---

## GitHub Pages CSP Challenge

**Core Problem**: GitHub Pages enforces strict Content Security Policy that blocks:
1. External JavaScript libraries from CDNs
2. Inline `eval()` usage
3. Unsafe script execution

**Why Local Works but GitHub Doesn't**: 
- Local Jekyll server has no CSP restrictions
- GitHub Pages enforces security policies automatically

---

## Student Workflow (Intended)
1. Professor displays attendance page in fullscreen
2. Student scans QR code with phone
3. QR opens Google Form with session time pre-filled
4. Student enters First Name and Last Name
5. Form submits with:
   - Session time (from QR)
   - Student name (manual entry)
   - Email (auto-collected by Google)
   - Submission timestamp (auto-recorded by Google Sheets)

---

## Data Tracking
### Form Captures:
- Session Date/Time: Which class period student attended
- First Name & Last Name: Student identity
- Email: Auto-collected for verification
- Timestamp: Actual submission time (to detect late/tampered submissions)

### Cross-Reference:
Professor can compare:
- **Pre-filled session time** (e.g., "10:00 AM") = intended class
- **Google timestamp** (e.g., "10:05 AM") = actual scan time
- Detect if students change the session time or scan after class

---

## Git Commits
1. `c4b5f17` - Updated attendance QR with correct Google Form entry ID
2. `6609a7b` - Fixed QR using Google Chart API
3. `b36a415` - Switched to QR Server API to avoid CSP issues
4. `44545f2` - Added CSP meta tag (didn't work - GitHub overrides)
5. **Final Solution** - Self-hosted QRCode.js library locally

---

## Next Steps to Try

### Option 1: Allow Unsafe Eval (If Acceptable)
Modify Jekyll `_config.yml` to add CSP meta tag allowing unsafe-eval:
```yaml
# Add to _includes/head.html or _config.yml
meta:
  - http-equiv: "Content-Security-Policy"
    content: "script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net;"
```

### Option 2: Self-Host QR Library
- Download QRCode.js or QRious locally
- Place in `/assets/js/` directory
- Load from local path instead of CDN
- May still face eval restrictions

### Option 3: Pure CSS/HTML QR (Complex)
- Generate QR code server-side during Jekyll build
- Not dynamic (won't refresh every 30 seconds)

### Option 4: Alternative Hosting
- Host attendance page on a different platform without CSP
- Netlify, Vercel, or custom server
- Link from main GitHub Pages site

### Option 5: Simplify to Static Link
- Generate one QR code per class session manually
- No auto-refresh, just link to form
- Loses timestamp automation benefit

---

## Files Modified
- `_pages/attendance-qr.md` - Main attendance QR page (updated to use local library)
- `assets/js/qrcode.min.js` - Self-hosted QRCode.js library (19KB)
- `_includes/head.html` - Added CSP meta tag (ineffective due to GitHub server-level CSP)
- `QR_ATTENDANCE_SUMMARY.md` - This documentation

---

## Final Solution ✅

**Self-hosted QRCode.js library** successfully resolves all CSP issues:

1. ✅ QR codes generate dynamically every 30 seconds
2. ✅ Works on GitHub Pages (CSP allows 'self' origin)
3. ✅ No external dependencies or API calls
4. ✅ Pre-fills Google Form with session date/time
5. ✅ Students only enter First Name and Last Name
6. ✅ Google automatically collects email and submission timestamp

**Live URL**: https://sorujov.github.io/attendance/math-stat-1/
