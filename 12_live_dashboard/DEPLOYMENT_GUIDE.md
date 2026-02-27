# 🚀 Deployment Guide for aileen.xyz

## Option 1: Deploy to aileen.xyz Subdomain (Recommended)

### Method A: Using Vercel (Easiest)

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Create vercel.json**
Already created in this folder with proper configuration.

3. **Deploy**
```bash
cd 12_live_dashboard
vercel
```

4. **Configure Custom Domain**
- Go to Vercel dashboard
- Add custom domain: `mev.aileen.xyz` or `analytics.aileen.xyz`
- Update DNS records at your domain registrar:
  ```
  Type: CNAME
  Name: mev (or analytics)
  Value: cname.vercel-dns.com
  ```

### Method B: Using DigitalOcean App Platform

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "MEV Dashboard"
git remote add origin https://github.com/yourusername/mev-dashboard
git push -u origin main
```

2. **Create App on DigitalOcean**
- Go to DigitalOcean Apps
- Connect GitHub repo
- Set environment:
  - Run Command: `gunicorn mev_dashboard:server -b 0.0.0.0:8050`
  - Build Command: `pip install -r requirements.txt`

3. **Add Custom Domain**
- In app settings, add: `mev.aileen.xyz`
- Update DNS:
  ```
  Type: CNAME
  Name: mev
  Value: [your-app-name].ondigitalocean.app
  ```

---

## Option 2: iframe Embed on aileen.xyz

If you already have aileen.xyz hosted, add this to your HTML:

```html
<div style="width: 100%; height: 100vh;">
  <iframe 
    src="https://your-dashboard-url.vercel.app" 
    style="width: 100%; height: 100%; border: none;">
  </iframe>
</div>
```

---

## Option 3: Self-Host on Your VPS

If you have a server for aileen.xyz:

### 1. Install Dependencies
```bash
ssh user@aileen.xyz
cd /var/www/mev-dashboard
git clone [your-repo]
cd 12_live_dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Gunicorn Service
Create `/etc/systemd/system/mev-dashboard.service`:
```ini
[Unit]
Description=MEV Dashboard
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/mev-dashboard/12_live_dashboard
Environment="PATH=/var/www/mev-dashboard/12_live_dashboard/venv/bin"
ExecStart=/var/www/mev-dashboard/12_live_dashboard/venv/bin/gunicorn mev_dashboard:server -b 127.0.0.1:8050

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable mev-dashboard
sudo systemctl start mev-dashboard
```

### 3. Configure Nginx
Add to `/etc/nginx/sites-available/aileen.xyz`:
```nginx
# Option A: Subdomain
server {
    listen 80;
    server_name mev.aileen.xyz;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Option B: Subfolder
server {
    server_name aileen.xyz;
    
    location /mev-dashboard/ {
        proxy_pass http://127.0.0.1:8050/;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d mev.aileen.xyz  # Get SSL
```

---

## Quick Start Commands

### Local Testing
```bash
cd 12_live_dashboard
./start.sh
# Visit http://localhost:8050
```

### Production Deploy (Vercel)
```bash
vercel --prod
```

### Production Deploy (Heroku)
```bash
heroku create aileen-mev-dashboard
git push heroku main
heroku open
```

---

## Custom Domain DNS Records

Add to your aileen.xyz DNS:

| Type  | Name      | Value                          | TTL  |
|-------|-----------|--------------------------------|------|
| CNAME | mev       | cname.vercel-dns.com          | Auto |
| OR    |           |                                |      |
| A     | mev       | [your-vps-ip]                  | 3600 |

---

## Monitoring & Analytics

After deployment, add:
- Google Analytics to track visitors
- Sentry for error monitoring
- Uptime monitoring (UptimeRobot, Pingdom)

---

## Support

For issues: aileen@aileen.xyz
Dashboard URL: https://aileen.xyz/mev-dashboard (after deployment)
