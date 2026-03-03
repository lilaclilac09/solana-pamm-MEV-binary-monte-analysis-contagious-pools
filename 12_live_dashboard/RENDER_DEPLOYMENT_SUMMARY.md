# MEV Dashboard Render Deployment - Complete Setup

**Last Updated:** February 27, 2026  
**Status:**  Ready for Deployment  
**Estimated Deploy Time:** 20-30 minutes  

---

##  Executive Summary

Your Solana pAMM MEV Dashboard is **fully configured and ready to deploy** to Render.com. This document provides everything you need to get your dashboard live on the internet.

### What You Have
 `mev_dashboard.py` - Dash/Flask app properly configured  
 `server = app.server` - WSGI server variable defined  
 `requirements.txt` - All dependencies listed  
 `Procfile` - Startup configuration  
 Git repository - Connected to GitHub  

### What You'll Get
 Public URL: `https://mev-dashboard.onrender.com`  
 Auto-redeploy on git push  
 Free tier available (with auto-sleep)  
 No credit card required for free tier  

---

##  Documentation Files

Choose what you need:

### **Start Here:**
1. **[RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)** ← **START HERE**
   - Exact copy-paste values
   - Minimal, focused guide
   - Print-friendly
   - 5 minutes to read

### **Detailed Guides:**
2. **[RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md)**
   - Step-by-step with screenshots descriptions
   - Troubleshooting guide
   - Performance tips
   - 10 minutes to read

3. **[RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)**
   - Comprehensive technical guide
   - Architecture explanation
   - Advanced configuration
   - 15+ minutes to read

### **Checklists:**
4. **[RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md)**
   - Pre-deployment checklist
   - Configuration checklist
   - Post-deployment verification
   - Troubleshooting checklist

### **Automation:**
5. **./render_precheck.sh**
   - Automated pre-deployment verification script
   - Check if files are correct
   - Verify Git status
   - Run once before deploying

---

##  Quick Start (3 Steps)

### Step 1: Prepare Your Code (2 minutes)

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard

git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Service (10 minutes)

1. Go to: https://render.com/dashboard
2. Click: **New** → **Web Service**
3. Connect GitHub and select your repo
4. Fill in settings (see Quick Reference)
5. Click: **Create Web Service**

### Step 3: Wait & Verify (5-10 minutes)

1. Monitor build in Logs tab
2. Wait for status → "Live"
3. Click `.onrender.com` link
4. Dashboard should load 

**Total time: ~20-30 minutes**

---

## ️ Render Configuration Settings

**Copy these exactly into Render dashboard:**

**Build Command:**
```
pip install -r 12_live_dashboard/requirements.txt
```

**Start Command:**
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

**Other Settings:**
- Name: `mev-dashboard`
- Environment: `Python 3`
- Runtime: `Python 3.11`
- Branch: `main`
- Plan: `Free` (or Starter for always-on)

---

##  Features Included

### Deployment Automation
-  Auto-rebuild on `git push origin main`
-  Zero-downtime deployments
-  Auto-SSL certificate (HTTPS)
-  Free tier: auto-sleep after 15 min inactivity

### Monitoring
-  Real-time logs
-  CPU/Memory metrics
-  Response time graphs
-  Error tracking

### Scaling
-  Free: 1 worker, 512MB RAM
-  Starter: 2 workers, 2GB RAM
-  Pro: Custom scaling

---

##  Pre-Deployment Checks

Run this before deploying (optional but recommended):

```bash
cd 12_live_dashboard
chmod +x render_precheck.sh
./render_precheck.sh
```

This verifies:
-  All required files exist
-  App is properly configured
-  Server variable is defined
-  Git repository is ready

---

##  After Deployment

### Accessing Your Dashboard
- URL: `https://mev-dashboard.onrender.com`
- Public: Anyone with the link can access
- Custom domain: Available on paid plans
- HTTPS: Automatic

### Making Updates
```bash
# Edit code locally
# ... make changes ...

# Deploy
git add .
git commit -m "Update features"
git push origin main

# Render auto-rebuilds (2-3 minutes)
```

### Monitoring
- View logs: Dashboard → Logs tab
- Check metrics: Dashboard → Metrics tab
- Set alerts: Dashboard → Settings tab (paid plans)

---

## 🆘 Troubleshooting

### Build Failed
**Most common:** Wrong path in Build Command  
**Solution:** Ensure it includes `12_live_dashboard/requirements.txt`

### Start Command Failed  
**Most common:** Wrong Start Command syntax  
**Solution:** Use exact command from settings above

### Dashboard Loads Slowly  
**On Free plan:** Normal after sleep, takes 30 sec to wake  
**Solution:** Upgrade to Starter ($7/month) or refresh page

### Python Errors
**Check:**
- All imports in code are in requirements.txt
- No hardcoded local paths
- Python version compatible (3.8+)

**See:** [RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md#-troubleshooting)

---

##  Tips & Best Practices

### For Best Performance
1. **Free tier:** Good for testing, demos, portfolios
2. **Starter tier:** Good for production dashboards
3. **Paid tier:** Good for high-traffic applications

### Keep Updated
- Push changes regularly: `git push origin main`
- Monitor logs for errors: Logs tab
- Check metrics: Metrics tab

### Security
- Keep API keys in environment variables
- Don't commit `.env` files
- Use Render's secure secrets manager

### Budget
- **Free:** $0/month (with auto-sleep)
- **Starter:** $7/month (always-on)
- Both include auto-deployments on git push

---

##  Support & Resources

### Render Help
- Docs: https://render.com/docs
- Status: https://status.render.com
- Support: https://render.com/help
- Community: https://discord.gg/render

### Your Tech Stack
- Dash: https://dash.plotly.com
- Flask: https://flask.palletsprojects.com
- Gunicorn: https://gunicorn.org
- Python: https://python.org

### This Project
- Check [RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md) for detailed help
- Run `./render_precheck.sh` if issues arise
- Check Render logs for specific error messages

---

##  Next Steps Checklist

**Pre-Deployment (5 min):**
- [ ] Read [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)
- [ ] Run `./render_precheck.sh` (optional)
- [ ] Commit and push code: `git push origin main`

**Deployment (10 min):**
- [ ] Go to https://render.com/dashboard
- [ ] Create new Web Service
- [ ] Fill in settings (use Quick Reference)
- [ ] Click "Create Web Service"

**Post-Deployment (5 min):**
- [ ] Wait for "Live" status
- [ ] Click `.onrender.com` URL
- [ ] Test dashboard functionality
- [ ] Share public link

---

##  Learning Path

If you want to understand more:

1. **Quick:** Read [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md) (5 min)
2. **Visual:** Read [RENDER_VISUAL_GUIDE.md](RENDER_VISUAL_GUIDE.md) (10 min)
3. **Deep:** Read [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) (15 min)
4. **Verify:** Use [RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md) during deployment

---

##  Your Project Status

```
Project: Solana pAMM MEV Analysis Dashboard
Location: 12_live_dashboard/
Framework: Dash (Python)
Server: Flask + Gunicorn
Status:  READY FOR DEPLOYMENT

Files:
   mev_dashboard.py (app code)
   requirements.txt (dependencies)
   Procfile (config)
   server = app.server (WSGI ready)
   Git repository

Documentation:
   RENDER_QUICK_REFERENCE.md
   RENDER_VISUAL_GUIDE.md
   RENDER_DEPLOYMENT_GUIDE.md
   RENDER_DEPLOYMENT_CHECKLIST.md
   RENDER_DEPLOYMENT_SUMMARY.md (this file)
   render_precheck.sh

Next: Start with RENDER_QUICK_REFERENCE.md
```

---

##  You're Ready!

Your dashboard is fully configured and ready to deploy. Pick any of the guides above and follow along. 

**The easiest path:**
1. Open [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)
2. Follow the 3-step Quick Start
3. Your dashboard will be live in 20-30 minutes!

---

**Questions?** Check the Logs tab on your Render dashboard for detailed error messages.

**Good luck! **

---

*Created: February 27, 2026*  
*Dashboard: MEV Analysis for Solana pAMM*  
*Researcher: Aileen | aileen.xyz*
