# Section 5c Plot Generation - Using Real Data

## Overview
Section 5c "Threat Intelligence Visualizations" displays three editorial-style plots generated from actual MEV attack data extracted from your workspace analysis.

## Generated Files

### 1. **token_pair_fragility.png**
- **Size:** 402K
- **Data Source:** Pool MEV summary showing HumidiFi as 39.5% of all attacks
- **Key Insight:** Visualizes high-risk token pair concentration (HumidiFi) vs diversified/safe pools

### 2. **oracle_latency_window.png** 
- **Size:** 542K
- **Data Source:** Median `us_since_first_shred` latencies from detailed activity CSVs
- **Key Insight:** Shows 0.3-0.4 second oracle latency windows across HumidiFi, GoonFi, SolFiV2

### 3. **mev_battlefield.png**
- **Size:** 475K
- **Data Source:** Pool profit totals from `pool_mev_summary.csv`
- **Key Insight:** Displays 66.8% HumidiFi profit concentration (75.1 SOL of 112.43 total)

## Real Data Used

Based on `visualization_data.json` generated from your analysis:

```json
{
  "token_pair_fragility": {
    "headline_percent": 39.5,
    "pump_wsol_label": "High-Risk Pool (HumidiFi)"
  },
  "oracle_latency_window": {
    "headline_latency_seconds": 0.4,
    "headline_trade_percent": 39.5,
    "pool_latencies_us": {
      "GoonFi": 322161,
      "HumidiFi": 341033,
      "SolFiV2": 350892
    }
  },
  "mev_battlefield": {
    "pool_profits_sol": {
      "HumidiFi": 75.1,
      "BisonFi": 11.2,
      "GoonFi": 7.9,
      "TesseraV": 7.8,
      "SolFiV2": 7.5,
      "ZeroFi": 2.8,
      "ObricV2": 0.1
    },
    "profit_share_percent": {
      "HumidiFi": 66.8,
      "BisonFi": 10.0,
      "GoonFi": 7.0,
      "TesseraV": 7.0,
      "SolFiV2": 6.7,
      "ZeroFi": 2.5,
      "ObricV2": 0.1
    }
  }
}
```

## Workflow to Regenerate Plots

### Step 1: Extract Real Data from Analysis Results
```bash
python3 extract_real_data.py
```

**What it does:**
- Reads `13_mev_comprehensive_analysis/outputs/from_02_mev_detection/pool_mev_summary.csv` for profit data
- Reads `02_mev_detection/POOL_SUMMARY.csv` for attack concentration
- Samples multiple `attacker_*_detailed_activity.csv` files for latency statistics
- Outputs `visualization_data.json` with real values

**Output:** `visualization_data.json`

### Step 2: Generate Visualizations
```bash
python3 generate_visualizations.py --data-file visualization_data.json --out-dir app/assets
```

**What it does:**
- Loads data from `visualization_data.json` (or uses DEFAULT_DATA if omitted)
- Generates three 300 DPI PNG images using matplotlib
- Saves directly to `app/assets/` directory for Dash app usage

**Output:**
- `app/assets/token_pair_fragility.png`
- `app/assets/oracle_latency_window.png`
- `app/assets/mev_battlefield.png`

### Step 3: Verify in Dashboard
The plots are automatically loaded by [app/index.py](app/index.py#L83-L147) in Section 5c:

```python
# Section 5c: Threat Intelligence Visualizations
html.Div([
    html.H2("Section 5c: Threat Intelligence Visualizations", 
            style={"color": section_colors["5"], "marginTop": "1em"}),
    
    html.Img(src='/assets/token_pair_fragility.png', 
             style={'width': '100%', 'marginBottom': '2em'}),
    
    html.Img(src='/assets/oracle_latency_window.png', 
             style={'width': '100%', 'marginBottom': '2em'}),
    
    html.Img(src='/assets/mev_battlefield.png', 
             style={'width': '100%', 'marginBottom': '2em'})
], style={"backgroundColor": "#fff8dc", "padding": "2em", "marginBottom": "2em"})
```

## File Relationships

```
workspace/
├── extract_real_data.py                 # NEW: Extracts real data from CSVs
├── visualization_data.json              # NEW: Real data in JSON format
├── generate_visualizations.py           # Existing: Matplotlib plot generator
├── visualization_data.example.json      # Template with example values
├── app/
│   ├── index.py                         # Dash app that renders Section 5c
│   └── assets/
│       ├── token_pair_fragility.png     # Generated plot 1
│       ├── oracle_latency_window.png    # Generated plot 2
│       └── mev_battlefield.png          # Generated plot 3
└── 13_mev_comprehensive_analysis/outputs/from_02_mev_detection/
    ├── pool_mev_summary.csv             # Source: Pool profit data
    ├── attacker_*_detailed_activity.csv # Source: Oracle latency timings
    └── ...
```

## Data Sources Detail

### Pool Profits (mev_battlefield)
**File:** `13_mev_comprehensive_analysis/outputs/from_02_mev_detection/pool_mev_summary.csv`

| Pool      | Total Profit (SOL) | % of Total |
|-----------|-------------------|------------|
| HumidiFi  | 75.11             | 66.8%      |
| BisonFi   | 11.23             | 10.0%      |
| GoonFi    | 7.88              | 7.0%       |
| TesseraV  | 7.83              | 7.0%       |
| SolFiV2   | 7.50              | 6.7%       |
| ZeroFi    | 2.77              | 2.5%       |
| ObricV2   | 0.11              | 0.1%       |

### Oracle Latency (oracle_latency_window)
**Files:** `attacker_*_detailed_activity.csv` (sampled 5 files)

| Pool      | Median Latency (us) | Seconds |
|-----------|---------------------|---------|
| HumidiFi  | 341,033             | 0.34s   |
| SolFiV2   | 350,892             | 0.35s   |
| GoonFi    | 322,161             | 0.32s   |

### Attack Concentration (token_pair_fragility)
**File:** `02_mev_detection/POOL_SUMMARY.csv`

- **HumidiFi attacks:** 593 (39.5% of 1,500 total)
- Highest concentration of MEV events in the ecosystem

## Customization

To adjust plot appearance, edit:
- **Colors/Fonts:** Modify matplotlib styling in `generate_visualizations.py` lines 84-307
- **Data Values:** Update `visualization_data.json` or rerun `extract_real_data.py`
- **Plot Layout:** Adjust figsize, axes positions in plot creation functions

## Notes

- Plots are 300 DPI publication-quality PNG images
- Default data is embedded in `generate_visualizations.py` if no JSON provided
- The script uses deep_merge to override DEFAULT_DATA with JSON values
- Generated timestamps: March 3, 2026 16:37
