# Solana pAMM MEV Interactive Dashboard

## Overview
Interactive web dashboard for analyzing Maximum Extractable Value (MEV) in Solana Proportional Automated Market Makers (pAMMs). Built with Dash/Plotly for real-time visualization and analysis.

**Live Demo**: Deploy to `https://aileen.xyz/allee_machina_01`

## Features

### Current Analytics (Historical Data)
- **Overview**: Key statistics (5.5M events, 617 fat sandwich attacks, 179 unique attackers)
- **MEV Distribution**: Profit breakdown across 8 protocols (HumidiFi, BisonFi, GoonFi, etc.)
- **Top Attackers**: Ranking by total profit and attack count
- **Contagion Analysis**: Cross-pool attacker overlap heatmap and network graph
- **Validator Behavior**: Bot activity ratios and MEV correlation
- **Oracle Analysis**: Update latency and frequency by pool
- **Token Pair Risk**: Vulnerability tiers (PUMP/WSOL, SOL/USDC, etc.)
- **ML Models**: Performance metrics (XGBoost F1=0.91, ROC-AUC=0.97)
- **Monte Carlo Simulations**: Risk distributions and expected losses

### Future: Live Data Integration
- Real-time transaction monitoring via Helius RPC
- MEV bundle tracking via Jito Block Engine
- Webhook-based event notifications
- Auto-refreshing charts with interval components
- Live contagion analysis with rolling windows

## Installation

### Prerequisites
- Python 3.9+
- pip or conda package manager
- (Optional) Helius API key for live data
- (Optional) Jito API access for bundle monitoring

### Setup Steps

1. **Clone/Navigate to Dashboard Directory**
```bash
cd 12_live_dashboard
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Dashboard**
```bash
python mev_dashboard.py
```

5. **Access in Browser**
Open: `http://127.0.0.1:8050/`

## Deployment Options

### Option 1: Heroku (Recommended for beginners)
1. Create `Procfile`:
```
web: gunicorn mev_dashboard:server
```

2. Add to dashboard code:
```python
server = app.server  # Add after app = dash.Dash(__name__)
```

3. Deploy:
```bash
heroku create solana-mev-dashboard
git push heroku main
```

### Option 2: Vercel (For Next.js integration)
1. Install Vercel CLI: `npm i -g vercel`
2. Create `vercel.json`:
```json
{
  "builds": [{"src": "mev_dashboard.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "mev_dashboard.py"}]
}
```
3. Deploy: `vercel --prod`

### Option 3: AWS EC2 (For full control)
1. Launch EC2 instance (Ubuntu 22.04)
2. SSH and install:
```bash
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt
```

3. Configure Nginx reverse proxy to port 8050
4. Use systemd or supervisor to run dashboard as service

### Option 4: Embed in Aileen.xyz (React/Next.js)
If your site uses React/Next.js:

1. Deploy Dash app separately (Heroku/Vercel)
2. Embed via iframe in your `/allee_machina_01` page:
```jsx
<iframe 
  src="https://your-deployed-dashboard.herokuapp.com" 
  width="100%" 
  height="1200px"
  frameborder="0"
/>
```

Or use `react-dash-renderer` for deeper integration.

## Live Data Integration

### Helius RPC Setup
1. Get API key: https://dev.helius.xyz/
2. Set environment variable:
```bash
export HELIUS_RPC_URL="https://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
```

3. Add fetching code (see `LIVE_DATA_INTEGRATION.md`)

### Jito MEV Bundles
1. Access: https://jito.network/
2. Poll explorer API for tips and bundles
3. See prompts in `AI_PROMPTS.md` for code generation

### Webhooks (Helius)
Set up webhooks for real-time pool updates:
```python
from flask import Flask, request
app_flask = Flask(__name__)

@app_flask.route('/webhook', methods=['POST'])
def helius_webhook():
    data = request.json
    # Process MEV events
    return "OK", 200
```

Run alongside Dash app or integrate with Dash callbacks.

## Configuration

### Environment Variables
```bash
# API Keys
export HELIUS_API_KEY="your_helius_key"
export JITO_API_KEY="your_jito_key"

# Dashboard Settings
export DASH_DEBUG="True"  # Set to False in production
export DASH_PORT="8050"
export DASH_HOST="0.0.0.0"

# Data Refresh Intervals (seconds)
export REFRESH_INTERVAL="60"  # Update charts every 60s
```

### Data Sources
The dashboard currently uses hardcoded data from the analysis report. To switch to live data:

1. Modify data loading functions in `mev_dashboard.py`
2. Add Dash `dcc.Interval` components for auto-refresh
3. Implement data fetching functions (see AI prompts)

## Customization

### Adding New Tabs
```python
dcc.Tab(label='🆕 New Analysis', children=[
    html.Div([
        html.H3('Custom Analysis'),
        dcc.Graph(figure=your_custom_figure)
    ])
])
```

### Styling
- Modify inline `style={}` dicts
- Use `dash-bootstrap-components` for themes
- Add custom CSS in `assets/` directory

### Real-Time Updates
Add interval component:
```python
dcc.Interval(
    id='interval-component',
    interval=60*1000,  # 60 seconds
    n_intervals=0
)
```

Then create callback to update data.

## Troubleshooting

### Common Issues

1. **Port 8050 already in use**
```bash
# Kill existing process
lsof -ti:8050 | xargs kill -9
# Or change port in app.run_server(port=8051)
```

2. **ModuleNotFoundError**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

3. **Graph not rendering**
- Check browser console for errors
- Verify Plotly version compatibility
- Clear browser cache

4. **Slow performance with large datasets**
- Implement data sampling
- Use Dash caching (`@cache.memoize()`)
- Consider Dash Enterprise for optimization

## Performance Optimization

### For 5M+ Events
1. Use Pandas with dtype optimization
2. Implement data aggregation before visualization
3. Add caching layer (Redis)
4. Paginate large tables
5. Use `dcc.Loading` components

### Memory Management
```python
import gc
# Periodically clear cache
gc.collect()
```

## Security

### Production Checklist
- [ ] Set `debug=False` in production
- [ ] Use HTTPS (SSL certificate)
- [ ] Implement rate limiting
- [ ] Sanitize user inputs (if adding search/filters)
- [ ] Store API keys in environment variables (never commit)
- [ ] Use web server authentication if needed

## Support & Documentation

### Additional Resources
- `AI_PROMPTS.md` - Ready-to-use prompts for AI code generation
- `LIVE_DATA_INTEGRATION.md` - Detailed integration guides
- Main analysis report: `../11_report_generation/outputs/Solana_PAMM_MEV_Analysis_Report.pdf`

### API Documentation
- Helius: https://docs.helius.dev/
- Jito: https://jito-labs.gitbook.io/
- Solana RPC: https://docs.solana.com/api/

## License
Based on Solana pAMM MEV Analysis research (2024-2026)

## Credits
Dashboard implementation based on comprehensive MEV analysis across 8 Solana pAMM protocols.

---

**Last Updated**: February 27, 2026  
**Version**: 1.0.0  
**Status**: Production-ready (historical data) + Live integration (in progress)
