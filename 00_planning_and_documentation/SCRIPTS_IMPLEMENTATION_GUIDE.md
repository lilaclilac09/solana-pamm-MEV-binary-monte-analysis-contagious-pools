# Scripts Implementation Summary

**Date:** February 24, 2026  
**Location:** `/scripts/` folder (created)  
**Total Scripts:** 9 ready-to-run Python modules

---

## Overview

All scripts assume execution from the **repository root** and process data through the complete MEV contagion pipeline. Each script is standalone but can be chained together for end-to-end analysis.

---

## Script Inventory

### 1. `01_top_attackers_extractor.py`
**Purpose:** Extract and rank top MEV attackers from PAMM dataset

**Input:**
- `data/pamm_clean_final.parquet` (configurable)

**Output:**
- `outputs/top_attackers_report.json`

**Key Operations:**
- Aggregate attacker stats (profit, attack count, cascade count)
- Cross-reference with known sandwicher list
- Sort by total profit descending

**Run:**
```bash
python scripts/01_top_attackers_extractor.py
```

**Dependencies:** `pandas`, `pyarrow`

---

### 2. `02_fetch_sandwiched_me_top.py`
**Purpose:** Scrape current top 10 sandwichers from sandwiched.me (30-day window)

**Input:**
- Live web scrape from `https://sandwiched.me/`

**Output:**
- `outputs/sandwiched_me_top_30d.json`

**Key Operations:**
- Parse HTML table from sandwiched.me
- Extract rank, address, profit_sol, extracted_sol
- Timestamp report with ISO datetime

**Run:**
```bash
python scripts/02_fetch_sandwiched_me_top.py
```

**Dependencies:** `requests`, `beautifulsoup4`

**Note:** If scraping breaks, manually copy top 10 from website into JSON format (~10 lines)

---

### 3. `03_update_contagion_report_with_attackers.py`
**Purpose:** Inject real attacker statistics into contagion_report.json

**Input:**
- `contagion_report.json` (existing)
- `data/pamm_clean_final.parquet` (attacker data)

**Output:**
- `contagion_report.json` (updated with new section)

**Key Operations:**
- Load current report
- Add `top_attackers_section` with top 20 by profit
- Count total unique attackers in dataset
- Overwrite contagion_report with enriched data

**Run:**
```bash
python scripts/03_update_contagion_report_with_attackers.py
```

**Dependencies:** `pandas`, `pyarrow`

---

### 4. `04_validator_winrate_per_prop_amm.py`
**Purpose:** Compute validator win rates aggregated by Proposer/AMM pair

**Input:**
- `validator_contagion_graph.json` (from phase 1 analysis)

**Output:**
- `outputs/validator_winrate_per_prop_amm.csv`

**Key Operations:**
- Extract `validator_amm_pairs` from graph JSON
- Group by proposer/AMM combination
- Calculate mean win_rate and sum block_count
- Sort descending by average win rate

**Run:**
```bash
python scripts/04_validator_winrate_per_prop_amm.py
```

**Dependencies:** `pandas`

---

### 5. `05_oracle_latency_comparison.py`
**Purpose:** Aggregate oracle latency metrics across multiple pools

**Input:**
- `data/oracle_bisonfi.csv` (adjust paths as needed)
- `data/oracle_humidifi.csv`
- `data/oracle_raydium.csv`

**Output:**
- `outputs/oracle_latency_comparison.csv`

**Key Operations:**
- Load multiple oracle log CSVs
- Extract pool name from filename
- Compute per-pool statistics: mean, max, median lag_ms
- Rank by median latency

**Run:**
```bash
python scripts/05_oracle_latency_comparison.py
```

**Dependencies:** `pandas`

**Note:** Adjust file paths before running based on your oracle data location

---

### 6. `06_test_twap_bam_protection.py`
**Purpose:** Monte Carlo simulation of TWAP + BAM mitigation effectiveness

**Input:**
- None (simulation-only)

**Output:**
- `outputs/twap_bam_simulation.csv`

**Key Parameters:**
- Base cascade rate: 80.1%
- TWAP reduction: 85%
- BAM visibility reduction: 65%
- Number of simulations: 10,000

**Key Operations:**
- For each sim: compute effective cascade rate after both mitigations
- Binomial sample (5 max jumps per slot)
- Output statistics and save distribution

**Run:**
```bash
python scripts/06_test_twap_bam_protection.py
```

**Dependencies:** `numpy`, `pandas`

---

### 7. `07_extend_monte_carlo_with_top_attackers.py`
**Purpose:** Weighted Monte Carlo simulation using real top-attacker profit distribution

**Input:**
- `outputs/top_attackers_report.json` (from script 1)

**Output:**
- `outputs/monte_carlo_weighted.csv`

**Key Operations:**
- Load top 10 attackers by profit
- Normalize profits as probability weights
- Run 50k simulations with weighted attacker selection
- Sample trigger events (22% baseline)
- Sample cascades under BAM reduction (35% effective rate)
- Output per-attacker cascade statistics

**Run:**
```bash
python scripts/07_extend_monte_carlo_with_top_attackers.py
```

**Prerequisite:** Run script 1 first

**Dependencies:** `numpy`, `pandas`

---

### 8. `08_generate_final_report_pdf.py`
**Purpose:** Generate professional PDF report with top-5 attackers and key metrics

**Input:**
- `outputs/top_attackers_report.json` (from script 1)

**Output:**
- `outputs/Solana_PAMM_MEV_Final_Report.pdf`

**Key Operations:**
- Load top 5 attackers
- Create formatted table (Rank, Attacker, Profit SOL, Cascade %)
- Apply ReportLab styling (grey header, black borders, centered text)
- Generate PDF with title "PAMM MEV Contagion Final Report - Feb 2026"

**Run:**
```bash
python scripts/08_generate_final_report_pdf.py
```

**Prerequisites:** Run script 1 first

**Dependencies:** `reportlab`, `pandas`

---

### 9. `09_post_report_to_x.py`
**Purpose:** Generate X/Twitter post template for research publication

**Input:**
- None (template-only)

**Output:**
- Console output + copyable text

**Key Content:**
- Highlights: 80.1% cascade rate, top attacker >1,666 SOL
- Mentions key stakeholders: @helius_xyz, @jito_labs, @sandwichedme
- GitHub repo link

**Run:**
```bash
python scripts/09_post_report_to_x.py
```

**Optional Extension:** Integrate tweepy for automated posting (requires API keys)

**Dependencies:** None (pure Python)

---

## Execution Order (Recommended)

```
1. 01_top_attackers_extractor.py          ← Foundation
2. 03_update_contagion_report_with_attackers.py  ← Enrich report
3. 02_fetch_sandwiched_me_top.py          ← External validation
4. 04_validator_winrate_per_prop_amm.py   ← Validator analysis
5. 05_oracle_latency_comparison.py        ← Network performance
6. 06_test_twap_bam_protection.py         ← Mitigation testing
7. 07_extend_monte_carlo_with_top_attackers.py ← Advanced sim
8. 08_generate_final_report_pdf.py        ← PDF report
9. 09_post_report_to_x.py                 ← Social media
```

---

## Dependencies by Script

| Script | Dependencies | Install Command |
|--------|--------------|-----------------|
| 1 | `pandas`, `pyarrow` | `pip install pandas pyarrow` |
| 2 | `requests`, `beautifulsoup4` | `pip install requests beautifulsoup4` |
| 3 | `pandas`, `pyarrow` | `pip install pandas pyarrow` |
| 4 | `pandas` | `pip install pandas` |
| 5 | `pandas` | `pip install pandas` |
| 6 | `numpy`, `pandas` | `pip install numpy pandas` |
| 7 | `numpy`, `pandas` | `pip install numpy pandas` |
| 8 | `reportlab`, `pandas` | `pip install reportlab pandas` |
| 9 | (none) | — |

**One-liner install all:**
```bash
pip install pandas pyarrow requests beautifulsoup4 numpy reportlab
```

---

## Configuration Points

### Script 1: Data Path
```python
PARQUET_PATH = 'data/pamm_clean_final.parquet'  # Change if needed
OUTPUT_JSON = 'outputs/top_attackers_report.json'
```

### Script 5: Oracle File Paths
```python
files = ['data/oracle_bisonfi.csv', 'data/oracle_humidifi.csv', 'data/oracle_raydium.csv']
# Update based on your actual file locations
```

### Script 6: Monte Carlo Parameters
```python
n_sims=10000           # Number of simulations
base_cascade=0.801     # Historical cascade rate
twap_reduction=0.85    # TWAP effectiveness
bam_reduction=0.65     # BAM visibility reduction
```

### Script 7: Attack Trigger Rate
```python
trigger = np.random.rand() < 0.22  # 22% attack rate (from your report)
```

---

## Output Files Created

```
outputs/
├── top_attackers_report.json                    (script 1)
├── sandwiched_me_top_30d.json                  (script 2)
├── validator_winrate_per_prop_amm.csv          (script 4)
├── oracle_latency_comparison.csv               (script 5)
├── twap_bam_simulation.csv                     (script 6)
├── monte_carlo_weighted.csv                    (script 7)
├── Solana_PAMM_MEV_Final_Report.pdf            (script 8)
```

---

## Running All Scripts (Batch)

```bash
#!/bin/bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools

python scripts/01_top_attackers_extractor.py
python scripts/03_update_contagion_report_with_attackers.py
python scripts/02_fetch_sandwiched_me_top.py
python scripts/04_validator_winrate_per_prop_amm.py
python scripts/05_oracle_latency_comparison.py
python scripts/06_test_twap_bam_protection.py
python scripts/07_extend_monte_carlo_with_top_attackers.py
python scripts/08_generate_final_report_pdf.py
python scripts/09_post_report_to_x.py

echo "✅ All scripts completed!"
```

---

## Error Handling

| Error | Solution |
|-------|----------|
| `FileNotFoundError: pamm_clean_final.parquet` | Update `PARQUET_PATH` in script 1 or create the file |
| `requests.ConnectionError` (script 2) | Check internet connection; sandwiched.me may be down |
| `ModuleNotFoundError: No module named 'reportlab'` | `pip install reportlab` |
| `KeyError: 'validator_amm_pairs'` (script 4) | Ensure validator_contagion_graph.json has correct format |

---

## Next Steps

1. ✅ Verify all dependencies installed
2. ✅ Confirm data file paths are correct
3. ✅ Run scripts 1-3 sequentially (foundation layer)
4. ✅ Run scripts 4-5 (parallel validation)
5. ✅ Run scripts 6-7 (Monte Carlo analysis)
6. ✅ Generate report (script 8)
7. ✅ Post findings (script 9)

---

**Created:** 2026-02-24  
**Status:** Ready to execute
