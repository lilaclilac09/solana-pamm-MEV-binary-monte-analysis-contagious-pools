import numpy as np
import pandas as pd
import json

# Load top attackers weights from script 3
with open('outputs/top_attackers_report.json') as f:
    attackers = json.load(f)

# Example weights (normalize)
weights = [a['total_profit'] for a in attackers[:10]]
weights = np.array(weights) / sum(weights)

def monte_carlo_weighted(n_sims=50000):
    results = []
    for _ in range(n_sims):
        attacker_idx = np.random.choice(len(weights), p=weights)
        trigger = np.random.rand() < 0.22  # from your report
        cascades = np.random.binomial(4, 0.801 * 0.35) if trigger else 0  # BAM reduction
        results.append({'attacker_rank': attacker_idx+1, 'cascades': cascades})
    
    df = pd.DataFrame(results)
    print(df.groupby('attacker_rank')['cascades'].mean())
    df.to_csv('outputs/monte_carlo_weighted.csv', index=False)

monte_carlo_weighted()
