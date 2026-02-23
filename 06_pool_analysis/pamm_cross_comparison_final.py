#!/usr/bin/env python3
"""
PAMM Pool Cross-Comparison Analysis
Oracle Latency, Vulnerabilities & MEV Exposure

Analysis of PAMM pools comparing:
- MEV frequency and risk by validator
- Transaction latency metrics  
- Oracle update patterns
- Sandwich/front-run/back-run attack metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SETUP
# ============================================================================

print("\n" + "="*80)
print("PAMM POOL CROSS-COMPARISON ANALYSIS")
print("Oracle Latency, Vulnerabilities & MEV Exposure")
print("="*80)

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

df = pd.read_parquet(data_path)
print(f"✓ Transaction data: {len(df):,} records")

if mev_path.exists():
    mev_df = pd.read_csv(mev_path)
    print(f"✓ MEV analysis: {len(mev_df):,} detected events")
else:
    mev_df = pd.DataFrame()
    print(f"⚠ MEV data not found")

# ============================================================================
# 2. ANALYZE ORACLE PATTERNS & LATENCY
# ============================================================================

print("\n⏱️ Analyzing oracle update patterns and latency...")

# Oracle types and their frequency
oracle_types = df['amm_oracle'].value_counts()
print(f"\nOracle Types by Frequency:")
print(oracle_types.head(15))

# Create oracle latency analysis by oracle type
oracle_latency_stats = df.groupby('amm_oracle').agg({
    'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'validator': 'nunique',
    'signer': 'nunique',
    'is_pool_trade': 'sum'
}).round(2)

oracle_latency_stats.columns = [
    'update_count', 'mean_latency_us', 'median_latency_us', 'std_latency_us',
    'min_latency_us', 'max_latency_us', 'unique_validators', 'unique_signers', 'pool_trades'
]
oracle_latency_stats = oracle_latency_stats.reset_index()
oracle_latency_stats = oracle_latency_stats.rename(columns={'amm_oracle': 'oracle_type'})
oracle_latency_stats = oracle_latency_stats.sort_values('mean_latency_us', ascending=False)

print(f"\n✓ Oracle latency analysis for {len(oracle_latency_stats)} oracle types")

# ============================================================================
# 3. ANALYZE TRANSACTION LATENCY BY VALIDATOR
# ============================================================================

print("\nAnalyzing transaction latency by validator...")

validator_latency = df.groupby('validator').agg({
    'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'is_pool_trade': ['sum', 'mean'],
    'signer': 'nunique',
    'amm_oracle': lambda x: x.nunique()
}).round(2)

validator_latency.columns = [
    'total_txns', 'mean_latency_us', 'median_latency_us', 'std_latency_us',
    'min_latency_us', 'max_latency_us', 'pool_trades_count', 'pool_trade_ratio',
    'unique_signers', 'oracle_types'
]
validator_latency = validator_latency.reset_index()
validator_latency = validator_latency.sort_values('mean_latency_us', ascending=False)

print(f"✓ Validator latency for {len(validator_latency)} validators")

# ============================================================================
# 4. MEV VULNERABILITY & RISK ANALYSIS
# ============================================================================

print("\n🚨 Analyzing MEV vulnerability by validator...")

if len(mev_df) > 0:
    # Convert confidence to numeric
    mev_df['confidence'] = pd.to_numeric(mev_df['confidence'], errors='coerce')
    
    # Aggregate MEV metrics
    mev_summary = {
        'back_running': mev_df['back_running'].sum(),
        'front_running': mev_df['front_running'].sum(),
        'sandwich': mev_df['sandwich'].sum(),
        'fat_sandwich': mev_df['fat_sandwich'].sum(),
        'sandwich_complete': mev_df['sandwich_complete'].sum(),
        'total_cost_sol': mev_df['cost_sol'].sum(),
        'total_profit_sol': mev_df['profit_sol'].sum(),
        'net_profit_sol': mev_df['net_profit_sol'].sum(),
        'avg_confidence': mev_df['confidence'].mean()
    }
    
    # MEV by validator
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
    
    mev_by_validator.columns = [
        'back_running_count', 'front_running_count', 'sandwich_count',
        'fat_sandwich_count', 'sandwich_complete_count', 'total_cost_sol',
        'total_profit_sol', 'net_profit_sol', 'avg_confidence', 'mev_events'
    ]
    mev_by_validator = mev_by_validator.sort_values('net_profit_sol', ascending=False)
    mev_by_validator = mev_by_validator.reset_index()
    
    # Calculate vulnerability score
    mev_by_validator['mev_risk_score'] = (
        (mev_by_validator['mev_events'] / mev_by_validator['mev_events'].max() * 0.4) +
        (mev_by_validator['net_profit_sol'] / (mev_by_validator['net_profit_sol'].max() + 1e-10) * 0.3) +
        (mev_by_validator['avg_confidence'] * 0.3)
    ).round(3)
    
    mev_by_validator = mev_by_validator.sort_values('mev_risk_score', ascending=False)
    
    print(f"✓ MEV risk analysis for {len(mev_by_validator)} validators")
else:
    mev_summary = {}
    mev_by_validator = pd.DataFrame()
    print("⚠ No MEV data available")

# ============================================================================
# 5. ORACLE vs LATENCY CORRELATION
# ============================================================================

print("\nAnalyzing oracle-latency correlation...")

oracle_validator_matrix = df.groupby(['amm_oracle', 'validator']).agg({
    'us_since_first_shred': ['count', 'mean', 'std'],
    'is_pool_trade': 'sum'
}).round(2)

oracle_validator_matrix.columns = [
    'transaction_count', 'mean_latency_us', 'std_latency_us', 'pool_trades'
]
oracle_validator_matrix = oracle_validator_matrix.reset_index()

# Get top combinations
top_combos = oracle_validator_matrix.nlargest(20, 'transaction_count')
print(f"\n✓ Oracle-Validator combinations: {len(oracle_validator_matrix)} total")
print(f"✓ Analyzing top {len(top_combos)} combinations")

# ============================================================================
# 6. CREATE VULNERABILITY SCORE
# ============================================================================

print("\nCalculating comprehensive vulnerability scores...")

# Merge MEV data with latency data
if len(mev_by_validator) > 0:
    vulnerability_analysis = validator_latency.copy()
    
    # Add MEV metrics
    mev_cols = mev_by_validator[['validator', 'mev_events', 'net_profit_sol', 
                                  'sandwich_count', 'fat_sandwich_count', 'mev_risk_score']]
    vulnerability_analysis = vulnerability_analysis.merge(
        mev_cols, on='validator', how='left'
    ).fillna(0)
    
    # Create composite vulnerability score
    latency_norm = (vulnerability_analysis['mean_latency_us'] - vulnerability_analysis['mean_latency_us'].min()) / \
                   ((vulnerability_analysis['mean_latency_us'].max() - vulnerability_analysis['mean_latency_us'].min()) + 1e-10)
    mev_norm = vulnerability_analysis['mev_risk_score'] / (vulnerability_analysis['mev_risk_score'].max() + 1e-10)
    pool_trade_norm = vulnerability_analysis['pool_trade_ratio']
    
    vulnerability_analysis['vulnerability_score'] = (
        latency_norm * 0.35 +  # Latency factor
        mev_norm * 0.35 +      # MEV risk factor
        pool_trade_norm * 0.30  # Pool trade concentration
    ).round(3)
    
    vulnerability_analysis = vulnerability_analysis.sort_values('vulnerability_score', ascending=False)
    print(f"✓ Vulnerability scores calculated for {len(vulnerability_analysis)} validators")
else:
    vulnerability_analysis = validator_latency.copy()
    vulnerability_analysis['vulnerability_score'] = \
        ((vulnerability_analysis['mean_latency_us'] / vulnerability_analysis['mean_latency_us'].max()) * 0.5 + \
         (vulnerability_analysis['pool_trade_ratio'] * 0.5)).round(3)

# ============================================================================
# 7. PRINT SUMMARY TABLES
# ============================================================================

print("\n" + "="*80)
print("TABLE 1: ORACLE LATENCY METRICS (Top 20)")
print("="*80)
table1 = oracle_latency_stats.head(20)[[
    'oracle_type', 'update_count', 'mean_latency_us', 'median_latency_us',
    'std_latency_us', 'max_latency_us', 'unique_validators'
]]
print(table1.to_string(index=False))

print("\n" + "="*80)
print("TABLE 2: VALIDATOR LATENCY METRICS (Top 20)")
print("="*80)
table2 = validator_latency.head(20)[[
    'validator', 'total_txns', 'mean_latency_us', 'median_latency_us',
    'pool_trade_ratio', 'unique_signers'
]]
print(table2.to_string(index=False))

if len(mev_by_validator) > 0:
    print("\n" + "="*80)
    print("TABLE 3: MEV RISK ASSESSMENT BY VALIDATOR (Top 20)")
    print("="*80)
    table3 = mev_by_validator.head(20)[[
        'validator', 'mev_events', 'sandwich_count', 'fat_sandwich_count',
        'net_profit_sol', 'avg_confidence', 'mev_risk_score'
    ]]
    print(table3.to_string(index=False))

print("\n" + "="*80)
print("TABLE 4: VALIDATOR VULNERABILITY ASSESSMENT (Top 20)")
print("="*80)
table4 = vulnerability_analysis.head(20)[[
    'validator', 'mean_latency_us', 'pool_trade_ratio', 'unique_signers',
    'mev_events', 'vulnerability_score'
]]
print(table4.to_string(index=False))

# ============================================================================
# 8. GENERATE VISUALIZATIONS
# ============================================================================

print("\n📊 Generating visualizations...")

# Chart 1: Oracle Latency Comparison
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

oracle_top15 = oracle_latency_stats.nlargest(15, 'mean_latency_us').copy()

ax1 = axes[0]
bars1 = ax1.barh(range(len(oracle_top15)), oracle_top15['mean_latency_us'], color='steelblue')
ax1.set_yticks(range(len(oracle_top15)))
ax1.set_yticklabels(oracle_top15['oracle_type'], fontsize=10, fontweight='bold')
ax1.set_xlabel('Mean Oracle Latency (microseconds)', fontsize=11, fontweight='bold')
ax1.set_title('TOP 15 ORACLES: Mean Update Latency', fontsize=13, fontweight='bold')
ax1.invert_yaxis()
for i, (idx, row) in enumerate(oracle_top15.iterrows()):
    ax1.text(row['mean_latency_us'], i, f"  {row['mean_latency_us']:.0f}µs", va='center', fontsize=9)

ax2 = axes[1]
oracle_top15_freq = oracle_latency_stats.nlargest(15, 'update_count').copy()
bars2 = ax2.barh(range(len(oracle_top15_freq)), oracle_top15_freq['update_count'], color='darkgreen')
ax2.set_yticks(range(len(oracle_top15_freq)))
ax2.set_yticklabels(oracle_top15_freq['oracle_type'], fontsize=10, fontweight='bold')
ax2.set_xlabel('Number of Updates', fontsize=11, fontweight='bold')
ax2.set_title('TOP 15 ORACLES: Update Frequency', fontsize=13, fontweight='bold')
ax2.invert_yaxis()
for i, (idx, row) in enumerate(oracle_top15_freq.iterrows()):
    ax2.text(row['update_count'], i, f"  {int(row['update_count']):,}", va='center', fontsize=9)

plt.tight_layout()
plt.savefig(output_dir / 'oracle_latency_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: oracle_latency_comparison.png")
plt.close()

# Chart 2: Validator Latency Comparison
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

validator_top15 = validator_latency.nlargest(15, 'mean_latency_us').copy()

ax1 = axes[0]
bars1 = ax1.barh(range(len(validator_top15)), validator_top15['mean_latency_us'], color='coral')
ax1.set_yticks(range(len(validator_top15)))
ax1.set_yticklabels(validator_top15['validator'].str[:12], fontsize=9)
ax1.set_xlabel('Mean Transaction Latency (microseconds)', fontsize=11, fontweight='bold')
ax1.set_title('TOP 15 VALIDATORS: Mean Transaction Latency', fontsize=13, fontweight='bold')
ax1.invert_yaxis()
for i, (idx, row) in enumerate(validator_top15.iterrows()):
    ax1.text(row['mean_latency_us'], i, f"  {row['mean_latency_us']:.0f}µs", va='center', fontsize=8)

ax2 = axes[1]
validator_top15_trade = validator_latency.nlargest(15, 'pool_trade_ratio').copy()
bars2 = ax2.barh(range(len(validator_top15_trade)), validator_top15_trade['pool_trade_ratio'], color='darkred')
ax2.set_yticks(range(len(validator_top15_trade)))
ax2.set_yticklabels(validator_top15_trade['validator'].str[:12], fontsize=9)
ax2.set_xlabel('Pool Trade Ratio', fontsize=11, fontweight='bold')
ax2.set_title('TOP 15 VALIDATORS: Pool Trade Concentration', fontsize=13, fontweight='bold')
ax2.invert_yaxis()

plt.tight_layout()
plt.savefig(output_dir / 'validator_latency_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: validator_latency_comparison.png")
plt.close()

# Chart 3: Vulnerability Score Assessment
if len(mev_by_validator) > 0:
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    vuln_top15 = vulnerability_analysis.nlargest(15, 'vulnerability_score').copy()
    
    ax1 = axes[0, 0]
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(vuln_top15)))
    bars1 = ax1.barh(range(len(vuln_top15)), vuln_top15['vulnerability_score'], color=colors)
    ax1.set_yticks(range(len(vuln_top15)))
    ax1.set_yticklabels(vuln_top15['validator'].str[:12], fontsize=9)
    ax1.set_xlabel('Vulnerability Score', fontsize=11, fontweight='bold')
    ax1.set_title('TOP 15 VALIDATORS: MEV Vulnerability Score', fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    for i, (idx, row) in enumerate(vuln_top15.iterrows()):
        ax1.text(row['vulnerability_score'], i, f"  {row['vulnerability_score']:.3f}", va='center', fontsize=8)
    
    latency_top15 = vulnerability_analysis.nlargest(15, 'mean_latency_us').copy()
    ax2 = axes[0, 1]
    scatter = ax2.scatter(latency_top15['mean_latency_us'], latency_top15['mev_risk_score'],
                         s=latency_top15['mev_events']*5, alpha=0.6,
                         c=latency_top15['vulnerability_score'], cmap='RdYlGn_r')
    ax2.set_xlabel('Mean Latency (µs)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('MEV Risk Score', fontsize=11, fontweight='bold')
    ax2.set_title('LATENCY vs MEV RISK (bubble size = MEV events)', fontsize=12, fontweight='bold')
    plt.colorbar(scatter, ax=ax2, label='Vulnerability')
    
    mev_top15 = mev_by_validator.nlargest(15, 'mev_events').copy()
    ax3 = axes[1, 0]
    x_pos = np.arange(min(10, len(mev_top15)))
    mev_top10 = mev_top15.head(10)
    width = 0.2
    ax3.bar(x_pos - 1.5*width, mev_top10['sandwich_count'].head(10), width, label='Sandwich', alpha=0.8)
    ax3.bar(x_pos - 0.5*width, mev_top10['front_running_count'].head(10), width, label='Front-run', alpha=0.8)
    ax3.bar(x_pos + 0.5*width, mev_top10['back_running_count'].head(10), width, label='Back-run', alpha=0.8)
    ax3.bar(x_pos + 1.5*width, mev_top10['fat_sandwich_count'].head(10), width, label='Fat-sandwich', alpha=0.8)
    ax3.set_xlabel('Validator', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Attack Count', fontsize=11, fontweight='bold')
    ax3.set_title('TOP 10 VALIDATORS: MEV Attack Types', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(mev_top10['validator'].str[:6], rotation=45, ha='right', fontsize=8)
    ax3.legend(loc='upper right', fontsize=8)
    ax3.grid(axis='y', alpha=0.3)
    
    profit_top15 = mev_by_validator.nlargest(15, 'net_profit_sol').copy()
    ax4 = axes[1, 1]
    colors_profit = ['green' if x > 0 else 'red' for x in profit_top15['net_profit_sol']]
    bars4 = ax4.barh(range(len(profit_top15)), profit_top15['net_profit_sol'], color=colors_profit)
    ax4.set_yticks(range(len(profit_top15)))
    ax4.set_yticklabels(profit_top15['validator'].str[:12], fontsize=9)
    ax4.set_xlabel('Net Profit (SOL)', fontsize=11, fontweight='bold')
    ax4.set_title('TOP 15 VALIDATORS: MEV Net Profit', fontsize=12, fontweight='bold')
    ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax4.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'vulnerability_assessment.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: vulnerability_assessment.png")
    plt.close()

# ============================================================================
# 9. EXPORT TABLES TO CSV
# ============================================================================

print("\n💾 Exporting analysis to CSV...")

oracle_latency_stats.to_csv(output_dir / 'oracle_latency_by_type.csv', index=False)
print("✓ oracle_latency_by_type.csv")

validator_latency.to_csv(output_dir / 'validator_latency_metrics.csv', index=False)
print("✓ validator_latency_metrics.csv")

if len(mev_by_validator) > 0:
    mev_by_validator.to_csv(output_dir / 'mev_risk_by_validator.csv', index=False)
    print("✓ mev_risk_by_validator.csv")

vulnerability_analysis.to_csv(output_dir / 'vulnerability_assessment.csv', index=False)
print("✓ vulnerability_assessment.csv")

oracle_validator_matrix.to_csv(output_dir / 'oracle_validator_matrix.csv', index=False)
print("✓ oracle_validator_matrix.csv")

# ============================================================================
# 10. FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
print("="*80)

print(f"\n📊 DATA OVERVIEW:")
print(f"   • Total transactions: {len(df):,}")
print(f"   • Pool trades: {df['is_pool_trade'].sum():,}")
print(f"   • MEV events detected: {len(mev_df):,}")

print(f"\n🏊 ORACLE ANALYSIS:")
print(f"   • Unique oracle types: {df['amm_oracle'].nunique()}")
print(f"   • Mean oracle latency: {oracle_latency_stats['mean_latency_us'].mean():.2f} µs")
print(f"   • Median oracle latency: {oracle_latency_stats['median_latency_us'].median():.2f} µs")
print(f"   • Max oracle latency: {oracle_latency_stats['mean_latency_us'].max():.2f} µs")

print(f"\n🔄 VALIDATOR ANALYSIS:")
print(f"   • Unique validators: {df['validator'].nunique()}")
print(f"   • Mean transaction latency: {validator_latency['mean_latency_us'].mean():.2f} µs")
print(f"   • Median transaction latency: {validator_latency['median_latency_us'].median():.2f} µs")
print(f"   • Mean pool trade ratio: {validator_latency['pool_trade_ratio'].mean():.3f}")

print(f"\n⚠️ VULNERABILITY ASSESSMENT:")
print(f"   • Validators analyzed: {len(vulnerability_analysis)}")
print(f"   • Average vulnerability: {vulnerability_analysis['vulnerability_score'].mean():.3f}")
print(f"   • Highest risk: {vulnerability_analysis.iloc[0]['validator']}")
print(f"   • Lowest risk: {vulnerability_analysis.iloc[-1]['validator']}")

if len(mev_summary) > 0:
    print(f"\n🚨 MEV RISK SUMMARY:")
    print(f"   • Sandwich attacks: {int(mev_summary.get('sandwich', 0)):,}")
    print(f"   • Front-running attacks: {int(mev_summary.get('front_running', 0)):,}")
    print(f"   • Back-running attacks: {int(mev_summary.get('back_running', 0)):,}")
    print(f"   • Fat sandwiches: {int(mev_summary.get('fat_sandwich', 0)):,}")
    print(f"   • Total victim cost: {mev_summary.get('total_cost_sol', 0):.4f} SOL")
    print(f"   • Total MEV profit: {mev_summary.get('total_profit_sol', 0):.4f} SOL")
    print(f"   • Avg detection confidence: {mev_summary.get('avg_confidence', 0):.3f}")

print(f"\n✅ OUTPUTS IN: {output_dir.absolute()}/")
print("   📊 CSV Tables:")
print("      • oracle_latency_by_type.csv")
print("      • validator_latency_metrics.csv")
print("      • vulnerability_assessment.csv")
print("      • oracle_validator_matrix.csv")
if len(mev_by_validator) > 0:
    print("      • mev_risk_by_validator.csv")

print("   📈 PNG Charts:")
print("      • oracle_latency_comparison.png")
print("      • validator_latency_comparison.png")
if len(mev_by_validator) > 0:
    print("      • vulnerability_assessment.png")

print("\n" + "="*80)
print("✅ PAMM CROSS-COMPARISON ANALYSIS COMPLETE")
print("="*80 + "\n")
