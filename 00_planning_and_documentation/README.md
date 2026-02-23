# Notebooks - MEV Analysis Pipeline

This directory contains all analysis notebooks organized by analysis type. Each notebook has its own folder with outputs and documentation.

## 📁 Folder Structure

```
notebooks/
├── 01_data_cleaning/              # Data cleaning & parsing
├── 01a_data_cleaning_filters/     # DeezNode filter
├── 01b_jito_tip_filter/           # Jito tip filter
├── 02_mev_detection/              # All MEV detection algorithms
├── 03_oracle_analysis/           # Oracle timing & burst detection
├── 04_validator_analysis/         # Validator MEV metrics & clustering
├── 05_token_pair_analysis/       # Single AMM token pair MEV (with aggregator + MEV selection)
├── 06_pool_analysis/              # General pool MEV analysis
├── 07_ml_classification/          # ML classification for MEV bots
├── 08_monte_carlo_risk/           # Monte Carlo risk simulation
```

## 📊 Execution Order

1. **01_data_cleaning/** - Clean and parse raw data
2. **01a_data_cleaning_filters/** - Filter DeezNode transactions
3. **01b_jito_tip_filter/** - Filter Jito tip transactions
4. **02_mev_detection/** - Detect all MEV patterns
5. **03_oracle_analysis/** - Analyze oracle patterns
6. **04_validator_analysis/** - Analyze validator MEV metrics
7. **05_token_pair_analysis/** - Deep-dive single token pair analysis
8. **06_pool_analysis/** - General pool analysis
9. **07_ml_classification/** - ML model training and classification
10. **08_monte_carlo_risk/** - Risk simulation
11. **09_aggregator_mev_analysis/** - Combined aggregator + MEV analysis

## 📝 Each Folder Contains

- **Notebook file** (`.ipynb`) - The analysis notebook
- **notes.md** - Detailed documentation of the analysis
- **outputs/** - Analysis outputs
  - **csv/** - CSV data files
  - **images/** - Visualization images

## 🔍 Quick Reference

| Notebook | Purpose | Key Outputs |
|----------|---------|-------------|
| `01_data_cleaning` | Parse account_updates, trades, timing | Cleaned dataset |
| `01a_data_cleaning_filters` | Filter DeezNode addresses | Filtered dataset |
| `01b_jito_tip_filter` | Filter Jito tip addresses | Filtered dataset |
| `02_mev_detection` | All 7 MEV algorithms | `comprehensive_mev_all_with_pnl.csv` |
| `03_oracle_analysis` | Oracle timing patterns | `oracle_bursts.csv`, `top_oracle_updaters.csv` |
| `04_validator_analysis` | Validator MEV metrics | `mev_trades_bots_per_validator.csv` |
| `05_token_pair_analysis` | Single token pair deep-dive | `per_pool_analysis.csv`, `monte_carlo_by_token_pair.csv` |
| `06_pool_analysis` | General pool analysis | `pool_density_analysis.csv` |
| `07_ml_classification` | ML bot classification | `ml_model_performance.csv`, `feature_importance.csv` |
| `08_monte_carlo_risk` | Risk simulation | `monte_carlo_by_*.csv` |


## 📚 Documentation

- Each folder has a `notes.md` file with detailed documentation


## 🔗 Key Code Locations

All code locations are documented in `CODE_ORGANIZATION_PLAN.md` with 📍 markers pointing to:
- Source notebook locations
- Specific cell numbers
- Reference documentation

## ⚠️ Important Notes

- **All code stays in `.ipynb` notebooks** - NO `.py` file extraction
- Outputs are organized in each notebook's `outputs/` folder
- Each notebook is self-contained with its own documentation
