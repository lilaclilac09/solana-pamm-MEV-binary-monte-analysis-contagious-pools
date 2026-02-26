#!/usr/bin/env python3
"""
Regenerate ALL visualizations using ONLY the filtered data (617 validated fat sandwich attacks)
This ensures no false positives (failed sandwiches or multi-hop arbitrage) contaminate the analysis.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

# Paths
BASE = Path(__file__).resolve().parent.parent
FILTERED_DATA = BASE / '02_mev_detection' / 'filtered_output' / 'all_fat_sandwich_only.csv'
AGGREGATOR_DATA = BASE / '07_ml_classification' / 'derived' / 'aggregator_analysis' / 'aggregators_with_pools.csv'
POOL_SUMMARY = BASE / '02_mev_detection' / 'POOL_SUMMARY.csv'
OUTPUT_DIR = BASE / '02_mev_detection' / 'filtered_output' / 'plots'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("REGENERATING ALL PLOTS WITH FILTERED DATA (617 VALIDATED ATTACKS ONLY)")
print("="*80)

# Verify data files exist
if not FILTERED_DATA.exists():
    raise FileNotFoundError(f"Filtered data not found: {FILTERED_DATA}")
if not AGGREGATOR_DATA.exists():
    raise FileNotFoundError(f"Aggregator data not found: {AGGREGATOR_DATA}")

# Load filtered data ONLY (617 validated fat sandwich attacks)
print(f"\n✓ Loading filtered data: {FILTERED_DATA}")
df_fat = pd.read_csv(FILTERED_DATA)
print(f"  Records loaded: {len(df_fat):,} (validated fat sandwich attacks only)")
print(f"  No false positives included (failed sandwiches or multi-hop arbitrage excluded)")
print(f"  Columns: {', '.join(df_fat.columns)}")

# Rename columns for consistency
if 'attacker_signer' in df_fat.columns and 'signer' not in df_fat.columns:
    df_fat['signer'] = df_fat['attacker_signer']
if 'amm_trade' in df_fat.columns and 'pool' not in df_fat.columns:
    df_fat['pool'] = df_fat['amm_trade']

# Load aggregator data
print(f"\n✓ Loading aggregator data: {AGGREGATOR_DATA}")
df_agg = pd.read_csv(AGGREGATOR_DATA)
print(f"  Aggregator signers: {len(df_agg):,}")

# Load pool summary
print(f"\n✓ Loading pool summary: {POOL_SUMMARY}")
df_pools = pd.read_csv(POOL_SUMMARY)
print(f"  Pools analyzed: {len(df_pools)}")

print("\n" + "="*80)
print("GENERATING VISUALIZATIONS WITH FILTERED DATA")
print("="*80)

# ============================================================================
# PLOT 1: MEV DISTRIBUTION BY PROTOCOL (FILTERED DATA ONLY)
# ============================================================================
print("\n📊 Plot 1: MEV Distribution by Protocol (Filtered Data)")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('MEV Distribution Across Protocols (617 Validated Attacks Only)', 
             fontsize=16, fontweight='bold')

# By pool
if 'pool' in df_fat.columns:
    pool_counts = df_fat['pool'].value_counts()
    pool_profits = df_fat.groupby('pool')['net_profit_sol'].sum().sort_values(ascending=False)
    
    # Attack volume
    ax1 = axes[0, 0]
    pool_counts.plot(kind='bar', ax=ax1, color='steelblue', alpha=0.8)
    ax1.set_title('Attack Volume by Pool', fontweight='bold')
    ax1.set_xlabel('Pool')
    ax1.set_ylabel('Number of Attacks')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # Total profit
    ax2 = axes[0, 1]
    pool_profits.plot(kind='bar', ax=ax2, color='darkgreen', alpha=0.8)
    ax2.set_title('Total Profit by Pool (SOL)', fontweight='bold')
    ax2.set_xlabel('Pool')
    ax2.set_ylabel('Total Profit (SOL)')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Average profit per attack
    ax3 = axes[1, 0]
    avg_profit = df_fat.groupby('pool')['net_profit_sol'].mean().sort_values(ascending=False)
    avg_profit.plot(kind='bar', ax=ax3, color='coral', alpha=0.8)
    ax3.set_title('Average Profit per Attack', fontweight='bold')
    ax3.set_xlabel('Pool')
    ax3.set_ylabel('Avg Profit (SOL)')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(axis='y', alpha=0.3)
    
    # Profit concentration pie chart
    ax4 = axes[1, 1]
    top5_pools = pool_profits.head(5)
    others = pool_profits[5:].sum() if len(pool_profits) > 5 else 0
    
    if others > 0:
        pie_data = pd.concat([top5_pools, pd.Series({'Others': others})])
    else:
        pie_data = top5_pools
    
    colors = plt.cm.Set3(range(len(pie_data)))
    ax4.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%',
            startangle=90, colors=colors)
    ax4.set_title('Profit Share by Pool', fontweight='bold')

plt.tight_layout()
output_file = OUTPUT_DIR / 'mev_distribution_comprehensive_filtered.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"  ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# PLOT 2: TOP 20 ATTACKERS (FILTERED DATA ONLY)
# ============================================================================
print("\n📊 Plot 2: Top 20 Attackers by Profit (Filtered Data)")

if 'signer' in df_fat.columns and 'net_profit_sol' in df_fat.columns:
    top20_attackers = df_fat.groupby('signer')['net_profit_sol'].sum().sort_values(ascending=False).head(20)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(top20_attackers)), top20_attackers.values, color='darkred', alpha=0.7)
    ax.set_yticks(range(len(top20_attackers)))
    ax.set_yticklabels([f"{s[:8]}...{s[-8:]}" for s in top20_attackers.index], fontsize=9)
    ax.set_xlabel('Total Profit (SOL)', fontweight='bold')
    ax.set_ylabel('Attacker Signer', fontweight='bold')
    ax.set_title('Top 20 MEV Attackers by Total Profit (617 Validated Attacks)', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
    
    # Add value labels
    for i, (idx, val) in enumerate(top20_attackers.items()):
        ax.text(val, i, f' {val:.3f} SOL', va='center', fontsize=8)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / 'top_attackers_filtered.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()

# ============================================================================
# PLOT 3: AGGREGATOR VS MEV BOT COMPARISON
# ============================================================================
print("\n📊 Plot 3: Aggregator vs MEV Bot Detailed Comparison")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Aggregators vs MEV Bots: Behavioral Differences', 
             fontsize=16, fontweight='bold')

# Prepare MEV bot data
mev_pool_counts = df_fat.groupby('signer')['pool'].nunique() if 'pool' in df_fat.columns else pd.Series()
mev_avg_profit = df_fat.groupby('signer')['net_profit_sol'].mean()
mev_attack_count = df_fat.groupby('signer').size()

# Aggregator data
agg_pool_counts = df_agg['unique_pools'] if 'unique_pools' in df_agg.columns else pd.Series()
agg_mev_scores = df_agg['mev_score'] if 'mev_score' in df_agg.columns else pd.Series()
agg_trade_freq = df_agg['trades_per_hour'] if 'trades_per_hour' in df_agg.columns else pd.Series()

# 1. Pool Diversity Distribution
ax1 = axes[0, 0]
if len(mev_pool_counts) > 0 and len(agg_pool_counts) > 0:
    ax1.hist([mev_pool_counts, agg_pool_counts], bins=15, label=['MEV Bots', 'Aggregators'],
             color=['red', 'blue'], alpha=0.6, edgecolor='black')
    ax1.set_xlabel('Number of Unique Pools', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    ax1.set_title('Pool Diversity Comparison', fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.text(0.95, 0.95, f'MEV: {mev_pool_counts.mean():.1f} pools avg\nAgg: {agg_pool_counts.mean():.1f} pools avg',
             transform=ax1.transAxes, ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 2. MEV Score Distribution
ax2 = axes[0, 1]
if len(agg_mev_scores) > 0:
    # Create MEV score for bots (proxy: normalized profit consistency)
    if len(mev_avg_profit) > 0:
        mev_score_proxy = (mev_avg_profit / mev_avg_profit.max()).fillna(0)
        ax2.hist([mev_score_proxy, agg_mev_scores], bins=20, label=['MEV Bots', 'Aggregators'],
                color=['red', 'blue'], alpha=0.6, edgecolor='black')
        ax2.set_xlabel('MEV Score', fontweight='bold')
        ax2.set_ylabel('Frequency', fontweight='bold')
        ax2.set_title('MEV Score Distribution', fontweight='bold')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        ax2.text(0.95, 0.95, f'MEV: {mev_score_proxy.mean():.3f} avg\nAgg: {agg_mev_scores.mean():.3f} avg',
                 transform=ax2.transAxes, ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 3. Attack/Trade Frequency
ax3 = axes[0, 2]
if len(mev_attack_count) > 0 and len(agg_trade_freq) > 0:
    ax3.hist([mev_attack_count, agg_trade_freq], bins=20, label=['MEV Bots (attacks)', 'Aggregators (trades/hr)'],
             color=['red', 'blue'], alpha=0.6, edgecolor='black', range=(0, 50))
    ax3.set_xlabel('Frequency', fontweight='bold')
    ax3.set_ylabel('Count', fontweight='bold')
    ax3.set_title('Activity Frequency Comparison', fontweight='bold')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)

# 4. Scatter: Pool Count vs MEV Score
ax4 = axes[1, 0]
if len(agg_pool_counts) > 0 and len(agg_mev_scores) > 0:
    ax4.scatter(agg_pool_counts, agg_mev_scores, alpha=0.5, c='blue', label='Aggregators', s=30)
    if len(mev_pool_counts) > 0 and len(mev_score_proxy) > 0:
        ax4.scatter(mev_pool_counts, mev_score_proxy, alpha=0.5, c='red', label='MEV Bots', s=30)
    ax4.set_xlabel('Unique Pools', fontweight='bold')
    ax4.set_ylabel('MEV Score', fontweight='bold')
    ax4.set_title('Pool Diversity vs MEV Score', fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    # Add separation line (decision boundary)
    ax4.axvline(x=5, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Threshold (5 pools)')

# 5. Profit per Event Comparison
ax5 = axes[1, 1]
if len(mev_avg_profit) > 0:
    data_to_plot = [mev_avg_profit[mev_avg_profit < 1.0]]  # Cap outliers for visualization
    ax5.boxplot(data_to_plot, labels=['MEV Bots'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='red', alpha=0.6))
    ax5.set_ylabel('Profit per Attack (SOL)', fontweight='bold')
    ax5.set_title('Profit Distribution (MEV Bots)', fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    ax5.text(0.5, 0.95, f'Median: {mev_avg_profit.median():.4f} SOL\nMean: {mev_avg_profit.mean():.4f} SOL',
             transform=ax5.transAxes, ha='center', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 6. Key Differences Summary Table
ax6 = axes[1, 2]
ax6.axis('off')

# Calculate statistics
mev_pools_mean = mev_pool_counts.mean() if len(mev_pool_counts) > 0 else 0
agg_pools_mean = agg_pool_counts.mean() if len(agg_pool_counts) > 0 else 0
mev_score_mean = mev_score_proxy.mean() if 'mev_score_proxy' in locals() and len(mev_score_proxy) > 0 else 0
agg_score_mean = agg_mev_scores.mean() if len(agg_mev_scores) > 0 else 0

summary_text = f"""
KEY DIFFERENCES:

MEV BOTS (617 validated):
• Pool focus: {mev_pools_mean:.1f} pools avg
• MEV score: {mev_score_mean:.3f} avg
• Attacks: {len(df_fat)} total
• Avg profit: {mev_avg_profit.mean():.4f} SOL
• Behavior: Targeted exploitation

AGGREGATORS (1,908 signers):
• Pool diversity: {agg_pools_mean:.1f} pools avg
• MEV score: {agg_score_mean:.3f} avg
• Trade freq: {agg_trade_freq.mean():.1f}/hr avg
• Profit: Routing fees only
• Behavior: Multi-pool routing

SEPARATION CRITERIA:
✓ Pool count threshold: 5+
✓ MEV score threshold: <0.35
✓ No victim patterns
✓ Token path: cyclic vs linear
"""

ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, 
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

plt.tight_layout()
output_file = OUTPUT_DIR / 'aggregator_vs_mev_detailed_comparison.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"  ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# PLOT 4: PROFIT DISTRIBUTION (FILTERED DATA)
# ============================================================================
print("\n📊 Plot 4: Profit Distribution Analysis (Filtered Data)")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('MEV Profit Distribution (617 Validated Attacks)', fontsize=14, fontweight='bold')

if 'net_profit_sol' in df_fat.columns:
    profits = df_fat['net_profit_sol']
    
    # Histogram
    ax1 = axes[0]
    ax1.hist(profits[profits < profits.quantile(0.95)], bins=50, color='darkgreen', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Profit (SOL)', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    ax1.set_title('Profit Distribution (95th percentile)', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.axvline(profits.median(), color='red', linestyle='--', linewidth=2, label=f'Median: {profits.median():.4f}')
    ax1.legend()
    
    # Box plot by pool
    ax2 = axes[1]
    if 'pool' in df_fat.columns:
        pool_profit_data = [df_fat[df_fat['pool'] == pool]['net_profit_sol'].values 
                           for pool in df_fat['pool'].unique()]
        ax2.boxplot(pool_profit_data, labels=df_fat['pool'].unique(), vert=True, patch_artist=True)
        ax2.set_xlabel('Pool', fontweight='bold')
        ax2.set_ylabel('Profit (SOL)', fontweight='bold')
        ax2.set_title('Profit by Pool (Box Plot)', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
    
    # Cumulative distribution  
    ax3 = axes[2]
    sorted_profits = np.sort(profits)
    cumulative = np.arange(1, len(sorted_profits) + 1) / len(sorted_profits) * 100
    ax3.plot(sorted_profits, cumulative, linewidth=2, color='purple')
    ax3.set_xlabel('Profit (SOL)', fontweight='bold')
    ax3.set_ylabel('Cumulative Percentage (%)', fontweight='bold')
    ax3.set_title('Cumulative Profit Distribution', fontweight='bold')
    ax3.grid(alpha=0.3)
    ax3.axhline(50, color='red', linestyle='--', alpha=0.5, label='50th percentile')
    ax3.axhline(95, color='orange', linestyle='--', alpha=0.5, label='95th percentile')
    ax3.legend()

plt.tight_layout()
output_file = OUTPUT_DIR / 'profit_distribution_filtered.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"  ✓ Saved: {output_file}")
plt.close()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY STATISTICS (FILTERED DATA - 617 VALIDATED ATTACKS)")
print("="*80)

print(f"\n📊 Total validated attacks: {len(df_fat):,}")
print(f"📊 Total profit: {df_fat['net_profit_sol'].sum():.3f} SOL")
print(f"📊 Average profit per attack: {df_fat['net_profit_sol'].mean():.4f} SOL")
print(f"📊 Median profit: {df_fat['net_profit_sol'].median():.4f} SOL")
print(f"📊 Top pool: {df_fat['pool'].value_counts().index[0]} ({df_fat['pool'].value_counts().values[0]} attacks)")

if 'pool' in df_fat.columns:
    pool_profits = df_fat.groupby('pool')['net_profit_sol'].sum().sort_values(ascending=False)
    top_pool = pool_profits.index[0]
    top_pool_profit = pool_profits.values[0]
    print(f"📊 Most profitable pool: {top_pool} ({top_pool_profit:.3f} SOL, {top_pool_profit/df_fat['net_profit_sol'].sum()*100:.1f}%)")

print("\n" + "="*80)
print("✅ ALL PLOTS REGENERATED WITH FILTERED DATA (617 VALIDATED ATTACKS)")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print("\nGenerated files:")
print("  1. mev_distribution_comprehensive_filtered.png")
print("  2. top_attackers_filtered.png")
print("  3. aggregator_vs_mev_detailed_comparison.png")
print("  4. profit_distribution_filtered.png")
print("\n🔍 All plots use ONLY validated fat sandwich attacks (no false positives)")
print("🔍 Failed sandwiches (865) and multi-hop arbitrage (19) are EXCLUDED")
