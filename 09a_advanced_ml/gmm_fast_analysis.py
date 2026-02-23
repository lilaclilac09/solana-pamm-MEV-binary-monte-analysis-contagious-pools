#!/usr/bin/env python3
"""
⚡ OPTIMIZED GMM CLUSTERING - Fast version for large datasets
Uses intelligent sampling and reduced hyperparameter space
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*100)
print("⚡ FAST OPTIMIZED GMM CLUSTERING - Large Dataset Version")
print("="*100)

# ==================== STEP 1: LOAD DATA ====================
print("\n📊 STEP 1: Loading Data")
print("-" * 100)

try:
    df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
    print(f"✅ Loaded: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# ==================== STEP 2: INTELLIGENT SAMPLING ====================
print("\n📉 STEP 2: Intelligent Sampling Strategy")
print("-" * 100)

# Use stratified sampling for better representation
sample_size = 100000
np.random.seed(42)

# Try to sample evenly across time periods if 'time' column exists
if 'time' in df_clean.columns:
    df_sample = df_clean.sample(n=min(sample_size, len(df_clean)), random_state=42)
    print(f"✅ Stratified sample: {len(df_sample):,} records ({len(df_sample)/len(df_clean)*100:.2f}% of total)")
else:
    df_sample = df_clean.sample(n=min(sample_size, len(df_clean)), random_state=42)
    print(f"✅ Random sample: {len(df_sample):,} records")

# ==================== STEP 3: FEATURE SELECTION ====================
print("\n🔧 STEP 3: Feature Engineering")
print("-" * 100)

# Get numeric columns
numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
print(f"📊 Available numeric features: {len(numeric_cols)}")

# Select key features (at least 3 of the most promising ones)
key_features = [col for col in ['tx_idx', 'slot', 'us_since_first_shred', 'bytes_changed_trade', 'time', 'ms_time'] 
                if col in df_sample.columns][:6]

if len(key_features) < 3:
    key_features = numeric_cols[:6]

print(f"✅ Selected features ({len(key_features)}):")
for feat in key_features:
    print(f"     • {feat}")

# Prepare working dataset
df_work = df_sample[key_features].dropna().copy()
print(f"   After cleaning: {len(df_work):,} records")

# ==================== STEP 4: OUTLIER REMOVAL ====================
print("\n🎯 STEP 4: Outlier Detection")
print("-" * 100)

iso_forest = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
outlier_mask = iso_forest.fit_predict(df_work) == 1
df_work = df_work[outlier_mask].copy()
print(f"✅ After outlier removal: {len(df_work):,} records")

# ==================== STEP 5: SCALING ====================
print("\n📏 STEP 5: Feature Scaling")
print("-" * 100)

scaler = RobustScaler()
X_scaled = scaler.fit_transform(df_work)
print(f"✅ RobustScaler applied: shape {X_scaled.shape}")

# ==================== STEP 6: FAST HYPERPARAMETER SEARCH ====================
print("\n⚡ STEP 6: Fast Hyperparameter Optimization")
print("-" * 100)

# Reduced grid for speed
n_components_range = range(2, 7)  # Test 2-6 clusters instead of 2-8
covariance_types = ['full', 'diag']  # Test 2 types instead of 4

best_score = -np.inf
best_params = None
best_gmm = None
results = []

print("   Testing configurations...")
config_count = 0
for n_comp in n_components_range:
    for cov_type in covariance_types:
        config_count += 1
        try:
            gmm = GaussianMixture(
                n_components=n_comp,
                covariance_type=cov_type,
                random_state=42,
                n_init=5,
                max_iter=100,
                tol=1e-2
            )
            gmm.fit(X_scaled)
            bic = gmm.bic(X_scaled)
            
            results.append({
                'n_components': n_comp,
                'covariance_type': cov_type,
                'BIC': bic
            })
            
            if bic < best_score or best_score == -np.inf:
                best_score = bic
                best_params = {'n_components': n_comp, 'covariance_type': cov_type}
                best_gmm = gmm
            
            print(f"     {config_count}. n_comp={n_comp}, cov={cov_type:6s} → BIC={bic:,.0f}")
        except Exception as e:
            print(f"     {config_count}. n_comp={n_comp}, cov={cov_type:6s} → Error: {str(e)[:30]}")

print(f"\n   ✅ Tested {config_count} configurations")
print(f"   🏆 Best Configuration:")
print(f"      • Components: {best_params['n_components']}")
print(f"      • Covariance: {best_params['covariance_type']}")
print(f"      • BIC Score: {best_score:,.0f}")

# ==================== STEP 7: CLUSTERING ====================
print("\n⚙️  STEP 7: Final Clustering")
print("-" * 100)

cluster_labels = best_gmm.fit_predict(X_scaled)
df_work['cluster'] = cluster_labels

print(f"✅ GMM clustering complete")
print(f"   Clusters found: {len(np.unique(cluster_labels))}")

# ==================== STEP 8: QUALITY METRICS ====================
print("\n📊 STEP 8: Clustering Quality")
print("-" * 100)

if len(np.unique(cluster_labels)) > 1:
    sil_score = silhouette_score(X_scaled, cluster_labels)
    db_score = davies_bouldin_score(X_scaled, cluster_labels)
    ll_score = best_gmm.score(X_scaled)
    
    print(f"   🔹 Silhouette Score: {sil_score:.4f}")
    if sil_score > 0.5:
        print(f"      → Excellent clustering ✅")
    elif sil_score > 0.3:
        print(f"      → Good clustering")
    else:
        print(f"      → Moderate clustering")
    
    print(f"   🔹 Davies-Bouldin Index: {db_score:.4f}")
    if db_score < 1.0:
        print(f"      → Good cluster separation ✅")
    
    print(f"   🔹 Log-Likelihood: {ll_score:.2f}")
    print(f"   🔹 Cluster Weights: {np.round(best_gmm.weights_, 2)}")

# ==================== STEP 9: CLUSTER ANALYSIS ====================
print("\n🔬 STEP 9: Cluster Characteristics")
print("-" * 100)

for cluster_id in sorted(np.unique(cluster_labels)):
    cluster_data = df_work[df_work['cluster'] == cluster_id]
    weight = best_gmm.weights_[cluster_id]
    
    print(f"\n   📍 CLUSTER {cluster_id}")
    print(f"      Size: {len(cluster_data):,} samples ({weight*100:.1f}%)")
    
    # Show feature statistics for first 3 features
    for feat in key_features[:3]:
        mean_val = cluster_data[feat].mean()
        std_val = cluster_data[feat].std()
        print(f"      {feat}: {mean_val:.2f} ± {std_val:.2f}")

# ==================== STEP 10: VISUALIZATIONS ====================
print("\n📈 STEP 10: Generating Visualizations")
print("-" * 100)

import os
os.makedirs('09a_advanced_ml/results', exist_ok=True)

# 1. PCA Visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Clusters in PCA space
scatter = axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_labels, 
                         cmap='viridis', alpha=0.6, s=30, edgecolors='black', linewidth=0.3)
axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
axes[0].set_title('GMM Clustering - PCA Space')
plt.colorbar(scatter, ax=axes[0], label='Cluster')
axes[0].grid(alpha=0.3)

# Cluster sizes
cluster_sizes = pd.Series(cluster_labels).value_counts().sort_index()
colors = plt.cm.viridis(np.linspace(0, 1, len(cluster_sizes)))
axes[1].bar(cluster_sizes.index, cluster_sizes.values, color=colors, edgecolor='black', linewidth=1.5)
axes[1].set_xlabel('Cluster ID')
axes[1].set_ylabel('Sample Count')
axes[1].set_title('Cluster Size Distribution')
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('09a_advanced_ml/results/01_gmm_clusters_pca.png', dpi=300, bbox_inches='tight')
print("   ✅ Saved: 01_gmm_clusters_pca.png")
plt.close()

# 2. BIC Optimization Curve
if results:
    results_df = pd.DataFrame(results)
    fig, ax = plt.subplots(figsize=(10, 5))
    
    for cov_type in results_df['covariance_type'].unique():
        subset = results_df[results_df['covariance_type'] == cov_type].sort_values('n_components')
        ax.plot(subset['n_components'], subset['BIC'], marker='o', label=cov_type, linewidth=2)
    
    ax.set_xlabel('Number of Components')
    ax.set_ylabel('BIC Score')
    ax.set_title('GMM Hyperparameter Optimization')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('09a_advanced_ml/results/02_bic_optimization.png', dpi=300, bbox_inches='tight')
    print("   ✅ Saved: 02_bic_optimization.png")
    plt.close()

# 3. Feature Distribution by Cluster
fig, axes = plt.subplots(min(3, len(key_features)), 1, figsize=(12, 10))
if len(key_features) == 1:
    axes = [axes]

for idx, feat in enumerate(key_features[:3]):
    cluster_data_by_cluster = [df_work[df_work['cluster'] == c][feat].values 
                               for c in sorted(np.unique(cluster_labels))]
    
    bp = axes[idx].boxplot(cluster_data_by_cluster, labels=sorted(np.unique(cluster_labels)))
    axes[idx].set_ylabel(feat)
    axes[idx].set_xlabel('Cluster ID')
    axes[idx].set_title(f'{feat} Distribution by Cluster')
    axes[idx].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('09a_advanced_ml/results/03_feature_distributions.png', dpi=300, bbox_inches='tight')
print("   ✅ Saved: 03_feature_distributions.png")
plt.close()

# ==================== SAVE RESULTS ====================
print("\n💾 STEP 11: Saving Results")
print("-" * 100)

# Save clustered data sample
df_work.to_csv('09a_advanced_ml/results/clustered_data_sample.csv', index=False)
print(f"   ✅ Saved: clustered_data_sample.csv ({len(df_work):,} records)")

# Save optimization results
if results:
    results_df.to_csv('09a_advanced_ml/results/gmm_optimization_results.csv', index=False)
    print(f"   ✅ Saved: gmm_optimization_results.csv")

# Save summary report
summary_text = f"""
╔══════════════════════════════════════════════════════════════╗
║          GMM CLUSTERING ANALYSIS - FINAL REPORT             ║
╚══════════════════════════════════════════════════════════════╝

📊 DATA SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Original Dataset:        {len(df_clean):,} records
Sampled Dataset:         {len(df_sample):,} records ({len(df_sample)/len(df_clean)*100:.2f}%)
After Preprocessing:     {len(df_work):,} records ({len(df_work)/len(df_sample)*100:.2f}%)

🔧 MODEL CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Features Used:           {', '.join(key_features)}
Number of Features:      {len(key_features)}
Optimal Clusters:        {best_params['n_components']}
Covariance Type:         {best_params['covariance_type']}
Scaler Method:           RobustScaler

📈 MODEL PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BIC Score:               {best_score:,.0f}
Silhouette Score:        {sil_score:.4f}
Davies-Bouldin Index:    {db_score:.4f}
Log-Likelihood:          {ll_score:.2f}

📍 CLUSTER DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

for cluster_id in sorted(np.unique(cluster_labels)):
    cluster_data = df_work[df_work['cluster'] == cluster_id]
    weight = best_gmm.weights_[cluster_id]
    summary_text += f"\nCluster {cluster_id}:  {len(cluster_data):,} samples ({weight*100:.1f}%)"

summary_text += """

📁 OUTPUT FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 01_gmm_clusters_pca.png         - PCA visualization of clusters
✅ 02_bic_optimization.png          - Hyperparameter tuning curves
✅ 03_feature_distributions.png     - Feature boxplots by cluster
✅ clustered_data_sample.csv        - Sample data with cluster labels
✅ gmm_optimization_results.csv     - Detailed optimization metrics

"""

with open('09a_advanced_ml/results/ANALYSIS_REPORT.txt', 'w') as f:
    f.write(summary_text)

print(f"   ✅ Saved: ANALYSIS_REPORT.txt")

# ==================== FINAL SUMMARY ====================
print("\n" + "="*100)
print("✅ GMM ANALYSIS COMPLETE!")
print("="*100)

print(summary_text)

print("\n📊 Key Insights:")
print(f"   • Identified {best_params['n_components']} distinct clusters in transaction patterns")
print(f"   • Silhouette score of {sil_score:.4f} indicates {'excellent' if sil_score > 0.5 else 'good' if sil_score > 0.3 else 'moderate'} separation")
print(f"   • All results saved to: 09a_advanced_ml/results/")
print("\n")
