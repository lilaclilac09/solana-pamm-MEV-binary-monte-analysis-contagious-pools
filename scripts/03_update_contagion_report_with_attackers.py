import json
import pandas as pd

# Load your current report + top attackers
with open('contagion_report.json') as f:
    report = json.load(f)

df = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')

# Add top attackers section
top_df = df.groupby('attacker_signer').agg(total_profit=('profit_sol','sum'), attacks=('attacker_signer','count')).nlargest(20, 'total_profit')

report['top_attackers_section'] = {
    "generated_at": "2026-02-24",
    "top_20": top_df.to_dict('records'),
    "total_unique_attackers_in_dataset": len(df['attacker_signer'].unique())
}

with open('contagion_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("✅ contagion_report.json updated with real attacker_signer stats")
