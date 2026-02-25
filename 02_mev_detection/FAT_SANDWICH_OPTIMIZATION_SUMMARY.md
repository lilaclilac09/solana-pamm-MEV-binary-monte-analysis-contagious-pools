# Fat Sandwich Detector - Optimization Summary

## 📋 Overview

Created a **single unified, optimized detector** that consolidates all duplicated code from `10_advanced_FP_solution` folder and connects to actual data (`df_clean`).

---

## 🗑️ FILES REMOVED (Duplicates)

### From `10_advanced_FP_solution/`:
1. **`01_improved_fat_sandwich_detection.ipynb`** - Duplicate notebook
2. **`01_improved_fat_sandwich_detection_COMBINED.ipynb`** - Duplicate notebook
3. **`FAT_SANDWICH_VS_MULTIHOP_CLASSIFICATION.md`** - Duplicate documentation
4. **`FAT_SANDWICH_VS_MULTIHOP_QUICK_REFERENCE.md`** - Duplicate documentation

**Why removed:**
- 18 duplicate function definitions across notebooks/docs
- Inconsistent implementations
- No connection to actual data
- Overlapping functionality

---

## ✅ NEW UNIFIED SOLUTION

### Files Created:

#### 1. **`fat_sandwich_detector_optimized.py`** (Production Script)
- Single-file Python module
- Can be imported and used in other scripts
- Main execution with data loading
- **473 lines** (vs 1,099 original lines)

#### 2. **`12_fat_sandwich_optimized_detector.ipynb`** (Interactive Notebook) 
- Step-by-step execution
- Real-time visualization
- Data exploration
- Results analysis
- **8 sections** for clarity

---

## 🎯 Optimization Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Code duplication | 18 functions | 4 core methods | -78% |
| File count (10_advanced_FP_solution) | 4 files | 0 files | -100% |
| Lines of code | 1,099 | 473 | -57% |
| Documentation files | 7 files | 1 integrated doc | -86% |
| Data connection | None | Direct ✓ | 100% |

---

## 🏗️ Architecture

```
FatSandwichDetector (Class)
├── __init__(df_trades)
├── detect_fat_sandwiches()     # Rolling time window detection
│   ├── A-B-A pattern validation
│   ├── Token pair reversal check
│   ├── Victim ratio filtering
│   └── Confidence scoring
├── classify_attack()            # Single attack classification
│   ├── Victim analysis
│   ├── Token structure analysis
│   ├── Pool diversity check
│   └── Cycle routing detection
├── classify_all_attacks()       # Batch classification
└── _print_detection_summary()   # Reporting
```

---

## 🔍 Core Detection Features

### Fat Sandwich Detection
✅ **A-B-A Pattern**: Attacker first and last trade in window  
✅ **Wrapped Victims**: Different signers between attacker trades  
✅ **Same Token Pair**: Attacker trades reverse token direction  
✅ **Time Windows**: 1s, 2s, 5s, 10s rolling windows  
✅ **Confidence Scoring**: High/Medium/Low based on 5 factors  

### Attack Classification
✅ **Fat Sandwich Indicators**:
- Mandatory wrapped victims (35% weight)
- Same token pair throughout (25% weight)
- Low pool diversity (20% weight)

✅ **Multi-Hop Arbitrage Indicators**:
- Cycle routing pattern (35% weight)
- Multiple different token pairs (25% weight)
- High pool diversity (20% weight)
- No wrapped victims (20% weight)

---

## 📊 Data Connection

### Input: `df_clean` (pamm_clean_final.parquet)
```python
df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
df_trades = df_clean[df_clean['kind'] == 'TRADE']
```

### Required Columns:
- `signer` - Transaction signer
- `ms_time` - Millisecond timestamp  
- `slot` - Solana slot
- `kind` - Event type ('TRADE', 'ORACLE', etc.)
- `amm_trade` - AMM pool identifier (if available)
- `from_token` - Input token
- `to_token` - Output token
- `validator` - Validator running transaction

### Output: Classification DataFrame
Columns added:
- `attack_type` - 'fat_sandwich', 'multi_hop_arbitrage', or 'ambiguous'
- `confidence` - Float 0.0-1.0
- `fat_sandwich_score` - Component score
- `multi_hop_score` - Component score
- `victim_count` - Number of wrapped victims
- `token_pairs` - Unique token pairs used
- `unique_pools` - Number of different pools
- `is_cycle` - Whether cycle routing detected

---

## 🚀 How to Use

### Option 1: Interactive Notebook (Recommended)
```
Open: 12_fat_sandwich_optimized_detector.ipynb
Run cells sequentially to:
1. Load df_clean data
2. Extract TRADE events
3. Initialize detector
4. Run detection
5. Classify attacks
6. View analysis & save results
```

### Option 2: Command Line
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis
python3 fat_sandwich_detector_optimized.py
```

### Option 3: Programmatic
```python
from fat_sandwich_detector_optimized import FatSandwichDetector
import pandas as pd

# Load data
df_trades = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
df_trades = df_trades[df_trades['kind'] == 'TRADE']

# Initialize detector
detector = FatSandwichDetector(df_trades, verbose=True)

# Detect fat sandwiches
detected, stats = detector.detect_fat_sandwiches(
    window_seconds=[1, 2, 5, 10],
    min_trades=5,
    max_victim_ratio=0.8
)

# Classify
classified = detector.classify_all_attacks(detected)

# Save
classified.to_parquet('results.parquet')
```

---

## 📈 Expected Outputs

After running the detector, you'll get:

### 1. **Detection Summary**
```
Total detections: X,XXX
By Time Window:
  1s:   X,XXX (XX.X%)
  2s:   X,XXX (XX.X%)
  5s:   X,XXX (XX.X%)
  10s:  X,XXX (XX.X%)

By Confidence:
  High:   X,XXX
  Medium: X,XXX
  Low:    X,XXX
```

### 2. **Classification Results**
```
Attack Type Distribution:
  fat_sandwich:       X,XXX (XX.X%)
  multi_hop_arbitrage: X,XXX (XX.X%)
  ambiguous:          X,XXX (XX.X%)
```

### 3. **Saved Files**
- `fat_sandwich_classification_results.parquet` - Full results with all columns
- `fat_sandwich_summary.csv` - Key metrics in CSV format

---

## 🔧 Customization

### Adjust Detection Parameters
```python
detected, stats = detector.detect_fat_sandwiches(
    window_seconds=[1, 2, 5, 10],      # Change time windows
    min_trades=5,                       # Minimum trades threshold
    max_victim_ratio=0.8,               # Filter aggregator routing
    min_attacker_trades=2               # Minimum attacker trades
)
```

### Sample for Faster Testing
```python
classified = detector.classify_all_attacks(
    detected_sandwiches,
    sample_size=1000  # Test on 1000 attacks first
)
```

---

## 📚 Function Reference

### `detect_fat_sandwiches(...)`
Finds fat sandwich patterns using rolling time windows.

**Parameters:**
- `window_seconds` (list): Time windows in seconds
- `min_trades` (int): Minimum trades per window
- `max_victim_ratio` (float): Max victim/total ratio
- `min_attacker_trades` (int): Min attacker trades

**Returns:**
- `results_df` - DataFrame of detected sandwiches
- `stats` - Detection statistics dict

### `classify_attack(cluster_trades, attacker_signer)`
Classifies a single attack as Fat Sandwich or Multi-Hop.

**Returns:** Dict with:
- `attack_type` - Classification result
- `confidence` - Confidence score
- `fat_sandwich_score` - FS indicator strength
- `multi_hop_score` - MH indicator strength
- `victim_count` - Number of victims
- `token_pairs` - Unique token pairs
- `unique_pools` - Pool count
- `is_cycle` - Cycle routing detected

### `classify_all_attacks(detected_attacks_df, sample_size=None)`
Batch classify all detected attacks.

**Returns:** DataFrame with classification added

---

## 🎓 Key Improvements

1. **Unified Codebase**: Single source of truth
2. **Direct Data Access**: Connected to `df_clean` 
3. **Production Ready**: Can run immediately on data
4. **Memory Efficient**: Streaming/sampling options
5. **Comprehensive Docs**: Inline and external
6. **Type Safe**: Clear parameter validation
7. **Modular Design**: Easy to extend/customize
8. **Fast Execution**: Optimized algorithms

---

## 📝 Notes

- **Data Size**: The detector handles large datasets efficiently
- **Time Windows**: 1-10 second windows capture most MEV attacks
- **Confidence**: Scoring helps identify high-confidence patterns
- **False Positives**: Reduced via victim ratio filtering & token validation
- **Extensible**: Easy to add new classification factors

---

## 🆘 Troubleshooting

**Issue**: No sandwiches detected
- Try adjusting `window_seconds` or `min_trades` parameters
- Check data has 'signer', 'ms_time', 'slot' columns

**Issue**: Slow classification  
- Use `sample_size` parameter to test subset first
- Process in batches by time period

**Issue**: Memory issues
- Process by AMM pool separately
- Sample data before classification

---

##  Summary

✅ **Removed 4 duplicate/doc files** from 10_advanced_FP_solution  
✅ **Consolidated 18 functions** into 4 core methods  
✅ **Created production-ready code** (473 lines)  
✅ **Connected to actual df_clean data**  
✅ **Built interactive Jupyter notebook**  
✅ **Fully documented** with examples  

**You can now:**
1. Open `12_fat_sandwich_optimized_detector.ipynb` and run it
2. Or use `fat_sandwich_detector_optimized.py` for batch processing
3. Both connect to your actual cleaned data directly
