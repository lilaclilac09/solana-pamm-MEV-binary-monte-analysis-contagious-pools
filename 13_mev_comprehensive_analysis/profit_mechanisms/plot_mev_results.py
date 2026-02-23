"""
Generate visualizations from MEV analysis outputs.
Creates PNGs in `outputs/plots/`:
- profit_by_pool.png
- top_attackers.png
- profit_distribution.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set(style='whitegrid')

OUT_DIR = Path('outputs/plots')
OUT_DIR.mkdir(parents=True, exist_ok=True)

MEV_SUMMARY = Path('outputs/mev_profit_summary.csv')
ATTACKER_STATS = Path('outputs/attacker_statistics.csv')

# Read data
if not MEV_SUMMARY.exists():
    raise FileNotFoundError(f"{MEV_SUMMARY} not found. Run mev_profit_analysis.py first.")

mev = pd.read_csv(MEV_SUMMARY)
attackers = pd.read_csv(ATTACKER_STATS)

# Profit by pool
plt.figure(figsize=(8,5))
pool_sum = mev.groupby('amm_trade')['net_profit_sol'].sum().sort_values(ascending=False)
sns.barplot(x=pool_sum.values, y=pool_sum.index, palette='viridis')
plt.xlabel('Total Net Profit (SOL)')
plt.ylabel('Pool')
plt.title('Total Net Profit by AMM Pool')
plt.tight_layout()
plt.savefig(OUT_DIR / 'profit_by_pool.png', dpi=200)
plt.close()

# Top attackers (by total_profit in attacker stats)
attackers_sorted = attackers.sort_values('total_profit', ascending=False).head(10).copy()
plt.figure(figsize=(8,5))
# Create readable labels by truncating signer addresses
if 'attacker_signer' in attackers_sorted.columns:
    attackers_sorted['label'] = attackers_sorted['attacker_signer'].apply(lambda s: str(s)[:16] + '...')
else:
    attackers_sorted['label'] = attackers_sorted.index.map(lambda s: str(s)[:16] + '...')

sns.barplot(x='total_profit', y='label', data=attackers_sorted, palette='magma')
plt.xlabel('Total Net Profit (SOL)')
plt.ylabel('Attacker (truncated)')
plt.title('Top 10 Attackers by Total Profit')
plt.tight_layout()
plt.savefig(OUT_DIR / 'top_attackers.png', dpi=200)
plt.close()

# Profit distribution histogram
plt.figure(figsize=(7,5))
sns.histplot(mev['net_profit_sol'], bins=10, kde=False, color='steelblue')
plt.xlabel('Net Profit (SOL)')
plt.ylabel('Count')
plt.title('Distribution of Net Profit per Attack')
plt.tight_layout()
plt.savefig(OUT_DIR / 'profit_distribution.png', dpi=200)
plt.close()

print('Plots saved to', OUT_DIR)
