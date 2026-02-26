#!/usr/bin/env python3
"""
Comprehensive Contagion Analysis Visualization Generator
Generates all contagion-related plots based on the corrected MEV data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import sys

# Styling
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

print("="*80)
print("GENERATING COMPREHENSIVE CONTAGION ANALYSIS VISUALIZATIONS")
print("="*80)

# Load contagion report
contagion_report_path = 'contagion_report.json'
if not Path(contagion_report_path).exists():
    print(f"⚠️  Contagion report not found: {contagion_report_path}")
    sys.exit(1)

with open(contagion_report_path, 'r') as f:
    contagion_data = json.load(f)

print(f"\n✓ Loaded contagion report")
print(f"  Key Finding: {contagion_data.get('key_finding', 'N/A')[:80]}...")

# Load MEV data
mev_file = '02_mev_detection/filtered_output/all_fat_sandwich_only.csv'
if not Path(mev_file).exists():
    print(f"⚠️  MEV data not found: {mev_file}")
    sys.exit(1)

df_mev = pd.read_csv(mev_file)
print(f"\n✓ Loaded MEV data: {len(df_mev)} records")

# Normalize column names
if 'amm_trade' in df_mev.columns:
    df_mev = df_mev.rename(columns={'amm_trade': 'pool', 'attacker_signer': 'signer'})

# Extract contagion data
attack_probs = contagion_data.get('sections', {}).get('attack_probability_analysis', {}).get('downstream_attack_probabilities', [])
cascade_info = contagion_data.get('sections', {}).get('cascade_rate_analysis', {}).get('cascade_rates', {})

print(f"✓ Found {len(attack_probs)} downstream pools for contagion analysis")

# Create comprehensive dashboard
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

fig.suptitle('Contagious Pool MEV Attack Analysis Dashboard\n(Based on 617 Validated Fat Sandwich Attacks)', 
             fontsize=18, fontweight='bold', y=0.98)

# --- Panel 1: Attack Probability by Pool (Top probabilities)
ax1 = fig.add_subplot(gs[0, :2])
pools = [p['downstream_pool'] for p in attack_probs[:8]]
probs = [p['attack_probability_pct'] for p in attack_probs[:8]]
shared_attackers = [p['shared_attackers'] for p in attack_probs[:8]]

colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.8, len(pools)))
bars = ax1.barh(pools, probs, color=colors)
ax1.set_xlabel('Contagion Probability (%)', fontsize=11, fontweight='bold')
ax1.set_title('Attack Probability: If HumidiFi Attacked, Probability of Attacking Downstream Pool', 
              fontsize=12, fontweight='bold')
ax1.set_xlim(0, max(probs) * 1.1)

# Add value labels and attacker counts
for i, (bar, prob, attackers) in enumerate(zip(bars, probs, shared_attackers)):
    ax1.text(prob + 0.5, i, f'{prob:.1f}% ({attackers} attackers)', 
             va='center', fontsize=10, fontweight='bold')

# --- Panel 2: Risk Level Distribution
ax2 = fig.add_subplot(gs[0, 2])
risk_levels = [p.get('risk_level', 'UNKNOWN') for p in attack_probs]
risk_counts = pd.Series(risk_levels).value_counts()
colors_risk = {'HIGH': '#d73027', 'MODERATE': '#fee090', 'LOW': '#91bfdb'}
colors_list = [colors_risk.get(level, '#808080') for level in risk_counts.index]
ax2.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.0f%%', 
        colors=colors_list, startangle=90)
ax2.set_title('Risk Level Distribution\nAcross All Pools', fontsize=11, fontweight='bold')

# --- Panel 3: Attack Volume by Pool
ax3 = fig.add_subplot(gs[1, 0])
pool_attack_counts = df_mev['pool'].value_counts()
pool_attack_counts = pool_attack_counts.sort_values(ascending=True)
ax3.barh(pool_attack_counts.index, pool_attack_counts.values, color='steelblue', alpha=0.7)
ax3.set_xlabel('Number of MEV Attacks', fontsize=10, fontweight='bold')
ax3.set_title('MEV Attack Volume by Pool\n(All 617 Validated Attacks)', fontsize=11, fontweight='bold')

# --- Panel 4: Profit Impact by Pool
ax4 = fig.add_subplot(gs[1, 1])
pool_profits = df_mev.groupby('pool')['net_profit_sol'].sum().sort_values(ascending=True)
bars4 = ax4.barh(pool_profits.index, pool_profits.values, color='forestgreen', alpha=0.7)
ax4.set_xlabel('Total MEV Profit (SOL)', fontsize=10, fontweight='bold')
ax4.set_title('Total MEV Profit by Pool\nHumidiFi Dominates at 66.8% Share', fontsize=11, fontweight='bold')

# Add value labels
for i, (bar, val) in enumerate(zip(bars4, pool_profits.values)):
    pct = (val / pool_profits.sum()) * 100
    ax4.text(val + 1, i, f'{val:.2f} SOL ({pct:.1f}%)', va='center', fontsize=9)

# --- Panel 5: Cascade Rate Analysis
ax5 = fig.add_subplot(gs[1, 2])
cascade_labels = ['Cascaded\nAttacks', 'Non-Cascaded\nAttacks']
cascade_total = cascade_info.get('trigger_attacks_total', 593)
cascade_actual = cascade_info.get('cascaded_attacks', 0)
cascade_values = [cascade_actual, cascade_total - cascade_actual]
colors_cascade = ['#d73027', '#1a9850']

wedges, texts, autotexts = ax5.pie(cascade_values, labels=cascade_labels, autopct='%1.1f%%',
                                     colors=colors_cascade, startangle=90)
ax5.set_title(f"Cascade Rate Analysis\n({cascade_info.get('cascade_percentage', 0):.1f}% Contagion)", 
              fontsize=11, fontweight='bold')

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

# --- Panel 6: Shared Attacker Analysis
ax6 = fig.add_subplot(gs[2, :2])
pools_shared = [p['downstream_pool'] for p in attack_probs[:8]]
attackers_shared = [p['shared_attackers'] for p in attack_probs[:8]]
total_downstream = [p['total_downstream_attacks'] for p in attack_probs[:8]]

x_pos = np.arange(len(pools_shared))
width = 0.35

bars_shared = ax6.bar(x_pos - width/2, attackers_shared, width, label='Shared Attackers', 
                      color='coral', alpha=0.8)
bars_downstream = ax6.bar(x_pos + width/2, total_downstream, width, label='Total Downstream Attacks',
                          color='skyblue', alpha=0.8)

ax6.set_xlabel('Downstream Pool', fontsize=11, fontweight='bold')
ax6.set_ylabel('Count', fontsize=11, fontweight='bold')
ax6.set_title('Attacker Overlap Analysis: Shared Attackers vs Total Downstream Attacks', 
              fontsize=12, fontweight='bold')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(pools_shared, rotation=45, ha='right')
ax6.legend(fontsize=10)
ax6.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars_shared, bars_downstream]:
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=8)

# --- Panel 7: Key Findings Text Box
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

findings_text = f"""CONTAGION KEY INSIGHTS

Trigger Pool:
    {contagion_data.get('sections', {}).get('trigger_pool_identification', {}).get('trigger_pool', 'N/A')}

Cascade Rate:
    {cascade_info.get('cascade_percentage', 0):.1f}% of attacks cascade

Highest Risk:
    {pools_shared[0] if pools_shared else 'N/A'} ({probs[0]:.1f}%)

Total Pools:
    {len(pools_shared)} affected

MEV Concentration:
    HumidiFi: 66.8%
    BisonFi: 10.0%
    Other: 23.2%
"""

ax7.text(0.05, 0.95, findings_text, transform=ax7.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Save dashboard
output_dir = Path('11_report_generation/outputs')
output_dir.mkdir(parents=True, exist_ok=True)

dashboard_path = output_dir / 'contagion_analysis_dashboard.png'
plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: {dashboard_path}")
plt.close()

# --- Create Pool Coordination Network Visualization (zoomed)
fig2, axes = plt.subplots(2, 2, figsize=(20, 15))
fig2.suptitle('Pool Coordination & Attack Pattern Analysis\n(Contagious Vulnerability)', 
              fontsize=20, fontweight='bold')

# Plot 1: Attacker distribution across pools
ax = axes[0, 0]
pool_attackers = df_mev.groupby('pool')['signer'].nunique().sort_values(ascending=False)
ax.barh(pool_attackers.index, pool_attackers.values, color='mediumpurple', alpha=0.7)
ax.set_xlabel('Number of Unique Attackers', fontsize=12, fontweight='bold')
ax.set_title('Unique Attackers per Pool', fontsize=13, fontweight='bold')
grid_text = '\n'.join([f"{pool}: {count}" for pool, count in pool_attackers.items()])
ax.grid(axis='x', alpha=0.3)

# Plot 2: Attack frequency distribution
ax = axes[0, 1]
pool_freq = df_mev['pool'].value_counts()
pool_freq_sorted = pool_freq.sort_values(ascending=False)
ax.bar(range(len(pool_freq_sorted)), pool_freq_sorted.values, color='teal', alpha=0.7)
ax.set_xticks(range(len(pool_freq_sorted)))
ax.set_xticklabels(pool_freq_sorted.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Attack Count', fontsize=12, fontweight='bold')
ax.set_title('Attack Frequency by Pool', fontsize=13, fontweight='bold')
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(pool_freq_sorted.values):
    ax.text(i, v + 2, str(v), ha='center', fontweight='bold', fontsize=10)

# Plot 3: Profit concentration analysis
ax = axes[1, 0]
profit_data = df_mev.groupby('pool')['net_profit_sol'].agg(['sum', 'mean', 'count'])
profit_data = profit_data.sort_values('sum', ascending=False)

x = np.arange(len(profit_data))
width = 0.35

bars1 = ax.bar(x - width/2, profit_data['sum'], width, label='Total Profit (SOL)', color='gold', alpha=0.8)
ax2_twin = ax.twinx()
bars2 = ax2_twin.bar(x + width/2, profit_data['mean'], width, label='Avg Profit per Attack (SOL)', 
                     color='crimson', alpha=0.8)

ax.set_xlabel('Pool', fontsize=10, fontweight='bold')
ax.set_ylabel('Total Profit (SOL)', fontsize=12, fontweight='bold', color='gold')
ax2_twin.set_ylabel('Average Profit (SOL)', fontsize=12, fontweight='bold', color='crimson')
ax.set_title('Profit Analysis: Total vs Average', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(profit_data.index, rotation=45, ha='right', fontsize=10)

ax.tick_params(axis='y', labelcolor='gold')
ax2_twin.tick_params(axis='y', labelcolor='crimson')
ax.grid(axis='y', alpha=0.3)

# Plot 4: Contagion matrix heatmap
ax = axes[1, 1]

# Create a contagion matrix showing shared attackers between pools
pools_list = df_mev['pool'].unique()
contagion_matrix = np.zeros((len(pools_list), len(pools_list)))

for i, pool1 in enumerate(pools_list):
    for j, pool2 in enumerate(pools_list):
        attackers_pool1 = set(df_mev[df_mev['pool'] == pool1]['signer'].unique())
        attackers_pool2 = set(df_mev[df_mev['pool'] == pool2]['signer'].unique())
        overlap = len(attackers_pool1 & attackers_pool2)
        contagion_matrix[i, j] = overlap

sns.heatmap(contagion_matrix, annot=True, fmt='g', cmap='YlOrRd', ax=ax,
            xticklabels=pools_list, yticklabels=pools_list, cbar_kws={'label': 'Shared Attackers'},
            annot_kws={'fontsize': 10})
ax.set_title('Contagion Matrix: Shared Attackers Between Pools', fontsize=13, fontweight='bold')
ax.set_xlabel('Pool', fontsize=12, fontweight='bold')
ax.set_ylabel('Pool', fontsize=12, fontweight='bold')

plt.tight_layout()

network_path = output_dir / 'pool_coordination_network.png'
plt.savefig(network_path, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {network_path}")
plt.close()

print("\n" + "="*80)
print("✅ CONTAGION VISUALIZATIONS GENERATED SUCCESSFULLY")
print("="*80)
print(f"\nGenerated files:")
print(f"  1. {dashboard_path}")
print(f"  2. {network_path}")
print(f"\nFiles ready for integration into PDF report")
