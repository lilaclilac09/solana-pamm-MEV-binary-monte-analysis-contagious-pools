import json
import pandas as pd

# Load your current report
with open('contagion_report.json') as f:
    report = json.load(f)

# Load real attacker statistics
df = pd.read_csv('13_mev_comprehensive_analysis/profit_mechanisms/outputs/attacker_statistics.csv')

# Get top 20 by profit
top_df = df.nlargest(20, 'total_profit')[['attacker_signer', 'total_profit', 'num_attacks', 'fat_sandwiches']].reset_index(drop=True)

report['top_attackers_section'] = {
    "generated_at": "2026-02-24",
    "top_20": top_df.to_dict('records'),
    "total_unique_attackers_in_dataset": len(df['attacker_signer'].unique())
}

with open('contagion_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("✅ contagion_report.json updated with real attacker_signer stats")
