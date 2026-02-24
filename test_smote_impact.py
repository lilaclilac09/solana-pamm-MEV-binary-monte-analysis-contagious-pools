import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("EXPERIMENT 1: SMOTE IMPACT ON TRAINING CLASS DISTRIBUTION")
print("=" * 70)

# Load data
print("\n[Loading data...]")
df = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
print(f"  Dataset size: {len(df):,} rows")

# Feature engineering (simplified from notebook)
print("\n[Building signer-level features...]")
signer_features = []
for signer, group in df.groupby('signer'):
    total_trades = len(group)
    if total_trades < 5:
        continue
    
    trades_list = []
    for trades in group['trades']:
        if isinstance(trades, list):
            trades_list.extend(trades)
    
    trades_per_hour = total_trades / max(1, (group['block_time'].max() - group['block_time'].min()) / 3600)
    
    # Simplified feature calculations (using defaults if not available)
    cluster_ratio = 0.0
    mev_score = 0.0
    oracle_backrun_ratio = 0.0
    wash_trading_score = 0.0
    aggregator_likelihood = 0.0
    late_slot_ratio = 0.0
    high_bytes_ratio = 0.0
    
    signer_features.append({
        'signer': signer,
        'total_trades': total_trades,
        'trades_per_hour': min(trades_per_hour, 100),
        'aggregator_likelihood': aggregator_likelihood,
        'late_slot_ratio': late_slot_ratio,
        'oracle_backrun_ratio': oracle_backrun_ratio,
        'high_bytes_ratio': high_bytes_ratio,
        'cluster_ratio': cluster_ratio,
        'mev_score': mev_score,
        'wash_trading_score': wash_trading_score,
    })

df_features = pd.DataFrame(signer_features)
print(f"  Created {len(df_features):,} signer features")

# Create labels based on MEV detection (simplified for this test)
# In real notebook, this would use MEV detection results
df_features['mev_label'] = np.random.choice([0, 1], size=len(df_features), p=[0.9, 0.1])

# Prepare data
feature_cols = [
    'total_trades', 'trades_per_hour', 'aggregator_likelihood',
    'late_slot_ratio', 'oracle_backrun_ratio', 'high_bytes_ratio',
    'cluster_ratio', 'mev_score', 'wash_trading_score'
]

X = df_features[feature_cols].fillna(0)
y = df_features['mev_label']

print(f"\n[Train/Test split...]")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

print("\n" + "="*70)
print("CLASS DISTRIBUTION BEFORE SMOTE:")
print("="*70)
class_dist_before = Counter(y_train)
print(f"\nTraining set class distribution:")
for label, count in sorted(class_dist_before.items()):
    pct = (count / len(y_train)) * 100
    print(f"  Class {label}: {count:,} samples ({pct:.1f}%)")

print(f"\nTotal training samples: {len(y_train):,}")
print(f"Imbalance ratio: {max(class_dist_before.values()) / min(class_dist_before.values()):.2f}x")

# Apply SMOTE
print("\n" + "="*70)
print("APPLYING SMOTE (sampling_strategy=0.5)...")
print("="*70)
smote = SMOTE(sampling_strategy=0.5, random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)

print("\n" + "="*70)
print("CLASS DISTRIBUTION AFTER SMOTE:")
print("="*70)
class_dist_after = Counter(y_train_res)
print(f"\nTraining set class distribution (after SMOTE):")
for label, count in sorted(class_dist_after.items()):
    pct = (count / len(y_train_res)) * 100
    print(f"  Class {label}: {count:,} samples ({pct:.1f}%)")

print(f"\nTotal training samples: {len(y_train_res):,}")
print(f"Imbalance ratio: {max(class_dist_after.values()) / min(class_dist_after.values()):.2f}x")

print("\n" + "="*70)
print("SMOTE IMPACT SUMMARY:")
print("="*70)
print(f"\n  ✓ Class 0 samples: {class_dist_before[0]:,} → {class_dist_after[0]:,}")
print(f"  ✓ Class 1 samples: {class_dist_before[1]:,} → {class_dist_after[1]:,} (+{class_dist_after[1] - class_dist_before[1]:,})")
print(f"  ✓ Total training samples: {len(y_train):,} → {len(y_train_res):,} (+{len(y_train_res) - len(y_train):,})")
print(f"  ✓ Imbalance ratio improved: {max(class_dist_before.values()) / min(class_dist_before.values()):.2f}x → {max(class_dist_after.values()) / min(class_dist_after.values()):.2f}x")
