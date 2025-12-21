# ☁️ Cloud Storage Upload Setup Guide

## Overview
Enable users to upload videos directly from **Google Drive** and **Dropbox** without downloading to their device first.

**Note:** This is **optional** - the system works with local file uploads without any cloud setup.

---

## 🌐 Google Drive Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project:**
   - Click "Select a project" dropdown (top left)
   - Click "NEW PROJECT"
   - Project name: `Video-Captioning-App` (or your choice)
   - Click "CREATE"
   - Wait for project creation (10-20 seconds)

3. **Select Your Project:**
   - Click "Select a project" dropdown again
   - Choose your newly created project

### Step 2: Enable Google Drive API

1. **Navigate to APIs & Services:**
   - In left sidebar, click "APIs & Services" → "Library"
   - Or visit: https://console.cloud.google.com/apis/library

2. **Enable Drive API:**
   - Search for "Google Drive API"
   - Click on "Google Drive API"
   - Click "ENABLE" button
   - Wait for activation (~5 seconds)

3. **Enable Picker API:**
   - Search for "Google Picker API"
   - Click on "Google Picker API"
   - Click "ENABLE" button

### Step 3: Create API Key

1. **Go to Credentials:**
   - Click "APIs & Services" → "Credentials" in left sidebar
   - Or visit: https://console.cloud.google.com/apis/credentials

2. **Create API Key:**
   - Click "+ CREATE CREDENTIALS" (top)
   - Select "API key"
   - Copy the generated key (starts with `AIza...`)
   - Click "RESTRICT KEY" (recommended)

3. **Restrict API Key (Recommended):**
   - Under "API restrictions", select "Restrict key"
   - Check these APIs:
     - ✅ Google Drive API
     - ✅ Google Picker API
   - Under "Application restrictions":
     - Select "HTTP referrers (web sites)"
     - Add referrer: `http://localhost:5000/*` (for local development)
     - Add referrer: `https://yourdomain.com/*` (for production)
   - Click "SAVE"

4. **Save Your API Key:**
   ```
   Example: AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
   ```

### Step 4: Create OAuth 2.0 Client ID

1. **Configure Consent Screen (First Time Only):**
   - Go to "OAuth consent screen" tab
   - Select "External" (unless G Suite user)
   - Click "CREATE"
   - Fill required fields:
     - App name: `Video Captioning System`
     - User support email: Your email
     - Developer contact: Your email
   - Click "SAVE AND CONTINUE"
   
   - **Scopes Configuration (IMPORTANT):**
     - Click "ADD OR REMOVE SCOPES"
     - Search and add these scopes:
       - ✅ `https://www.googleapis.com/auth/drive.readonly` - View files in Drive
       - ✅ `https://www.googleapis.com/auth/drive.file` - View/manage files created by this app
       - ✅ `openid` - Authenticate identity (required for sign-in)
       - ✅ `https://www.googleapis.com/auth/userinfo.profile` - View basic profile info
       - ✅ `https://www.googleapis.com/auth/userinfo.email` - View email address
     - Click "UPDATE" at bottom
     - Click "SAVE AND CONTINUE"
   
   - Test users: Add your email
   - Click "SAVE AND CONTINUE"
   - Click "BACK TO DASHBOARD"

2. **Create OAuth Client ID:**
   - Go back to "Credentials" tab
   - Click "+ CREATE CREDENTIALS"
   - Select "OAuth client ID"
   - Application type: "Web application"
   - Name: `Video Captioning Web Client`

3. **Configure Authorized Origins:**
   - Under "Authorized JavaScript origins", click "+ ADD URI"
   - Add: `http://localhost:5000` (for local development)
   - Add: `https://yourdomain.com` (for production deployment)

4. **Configure Redirect URIs (Optional):**
   - Under "Authorized redirect URIs", click "+ ADD URI"
   - Add: `http://localhost:5000/oauth2callback`

5. **Create and Save:**
   - Click "CREATE"
   - **Copy Your Client ID** (looks like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
   - Click "OK"

### Step 5: Configure Environment Variables

1. **Open `.env` file in project root:**
   ```bash
   # Windows
   notepad .env

   # Mac/Linux
   nano .env
   ```

2. **Add Google Drive credentials:**
   ```env
   # Google Drive Configuration
   GOOGLE_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
   GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
   ```

3. **Save the file**

### Step 6: Test Google Drive Integration

1. **Restart Flask server:**
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   python app.py
   ```

2. **Open browser:**
   - Go to: http://localhost:5000
   - You should see "Google Drive" button in upload section
   - Click it to test file picker

---

## 📦 Dropbox Setup

### Step 1: Create Dropbox App

1. **Go to Dropbox App Console:**
   - Visit: https://www.dropbox.com/developers/apps
   - Sign in with your Dropbox account

2. **Create New App:**
   - Click "Create app" button
   - Choose API: **Scoped access**
   - Choose access type: **Full Dropbox** (or "App folder" for restricted access)
   - Name your app: `video-captioning-app` (must be unique globally)
   - Check the agreement box
   - Click "Create app"

### Step 2: Configure App Permissions

1. **Navigate to Permissions Tab:**
   - In your app settings, click "Permissions" tab

2. **Enable Required Permissions:**
   - Under "Files and folders", check:
     - ✅ `files.metadata.read` - View information about files
     - ✅ `files.content.read` - View content of files
     - ✅ `sharing.read` - View sharing settings

3. **Submit Changes:**
   - Click "Submit" button at bottom

### Step 3: Configure App Settings

1. **Go to Settings Tab:**
   - Click "Settings" tab in your app

2. **Add Redirect URIs:**
   - Scroll to "OAuth 2" section
   - Under "Redirect URIs", add:
     - `http://localhost:5000` (for local development)
     - `https://yourdomain.com` (for production)
   - Click "Add"

3. **Configure CORS (Optional):**
   - Scroll to "CORS" section
   - Add allowed origins:
     - `http://localhost:5000`
     - `https://yourdomain.com`

### Step 4: Get App Key

1. **Find Your App Key:**
   - Stay on "Settings" tab
   - Scroll to "App key" section
   - Copy the **App key** (looks like: `abcdefgh1234567`)

### Step 5: Configure Environment Variables

1. **Open `.env` file:**
   ```bash
   # Windows
   notepad .env

   # Mac/Linux
   nano .env
   ```

2. **Add Dropbox credentials:**
   ```env
   # Dropbox Configuration
   DROPBOX_APP_KEY=abcdefgh1234567
   ```

3. **Save the file**

### Step 6: Test Dropbox Integration

1. **Restart Flask server:**
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   python app.py
   ```

2. **Open browser:**
   - Go to: http://localhost:5000
   - You should see "Dropbox" button in upload section
   - Click it to test file picker

---

## 📝 Complete .env File Example

Create or edit `.env` file in project root:

```env
# =============================================================================
# CLOUD STORAGE CONFIGURATION
# =============================================================================

# Google Drive Setup (Optional)
# Get these from: https://console.cloud.google.com/
GOOGLE_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# Dropbox Setup (Optional)
# Get this from: https://www.dropbox.com/developers/apps
DROPBOX_APP_KEY=abcdefgh1234567

# =============================================================================
# OPENAI CONFIGURATION (Optional - for advanced AI summaries)
# =============================================================================
# OPENAI_API_KEY=sk-...

# =============================================================================
# FLASK CONFIGURATION
# =============================================================================
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
```

**Important:**
- Replace example values with your actual keys
- Don't commit `.env` to Git (already in `.gitignore`)
- Keep keys secret and secure

---

## ✅ Verification Checklist

### Google Drive Setup Complete When:
- [ ] Google Cloud project created
- [ ] Google Drive API enabled
- [ ] Google Picker API enabled
- [ ] API Key created and copied
- [ ] OAuth Client ID created and copied
- [ ] Both keys added to `.env` file
- [ ] "Google Drive" button appears in web interface

### Dropbox Setup Complete When:
- [ ] Dropbox app created
- [ ] Permissions configured
- [ ] App key copied
- [ ] Key added to `.env` file
- [ ] "Dropbox" button appears in web interface

---

## 🚀 Testing Cloud Integration

### Test Google Drive:
1. Start server: `python app.py`
2. Open: http://localhost:5000
3. Click "Google Drive" button
4. Sign in to Google account
5. Select a video file
6. Should start uploading/processing

### Test Dropbox:
1. Start server: `python app.py`
2. Open: http://localhost:5000
3. Click "Dropbox" button
4. Sign in to Dropbox account
5. Select a video file
6. Should start uploading/processing

---

## ⚠️ Troubleshooting

### Issue: "Google Drive button not showing"
**Solutions:**
1. Check `.env` file has correct `GOOGLE_API_KEY` and `GOOGLE_CLIENT_ID`
2. Restart Flask server after changing `.env`
3. Clear browser cache (Ctrl+F5)
4. Check browser console for JavaScript errors

### Issue: "Dropbox button not showing"
**Solutions:**
1. Check `.env` file has correct `DROPBOX_APP_KEY`
2. Restart Flask server after changing `.env`
3. Clear browser cache (Ctrl+F5)

### Issue: "Google sign-in popup blocked"
**Solution:** 
- Allow popups for localhost:5000 in browser settings
- Click popup blocker icon in address bar
- Select "Always allow popups from localhost"

### Issue: "401 Unauthorized" error with Google
**Solutions:**
1. Check OAuth consent screen is configured
2. **Verify required scopes are added:**
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.file`
   - `openid` (for identity/sign-in)
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/userinfo.email`
3. Add your email as test user
4. Verify Authorized JavaScript origins includes `http://localhost:5000`
5. Make sure both APIs are enabled (Drive + Picker)

### Issue: "Invalid App Key" with Dropbox
**Solutions:**
1. Verify App Key copied correctly (no spaces)
2. Check app status is "Development" or "Production"
3. Verify redirect URIs include your domain

### Issue: "CORS error" in browser console
**Solutions:**
1. Add your domain to allowed origins in API settings
2. For Google: Add to Authorized JavaScript origins
3. For Dropbox: Add to CORS allowed origins

---

## 🔒 Security Best Practices

### 1. API Key Protection
- ✅ Never commit `.env` to Git
- ✅ Use `.gitignore` to exclude `.env`
- ✅ Restrict API keys to specific domains
- ✅ Rotate keys periodically

### 2. OAuth Security
- ✅ Use HTTPS in production (required for OAuth)
- ✅ Keep Client IDs and secrets separate
- ✅ Limit OAuth scopes to minimum needed
- ✅ Add only trusted domains to allowed origins

### 3. Production Deployment
- ✅ Use environment variables (not hardcoded)
- ✅ Enable API key restrictions
- ✅ Whitelist only production domain
- ✅ Use production OAuth credentials (not development)

---

## 📊 Quota Limits

### Google Drive API Limits (Free Tier)
- **Queries per day:** 1 billion
- **Queries per 100 seconds per user:** 1,000
- **Queries per 100 seconds:** 20,000

**For this app:** Limits are more than sufficient for typical use

### Dropbox API Limits (Free App)
- **API calls per app:** Generous limits
- **File size:** Depends on your Dropbox storage

**For this app:** Limits are sufficient unless extremely high traffic

---

## 🎯 Quick Setup Summary

**Minimal steps to enable cloud storage:**

### Google Drive (5 minutes):
1. Create project at https://console.cloud.google.com/
2. Enable Drive API + Picker API
3. Create API Key
4. Create OAuth Client ID
5. Add both to `.env` file

### Dropbox (3 minutes):
1. Create app at https://www.dropbox.com/developers/apps
2. Configure permissions (files.metadata.read, files.content.read)
3. Copy App Key
4. Add to `.env` file

**That's it!** Restart server and cloud buttons appear. 🎉

---

## 🌐 Production Deployment Notes

When deploying to production server:

1. **Update Allowed Origins:**
   - Google: Add `https://yourdomain.com` to Authorized JavaScript origins
   - Dropbox: Add `https://yourdomain.com` to Redirect URIs

2. **Use HTTPS:**
   - OAuth requires HTTPS (not HTTP) in production
   - Get SSL certificate (Let's Encrypt is free)

3. **Environment Variables:**
   - Set `.env` on production server
   - Or use server environment variables
   - Never expose keys in frontend code

4. **Domain Verification:**
   - Some providers require domain verification
   - Follow provider's domain verification process

---

## 📖 Additional Resources

### Google Drive:
- **Console:** https://console.cloud.google.com/
- **Documentation:** https://developers.google.com/drive/api/guides/about-sdk
- **Picker API:** https://developers.google.com/drive/picker

### Dropbox:
- **App Console:** https://www.dropbox.com/developers/apps
- **Documentation:** https://www.dropbox.com/developers/documentation
- **Chooser JS:** https://www.dropbox.com/developers/chooser

---

## ❓ FAQ

**Q: Do I need both Google Drive AND Dropbox?**
A: No, configure only what you need. You can have one, both, or neither.

**Q: Does this cost money?**
A: Both Google and Dropbox offer generous free tiers. For typical usage, it's free.

**Q: Can users upload from their own Google Drive/Dropbox?**
A: Yes! They sign in with their own account and select files from their storage.

**Q: Is the video downloaded to the server?**
A: Yes, the server downloads the video temporarily to process it, then deletes it.

**Q: What if I skip this setup?**
A: Local file upload still works perfectly. Cloud storage is optional convenience.

---

## ✨ Benefits of Cloud Integration

- ✅ **No local download:** Users don't need to download videos to their device first
- ✅ **Faster workflow:** Direct access to cloud storage
- ✅ **Better UX:** Seamless integration with file pickers
- ✅ **Saves bandwidth:** Direct server-to-server transfer
- ✅ **Large files:** Easier to handle large videos (2GB+)

---

**🎉 You're all set!** Cloud storage integration is now configured.
