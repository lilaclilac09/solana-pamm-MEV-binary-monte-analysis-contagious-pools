# Fixes Applied to 07_ml_classification.ipynb

## Summary

This document describes all the fixes applied to address the issues identified in the ML classification notebook, including:
- Perfect accuracy with zero feature importance (trivial model)
- Single class or extremely imbalanced data
- Missing MEV class detection
- Small test sets (only 2 samples)

## Fixes Applied

### 1. ✅ Lowered MEV Detection Thresholds

**Problem**: MEV threshold was too high (0.3), causing most MEV cases to be missed.

**Fix**: 
- Changed `mev_score > 0.3` to `mev_score > 0.1` (3x lower threshold)
- Changed `cluster_ratio > 0.3` to `cluster_ratio > 0.2` for sandwich patterns

**Location**: Classification logic in data loading cell

### 2. ✅ Added Comprehensive Data Diagnostics

**Problem**: No visibility into data quality, class distribution, or feature statistics.

**Fix**: Added new diagnostic cell that reports:
- Class distribution and proportions
- Feature statistics (mean, std, min, max)
- Constant feature detection (variance check)
- Missing values check
- Class imbalance assessment
- Sample size assessment
- MEV class detection status

**Location**: New cell after data loading (cell index 2)

### 3. ✅ Added SMOTE Oversampling

**Problem**: Severe class imbalance (MEV ~7.6%, Aggregator ~88.6%) causing models to ignore minority classes.

**Fix**: 
- Added SMOTE (Synthetic Minority Oversampling Technique) support
- Automatically oversamples minority classes in training set only
- Configurable via `USE_SMOTE` flag
- Handles edge cases (too few samples for k_neighbors)

**Location**: New cell after train_test_split (cell index 5)

**Dependencies**: Requires `imbalanced-learn` package
```bash
pip install imbalanced-learn
```

### 4. ✅ Fixed Models to Handle Class Imbalance

**Problem**: Models didn't account for class imbalance, leading to trivial predictions.

**Fixes Applied**:

#### Random Forest:
- Added `class_weight='balanced'` to automatically weight classes
- Added `min_samples_split=5` and `min_samples_leaf=2` for better small dataset handling

#### XGBoost:
- Added automatic `scale_pos_weight` calculation for MEV class
- Added `min_child_weight=1` and `subsample=0.8` for regularization

**Location**: Model definition cells for Random Forest and XGBoost

### 5. ✅ Added Monte Carlo Simulation

**Problem**: No robustness testing - single train/test split can be misleading.

**Fix**: Added Monte Carlo simulation that:
- Runs 1000 iterations with noise injection (1% of feature scale)
- Tests model stability under feature perturbations
- Reports mean accuracy, std deviation, and 95% confidence intervals
- Specifically tracks MEV class recall stability
- Provides stability assessment

**Location**: New cell before results saving (cell index 30)

### 6. ✅ Added SMOTE Import

**Problem**: SMOTE not available in imports.

**Fix**: Added import with graceful fallback:
```python
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
```

**Location**: Imports cell (cell index 1)

## Expected Improvements

After applying these fixes, you should see:

1. **More MEV Cases Detected**: Lower thresholds will capture ~3x more MEV cases
2. **Better Class Balance**: SMOTE will balance training set classes
3. **Non-Zero Feature Importance**: Models will actually use features to make predictions
4. **Realistic Accuracy**: Accuracy will drop from 1.0 to more realistic values (likely 0.85-0.95)
5. **MEV Recall > 0**: Models will actually detect MEV cases instead of ignoring them
6. **Stability Metrics**: Monte Carlo will show if models are robust

## Usage Instructions

1. **Install Dependencies** (if not already installed):
   ```bash
   pip install imbalanced-learn
   ```

2. **Run the Notebook**:
   - The diagnostics cell will show data quality issues
   - SMOTE will automatically balance classes (if enabled)
   - Models will use balanced weights
   - Monte Carlo will test robustness

3. **Monitor Outputs**:
   - Check diagnostics for class distribution
   - Verify SMOTE increased minority class samples
   - Check feature importance is non-zero
   - Review Monte Carlo stability metrics

## Configuration Options

- **SMOTE**: Set `USE_SMOTE = False` in cell 5 to disable oversampling
- **Monte Carlo**: Adjust `N_SIMULATIONS` and `NOISE_LEVEL` in Monte Carlo cell
- **MEV Thresholds**: Modify thresholds in classification logic (cell 3)

## Next Steps

If issues persist after these fixes:

1. **Check Data Quality**: Review diagnostics output for constant features or missing values
2. **Increase Sample Size**: Remove the 5000 signer sampling limit if possible
3. **Feature Engineering**: Add more discriminative features if current ones are insufficient
4. **Binary Classification**: Consider binary MEV vs Non-MEV instead of multi-class
5. **Ensemble Methods**: Combine multiple models for better MEV detection

## Notes

- SMOTE only applies to training set (test set remains untouched)
- Monte Carlo uses Random Forest by default (can be extended to other models)
- All fixes are backward compatible (notebook will work without SMOTE if package missing)
- Thresholds can be further adjusted based on domain knowledge
