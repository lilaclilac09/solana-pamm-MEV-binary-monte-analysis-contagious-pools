# Render Deployment: Field-by-Field Reference

Use this while filling out the Render dashboard form.

---

## Form Fields - Exact Values

### Service Information Section

#### Name
```
mev-dashboard
```
- Use lowercase
- No spaces
- This creates subdomain: mev-dashboard.onrender.com

#### Environment (Dropdown)
```
Python 3
```
- Must select from dropdown
- Not "Python 3.11" - that's Runtime (below)

#### Region (Dropdown)
```
(Default or closest to you)
```
- Leave default OR choose your region
- Affects latency and availability

#### Branch (Dropdown)
```
main
```
- Your repo's main branch
- Auto-updates on push to this branch

---

### Build Configuration Section

#### Runtime (Dropdown)
```
Python 3.11
```
- Select from available options
- Python 3.8+ will work
- 3.11 is recommended

#### Build Command (Text Field)
```
pip install -r 12_live_dashboard/requirements.txt
```

**MUST INCLUDE:** `12_live_dashboard/` path  
**DO NOT USE:** Just `requirements.txt` (will fail!)

**Paste into field:**
1. Click in field
2. Cmd+A (select all existing text)
3. Paste from above
4. Verify path shows: `12_live_dashboard/requirements.txt`

#### Start Command (Text Field)
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

**MUST INCLUDE:** `cd 12_live_dashboard &&` (changes directory)  
**MUST END WITH:** `mev_dashboard:server` (your Flask app)  
**DO NOT CHANGE:** `$PORT`, `--bind 0.0.0.0`

**Paste into field:**
1. Click in field
2. Cmd+A (select all existing text)
3. Paste from above
4. Verify format (especially beginning and ending)

---

### Plan Selection Section

#### Plan (Radio or Dropdown)
```
Free
```

**Options:**
- **Free** (Recommended) - $0/month, auto-sleep after 15 min
- **Starter** - $7/month, always-on, better performance
- **Pro** - $50+/month, advanced features

**Choose Free for** - Testing, demos, portfolios  
**Choose Starter for** - Production dashboards, always-on

---

## Field Appearance Reference

```
┌─────────────────────────────────────────────┐
│ New Web Service Configuration               │
├─────────────────────────────────────────────┤
│                                             │
│ Service Information                         │
│ ┌─────────────────────────────────────────┐ │
│ │ Name           [mev-dashboard]          │ │
│ │ Environment    [Python 3 ▼]             │ │
│ │ Region         [(Default) ▼]            │ │
│ │ Branch         [main ▼]                 │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Build & Deploy                              │
│ ┌─────────────────────────────────────────┐ │
│ │ Runtime        [Python 3.11 ▼]          │ │
│ │                                         │ │
│ │ Build Command:                          │ │
│ │ [pip install -r 12_live_dashboard/..] │ │
│ │                                         │ │
│ │ Start Command:                          │ │
│ │ [cd 12_live_dashboard && gunicorn...] │ │
│ │                                         │ │
│ │  Auto-Deploy on Push                   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Instance Type                               │
│ ┌─────────────────────────────────────────┐ │
│ │ Type: Web Service (WSGI)                │ │
│ │ Memory: 512 MB                          │ │
│ │ CPU: Shared                             │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Plan                                        │
│ ┌─────────────────────────────────────────┐ │
│ │ ◉ Free                                   │ │
│ │ ○ Starter                               │ │
│ │ ○ Pro                                   │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Cancel]                [Create Web Service]│
└─────────────────────────────────────────────┘
```

---

## Copy Blocks (Use Cmd+C to Copy)

### Build Command (One Block)
```
pip install -r 12_live_dashboard/requirements.txt
```

### Start Command (One Block)
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

---

## Verification Checklist

After filling each field, verify:

- [ ] Name: `mev-dashboard` (lowercase, no spaces)
- [ ] Environment: `Python 3` (from dropdown)
- [ ] Region: Selected or default
- [ ] Branch: `main`
- [ ] Runtime: `Python 3.11` (from dropdown)
- [ ] Build includes: `12_live_dashboard/requirements.txt`
- [ ] Start includes: `cd 12_live_dashboard &&`
- [ ] Start includes: `mev_dashboard:server`
- [ ] Plan: `Free` selected (or paid if preferred)
- [ ] All text fields match exactly

---

## What Each Command Does

### Build Command Explained
```
pip install -r 12_live_dashboard/requirements.txt
         │                  │
         │                  └─ The requirements file
         │
         └─ Install packages from file
```

- Runs when service is created and on each deploy
- Installs all Python dependencies
- Must include full path since app is in subdirectory

### Start Command Explained
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
│                       │        │       │           │     │       │     │       │
│                       │        │       │           │     │       │     │       └─ Flask app variable
│                       │        │       │           │     │       │     └─ App module name
│                       │        │       │           │     │       └─ Timeout (seconds)
│                       │        │       │           │     └─ Worker processes
│                       │        │       │           └─ All network interfaces
│                       │        │       └─ Bind to port
│                       │        └─ HTTP server
│                       └─ Python package (installed with pip)
│
└─ Change to directory with app
```

- Change to correct directory
- Start Gunicorn web server
- Bind to port (Render provides via $PORT)
- Use Flask server variable

---

## Common Mistakes & Fixes

###  Wrong Build Command
```
pip install -r requirements.txt
          ← Missing "12_live_dashboard/"
```
**Fix:**
```
pip install -r 12_live_dashboard/requirements.txt
```

###  Wrong Start Command (Missing cd)
```
gunicorn --bind 0.0.0.0:$PORT mev_dashboard:server
  ↑ Missing "cd 12_live_dashboard &&" prefix
```
**Fix:**
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

###  Wrong Start Command (Wrong server variable)
```
cd 12_live_dashboard && gunicorn mev_dashboard:app
                                                 ↑ Should be "server" not "app"
```
**Fix:**
```
cd 12_live_dashboard && gunicorn mev_dashboard:server
                                                ↑ Correct variable
```

###  Wrong Environment Selection
```
Environment: Python 3.11
     ↑ Should be "Python 3" not the version number
```
**Fix:**
```
Environment: Python 3 ← Select this from dropdown
Runtime: Python 3.11 ← Version goes here
```

---

## Settings Comparison Chart

| Feature | Free | Starter | Pro |
|---------|------|---------|-----|
| Price | $0 | $7 | $50+ |
| Status | Auto-sleep | Always-on | Always-on |
| Workers | 1 | 2 | 4+ |
| Memory | 512 MB | 2 GB | 8+ GB |
| Domain | .onrender.com | Custom | Custom |
| Build Time | 5-10 min | 5-10 min | 5-10 min |
| First Deploy | 5-10 min | 5-10 min | 5-10 min |

**For MVP/Testing:** Free  
**For Production:** Starter+

---

## After Clicking "Create Web Service"

1. **Service is created** → Status: "Building"
2. **Build starts** → Watch Logs
3. **Dependencies install** → See pip output
4. **Server starts** → See Flask startup
5. **Status changes** → "Live"
6. **URL appears** → Click to access

---

## Troubleshooting During Deployment

### Issue: Status stuck on "Building"
**Check:** Logs tab for errors
- If red text: syntax error in requirements.txt or build command
- **Fix:** Cancel, update files locally, git push, try again

### Issue: Status changes to "Live" but page won't load
**Check:** Refresh page (might be caching)
**Check:** Browser console (F12) for errors
**Check:** Render Logs tab for Python errors

### Issue: Page loads but no content
**Check:** Render Logs tab
- Should see "Starting Flask app..."
- Should see no red Python errors
- **Fix:** Check if data files exist, paths are correct

---

## Access Your Live Dashboard

Once status is "Live":

```
Your URL will be:  https://mev-dashboard.onrender.com
```

Add to:
- Bookmarks
- Portfolio
- Resume
- Social media
- Share with others

---

## Quick Copy-Paste Commands

**If you need to redo something locally:**

```bash
# Navigate to your dashboard folder
cd 12_live_dashboard

# Test build command locally
pip install -r requirements.txt

# Test app locally
python mev_dashboard.py
# Should say: Starting Solana pAMM MEV Dashboard...
# Visit: http://127.0.0.1:8050

# When done, commit and push
git add .
git commit -m "Update dashboard"
git push origin main
# Render auto-redeploys
```

---

## Need Help?

1. **Settings unclear?** → See "Field Appearance Reference" above
2. **Command wrong?** → See "Copy Blocks" section above
3. **Build fails?** → See "Common Mistakes & Fixes" above
4. **App won't load?** → See "Troubleshooting" above
5. **More help?** → Read [RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md)

---

**You have everything you need. Your dashboard is ready to deploy!** 

Print this page or keep it open in one window, Render dashboard in another. 
