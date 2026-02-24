import pandas as pd

# Example: assume you have oracle_logs_*.csv
files = ['data/oracle_bisonfi.csv', 'data/oracle_humidifi.csv', 'data/oracle_raydium.csv']  # adjust names

df_list = []
for f in files:
    df = pd.read_csv(f)
    df['pool'] = f.split('_')[1].split('.')[0].upper()
    df_list.append(df)

combined = pd.concat(df_list)
latency = combined.groupby('pool')['lag_ms'].agg(['mean', 'max', 'median', 'count']).round(1)
latency.to_csv('outputs/oracle_latency_comparison.csv')
print(latency)
