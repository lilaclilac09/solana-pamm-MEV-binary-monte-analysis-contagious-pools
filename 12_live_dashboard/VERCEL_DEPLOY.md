# Deploy to mev.aileen.xyz - VERCEL (Easiest Method)

## 🚀 5-Minute Setup

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy from Dashboard Directory
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard

# Login to Vercel (one-time)
vercel login

# Deploy to production
vercel --prod
```

### Step 3: Connect Your Domain

When deployment completes, you'll see:
```
✅ Production: https://mev-dashboard-xxxxx.vercel.app
```

**Connect to mev.aileen.xyz:**

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Domains**
2. Click "Add Domain"
3. Enter: `mev.aileen.xyz`
4. Choose "Use Nameservers" OR "Add CNAME Record"

#### **If using CNAME (DNS provider):**
At your domain host (GoDaddy, Namecheap, etc.):
- **Type:** CNAME
- **Name:** mev
- **Value:** cname.vercel.com
- **TTL:** 3600

Then verify in Vercel dashboard (wait 5-15 minutes for DNS propagation).

#### **If using Vercel Nameservers:**
Update your domain registrar nameservers to:
```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

---

## ✅ Verification

Once deployed:
```bash
# Check that it's live
curl https://mev.aileen.xyz/

# Should return dashboard HTML
```

---

## 🔄 Auto-Deploy on Push (Optional)

Connect your GitHub repo for auto-deploy:

1. Push this folder to GitHub:
```bash
git add .
git commit -m "Add MEV dashboard with Vercel config"
git push
```

2. In Vercel Dashboard:
   - **Connect Git** → Select GitHub repo
   - Auto-deploys on every push
   - Choose `12_live_dashboard` as root directory

---

## 📊 Live Dashboard Features

Your dashboard at **mev.aileen.xyz** will have:

- ✅ **13 Interactive Tabs**
  - Overview, MEV Distribution, Top Attackers
  - Event Analysis, Contagion, Oracle Analysis
  - Token Pair Risk, Validators, ML Models
  - Monte Carlo, Attack Animation
  - BisonFi Case Studies, Live Data Integration

- ✅ **Real-Time Visualizations**
  - Network graphs of pool coordination
  - Oracle latency analysis
  - Animated sandwich attack simulation
  - Feature importance charts

- ✅ **Custom Branding**
  - Purple gradient header (#667EEA → #764BA2)
  - aileen.xyz branding throughout
  - Professional color scheme

---

## 🛠️ Troubleshooting

### Domain not resolving?
- Wait 15-30 minutes for DNS propagation
- Check Vercel dashboard for domain status (should be ✅ Valid)

### 502 Bad Gateway?
- Check Vercel logs: Dashboard → Deployments → View logs
- Ensure `mev_dashboard_enhanced.py` exists
- Check requirements.txt has all dependencies

### Want to rollback?
- Vercel Dashboard → Deployments → Select previous version → Promote to Production

---

## 📝 Environment Variables (Optional)

If you add live data integration later, add env vars in Vercel:
1. **Settings** → **Environment Variables**
2. Add: `HELIUS_API_KEY`, `JITO_BLOCK_ENGINE_URL`, etc.
3. Redeploy

---

**You're all set! 🎉**
- Dashboard: https://mev.aileen.xyz
- View logs: https://vercel.com/dashboard
- Manage domain: https://vercel.com/dashboard/[project]/settings/domains
