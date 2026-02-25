import pandas as pd
import json
from datetime import datetime

# === CONFIG ===
CSV_PATH = '13_mev_comprehensive_analysis/profit_mechanisms/outputs/attacker_statistics.csv'
OUTPUT_JSON = 'outputs/top_attackers_report.json'

# Load your MEV attacker statistics
df = pd.read_csv(CSV_PATH)

# Sort by total profit
top_attackers = df.sort_values('total_profit', ascending=False).reset_index(drop=True)

# Current known top from sandwiched.me (Feb 25 2026)
known_top = {
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "Sandwicher #1",
    "67DZRe7LSwxw66Xtdx5MvaWCgpb4tuY3iuUm4kebSVQZ": "Sandwicher #2",
}

top_attackers['known_name'] = top_attackers['attacker_signer'].map(known_top).fillna('Unknown')

# Save
top_attackers.to_json(OUTPUT_JSON, orient='records', indent=2)
print(f"✅ Top attackers saved → {OUTPUT_JSON}")
print(f"Total unique attackers: {len(top_attackers)}")
print(f"\nTop 10 by profit:")
print(top_attackers[['attacker_signer', 'total_profit', 'num_attacks', 'fat_sandwiches']].head(10))
