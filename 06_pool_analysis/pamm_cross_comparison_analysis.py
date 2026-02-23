#!/usr/bin/env python3
"""
PAMM Pool Cross-Comparison Analysis
Oracle Latency, Vulnerabilities & MEV Exposure Analysis

Generates:
- Tables: Oracle latency, Trade latency, Vulnerability scores, MEV risk
- Charts: Bar charts and scatter plots for comprehensive pool comparison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SETUP
# ============================================================================

print("\n" + "="*80)
print("PAMM POOL CROSS-COMPARISON ANALYSIS")
print("Oracle Latency, Vulnerabilities & MEV Exposure")
print("="*80)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 6)

# Paths
base_path = Path('../')
data_path = base_path / '01_data_cleaning/outputs/pamm_clean_final.parquet'
mev_path = base_path / '02_mev_detection/per_pamm_all_mev_with_validator.csv'

output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n📂 Loading data...")
if not data_path.exists():
    print(f"❌ Data file not found: {data_path}")
    exit(1)

# Sample data for analysis (load 50% of first records for efficiency)
print(f"Loading transaction data...")
df = pd.read_parquet(data_path, engine='pyarrow')
print(f"✓ Main data: {len(df):,} records, {df.shape[1]} columns")

# Focus on MEV-relevant data (where is_pool_trade=True)
df_pool_trades = df[df['is_pool_trade'] == True].copy()
print(f"✓ Pool trades (is_pool_trade=True): {len(df_pool_trades):,} records")

if mev_path.exists():
    mev_df = pd.read_csv(mev_path)
    print(f"✓ MEV data: {len(mev_df):,} records, {mev_df.shape[1]} columns")
else:
    mev_df = pd.DataFrame()
    print(f"⚠ MEV data not found: {mev_path}")

# ============================================================================
# 2. EXTRACT TRADES AND ORACLE DATA
# ============================================================================

print("\n📊 Extracting trades and oracle data...")

# Convert time to datetime
if 'datetime' in df.columns:
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

# Extract trades
trades_list = []
oracle_list = []

for idx, row in df.iterrows():
    # Extract trades
    try:
        trades = row.get('trades')
        if pd.notna(trades) and trades is not None and len(trades) > 0:
            trades_list_row = trades if isinstance(trades, list) else [trades]
            for trade in trades_list_row:
                if isinstance(trade, dict):
                    trade_record = {
                        'slot': row['slot'],
                        'time': row['time'],
                        'datetime': row.get('datetime'),
                        'validator': row['validator'],
                        'signer': row['signer'],
                        'pool': trade.get('pool'),
                        'token_pair': trade.get('token_pair'),
                        'amount_in': trade.get('amount_in'),
                        'amount_out': trade.get('amount_out'),
                        'us_since_first_shred': row.get('us_since_first_shred')
                    }
                    trades_list.append(trade_record)
    except (TypeError, ValueError):
        pass
    
    # Extract oracle updates
    try:
        oracles = row.get('amm_oracle')
        if pd.notna(oracles) and oracles is not None and len(oracles) > 0:
            oracles_list_row = oracles if isinstance(oracles, list) else [oracles]
            for oracle in oracles_list_row:
                if isinstance(oracle, dict):
                    oracle_record = {
                        'slot': row['slot'],
                        'time': row['time'],
                        'datetime': row.get('datetime'),
                        'validator': row['validator'],
                        'oracle_type': oracle.get('oracle_type'),
                        'pool': oracle.get('pool'),
                        'token_pair': oracle.get('token_pair'),
                        'us_since_first_shred': row.get('us_since_first_shred')
                    }
                    oracle_list.append(oracle_record)
    except (TypeError, ValueError):
        pass
    
    if (idx + 1) % 500000 == 0:
        print(f"  Processed: {idx+1:,} records | Trades: {len(trades_list):,} | Oracles: {len(oracle_list):,}")

trades_df = pd.DataFrame(trades_list)
oracle_df = pd.DataFrame(oracle_list)

print(f"\n✓ Extracted {len(trades_df):,} trades")
print(f"✓ Extracted {len(oracle_df):,} oracle updates")

# ============================================================================
# 3. CALCULATE ORACLE LATENCY METRICS
# ============================================================================

print("\n⏱️ Calculating oracle latency metrics...")

oracle_latency = oracle_df.groupby(['pool', 'token_pair']).agg({
    'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'time': lambda x: (x.max() - x.min()) if len(x) > 1 else 0
}).round(2)

oracle_latency.columns = ['update_count', 'mean_latency_us', 'median_latency_us', 
                          'std_latency_us', 'min_latency_us', 'max_latency_us', 'time_span']
oracle_latency = oracle_latency.reset_index()
oracle_latency = oracle_latency.sort_values('mean_latency_us', ascending=False)

print(f"✓ Oracle latency metrics for {len(oracle_latency)} pool-pair combinations")

# ============================================================================
# 4. CALCULATE TRADE LATENCY METRICS
# ============================================================================

print("\n📈 Calculating trade latency metrics...")

trade_latency = trades_df.groupby(['pool', 'token_pair']).agg({
    'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'signer': 'nunique'
}).round(2)

trade_latency.columns = ['trade_count', 'mean_trade_latency_us', 'median_trade_latency_us', 
                         'std_trade_latency_us', 'min_trade_latency_us', 'max_trade_latency_us', 'unique_signers']
trade_latency = trade_latency.reset_index()
trade_latency = trade_latency.sort_values('mean_trade_latency_us', ascending=False)

print(f"✓ Trade latency metrics for {len(trade_latency)} pool-pair combinations")

# ============================================================================
# 5. CALCULATE VULNERABILITY SCORES
# ============================================================================

print("\n⚠️ Calculating vulnerability scores...")

if len(trades_df) > 0:
    pair_metrics = trades_df.groupby('token_pair').agg({
        'us_since_first_shred': ['mean', 'median', 'std'],
        'signer': 'nunique',
        'validator': 'nunique',
        'pool': 'nunique'
    }).round(2)
    
    pair_metrics.columns = ['mean_latency_us', 'median_latency_us', 'std_latency_us',
                           'unique_signers', 'unique_validators', 'unique_pools']
    pair_metrics = pair_metrics.reset_index()
    
    # Normalize metrics to 0-1 scale
    try:
        latency_norm = (pair_metrics['mean_latency_us'] - pair_metrics['mean_latency_us'].min()) / \
                      (pair_metrics['mean_latency_us'].max() - pair_metrics['mean_latency_us'].min() + 1e-10)
        val_norm = (pair_metrics['unique_validators'] - pair_metrics['unique_validators'].min()) / \
                  (pair_metrics['unique_validators'].max() - pair_metrics['unique_validators'].min() + 1e-10)
        signer_norm = (pair_metrics['unique_signers'] - pair_metrics['unique_signers'].min()) / \
                     (pair_metrics['unique_signers'].max() - pair_metrics['unique_signers'].min() + 1e-10)
        pool_norm = (pair_metrics['unique_pools'] - pair_metrics['unique_pools'].min()) / \
                   (pair_metrics['unique_pools'].max() - pair_metrics['unique_pools'].min() + 1e-10)
        
        # Composite vulnerability score
        pair_metrics['vulnerability_score'] = (
            latency_norm * 0.3 +      # Oracle latency (30%)
            val_norm * 0.3 +          # Validator concentration (30%)
            signer_norm * 0.2 +       # MEV signer diversity (20%)
            pool_norm * 0.2           # Pool diversity (20%)
        ).round(3)
    except:
        pair_metrics['vulnerability_score'] = 0.5
    
    pair_metrics = pair_metrics.sort_values('vulnerability_score', ascending=False)
    print(f"✓ Vulnerability metrics for {len(pair_metrics)} token pairs")
else:
    pair_metrics = pd.DataFrame()

# ============================================================================
# 6. MEV VULNERABILITY METRICS
# ============================================================================

print("\n🚨 Calculating MEV vulnerability metrics...")

if len(mev_df) > 0:
    mev_aggregated = mev_df.agg({
        'back_running': 'sum',
        'front_running': 'sum',
        'sandwich': 'sum',
        'fat_sandwich': 'sum',
        'sandwich_complete': 'sum',
        'cost_sol': 'sum',
        'profit_sol': 'sum',
        'net_profit_sol': 'sum',
        'confidence': 'mean'
    })
    
    mev_by_validator = mev_df.groupby('validator').agg({
        'back_running': 'sum',
        'front_running': 'sum',
        'sandwich': 'sum',
        'fat_sandwich': 'sum',
        'sandwich_complete': 'sum',
        'cost_sol': 'sum',
        'profit_sol': 'sum',
        'net_profit_sol': 'sum',
        'confidence': 'mean',
        'amm_trade': 'count'
    }).round(4)
    
    mev_by_validator.columns = ['back_running_count', 'front_running_count', 'sandwich_count', 
                                'fat_sandwich_count', 'sandwich_complete_count', 'total_cost_sol', 
                                'total_profit_sol', 'net_profit_sol', 'avg_confidence', 'mev_events']
    mev_by_validator = mev_by_validator.sort_values('net_profit_sol', ascending=False)
    print(f"✓ MEV metrics for {len(mev_by_validator)} validators")
else:
    mev_aggregated = {}
    mev_by_validator = pd.DataFrame()

# ============================================================================
# 7. PRINT SUMMARY TABLES
# ============================================================================

print("\n" + "="*80)
print("TABLE 1: ORACLE LATENCY METRICS BY POOL-PAIR (Top 20)")
print("="*80)
table1 = oracle_latency.head(20)[['pool', 'token_pair', 'update_count', 
                                   'mean_latency_us', 'median_latency_us', 
                                   'std_latency_us', 'max_latency_us']]
print(table1.to_string(index=False))

print("\n" + "="*80)
print("TABLE 2: TRADE LATENCY METRICS BY POOL-PAIR (Top 20)")
print("="*80)
table2 = trade_latency.head(20)[['pool', 'token_pair', 'trade_count', 
                                  'mean_trade_latency_us', 'median_trade_latency_us', 
                                  'std_trade_latency_us', 'unique_signers']]
print(table2.to_string(index=False))

if len(pair_metrics) > 0:
    print("\n" + "="*80)
    print("TABLE 3: TOKEN PAIR VULNERABILITY ASSESSMENT (Top 20)")
    print("="*80)
    table3 = pair_metrics.head(20)[['token_pair', 'mean_latency_us', 
                                     'unique_validators', 'unique_signers', 
                                     'unique_pools', 'vulnerability_score']]
    print(table3.to_string(index=False))

if len(mev_by_validator) > 0:
    print("\n" + "="*80)
    print("TABLE 4: MEV RISK ASSESSMENT BY VALIDATOR (Top 15)")
    print("="*80)
    table4 = mev_by_validator.head(15).reset_index()[['validator', 'mev_events', 'sandwich_count', 
                                                        'fat_sandwich_count', 'net_profit_sol', 'avg_confidence']]
    print(table4.to_string(index=False))

# ============================================================================
# 8. GENERATE VISUALIZATIONS
# ============================================================================

print("\n📊 Generating visualizations...")

# Chart 1: Oracle Latency Comparison
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

oracle_top15 = oracle_latency.nlargest(15, 'mean_latency_us').copy()
oracle_top15['pool_pair'] = oracle_top15['pool'].str[:8] + '...' + oracle_top15['token_pair']

ax1 = axes[0]
bars1 = ax1.barh(range(len(oracle_top15)), oracle_top15['mean_latency_us'], color='steelblue')
ax1.set_yticks(range(len(oracle_top15)))
ax1.set_yticklabels(oracle_top15['pool_pair'], fontsize=9)
ax1.set_xlabel('Mean Oracle Latency (microseconds)', fontsize=11, fontweight='bold')
ax1.set_title('TOP 15 POOLS: Mean Oracle Update Latency', fontsize=12, fontweight='bold')
ax1.invert_yaxis()
for i, (idx, row) in enumerate(oracle_top15.iterrows()):
    ax1.text(row['mean_latency_us'], i, f" {row['mean_latency_us']:.0f}µs", va='center', fontsize=8)

ax2 = axes[1]
oracle_top15_freq = oracle_latency.nlargest(15, 'update_count').copy()
oracle_top15_freq['pool_pair'] = oracle_top15_freq['pool'].str[:8] + '...' + oracle_top15_freq['token_pair']
bars2 = ax2.barh(range(len(oracle_top15_freq)), oracle_top15_freq['update_count'], color='darkgreen')
ax2.set_yticks(range(len(oracle_top15_freq)))
ax2.set_yticklabels(oracle_top15_freq['pool_pair'], fontsize=9)
ax2.set_xlabel('Number of Oracle Updates', fontsize=11, fontweight='bold')
ax2.set_title('TOP 15 POOLS: Oracle Update Frequency', fontsize=12, fontweight='bold')
ax2.invert_yaxis()
for i, (idx, row) in enumerate(oracle_top15_freq.iterrows()):
    ax2.text(row['update_count'], i, f" {int(row['update_count'])}", va='center', fontsize=8)

plt.tight_layout()
plt.savefig(output_dir / 'oracle_latency_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: oracle_latency_comparison.png")
plt.close()

# Chart 2: Trade Latency Comparison
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

trade_top15 = trade_latency.nlargest(15, 'mean_trade_latency_us').copy()
trade_top15['pool_pair'] = trade_top15['pool'].str[:8] + '...' + trade_top15['token_pair']

ax1 = axes[0]
bars1 = ax1.barh(range(len(trade_top15)), trade_top15['mean_trade_latency_us'], color='coral')
ax1.set_yticks(range(len(trade_top15)))
ax1.set_yticklabels(trade_top15['pool_pair'], fontsize=9)
ax1.set_xlabel('Mean Trade Latency (microseconds)', fontsize=11, fontweight='bold')
ax1.set_title('TOP 15 POOLS: Mean Trade Execution Latency', fontsize=12, fontweight='bold')
ax1.invert_yaxis()
for i, (idx, row) in enumerate(trade_top15.iterrows()):
    ax1.text(row['mean_trade_latency_us'], i, f" {row['mean_trade_latency_us']:.0f}µs", va='center', fontsize=8)

ax2 = axes[1]
trade_top15_vol = trade_latency.nlargest(15, 'trade_count').copy()
trade_top15_vol['pool_pair'] = trade_top15_vol['pool'].str[:8] + '...' + trade_top15_vol['token_pair']
bars2 = ax2.barh(range(len(trade_top15_vol)), trade_top15_vol['trade_count'], color='darkred')
ax2.set_yticks(range(len(trade_top15_vol)))
ax2.set_yticklabels(trade_top15_vol['pool_pair'], fontsize=9)
ax2.set_xlabel('Number of Trades', fontsize=11, fontweight='bold')
ax2.set_title('TOP 15 POOLS: Trade Volume', fontsize=12, fontweight='bold')
ax2.invert_yaxis()
for i, (idx, row) in enumerate(trade_top15_vol.iterrows()):
    ax2.text(row['trade_count'], i, f" {int(row['trade_count'])}", va='center', fontsize=8)

plt.tight_layout()
plt.savefig(output_dir / 'trade_latency_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: trade_latency_comparison.png")
plt.close()

# Chart 3: Vulnerability Assessment
if len(pair_metrics) > 0:
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    vuln_top15 = pair_metrics.nlargest(15, 'vulnerability_score').copy()
    ax1 = axes[0, 0]
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(vuln_top15)))
    bars1 = ax1.barh(range(len(vuln_top15)), vuln_top15['vulnerability_score'], color=colors)
    ax1.set_yticks(range(len(vuln_top15)))
    ax1.set_yticklabels(vuln_top15['token_pair'], fontsize=9)
    ax1.set_xlabel('Vulnerability Score', fontsize=11, fontweight='bold')
    ax1.set_title('TOP 15 TOKEN PAIRS: MEV Vulnerability Score', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    for i, (idx, row) in enumerate(vuln_top15.iterrows()):
        ax1.text(row['vulnerability_score'], i, f" {row['vulnerability_score']:.3f}", va='center', fontsize=8)
    
    latency_top15 = pair_metrics.nlargest(15, 'mean_latency_us').copy()
    ax2 = axes[0, 1]
    scatter = ax2.scatter(latency_top15['mean_latency_us'], latency_top15['vulnerability_score'],
                         s=latency_top15['unique_validators']*30, alpha=0.6, 
                         c=latency_top15['vulnerability_score'], cmap='RdYlGn_r')
    ax2.set_xlabel('Mean Oracle Latency (µs)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Vulnerability Score', fontsize=11, fontweight='bold')
    ax2.set_title('LATENCY vs VULNERABILITY (bubble size = validator count)', fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax2, label='Vulnerability')
    
    val_top15 = pair_metrics.nlargest(15, 'unique_validators').copy()
    ax3 = axes[1, 0]
    bars3 = ax3.barh(range(len(val_top15)), val_top15['unique_validators'], color='teal')
    ax3.set_yticks(range(len(val_top15)))
    ax3.set_yticklabels(val_top15['token_pair'], fontsize=9)
    ax3.set_xlabel('Number of Unique Validators', fontsize=11, fontweight='bold')
    ax3.set_title('TOP 15 TOKEN PAIRS: Validator Concentration', fontsize=12, fontweight='bold')
    ax3.invert_yaxis()
    
    signer_top15 = pair_metrics.nlargest(15, 'unique_signers').copy()
    ax4 = axes[1, 1]
    bars4 = ax4.barh(range(len(signer_top15)), signer_top15['unique_signers'], color='purple')
    ax4.set_yticks(range(len(signer_top15)))
    ax4.set_yticklabels(signer_top15['token_pair'], fontsize=9)
    ax4.set_xlabel('Number of Unique MEV Signers', fontsize=11, fontweight='bold')
    ax4.set_title('TOP 15 TOKEN PAIRS: MEV Signer Diversity', fontsize=12, fontweight='bold')
    ax4.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'vulnerability_assessment.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: vulnerability_assessment.png")
    plt.close()

# Chart 4: MEV Risk Analysis
if len(mev_by_validator) > 0:
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    mev_top12 = mev_by_validator.head(12).reset_index()
    
    # Plot 1: MEV events by type
    ax1 = axes[0, 0]
    x_pos = np.arange(len(mev_top12))
    width = 0.2
    ax1.bar(x_pos - 1.5*width, mev_top12['back_running_count'], width, label='Back-run', alpha=0.8)
    ax1.bar(x_pos - 0.5*width, mev_top12['front_running_count'], width, label='Front-run', alpha=0.8)
    ax1.bar(x_pos + 0.5*width, mev_top12['sandwich_count'], width, label='Sandwich', alpha=0.8)
    ax1.bar(x_pos + 1.5*width, mev_top12['fat_sandwich_count'], width, label='Fat Sandwich', alpha=0.8)
    ax1.set_xlabel('Validator', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Attack Count', fontsize=11, fontweight='bold')
    ax1.set_title('MEV Attack Types by Top Validators', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(mev_top12['validator'].str[:6], rotation=45, ha='right', fontsize=8)
    ax1.legend(loc='upper right')
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Net Profit
    ax2 = axes[0, 1]
    colors_profit = ['green' if x > 0 else 'red' for x in mev_top12['net_profit_sol']]
    bars2 = ax2.barh(range(len(mev_top12)), mev_top12['net_profit_sol'], color=colors_profit)
    ax2.set_yticks(range(len(mev_top12)))
    ax2.set_yticklabels(mev_top12['validator'], fontsize=9)
    ax2.set_xlabel('Net Profit (SOL)', fontsize=11, fontweight='bold')
    ax2.set_title('MEV Net Profit by Top Validators', fontsize=12, fontweight='bold')
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax2.invert_yaxis()
    
    # Plot 3: Cost vs Profit
    ax3 = axes[1, 0]
    scatter3 = ax3.scatter(mev_top12['total_cost_sol'], mev_top12['total_profit_sol'],
                          s=mev_top12['mev_events']*5, alpha=0.6,
                          c=mev_top12['net_profit_sol'], cmap='RdYlGn')
    ax3.set_xlabel('Total Cost (SOL)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Total Profit (SOL)', fontsize=11, fontweight='bold')
    ax3.set_title('MEV Cost vs Profit (bubble size = event count)', fontsize=12, fontweight='bold')
    plt.colorbar(scatter3, ax=ax3, label='Net Profit')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Confidence
    ax4 = axes[1, 1]
    bars4 = ax4.barh(range(len(mev_top12)), mev_top12['avg_confidence'], color='steelblue')
    ax4.set_yticks(range(len(mev_top12)))
    ax4.set_yticklabels(mev_top12['validator'], fontsize=9)
    ax4.set_xlabel('Average Detection Confidence', fontsize=11, fontweight='bold')
    ax4.set_title('MEV Detection Confidence by Validator', fontsize=12, fontweight='bold')
    ax4.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'mev_risk_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: mev_risk_analysis.png")
    plt.close()

# ============================================================================
# 9. EXPORT TABLES TO CSV
# ============================================================================

print("\n💾 Exporting tables to CSV...")

oracle_latency.to_csv(output_dir / 'oracle_latency_by_pool.csv', index=False)
print("✓ oracle_latency_by_pool.csv")

trade_latency.to_csv(output_dir / 'trade_latency_by_pool.csv', index=False)
print("✓ trade_latency_by_pool.csv")

if len(pair_metrics) > 0:
    pair_metrics.to_csv(output_dir / 'token_pair_vulnerability_scores.csv', index=False)
    print("✓ token_pair_vulnerability_scores.csv")

if len(mev_by_validator) > 0:
    mev_by_validator.to_csv(output_dir / 'mev_risk_by_validator.csv')
    print("✓ mev_risk_by_validator.csv")
    
    if len(mev_aggregated) > 0:
        mev_agg_df = pd.DataFrame([mev_aggregated]).T
        mev_agg_df.to_csv(output_dir / 'mev_summary_totals.csv')
        print("✓ mev_summary_totals.csv")

# ============================================================================
# 10. FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
print("="*80)

print(f"\n📊 DATA OVERVIEW:")
print(f"   • Total transactions: {len(df):,}")
print(f"   • Total trades extracted: {len(trades_df):,}")
print(f"   • Total oracle updates: {len(oracle_df):,}")
print(f"   • MEV events detected: {len(mev_df):,}")

if len(trades_df) > 0:
    print(f"\n🏊 POOL & PAIR ANALYSIS:")
    print(f"   • Unique pools in trades: {trades_df['pool'].nunique():,}")
    print(f"   • Unique token pairs: {trades_df['token_pair'].nunique():,}")
    print(f"   • Unique validators: {trades_df['validator'].nunique():,}")
    print(f"   • Unique MEV signers: {trades_df['signer'].nunique():,}")

if len(oracle_df) > 0:
    print(f"\n⏱️ ORACLE LATENCY METRICS:")
    print(f"   • Mean oracle latency: {oracle_latency['mean_latency_us'].mean():.2f} µs")
    print(f"   • Median oracle latency: {oracle_latency['median_latency_us'].median():.2f} µs")
    print(f"   • Max oracle latency: {oracle_latency['mean_latency_us'].max():.2f} µs")
    print(f"   • Min oracle latency: {oracle_latency['mean_latency_us'].min():.2f} µs")

if len(trade_latency) > 0:
    print(f"\n📈 TRADE LATENCY METRICS:")
    print(f"   • Mean trade latency: {trade_latency['mean_trade_latency_us'].mean():.2f} µs")
    print(f"   • Median trade latency: {trade_latency['median_trade_latency_us'].median():.2f} µs")
    print(f"   • Max trade latency: {trade_latency['mean_trade_latency_us'].max():.2f} µs")
    print(f"   • Min trade latency: {trade_latency['mean_trade_latency_us'].min():.2f} µs")

if len(pair_metrics) > 0:
    print(f"\n⚠️ VULNERABILITY ASSESSMENT:")
    print(f"   • Pairs analyzed: {len(pair_metrics)}")
    print(f"   • Average vulnerability: {pair_metrics['vulnerability_score'].mean():.3f}")
    print(f"   • Highest risk: {pair_metrics.iloc[0]['token_pair']} ({pair_metrics.iloc[0]['vulnerability_score']:.3f})")
    print(f"   • Lowest risk: {pair_metrics.iloc[-1]['token_pair']} ({pair_metrics.iloc[-1]['vulnerability_score']:.3f})")

if len(mev_aggregated) > 0:
    print(f"\n🚨 MEV RISK SUMMARY:")
    print(f"   • Total MEV events: {int(mev_aggregated.get('sandwich', 0)):,}")
    print(f"   • Front-running attacks: {int(mev_aggregated.get('front_running', 0)):,}")
    print(f"   • Back-running attacks: {int(mev_aggregated.get('back_running', 0)):,}")
    print(f"   • Sandwich attacks: {int(mev_aggregated.get('sandwich', 0)):,}")
    print(f"   • Fat sandwiches: {int(mev_aggregated.get('fat_sandwich', 0)):,}")
    print(f"   • Total victim cost: {mev_aggregated.get('cost_sol', 0):.4f} SOL")
    print(f"   • Total MEV profit: {mev_aggregated.get('profit_sol', 0):.4f} SOL")
    print(f"   • Avg confidence: {mev_aggregated.get('confidence', 0):.3f}")

print(f"\n✅ OUTPUTS GENERATED IN: {output_dir.absolute()}/")
print("   📊 Tables (CSV):")
print("      • oracle_latency_by_pool.csv")
print("      • trade_latency_by_pool.csv")
if len(pair_metrics) > 0:
    print("      • token_pair_vulnerability_scores.csv")
if len(mev_by_validator) > 0:
    print("      • mev_risk_by_validator.csv")
    print("      • mev_summary_totals.csv")

print("   📈 Charts (PNG):")
print("      • oracle_latency_comparison.png")
print("      • trade_latency_comparison.png")
if len(pair_metrics) > 0:
    print("      • vulnerability_assessment.png")
if len(mev_by_validator) > 0:
    print("      • mev_risk_analysis.png")

print("\n" + "="*80)
print("Analysis completed successfully!")
print("="*80 + "\n")
