import json
import pandas as pd

with open('validator_contagion_graph.json') as f:
    graph = json.load(f)

# Assume graph has "validators" list with win_rate, amm, etc.
df = pd.DataFrame(graph.get('validator_amm_pairs', []))

winrate = (df.groupby('prop_amm')
           .agg(avg_win_rate=('win_rate', 'mean'),
                total_blocks=('block_count', 'sum'))
           .round(4)
           .sort_values('avg_win_rate', ascending=False))

winrate.to_csv('outputs/validator_winrate_per_prop_amm.csv')
print(winrate)
