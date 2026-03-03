# Render Deployment: Quick Reference Card

**Print this page or keep it open while deploying!**

---

## URL Shortcuts

| What | URL |
|------|-----|
| Render Dashboard | https://render.com/dashboard |
| Render Sign Up | https://render.com |
| Your GitHub Repo | [your-repo-link] |
| Your Dashboard (after deploy) | https://mev-dashboard.onrender.com |

---

## Exact Copy-Paste Values for Render Dashboard

### COPY & PASTE THESE INTO RENDER SETTINGS:

#### Name (Lowercase, no spaces)
```
mev-dashboard
```

#### Environment (Select from dropdown)
```
Python 3
```

#### Region (Default OK, or choose closest)
```
(Leave as default)
```

#### Branch
```
main
```

#### Runtime (Select from dropdown)
```
Python 3.11
```

####  BUILD COMMAND (Copy the entire thing)
```
pip install -r 12_live_dashboard/requirements.txt
```

**After pasting:** 
- Click field
- Select all (Cmd+A)
- Paste from above
- Verify:  Path includes `12_live_dashboard/`

---

#### ▶️ START COMMAND (Copy the entire thing)
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

**After pasting:**
- Click field  
- Select all (Cmd+A)
- Paste from above
- Verify:  Includes `cd 12_live_dashboard &&`
- Verify:  Ends with `mev_dashboard:server`

---

#### Plan
```
Free (recommended for testing)
```

---

## Step-by-Step Git Commands

**Before deploying, run from 12_live_dashboard/ directory:**

```bash
# Check status
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Prepare MEV dashboard for Render deployment"

# Push to GitHub
git push origin main

#  Verify on GitHub.com - you should see updated files
```

---

## Render Dashboard Creation Steps

1. Go to: https://render.com/dashboard
2. Click: **New** → **Web Service**
3. Select: Your GitHub repository
4. Choose: **main** branch
5. Fill in the settings above (Build Command, Start Command, etc.)
6. Click: **Create Web Service**
7. Wait: 5-10 minutes
8. Check: Status changes to "Live"
9. Visit: Your `.onrender.com` URL

---

## Verify Deployment Works

**When status = "Live":**

1. Click the `.onrender.com` link
2. Dashboard should load
3. Check:
   - Charts visible? 
   - Interactive elements work? 
   - No red errors? 
4. Open **Logs** tab:
   - Look for: `Starting app...` or similar
   - No Python errors? 

---

## If Something Goes Wrong

| Symptom | Check |
|---------|-------|
| Build failed | Look at Logs tab, check requirements.txt |
| Won't start | Check Start Command syntax (must be exact) |
| Page won't load | Check Build Command path (must include `12_live_dashboard/`) |
| Blank page | Check browser console (F12) for errors |
| Timeout errors | Increase `--timeout 180` in Start Command |

---

## Update Your Dashboard Later

```bash
# Make changes to code
# ... edit files ...

# Commit and push
git add .
git commit -m "Update dashboard"
git push origin main

#  Render auto-rebuilds (watch logs)
#  New version live in 2-3 minutes
```

---

## Key Files in Your Project

**These must exist:**
-  `mev_dashboard.py` - Your Dash app
-  `requirements.txt` - Dependencies
-  `Procfile` - Startup configuration (Render optional)
-  `server = app.server` - In mev_dashboard.py

**Directory structure:**
```
your-repo/
├── 12_live_dashboard/          ← THIS IS THE DEPLOYMENT FOLDER
│   ├── mev_dashboard.py        ← Main app (has server = app.server)
│   ├── requirements.txt        ← Dependencies
│   ├── Procfile                ← Startup config
│   └── ... other files ...
└── ... other folders ...
```

---

## Common Settings Mistakes

 **WRONG:**
```
Build: pip install -r requirements.txt
(Missing 12_live_dashboard/)

Start: gunicorn --bind 0.0.0.0:$PORT mev_dashboard:server
(Missing cd 12_live_dashboard &&)
```

 **RIGHT:**
```
Build: pip install -r 12_live_dashboard/requirements.txt

Start: cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

---

## How to Read Render Logs

**Good signs:**
```
Building...
Cloning repository...
Installing dependencies...
Build successful!
Running service...
Starting application...
```

**Bad signs (red text):**
```
ERROR: Could not find a version...
ModuleNotFoundError: No module named...
SyntaxError: invalid syntax
```

If you see red errors:
1. Copy the error message
2. Check if package is in requirements.txt
3. Fix locally: `pip install -r 12_live_dashboard/requirements.txt`
4. Commit: `git add . && git commit -m "Fix dependencies"`
5. Push: `git push origin main`
6. Render auto-rebuilds

---

## Your Dashboard is Ready!

**Your file structure is correct:**
-  mev_dashboard.py exists
-  server = app.server is defined  
-  requirements.txt has all dependencies
-  gunicorn is listed

**You can proceed with deployment immediately!**

---

## Desktop Version (Side-by-Side)

**Left Monitor (This Guide):**
- [RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md) ← Full detailed guide
- [RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md) ← Checklist

**Right Monitor (Render Dashboard):**
- https://render.com/dashboard
- Fill in settings
- Monitor logs

---

**Estimated Total Time: 20-30 minutes**

Questions? Click "Logs" tab on Render for detailed error messages.

Good luck! 
