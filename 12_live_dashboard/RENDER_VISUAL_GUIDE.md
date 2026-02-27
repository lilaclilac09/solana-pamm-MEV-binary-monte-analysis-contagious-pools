# Render.com Deployment: Step-by-Step Visual Guide

## Overview: Your Deployment in 20-30 Minutes

Your Solana pAMM MEV Dashboard will be live and publicly accessible at a URL like:
```
https://mev-dashboard.onrender.com
```

---

## ⚙️ Step 1: Prepare Your Project for Deployment

### A. Make sure everything is committed to GitHub

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard

# Stage all changes
git add .

# Commit with a message
git commit -m "Prepare for Render deployment"

# Push to GitHub
git push origin main
```

**Verify on GitHub:**
- Go to your repository on github.com
- Confirm you see the updated files
- Make sure branch is `main`

### B. Run Pre-Deployment Check (Optional)

```bash
# Make script executable
chmod +x render_precheck.sh

# Run the verification script
./render_precheck.sh
```

---

## 🌐 Step 2: Create Render Account

1. **Visit:** https://render.com
2. **Click:** Sign Up (top right)
3. **Choose:** GitHub (to connect your GitHub account)
4. **Authorize:** Render to access your GitHub repos
5. **Done:** You're logged in

---

## 🚀 Step 3: Create a New Web Service

### A. Go to Dashboard
- Visit: https://render.com/dashboard

### B. Create Service
- Click: **New** (blue button, top area)
- Select: **Web Service** (from dropdown menu)

### C. Connect GitHub
1. You'll see: "Select a repository"
2. Find your MEV repository
3. Click: **Connect** (next to the repo name)
4. Authorize if prompted

### D. Select Repository Details
After connecting, configure:
- **Repository:** Your MEV analysis repo
- **Branch:** `main` (default)
- Click: **Continue**

---

## 📋 Step 4: Configure Service Settings

You'll see a form. Fill in **EXACTLY** as shown:

### General Settings Section

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `mev-dashboard` | Keep lowercase, no spaces |
| **Environment** | `Python 3` | Select from dropdown |
| **Region** | (Default) | Or pick closest to you |
| **Branch** | `main` | Should be pre-selected |
| **Runtime** | `Python 3.11` | From dropdown |

### Build & Deploy Section

#### 🔨 Build Command
**Exact value to paste:**
```
pip install -r 12_live_dashboard/requirements.txt
```

> ⚠️ **IMPORTANT:** The path `12_live_dashboard/requirements.txt` is required because your app is in a subdirectory!

#### ▶️ Start Command
**Exact value to paste:**
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

> ⚠️ **IMPORTANT:** This command:
> - Changes to the `12_live_dashboard/` directory
> - Starts gunicorn with proper configuration
> - Uses `mev_dashboard:server` (your Flask app variable)

#### Plan Selection
- **Select:** `Free` (for testing)
- Or **Starter** ($7/month) for better performance
- Free plan includes: auto-sleep after 15 min inactivity

### Environment Variables (Optional)

If your dashboard needs API keys or secrets:

1. Scroll to: **Environment** section
2. Click: **Add Environment Variable**
3. Enter pairs like:
   ```
   SOLANA_RPC_URL = https://api.mainnet-beta.solana.com
   API_KEY = your_secret_key_here
   ```

4. Access in your Python code:
   ```python
   import os
   rpc_url = os.getenv('SOLANA_RPC_URL')
   ```

---

## ✅ Step 5: Deploy!

1. **Verify all settings one more time:**
   - Build Command: ✓ `pip install -r 12_live_dashboard/requirements.txt`
   - Start Command: ✓ `cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server`

2. **Click:** **Create Web Service** (blue button at bottom)

3. **Watch the magic:**
   - Status changes to "Building"
   - Render downloads your repo
   - Installs dependencies
   - Starts your app
   - Takes 5-10 minutes first time

---

## 📊 Step 6: Monitor Deployment

### A. View Build Progress

Render shows live logs as it builds:

```
Building...
Cloning repository...
Installing dependencies...
Running: pip install -r 12_live_dashboard/requirements.txt
...
Build complete!
Starting service...
```

### B. Check Service Status

Top of the page shows:
- **Building** (in progress)
- **Live** (ready to use!) ✅
- **Failed** (debug from logs)

### C. Access Your Dashboard

Once status is **Live**:

1. Render shows your public URL (e.g., `https://mev-dashboard.onrender.com`)
2. Click the link OR copy-paste into browser
3. Your dashboard loads! 🎉

---

## 🧪 Step 7: Verify It Works

### Test Your Dashboard

1. **Load the page:**
   - Does the page load without errors?
   - Do charts appear?
   - Do interactive elements work?

2. **Check Logs for Errors:**
   - Go to: **Logs** tab on Render dashboard
   - Look for red error messages
   - Python stack traces indicate problems

3. **Common Issues:**

| Problem | Solution |
|---------|----------|
| Page won't load | Check logs for Python errors |
| Blank page | Check browser console (F12) for JS errors |
| 404 errors | Verify Build/Start commands are exact |
| Slow loading | Free plan sleeps after 15 min; upgrade for continuous |

---

## 🔄 Step 8: Auto-Deployment on Updates

Render automatically redeploys when you push to `main`:

```bash
# Make changes to your local code
# ... edit mev_dashboard.py, etc ...

# Commit and push
git add .
git commit -m "Update dashboard features"
git push origin main

# Render automatically rebuilds (watch logs in dashboard)
# New version live in 2-3 minutes
```

---

## 📱 Share Your Dashboard

Your public URL (once live):
```
https://mev-dashboard.onrender.com
```

**Share directly:**
- Email the link
- Post on social media
- Add to your portfolio/website
- No authentication required (public)

---

## 🔐 Security Note

Your dashboard is **publicly accessible** by default.

If you need authentication:
- Upgrade to Paid plan
- Implement login in Dash (advanced)
- Use private URL with `.onrender.com` domain

---

## 📈 Performance Tips

### Free Plan (What you get):
- ✅ Automatic sleep after 15 minutes of inactivity
- ✅ Auto-wake when accessed again
- ✅ Zero downtime deployments
- ✅ Auto-redeploy on git push
- ❌ Slower than paid plans
- ❌ Limited to 1 concurrent request

### Upgrade to Starter ($7/month):
- ✅ Always on (no sleep)
- ✅ Better performance (2 workers)
- ✅ Custom domain support
- ✅ Higher quotas
- ✅ Priority support

---

## 🚨 Troubleshooting

### Build Failed
**Check:**
- Requirements.txt syntax (typos?)
- Python packages exist (try `pip install -r requirements.txt` locally)
- No duplicate packages listed

**Fix:**
```bash
# Test locally
pip install -r 12_live_dashboard/requirements.txt

# If error, update requirements.txt
git add requirements.txt
git commit -m "Fix requirements"
git push origin main
# Render auto-rebuilds
```

### Start Command Failed
**Check:**
- Is `server = app.server` in `mev_dashboard.py`? (✅ Yes, you have it)
- Is gunicorn in requirements.txt? (✅ Yes)
- Are Build/Start commands exact?

**Most common issue:**
- Wrong start command syntax
- Typo in `mev_dashboard:server`
- Missing `cd 12_live_dashboard &&` prefix

**Fix:**
```
Start Command (EXACT):
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

### Dashboard Loads Slowly
**Free plan:** Normal after 15-minute sleep
**Solution:** Wait 30 seconds after first access

**Persistent slowness:**
- Upgrade to Starter plan
- Reduce data processing in app
- Use caching for static data

### Errors in Logs
**Look for Python stack traces:**
- Missing imports → Add to requirements.txt
- File not found → Check paths (no local hardcoded paths)
- Port already in use → Rarely happens on Render

---

## 📞 Getting Help

### Render Support
- Render Docs: https://render.com/docs
- Help & Support: https://render.com/help
- Status: https://status.render.com

### Dash Support
- Docs: https://dash.plotly.com
- Community: https://community.plotly.com

### Your Dashboard Issues
- Check Python version (3.8+)
- Verify all imports in requirements.txt
- Test locally: `python mev_dashboard.py`

---

## 📚 Quick Reference Cheat Sheet

### Essential URLs
```
GitHub: https://github.com/YOUR_USERNAME/YOUR_REPO
Render Dashboard: https://render.com/dashboard
Your Dashboard: https://mev-dashboard.onrender.com
```

### Essential Commands (from 12_live_dashboard/ directory)

**Test locally before deploying:**
```bash
pip install -r requirements.txt
python mev_dashboard.py
# Visit http://localhost:8050
```

**Deploy updates:**
```bash
git add .
git commit -m "Your message"
git push origin main
# Wait 2-3 min, refresh your Render dashboard URL
```

### Build Command (Copy-Paste)
```
pip install -r 12_live_dashboard/requirements.txt
```

### Start Command (Copy-Paste)
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

---

## ✨ Success Checklist

- [ ] Code pushed to GitHub `main` branch
- [ ] Render account created
- [ ] Web Service created
- [ ] All settings configured (especially Build/Start Commands)
- [ ] Clicked "Create Web Service"
- [ ] Build completed (status changed to "Live")
- [ ] Dashboard loads at `.onrender.com` URL
- [ ] All charts and features work
- [ ] URL works from different devices/browsers
- [ ] Ready to share with the world! 🎉

---

**Timeline:**
| Step | Time |
|------|------|
| Account + GitHub connection | 5 min |
| Service configuration | 5 min |
| Build & deployment | 5-10 min |
| Verification | 3 min |
| **Total** | **20-30 min** |

---

**Your dashboard is ready to deploy! 🚀**

Questions? Check the Logs tab on your Render dashboard for detailed error messages.
