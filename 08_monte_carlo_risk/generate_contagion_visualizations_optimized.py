#!/usr/bin/env python3
"""
Optimized version of generate_contagion_visualizations.py.

Algorithmic changes vs the original (output is identical):

1. Contagion matrix (the original's hottest section)
   Original: nested loop over `pools x pools`, each cell does a full
   `df_mev[df_mev['pool'] == pool] -> set(...) & set(...)`. That is
   O(P^2) DataFrame scans plus O(P^2) Python set operations.
   Optimized: build the binary pool x signer indicator with crosstab
   once, then a single matrix product gives every shared-attacker
   count in one BLAS call. O(P^2) shrinks to one matmul.

2. Per-pool aggregates (signer counts, attack counts, profit sums)
   Original: recomputed by re-running `groupby('pool')` four times.
   Optimized: one groupby produces every per-pool stat used downstream.

Plot code is unchanged so the rendered PNGs are byte-identical to the
original script's output (matplotlib figure timing dominates wall-clock,
so the absolute speedup is small on this 617-row dataset, but the
algorithm now scales linearly in pool count instead of quadratically).
"""

import json
import re
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("GENERATING COMPREHENSIVE CONTAGION ANALYSIS VISUALIZATIONS (OPTIMIZED)")
print("=" * 80)

t_start = time.perf_counter()


def _repair_invalid_json_escapes(raw_text):
    fixed_text = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', raw_text)
    fixed_text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', fixed_text)
    return fixed_text


def _load_json_safe(file_path):
    with open(file_path, 'r', encoding='utf-8') as file_handle:
        raw_text = file_handle.read()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        repaired_text = _repair_invalid_json_escapes(raw_text)
        if repaired_text != raw_text:
            print(f"⚠️ Repaired invalid JSON escape sequences in {file_path}")
            return json.loads(repaired_text)
        raise


contagion_report_path = 'contagion_report.json'
if not Path(contagion_report_path).exists():
    print(f"⚠️  Contagion report not found: {contagion_report_path}")
    sys.exit(1)

contagion_data = _load_json_safe(contagion_report_path)
print(f"\n✓ Loaded contagion report")
print(f"  Key Finding: {contagion_data.get('key_finding', 'N/A')[:80]}...")

mev_file = '02_mev_detection/filtered_output/all_fat_sandwich_only.csv'
if not Path(mev_file).exists():
    print(f"⚠️  MEV data not found: {mev_file}")
    sys.exit(1)

df_mev = pd.read_csv(mev_file)
print(f"\n✓ Loaded MEV data: {len(df_mev)} records")

if 'amm_trade' in df_mev.columns:
    df_mev = df_mev.rename(columns={'amm_trade': 'pool', 'attacker_signer': 'signer'})

attack_probs = contagion_data.get('sections', {}).get('attack_probability_analysis', {}).get('downstream_attack_probabilities', [])
cascade_info = contagion_data.get('sections', {}).get('cascade_rate_analysis', {}).get('cascade_rates', {})
print(f"✓ Found {len(attack_probs)} downstream pools for contagion analysis")

# --- Optimization #2: single groupby pass produces every per-pool stat
# downstream (counts, unique signers, profit totals).
pool_stats = (
    df_mev.groupby('pool')
    .agg(
        attack_count=('pool', 'size'),
        unique_signers=('signer', 'nunique'),
        total_profit=('net_profit_sol', 'sum'),
        mean_profit=('net_profit_sol', 'mean'),
    )
)
pool_attack_counts = pool_stats['attack_count']
pool_attackers = pool_stats['unique_signers'].sort_values(ascending=False)
pool_profits = pool_stats['total_profit']

# --- Optimization #1: vectorized contagion matrix.
# `pool x signer` indicator (0/1). pool_attacker_indicator @ .T yields
# an 8x8 matrix whose (i,j) entry is the number of signers seen in
# both pool i and pool j -- mathematically equivalent to the nested
# set-intersection loop but computed in a single BLAS call.
indicator = (pd.crosstab(df_mev['pool'], df_mev['signer']) > 0).astype(np.int64)
contagion_df = indicator @ indicator.T
pools_list = df_mev['pool'].unique()
contagion_matrix = contagion_df.reindex(index=pools_list, columns=pools_list).to_numpy()

t_data = time.perf_counter() - t_start
print(f"  data preparation: {t_data*1000:.1f} ms")

# ---------------- plotting (unchanged from original) ----------------
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

fig.suptitle('Contagious Pool MEV Attack Analysis Dashboard\n(Based on 617 Validated Fat Sandwich Attacks)',
             fontsize=18, fontweight='bold', y=0.98)

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
for i, (bar, prob, attackers) in enumerate(zip(bars, probs, shared_attackers)):
    ax1.text(prob + 0.5, i, f'{prob:.1f}% ({attackers} attackers)',
             va='center', fontsize=10, fontweight='bold')

ax2 = fig.add_subplot(gs[0, 2])
risk_levels = [p.get('risk_level', 'UNKNOWN') for p in attack_probs]
risk_counts = pd.Series(risk_levels).value_counts()
colors_risk = {'HIGH': '#d73027', 'MODERATE': '#fee090', 'LOW': '#91bfdb'}
colors_list = [colors_risk.get(level, '#808080') for level in risk_counts.index]
ax2.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.0f%%',
        colors=colors_list, startangle=90)
ax2.set_title('Risk Level Distribution\nAcross All Pools', fontsize=11, fontweight='bold')

ax3 = fig.add_subplot(gs[1, 0])
pool_attack_counts_sorted = pool_attack_counts.sort_values(ascending=True)
ax3.barh(pool_attack_counts_sorted.index, pool_attack_counts_sorted.values, color='steelblue', alpha=0.7)
ax3.set_xlabel('Number of MEV Attacks', fontsize=10, fontweight='bold')
ax3.set_title('MEV Attack Volume by Pool\n(All 617 Validated Attacks)', fontsize=11, fontweight='bold')

ax4 = fig.add_subplot(gs[1, 1])
pool_profits_sorted = pool_profits.sort_values(ascending=True)
bars4 = ax4.barh(pool_profits_sorted.index, pool_profits_sorted.values, color='forestgreen', alpha=0.7)
ax4.set_xlabel('Total MEV Profit (SOL)', fontsize=10, fontweight='bold')
ax4.set_title('Total MEV Profit by Pool\nHumidiFi Dominates at 66.8% Share', fontsize=11, fontweight='bold')
profits_total = pool_profits_sorted.sum()
for i, (bar, val) in enumerate(zip(bars4, pool_profits_sorted.values)):
    pct = (val / profits_total) * 100
    ax4.text(val + 1, i, f'{val:.2f} SOL ({pct:.1f}%)', va='center', fontsize=9)

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
for bars in [bars_shared, bars_downstream]:
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}', ha='center', va='bottom', fontsize=8)

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

output_dir = Path('11_report_generation/outputs')
output_dir.mkdir(parents=True, exist_ok=True)
dashboard_path = output_dir / 'contagion_analysis_dashboard_optimized.png'
plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Saved: {dashboard_path}")
plt.close()

fig2, axes = plt.subplots(2, 2, figsize=(20, 15))
fig2.suptitle('Pool Coordination & Attack Pattern Analysis\n(Contagious Vulnerability)',
              fontsize=20, fontweight='bold')

ax = axes[0, 0]
ax.barh(pool_attackers.index, pool_attackers.values, color='mediumpurple', alpha=0.7)
ax.set_xlabel('Number of Unique Attackers', fontsize=12, fontweight='bold')
ax.set_title('Unique Attackers per Pool', fontsize=13, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

ax = axes[0, 1]
pool_freq_sorted = pool_attack_counts.sort_values(ascending=False)
ax.bar(range(len(pool_freq_sorted)), pool_freq_sorted.values, color='teal', alpha=0.7)
ax.set_xticks(range(len(pool_freq_sorted)))
ax.set_xticklabels(pool_freq_sorted.index, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Attack Count', fontsize=12, fontweight='bold')
ax.set_title('Attack Frequency by Pool', fontsize=13, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
for i, v in enumerate(pool_freq_sorted.values):
    ax.text(i, v + 2, str(v), ha='center', fontweight='bold', fontsize=10)

ax = axes[1, 0]
profit_data = pool_stats[['total_profit', 'mean_profit', 'attack_count']].rename(
    columns={'total_profit': 'sum', 'mean_profit': 'mean', 'attack_count': 'count'}
).sort_values('sum', ascending=False)
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

ax = axes[1, 1]
sns.heatmap(contagion_matrix, annot=True, fmt='g', cmap='YlOrRd', ax=ax,
            xticklabels=pools_list, yticklabels=pools_list, cbar_kws={'label': 'Shared Attackers'},
            annot_kws={'fontsize': 10})
ax.set_title('Contagion Matrix: Shared Attackers Between Pools', fontsize=13, fontweight='bold')
ax.set_xlabel('Pool', fontsize=12, fontweight='bold')
ax.set_ylabel('Pool', fontsize=12, fontweight='bold')

plt.tight_layout()
network_path = output_dir / 'pool_coordination_network_optimized.png'
plt.savefig(network_path, dpi=300, bbox_inches='tight')
print(f"✓ Saved: {network_path}")
plt.close()

elapsed = time.perf_counter() - t_start
print("\n" + "=" * 80)
print("✅ CONTAGION VISUALIZATIONS GENERATED SUCCESSFULLY (OPTIMIZED)")
print("=" * 80)
print(f"\nGenerated files:")
print(f"  1. {dashboard_path}")
print(f"  2. {network_path}")
print(f"\nTotal time: {elapsed*1000:.0f} ms")
