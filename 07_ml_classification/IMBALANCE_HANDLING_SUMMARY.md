# Class Imbalance Handling Implementation Summary

## What Was Added

### 1. Imports and Dependencies
- Added `imblearn` imports (SMOTE, RandomUnderSampler, SMOTEENN, BalancedRandomForestClassifier)
- Added `Counter` from collections for class distribution analysis
- Graceful fallback if imbalanced-learn is not installed

### 2. Class Imbalance Assessment (New Cell)
- Detailed class distribution analysis
- Imbalance ratio calculation
- MEV class specific analysis
- Severity assessment with recommendations

### 3. SMOTE Resampling (New Cell)
- Configurable SMOTE application (USE_SMOTE flag)
- Automatic k_neighbors calculation based on smallest class
- Only applied to training set (not test set to avoid data leakage)
- Before/after class distribution reporting

### 4. Model Updates
- **Random Forest**: Added `class_weight='balanced'`, `min_samples_split=5`, `min_samples_leaf=2`
- **XGBoost**: Added automatic `scale_pos_weight` calculation for MEV class
- Updated cross-validation models dictionary

### 5. Monte Carlo Simulation (New Cell)
- 1000 iterations with noise injection (1% of feature scale)
- Tests model stability under feature perturbations
- Reports:
  - Mean accuracy ± std dev with 95% CI
  - Mean F1 score (macro average) ± std dev with 95% CI
  - MEV class recall ± std dev with 95% CI
  - Stability assessment

## Configuration Options

### SMOTE Configuration
```python
USE_SMOTE = True  # Set to False to disable
SMOTE_STRATEGY = 'auto'  # 'auto' balances all classes
```

### Monte Carlo Configuration
```python
N_SIMULATIONS = 1000  # Number of iterations
NOISE_LEVEL = 0.01  # 1% of feature scale
```

## Expected Improvements

1. **Better MEV Detection**: SMOTE + class_weight should improve MEV recall from 0 to >0
2. **More Realistic Accuracy**: Should drop from perfect 1.0 to realistic 0.85-0.95
3. **Non-Zero Feature Importance**: Models will actually use features
4. **Stability Metrics**: Monte Carlo shows if models are robust

## Usage

1. **Install dependencies** (if not already installed):
   ```bash
   pip install imbalanced-learn
   ```

2. **Run the notebook**: All imbalance handling is automatic

3. **Monitor outputs**:
   - Check imbalance assessment for severity
   - Verify SMOTE balanced classes
   - Review Monte Carlo stability metrics
   - Check MEV recall in classification reports

## Next Steps

If issues persist:
1. Adjust SMOTE_STRATEGY to target specific classes
2. Try SMOTEENN (SMOTE + Edited Nearest Neighbours) for noise cleaning
3. Use BalancedRandomForestClassifier instead of standard RF
4. Consider binary classification (MEV vs Non-MEV) if multi-class is too hard
