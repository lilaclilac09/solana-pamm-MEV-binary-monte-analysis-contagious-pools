# Render Deployment Checklist

## Pre-Deployment Checklist

### Code Readiness
- [ ] All code is working locally (tested with `python mev_dashboard.py`)
- [ ] No hardcoded paths or local file references
- [ ] No credentials/API keys in code (use environment variables)
- [ ] Import statements are correct

### Repository Preparation
- [ ] GitHub repository is created and accessible
- [ ] Code is pushed to `main` branch
- [ ] `.gitignore` excludes virtual environments and cache
- [ ] No large binary files in repo (< 100MB)

### Files Present
- [ ] ✅ `mev_dashboard.py` (main app file)
- [ ] ✅ `requirements.txt` (dependencies)
- [ ] ✅ `Procfile` (startup configuration)
- [ ] ✅ Python version compatible (3.8+)

### Special Configuration
- [ ] Check if app is in subdirectory: `12_live_dashboard/` → YES
- [ ] App uses WSGI-compatible server: Dash with Flask ✅
- [ ] Server variable is defined: `server = app.server` ✅

## Render.com Setup Steps

### Account & Service Creation
- [ ] Create Render.com account at https://render.com
- [ ] Go to Dashboard: https://render.com/dashboard
- [ ] Click: **New** → **Web Service**
- [ ] Connect GitHub account (authorize Render)
- [ ] Select repository and `main` branch

### Service Configuration
Configure these settings exactly:

#### Basic Settings
- [ ] **Name:** `mev-dashboard`
- [ ] **Environment:** `Python 3`
- [ ] **Region:** (default or closest to you)
- [ ] **Branch:** `main`
- [ ] **Runtime:** `Python 3.11`

#### Build & Start Commands
```
Build Command:
pip install -r 12_live_dashboard/requirements.txt

Start Command:
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

- [ ] **Build Command:** Copy-paste exactly (includes `12_live_dashboard/` path)
- [ ] **Start Command:** Copy-paste exactly (includes directory + gunicorn call)

#### Plan Selection
- [ ] **Plan:** Select `Free` (optional: upgrade to Starter for better performance)
- [ ] **Auto-deploy:** Leave enabled (auto-redeploy on git push)

## Deployment Process

- [ ] Click **Create Web Service**
- [ ] Wait for build to complete (5-10 minutes first time)
- [ ] Monitor build logs for errors
- [ ] Service status changes from "Building" → "Live"
- [ ] Render assigns `.onrender.com` URL automatically

## Post-Deployment Verification

### Access & Testing
- [ ] Dashboard URL provided by Render (e.g., `https://mev-dashboard.onrender.com`)
- [ ] Can access dashboard without errors
- [ ] All charts and data load correctly
- [ ] Interactive features work (filters, buttons, etc.)

### Logs & Monitoring
- [ ] View logs in Render Dashboard → Your Service → Logs
- [ ] No Python errors in logs
- [ ] Flask/Gunicorn startup messages visible
- [ ] Monitor CPU and memory usage

## Troubleshooting Checklist

If deployment fails:

### Build Failed
- [ ] Check `requirements.txt` syntax (no trailing spaces, valid package names)
- [ ] Verify all dependencies are installable (`pip install -r requirements.txt` locally)
- [ ] Check Build Command path is correct for subdirectory
- [ ] Look for Python version incompatibilities

### Start Command Failed
- [ ] Verify Start Command has correct directory: `cd 12_live_dashboard &&`
- [ ] Confirm server variable exists: `server = app.server` in `mev_dashboard.py`
- [ ] Check `mev_dashboard:server` syntax matches your code
- [ ] Ensure gunicorn is in requirements.txt

### Dashboard Loads Slowly
- [ ] Increase timeout: `--timeout 180`
- [ ] Reduce data processing in initial load
- [ ] Check if data loading is blocking the server

### Module Import Errors
- [ ] All imports in code must be in requirements.txt
- [ ] Run locally: `pip install -r requirements.txt` and test
- [ ] Check for version conflicts (e.g., dash==4.0.0, flask==3.0.0)

## Updates & Maintenance

### Push Updates to Render
```bash
# Local changes
git add .
git commit -m "Update dashboard"
git push origin main

# Render auto-redeploys (watch logs in dashboard)
```

### Check Service Health
- Render Dashboard → Your Service → **Metrics**
- Monitor: CPU usage, Memory, Requests/sec
- View uptime and response times

## Estimated Timeline

| Step | Time |
|------|------|
| Account creation | 2 min |
| GitHub connection | 2 min |
| Service configuration | 5 min |
| Initial build | 5-10 min |
| Verification | 3-5 min |
| **Total** | **20-30 min** |

## Success Indicators

✅ Dashboard is live when you see:
- Green "Live" status in Render Dashboard
- `.onrender.com` URL is responsive
- Charts and data display correctly
- No errors in Logs tab
- Can access from different devices/browsers

---

## Quick Reference: Copy-Paste Commands

**Build Command (subdirectory):**
```
pip install -r 12_live_dashboard/requirements.txt
```

**Start Command (subdirectory with gunicorn):**
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

---

Last Updated: February 27, 2026
