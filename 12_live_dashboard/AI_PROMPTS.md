# AI Prompts for Integrating Live Data into Solana MEV Dashboard

This document contains ready-to-use prompts for AI code generation to extend your interactive dashboard with live Solana data. These prompts are designed for use with models like GPT-4, Claude, or Grok.

**How to Use**: Copy a prompt, paste into your AI assistant, and use the generated code in your dashboard project.

---

## 1. Fetching Live Transaction Data via Helius RPC

**Prompt:**
```
Generate Python code using the Helius Solana RPC API to fetch the last 100 confirmed transactions from recent blocks on the Solana mainnet. Focus on events from AMM protocols like HumidiFi, BisonFi, or equivalents (e.g., Raydium or Orca if placeholders). Parse the data for trade events, including slot numbers, signers, and account updates. Include error handling and rate limiting. Use the 'getBlock' or 'getRecentBlockhash' methods, and output the data as a Pandas DataFrame for easy integration into a dashboard.
```

**Expected Output**: Python function that returns DataFrame with columns: `slot`, `signer`, `pool`, `trade_type`, `amount_sol`, `timestamp`

---

## 2. Real-Time MEV Tip and Bundle Monitoring via Jito API

**Prompt:**
```
Write a Python script that uses the Jito Block Engine API to stream real-time MEV tips, bundle submissions, and rewards on Solana. Poll the Jito explorer endpoint (e.g., via requests to explorer.jito.wtf API if available) every 30 seconds for metrics like total tips in SOL, bundle activity, and validator stake share. Format the output as JSON and include a function to detect spikes in MEV activity (e.g., tips > 10 SOL in a slot). Make it compatible with Dash callbacks for live updates.
```

**Expected Output**: Polling function that returns JSON with `total_tips_sol`, `bundle_count`, `top_validators`, `spike_detected`

---

## 3. Detecting Sandwich Attacks in Live Data

**Prompt:**
```
Based on the MEV detection algorithms from a Solana pAMM report (e.g., fat sandwich with 5+ trades per slot, same signer for front-run and back-run), create Python code to analyze live Solana transactions fetched via Helius RPC. Identify patterns like attacker-victim-attacker sequences, exclude false positives (e.g., zero-profit or aggregator routes like Jupiter), and calculate extracted value in SOL. Use Pandas for data processing and output a list of detected attacks with details like attacker address, victim trade size, and profit.
```

**Expected Output**: Function `detect_sandwich_attacks(transactions_df)` returning list of dicts with attack details

---

## 4. Integrating Webhooks for Real-Time Event Notifications

**Prompt:**
```
Generate code for setting up Helius webhooks in Python to receive real-time notifications for Solana account updates or transactions in specific pAMM pools (e.g., HumidiFi or similar DEXes). Handle incoming webhook payloads to parse oracle updates and trades, then trigger MEV pattern detection (e.g., back-running within 50ms of oracle refresh). Include a Flask endpoint for receiving webhooks and integrating with a Dash app to update charts live.
```

**Expected Output**: Flask app with `/webhook` endpoint + integration code for Dash callback updates

---

## 5. Updating Dashboard with Live Contagion Analysis

**Prompt:**
```
Modify the provided Dash app code to add a new tab for live contagion analysis. Use data from Jito or Helius to track cross-pool MEV attacks (e.g., attacker overlap between pools like HumidiFi and BisonFi). Generate a real-time heatmap using Plotly for attacker distribution and cascade probabilities, polling every minute. Include Monte Carlo simulation code to estimate delayed contagion risk (22% baseline from report) based on recent data.
```

**Context to Provide**: Share your current `mev_dashboard.py` code

**Expected Output**: New Dash tab with auto-updating heatmap and simulation results

---

## 6. Visualizing Live MEV Profit Distribution

**Prompt:**
```
Create Plotly code snippets for a Dash dashboard to display live MEV profit distribution by protocol. Fetch real-time data from DeFi Llama API (for TVL) combined with Jito MEV metrics. Recreate visuals like bar charts for profits (e.g., HumidiFi at 66.8% share) and pie charts for risk levels, updating dynamically. Handle data filtering for false positives and add tooltips with details like attack counts and top attackers.
```

**Expected Output**: Dash callback function with Plotly figures for bar/pie charts updating from live data

---

## 7. Oracle Manipulation Detection in Live Streams

**Prompt:**
```
Write a Python function using Solana's gRPC streaming (e.g., via Helius LaserStream) to monitor oracle updates in pAMM protocols. Detect manipulation patterns (e.g., trades within 400ms of price updates) and correlate with validator behavior. Output alerts for high-risk slots and integrate as a live feed in a Dash component, similar to the report's oracle timing analysis.
```

**Expected Output**: Streaming function + Dash component for real-time alerts

---

## 8. Top Attacker Ranking with Live Data

**Prompt:**
```
Generate code to rank top MEV attackers on Solana in real-time using transaction data from QuickNode or Helius RPC. Parse signers from recent bundles via Jito, calculate profits (correct for mismatches like 13.716 SOL to 16.731 SOL), and display a bar chart in Dash. Update every 5 minutes and filter for validated fat sandwich attacks (e.g., 617 baseline).
```

**Expected Output**: Scheduled function + Dash callback for updating top attackers chart

---

## 9. Full Live Dashboard Extension

**Prompt:**
```
Extend the following Dash Python code to plug in live Solana data: Add interval components for polling Helius RPC and Jito APIs, update DataFrames with new events, and refresh tabs like MEV Distribution, Contagion Analysis, and Monte Carlo Simulations. Ensure it handles 5M+ events efficiently with caching, and add a 'Live Mode' toggle.
```

**Context to Provide**: Share your complete `mev_dashboard.py` file

**Expected Output**: Enhanced dashboard with `dcc.Interval`, data fetching, and toggle switch

---

## 10. Custom User Queries on Live Data

**Prompt:**
```
Create a natural language processing prompt system in Python (using Hugging Face or similar) for a Solana MEV dashboard. Allow users to query live data like 'Show recent sandwich attacks on HumidiFi' or 'Estimate contagion risk for BisonFi'. Use fetched data from Helius to generate responses with tables and charts, integrated as a chat component in Dash.
```

**Expected Output**: Dash chat interface with NLP backend for querying MEV data

---

## Advanced Integration Prompts

### 11. Real-Time Validator Coordination Tracking

**Prompt:**
```
Create Python code to track validator coordination in real-time MEV bundles on Solana. Use Jito API to identify validators ordering suspicious transaction sequences (front-run → victim → back-run within single slot). Calculate validator revenue share (estimated 15-35% from report) and display network graph in Dash showing validator-attacker relationships. Update graph every 2 minutes.
```

---

### 12. Crisis Event Detection (Liquidity Depletion)

**Prompt:**
```
Write a monitoring system in Python that detects liquidity crisis events in Solana pAMM pools similar to the SOL/USDC case study (reserves dropping from $850K to $75K). Use Helius RPC to track pool reserves in real-time and trigger alerts when depletion > 80% occurs. Integrate with Dash to show crisis timeline and predict MEV attack probability spikes.
```

---

### 13. Multi-Slot Attack Sequence Visualization

**Prompt:**
```
Generate Plotly code for visualizing multi-slot MEV attack sequences like the PYTH/WSOL case (3 slots: LP deposit → sandwich → LP removal). Parse live transaction data to identify cross-slot patterns and create animated timeline visualizations showing attacker actions, validator coordination, and profit extraction. Integrate as interactive chart in Dash.
```

---

### 14. Funding Source Tracker Integration

**Prompt:**
```
Create Python code to integrate with orbmarkets.io or similar blockchain analytics APIs to track MEV attacker funding sources. Given a Solana wallet address (e.g., YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP), trace back to CEX deposits (Binance, Kraken, FTX) and identify wallet clusters. Display as network graph in Dash with funding flow arrows.
```

---

### 15. Comparative Pool Risk Heatmap

**Prompt:**
```
Write Dash code to create a live comparative risk heatmap showing real-time MEV exposure across all 8 pAMM protocols (HumidiFi, BisonFi, GoonFi, SolFiV2, TesseraV, ZeroFi, SolFi, ObricV2). Calculate risk score based on: attack frequency, profit concentration, oracle latency, and liquidity depth. Use color gradient (green=low, red=high) and update every 60 seconds.
```

---

## Implementation Workflow

### Recommended Execution Order:
1. Start with **Prompt 1** (data fetching) to establish data pipeline
2. Add **Prompt 3** (sandwich detection) for core MEV analysis
3. Implement **Prompt 6** (profit distribution) for first live visualization
4. Deploy **Prompt 4** (webhooks) for real-time push notifications
5. Extend with **Prompt 9** (full dashboard integration)
6. Advanced: Add **Prompts 11-15** for specialized features

### Testing Strategy:
- Use Solana **devnet** for initial testing to avoid mainnet costs
- Start with small data samples (100 transactions) before scaling to 5M+
- Implement rate limiting to respect API quotas (Helius: 100 req/sec)
- Add error logging for all external API calls

### Deployment Considerations:
- **Caching**: Use Redis to store fetched data and reduce API calls
- **Background Tasks**: Use Celery for async data fetching
- **Database**: Consider PostgreSQL for storing historical MEV events
- **Monitoring**: Add Sentry or similar for error tracking

---

## API Setup Checklist

Before using these prompts, ensure you have:

- [ ] Helius API key (free tier: 100K req/day)
- [ ] Jito API access (check jito.network for requirements)
- [ ] Solana RPC endpoint (Helius, QuickNode, or public)
- [ ] (Optional) DeFi Llama API access for TVL data
- [ ] (Optional) Orbmarkets.io account for wallet tracking

### Environment Variables Template:
```bash
# Add to .env file
HELIUS_API_KEY="your_key_here"
HELIUS_RPC_URL="https://mainnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}"
JITO_API_KEY="your_jito_key"
DASH_SECRET_KEY="random_secret_for_sessions"
```

---

## Troubleshooting AI Responses

If AI-generated code doesn't work:

1. **Missing imports**: Check for all required libraries
2. **API changes**: Verify endpoint URLs against latest docs
3. **Data schema**: Ensure DataFrame columns match expected format
4. **Authentication**: Confirm API keys are set correctly
5. **Rate limits**: Add time.sleep() or async handling

### Example Fix:
```python
# If Helius API returns different schema
# Original AI code might expect:
df['slot'] = data['slot']

# But API returns:
df['slot'] = data['result']['slot']  # Nested structure
```

---

## Performance Benchmarks

Expected processing times (on standard hardware):

| Task | Volume | Time | Notes |
|------|--------|------|-------|
| Fetch transactions | 100 txs | ~2s | Helius RPC |
| Detect sandwiches | 1000 txs | ~5s | Pandas processing |
| Update dashboard | Full refresh | ~3s | All charts |
| Live polling | Continuous | 60s interval | Recommended |

For better performance:
- Batch API requests
- Use async/await for parallel fetching
- Implement data pagination
- Cache frequently accessed data

---

**Last Updated**: February 27, 2026  
**Maintenance**: Update prompts as APIs evolve  
**Community**: Share improvements via GitHub issues
