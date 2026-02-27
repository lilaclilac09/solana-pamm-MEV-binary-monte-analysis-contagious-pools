# Render Deployment Guide for MEV Dashboard

Complete step-by-step guide to deploy your Solana pAMM MEV Dashboard to Render.

## Prerequisites

✅ Your dashboard is ready! Your project has:
- `mev_dashboard.py` with Dash app configured
- `server = app.server` properly defined for WSGI deployment
- `gunicorn` in requirements.txt
- `Procfile` with correct configuration

## Step 1: Prepare Your GitHub Repository

1. **Ensure your repo is pushed to GitHub:**
   ```bash
   cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify files are committed:**
   - `requirements.txt` ✅
   - `mev_dashboard.py` ✅
   - `Procfile` ✅
   - `.gitignore` should exclude `.venv`, `__pycache__`, `.env`

## Step 2: Create Render Account & Service

1. **Go to [render.com](https://render.com)** and sign up (free account)

2. **Visit [render.com/dashboard](https://render.com/dashboard)**

3. **Create new Web Service:**
   - Click **New** → **Web Service**
   - Connect your GitHub account
   - Select your repository
   - Choose branch: `main`

## Step 3: Configure the Service

Fill in the following settings on Render:

| Setting | Value |
|---------|-------|
| **Name** | `mev-dashboard` (or your preferred name) |
| **Environment** | `Python 3` |
| **Region** | Select closest to you (e.g., `Oregon`) |
| **Branch** | `main` |
| **Runtime** | `Python 3.11` |
| **Build Command** | `pip install -r 12_live_dashboard/requirements.txt` |
| **Start Command** | `cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server` |
| **Plan** | `Free` (0 downtime, auto-sleep after 15 mins) |

### Important Notes:

- **Build Command:** References the full path since dashboard is in subdirectory
- **Start Command:** Changes to dashboard directory before running gunicorn
- **Server Variable:** `mev_dashboard:server` (Flask app defined in mev_dashboard.py)
- **Workers:** Set to `2` for free plan (use `4` for paid)
- **Timeout:** Set to `120` for longer-running requests

## Step 4: Deploy

1. **Click "Create Web Service"**
   - Render will start the initial build automatically
   - First deployment takes 5-10 minutes

2. **Monitor build progress:**
   - View logs in real-time
   - Watch for build and startup messages

3. **Access your dashboard:**
   - Once deployed, Render provides a `.onrender.com` URL
   - Example: `https://mev-dashboard.onrender.com`

## Step 5: Verify Deployment

✅ **Check dashboard is working:**
- Navigate to your `.onrender.com` URL
- Verify all charts load correctly
- Check browser console for errors

✅ **View logs:**
- Go to Render Dashboard → Your Service → Logs
- Look for flask startup messages

## Troubleshooting

### Issue: Build Command Fails
**Solution:** Ensure full path to requirements.txt in build command:
```
pip install -r 12_live_dashboard/requirements.txt
```

### Issue: Start Command Not Working
**Solution:** Check Start Command format:
```
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 mev_dashboard:server
```

### Issue: Dashboard Loads Slowly
**Solution:** 
- Upgrade to paid plan for better performance
- Increase timeout in Start Command
- Check data loading in mev_dashboard.py

### Issue: Module Not Found Errors
**Solution:**
- Verify all imports are in requirements.txt
- Check Python version compatibility (3.8+)
- Rebuild service after updating requirements.txt

## Auto-Deploy on GitHub Push

Render automatically rebuilds when you push to your branch:

```bash
# Make changes locally
git add .
git commit -m "Update dashboard"
git push origin main
# Render redeploys automatically!
```

## Environment Variables (Optional)

If you need API keys or secrets:

1. Go to **Environment** tab in Render service settings
2. Add environment variables:
   ```
   SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
   API_KEY=your_key_here
   ```
3. Access in Python:
   ```python
   import os
   solana_rpc = os.getenv('SOLANA_RPC_URL')
   ```

## Performance Optimization

### For Free Plan:
- Accept 15-minute auto-sleep after inactivity
- Simpler data processing recommended
- Limit real-time data updates

### For Paid Plans:
- Enable 0 downtime deployments
- Increase worker count to 4
- Use caching (Redis) for heavy data

## Monitoring & Maintenance

**View Service Health:**
- Render Dashboard → Your Service → Metrics
- Monitor CPU, Memory, requests/min

**Update Dashboard:**
```bash
# Update code locally
git push origin main
# Render auto-rebuilds in ~2 minutes
```

**Logs:**
- Check Render logs for errors
- Use `print()` statements for debugging (visible in logs)

## Next Steps

1. ✅ Push your repo to GitHub
2. ✅ Sign up for Render.com
3. ✅ Create Web Service with above settings
4. ✅ Wait for first deployment (5-10 mins)
5. ✅ Test your dashboard at the provided URL
6. ✅ Share link: `https://mev-dashboard.onrender.com`

## Additional Resources

- [Render Python Deployment Docs](https://render.com/docs/deploy-python)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/)
- [Dash Deployment Guide](https://dash.plotly.com/deployment)

---

**Questions?** Check Render logs for specific error messages.
