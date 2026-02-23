#!/usr/bin/env python3
"""
🧠 Optimized GMM Clustering Analysis
Connects to df_clea (cleaned data) and performs advanced clustering
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*100)
print("🧠 OPTIMIZED GMM CLUSTERING ANALYSIS - CONNECTED TO REAL DATA")
print("="*100)

# ==================== STEP 1: LOAD AND PREPARE DATA ====================
print("\n📊 STEP 1: Loading and Preparing Data")
print("-" * 100)

try:
    # Load cleaned data
    df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
    print(f"✅ Cleaned data loaded: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
    
    # Display available columns
    print(f"\n   Available columns ({len(df_clean.columns)}):")
    for i, col in enumerate(df_clean.columns, 1):
        if i <= 15:
            print(f"     {i:2d}. {col}")
    if len(df_clean.columns) > 15:
        print(f"     ... and {len(df_clean.columns) - 15} more columns")
    
except Exception as e:
    print(f"❌ Error loading cleaned data: {e}")
    exit(1)

# ==================== STEP 2: FEATURE ENGINEERING ====================
print("\n🔧 STEP 2: Feature Engineering & Variable Selection")
print("-" * 100)

# Identify numeric columns that can be used for clustering
numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
print(f"📊 Numeric columns available: {len(numeric_cols)}")
for col in numeric_cols[:15]:
    print(f"     • {col}")
if len(numeric_cols) > 15:
    print(f"     ... and {len(numeric_cols) - 15} more")

# Select key features for analysis
# Prioritize columns that are likely to be present in MEV analysis
key_features_candidates = [
    'oracle_backrun_ratio', 'bot_ratio', 'time_diff_ms', 'late_slot_ratio',
    'wash_trading_score', 'attacker_count', 'tx_idx', 'slot', 'us_since_first_shred'
]

# Check which candidates exist in the data
key_features = [col for col in key_features_candidates if col in df_clean.columns]
print(f"\n✅ Selected key features for clustering ({len(key_features)}):")
for feat in key_features:
    print(f"     • {feat}")

if len(key_features) < 3:
    # If not enough key features, use top numeric columns
    key_features = numeric_cols[:min(5, len(numeric_cols))]
    print(f"\n⚠️  Using top numeric columns instead: {key_features}")

# Create working dataset
df_work = df_clean[key_features].copy()

# Handle missing values
print(f"\n📋 Data Quality Check:")
missing_counts = df_work.isnull().sum()
print(f"   Total records: {len(df_work):,}")
for col, count in missing_counts[missing_counts > 0].items():
    print(f"     • {col}: {count:,} missing ({count/len(df_work)*100:.2f}%)")

# Remove rows with missing values
df_work = df_work.dropna()
print(f"   After removing NaN: {len(df_work):,} records ({len(df_work)/len(df_clean)*100:.1f}% retained)")

# ==================== STEP 3: OUTLIER DETECTION ====================
print("\n🎯 STEP 3: Outlier Detection & Cleaning")
print("-" * 100)

iso_forest = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
outlier_pred = iso_forest.fit_predict(df_work)
clean_mask = outlier_pred == 1

print(f"   Outliers detected: {(outlier_pred == -1).sum():,} ({(~clean_mask).sum()/len(df_work)*100:.2f}%)")
df_work = df_work[clean_mask].copy()
print(f"   ✅ Clean dataset: {len(df_work):,} records")

# ==================== STEP 4: FEATURE SCALING ====================
print("\n📏 STEP 4: Feature Scaling & Normalization")
print("-" * 100)

# Use RobustScaler for better handling of outliers
scaler = RobustScaler()
X_scaled = scaler.fit_transform(df_work)

print(f"   Scaling method: RobustScaler (robust to outliers)")
print(f"   Scaled data shape: {X_scaled.shape}")
print(f"   Mean ≈ {X_scaled.mean():.4f}, Std ≈ {X_scaled.std():.4f}")

# ==================== STEP 5: OPTIMAL CLUSTER FINDING ====================
print("\n🔍 STEP 5: Hyperparameter Optimization (GridSearch)")
print("-" * 100)

# Grid search for optimal GMM parameters
param_grid = {
    'n_components': range(2, 9),
    'covariance_type': ['full', 'tied', 'diag', 'spherical'],
}

best_bic = np.inf
best_aic = np.inf
best_params = None
results = []

print("   Testing configurations...")
for n_comp in param_grid['n_components']:
    for cov_type in param_grid['covariance_type']:
        try:
            gmm = GaussianMixture(
                n_components=n_comp, 
                covariance_type=cov_type, 
                tol=1e-3,
                random_state=42,
                n_init=10
            )
            gmm.fit(X_scaled)
            bic_score = gmm.bic(X_scaled)
            aic_score = gmm.aic(X_scaled)
            
            results.append({
                'n_components': n_comp,
                'covariance_type': cov_type,
                'BIC': bic_score,
                'AIC': aic_score
            })
            
            if bic_score < best_bic:
                best_bic = bic_score
                best_params = {'n_components': n_comp, 'covariance_type': cov_type}
        except Exception as e:
            continue

results_df = pd.DataFrame(results)
print(f"\n   ✅ Tested {len(results)} configurations")
print(f"\n   📊 Best Parameters (by BIC):")
print(f"      • n_components: {best_params['n_components']}")
print(f"      • covariance_type: {best_params['covariance_type']}")
print(f"      • BIC Score: {best_bic:,.0f}")

# Show top 5 configurations
print(f"\n   Top 5 configurations by BIC:")
top_5 = results_df.nsmallest(5, 'BIC')[['n_components', 'covariance_type', 'BIC', 'AIC']]
for idx, row in top_5.iterrows():
    print(f"      {idx+1}. n_comp={int(row['n_components'])}, cov={row['covariance_type']}, BIC={row['BIC']:,.0f}")

# ==================== STEP 6: FINAL GMM MODEL ====================
print("\n⚙️  STEP 6: Fitting Optimized GMM Model")
print("-" * 100)

gmm_final = GaussianMixture(**best_params, random_state=42, n_init=20)
cluster_labels = gmm_final.fit_predict(X_scaled)

print(f"   ✅ GMM model fitted successfully")
print(f"   Clusters identified: {len(np.unique(cluster_labels))}")

# ==================== STEP 7: CLUSTERING QUALITY METRICS ====================
print("\n📊 STEP 7: Clustering Quality Evaluation")
print("-" * 100)

if len(np.unique(cluster_labels)) > 1:
    # Silhouette score (higher is better, range: -1 to 1)
    sil_score = silhouette_score(X_scaled, cluster_labels)
    print(f"   🔹 Silhouette Score: {sil_score:.4f}")
    if sil_score > 0.5:
        print(f"      → Excellent clustering quality ✅")
    elif sil_score > 0.3:
        print(f"      → Good clustering quality")
    else:
        print(f"      → Weak clustering structure")
    
    # Davies-Bouldin Index (lower is better)
    db_score = davies_bouldin_score(X_scaled, cluster_labels)
    print(f"   🔹 Davies-Bouldin Index: {db_score:.4f}")
    if db_score < 1.0:
        print(f"      → Good cluster separation ✅")
    
    # Inertia and Log-Likelihood
    print(f"   🔹 Log-Likelihood: {gmm_final.score(X_scaled):.2f}")
    print(f"   🔹 Weights: {np.round(gmm_final.weights_, 3)}")

# ==================== STEP 8: CLUSTER ANALYSIS ====================
print("\n🔬 STEP 8: Detailed Cluster Analysis")
print("-" * 100)

df_work['cluster'] = cluster_labels

for cluster_id in sorted(np.unique(cluster_labels)):
    cluster_data = df_work[df_work['cluster'] == cluster_id]
    cluster_weight = gmm_final.weights_[cluster_id]
    
    print(f"\n   📍 CLUSTER {cluster_id}:")
    print(f"      • Size: {len(cluster_data):,} samples ({cluster_weight*100:.1f}% of data)")
    print(f"      • Features statistics:")
    
    for feature in key_features[:5]:  # Show first 5 features
        mean_val = cluster_data[feature].mean()
        std_val = cluster_data[feature].std()
        print(f"         - {feature}: {mean_val:.4f} ± {std_val:.4f}")

# ==================== STEP 9: VISUALIZATION ====================
print("\n📈 STEP 9: Generating Visualizations")
print("-" * 100)

# Create output directory
import os
os.makedirs('09a_advanced_ml/results', exist_ok=True)

# 1. PCA Visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# PCA plot
scatter = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6, s=20)
axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
axes[0].set_title('GMM Clusters - PCA Visualization')
plt.colorbar(scatter, ax=axes[0], label='Cluster')

# Cluster sizes
cluster_sizes = pd.Series(cluster_labels).value_counts().sort_index()
axes[1].bar(cluster_sizes.index, cluster_sizes.values, color=plt.cm.viridis(np.linspace(0, 1, len(cluster_sizes))))
axes[1].set_xlabel('Cluster ID')
axes[1].set_ylabel('Number of Samples')
axes[1].set_title('Cluster Size Distribution')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('09a_advanced_ml/results/01_gmm_clusters_pca.png', dpi=300, bbox_inches='tight')
print("   ✅ Saved: 01_gmm_clusters_pca.png")
plt.close()

# 2. BIC/AIC Comparison
fig, ax = plt.subplots(figsize=(12, 5))
pivot_data = results_df.pivot_table(values='BIC', index='n_components', columns='covariance_type')
pivot_data.plot(ax=ax, marker='o', linewidth=2)
ax.set_xlabel('Number of Components')
ax.set_ylabel('BIC Score')
ax.set_title('GMM Hyperparameter Optimization - BIC Scores')
ax.grid(alpha=0.3)
plt.legend(title='Covariance Type', loc='best')
plt.tight_layout()
plt.savefig('09a_advanced_ml/results/02_gmm_bic_optimization.png', dpi=300, bbox_inches='tight')
print("   ✅ Saved: 02_gmm_bic_optimization.png")
plt.close()

# 3. Feature importance by cluster
fig, axes = plt.subplots(len(key_features), 1, figsize=(12, len(key_features)*2.5))
if len(key_features) == 1:
    axes = [axes]

for idx, feature in enumerate(key_features):
    cluster_means = df_work.groupby('cluster')[feature].mean()
    axes[idx].bar(cluster_means.index, cluster_means.values, color=plt.cm.viridis(np.linspace(0, 1, len(cluster_means))))
    axes[idx].set_ylabel(feature)
    axes[idx].set_xlabel('Cluster ID')
    axes[idx].set_title(f'{feature} by Cluster')
    axes[idx].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('09a_advanced_ml/results/03_feature_by_cluster.png', dpi=300, bbox_inches='tight')
print("   ✅ Saved: 03_feature_by_cluster.png")
plt.close()

# ==================== STEP 10: SUMMARY REPORT ====================
print("\n" + "="*100)
print("📋 FINAL SUMMARY REPORT")
print("="*100)

summary = {
    'Total Records Analyzed': f"{len(df_work):,}",
    'Features Used': len(key_features),
    'Feature List': ', '.join(key_features),
    'Optimal Clusters': best_params['n_components'],
    'Covariance Type': best_params['covariance_type'],
    'BIC Score': f"{best_bic:,.0f}",
    'Silhouette Score': f"{sil_score:.4f}" if len(np.unique(cluster_labels)) > 1 else "N/A",
    'Data Retention': f"{len(df_work)/len(df_clean)*100:.1f}%",
}

for key, value in summary.items():
    print(f"   {key:.<40} {value}")

print("\n📁 Output files saved to: 09a_advanced_ml/results/")
print("   ✅ 01_gmm_clusters_pca.png")
print("   ✅ 02_gmm_bic_optimization.png") 
print("   ✅ 03_feature_by_cluster.png")

# Save detailed results
results_df.to_csv('09a_advanced_ml/results/gmm_optimization_results.csv', index=False)
df_work.to_csv('09a_advanced_ml/results/clustered_data.csv', index=False)
print("   ✅ gmm_optimization_results.csv")
print("   ✅ clustered_data.csv")

print("\n" + "="*100)
print("✅ GMM ANALYSIS COMPLETE!")
print("="*100 + "\n")
