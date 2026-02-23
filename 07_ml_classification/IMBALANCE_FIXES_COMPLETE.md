# Complete Imbalance Handling Implementation

## All Modifications Applied

### 1. Lowered MEV Detection Thresholds
- **Changed**: `mev_score > 0.3` → `mev_score > 0.1` (3x lower threshold)
- **Changed**: `cluster_ratio > 0.3` → `cluster_ratio > 0.2` (for sandwich patterns)
- **Impact**: Will capture ~3x more MEV cases in classification

### 2. Comprehensive Class Imbalance Assessment
- **New Cell**: Detailed class distribution analysis
- **Features**:
  - Class counts and percentages
  - Imbalance ratio calculation
  - MEV class specific analysis
  - Severity assessment with recommendations
  - **Visualization**: Bar chart and pie chart of class distribution
  - Saved to: `derived/ml_results/class_distribution.png`

### 3. SMOTE Resampling
- **New Cell**: Configurable SMOTE application
- **Features**:
  - `USE_SMOTE = True` flag to enable/disable
  - Automatic `k_neighbors` calculation
  - Only applied to training set (no data leakage)
  - Before/after class distribution reporting
  - Graceful fallback if imbalanced-learn not installed

### 4. Model Updates with Class Weight
- **Random Forest**:
  - Added `class_weight='balanced'`
  - Added `min_samples_split=5`, `min_samples_leaf=2`
- **XGBoost**:
  - Automatic `scale_pos_weight` calculation for MEV class
  - Added `min_child_weight=1`, `subsample=0.8`
- **Cross-validation models**: Updated dictionary with balanced weights

### 5. Detailed MEV Metrics Evaluation
- **New Cell**: Comprehensive MEV-specific metrics
- **Features**:
  - Per-MEV-class precision, recall, F1-score
  - Combined MEV metrics (all MEV classes together)
  - Support (number of samples)
  - Warnings if no MEV samples in test set
  - Evaluates both Random Forest and XGBoost

### 6. Monte Carlo Simulation
- **New Cell**: Model robustness testing
- **Features**:
  - 1000 iterations with noise injection (1% of feature scale)
  - Reports:
    - Mean accuracy ± std dev with 95% CI
    - Mean F1 score (macro average) ± std dev with 95% CI
    - MEV class recall ± std dev with 95% CI
  - Stability assessment and recommendations

## Expected Results After Running

### Before Fixes:
- MEV recall: 0 (model ignores MEV class)
- Accuracy: 1.0 (trivial, predicts only majority class)
- Feature importance: All zeros
- Test set: Only 2 samples, single class

### After Fixes:
- MEV recall: >0 (should be 0.5-0.9 depending on data)
- Accuracy: 0.85-0.95 (realistic, not perfect)
- Feature importance: Non-zero values (models use features)
- Test set: Multiple classes represented
- MEV F1-score: >0.5 (improved detection)

## Configuration

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

### MEV Thresholds (in feature engineering)
```python
mev_score > 0.1  # Lowered from 0.3
cluster_ratio > 0.2  # Lowered from 0.3
```

## Installation

```bash
pip install imbalanced-learn
```

## Running the Notebook

1. **Run all cells** from top to bottom
2. **Check outputs**:
   - Class imbalance assessment (should show severity)
   - SMOTE resampling (should balance classes)
   - MEV metrics (should show recall > 0)
   - Monte Carlo (should show stability)

## Troubleshooting

### If MEV recall is still 0:
1. Check if MEV classes exist in test set (see MEV metrics output)
2. Lower MEV thresholds further (e.g., `mev_score > 0.05`)
3. Increase SMOTE sampling (e.g., `sampling_strategy={mev_class: target_count}`)
4. Check if data filtering is too aggressive

### If accuracy is still 1.0:
1. Check feature importance (should be non-zero)
2. Verify SMOTE was applied (check before/after distribution)
3. Check if test set has multiple classes
4. Consider binary classification (MEV vs Non-MEV)

### If Monte Carlo shows high variance:
1. Increase training data
2. Use simpler models
3. Reduce feature noise
4. Check for data quality issues

## Files Generated

- `derived/ml_results/class_distribution.png` - Class distribution visualization
- All other results in `derived/ml_results/` as before

## Next Steps

1. Run the notebook and check MEV metrics
2. If MEV recall < 0.5, try:
   - Further lower thresholds
   - Use SMOTEENN (SMOTE + Edited Nearest Neighbours)
   - Try BalancedRandomForestClassifier
   - Consider binary classification
3. Monitor Monte Carlo stability
4. Adjust hyperparameters based on results
