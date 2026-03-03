# Heroku Deployment Guide for MEV Dashboard

**Alternative to Render** - Free tier available with sleep mechanism

---

##  What You Have Ready

Your project is already configured for Heroku:
-  `Procfile` - Startup command
-  `runtime.txt` - Python version specified
-  `requirements.txt` - All dependencies
-  `mev_dashboard.py` - App with `server = app.server`

---

##  Step 1: Install Heroku CLI

### On macOS:
```bash
# Using Homebrew
brew install heroku

# Verify installation
heroku --version
```

### Or download directly:
https://devcenter.heroku.com/articles/heroku-cli

---

##  Step 2: Create Heroku Account & Login

```bash
# Create account at: https://www.heroku.com/
# Then login in terminal:

heroku login
# Opens browser to authenticate
# You're ready to deploy!
```

---

##  Step 3: Create & Deploy App

### Option A: Deploy from main repo directory

If your entire repo is on GitHub:

```bash
# Go to your main project directory
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools

# Create Heroku app
heroku create mev-dashboard

# Deploy using git subtree (for subdirectory)
git subtree push --prefix 12_live_dashboard heroku main

# View logs
heroku logs --tail
```

### Option B: Deploy from subdirectory only (Simpler)

```bash
# Copy to new directory
mkdir ~/heroku-mev-dashboard
cp -r 12_live_dashboard/* ~/heroku-mev-dashboard/
cd ~/heroku-mev-dashboard

# Initialize git (if not already)
git init
git add .
git commit -m "Initial Heroku deployment"

# Create Heroku app
heroku create mev-dashboard

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

##  Verify Deployment

After deployment completes:

```bash
# Open your app in browser
heroku open

# Check if app is running
heroku ps

# View recent logs
heroku logs -n 50
```

Visit: `https://mev-dashboard.herokuapp.com`

Your dashboard should load with all charts! 

---

##  Step 4: Add Custom Domain (Optional)

You already have **mev.aileena.xyz** on Render. To use same domain on Heroku:

### A. Add domain to Heroku app:
```bash
heroku domains:add mev.aileena.xyz
```

Heroku returns something like:
```
Configure your app to use the domain mev.aileena.xyz
where is your DNS provider? (e.g., namecheap, godaddy)
Get the DNS target value for CNAME/ALIAS:
target: mev-dashboard.herokuapp.com
```

### B. Update DNS records:

1. Go to your DNS provider (where you manage aileena.xyz)
2. Find your DNS records
3. For `mev` subdomain, update:
   - **Current (Render):** Points to Render
   - **New (Heroku):** Create separate or update

**Option 1: Load balance both**
Add CNAME record: `mev.aileena.xyz` → `mev-dashboard.herokuapp.com`

**Option 2: Keep Render, create new subdomain**
Create: `heroku-mev.aileena.xyz` → `mev-dashboard.herokuapp.com`

---

##  Free Tier Details

### Limitations:
-  Free until you verify payment method
- ⏸️ Sleeps after 30 min inactivity
- ⏱️ 550 hours/month (enough for always-on during US business hours)
-  512 MB RAM
-  Single dyno only

### Wake-up:
- First request wakes app (takes 5-10 seconds)
- After wake-up: runs normally

### To upgrade:
```bash
heroku ps:scale web=1:standard-1x
# Costs $7/month, always-on
```

---

##  Deploy Updates

### From subdirectory:
```bash
cd 12_live_dashboard

# Make changes
# Edit mev_dashboard.py

# Deploy
git add .
git commit -m "Update dashboard"
git push heroku main
```

### From main repo with subtree:
```bash
git add .
git commit -m "Update dashboard"
git subtree push --prefix 12_live_dashboard heroku main
```

---

## 🆘 Troubleshooting

### App won't start
```bash
heroku logs --tail
```
Look for Python errors, missing imports, etc.

### Check for common issues:
```bash
# Test locally first
python3 mev_dashboard.py
# Should say "Running on 0.0.0.0:8050"

# Check gunicorn can start
gunicorn mev_dashboard:server
```

### Rebuild without cache:
```bash
git push heroku main --force-with-lease
```

### Check if dependencies are in requirements.txt:
```bash
cat requirements.txt | grep -E "dash|plotly|gunicorn"
# Should show all three
```

---

##  Scale Up (Optional)

For production use:

```bash
# Upgrade to paid dyno (always-on)
heroku ps:scale web=1:standard-1x

# Upgrade plan
heroku apps:info -a mev-dashboard
```

---

##  Quick Reference

| Action | Command |
|--------|---------|
| Create app | `heroku create mev-dashboard` |
| Deploy | `git push heroku main` |
| View logs | `heroku logs --tail` |
| Open app | `heroku open` |
| Check status | `heroku ps` |
| Scale up | `heroku ps:scale web=1:standard-1x` |
| Add domain | `heroku domains:add mev.aileena.xyz` |
| Destroy app | `heroku apps:destroy mev-dashboard` |

---

##  Comparison: Render vs Heroku

| Feature | Render | Heroku |
|---------|--------|--------|
| Free tier |  Yes |  Yes |
| Always-on |  No (sleeps) |  No (sleeps) |
| Custom domain |  Yes |  Yes |
| Auto-deploy |  Yes (git push) | ️ Manual (git push) |
| Uptime | 99% | 99% |
| Setup | Easy | Easy |
| Price (paid) | $7/mo | $7/mo |
| **Current Status** | ** LIVE** |  Ready |

---

##  You're Ready!

Your dashboard is configured for **both** Render and Heroku:
1. **Render (Current)**: mev.aileena.xyz 
2. **Heroku (Optional)**: Ready to deploy

Choose one or run both!

---

## Next Steps

1. **Install Heroku CLI:**
   ```bash
   brew install heroku
   ```

2. **Create account at:** https://www.heroku.com/

3. **Deploy:**
   ```bash
   heroku login
   heroku create mev-dashboard
   git push heroku main  # or use git subtree for subdirectory
   ```

4. **Test:**
   ```bash
   heroku open
   ```

---

##  Support

- Heroku Docs: https://devcenter.heroku.com/
- Dash on Heroku: https://dash.plotly.com/deployment
- Heroku CLI Reference: https://devcenter.heroku.com/articles/heroku-cli-commands

---

**Your dashboard is deployment-ready!** Choose Render (already live) or Heroku (setup on demand). 
