"""
Extended Visualization: Validator-Level MEV Contagion Overlay
Analyzes which validators enable fat sandwich attacks and identifies contagion patterns
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter

ROOT = '/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis'
INPUT_FAT = os.path.join(ROOT, '13_mev_comprehensive_analysis', 'outputs', 'from_02_mev_detection', 'all_fat_sandwich_only.csv')
OUT_DIR = os.path.join(ROOT, '02_mev_detection', 'filtered_output', 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

print('[1] Loading fat sandwich data...')
fat_df = pd.read_csv(INPUT_FAT)
print(f'Loaded {len(fat_df)} fat sandwich cases')

# Identify columns
amm_col = 'amm_trade' if 'amm_trade' in fat_df.columns else 'amm'
validator_col = 'validator' if 'validator' in fat_df.columns else None
attacker_col = 'attacker_signer' if 'attacker_signer' in fat_df.columns else 'attacker'
profit_col = 'net_profit_sol' if 'net_profit_sol' in fat_df.columns else 'profit_sol'

if validator_col not in fat_df.columns:
    print('ERROR: no validator column found')
    print('Available columns:', fat_df.columns.tolist())
    exit(1)

# === PLOT 1: Top 15 Validators by Fat Sandwich Count ===
print('[2] Creating validator activity plot...')
val_counts = fat_df[validator_col].value_counts().head(15)
plt.figure(figsize=(10, 6))
val_counts.plot(kind='barh', color='steelblue')
plt.title('Top 15 Validators Processing Fat Sandwich Attacks')
plt.xlabel('Number of Fat Sandwich Cases')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_activity_top15.png'), dpi=150)
plt.close()
print(f'WROTE validator_activity_top15.png')

# === PLOT 2: Top 15 Validators by Total MEV Profit ===
print('[3] Creating validator profit plot...')
val_profit = fat_df.groupby(validator_col)[profit_col].sum().sort_values(ascending=False).head(15)
plt.figure(figsize=(10, 6))
val_profit.plot(kind='barh', color='coral')
plt.title('Top 15 Validators by Total Fat Sandwich Profit (SOL)')
plt.xlabel('Total Profit (SOL)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_profit_top15.png'), dpi=150)
plt.close()
print(f'WROTE validator_profit_top15.png')

# === PLOT 3: Validator-AMM Contagion Heatmap ===
print('[4] Creating validator-AMM contagion heatmap...')
# Create cross-tab of validators x AMMs showing case counts
top_validators = fat_df[validator_col].value_counts().head(10).index
top_amms = fat_df[amm_col].value_counts().head(8).index
pivot_data = fat_df[fat_df[validator_col].isin(top_validators)].copy()
heatmap = pd.crosstab(pivot_data[validator_col], pivot_data[amm_col])
# Filter to top amms
heatmap = heatmap[[col for col in heatmap.columns if col in top_amms]]
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap, annot=True, fmt='d', cmap='YlOrRd', cbar_kws={'label': 'Case Count'})
plt.title('Validator-AMM Contagion Matrix (Top 10 Validators × Top 8 AMMs)')
plt.xlabel('AMM')
plt.ylabel('Validator')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_amm_contagion_heatmap.png'), dpi=150)
plt.close()
print(f'WROTE validator_amm_contagion_heatmap.png')

# === PLOT 4: Validator Profit Concentration (Gini-like) ===
print('[5] Creating validator profit concentration plot...')
val_profit_all = fat_df.groupby(validator_col)[profit_col].sum().sort_values(ascending=False)
cumsum = val_profit_all.cumsum() / val_profit_all.sum()
plt.figure(figsize=(10, 6))
plt.plot(range(len(cumsum)), cumsum.values, marker='o', linestyle='-', linewidth=2, markersize=4, color='darkgreen')
plt.axhline(y=0.8, color='red', linestyle='--', label='80% of profit')
plt.xlabel('Number of Validators (sorted by profit)')
plt.ylabel('Cumulative Profit Share')
plt.title('Validator Profit Concentration (Lorenz-style curve)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_profit_concentration.png'), dpi=150)
plt.close()
print(f'WROTE validator_profit_concentration.png')

# === PLOT 5: Attacker Diversity per Validator ===
print('[6] Creating attacker diversity plot...')
# For each top validator, count unique attackers
top_vals = fat_df[validator_col].value_counts().head(12).index
attacker_diversity = {}
for val in top_vals:
    subset = fat_df[fat_df[validator_col] == val]
    attacker_diversity[val] = len(subset[attacker_col].unique())
attacker_diversity = dict(sorted(attacker_diversity.items(), key=lambda x: x[1], reverse=True))
plt.figure(figsize=(10, 6))
plt.barh(list(range(len(attacker_diversity))), list(attacker_diversity.values()), color='mediumpurple')
plt.yticks(range(len(attacker_diversity)), list(attacker_diversity.keys()), fontsize=8)
plt.xlabel('Number of Unique Attackers')
plt.title('Attacker Diversity by Validator (Top 12 by Case Count)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_attacker_diversity.png'), dpi=150)
plt.close()
print(f'WROTE validator_attacker_diversity.png')

# === PLOT 6: Average Profit per Case by Validator ===
print('[7] Creating average profit per case plot...')
val_avg_profit = fat_df.groupby(validator_col)[profit_col].mean().sort_values(ascending=False).head(12)
plt.figure(figsize=(10, 6))
val_avg_profit.plot(kind='barh', color='teal')
plt.title('Average Fat Sandwich Profit per Case by Validator (Top 12)')
plt.xlabel('Average Profit (SOL)')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_avg_profit_per_case.png'), dpi=150)
plt.close()
print(f'WROTE validator_avg_profit_per_case.png')

# === PLOT 7: Validator-Specific AMM Targeting ===
print('[8] Creating validator specialization plot...')
# For each top validator, which AMM is targeted most?
top_vals_spec = fat_df[validator_col].value_counts().head(8).index
spec_data = []
for val in top_vals_spec:
    subset = fat_df[fat_df[validator_col] == val]
    top_amm = subset[amm_col].value_counts().index[0]
    top_amm_count = subset[amm_col].value_counts().values[0]
    total_count = len(subset)
    spec_data.append({'validator': val[:20], 'top_amm': top_amm, 'cases': top_amm_count, 'total': total_count})
spec_df = pd.DataFrame(spec_data)
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(spec_df))
width = 0.6
bars = ax.bar(x, spec_df['cases'], width, label='Top Target AMM Cases', color='indianred')
ax.set_ylabel('Cases')
ax.set_title('Validator Specialization: Top Targeted AMM per Validator')
ax.set_xticks(x)
ax.set_xticklabels([f"{r['validator']}\n({r['top_amm']})" for _, r in spec_df.iterrows()], fontsize=8, rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'validator_specialization.png'), dpi=150)
plt.close()
print(f'WROTE validator_specialization.png')

# === PLOT 8: Confidence Distribution by Validator ===
print('[9] Creating validator confidence plot...')
if 'confidence' in fat_df.columns:
    confidence_by_val = pd.crosstab(fat_df[validator_col], fat_df['confidence'])
    top_vals_conf = fat_df[validator_col].value_counts().head(10).index
    confidence_by_val = confidence_by_val.loc[top_vals_conf]
    fig, ax = plt.subplots(figsize=(10, 6))
    confidence_by_val.plot(kind='bar', stacked=True, ax=ax, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.title('Confidence Levels by Top Validators')
    plt.xlabel('Validator')
    plt.ylabel('Cases')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.legend(title='Confidence', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'validator_confidence_distribution.png'), dpi=150)
    plt.close()
    print(f'WROTE validator_confidence_distribution.png')

# === Output Summary Report ===
print('\n' + '=' * 80)
print('VALIDATOR CONTAGION ANALYSIS SUMMARY')
print('=' * 80)
print(f'\nTotal Fat Sandwich Cases: {len(fat_df)}')
print(f'Unique Validators: {fat_df[validator_col].nunique()}')
print(f'Unique Attackers: {fat_df[attacker_col].nunique()}')
print(f'Total Profit: {fat_df[profit_col].sum():.2f} SOL')

print('\nTOP 5 VALIDATORS BY CASE COUNT:')
for i, (val, count) in enumerate(fat_df[validator_col].value_counts().head(5).items(), 1):
    profit = fat_df[fat_df[validator_col] == val][profit_col].sum()
    pct = (count / len(fat_df)) * 100
    print(f'  {i}. {val}: {count} cases ({pct:.1f}%) - {profit:.3f} SOL')

print('\nTOP 5 VALIDATORS BY TOTAL PROFIT:')
val_profit_sorted = fat_df.groupby(validator_col)[profit_col].sum().sort_values(ascending=False)
for i, (val, profit) in enumerate(val_profit_sorted.head(5).items(), 1):
    count = len(fat_df[fat_df[validator_col] == val])
    pct = (profit / fat_df[profit_col].sum()) * 100
    print(f'  {i}. {val}: {profit:.3f} SOL ({pct:.1f}%) - {count} cases')

print('\nCONTAGION INDICATORS:')
# Calculate contagion: validators hitting multiple AMMs
multi_amm_validators = {}
for val in fat_df[validator_col].unique():
    subset = fat_df[fat_df[validator_col] == val]
    amm_count = subset[amm_col].nunique()
    attack_count = len(subset)
    if amm_count > 1:
        multi_amm_validators[val] = (amm_count, attack_count)

multi_amm_validators = dict(sorted(multi_amm_validators.items(), key=lambda x: x[0], reverse=True))
print(f'  Validators hitting multiple AMMs: {len(multi_amm_validators)}')
print(f'  Top 5 multi-AMM validators:')
for val, (amm_count, attack_count) in list(multi_amm_validators.items())[:5]:
    print(f'    - {val}: {amm_count} AMMs, {attack_count} attacks')

# Calculate attacker specialization
print('\nATTACKER SPECIALIZATION:')
attacker_validator_pairs = fat_df.groupby([attacker_col, validator_col]).size().reset_index(name='count')
repeat_attackers = attacker_validator_pairs[attacker_validator_pairs['count'] > 5].sort_values('count', ascending=False)
print(f'  Attacker-Validator pairs (>5 cases): {len(repeat_attackers)}')
print(f'  Top 5 repeat attacker-validator pairs:')
for _, row in repeat_attackers.head(5).iterrows():
    print(f'    - {row[attacker_col][:20]}... + {row[validator_col][:20]}...: {row["count"]} cases')

print('\n' + '=' * 80)
print('All visualizations saved to:', OUT_DIR)
print('=' * 80)
