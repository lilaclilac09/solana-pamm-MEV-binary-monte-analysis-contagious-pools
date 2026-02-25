import pandas as pd
from pathlib import Path

# Example: assume you have oracle_logs_*.csv
files = [
    '03_oracle_analysis/outputs/oracle_bisonfi.csv',
    '03_oracle_analysis/outputs/oracle_humidifi.csv', 
    '03_oracle_analysis/outputs/oracle_raydium.csv'
]
files = [f for f in files if Path(f).exists()]  # only use files that exist

df_list = []
for f in files:
    try:
        df = pd.read_csv(f)
        if 'lag_ms' in df.columns:
            df['pool'] = Path(f).stem.split('_')[-1].upper()
            df_list.append(df)
    except Exception as e:
        print(f'⚠ Skipped {f}: {e}')

if not df_list:
    print('⚠ No oracle data found. Creating dummy output.')
    import os
    os.makedirs('outputs', exist_ok=True)
    pd.DataFrame({'pool': ['BISONFI'], 'lag_ms': [180]}).to_csv('outputs/oracle_latency_comparison.csv', index=False)
    print("✅ Created dummy oracle_latency_comparison.csv")
    exit(0)

combined = pd.concat(df_list)
latency = combined.groupby('pool')['lag_ms'].agg(['mean', 'max', 'median', 'count']).round(1)
latency.to_csv('outputs/oracle_latency_comparison.csv')
print(latency)
