#!/usr/bin/env python3
"""
Create comparison plots for top MEV attackers and validators.

Outputs:
 - outputs/plots/top_attackers.png
 - outputs/plots/top_validators.png
 - outputs/plots/top_attackers_full.csv
 - outputs/plots/top_validators_full.csv
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

OUT_DIR = "outputs/plots"
os.makedirs(OUT_DIR, exist_ok=True)

def try_read(paths):
    for p in paths:
        if os.path.exists(p):
            try:
                return pd.read_csv(p)
            except Exception:
                pass
    return None

# Candidate sources (found in repo)
attacker_stats_paths = [
    "13_mev_comprehensive_analysis/profit_mechanisms/outputs/attacker_statistics.csv",
    "12_mev_profit_mechanisms/outputs/attacker_statistics.csv",
]
validators_paths = [
    "06_pool_analysis/outputs/mev_risk_by_validator.csv",
]
events_paths = [
    "13_mev_comprehensive_analysis/outputs/from_02_mev_detection/per_pamm_all_mev_with_validator.csv",
    "02_mev_detection/per_pamm_all_mev_with_validator.csv",
]

att_df = try_read(attacker_stats_paths)
val_df = try_read(validators_paths)
evt_df = try_read(events_paths)

if att_df is None and val_df is None and evt_df is None:
    raise SystemExit("No source CSVs found. Check paths in script.")

print("Dataframes loaded:")
print(" - attacker_stats:", 'yes' if att_df is not None else 'no')
print(" - mev_risk_by_validator:", 'yes' if val_df is not None else 'no')
print(" - event-level per_pamm:", 'yes' if evt_df is not None else 'no')

# Top attackers
if att_df is not None:
    # Ensure numeric column name variants
    if 'total_profit' in att_df.columns:
        profit_col = 'total_profit'
    elif 'total_profit_sol' in att_df.columns:
        profit_col = 'total_profit_sol'
    else:
        # try a generic profit-like column
        profit_col = next((c for c in att_df.columns if 'profit' in c.lower()), None)

    topN = 15
    if profit_col:
        top_att = att_df.sort_values(profit_col, ascending=False).head(topN).copy()
    else:
        top_att = att_df.head(topN).copy()

    # Save full CSV of top attackers (full addresses preserved)
    top_att.to_csv(os.path.join(OUT_DIR, 'top_attackers_full.csv'), index=False)

    plt.figure(figsize=(12,6))
    x = top_att.iloc[:,0].astype(str)
    y = top_att[profit_col] if profit_col else range(len(x))
    sns.barplot(x=y, y=x, palette='viridis')
    plt.xlabel(profit_col or 'index')
    plt.ylabel('attacker_signer (full address)')
    plt.title('Top attackers by {}'.format(profit_col or 'index'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'top_attackers.png'), dpi=150)
    print('Saved:', os.path.join(OUT_DIR, 'top_attackers.png'))

# Top validators
if val_df is not None:
    # prefer mev_risk_score or net_profit_sol
    score_col = 'mev_risk_score' if 'mev_risk_score' in val_df.columns else (
        'net_profit_sol' if 'net_profit_sol' in val_df.columns else None
    )
    topN = 15
    if score_col:
        top_val = val_df.sort_values(score_col, ascending=False).head(topN).copy()
    else:
        top_val = val_df.head(topN).copy()

    top_val.to_csv(os.path.join(OUT_DIR, 'top_validators_full.csv'), index=False)

    plt.figure(figsize=(12,6))
    x = top_val.iloc[:,0].astype(str)
    y = top_val[score_col] if score_col else range(len(x))
    sns.barplot(x=y, y=x, palette='magma')
    plt.xlabel(score_col or 'index')
    plt.ylabel('validator (full address)')
    plt.title('Top validators by {}'.format(score_col or 'index'))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'top_validators.png'), dpi=150)
    print('Saved:', os.path.join(OUT_DIR, 'top_validators.png'))

# Optional: event-level summary comparisons
if evt_df is not None:
    # count events per attacker_signer or validator
    if 'attacker_signer' in evt_df.columns:
        s = evt_df['attacker_signer'].value_counts().head(20)
        s = s.reset_index()
        s.columns = ['attacker_signer','count']
        s.to_csv(os.path.join(OUT_DIR,'top_attackers_by_event_count.csv'), index=False)
        plt.figure(figsize=(10,6))
        sns.barplot(x='count', y='attacker_signer', data=s, palette='cubehelix')
        plt.title('Top attackers by event count (top 20)')
        plt.tight_layout()
        plt.savefig(os.path.join(OUT_DIR,'top_attackers_by_event_count.png'), dpi=150)
        print('Saved:', os.path.join(OUT_DIR,'top_attackers_by_event_count.png'))

print('\nAll plots and CSV summaries saved to', OUT_DIR)

if __name__ == '__main__':
    pass
"""
Plot MEV CSVs and produce cross-comparison PNGs.
Saves plots to: 02_mev_detection/filtered_output/plots/
"""
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='whitegrid')

BASE = Path(__file__).resolve().parents[0]
MEV_DIR = BASE.parent / '02_mev_detection'
FILTERED = MEV_DIR / 'filtered_output'
PLOTS_DIR = FILTERED / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Files
files = {
    'all_fat': FILTERED / 'all_fat_sandwich_only.csv',
    'all_mev': FILTERED / 'all_mev_with_classification.csv',
    'top20': FILTERED / 'top20_profit_fat_sandwich.csv',
    'top10': FILTERED / 'top10_mev_with_classification.csv'
}

for k,f in files.items():
    if not f.exists():
        raise SystemExit(f"Required file missing: {f}")

# Load
df_fat = pd.read_csv(files['all_fat'])
df_all = pd.read_csv(files['all_mev'])
df_top20 = pd.read_csv(files['top20'])
df_top10 = pd.read_csv(files['top10'])

# Ensure numeric
for col in ['net_profit_sol','profit_sol','cost_sol']:
    for df in (df_fat, df_all, df_top20, df_top10):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

# 1) Bar: Fat Sandwich count per AMM
plt.figure(figsize=(10,6))
order = df_fat['amm_trade'].value_counts().index
ax = sns.countplot(data=df_fat, x='amm_trade', order=order, palette='tab10')
ax.set_title('Fat Sandwich Cases per AMM')
ax.set_ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'fat_sandwich_count_per_amm.png')
plt.close()

# 2) Distribution: Net profit per AMM (boxplot, log-scale)
plt.figure(figsize=(10,6))
df_box = df_fat.copy()
# keep positive profits only
df_box = df_box[df_box['net_profit_sol'] > 0]
ax = sns.boxplot(data=df_box, x='amm_trade', y='net_profit_sol', order=order, palette='tab10')
ax.set_yscale('symlog')
ax.set_title('Net Profit Distribution per AMM (symlog scale)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'net_profit_distribution_per_amm.png')
plt.close()

# 3) Histogram: net_profit overall (fat sandwiches)
plt.figure(figsize=(8,5))
sns.histplot(df_box['net_profit_sol'], bins=50, log_scale=(True, False))
plt.title('Net Profit Distribution (Fat Sandwiches)')
plt.xlabel('Net Profit (SOL)')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'net_profit_histogram_fat.png')
plt.close()

# 4) Pie / bar: classification breakdown (all_mev)
plt.figure(figsize=(7,5))
counts = df_all['classification'].value_counts()
counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, explode=[0.05]*len(counts))
plt.title('MEV Classification Breakdown')
plt.ylabel('')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'classification_breakdown_pie.png')
plt.close()

# 5) Top20: bar of top profits
plt.figure(figsize=(10,6))
df_top20_sorted = df_top20.sort_values('net_profit_sol', ascending=False).head(20)
sns.barplot(data=df_top20_sorted, x='net_profit_sol', y='attacker_signer', palette='magma')
plt.title('Top 20 Fat Sandwich Cases by Net Profit')
plt.xlabel('Net Profit (SOL)')
plt.ylabel('Attacker (truncated)')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'top20_net_profit_bar.png')
plt.close()

# 6) Confidence breakdown per AMM (stacked counts)
if 'confidence' in df_fat.columns:
    conf = df_fat.groupby(['amm_trade','confidence']).size().unstack(fill_value=0)
    conf.plot(kind='bar', stacked=True, figsize=(10,6), colormap='tab20')
    plt.title('Confidence Levels per AMM (Fat Sandwich)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'confidence_per_amm_stacked.png')
    plt.close()

# 7) Cross-comparison table plot: counts and max profit per AMM
summary = df_fat.groupby('amm_trade').agg(count=('attacker_signer','count'), max_profit=('net_profit_sol','max')).reset_index()
summary = summary.sort_values('count', ascending=False)
plt.figure(figsize=(10,6))
ax = sns.barplot(data=summary, x='amm_trade', y='count', palette='tab10')
ax2 = ax.twinx()
sns.pointplot(data=summary, x='amm_trade', y='max_profit', color='black', ax=ax2)
ax.set_title('AMM Comparison: Count (bars) and Max Profit (points)')
ax.set_ylabel('Count')
ax2.set_ylabel('Max Net Profit (SOL)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'amm_count_and_maxprofit.png')
plt.close()

# Save summary CSV
summary.to_csv(FILTERED / 'amm_summary_counts_maxprofit.csv', index=False)

# Print small console summary
print('Plots saved to:', PLOTS_DIR)
print('\nSummary (per AMM):')
print(summary.to_string(index=False))
print('\nTop files created:')
for p in sorted(PLOTS_DIR.glob('*.png')):
    print(' -', p.name)
