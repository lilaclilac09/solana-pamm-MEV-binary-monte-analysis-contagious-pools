#!/usr/bin/env python3
"""
Generate Contagion Analysis Plots
Saves:
 - contagion_analysis_dashboard.png
 - pool_coordination_network.png

Usage: python3 scripts/generate_contagion_plots.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys

sys.path.insert(0, '.')
from contagious_vulnerability_analyzer import ContagiousVulnerabilityAnalyzer

sns.set_style('whitegrid')

OUT_DASH = Path('contagion_analysis_dashboard.png')
OUT_NET = Path('pool_coordination_network.png')

analyzer = ContagiousVulnerabilityAnalyzer()
mev_path = '02_mev_detection/per_pamm_all_mev_with_validator.csv'
if not Path(mev_path).exists():
    raise SystemExit(f"MEV data not found: {mev_path}")

mev_df = analyzer.load_mev_data(mev_path)
# Identify trigger pool
trigger_info = analyzer.identify_trigger_pool(mev_df)
trigger_pool = trigger_info.get('trigger_pool') or mev_df['pool'].mode().iloc[0]

# Cascade & probs
cascade = analyzer.analyze_cascade_rates(mev_df, trigger_pool=trigger_pool, time_window_ms=5000)
probs = analyzer.calculate_attack_probability(mev_df, trigger_pool=trigger_pool)

# Prepare data
top_pools = mev_df['pool'].value_counts().head(10)
probs_sorted = sorted(probs.get('downstream_attack_probabilities', []), key=lambda x: x['attack_probability_pct'], reverse=True)[:8]
sequences = cascade.get('cascade_sequences', [])

# Dashboard
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Contagious Vulnerability Dashboard', fontsize=16, fontweight='bold')

# Top attacked pools
ax = axes[0,0]
top_pools.plot(kind='barh', ax=ax, color='steelblue')
ax.set_title('Top Attacked Pools')
ax.set_xlabel('Number of Attacks')
ax.invert_yaxis()

# Cascade rate
ax = axes[0,1]
cascade_pct = cascade.get('cascade_rates', {}).get('cascade_percentage', 0.0)
color = '#d32f2f' if cascade_pct > 75 else '#ffa726' if cascade_pct > 50 else '#66bb6a'
ax.barh(['Cascade Rate'], [cascade_pct], color=color)
ax.set_xlim(0, 100)
ax.set_xlabel('Percentage (%)')
ax.set_title(f'Cascade Rate (trigger={trigger_pool})')
ax.text(cascade_pct/2, 0, f'{cascade_pct:.1f}%', ha='center', va='center', color='white', fontsize=14, fontweight='bold')

# Downstream probabilities
ax = axes[1,0]
if probs_sorted:
    names = [p['downstream_pool'][:30] for p in probs_sorted]
    vals = [p['attack_probability_pct'] for p in probs_sorted]
    colors = ['#d32f2f' if v>80 else '#ffa726' if v>50 else '#66bb6a' for v in vals]
    ax.barh(names, vals, color=colors)
    ax.set_title('P(downstream | trigger)')
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
else:
    ax.text(0.5, 0.5, 'No downstream probability data', ha='center', va='center', transform=ax.transAxes)

# Time lag distribution
ax = axes[1,1]
time_lags = [s['time_lag_ms'] for s in sequences if s.get('time_lag_ms') is not None]
if time_lags:
    ax.hist(time_lags, bins=30, color='steelblue', edgecolor='black')
    ax.set_title('Cascade Time Lag Distribution (ms)')
    ax.set_xlabel('Time Lag (ms)')
    ax.set_ylabel('Frequency')
    ax.axvline(np.median(time_lags), color='red', linestyle='--', label=f"Median {np.median(time_lags):.0f}ms")
    ax.legend()
else:
    ax.text(0.5, 0.5, 'No cascade sequences found', ha='center', va='center', transform=ax.transAxes)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(OUT_DASH, dpi=150, bbox_inches='tight')
print(f"Saved dashboard to {OUT_DASH}")

# Pool coordination network heatmap
out = Path(OUT_NET)
attack_matrix = pd.crosstab(mev_df['attacker_address'], mev_df['pool'])
# Correlation between pools
pool_corr = attack_matrix.corr()
# Limit to top pools
top_pool_names = mev_df['pool'].value_counts().head(12).index.tolist()
pool_corr_sub = pool_corr.loc[top_pool_names, top_pool_names]

plt.figure(figsize=(10,8))
sns.heatmap(pool_corr_sub, annot=True, fmt='.2f', cmap='RdYlGn', center=0, linewidths=0.5)
plt.title('Pool Coordination (Attacker Correlation)')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f"Saved network heatmap to {out}")

print('Done')
