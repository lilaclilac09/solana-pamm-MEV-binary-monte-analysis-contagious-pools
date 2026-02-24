# Quick Start: Binary Monte Carlo for MEV Contagion

## 30-Second Quickstart

```bash
# In the 08_monte_carlo_risk/ folder, open the notebook:
jupyter notebook 09_binary_monte_carlo_contagion.ipynb

# Then press Ctrl+A to select all cells, Shift+Enter to run them all
# Results appear in ~4 seconds
```

## What You'll Get

### 📊 CSV Results (3 files, 100k rows each)
- `monte_carlo_jito_baseline_*.csv` — 14.9% attack rate, 3.99 cascades
- `monte_carlo_bam_privacy_*.csv` — 14.97% attack rate, 1.41 cascades (64% reduction)
- `monte_carlo_harmony_multibuilder_*.csv` — 15.03% attack rate, 1.93 cascades (52% reduction)

### 📈 Visualizations (4 PNG files)
1. **Cascade distribution histograms** — Compare distributions across scenarios
2. **Infrastructure comparison** — Risk metrics side-by-side
3. **Box plots** — Quartiles for cascades, slots, losses
4. **Oracle lag correlation** — 2D heatmaps showing relationships

### 📋 Summary Statistics
```
Infrastructure               Attack % | Mean Cascades | P90 Slots | Mean Loss | High Risk %
────────────────────────────────────────────────────────────────────────────────────────
Jito Baseline                 14.90%  |     3.99      |    6.00   |  $415.23  |   11.62%
BAM Privacy (65% reduction)   14.97%  |     1.41      |    3.00   |  $148.22  |    1.45%
Harmony Multi-Builder         15.03%  |     1.93      |    4.00   |  $201.01  |    2.90%
```

---

## How the Simulation Works

### Stage 1: Attack Trigger
```python
trigger = np.random.rand() < 0.15  # 15% of slots have attacks
```

### Stage 2: Cascades (Infrastructure-Dependent)
```python
# Visibility reduction = how much the infrastructure hides MEV
# Higher visibility_reduction → more hidden → fewer cascades

cascade_rate = 0.801  # 80.1% baseline (from data)

# Jito
effective_rate = 0.801 * (1 - 0.0)       # = 64.0%
cascades = Binomial(5, 0.640)             # 0-5 cascades

# BAM (65% visibility reduction)
effective_rate = 0.801 * (1 - 0.65)       # = 28.0%
cascades = Binomial(5, 0.280)             # 0-5 cascades (fewer on average)

# Harmony (40% reduction + 20% competition suppression)
effective_rate = 0.801 * (1 - 0.40) * 0.8 # = 38.4%
cascades = Binomial(5, 0.384)             # 0-5 cascades
```

### Stage 3: Slot Jumps (Network Congestion Proxy)
```python
# Each cascade takes time (100-700ms uniformly)
# Solana slot = 400ms
# High jumps → more slots consumed → higher skipped-slot risk

cascade_times = np.random.uniform(100, 700, cascades)
total_time = sum(cascade_times)
slots_jumped = ceil(total_time / 400)

# If slots_jumped > 3 → marked as "high risk"
```

### Stage 4: Economic Impact
```python
# Loss = base damage + oracle lag impact
loss_per_cascade = 50 + (180ms oracle_lag * 0.3)  # ≈ $104 per cascade
total_loss = cascades * loss_per_cascade + noise
```

---

## Customize & Extend

### Add New Scenario

```python
# In mev_contagion_monte_carlo.py, add to self.scenarios:

'your_scenario': {
    'name': 'Your Infrastructure Name',
    'base_trigger_prob': 0.15,
    'cascade_rate': 0.801,
    'visibility_reduction': 0.75,  # ← Adjust this (0-1)
    'description': 'Your description here'
}

# Then in notebook:
mc = ContagionMonteCarlo()
results = mc.run_all_scenarios(n_sims=100_000)
```

### Load Real Oracle Lag Data

```python
# Instead of fixed 180ms, use distribution from oracle analysis:
oracle_df = pd.read_csv('../03_oracle_analysis/outputs/*.csv')
oracle_lags = oracle_df['oracle_lag_ms'].values

# Use in simulation:
for sim in range(n_sims):
    oracle_lag = np.random.choice(oracle_lags)  # Sample from real data
    # ... rest of simulation
```

### Weight by Validator Centralization

```python
validator_df = pd.read_csv('../04_validator_analysis/VALIDATOR_POOL_PARTICIPATION.csv')
centralization = validator_df['stake_concentration'].mean()

# Higher centralization → higher cascade multiplier
cascade_multiplier = 1 + centralization
effective_cascades = cascades * cascade_multiplier
```

---

## Key Outputs Explained

### Comparison Table

| Metric | Meaning | Why It Matters |
|--------|---------|----------------|
| **Attack Rate %** | % of slots where attacks trigger | Should be ~15% (market probability) |
| **Mean Cascades** | Avg cascades per triggered attack | Lower = better (less contagion) |
| **P90 Cascades** | 90th percentile of cascades | 90% of attacks are below this |
| **P90 Slots** | 90th percentile of slots jumped | Correlates with skipped-slot risk |
| **Mean Loss** | Average economic loss per attack | Direct financial impact |
| **High Risk %** | % of sims with slots > 3 | Proxy for validator downtime risk |

### Protection Metrics

```
BAM Privacy vs Jito Baseline:
  Cascade reduction: 64.7%
  P90 slots reduction: 50.0%
  Economic loss reduction: 64.3%
  High-risk event reduction: 87.5%

Interpretation:
- Cascades drop by ~2/3 (from 3.99 to 1.41)
- Congestion (slots jumped) drops by 1/2 (from 6 to 3)
- Economic loss drops by ~2/3 (from $415 to $148)
- Only 1.45% of attacks pose high-risk (vs 11.62%)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"
**Solution**: Run cell 1 first (library imports), or install manually:
```bash
pip install numpy pandas matplotlib seaborn scipy
```

### Results don't save to outputs/
**Solution**: Ensure `outputs/` directory exists:
```bash
mkdir -p 08_monte_carlo_risk/outputs
```

### Simulation takes >5 seconds
**Solution**: Reduce n_sims in cell 10:
```python
results = mc.run_all_scenarios(n_sims=10_000)  # 10k instead of 100k (10x faster)
```

### Want to compare with historical data?
**Solution**: See cell 17 (validation section):
- Loads `contagion_report.json`
- Compares Monte Carlo output to empirical cascade rates
- Shows goodness-of-fit diagnostics

---

## Files Generated

Each run creates timestamped outputs:

```
outputs/
├── monte_carlo_jito_baseline_20260224_120000.csv
├── monte_carlo_bam_privacy_20260224_120000.csv
├── monte_carlo_harmony_multibuilder_20260224_120000.csv
├── monte_carlo_summary_binary_monte_carlo_20260224_120000.csv
├── monte_carlo_cascade_distributions_20260224_120000.png
├── infrastructure_comparison_20260224_120000.png
├── monte_carlo_boxplots_20260224_120000.png
└── oracle_lag_correlation_20260224_120000.png
```

Delete old files to avoid clutter:
```bash
rm outputs/monte_carlo_*.csv outputs/*.png
```

---

## Questions?

- **What's "slots jumped"?** → Proxy for network congestion (higher = more leader skips)
- **Why cascade rate 80.1%?** → From your `contagion_report.json` (historical data)
- **Why 100k simulations?** → Statistical power (captures tail risks at P99)
- **Can I use different oracle lags?** → Yes! Modify `oracle_lag_ms` in MC initialization or load from CSV
- **What about validator participation?** → See "Extend" section above

---

**Ready to run?** Open `09_binary_monte_carlo_contagion.ipynb` and hit Shift+Enter!
