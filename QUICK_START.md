# 🎯 MEV Threat Intelligence - Quick Reference Card

**TL;DR:** Everything is ready. Run these 3 commands to deploy.

---

## ⚡ The Absolute Quickest Deploy (Copy-Paste Ready)

```bash
# STEP 1: Test locally (ctrl+C to stop)
source .venv/bin/activate && cd app && python index.py

# After testing...
cd ..

# STEP 2: Deploy main page to website
scp index.html mev.aileena.xyz:/var/www/html/ && \
scp -r app/assets mev.aileena.xyz:/var/www/html/

# STEP 3: Deploy dashboard to Vercel
git add -A && git commit -m "Deploy MEV dashboard" && git push origin main
```

**Result:** 
- Static page live at: https://mev.aileena.xyz/
- Dashboard live at: your-project.vercel.app

---

## 📁 What You Have (File Inventory)

| What | Where | Status | Size |
|------|-------|--------|------|
| Main page | `index.html` | ✅ Ready | 44K |
| Dash app | `app/index.py` | ✅ Ready | 407 lines |
| Visualizations | `app/assets/*.png` | ✅ Ready | 1.3 MB |
| Top stories | `TOP_STORIES_ATTACK_CASE_STUDIES.md` | ✅ Ready | 500+ lines |
| Setup guide | `DEPLOYMENT_CHECKLIST.md` | ✅ Created | Full |
| Deploy script | `deploy.sh` | ✅ Created | Bash |

---

## 🎯 What's on Each Page

### **mev.aileena.xyz/** (Static HTML)
- Executive summary (6 metrics)
- 3-step deployment guide
- 4 attack case studies
- 3 visualizations (PNG charts)
- Troubleshooting guide
- Responsive design

### **your-project.vercel.app** (Interactive Dash)
- Section 5b: TOP STORIES with 4 cases
- Section 5c: 3 visualizations embedded
- Key metrics cards
- 6 data tables
- Interactive Plotly charts

---

## 📊 Attack Data at a Glance

| Metric | Value |
|--------|-------|
| Events Analyzed | 5.5M |
| Attacks Found | 617 |
| Total Profit | 7.666 SOL |
| Victim Losses | 10.49 SOL |
| Max ROI | 552% (Case 2) |
| Avg Duration | 1.16 seconds |
| Top Protocol | HumidiFi (66.8%) |
| Oracle Lag | 2.1s |

---

## ✅ After Deployment, Verify:

### Local Test
- [ ] Dash starts on localhost:8050
- [ ] Section 5b shows 4 cases
- [ ] Section 5c shows 3 charts

### Website Deployment
- [ ] https://mev.aileena.xyz/ loads
- [ ] Charts display correctly
- [ ] Mobile responsive

### Vercel Deployment
- [ ] your-project.vercel.app loads
- [ ] Sections 5b + 5c visible
- [ ] Images render

---

## 🚨 Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| Images don't load | `ls app/assets/` verify files |
| Dash won't start | `pip install -r requirements.txt` |
| SCP fails | `ssh mev.aileena.xyz` test connection |
| Port 8050 busy | `pkill -f "python index.py"` |
| Git push fails | `git status` check commits |

---

## 📞 File Locations (Reference)

```
/Users/aileen/Downloads/pamm/solana-pamm-analysis/
  solana-pamm-MEV-binary-monte-analysis-contagious-pools/
  ├── index.html ..................... Main page (44K)
  ├── app/
  │   ├── index.py ................... Dash app
  │   └── assets/
  │       ├── token_pair_fragility.png (394K)
  │       ├── oracle_latency_window.png (526K)
  │       └── mev_battlefield.png (443K)
  ├── TOP_STORIES_ATTACK_CASE_STUDIES.md
  ├── DEPLOYMENT_CHECKLIST.md
  ├── DEPLOYMENT_STATUS.md
  ├── deploy.sh
  └── requirements.txt
```

---

## 🎬 Start Here

**Choose Your Path:**

### 👤 I want to test locally first
```bash
source .venv/bin/activate
cd app
python index.py
# Visit http://localhost:8050
```

### 🌐 I want to deploy now
```bash
bash deploy.sh all  # Runs all 3 steps automatically
```

### 📖 I want detailed steps
```bash
cat DEPLOYMENT_CHECKLIST.md
```

---

## 💡 Pro Tips

1. **First time?** Start with `bash deploy.sh local` to verify everything works
2. **Working now?** `scp` copies files instantly. Network dependent only.
3. **Vercel deploy?** Auto-triggers on `git push origin main`. Check vercel.com/deployments
4. **Assets missing?** Both servers need PNG files: `cp app/assets/* /var/www/html/assets/`
5. **Need help?** Check `DEPLOYMENT_CHECKLIST.md` troubleshooting section

---

## 🏁 Expected Outcome

### ✅ After Following Guide:

**You will have:**
- Live static website at mev.aileena.xyz with complete MEV analysis
- Interactive dashboard at your-project.vercel.app with Sections 5b + 5c
- All 3 visualizations (300 DPI) displaying on both sites
- 4 real-world attack case studies visible
- Professional, responsive design working on all devices

**Total setup time:** 10-15 minutes
**Maintenance:** 0 (static files + git push for updates)

---

## 🚀 You're 90% Done

Everything is ready to go. Just need to:

1. ☑️ Run local test: `bash deploy.sh local`
2. ☑️ Deploy website: `bash deploy.sh website`  
3. ☑️ Deploy dashboard: `bash deploy.sh vercel`

**That's it!** 🎉

---

**Status:** 🟢 PRODUCTION READY  
**Next Step:** `bash deploy.sh local`  
**Questions?** See DEPLOYMENT_CHECKLIST.md
