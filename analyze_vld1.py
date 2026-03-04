#!/usr/bin/env python3
import pandas as pd
import os

# Load the fat sandwich data
fat_csv = '02_mev_detection/filtered_output/all_fat_sandwich_only.csv'
fat_df = pd.read_csv(fat_csv)
print(f"Total records: {len(fat_df)}\n")

# Identify columns
validator_col = 'validator' if 'validator' in fat_df.columns else 'validator_pubkey'
profit_col = 'net_profit_sol' if 'net_profit_sol' in fat_df.columns else 'profit_sol'

print(f"Validator column: {validator_col}")
print(f"Profit column: {profit_col}\n")

# Rankings by case count (Activity) - this is what Figure VLD-1 shows
print("=" * 80)
print("TOP 15 VALIDATORS BY MEV ACTIVITY (Case Count) - Figure VLD-1")
print("=" * 80)
val_counts = fat_df[validator_col].value_counts().head(15)
for rank, (val, count) in enumerate(val_counts.items(), 1):
    profit = fat_df[fat_df[validator_col] == val][profit_col].sum()
    print(f"{rank:2d}. {val[:40]:40s} | Cases: {count:3d} | Profit: {profit:8.3f} SOL")

# Rankings by total profit
print("\n" + "=" * 80)
print("TOP 15 VALIDATORS BY TOTAL MEV PROFIT")
print("=" * 80)
val_profit = fat_df.groupby(validator_col)[profit_col].sum().sort_values(ascending=False).head(15)
for rank, (val, profit) in enumerate(val_profit.items(), 1):
    count = len(fat_df[fat_df[validator_col] == val])
    print(f"{rank:2d}. {val[:40]:40s} | Profit: {profit:8.3f} SOL | Cases: {count:3d}")

# Find which validator is 15th in activity but where does it rank in profit?
print("\n" + "=" * 80)
print("ANALYSIS: 15th VALIDATOR IN ACTIVITY")
print("=" * 80)
validator_15th = val_counts.index[14]  # 15th is at index 14
cases_15th = val_counts.iloc[14]
profit_15th = fat_df[fat_df[validator_col] == validator_15th][profit_col].sum()

# Rank this validator in profit
profit_rank = (val_profit > profit_15th).sum() + 1

print(f"Validator ID: {validator_15th}")
print(f"  Cases: {cases_15th}")
print(f"  Profit: {profit_15th:.3f} SOL")
print(f"  Rank by Profit: #{profit_rank} out of {len(val_profit)}")

# Get details of top transactions for this validator
print(f"\n" + "=" * 80)
print(f"TOP 15 TRANSACTIONS FOR THIS VALIDATOR")
print("=" * 80)
validator_txs = fat_df[fat_df[validator_col] == validator_15th].sort_values(profit_col, ascending=False).head(15)
print(f"\nTotal transactions for this validator: {len(fat_df[fat_df[validator_col] == validator_15th])}")
print()

for i, (idx, row) in enumerate(validator_txs.iterrows(), 1):
    print(f"{i}. Profit: {row.get(profit_col, 'N/A'):.5f} SOL")
    if 'signature' in row.index:
        print(f"   TX: {str(row['signature'])[:60]}")
    if 'amm_trade' in row.index:
        print(f"   AMM: {row['amm_trade']}")
    if 'attacker_signer' in row.index:
        print(f"   Attacker: {str(row['attacker_signer'])[:50]}")
    if 'slot' in row.index:
        print(f"   Slot: {row['slot']}")
    print()

# Summary breakdown
print("\n" + "=" * 80)
print("PROFIT BREAKDOWN FOR 15TH VALIDATOR")
print("=" * 80)
validator_df = fat_df[fat_df[validator_col] == validator_15th].copy()
print(f"Total Profit: {validator_df[profit_col].sum():.4f} SOL")
print(f"Mean Profit per TX: {validator_df[profit_col].mean():.6f} SOL")
print(f"Median Profit per TX: {validator_df[profit_col].median():.6f} SOL")
print(f"Max Single TX: {validator_df[profit_col].max():.6f} SOL")
print(f"Min Single TX: {validator_df[profit_col].min():.6f} SOL")

if 'amm_trade' in validator_df.columns:
    print(f"\nAMM Breakdown:")
    amm_breakdown = validator_df.groupby('amm_trade')[profit_col].agg(['sum', 'count', 'mean'])
    amm_breakdown = amm_breakdown.sort_values('sum', ascending=False)
    print(amm_breakdown)
