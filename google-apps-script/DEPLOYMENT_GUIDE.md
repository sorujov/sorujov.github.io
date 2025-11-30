# Google Apps Script Deployment Guide

## Step 1: Create New Apps Script Project

1. Go to https://script.google.com/
2. Click **"New Project"**
3. Name it: `QR Attendance Validator`

## Step 2: Copy the Code

1. Delete any default code in the editor
2. Copy all code from `attendance-validator.gs`
3. Paste it into the Apps Script editor
4. **IMPORTANT**: Change the `SECRET_KEY` on line 11:
   ```javascript
   const SECRET_KEY = 'MySecretKey_' + Math.random(); // Make this unique!
   ```
   **Example**: `const SECRET_KEY = 'ADA_Stats_2025_xyz789abc';`

## Step 3: Deploy as Web App

1. Click **"Deploy"** → **"New deployment"**
2. Click gear icon ⚙️ → Select **"Web app"**
3. Fill in:
   - **Description**: `QR Attendance Validator`
   - **Execute as**: `Me (your-email@gmail.com)`
   - **Who has access**: `Anyone` (no authentication)
4. Click **"Deploy"**
5. **Copy the Web App URL** - looks like:
   ```
   https://script.google.com/macros/s/ABC123...XYZ/exec
   ```
   ⚠️ **Save this URL** - you'll need it for the next step!

## Step 4: Test the Deployment

1. In Apps Script editor, click **"Run"** → Select `testSignature`
2. First time: Authorize the script (click "Review Permissions")
3. Check **"View" → "Logs"** to see the test output
4. You should see something like:
   ```
   Timestamp: 1731744000000
   Signature: a1b2c3d4e5f6g7h8
   Token: 1731744000000|a1b2c3d4e5f6g7h8
   ```

## Step 5: Update Attendance Page

Copy your **Apps Script Web App URL** and update the attendance page.

I'll do this for you now...

## Step 6: Test End-to-End

1. Visit your attendance page: `https://sorujov.github.io/attendance/math-stat-1/`
2. QR code should display
3. Scan with phone
4. Should redirect to Google Form with session time pre-filled
5. Wait 6 minutes, scan old QR → Should show "Expired" page

---

## Troubleshooting

### "Authorization required"
- Re-deploy with **"Execute as: Me"** and **"Anyone"** access
- Make sure you authorized the script

### "Invalid signature"
- Make sure `SECRET_KEY` matches in both:
  - Apps Script (line 11)
  - Attendance page JavaScript

### "Missing token"
- Check that WORKER_URL in attendance page is correct
- Should be: `https://script.google.com/macros/s/YOUR_ID/exec`

---

## Security Notes

✅ **Apps Script URL is public** - This is intentional and safe
- Token validation prevents unauthorized access
- Only valid tokens (< 5 min old) work
- Signature prevents token tampering

✅ **SECRET_KEY must match** in both places:
- Apps Script (`attendance-validator.gs` line 11)
- Attendance page JavaScript

❌ **Don't share your SECRET_KEY publicly**
- Keep it secret between your Apps Script and attendance page
- Change it if you suspect it's been compromised

---

## Advanced: Managing Multiple Classes

To use for multiple classes, you can:

1. **Option A**: Use same Apps Script, different SECRET_KEYs per class
2. **Option B**: Deploy multiple Apps Script projects (one per class)
3. **Option C**: Add class ID to token and validate in Apps Script

For now, one deployment works for all your classes!
