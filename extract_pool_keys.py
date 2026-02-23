#!/usr/bin/env python3
"""
Extract and consolidate all pool data, validator keys, and attacker keys
into organized summary files.
"""

import pandas as pd
import os

# Load MEV data
df = pd.read_csv('02_mev_detection/per_pamm_all_mev_with_validator.csv')

print("=" * 70)
print("EXTRACTING POOL DATA & KEYS")
print("=" * 70)

# 1. Pool-level summary
pool_summary = []
for pool in sorted(df['amm_trade'].unique()):
    pool_data = df[df['amm_trade'] == pool]
    
    pool_summary.append({
        'pool': pool,
        'unique_attackers': pool_data['attacker_signer'].nunique(),
        'unique_validators': pool_data['validator'].nunique(),
        'total_mev_events': len(pool_data),
        'total_fat_sandwiches': int(pool_data['fat_sandwich'].sum()),
        'total_sandwiches': int(pool_data['sandwich'].sum()),
        'total_front_runs': int(pool_data['front_running'].sum()),
        'total_back_runs': int(pool_data['back_running'].sum()),
        'total_profit_sol': round(pool_data['profit_sol'].sum(), 4),
        'total_cost_sol': round(pool_data['cost_sol'].sum(), 4),
        'net_profit_sol': round(pool_data['net_profit_sol'].sum(), 4),
        'avg_profit_per_event': round(pool_data['profit_sol'].mean(), 4),
        'high_confidence_events': int((pool_data['confidence'] == 'high').sum()),
        'medium_confidence_events': int((pool_data['confidence'] == 'medium').sum()),
    })

pool_df = pd.DataFrame(pool_summary)
pool_df.to_csv('02_mev_detection/POOL_SUMMARY.csv', index=False)
print("\n✓ Pool Summary created: 02_mev_detection/POOL_SUMMARY.csv")
print(pool_df.to_string(index=False))

# 2. Validator participation per pool
val_pool = df.groupby(['amm_trade', 'validator']).agg({
    'attacker_signer': 'nunique',
    'profit_sol': 'sum',
    'net_profit_sol': 'sum',
    'fat_sandwich': 'sum',
}).reset_index()
val_pool.columns = ['pool', 'validator', 'attacker_count', 'total_profit', 'net_profit', 'fat_sandwiches']
val_pool = val_pool.sort_values(['pool', 'net_profit'], ascending=[True, False])
val_pool.to_csv('02_mev_detection/VALIDATOR_POOL_PARTICIPATION.csv', index=False)
print(f"\n✓ Validator-Pool participation: {len(val_pool)} entries")
print(f"   Saved to: 02_mev_detection/VALIDATOR_POOL_PARTICIPATION.csv")

# 3. Attacker keys per pool
print("\n=== UNIQUE ATTACKER KEYS BY POOL ===")
attacker_keys = []
for pool in sorted(df['amm_trade'].unique()):
    attackers = df[df['amm_trade'] == pool]['attacker_signer'].unique()
    print(f"\n{pool}: {len(attackers)} unique attackers")
    
    for attacker in attackers:
        attacker_data = df[(df['amm_trade'] == pool) & (df['attacker_signer'] == attacker)]
        attacker_keys.append({
            'pool': pool,
            'attacker_key': attacker,
            'event_count': len(attacker_data),
            'total_profit': round(attacker_data['profit_sol'].sum(), 4),
            'net_profit': round(attacker_data['net_profit_sol'].sum(), 4),
        })

attacker_df = pd.DataFrame(attacker_keys)
attacker_df.to_csv('02_mev_detection/ATTACKER_KEYS_BY_POOL.csv', index=False)
print(f"\n✓ Attacker keys exported: {len(attacker_df)} entries")
print(f"   Saved to: 02_mev_detection/ATTACKER_KEYS_BY_POOL.csv")

# 4. Validator keys
validator_keys = sorted(df['validator'].unique())
with open('02_mev_detection/VALIDATOR_KEYS.txt', 'w') as f:
    f.write("=== UNIQUE VALIDATOR KEYS IN MEV ANALYSIS ===\n")
    f.write(f"Total: {len(validator_keys)} validators\n\n")
    for v in validator_keys:
        f.write(f"{v}\n")

print(f"\n✓ Validator keys exported: {len(validator_keys)} keys")
print(f"   Saved to: 02_mev_detection/VALIDATOR_KEYS.txt")

# 5. Create comprehensive index file
index_content = f"""
# ============================================================================
# POOL DATA CONSOLIDATION - COMPLETE INDEX
# ============================================================================
# Generated from: per_pamm_all_mev_with_validator.csv
# Total MEV Events: {len(df):,}
# Analysis Pools: {len(df['amm_trade'].unique())}
# Total Validators: {len(validator_keys)}
# Total Unique Attackers: {df['attacker_signer'].nunique()}

## FILES GENERATED

### 1. POOL_SUMMARY.csv
   - Pool-level statistics
   - Columns: pool, unique_attackers, unique_validators, total_mev_events, 
             total_fat_sandwiches, total_sandwiches, total_front_runs, 
             total_back_runs, total_profit_sol, total_cost_sol, 
             net_profit_sol, avg_profit_per_event, high_confidence_events, 
             medium_confidence_events
   - Rows: {len(pool_df)}

### 2. VALIDATOR_POOL_PARTICIPATION.csv
   - Validator activity broken down by pool
   - Columns: pool, validator, attacker_count, total_profit, net_profit, fat_sandwiches
   - Rows: {len(val_pool)}

### 3. ATTACKER_KEYS_BY_POOL.csv
   - All attacker addresses with per-pool performance
   - Columns: pool, attacker_key, event_count, total_profit, net_profit
   - Rows: {len(attacker_df)}

### 4. VALIDATOR_KEYS.txt
   - Complete list of unique validator addresses
   - Count: {len(validator_keys)}

## POOL BREAKDOWN

"""

for pool in sorted(df['amm_trade'].unique()):
    pool_data = df[df['amm_trade'] == pool]
    index_content += f"""
### {pool}
   - MEV Events: {len(pool_data):,}
   - Unique Attackers: {pool_data['attacker_signer'].nunique()}
   - Unique Validators: {pool_data['validator'].nunique()}
   - Fat Sandwiches: {int(pool_data['fat_sandwich'].sum())}
   - Total Profit: {pool_data['profit_sol'].sum():.4f} SOL
   - Net Profit: {pool_data['net_profit_sol'].sum():.4f} SOL
"""

with open('02_mev_detection/INDEX.md', 'w') as f:
    f.write(index_content)

print(f"\n✓ Index file created: 02_mev_detection/INDEX.md")

print("\n" + "=" * 70)
print("FILES CREATED IN 02_mev_detection/:")
print("=" * 70)
print("1. POOL_SUMMARY.csv              - Pool-level statistics")
print("2. VALIDATOR_POOL_PARTICIPATION.csv - Validator activity by pool")
print("3. ATTACKER_KEYS_BY_POOL.csv    - All attacker addresses")
print("4. VALIDATOR_KEYS.txt           - All validator addresses")
print("5. INDEX.md                     - Complete index & reference")
print("=" * 70)
