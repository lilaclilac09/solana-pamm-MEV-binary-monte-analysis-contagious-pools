# Render Deployment - Step-by-Step Instructions

## Prerequisites
 GitHub account with your code pushed to a repository  
 All files ready in `12_live_dashboard/` folder

---

## Step 1: Create Render Account & New Service

1. Go to **[render.com/dashboard](https://render.com/dashboard)**
2. Sign up/login (use GitHub for easy integration)
3. Click **"New +"** button (top right)
4. Select **"Web Service"**

---

## Step 2: Connect Your Repository

1. Click **"Connect account"** under GitHub
2. Authorize Render to access your GitHub
3. Select your repository from the list
4. Choose branch: **`main`** (or your default branch)

---

## Step 3: Configure Service Settings

**Fill in the following fields exactly:**

| Field | Value |
|-------|-------|
| **Name** | `mev-dashboard` |
| **Region** | `Oregon (US West)` (or nearest to you) |
| **Branch** | `main` |
| **Root Directory** | `12_live_dashboard` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn mev_dashboard:server --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Plan** | `Free` |

---

## Step 4: Environment Variables (Optional)

Click **"Advanced"** to add environment variables if needed:
- Most settings are already configured in the code
- No additional env vars required for basic deployment

---

## Step 5: Deploy

1. Click **"Create Web Service"** button
2. Render will automatically:
   - Clone your repository
   - Run the build command
   - Start your application
3. **Initial deployment takes 5-10 minutes**

---

## Step 6: Monitor Deployment

Watch the deployment logs in real-time:
-  Green checkmarks = successful steps
-  Red errors = check logs for details

Common issues:
- **Dependency errors**: Check `requirements.txt` syntax
- **Port binding errors**: Make sure start command uses `$PORT`
- **Module not found**: Ensure all imports are in requirements.txt

---

## Step 7: Access Your Dashboard

Once deployed successfully:
1. Render provides a URL: `https://mev-dashboard.onrender.com`
2. Click the URL to open your dashboard
3. Share the link with others!

---

## Free Plan Notes

- ️ **Auto-sleep**: App sleeps after 15 minutes of inactivity
- ️ **Wake-up time**: ~30 seconds on first request after sleep
- ️ **750 hours/month** free (resets monthly)
- No credit card required

---

## Useful Commands

### View Logs
```bash
# In Render dashboard
Logs tab → Select time range
```

### Redeploy
```bash
# Manual redeploy: Dashboard → Manual Deploy → Deploy latest commit
# Auto-deploy: Enabled by default on git push
```

### Update Code
```bash
# In your local terminal
git add .
git commit -m "Update dashboard"
git push origin main
# Render auto-deploys on push
```

---

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Dashboard Issues**: Check logs in Render dashboard
- **Status**: [status.render.com](https://status.render.com)

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check requirements.txt dependencies |
| App crashes on start | Verify start command syntax |
| 404 errors | Check Root Directory is set to `12_live_dashboard` |
| Module errors | Add missing packages to requirements.txt |
| Timeout | Increase timeout in start command |

---

**Your dashboard is configured and ready to deploy!** 
