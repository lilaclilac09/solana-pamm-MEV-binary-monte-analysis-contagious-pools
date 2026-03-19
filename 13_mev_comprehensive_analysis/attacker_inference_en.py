import pandas as pd
import os

# Path to attack CSV
attack_path = os.path.join(os.path.dirname(__file__), 'outputs/from_02_mev_detection/all_fat_sandwich_only.csv')

# Load data
df_attack = pd.read_csv(attack_path)

# Aggregate analysis
summary = df_attack.groupby('attacker_signer').agg(
    event_count=('fat_sandwich', 'sum'),
    profit_sum=('net_profit_sol', 'sum'),
    main_type=('classification', lambda x: x.value_counts().index[0] if len(x) else 'Unknown')
).reset_index()

# English inference
mean_events = summary['event_count'].mean()
def infer(row):
    if row['event_count'] > mean_events:
        return f"Attacker {row['attacker_signer']}: Mainly uses {row['main_type']}, event count {row['event_count']}, profit {row['profit_sum']} SOL."
    else:
        return f"Attacker {row['attacker_signer']}: Low activity, likely normal arbitrage or voting."
summary['inference'] = summary.apply(infer, axis=1)

# Save
summary.to_csv(os.path.join(os.path.dirname(__file__), 'attacker_inference_en.csv'), index=False)
print('Attacker aggregation and inference saved to attacker_inference_en.csv.')
