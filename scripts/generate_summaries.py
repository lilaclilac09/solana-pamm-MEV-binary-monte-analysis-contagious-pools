#!/usr/bin/env python3
import pandas as pd
import os

SRC = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/per_pamm_all_mev_with_validator.csv'
OUT_DIR = '02_mev_detection'

if not os.path.exists(SRC):
    print('Source CSV not found:', SRC)
    raise SystemExit(1)

print('Reading', SRC)
df = pd.read_csv(SRC)
print('Rows:', len(df))

os.makedirs(OUT_DIR, exist_ok=True)

# Pool summary
pool_summary = []
for pool in sorted(df['amm_trade'].unique()):
    pool_data = df[df['amm_trade']==pool]
    pool_summary.append({
        'pool':pool,
        'unique_attackers': pool_data['attacker_signer'].nunique(),
        'unique_validators': pool_data['validator'].nunique(),
        'total_mev_events': len(pool_data),
        'total_fat_sandwiches': int(pool_data['fat_sandwich'].sum()),
        'total_sandwiches': int(pool_data['sandwich'].sum()),
        'total_front_runs': int(pool_data['front_running'].sum()),
        'total_back_runs': int(pool_data['back_running'].sum()),
        'total_profit_sol': round(pool_data['profit_sol'].sum(),4),
        'total_cost_sol': round(pool_data['cost_sol'].sum(),4),
        'net_profit_sol': round(pool_data['net_profit_sol'].sum(),4),
        'avg_profit_per_event': round(pool_data['profit_sol'].mean(),4),
        'high_confidence_events': int((pool_data['confidence']=='high').sum()),
        'medium_confidence_events': int((pool_data['confidence']=='medium').sum()),
    })

pd.DataFrame(pool_summary).to_csv(os.path.join(OUT_DIR,'POOL_SUMMARY.csv'), index=False)

# Validator participation
val = df.groupby(['amm_trade','validator']).agg({'attacker_signer':'nunique','profit_sol':'sum','net_profit_sol':'sum','fat_sandwich':'sum'}).reset_index()
val.columns=['pool','validator','attacker_count','total_profit','net_profit','fat_sandwiches']
val.sort_values(['pool','net_profit'],ascending=[True,False]).to_csv(os.path.join(OUT_DIR,'VALIDATOR_POOL_PARTICIPATION.csv'), index=False)

# Attacker keys
attackers=[]
for pool in sorted(df['amm_trade'].unique()):
    for attacker in df[df['amm_trade']==pool]['attacker_signer'].unique():
        d = df[(df['amm_trade']==pool)&(df['attacker_signer']==attacker)]
        attackers.append({'pool':pool,'attacker_key':attacker,'event_count':len(d),'total_profit':round(d['profit_sol'].sum(),4),'net_profit':round(d['net_profit_sol'].sum(),4)})

pd.DataFrame(attackers).to_csv(os.path.join(OUT_DIR,'ATTACKER_KEYS_BY_POOL.csv'), index=False)

print('Wrote summaries into', OUT_DIR)
