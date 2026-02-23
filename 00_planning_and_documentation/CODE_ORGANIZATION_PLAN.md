# Code Organization & House Cleaning Plan

This document outlines the plan to organize, clean, and improve all scripts with solid code and visuals.

**⚠️ IMPORTANT: All code stays in `.ipynb` notebooks - NO `.py` file extraction**

---

## 📍 Quick Code Reference - All Notebook Locations

| **Analysis Type** | **Notebook Location** | **Key Cell(s)** | **Purpose** |
|-------------------|----------------------|-----------------|-------------|
| **MEV Case Studies** | `scripts/mev_analysis/docs/Hypothetical MEV Bot & Attack Case Studies.md` | N/A (Document) | Fact-check reference for all algorithms |
| **Data Cleaning** | `scripts/prop_amm_analysis/notebooks/pamm_df_cleaned_parquet.ipynb` | Cells 1-8 | Parse account_updates, trades, timing data |
| **DeezNode Filter** | `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb` | Cell 2 | Filter DeezNode bot/validator addresses |
| **Jito Tip Filter** | `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` | Cell 2 | Filter Jito tip addresses (8 addresses) |
| **Fat Sandwich** | `scripts/mev_analysis/notebooks/MEV Toxic MEV Stats & Validator Analysis #2.ipynb` | Cell 2 | ≥5 TRADEs, same attacker, victims between |
| **Classic Sandwich** | `scripts/mev_analysis/notebooks/MEV Toxic MEV Stats & Validator Analysis #2.ipynb` | Cell 2 | 3-4 TRADEs pattern |
| **Front-Running** | `scripts/mev_analysis/code/improved_front_running_detection.py` | Reference | Multi-factor analysis (>300ms threshold) |
| **Back-Running** | `scripts/mev_analysis/notebooks/MEV Toxic MEV Stats & Validator Analysis #2.ipynb` | Cell 4 | Oracle update → trade timing |
| **Cross-Slot Sandwich** | `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` | Cell 3+ | Multi-slot coordination |
| **Slippage Sandwich** | `scripts/mev_tasks_ipynb_with_readme/task3_slippage_sandwich.ipynb` | All cells | Slippage tolerance exploitation |
| **Token Pair Analysis** | `scripts/token_pair_pool_analysis/notebooks/deep_dive_pool_mev_analysis.ipynb` | Cells 2-5 | Single AMM token pair MEV analysis |
| **Validator Analysis** | `scripts/validator_analysis/notebooks/Top_Validator_AMM_MEV_Analysis.ipynb` | Cells 2-4 | Validator MEV metrics, clustering |
| **Aggregator Detection** | `scripts/machine_learning/notebooks/ml_mev_detection_test.ipynb` | Cell 2+ | Pool count method (8+ pools = aggregator) |
| **ML Classification** | `scripts/machine_learning/notebooks/ml_mev_detection_test.ipynb` | Cells 2-5 | Feature prep, training, evaluation |
| **Monte Carlo** | `scripts/monte_carlo/notebooks/monte_carlo_mev_risk_analysis.ipynb` | Cells 2-3 | Risk scenario simulation |
| **Oracle Analysis** | `scripts/oracle_analysis/notebooks/oracle_trade_timing_analysis.ipynb` | All cells | Oracle burst detection, timing analysis |

---

## MEV Case Studies - Fact Check Reference

**Purpose**: These case studies serve as the foundational reference and fact-check for all MEV detection algorithms and analysis. They define the expected patterns and behaviors that our detection methods should identify.

**📍 Source Document**: `scripts/mev_analysis/docs/Hypothetical MEV Bot & Attack Case Studies.md`

### Case Study Overview

The case studies document provides **hypothetical yet realistic** MEV attack scenarios based on real-world Solana MEV patterns observed in 2024–2025. These serve as reference models for what to look for in the data.

### Key Case Studies:

1. **Case Study #1: B91 Sandwicher Bot - Generalized Fat Sandwich**
   - Pattern: 4-10+ TRADEs per slot
   - Multiple victims wrapped by attacker
   - Detection criteria: ≥5 TRADEs, same attacker with ≥2 transactions, victims in between

2. **Case Study #2: Late-Slot Front-Runner**
   - Pattern: Trades placed late in slot (>300ms delay)
   - Exploits slippage from pending transactions
   - Detection: `us_since_first_shred > 300,000`

3. **Case Study #3: DeezNode Bot - Back-Running Pattern**
   - Pattern: Trades immediately after oracle price updates
   - Exploits new price before market adjusts
   - Detection: Oracle update → Trade within time window

4. **Case Study #4: 2Fast Bot - Cross-Slot Sandwich**
   - Pattern: Front-run in slot N, back-run in slot N+M
   - Multi-slot coordination
   - Detection: Attacker trades span multiple slots

5. **Case Study #5: Classic Sandwich (3-4 TRADEs)**
   - Pattern: Traditional single-victim sandwich
   - 3-4 TRADEs per slot
   - Detection: 3-4 TRADEs, same attacker, victim in between

### Usage in Analysis:

- **Algorithm Validation**: All MEV detection algorithms should align with these case study patterns
- **False Positive Filtering**: Patterns that don't match case studies should be flagged for review
- **Documentation Reference**: All algorithm documentation should reference relevant case studies
- **Testing Baseline**: Case studies provide expected outcomes for algorithm testing

**Implementation**: 
- Reference document: `docs/methodology/mev_case_studies.md` (extracted from source)
- All detection functions should include case study references in docstrings
- Notebooks should include case study examples in markdown cells

---

## Filtering Criteria - DeezNode & Jito Tips

**Purpose**: Filter out legitimate aggregator activity and known bot patterns that are not true MEV attacks.

### 1. DeezNode Filter

**Purpose**: Filter out transactions involving DeezNode bot/validator addresses.

**DeezNode Addresses**:
- **Bot Address**: `vpeNALD89BZ4KxNUFjdLmFXBCwtyqBDQ85ouNoax38b`
- **Validator Address**: `HM5H6FAYWEMcm9PCXFbbiUFfFVLTN9UGyAqmMQjdMRA`

**📍 Code Location**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb` - **Cell 2**

**Filtering Logic** (from notebook):
```python
# DeezNode addresses
deeznode_bot = 'vpeNALD89BZ4KxNUFjdLmFXBCwtyqBDQ85ouNoax38b'
deeznode_validator = 'HM5H6FAYWEMcm9PCXFbbiUFfFVLTN9UGy9AqmMQjdMRA'

# Extract addresses from account_updates
def extract_addresses(row):
    # ... (see notebook for full implementation)
    return addresses

# Check signer, validator, and parsed_accounts
signer_matches = df['signer'].isin([deeznode_bot, deeznode_validator])
validator_matches = df['validator'].isin([deeznode_bot, deeznode_validator])
parsed_matches = df['parsed_accounts'].apply(lambda x: any(addr in x for addr in [deeznode_bot, deeznode_validator]))

# Filter out DeezNode
deeznode_filter = signer_matches | validator_matches | parsed_matches
filtered_df = df[~deeznode_filter]
```

**Quick Reference**:
- **Notebook**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb`
- **Cell 2**: DeezNode address extraction and filtering
- **Output**: Filtered dataset with DeezNode transactions removed

**Alternative Implementation** (if needed as function):
```python
def filter_deeznode(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out transactions involving DeezNode addresses.
    
    Checks:
    - signer column
    - validator column  
    - parsed_accounts (extracted from account_updates)
    """
    deeznode_addresses = [
        'vpeNALD89BZ4KxNUFjdLmFXBCwtyqBDQ85ouNoax38b',  # Bot address
        'HM5H6FAYWEMcm9PCXFbbiUFfFVLTN9UGyAqmMQjdMRA'   # Validator address
    ]
    
    # Check signer
    deeznode_filter = trades_df['signer'].isin(deeznode_addresses)
    
    # Check validator
    deeznode_filter = deeznode_filter | trades_df['validator'].isin(deeznode_addresses)
    
    # Check parsed accounts
    if 'parsed_accounts' in trades_df.columns:
        deeznode_filter = deeznode_filter | trades_df['parsed_accounts'].apply(
            lambda x: any(addr in x for addr in deeznode_addresses) if isinstance(x, list) else False
        )
    
    # Return filtered dataframe (exclude DeezNode)
    return trades_df[~deeznode_filter]
```

**📍 Notebook Source**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb`
- **Cell 2**: DeezNode address filtering code
- **Cell 3+**: MEV detection after filtering

**Output**: 
- Filtered dataset with DeezNode transactions removed
- Statistics: Count of filtered transactions, percentage removed

---

### 2. Jito Tip Address Filter

**Purpose**: Filter out transactions involving Jito tip addresses (legitimate bundling, not MEV).

**Jito Tip Addresses** (8 known addresses):
```python
JITO_TIP_ADDRESSES = [
    '96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5',
    'HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe',
    'Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY',
    'ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49',
    'DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh',
    'ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt',
    'DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL',
    '3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT'
]
```

**📍 Code Location**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` - **Cell 2**

**Filtering Logic** (from notebook):
```python
# Jito tip addresses (8 known addresses)
jito_tips = [
    '96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5',
    'HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe',
    'Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY',
    'ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49',
    'DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh',
    'ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt',
    'DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL',
    '3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT'
]

# Extract addresses from account_updates (same function as task1)
df['parsed_accounts'] = df['account_updates'].apply(extract_addresses)

# Build filter conditions
tip_filter = df['parsed_accounts'].apply(lambda x: any(t in x for t in jito_tips))
tip_filter = tip_filter | df['signer'].isin(jito_tips)
tip_filter = tip_filter | df['validator'].isin(jito_tips)

# Filter out Jito tips
filtered_df = df[~tip_filter]
```

**Quick Reference**:
- **Notebook**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb`
- **Cell 2**: Jito tip address filtering code
- **Output**: Filtered dataset with Jito tip transactions removed

**Alternative Implementation** (if needed as function):
```python
def filter_jito_tips(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out transactions involving Jito tip addresses.
    
    Jito tips are payments to validators for transaction bundling.
    These are legitimate aggregator activities, not MEV attacks.
    
    Checks:
    - signer column
    - validator column
    - parsed_accounts (extracted from account_updates)
    """
    jito_tip_addresses = [
        '96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5',
        'HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe',
        'Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY',
        'ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49',
        'DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh',
        'ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt',
        'DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL',
        '3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT'
    ]
    
    # Check signer
    jito_filter = trades_df['signer'].isin(jito_tip_addresses)
    
    # Check validator
    jito_filter = jito_filter | trades_df['validator'].isin(jito_tip_addresses)
    
    # Check parsed accounts
    if 'parsed_accounts' in trades_df.columns:
        jito_filter = jito_filter | trades_df['parsed_accounts'].apply(
            lambda x: any(addr in x for addr in jito_tip_addresses) if isinstance(x, list) else False
        )
    
    # Return filtered dataframe (exclude Jito tips)
    return trades_df[~jito_filter]
```

**📍 Notebook Source**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb`
- **Cell 2**: Jito tip address filtering code
- **Cell 3+**: Sandwich detection near tips

**Output**:
- Filtered dataset with Jito tip transactions removed
- Statistics: Count of filtered transactions, percentage removed

---

### Combined Filtering Module

**📍 Notebook Location**: Create new notebook `notebooks/01_data_cleaning.ipynb` or add to existing cleaning notebook

**Quick Reference**:
- **DeezNode Filter**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb` - Cell 2
- **Jito Tip Filter**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` - Cell 2
- **Data Cleaning**: `scripts/prop_amm_analysis/notebooks/pamm_df_cleaned_parquet.ipynb` - Cells 1-8

**Implementation** (in notebook):
```python
# In notebook cell - combine both filters
def apply_all_filters(trades_df: pd.DataFrame, 
                     filter_deeznode: bool = True,
                     filter_jito_tips: bool = True) -> pd.DataFrame:
    """
    Apply all transaction filters to remove non-MEV activity.
    
    Parameters:
    -----------
    trades_df : pd.DataFrame
        Input trades dataframe
    filter_deeznode : bool
        Whether to filter DeezNode transactions (default: True)
    filter_jito_tips : bool
        Whether to filter Jito tip transactions (default: True)
    
    Returns:
    --------
    pd.DataFrame with filtered transactions
    """
    filtered_df = trades_df.copy()
    
    original_count = len(filtered_df)
    filter_stats = {}
    
    if filter_deeznode:
        before = len(filtered_df)
        filtered_df = filter_deeznode(filtered_df)
        after = len(filtered_df)
        filter_stats['deeznode'] = {
            'removed': before - after,
            'percentage': ((before - after) / before * 100) if before > 0 else 0
        }
    
    if filter_jito_tips:
        before = len(filtered_df)
        filtered_df = filter_jito_tips(filtered_df)
        after = len(filtered_df)
        filter_stats['jito_tips'] = {
            'removed': before - after,
            'percentage': ((before - after) / before * 100) if before > 0 else 0
        }
    
    filter_stats['total_removed'] = original_count - len(filtered_df)
    filter_stats['total_percentage'] = ((original_count - len(filtered_df)) / original_count * 100) if original_count > 0 else 0
    
    return filtered_df, filter_stats
```

**Integration**:
- All MEV detection notebooks should use filtered data
- Filtering should be applied in data cleaning phase
- Filter statistics should be logged and reported

**📍 Notebooks**:
- **Data Cleaning**: `scripts/prop_amm_analysis/notebooks/pamm_df_cleaned_parquet.ipynb`
- **DeezNode Filter**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb`
- **Jito Tip Filter**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb`

**Outputs**:
- `outputs/csv/filters/filter_statistics.csv` - Filtering statistics
- `outputs/csv/filters/deeznode_filtered.csv` - DeezNode transactions (for analysis)
- `outputs/csv/filters/jito_tips_filtered.csv` - Jito tip transactions (for analysis)

---

## Current Structure Analysis

### Issues Identified:
1. **Scattered notebooks** across multiple directories
2. **Duplicate code** in different locations
3. **Inconsistent naming** conventions
4. **Missing documentation** for some scripts
5. **Output files** not consistently organized
6. **Visualizations** scattered across notebooks

---

## Proposed Clean Structure

```
solana-pamm-analysis/
├── README.md                          # Main project README
├── requirements.txt                    # All dependencies
├── 
├── data/                              # Data files (gitignored)
│   ├── raw/                           # Original data
│   ├── cleaned/                       # Cleaned/processed data
│   └── README.md                      # Data documentation
│
├── notebooks/                         # All analysis notebooks (NO .py files)
│   ├── 01_data_cleaning.ipynb        # Data cleaning + filtering
│   ├── 02_mev_detection.ipynb        # All MEV algorithms
│   ├── 03_oracle_analysis.ipynb
│   ├── 04_validator_analysis.ipynb   # Enhanced validator metrics
│   ├── 05_token_pair_analysis.ipynb  # Single AMM token pair analysis
│   ├── 06_pool_analysis.ipynb
│   ├── 07_ml_classification.ipynb
│   ├── 08_monte_carlo_risk.ipynb
│   ├── 09_aggregator_mev_analysis.ipynb  # Combined aggregator + MEV
│   └── 10_comprehensive_report.ipynb
│
├── scripts/                           # Existing scripts (reference only)
│   ├── mev_tasks_ipynb_with_readme/  # Filtering notebooks
│   │   ├── task1_deeznode_filter.ipynb      # 📍 DeezNode filter code
│   │   ├── task2_jito_tip_sandwich.ipynb     # 📍 Jito tip filter code
│   │   └── task3_slippage_sandwich.ipynb
│   ├── mev_analysis/
│   │   ├── notebooks/
│   │   │   └── MEV Toxic MEV Stats & Validator Analysis #2.ipynb  # 📍 Main MEV detection
│   │   └── docs/
│   │       └── Hypothetical MEV Bot & Attack Case Studies.md  # 📍 Case studies
│   ├── prop_amm_analysis/
│   │   └── notebooks/
│   │       └── pamm_df_cleaned_parquet.ipynb  # 📍 Data cleaning code
│   ├── token_pair_pool_analysis/
│   │   └── notebooks/
│   │       └── deep_dive_pool_mev_analysis.ipynb  # 📍 Token pair analysis
│   ├── validator_analysis/
│   │   └── notebooks/
│   │       └── Top_Validator_AMM_MEV_Analysis.ipynb  # 📍 Validator analysis
│   └── ... (other existing scripts)
│
├── notebooks/                         # Jupyter notebooks (execution)
│   ├── 01_data_cleaning.ipynb
│   ├── 02_mev_detection.ipynb         # All MEV algorithms
│   ├── 03_oracle_analysis.ipynb
│   ├── 04_validator_analysis.ipynb    # Enhanced validator metrics
│   ├── 05_token_pair_analysis.ipynb   # Single AMM token pair analysis
│   ├── 06_pool_analysis.ipynb
│   ├── 07_ml_classification.ipynb
│   ├── 08_monte_carlo_risk.ipynb
│   ├── 09_aggregator_mev_analysis.ipynb  # Combined aggregator + MEV
│   └── 10_comprehensive_report.ipynb
│
├── scripts/                           # Standalone scripts
│   ├── data_processing/
│   │   ├── clean_data.py
│   │   └── validate_data.py
│   ├── analysis/
│   │   ├── run_mev_detection.py
│   │   ├── run_oracle_analysis.py
│   │   ├── run_validator_analysis.py
│   │   ├── run_pool_analysis.py
│   │   ├── run_ml_classification.py
│   │   └── run_monte_carlo.py
│   └── utils/
│       ├── extract_code_from_notebooks.py
│       └── generate_report.py
│
├── outputs/                           # All analysis outputs
│   ├── csv/
│   │   ├── filters/                   # Filtering results
│   │   │   ├── filter_statistics.csv
│   │   │   ├── deeznode_filtered.csv
│   │   │   └── jito_tips_filtered.csv
│   │   ├── mev/                       # All MEV algorithm outputs
│   │   ├── oracle/
│   │   ├── validator/                 # Enhanced validator metrics
│   │   ├── pool/                      # Pool & token pair analysis
│   │   ├── token_pair/                # Single AMM token pair results
│   │   ├── aggregator/                # Aggregator classification
│   │   ├── ml/
│   │   └── monte_carlo/
│   ├── images/
│   │   ├── mev/                       # MEV algorithm visualizations
│   │   ├── oracle/
│   │   ├── validator/                 # Validator clustering & heatmaps
│   │   ├── pool/                      # Pool & token pair visualizations
│   │   ├── token_pair/                # Token pair MEV timelines
│   │   ├── aggregator/                # Aggregator routing patterns
│   │   ├── ml/
│   │   └── monte_carlo/
│   └── reports/
│       ├── pure_report.md
│       └── report_with_code.md
│
├── docs/                              # Documentation
│   ├── methodology/
│   │   ├── mev_case_studies.md        # MEV case studies (fact check reference)
│   │   ├── data_cleaning.md
│   │   ├── mev_detection.md
│   │   ├── filtering_criteria.md      # DeezNode & Jito tip filtering
│   │   ├── oracle_analysis.md
│   │   ├── validator_analysis.md
│   │   ├── pool_analysis.md
│   │   ├── ml_classification.md
│   │   └── monte_carlo.md
│   ├── api/                           # API documentation
│   └── guides/
│       ├── getting_started.md
│       └── report_writing_guide.md
│
└── tests/                             # Unit tests
    ├── test_data_cleaner.py
    ├── test_mev_detector.py
    ├── test_oracle_analyzer.py
    └── ...
```

---

## Migration Plan

### Phase 1: Core Module Extraction

**Goal**: Extract reusable code from notebooks into `src/` modules

1. **Data Cleaning** (Keep in Notebook - NO .py extraction)
   - **📍 Source**: `scripts/prop_amm_analysis/notebooks/pamm_df_cleaned_parquet.ipynb`
   - **Cell 1**: Original data loading
   - **Cell 2**: Missing value detection
   - **Cell 3**: Parse `account_updates` column → `parse_account_update()` logic
   - **Cell 4**: Parse `trades` column → `parse_trades()` logic
   - **Cell 5+**: Timing data cleaning → `clean_timing_data()` logic
   - **Reference**: Use this notebook as template for `notebooks/01_data_cleaning.ipynb`

1a. **Transaction Filters** (Keep in Notebooks - NO .py extraction)
   - **📍 DeezNode Filter**: `scripts/mev_tasks_ipynb_with_readme/task1_deeznode_filter.ipynb` - Cell 2
     - Code: DeezNode address extraction and filtering
     - Addresses: `vpeNALD89BZ4KxNUFjdLmFXBCwtyqBDQ85ouNoax38b` (bot), `HM5H6FAYWEMcm9PCXFbbiUFfFVLTN9UGy9AqmMQjdMRA` (validator)
   - **📍 Jito Tip Filter**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` - Cell 2
     - Code: Jito tip address filtering (8 known addresses)
     - Addresses: See notebook Cell 2 for full list
   - **Integration**: Add filtering cells to `notebooks/01_data_cleaning.ipynb`

2. **MEV Detection Algorithms** (Keep in Notebooks - NO .py extraction)
   - **📍 Main MEV Detection**: `scripts/mev_analysis/notebooks/MEV Toxic MEV Stats & Validator Analysis #2.ipynb`
     - **Cell 2**: Fat sandwich detection (≥5 TRADEs, same attacker, victims in between)
     - **Cell 2**: Classic sandwich detection (3-4 TRADEs pattern)
     - **Cell 4**: Back-running detection (oracle update → trade timing)
   - **📍 Improved Algorithms**: `scripts/mev_analysis/code/improved_fat_sandwich_detection.py` (reference for notebook)
   - **📍 Improved Front-Running**: `scripts/mev_analysis/code/improved_front_running_detection.py` (reference for notebook)
   - **📍 Cross-Slot Sandwich**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb` - Cell 3+
   - **📍 Slippage Sandwich**: `scripts/mev_tasks_ipynb_with_readme/task3_slippage_sandwich.ipynb`
   - **📍 Bot Diagnostic**: `scripts/mev_analysis/code/mev_bot_diagnostic_analysis.py` (reference for notebook)
   - **Reference**: Consolidate all algorithms into `notebooks/02_mev_detection.ipynb`

3. **Oracle Analyzer** (`src/oracle_analyzer.py`)
   - Extract from: `scripts/oracle_analysis/notebooks/oracle_trade_timing_analysis.ipynb`
   - Functions to extract:
     - `detect_oracle_bursts()`
     - `analyze_oracle_frequency()`
     - `identify_top_updaters()`

4. **Validator Analysis** (Keep in Notebook - NO .py extraction)
   - **📍 Source**: `scripts/validator_analysis/notebooks/Top_Validator_AMM_MEV_Analysis.ipynb`
   - **Cell 2+**: Validator MEV breakdown analysis
   - **Cell 3+**: Bot ratio calculations
   - **Cell 4+**: Validator clustering and heatmaps
   - **Reference Doc**: `scripts/validator_analysis/docs/TOP_VALIDATOR_AMM_MEV_ANALYSIS.md`
   - **Reference**: Use this notebook as template for `notebooks/04_validator_analysis.ipynb`

5. **Pool Analysis** (Keep in Notebook - NO .py extraction)
   - **📍 Source**: `scripts/token_pair_pool_analysis/notebooks/deep_dive_pool_mev_analysis.ipynb`
   - **Cell 2+**: Pool MEV analysis
   - **Cell 3+**: Token pair validation
   - **Cell 4+**: Pool density calculations

6. **Token Pair Analysis** (Keep in Notebook - NO .py extraction) - NEW
   - **📍 Source**: `scripts/token_pair_pool_analysis/notebooks/deep_dive_pool_mev_analysis.ipynb`
   - **Cell 2+**: Single AMM token pair MEV analysis
   - **Cell 3+**: Pool coordination detection
   - **Cell 4+**: ML training data generation
   - **Cell 5+**: Monte Carlo risk scenarios
   - **Reference Doc**: `scripts/token_pair_pool_analysis/docs/DEEP_DIVE_AND_FILTER_ANALYSIS_SUMMARY.md`
   - **Reference**: Use this notebook as template for `notebooks/05_token_pair_analysis.ipynb`

7. **Aggregator + MEV Classification** (Keep in Notebook - NO .py extraction) - NEW
   - **📍 Source**: `scripts/mev_analysis/code/create_comprehensive_mev_table.py` (reference)
   - **📍 Source**: `scripts/machine_learning/code/comprehensive_mev_attacker_verification.py` (reference)
   - **📍 ML Notebook**: `scripts/machine_learning/notebooks/ml_mev_detection_test.ipynb`
     - **Cell 2+**: Aggregator likelihood calculation (pool count method)
     - **Cell 3+**: Attacker classification logic
     - **Cell 4+**: Comprehensive MEV table generation
   - **Reference Doc**: `scripts/machine_learning/docs/update_aggregator_detection_and_ml.md`
   - **Reference**: Use ML notebook as template for `notebooks/09_aggregator_mev_analysis.ipynb`

8. **ML Classification** (Keep in Notebook - NO .py extraction)
   - **📍 Source**: `scripts/machine_learning/notebooks/ml_mev_detection_test.ipynb`
   - **Cell 2+**: Feature preparation
   - **Cell 3+**: Model training
   - **Cell 4+**: Model evaluation
   - **Cell 5+**: GMM clustering
   - **Reference**: Use this notebook as template for `notebooks/07_ml_classification.ipynb`

9. **Monte Carlo Risk Analysis** (Keep in Notebook - NO .py extraction)
   - **📍 Source**: `scripts/monte_carlo/notebooks/monte_carlo_mev_risk_analysis.ipynb`
   - **Cell 2+**: Risk scenario simulation
   - **Cell 3+**: Risk percentile calculations
   - **Reference**: Use this notebook as template for `notebooks/08_monte_carlo_risk.ipynb`

10. **Visualizations** (Keep in Notebooks - NO .py extraction)
   - **📍 MEV Visualizations**: `scripts/mev_analysis/notebooks/MEV Toxic MEV Stats & Validator Analysis #2.ipynb` - Visualization cells
   - **📍 Oracle Visualizations**: `scripts/oracle_analysis/notebooks/oracle_trade_timing_analysis.ipynb` - Visualization cells
   - **📍 Validator Visualizations**: `scripts/validator_analysis/notebooks/Top_Validator_AMM_MEV_Analysis.ipynb` - Heatmap/clustering cells
   - **📍 Token Pair Visualizations**: `scripts/token_pair_pool_analysis/notebooks/deep_dive_pool_mev_analysis.ipynb` - Timeline/activity cells
   - **Reference**: Consolidate visualization code into respective analysis notebooks

---

### Phase 2: Notebook Refactoring

**Goal**: Refactor notebooks to use extracted modules

1. **Create clean execution notebooks** in `notebooks/`
2. **Remove duplicate code** - use imports from `src/`
3. **Standardize cell structure**:
   - Cell 1: Imports and setup
   - Cell 2: Load data
   - Cell 3: Run analysis (using src modules)
   - Cell 4: Generate visualizations
   - Cell 5: Save outputs
   - Cell 6: Summary statistics

4. **Add markdown cells** explaining each step

---

### Phase 3: Output Organization

**Goal**: Organize all outputs consistently

1. **Move all CSV outputs** to `outputs/csv/` with subdirectories
2. **Move all images** to `outputs/images/` with subdirectories
3. **Create output index** documenting what each file contains
4. **Standardize naming**:
   - `{analysis_type}_{metric}_{date}.csv`
   - `{analysis_type}_{chart_type}_{date}.png`

---

### Phase 4: Visualization Improvements

**Goal**: Create high-quality, consistent visualizations

1. **Standardize style**:
   - Color palette
   - Font sizes
   - Figure sizes
   - Layout templates

2. **Create visualization templates** in `src/visualizer.py`:
   - `plot_mev_summary()` - Overall MEV activity
   - `plot_attack_types()` - Attack type breakdown
   - `plot_oracle_timing()` - Oracle-trade timing
   - `plot_validator_heatmap()` - Validator clustering
   - `plot_risk_distributions()` - Monte Carlo results
   - `plot_ml_performance()` - ML metrics

3. **Generate all visualizations** programmatically
4. **Save high-resolution** versions for reports

---

### Phase 5: Documentation

**Goal**: Comprehensive documentation

1. **API Documentation**:
   - Docstrings for all functions
   - Type hints
   - Usage examples

2. **Methodology Documentation**:
   - Detailed explanations in `docs/methodology/`
   - Code references
   - Parameter explanations
   - All MEV algorithms documented with examples
   - Token pair analysis methodology
   - Aggregator detection methodology
   - Validator analysis methodology

3. **User Guides**:
   - Getting started guide
   - Report writing guide
   - Troubleshooting guide

---

## Comprehensive Analysis Modules

### Token Pair MEV Detection Analysis for Single AMM

**Purpose**: Deep-dive analysis of MEV patterns for specific token pairs within a single AMM (e.g., PUMP/WSOL on BisonFi).

**Module**: `src/token_pair_analyzer.py`

**Key Functions**:
- `analyze_token_pair_mev(token_pair: str, amm: str, trades_df: pd.DataFrame) -> Dict`
  - Analyzes all MEV attacks for a specific token pair
  - Identifies adjacent pools handling the same pair
  - Calculates pool coordination patterns
  - Returns comprehensive statistics

- `detect_pool_coordination(pool_trades: pd.DataFrame) -> pd.DataFrame`
  - Detects coordinated attacks across adjacent pools
  - Identifies cross-pool sandwich patterns
  - Analyzes pool routing strategies

- `generate_ml_training_data(token_pair: str, amm: str) -> pd.DataFrame`
  - Creates labeled dataset for ML training
  - Includes real swap scenarios with risk metrics
  - Features: latency, oracle timing, validator, bot_ratio, sandwich_risk

- `calculate_monte_carlo_scenarios(token_pair: str, real_swaps: pd.DataFrame) -> pd.DataFrame`
  - Generates risk simulation scenarios for real swaps
  - Calculates expected loss, success rate, sandwich risk
  - Output: `real_swap_mev_risk_{TOKEN_PAIR}.csv`

**Notebook**: `notebooks/05_token_pair_analysis.ipynb`

**Outputs**:
- `outputs/csv/pool/token_pair_{TOKEN_PAIR}_mev.csv` - MEV activity per token pair
- `outputs/csv/pool/token_pair_{TOKEN_PAIR}_ml_training.csv` - ML training dataset
- `outputs/csv/pool/token_pair_{TOKEN_PAIR}_monte_carlo.csv` - Risk scenarios
- `outputs/images/pool/token_pair_{TOKEN_PAIR}_frontrun_timing.png` - Front-run visualization
- `outputs/images/pool/token_pair_{TOKEN_PAIR}_backrun_timing.png` - Back-run visualization
- `outputs/images/pool/token_pair_{TOKEN_PAIR}_mev_timeline.png` - MEV timeline

**Analysis Components**:
1. **Pool Identification**: Find all pools handling the token pair
2. **MEV Mechanism Analysis**: Front-run, back-run, sandwich patterns
3. **ML Training Data**: Create labeled dataset with real swap outcomes
4. **Monte Carlo Scenarios**: Generate risk simulation scenarios
5. **Visualizations**: Show exactly how MEV works for the token pair

**Source Files**:
- Extract from: `scripts/token_pair_pool_analysis/notebooks/deep_dive_pool_mev_analysis.ipynb`
- Extract from: `scripts/token_pair_pool_analysis/docs/DEEP_DIVE_AND_FILTER_ANALYSIS_SUMMARY.md`

---

### Validator Analysis - Comprehensive MEV Metrics

**Purpose**: Complete validator-level analysis including MEV patterns, bot ratios, clustering, and aggregator detection.

**Module**: `src/validator_analyzer.py` (Enhanced)

**Key Functions**:
- `analyze_validator_mev(validator: str, trades_df: pd.DataFrame) -> Dict`
  - Complete MEV breakdown per validator
  - Fat sandwich, classic sandwich, front-running, back-running counts
  - Bot ratio calculation
  - Total trade count and MEV percentage

- `calculate_bot_ratios(validator: str, trades_df: pd.DataFrame) -> Dict`
  - Bot count vs total trades
  - Bot ratio percentage
  - Unique attacker count
  - MEV bot vs aggregator breakdown

- `cluster_validators(validators_df: pd.DataFrame) -> pd.DataFrame`
  - Clustering based on MEV patterns
  - Validator similarity analysis
  - Heatmap generation for validator-AMM relationships

- `analyze_validator_aggregator_patterns(validator: str, trades_df: pd.DataFrame) -> Dict`
  - Aggregator routing patterns per validator
  - Pool count analysis (8+ pools = aggregator)
  - Distinguishes MEV bots from aggregator bundles

- `generate_validator_comprehensive_report(validator: str) -> Dict`
  - All metrics combined:
    - Trade count, bot count, bot ratio
    - MEV breakdown (fat_sandwich, sandwich, front_running, back_running)
    - Aggregator likelihood
    - Top attackers per validator
    - AMM exposure analysis

**Notebook**: `notebooks/04_validator_analysis.ipynb` (Enhanced)

**Outputs**:
- `outputs/csv/validator/mev_trades_bots_per_validator.csv` - Per-validator MEV stats
- `outputs/csv/validator/per_pamm_all_mev_with_validator.csv` - Validator-AMM MEV matrix
- `outputs/csv/validator/per_pamm_top10_mev_with_validator.csv` - Top 10 per AMM
- `outputs/images/validator/validator_cluster_analysis.png` - Clustering visualization
- `outputs/images/validator/cluster_heatmap_validator_amm.png` - Validator-AMM heatmap

**Analysis Metrics**:
1. **MEV Activity**: Total attacks, attack types, profit/loss
2. **Bot Metrics**: Bot count, bot ratio, unique attackers
3. **Aggregator Detection**: Pool count analysis, aggregator likelihood
4. **Clustering**: Validator similarity based on MEV patterns
5. **AMM Exposure**: Which AMMs are most exposed per validator

**Source Files**:
- Extract from: `scripts/validator_analysis/notebooks/Top_Validator_AMM_MEV_Analysis.ipynb`
- Extract from: `scripts/validator_analysis/docs/TOP_VALIDATOR_AMM_MEV_ANALYSIS.md`

---

### Combined Aggregator + MEV Analysis

**Purpose**: Advanced analysis that distinguishes MEV bots from aggregators (Jupiter, DFlow, etc.) and provides comprehensive classification.

**Module**: `src/aggregator_mev_classifier.py`

**Key Functions**:
- `calculate_aggregator_likelihood(attacker: str, trades_df: pd.DataFrame, per_pamm_df: pd.DataFrame) -> float`
  - Pool count method: 8+ unique pools = likely aggregator
  - Threshold-based scoring:
    - 8+ pools: 0.5 + (pools - 8) * 0.05 (max 1.0)
    - 5-7 pools: 0.3 + (pools - 5) * 0.067
    - 3-4 pools: 0.1 + (pools - 3) * 0.1
    - <3 pools: pools * 0.05
  - Returns likelihood score (0-1)

- `classify_attacker(aggregator_likelihood: float, mev_score: float, wash_trading_score: float, cluster_ratio: float) -> Tuple[str, str]`
  - Classification logic:
    1. **LIKELY AGGREGATOR**: aggregator_likelihood > 50%
    2. **LIKELY WASH TRADING**: wash_trading_score > 1.0
    3. **LIKELY MEV BOT**: mev_score > 30%, aggregator_likelihood < 50%, wash_trading_score < 1.0
    4. **POSSIBLE MEV**: mev_score 10-30%
    5. **REGULAR TRADE BOT**: mev_score < 10%
  - Returns (classification, confidence)

- `analyze_aggregator_routing_patterns(attacker: str, trades_df: pd.DataFrame) -> Dict`
  - Unique pool count analysis
  - Slot-level unique signer ratio
  - Routing pattern detection
  - Distinguishes Jupiter/DFlow from MEV bots

- `generate_comprehensive_mev_table(trades_df: pd.DataFrame) -> pd.DataFrame`
  - Combined MEV + Aggregator analysis
  - Columns include:
    - `attacker_signer`, `classification`, `confidence`
    - `total_attacks`, `fat_sandwich`, `sandwich`, `front_running`, `back_running`
    - `cost_sol`, `profit_sol`, `net_profit_sol`
    - `validator`, `total_validators`, `amm_trade`, `total_pools`
    - `mev_score`, `aggregator_likelihood`, `wash_trading_score`
    - `late_slot_ratio`, `oracle_backrun_ratio`, `high_bytes_ratio`, `cluster_ratio`
    - `total_trades`, `trades_per_hour`
  - Filters out aggregators, wash trading, regular bots

- `filter_mev_bots(comprehensive_df: pd.DataFrame) -> pd.DataFrame`
  - Removes: LIKELY AGGREGATOR, LIKELY WASH TRADING, REGULAR TRADE BOT, UNKNOWN
  - Keeps: LIKELY MEV BOT, POSSIBLE MEV
  - Returns clean MEV bot dataset

**Notebook**: `notebooks/09_aggregator_mev_analysis.ipynb`

**Outputs**:
- `outputs/csv/mev/comprehensive_mev_all_with_pnl.csv` - All attackers with classification
- `outputs/csv/mev/mev_bots_filtered.csv` - Filtered MEV bots only
- `outputs/csv/mev/aggregators_filtered.csv` - Aggregators identified
- `outputs/images/mev/mev_vs_aggregator_classification.png` - Classification visualization
- `outputs/images/mev/aggregator_routing_patterns.png` - Aggregator routing analysis

**Analysis Components**:
1. **Aggregator Detection**: Pool count method (8+ pools = aggregator)
2. **MEV Classification**: Multi-factor scoring (MEV score, aggregator likelihood, wash trading)
3. **Filtering**: Separate MEV bots from aggregators and wash trading
4. **Routing Analysis**: Understand aggregator vs MEV bot patterns
5. **Comprehensive Metrics**: All relevant analysis combined

**Source Files**:
- Extract from: `scripts/mev_analysis/code/create_comprehensive_mev_table.py`
- Extract from: `scripts/machine_learning/code/comprehensive_mev_attacker_verification.py`
- Extract from: `scripts/machine_learning/docs/update_aggregator_detection_and_ml.md`

---

### All MEV Detection Algorithms

**Purpose**: Complete documentation and implementation of all MEV detection algorithms used in the analysis.

**Module**: `src/mev_detector/` (Enhanced with all algorithms)

#### 1. Fat Sandwich Detection (`src/mev_detector/fat_sandwich.py`)

**Algorithm**: Rolling Window Multi-Slot Analysis

**Detection Criteria**:
- Rolling window: 5 seconds or N slots (configurable)
- Minimum trade volume threshold: `bytes_changed_trade > threshold`
- Same attacker with trades at beginning and end of window
- Multiple victims in between (min 2 victims)
- Pattern: A-B-C-...-A (attacker wraps victims)
- Minimum total trades: 5 (configurable)
- Minimum attacker trades: 2

**Functions**:
- `detect_fat_sandwich_rolling_window(trades_df: pd.DataFrame, window_size_seconds: float = 5.0, min_trade_volume: float = 30.0, min_total_trades: int = 5, min_attacker_trades: int = 2, min_victims: int = 2) -> pd.DataFrame`
  - Multi-slot fat sandwich detection
  - Time series analysis across slots
  - Returns detected fat sandwiches with metadata

- `detect_fat_sandwich_single_slot(trades_df: pd.DataFrame, min_trades: int = 5) -> pd.DataFrame`
  - Single-slot fat sandwich (≥5 TRADEs per slot)
  - Same attacker with ≥2 transactions
  - Victims between attacker trades

**Source**: `scripts/mev_analysis/code/improved_fat_sandwich_detection.py`

---

#### 2. Classic Sandwich Detection (`src/mev_detector/classic_sandwich.py`)

**Algorithm**: Single-Slot 3-4 TRADE Pattern

**Detection Criteria**:
- 3-4 TRADE events in the same slot
- Same attacker (signer) with ≥2 transactions in that slot
- At least one victim between front-run and back-run
- Pattern: Attacker TX 1 (front-run) → Victim TX → Attacker TX 2 (back-run)

**Functions**:
- `detect_classic_sandwich(trades_df: pd.DataFrame, min_trades: int = 3, max_trades: int = 4) -> pd.DataFrame`
  - Detects traditional single-victim sandwich attacks
  - Returns sandwich events with attacker and victim info

**Source**: `scripts/validator_analysis/docs/TOP_VALIDATOR_AMM_MEV_ANALYSIS.md`

---

#### 3. Front-Running Detection (`src/mev_detector/front_running.py`)

**Algorithm**: Multi-Factor Analysis (Improved)

**Detection Criteria**:
- **Threshold-based**: `us_since_first_shred > 300,000` (300ms delay)
- **Percentile-based**: Relative to slot/pool/validator patterns
- **Relative timing**: Attacker timing vs victim timing
- **Statistical methods**: Z-scores, anomaly detection
- **Pool/validator-specific baselines**: Context-aware thresholds
- **Multi-factor validation**: Timing + volume + token pair + pattern

**Functions**:
- `detect_front_running_threshold(trades_df: pd.DataFrame, latency_threshold_us: int = 300000) -> pd.DataFrame`
  - Simple threshold-based detection (>300ms)

- `detect_front_running_improved(trades_df: pd.DataFrame, percentile_threshold: float = 0.95) -> pd.DataFrame`
  - Percentile-based detection (top 5% latency)
  - Pool/validator-specific baselines
  - Statistical anomaly detection

- `calculate_slot_statistics(trades_df: pd.DataFrame) -> pd.DataFrame`
  - Slot-level statistics for timing analysis
  - Min, max, mean, std of latency per slot

- `detect_front_running_relative(trades_df: pd.DataFrame, attacker: str, victim: str) -> pd.DataFrame`
  - Relative timing analysis
  - Attacker timing vs victim timing comparison

**Source**: `scripts/mev_analysis/code/improved_front_running_detection.py`

---

#### 4. Back-Running Detection (`src/mev_detector/back_running.py`)

**Algorithm**: Oracle Price Update Exploitation

**Detection Criteria**:
- Trade immediately after oracle price update
- Exploits new price before market adjusts
- Pattern: Oracle update → Attacker trade (within time window)
- Time window: Configurable (default: 200ms after oracle update)

**Functions**:
- `detect_back_running(trades_df: pd.DataFrame, oracle_updates: pd.DataFrame, time_window_ms: int = 200) -> pd.DataFrame`
  - Detects back-running after oracle updates
  - Matches trades to oracle updates within time window
  - Returns back-running events

- `calculate_oracle_backrun_ratio(attacker: str, trades_df: pd.DataFrame, oracle_updates: pd.DataFrame) -> float`
  - Calculates ratio of trades that are back-runs
  - Returns percentage (0-1)

**Source**: `scripts/validator_analysis/docs/TOP_VALIDATOR_AMM_MEV_ANALYSIS.md`

---

#### 5. Cross-Slot Sandwich Detection (`src/mev_detector/cross_slot_sandwich.py`)

**Algorithm**: Multi-Slot Coordination (2Fast Bot Pattern)

**Detection Criteria**:
- Attacker trades span multiple slots
- Front-run in slot N, back-run in slot N+M
- Victim trades in between slots
- Pattern: Slot N (front-run) → Slot N+1...N+M (victims) → Slot N+M+1 (back-run)

**Functions**:
- `detect_cross_slot_sandwich(trades_df: pd.DataFrame, max_slot_span: int = 10) -> pd.DataFrame`
  - Detects sandwiches across multiple slots
  - Configurable maximum slot span
  - Returns cross-slot sandwich events

**Source**: `scripts/mev_tasks_ipynb_with_readme/task2_jito_tip_sandwich.ipynb`

---

#### 6. Slippage Sandwich Detection (`src/mev_detector/slippage_sandwich.py`)

**Algorithm**: Slippage-Based Exploitation

**Detection Criteria**:
- Exploits slippage tolerance of victim trades
- Attacker maximizes profit within victim's slippage bounds
- Pattern: Front-run → Victim (with slippage) → Back-run

**Functions**:
- `detect_slippage_sandwich(trades_df: pd.DataFrame, slippage_threshold: float = 0.01) -> pd.DataFrame`
  - Detects sandwiches exploiting slippage
  - Analyzes price impact within slippage tolerance
  - Returns slippage sandwich events

**Source**: `scripts/mev_tasks_ipynb_with_readme/task3_slippage_sandwich.ipynb`

---

#### 7. MEV Bot Diagnostic Analysis (`src/mev_detector/bot_diagnostic.py`)

**Algorithm**: Comprehensive Bot Scoring

**Functions**:
- `calculate_mev_score(attacker: str, trades_df: pd.DataFrame) -> float`
  - Multi-factor MEV score calculation
  - Factors: attack frequency, profit, pattern consistency
  - Returns score (0-1)

- `diagnose_mev_bot(attacker: str, trades_df: pd.DataFrame) -> Dict`
  - Comprehensive bot diagnosis
  - Returns: classification, confidence, scores, patterns

**Source**: `scripts/mev_analysis/code/mev_bot_diagnostic_analysis.py`

---

**Notebook**: `notebooks/02_mev_detection.ipynb` (Enhanced with all algorithms)

**Outputs**:
- `outputs/csv/mev/fat_sandwich_detected.csv` - Fat sandwich events
- `outputs/csv/mev/classic_sandwich_detected.csv` - Classic sandwich events
- `outputs/csv/mev/front_running_detected.csv` - Front-running events
- `outputs/csv/mev/back_running_detected.csv` - Back-running events
- `outputs/csv/mev/cross_slot_sandwich_detected.csv` - Cross-slot sandwiches
- `outputs/csv/mev/slippage_sandwich_detected.csv` - Slippage sandwiches
- `outputs/csv/mev/failed_sandwich_attempts.csv` - Failed attempts
- `outputs/images/mev/mev_algorithm_comparison.png` - Algorithm performance comparison

**Algorithm Documentation**:
- All algorithms documented in `docs/methodology/mev_detection.md`
- Parameter explanations and tuning guides
- Performance metrics and accuracy measurements

---

## Code Quality Standards

### Python Code:
- **Type hints** for all functions
- **Docstrings** (Google style)
- **Error handling** with try/except
- **Logging** instead of print statements
- **Constants** defined at module level
- **Functions** should be < 50 lines
- **Classes** for complex logic

### Notebooks:
- **Clear markdown** explanations
- **Cell numbers** for reference
- **Output preservation** for reproducibility
- **Execution order** clearly documented
- **Dependencies** listed in first cell

### Visualizations:
- **Consistent styling** across all plots
- **Clear labels** and titles
- **Legends** for multi-series plots
- **High resolution** (300 DPI minimum)
- **Accessible colors** (colorblind-friendly)

---

## Implementation Checklist

### Core Notebooks (NO .py files - all in .ipynb):
- [ ] Reference MEV case studies documentation (fact check reference)
- [ ] Create `notebooks/01_data_cleaning.ipynb` with filtering (reference task1 & task2 notebooks)
- [ ] Create `notebooks/02_mev_detection.ipynb` with all 7 algorithms (reference MEV notebooks)
- [ ] Create `notebooks/03_oracle_analysis.ipynb` (reference oracle notebook)
- [ ] Create `notebooks/04_validator_analysis.ipynb` (reference validator notebook)
- [ ] Create `notebooks/05_token_pair_analysis.ipynb` (reference token pair notebook)
- [ ] Create `notebooks/06_pool_analysis.ipynb` (reference pool notebook)
- [ ] Create `notebooks/07_ml_classification.ipynb` (reference ML notebook)
- [ ] Create `notebooks/08_monte_carlo_risk.ipynb` (reference Monte Carlo notebook)
- [ ] Create `notebooks/09_aggregator_mev_analysis.ipynb` (reference aggregator code)
- [ ] Create `notebooks/10_comprehensive_report.ipynb` (combine all analyses)

### Notebooks:
- [ ] Refactor data cleaning notebook
- [ ] Refactor MEV detection notebook (all algorithms)
- [ ] Refactor oracle analysis notebook
- [ ] Refactor validator analysis notebook (enhanced metrics)
- [ ] Create token pair analysis notebook (single AMM)
- [ ] Refactor pool analysis notebook
- [ ] Refactor ML classification notebook
- [ ] Refactor Monte Carlo notebook
- [ ] Create aggregator + MEV analysis notebook
- [ ] Create comprehensive report notebook

### Outputs:
- [ ] Organize CSV files
- [ ] Organize image files
- [ ] Create output index
- [ ] Standardize naming

### Visualizations:
- [ ] Create visualization templates
- [ ] Generate all required plots
- [ ] Standardize styling
- [ ] Save high-resolution versions

### Documentation:
- [ ] Extract and document MEV case studies (fact check reference)
- [ ] Document filtering criteria (DeezNode, Jito tips)
- [ ] Write API documentation
- [ ] Write methodology docs (all algorithms, filtering, case studies)
- [ ] Write user guides
- [ ] Update README

### Testing:
- [ ] Write unit tests for core modules
- [ ] Test data cleaning
- [ ] Test MEV detection
- [ ] Test all analyzers

---

## Tools & Scripts Needed

1. **Code Extraction Script** (`scripts/utils/extract_code_from_notebooks.py`)
   - Extract code cells from notebooks
   - Convert to Python modules
   - Preserve comments and docstrings

2. **Report Generator** (`scripts/utils/generate_report.py`)
   - Generate pure report from outputs
   - Generate report with code from notebooks
   - Include visualizations

3. **Output Validator** (`scripts/utils/validate_outputs.py`)
   - Check all required outputs exist
   - Validate CSV structure
   - Check image files

4. **Visualization Generator** (`scripts/utils/generate_all_visualizations.py`)
   - Generate all visualizations from data
   - Apply consistent styling
   - Save in multiple formats

---

## Timeline Estimate

- **Phase 1** (Core Modules): 2-3 days
- **Phase 2** (Notebook Refactoring): 1-2 days
- **Phase 3** (Output Organization): 1 day
- **Phase 4** (Visualizations): 2-3 days
- **Phase 5** (Documentation): 1-2 days

**Total**: ~7-11 days

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Core Module Extraction)
3. Test extracted modules
4. Refactor notebooks to use modules
5. Generate all visualizations
6. Organize outputs
7. Write documentation
8. Generate final reports
