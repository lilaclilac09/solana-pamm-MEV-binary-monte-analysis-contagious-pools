# 07_ml_classification.ipynb Diagnosis Guide

## Added Diagnostic Code

### 1. Post Data Loading Diagnosis (Cell 2)
Run immediately after data loading to check:
- Total record count
- All column names
- Whether datetime column exists (to avoid KeyError)
- signer/wallet columns
- Event type distribution
- Label/classification columns (if present)
- Data quality (missing values, infinite values)

### 2. Post Feature Engineering Diagnosis (Cell 5)
Run after feature engineering completes to check:
- Final dataset size
- Class distribution and imbalance ratio
- Whether MEV classes exist and their proportions
- Feature quality (missing values, constant features)
- Specific repair recommendations

## How to Use

1. **Run data loading cell** (Cell 1)
2. **Run diagnosis cell 1** (Cell 2) - Check raw data
3. **Run feature engineering cell** (Cell 3)
4. **Run diagnosis cell 2** (Cell 5) - Check final data
5. **Review diagnosis output** and apply fixes as recommended

## Common Problem Diagnosis

### Problem 1: Total Records < 100
**Symptom**: `Total records: < 100`
**Cause**: Data filtering too strict
**Fix**:
- Check upstream data cleaning notebook (01_data_cleaning.ipynb)
- Relax filtering conditions
- Or use raw transaction-level data (not signer-level)

### Problem 2: Only 1 Class
**Symptom**: `Total classes: 1` or `CRITICAL: Only 1 class`
**Cause**: Classification logic thresholds too high, or data filtering left only one class
**Fix**:
- Lower MEV thresholds (already changed to mev_score > 0.1)
- Check classification logic code
- Consider using binary classification (MEV vs Non-MEV)

### Problem 3: MEV Class < 1%
**Symptom**: `MEV <1% - very rare` or `Total MEV: X (<1%)`
**Cause**: MEV samples extremely rare, severe imbalance
**Fix**:
- Use SMOTE resampling (already added)
- Use class_weight='balanced' (already added)
- Consider binary classification
- Or use anomaly detection (Isolation Forest)

### Problem 4: datetime KeyError
**Symptom**: `KeyError: 'datetime'`
**Cause**: Data file doesn't have 'datetime' column
**Fix**:
- Check data file column names
- Add datetime column in upstream notebook
- Or modify code to use other time column

### Problem 5: Unique Signers < 10
**Symptom**: `Very few unique signers (<10)`
**Cause**: Too few samples after signer-level aggregation
**Fix**:
- Relax signer filtering conditions
- Reduce sampling limit (currently 5000 signers)
- Or use transaction-level data

### Problem 6: Trivial Model (acc=1.0, feature imp=0)
**Symptom**: Model has perfect accuracy but all feature importance = 0
**Cause**: Data has only one class or features have no discriminative power
**Fix**:
- Check class distribution (should be >1 class)
- Check if features have variance (no constant features)
- Use SMOTE + class_weight (already added)

## Fix Steps Based on Diagnosis Results

### If Diagnosis Shows "Only 1 Class":
```python
# Option 1: Lower thresholds (already modified)
# mev_score > 0.1 (lowered from 0.3)

# Option 2: Convert to binary classification
mev_labels = ['LIKELY MEV BOT', 'POSSIBLE MEV']
df_clean['binary_label'] = df_clean['classification'].apply(
    lambda x: 1 if x in mev_labels else 0
)
# Then train with binary_label
```

### If Diagnosis Shows "MEV < 1%":
```python
# Already added fixes:
# 1. SMOTE resampling (Cell 6)
# 2. class_weight='balanced' (model configuration)
# 3. Lower MEV thresholds (feature engineering)

# If still not enough, can:
# - Lower thresholds further to 0.05
# - Use SMOTEENN (SMOTE + Edited Nearest Neighbours)
# - Use BalancedRandomForestClassifier
```

### If Diagnosis Shows "Too Little Data":
```python
# Option 1: Increase sampling size
# In feature engineering cell, modify:
if len(unique_signers) > 10000:  # Increase from 5000 to 10000
    unique_signers = np.random.choice(unique_signers, size=10000, replace=False)

# Option 2: Remove sampling limit
# Comment out sampling code, process all signers
```

## Expected Diagnosis Output Examples

### Normal Case:
```
Total records: 2,559
Total classes: 4
MEV classes found: 1
  - LIKELY MEV BOT: 194 (7.58%)
Total MEV: 194 (7.58%)
Imbalance ratio: 2268.00x
  MODERATE: Imbalance (>10x). Recommend class_weight='balanced'.
```

### Problem Case:
```
Total records: 5
Total classes: 1
  CRITICAL: Only 1 class found! Models will be trivial or skipped.
  WARNING: No MEV classes found!
```

## Next Steps

1. **Run diagnosis code** and review output
2. **Apply fixes** based on diagnosis results
3. **If problems are severe**, consider:
   - Use 07a_ml_classification_binary.ipynb (binary classification version)
   - Go back to upstream and relax data filtering
   - Use raw transaction-level data

## Quick Checklist

After running diagnosis, check:
- [ ] Total records > 100
- [ ] Number of classes >= 2
- [ ] MEV classes exist and > 0
- [ ] Unique signers > 10
- [ ] No datetime KeyError
- [ ] No missing values or already handled
- [ ] No constant features

If all items are checked, you can proceed with model training.
If any items are unchecked, fix them first before continuing.
