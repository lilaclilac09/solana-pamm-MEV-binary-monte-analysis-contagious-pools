import pandas as pd
import json
from datetime import datetime

# === CONFIG ===
PARQUET_PATH = '01_data_cleaning/outputs/pamm_clean_final.parquet'
OUTPUT_JSON = 'outputs/top_attackers_report.json'

# Load your PAMM data (assumes columns: attacker_signer, profit_sol, attack_count, cascade_count, pool)
df = pd.read_parquet(PARQUET_PATH)

# Aggregate
top_attackers = (df.groupby('attacker_signer')
                 .agg(
                     total_profit_sol=('profit_sol', 'sum'),
                     attack_count=('attack_count', 'sum'),      # or len if raw tx
                     cascade_count=('cascade_count', 'sum'),
                     pools_affected=('pool', 'nunique')
                 )
                 .reset_index()
                 .sort_values('total_profit_sol', ascending=False))

# Current known top from sandwiched.me (Feb 23 2026) - auto-updated in next script
known_top = {
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Sandwicher #1",
    "67DZRe7LSwxw66Xtdx5MvaWCgpb4tuY3iuUm4kebSVQZ": "Sandwicher #2",
    # add more from script 2
}

top_attackers['known_name'] = top_attackers['attacker_signer'].map(known_top).fillna('Unknown')

# Save
top_attackers.to_json(OUTPUT_JSON, orient='records', indent=2)
print(f"✅ Top attackers saved → {OUTPUT_JSON}")
print(top_attackers.head(10))
