# Jupiter Analysis Folder

This folder contains all Jupiter multi-hop and MEV detection refinement tools.

## Files

### Analysis Files
- **`02_jupiter_multihop_analysis.ipynb`** - Jupyter notebook detecting multi-hop routing patterns
  - Analyzes 5.5M+ transactions
  - Identifies Jupiter and aggregator routing
  - Tags: `is_multihop`, `hop_count`, `route_key`

### Guides & Documentation
- **`JUPITER_MULTIHOP_GUIDE.md`** - Complete guide on Jupiter multi-hop analysis
  - Results: 10.03% of txns are multi-hop (2+ legs)
  - Integration with contagion analysis
  - ML classification results

### Utilities & Scripts
- **`export_jupiter_tags.py`** - Tags raw data with Jupiter routing information
- **`integrate_jupiter_contagion.py`** - Connects Jupiter routing to contagion analysis

### MEV Refinement Scripts
- **`refine_mev_detection.py`** - **IMPORTANT: Run this first!**
  - Separates legitimate multi-hop bot trading from actual MEV sandwich attacks
  - Removes false positives where bots used multi-hop routes
  - Creates 3 datasets:
    - `true_mev_sandwiches.parquet` - Actual sandwich attacks
    - `legitimate_multihop_bots.parquet` - False positives (legit bot routing)
    - `normal_trades.parquet` - Regular trades
  - Generates: `mev_refinement_summary.json` and `mev_refinement_breakdown.csv`

- **`separate_mev_from_aggregators.py`** - Alternative separation approach
  - Classifies all transactions into categories
  - Exports filtered datasets by type

### Data & Results
- **`jupiter_contagion_analysis.json`** - Analysis results
- **`outputs/`** - Generated datasets and statistics

### Visualizations
- **`02_jupiter_routing_distribution.png`** - Distribution of routing patterns
- **`02_jupiter_stacked_routing.png`** - Stacked breakdown
- **`02_jupiter_timeseries_multihop.png`** - Time-series trends

## Quick Start

### Step 1: Run MEV Detection Refinement
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/02_mev_detection/jupiter_analysis

python3 refine_mev_detection.py
```

This will:
- Load your MEV-detected transactions
- Identify which ones used multi-hop routes (legitimate aggregator trading)
- Separate them from actual sandwich attacks
- Create 3 clean datasets in `outputs/`

### Step 2: Use Refined Data
```python
# TRUE MEV sandwiches only (actual attacks)
df_sandwiches = pd.read_parquet('outputs/true_mev_sandwiches.parquet')

# Legitimate multi-hop bots (previously misclassified)
df_bots = pd.read_parquet('outputs/legitimate_multihop_bots.parquet')

# Normal trades
df_normal = pd.read_parquet('outputs/normal_trades.parquet')
```

## What This Solves

### The Problem
Your MEV detector was flagging legitimate multi-hop bot trading as sandwich attacks because:
- Bots use aggregators like Jupiter to find best routes
- These create multi-leg transactions (A → B → C)
- The detector saw this as an attack pattern (A-B-A but through aggregator)
- **Result: False positives!**

### The Solution
This folder contains tools to:
1. **Identify multi-hop patterns** - Which transactions used aggregator routing?
2. **Separate by type**:
   - **Real MEV** - True sandwich attacks (have victim signatures)
   - **Legitimate Bots** - Normal multi-hop routing (no victim signatures)
   - **Normal Trades** - Everything else
3. **Remove false positives** - The multi-hop bots are NOT attacks

## Key Metrics

From `02_jupiter_multihop_analysis.ipynb`:
- **Multi-hop transactions: 10.03%** of volume (552,250 txns)
- **Single-hop: 2.39%** (131,578 txns)
- **Direct: 87.58%** (4.8M txns)

These multi-hop transactions should NOT be counted as MEV attacks.

## Next Steps

After running `refine_mev_detection.py`:
1. Use `outputs/true_mev_sandwiches.parquet` for accurate MEV analysis
2. Compare attack frequency before/after refinement
3. Update your risk models with corrected data
4. Use `outputs/legitimate_multihop_bots.parquet` for bot behavior studies

---

**Last Updated:** February 25, 2026
