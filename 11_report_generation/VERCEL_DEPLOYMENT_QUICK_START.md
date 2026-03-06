#  Vercel Deployment: Quick Start Guide

## What's Being Deployed

 **Dash Dashboard** (Python Plotly)
- Section 5b: TOP STORIES - Real-World Attack Case Studies
- Section 5c: Threat Intelligence Visualizations (3 high-res PNG plots)

 **Website HTML** (Responsive Design)
- MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html for mev.aileen.xyz

 **Visualization Assets** (300 DPI Publication Quality)
- token_pair_fragility.png (394K)
- oracle_latency_window.png (526K)
- mev_battlefield.png (443K)

---

## 5-Minute Deployment

### 1️⃣ Install Deployment Tool (if needed)
```bash
npm install -g vercel
```

### 2️⃣ Initialize Vercel Project (first time only)
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools
vercel
# Follow prompts to link project
```

### 3️⃣ Deploy to Vercel
```bash
# Option A: Push to git (auto-deploys)
git add -A
git commit -m "Deploy TOP STORIES + MEV visualizations"
git push origin main
# Vercel auto-deploys in 1-2 minutes

# Option B: Direct Vercel deployment
vercel --prod
```

### 4️⃣ Access Your Dashboard
```
https://your-project.vercel.app
# Sections 5b + 5c with all visualizations
```

---

##  Required Vercel Configuration

### Environment Variables
Go to **Vercel Dashboard** → **Settings** → **Environment Variables**

Add these variables:
```
PYTHONUNBUFFERED=1
DASH_ASSETS_PATH=/assets/
```

### Vercel.json Setup
File: `vercel.json`

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": ".",
  "framework": "other",
  "functions": {
    "app/index.py": {
      "runtime": "python3.9",
      "memory": 3008,
      "maxDuration": 60
    }
  },
  "routes": [
    {
      "src": "/assets/(.*)",
      "dest": "app/assets/$1"
    },
    {
      "src": "/(.*)",
      "dest": "app/index.py"
    }
  ]
}
```

---

##  Website Deployment (mev.aileen.xyz)

### Option 1: Upload to Web Server (SSH/SFTP)
```bash
# SSH into your server
ssh user@mev.aileen.xyz

# Create directories
mkdir -p /var/www/html/dashboard-assets
mkdir -p /var/www/html/stories

# Upload files locally (from your machine)
scp MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html user@mev.aileen.xyz:/var/www/html/stories/
scp -r app/assets/ user@mev.aileen.xyz:/var/www/html/dashboard-assets/

# Access at:
# https://mev.aileen.xyz/stories/MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html
```

### Option 2: Vercel Static Export
```bash
# Push to Vercel next.js/static branch
git checkout -b vercel/static
cp MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html vercel/public/
cp -r app/assets vercel/public/
git push origin vercel/static
# Vercel serves at: vercel-project.vercel.app
```

### Option 3: AWS S3 + CloudFront
```bash
# Upload to S3
aws s3 cp MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html s3://your-bucket/
aws s3 sync app/assets/ s3://your-bucket/assets/

# CloudFront serves at custom domain
# https://cdn.mev.aileen.xyz/MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html
```

---

##  Deployment Checklist

- [ ] Git status clean: `git status`
- [ ] All 3 PNG files in `app/assets/`: `ls -lh app/assets/`
- [ ] HTML pages ready: `ls -lh MEV_THREAT*.html`
- [ ] requirements.txt updated: Contains `dash`, `plotly`, `pandas`
- [ ] vercel.json configured: Check build command + routes
- [ ] Environment variables set in Vercel dashboard
- [ ] Git pushed: `git push origin main`

### Post-Deployment Verification

```bash
# Check deployed dashboard
curl -I https://your-project.vercel.app/

# Check visualizations exist
curl -I https://your-project.vercel.app/assets/token_pair_fragility.png

# Check website HTML
curl -I https://mev.aileen.xyz/MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html
```

Expected responses: `200 OK`

---

##  Troubleshooting

### "Module not found" Error
**Problem:** `ModuleNotFoundError: No module named 'dash'`

**Solution:**
```bash
# Verify requirements.txt has dash
grep dash requirements.txt

# If missing, add it:
echo "dash==4.0.0" >> requirements.txt
git add requirements.txt
git push origin main  # Triggers redeploy
```

### Images Not Loading
**Problem:** Visualizations show broken image icon

**Solution:**
```bash
# Check image paths in app/index.py - must use /assets/
grep "src=" app/index.py | head -5

# Correct format:
# src="/assets/token_pair_fragility.png"  
# src="token_pair_fragility.png"          

# Commit fix:
git add app/index.py
git push origin main
```

### "Build failed" on Vercel
**Problem:** Deployment logs show build error

**Solution:**
```bash
# Check logs:
vercel logs --prod

# Common causes:
# 1. Missing dependencies - update requirements.txt
# 2. Python syntax error - test locally first
#    python app/index.py
# 3. Missing files - verify git added all files
#    git status
```

---

##  Dashboard Sections Reference

### Section 5b: TOP STORIES (Attack Case Studies)
- **Location:** app/index.py, lines 267-330
- **Content:** 4 detailed MEV attack case studies
- **Metrics:** Total revenue, victim losses, max ROI, validator fees
- **Data:** 4 case study rows with timings and profit analysis

### Section 5c: Threat Intelligence Visualizations
- **Location:** app/index.py, lines 331-380
- **Content:** 3 high-resolution PNG visualizations
- **Images:** 
  1. Token Pair Fragility (38.2% PUMP/WSOL risk)
  2. Oracle Latency Window (2.1s HumidiFi extraction)
  3. MEV Battlefield (66.8% profit concentration)
- **Resolution:** 300 DPI, publication quality

---

##  Update Workflow

When you want to update content:

```bash
# 1. Make changes locally
nano app/index.py  # Edit dashboard content

# 2. Test locally
source .venv/bin/activate
cd app && python index.py
# Visit http://localhost:8050

# 3. Deploy to Vercel
git add app/index.py
git commit -m "Update: Description of changes"
git push origin main
# Vercel auto-deploys in 1-2 minutes

# 4. Verify at production URL
# https://your-project.vercel.app
```

---

##  Success Indicators

 **Dashboard is live** when you see:
- Dash app loads at HTTPS URL
- Sections 5b + 5c visible and styled correctly
- 3 PNG visualizations display without errors
- No 404s in browser console

 **Website is live** when you see:
- HTML page loads at mev.aileen.xyz
- All images display correctly
- Responsive design works on mobile
- Attack case study content is readable

---

##  Support

**Issue:** Dashboard not responding
**Fix:** Check `vercel logs --prod`

**Issue:** Images 404 errors  
**Fix:** Verify `/assets/` prefix in image src paths

**Issue:** Slow deployment
**Fix:** Dependencies installing - normal, takes 2-5 min

**Issue:** Domain not resolving
**Fix:** Update DNS records to point to Vercel nameservers

---

##  You're Done!

Your MEV threat intelligence is now:
-  Live on Vercel at https://your-project.vercel.app
-  Accessible on mev.aileen.xyz/stories (after manual upload)
-  Dashboard with Sections 5b + 5c fully integrated
-  3 high-resolution threat visualizations deployed
-  All data interactive and responsive

**Next:** Share the Vercel Dashboard URL + public website link with your team!
