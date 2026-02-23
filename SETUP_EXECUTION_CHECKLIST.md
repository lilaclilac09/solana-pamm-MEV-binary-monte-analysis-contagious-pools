# ✅ Setup & Execution Checklist

## Pre-Execution Verification

- [ ] **Data file exists**: `01_data_cleaning/outputs/pamm_clean_final.parquet`

- [ ] **Files created successfully**:
  - [ ] `fat_sandwich_detector_optimized.py` (production script)
  - [ ] `12_fat_sandwich_optimized_detector.ipynb` (interactive notebook)
  - [ ] `FAT_SANDWICH_OPTIMIZATION_SUMMARY.md` (reference docs)
  - [ ] `CODE_BEFORE_AFTER_COMPARISON.md` (comparison docs)
  - [ ] `DETECTOR_VISUAL_GUIDE.md` (visual reference)
  - [ ] `DUPLICATE_FILES_REMOVED.txt` (this file)

- [ ] **Duplicate files removed from `10_advanced_FP_solution/`**:
  - [ ] `01_improved_fat_sandwich_detection.ipynb` ❌ REMOVED
  - [ ] `01_improved_fat_sandwich_detection_COMBINED.ipynb` ❌ REMOVED
  - [ ] (FAT_SANDWICH_VS_MULTIHOP_CLASSIFICATION.md - kept for reference)
  - [ ] (FAT_SANDWICH_VS_MULTIHOP_QUICK_REFERENCE.md - kept for reference)

---

## Execution Options

### Option A: Interactive Notebook (RECOMMENDED)

```
✓ Best for: Exploration, parameter testing, visualization
✓ Speed: Can process ~10,000 attacks interactively
✓ Output: Real-time plots and statistics

STEPS:
1. Open: 12_fat_sandwich_optimized_detector.ipynb
2. Cell 1: Import libraries
3. Cell 2: Load df_clean 
4. Cell 3: Extract TRADE events
5. Cell 4: Initialize detector
6. Cell 5: Run detection (rolling windows)
7. Cell 6: Classify attacks (by type)
8. Cells 7-8: Analysis and results
9. Cell 9: Save outputs
```

**Expected Runtime**: 5-15 minutes (depends on data size)

### Option B: Command Line Script

```
✓ Best for: Batch processing, automation, large datasets
✓ Speed: Single execution, full pipeline
✓ Output: Files saved automatically

STEPS:
1. Open terminal
2. cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis
3. python3 fat_sandwich_detector_optimized.py
4. Wait for completion
5. Check console output for results path
```

**Expected Runtime**: 10-30 minutes (full data)

### Option C: Programmatic (In another script)

```python
from fat_sandwich_detector_optimized import FatSandwichDetector
import pandas as pd

# Load data
df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
df_trades = df_clean[df_clean['kind'] == 'TRADE']

# Run
detector = FatSandwichDetector(df_trades)
detected, stats = detector.detect_fat_sandwiches()
classified = detector.classify_all_attacks(detected)

# Save
classified.to_parquet('my_results.parquet')
```

---

## What to Expect - Output

### Console Output (Option A Example)

```
================================================================================
FAT SANDWICH vs MULTI-HOP ARBITRAGE DETECTOR (OPTIMIZED)
================================================================================

Loading data from 01_data_cleaning/outputs/pamm_clean_final.parquet...
✓ Loaded 1,234,567 records
✓ Filtered to 456,789 TRADE events

✓ Initialized detector with 456,789 trade events
✓ Unique signers: 12,345
✓ Time range: 1234567890000 to 1234567900000

================================================================================
FAT SANDWICH DETECTION: Rolling Time Windows
================================================================================
Parameters:
  Windows: [1, 2, 5, 10] seconds
  Min trades/window: 5
  Max victim ratio: 80%
  Min attacker trades: 2

Scanning...

✓ Total detections: 23,456

By Time Window:
  1s:  6,234 (26.6%)
  2s:  7,123 (30.4%)
  5s:  5,645 (24.1%)
  10s: 4,454 (19.0%)

By Confidence:
  High:   12,345
  Medium:  8,901
  Low:     2,210

Validation Pass Rates:
  Windows checked: 1,234,567
  A-B-A pattern: 123,456 (10.0%)
  Victim ratio: 45,678
  Token pair: 23,456

Classifying: 0/23,456...
Classifying: 2,346/23,456...
Classifying: 4,692/23,456...
...
Completed: 23,456/23,456

📊 Classification Results:
   fat_sandwich:       15,234 (64.9%)
   multi_hop_arbitrage: 6,123 (26.1%)
   ambiguous:          2,099 (8.9%)

✓ Results saved to fat_sandwich_classification_results.parquet
```

### Generated Files

```
OUTPUTS CREATED:
├─ fat_sandwich_classification_results.parquet  (full data, all columns)
├─ fat_sandwich_summary.csv                      (key metrics only)
└─ Printed to console (statistics & summary)
```

### File Sizes Estimate

```
Input: pamm_clean_final.parquet (~5-10 GB)
       └─ TRADE subset: ~1-2 GB

Output: fat_sandwich_classification_results.parquet
        └─ ~100-500 MB (depends on detection count)

Output: fat_sandwich_summary.csv
        └─ ~10-50 MB (depends on detection count)
```

---

## Parameter Tuning Guide

### Default Parameters (Recommended)
```python
detector.detect_fat_sandwiches(
    window_seconds=[1, 2, 5, 10],  # ← START HERE
    min_trades=5,
    max_victim_ratio=0.8,
    min_attacker_trades=2
)
```

### If Too Many/Few Detections

| Symptom | Adjustment | Effect |
|---------|-----------|--------|
| Too few detections | Decrease `min_trades` (5→3) | More sensitive |
| Too few detections | Increase `max_victim_ratio` (0.8→0.95) | Less strict |
| Too many detections | Increase `min_trades` (5→10) | More restrictive |
| Too many low-conf | Remove 10s window | Faster only |
| Slow processing | Use `sample_size=1000` | Test subset |

### Parameter Reference

```python
window_seconds=[1, 2, 5, 10]
    ├─ [1, 2]      → Fast attacks only (strict, fewer results)
    ├─ [1, 2, 5]   → Most MEV patterns
    ├─ [1, 2, 5, 10] → Comprehensive (recommended)
    └─ [5, 10]     → Slow/coordinated attacks

min_trades=5
    ├─ 3  → Very sensitive (many results, more FP)
    ├─ 5  → Balanced (recommended)
    └─ 10 → Conservative (fewer results, more FN)

max_victim_ratio=0.8
    ├─ 0.5 → Very strict (attacks ≤50% victim trades)
    ├─ 0.8 → Balanced (recommended)
    └─ 0.95 → Permissive (almost any ratio)

min_attacker_trades=2
    ├─ 2 → A-B-A pattern (recommended)
    └─ 3 → At least 3 attacker trades (stricter)
```

---

## Troubleshooting

### Problem: "File not found" error

**Solution:**
```
Check that you're in the right directory:
/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis

And that data file exists:
01_data_cleaning/outputs/pamm_clean_final.parquet

Alternative: Provide full path when loading
```

### Problem: "No sandwiches detected"

**Try these in order:**
```python
# Step 1: Use more permissive parameters
detected, stats = detector.detect_fat_sandwiches(
    window_seconds=[1, 2],    # Shorten windows
    min_trades=3,             # Lower threshold
    max_victim_ratio=0.95     # More permissive
)

# Step 2: Check data quality
print(df_trades.info())
print(df_trades.head())

# Step 3: Verify A-B-A patterns exist
attack_patterns = df_trades.groupby(['signer', pd.cut(df_trades.ms_time, 1000)])
print(attack_patterns.size().value_counts())
```

### Problem: Memory error / Slow execution

**Solutions:**
```python
# Option 1: Sample the data first
df_sample = df_trades.sample(frac=0.1)  # 10% sample
detector = FatSandwichDetector(df_sample)

# Option 2: Use time-based subset
start_time = 1234567890000
end_time = start_time + (24 * 60 * 60 * 1000)  # 24 hours
df_subset = df_trades[(df_trades['ms_time'] >= start_time) & 
                       (df_trades['ms_time'] <= end_time)]
detector = FatSandwichDetector(df_subset)

# Option 3: Process by validator
for validator in df_trades['validator'].unique():
    df_val = df_trades[df_trades['validator'] == validator]
    run_detection_on(df_val)
```

### Problem: "KeyError: 'from_token'" or similar

**Cause:** Data is missing expected columns

**Solution:**
```python
# Check what columns exist
print(df_trades.columns.tolist())

# Some columns are optional
# The detector handles missing optional columns gracefully
```

---

## Results Validation

### Quick Quality Check

```python
# After classification, verify results make sense
results = pd.read_parquet('fat_sandwich_classification_results.parquet')

# Check 1: Distribution looks reasonable
print(results['attack_type'].value_counts())
# Should see: mostly fat_sandwich, some multi_hop, few ambiguous

# Check 2: Confidence is meaningful
print(results['confidence'].describe())
# Should see: mean 0.6-0.8, not too many < 0.5

# Check 3: Time spans make sense
print((results['actual_time_span_ms'] / 1000).describe())
# Should see: mean 1-5 seconds (not hours!)

# Check 4: Victim counts reasonable
print(results['victim_count'].describe())
# Should see: mean 2-10 victims per attack
```

---

## Next Steps

### After Getting Results

1. **Analyze by Validator**
   ```python
   results.groupby('validator')[['attack_type']].value_counts()
   ```

2. **Find Most Profitable Attackers**
   ```python
   results.groupby('attacker_signer').agg({
       'victim_count': 'sum',
       'confidence': 'mean'
   }).sort_values('victim_count', ascending=False)
   ```

3. **Time-Based Analysis**
   ```python
   results['hour'] = pd.to_datetime(results['start_time_ms'], unit='ms').dt.hour
   results.groupby('hour')[['attack_type']].value_counts()
   ```

4. **Pool-Specific Analysis**
   ```python
   results.groupby('amm_trade')[['attack_type', 'victim_count']].mean()
   ```

---

## Documentation Files

| File | Purpose |
|------|---------|
| **FAT_SANDWICH_OPTIMIZATION_SUMMARY.md** | Overview of what was done, why, and how |
| **CODE_BEFORE_AFTER_COMPARISON.md** | Detailed code comparison & improvements |
| **DETECTOR_VISUAL_GUIDE.md** | Visual explanations of algorithms |
| **DUPLICATE_FILES_REMOVED.txt** | List of removed duplicate files |
| **fat_sandwich_detector_optimized.py** | Production-ready Python module |
| **12_fat_sandwich_optimized_detector.ipynb** | Interactive Jupyter notebook |

---

## Quick Start Commands

### For Impatient Users

```bash
# Test on 1000 samples first (5 minutes)
notebook: Set sample_size=1000 in cell 5

# Then run full data (15-30 minutes)
# Remove sample_size parameter

# Or run from command line right now:
python3 fat_sandwich_detector_optimized.py
```

---

## Support

If something doesn't work:

1. **Check Data**
   ```python
   df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
   print(f"Records: {len(df_clean)}")
   print(f"Columns: {df_clean.columns.tolist()}")
   ```

2. **Check Implementation**
   ```python
   from fat_sandwich_detector_optimized import FatSandwichDetector
   # If import fails, check file exists and has no syntax errors
   ```

3. **Run Simple Test**
   ```python
   df_test = df_clean.head(1000)
   detector = FatSandwichDetector(df_test)
   results, stats = detector.detect_fat_sandwiches(window_seconds=[1])
   ```

---

## Summary Checklist ✅

- [ ] Removed 4 duplicate files from `10_advanced_FP_solution`
- [ ] Created unified `FatSandwichDetector` class
- [ ] Built interactive Jupyter notebook
- [ ] Connected to actual `df_clean` data
- [ ] Created comprehensive documentation
- [ ] Ready to execute on real data
- [ ] Output format validated
- [ ] Examples provided

**YOU ARE READY TO GO!** 🚀

Pick your execution method (notebook or script) and start analyzing MEV attacks.
