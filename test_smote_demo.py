import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("EXPERIMENT 1: SMOTE IMPACT ON CLASS DISTRIBUTION (SYNTHETIC DATA)")
print("=" * 80)

# Create synthetic imbalanced data (10% MEV, 90% normal)
print("\n[Creating synthetic imbalanced dataset...]")
n_samples = 5000
np.random.seed(42)

# Generate features: 9 features similar to the ML notebook
n_features = 9
X = np.random.randn(n_samples, n_features)

# Create highly imbalanced labels (10% MEV, 90% normal)
y = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
print(f"  Dataset size: {n_samples:,} samples with {n_features} features")
print(f"  Initial distribution: Class 0: {(y == 0).sum()}, Class 1: {(y == 1).sum()}")

# Train/Test split
print("\n[Performing train/test split (80/20, stratified)...]")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

print("\n" + "="*80)
print("BEFORE SMOTE - Training Set Class Distribution:")
print("="*80)
class_dist_before = Counter(y_train)
print(f"\nUsing {len(X_train):,} training samples for model training:")
for label in sorted(class_dist_before.keys()):
    count = class_dist_before[label]
    pct = (count / len(y_train)) * 100
    bar = "█" * int(pct / 2)
    print(f"  Class {label}: {count:>5,} samples | {pct:>4.1f}% | {bar}")

imbalance_ratio_before = max(class_dist_before.values()) / min(class_dist_before.values())
print(f"\nImbalance ratio: {imbalance_ratio_before:.2f}x (Class 0 is {imbalance_ratio_before:.1f}x larger than Class 1)")

# Apply SMOTE with sampling_strategy=0.5 (same as the notebook)
print("\n" + "="*80)
print("APPLYING SMOTE with sampling_strategy=0.5")
print("  (This generates synthetic samples of the minority class)")
print("="*80)
smote = SMOTE(sampling_strategy=0.5, random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)

print("\n" + "="*80)
print("AFTER SMOTE - Training Set Class Distribution:")
print("="*80)
class_dist_after = Counter(y_train_res)
print(f"\nUsing {len(X_train_res):,} training samples for model training:")
for label in sorted(class_dist_after.keys()):
    count = class_dist_after[label]
    pct = (count / len(y_train_res)) * 100
    bar = "█" * int(pct / 2)
    print(f"  Class {label}: {count:>5,} samples | {pct:>4.1f}% | {bar}")

imbalance_ratio_after = max(class_dist_after.values()) / min(class_dist_after.values())
print(f"\nImbalance ratio: {imbalance_ratio_after:.2f}x (balanced to {imbalance_ratio_after:.1f}x)")

print("\n" + "="*80)
print("SMOTE IMPACT SUMMARY:")
print("="*80)
print(f"\n  ✓ Class 0 (Non-MEV) samples:")
print(f"    Before: {class_dist_before[0]:,} → After: {class_dist_after[0]:,} (no change)")
print(f"\n  ✓ Class 1 (MEV) samples:")
print(f"    Before: {class_dist_before[1]:,} → After: {class_dist_after[1]:,} (+{class_dist_after[1] - class_dist_before[1]:,} synthetic samples)")
print(f"\n  ✓ Total training samples:")
print(f"    Before: {len(y_train):,} → After: {len(y_train_res):,} (+{len(y_train_res) - len(y_train):,} total)")
print(f"\n  ✓ Imbalance ratio improved from {imbalance_ratio_before:.2f}x to {imbalance_ratio_after:.2f}x")

print("\n" + "="*80)
print("KEY FINDINGS:")
print("="*80)
print(f"""
1. SMOTE generates synthetic minority class samples (Class 1 = MEV detections)
   
2. With sampling_strategy=0.5, minority class is resampled to 50% of majority class
   - Original: {class_dist_before[1]:,} MEV vs {class_dist_before[0]:,} Non-MEV (ratio: 1:{imbalance_ratio_before:.0f})
   - After SMOTE: {class_dist_after[1]:,} MEV vs {class_dist_after[0]:,} Non-MEV (ratio: 1:{1/imbalance_ratio_after:.1f})

3. Effect on model training:
   ✓ Models trained on SMOTE-balanced data learn better decision boundaries
   ✓ Reduced bias towards majority (frequent) class
   ✓ Better sensitivity to minority (MEV) patterns
   ✓ Affects predicted labels for downstream tasks

4. BisonFi MEV detection numbers could differ because:
   ✓ SMOTE changes model sensitivity to MEV patterns during training
   ✓ More balanced training leads to different classification thresholds
   ✓ Ultimately affects count of MEV-positive predictions for BisonFi pools
""")
