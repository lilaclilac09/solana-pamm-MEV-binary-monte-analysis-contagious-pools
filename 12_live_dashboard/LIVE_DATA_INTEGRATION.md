# Live Data Integration Guide

This guide provides step-by-step instructions for integrating real-time Solana blockchain data into your MEV dashboard.

## Table of Contents
1. [Helius RPC Integration](#helius-rpc-integration)
2. [Jito Bundle Monitoring](#jito-bundle-monitoring)
3. [Webhook Setup](#webhook-setup)
4. [Dashboard Updates](#dashboard-updates)
5. [Performance Optimization](#performance-optimization)

---

## Helius RPC Integration

### Step 1: Get API Key
1. Sign up at https://dev.helius.xyz/
2. Create new project: "Solana MEV Dashboard"
3. Copy API key to `.env` file:
```bash
HELIUS_API_KEY=your_key_here
```

### Step 2: Install Solana Library
```bash
pip install solana solders
```

### Step 3: Basic Transaction Fetching

Create file: `live_data/helius_fetcher.py`

```python
import os
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
import pandas as pd
from datetime import datetime

class HeliusFetcher:
    def __init__(self):
        api_key = os.getenv('HELIUS_API_KEY')
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
        self.client = Client(self.rpc_url, commitment=Confirmed)
    
    def get_recent_transactions(self, limit=100):
        """Fetch recent confirmed transactions"""
        try:
            # Get recent slot
            response = self.client.get_slot()
            current_slot = response['result']
            
            # Fetch block data
            block = self.client.get_block(
                current_slot - 10,  # 10 slots back (~4 seconds)
                encoding="json",
                max_supported_transaction_version=0
            )
            
            transactions = []
            if 'result' in block and block['result']:
                for tx in block['result']['transactions'][:limit]:
                    # Parse transaction
                    signature = tx['transaction']['signatures'][0]
                    accounts = tx['transaction']['message']['accountKeys']
                    
                    transactions.append({
                        'signature': signature,
                        'slot': current_slot - 10,
                        'timestamp': datetime.now(),
                        'accounts': len(accounts)
                    })
            
            return pd.DataFrame(transactions)
        
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return pd.DataFrame()
    
    def get_pool_activity(self, pool_address):
        """Monitor specific pAMM pool activity"""
        try:
            # Get account info
            response = self.client.get_account_info(pool_address)
            
            if response['result']:
                return {
                    'pool': pool_address,
                    'lamports': response['result']['value']['lamports'],
                    'owner': response['result']['value']['owner'],
                    'timestamp': datetime.now()
                }
            return None
        
        except Exception as e:
            print(f"Error fetching pool data: {e}")
            return None

# Usage in dashboard
fetcher = HeliusFetcher()
recent_txs = fetcher.get_recent_transactions(100)
print(recent_txs.head())
```

### Step 4: MEV Pattern Detection

Create file: `live_data/mev_detector.py`

```python
import pandas as pd

class MEVDetector:
    @staticmethod
    def detect_sandwich_attacks(transactions_df):
        """
        Detect sandwich attack patterns:
        - Same signer in front-run and back-run
        - Victim transaction in between
        - All in same slot
        """
        attacks = []
        
        # Group by slot
        for slot, group in transactions_df.groupby('slot'):
            if len(group) < 3:
                continue
            
            # Look for attacker-victim-attacker pattern
            for i in range(len(group) - 2):
                tx1 = group.iloc[i]
                tx2 = group.iloc[i + 1]
                tx3 = group.iloc[i + 2]
                
                # Check if tx1 and tx3 have same signer (attacker)
                # and tx2 is different (victim)
                if (tx1['signer'] == tx3['signer'] and 
                    tx2['signer'] != tx1['signer']):
                    
                    attacks.append({
                        'slot': slot,
                        'attacker': tx1['signer'],
                        'victim': tx2['signer'],
                        'front_run_sig': tx1['signature'],
                        'victim_sig': tx2['signature'],
                        'back_run_sig': tx3['signature'],
                        'detected_at': pd.Timestamp.now()
                    })
        
        return pd.DataFrame(attacks)
    
    @staticmethod
    def calculate_extracted_value(attack_data, pool_prices):
        """Estimate MEV extracted from sandwich attack"""
        # Simplified calculation - real implementation needs price data
        # Value = (back_run_amount - front_run_amount) - gas_fees
        return 0.0  # Placeholder
```

---

## Jito Bundle Monitoring

### Step 1: Jito API Access
1. Visit https://jito.network/
2. Request API access or use public explorer
3. Add to `.env`:
```bash
JITO_API_KEY=your_jito_key
```

### Step 2: Bundle Tracking

Create file: `live_data/jito_monitor.py`

```python
import requests
import pandas as pd
from datetime import datetime

class JitoMonitor:
    def __init__(self):
        self.base_url = "https://bundles-api-rest.jito.wtf/api/v1"
        
    def get_recent_bundles(self):
        """Fetch recent Jito bundles"""
        try:
            response = requests.get(
                f"{self.base_url}/bundles",
                params={'limit': 50}
            )
            
            if response.status_code == 200:
                bundles = response.json()
                return pd.DataFrame(bundles)
            return pd.DataFrame()
        
        except Exception as e:
            print(f"Error fetching bundles: {e}")
            return pd.DataFrame()
    
    def get_validator_tips(self):
        """Track MEV tips to validators"""
        try:
            response = requests.get(f"{self.base_url}/tips")
            
            if response.status_code == 200:
                tips_data = response.json()
                return {
                    'total_tips_sol': sum([t['amount'] for t in tips_data]) / 1e9,
                    'validator_count': len(tips_data),
                    'timestamp': datetime.now()
                }
            return {}
        
        except Exception as e:
            print(f"Error fetching tips: {e}")
            return {}
    
    def detect_mev_spike(self, threshold_sol=10.0):
        """Alert on high MEV activity"""
        tips = self.get_validator_tips()
        
        if tips.get('total_tips_sol', 0) > threshold_sol:
            return {
                'alert': True,
                'message': f"High MEV activity detected: {tips['total_tips_sol']:.2f} SOL in tips",
                'timestamp': tips['timestamp']
            }
        return {'alert': False}

# Usage
monitor = JitoMonitor()
bundles = monitor.get_recent_bundles()
spike_alert = monitor.detect_mev_spike(threshold_sol=5.0)
print(spike_alert)
```

---

## Webhook Setup

### Step 1: Configure Helius Webhook

```python
# webhook_handler.py
from flask import Flask, request, jsonify
import json
from datetime import datetime

flask_app = Flask(__name__)
mev_events = []  # Store recent MEV events

@flask_app.route('/webhook/helius', methods=['POST'])
def helius_webhook():
    """Handle Helius webhook for pool updates"""
    try:
        data = request.json
        
        # Parse transaction data
        if data.get('type') == 'TRANSFER':
            event = {
                'type': 'pool_trade',
                'signature': data.get('signature'),
                'timestamp': datetime.now(),
                'accounts': data.get('accountData', [])
            }
            
            mev_events.append(event)
            
            # Trigger MEV detection
            # ... Add detection logic here
        
        return jsonify({'status': 'received'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/webhook/events', methods=['GET'])
def get_recent_events():
    """API endpoint for dashboard to fetch events"""
    return jsonify(mev_events[-100:])  # Last 100 events

if __name__ == '__main__':
    flask_app.run(port=5000, debug=True)
```

### Step 2: Register Webhook with Helius

```bash
curl -X POST https://api.helius.xyz/v0/webhooks \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhookURL": "https://your-domain.com/webhook/helius",
    "transactionTypes": ["TRANSFER", "SWAP"],
    "accountAddresses": ["YOUR_POOL_ADDRESS"],
    "webhookType": "enhanced"
  }'
```

---

## Dashboard Updates

### Step 1: Add Live Data Toggle

Update `mev_dashboard.py`:

```python
# Add to layout
html.Div([
    html.Label('Live Mode:'),
    dcc.RadioItems(
        id='live-mode-toggle',
        options=[
            {'label': ' Historical Data', 'value': 'historical'},
            {'label': ' Live Data', 'value': 'live'}
        ],
        value='historical',
        inline=True
    )
], style={'padding': '10px'})
```

### Step 2: Add Interval Component

```python
dcc.Interval(
    id='interval-component',
    interval=60*1000,  # Update every 60 seconds
    n_intervals=0
)
```

### Step 3: Create Update Callback

```python
from live_data.helius_fetcher import HeliusFetcher
from live_data.mev_detector import MEVDetector

fetcher = HeliusFetcher()
detector = MEVDetector()

@app.callback(
    Output('live-mev-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('live-mode-toggle', 'value')
)
def update_live_chart(n, mode):
    if mode == 'live':
        # Fetch recent data
        txs = fetcher.get_recent_transactions(100)
        attacks = detector.detect_sandwich_attacks(txs)
        
        # Create figure
        fig = px.bar(
            attacks.groupby('slot').size().reset_index(name='count'),
            x='slot',
            y='count',
            title=f'Live MEV Attacks (Last {len(attacks)} detected)'
        )
        return fig
    else:
        # Return historical chart
        return historical_figure
```

---

## Performance Optimization

### 1. Implement Caching

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def cached_fetch_transactions(timestamp_bucket):
    """Cache transactions by minute"""
    return fetcher.get_recent_transactions(100)

# Usage - bucket by minute
current_minute = int(time.time() / 60)
txs = cached_fetch_transactions(current_minute)
```

### 2. Use Redis for Shared State

```python
import redis
import json

r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

def cache_live_data(key, data, expire_seconds=300):
    """Store data in Redis with expiration"""
    r.setex(key, expire_seconds, json.dumps(data))

def get_cached_data(key):
    """Retrieve from Redis"""
    data = r.get(key)
    return json.loads(data) if data else None

# Usage
cache_live_data('recent_attacks', attacks.to_dict('records'), 60)
cached_attacks = get_cached_data('recent_attacks')
```

### 3. Background Data Fetching with Celery

```python
# tasks.py
from celery import Celery

celery_app = Celery('mev_tasks', broker='redis://localhost:6379')

@celery_app.task
def fetch_and_store_transactions():
    """Background task to fetch transactions"""
    fetcher = HeliusFetcher()
    txs = fetcher.get_recent_transactions(1000)
    
    # Store in database or cache
    cache_live_data('latest_transactions', txs.to_dict('records'))
    
    return len(txs)

# Schedule periodic task
celery_app.conf.beat_schedule = {
    'fetch-every-minute': {
        'task': 'tasks.fetch_and_store_transactions',
        'schedule': 60.0,  # Every 60 seconds
    },
}
```

### 4. Database Integration

```python
from sqlalchemy import create_engine
import pandas as pd

# PostgreSQL connection
engine = create_engine('postgresql://user:pass@localhost/mev_db')

def store_attacks(attacks_df):
    """Store detected attacks in database"""
    attacks_df.to_sql('mev_attacks', engine, if_exists='append', index=False)

def load_recent_attacks(hours=24):
    """Load attacks from last N hours"""
    query = f"""
        SELECT * FROM mev_attacks 
        WHERE detected_at > NOW() - INTERVAL '{hours} hours'
        ORDER BY detected_at DESC
    """
    return pd.read_sql(query, engine)
```

---

## Testing Live Integration

### Devnet Testing

```python
# Use devnet for testing
DEVNET_RPC = "https://api.devnet.solana.com"
client = Client(DEVNET_RPC)

# Test transaction fetching
test_slot = client.get_slot()['result']
test_block = client.get_block(test_slot - 5)
print(f"Devnet block #{test_slot-5}: {len(test_block['result']['transactions'])} txs")
```

### Monitoring Dashboard

Add health check tab:

```python
dcc.Tab(label='🔧 System Health', children=[
    html.Div([
        html.H3('API Status'),
        html.Div(id='api-status-display'),
        dcc.Interval(id='health-check-interval', interval=10000, n_intervals=0)
    ])
])

@app.callback(
    Output('api-status-display', 'children'),
    Input('health-check-interval', 'n_intervals')
)
def check_api_health(n):
    statuses = []
    
    # Check Helius
    try:
        fetcher = HeliusFetcher()
        fetcher.client.get_slot()
        statuses.append(html.P('✅ Helius RPC: Connected', style={'color': 'green'}))
    except:
        statuses.append(html.P('❌ Helius RPC: Failed', style={'color': 'red'}))
    
    # Check Jito
    try:
        monitor = JitoMonitor()
        monitor.get_recent_bundles()
        statuses.append(html.P('✅ Jito API: Connected', style={'color': 'green'}))
    except:
        statuses.append(html.P('⚠️ Jito API: Unavailable', style={'color': 'orange'}))
    
    return statuses
```

---

## Deployment Checklist

Before deploying with live data:

- [ ] API keys stored in environment variables (not code)
- [ ] Error handling for all API calls
- [ ] Rate limiting implemented (respect API quotas)
- [ ] Caching layer configured
- [ ] Database setup for historical storage
- [ ] Background tasks running (Celery/Redis)
- [ ] Health monitoring dashboard active
- [ ] Alerts configured for API failures
- [ ] Auto-retry logic for transient errors
- [ ] Logging configured (errors + performance metrics)

---

## Troubleshooting

### Common Issues

**1. RPC Connection Timeout**
```python
# Increase timeout
from solana.rpc.api import Client
from solana.rpc.providers.http import HTTPProvider

provider = HTTPProvider(rpc_url, timeout=30)  # 30 second timeout
client = Client(provider)
```

**2. WebSocket Disconnects**
```python
# Implement reconnection logic
import websocket
import time

def on_error(ws, error):
    print(f"WebSocket error: {error}")
    time.sleep(5)
    reconnect_websocket()
```

**3. Memory Leaks with Large DataFrames**
```python
# Clear old data periodically
import gc

if len(transactions_df) > 10000:
    transactions_df = transactions_df.tail(5000)  # Keep recent 5000
    gc.collect()
```

---

**Last Updated**: February 27, 2026  
**Next Steps**: See `AI_PROMPTS.md` for code generation prompts
