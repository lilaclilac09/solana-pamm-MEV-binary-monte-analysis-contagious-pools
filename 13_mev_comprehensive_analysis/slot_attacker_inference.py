import pandas as pd
import os

# Paths
parquet_path = os.path.join(os.path.dirname(__file__), '../01_data_cleaning/outputs/pamm_clean_final.parquet')
fat_sandwich_path = os.path.join(os.path.dirname(__file__), '../13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv')

# Load data
df = pd.read_parquet(parquet_path)
df_attack = pd.read_csv(fat_sandwich_path)

# Merge slot and attacker info
merged = pd.merge(df, df_attack, left_on='slot', right_on='slot', how='inner')

# Group by slot and attacker
summary = merged.groupby(['slot', 'attacker_signer']).agg(
    event_count=('slot', 'count'),
    profit_sum=('net_profit_sol', 'sum'),
    attack_types=('classification', lambda x: x.value_counts().index[0] if len(x) else 'Unknown'),
    victims=('victim', lambda x: x.nunique() if 'victim' in df_attack.columns else 0)
).reset_index()

# Inference
summary['inference'] = summary.apply(
    lambda row: f"Slot {int(row['slot'])}, 攻击者 {row['attacker_signer']}：主要通过 {row['attack_types']}，获利 {row['profit_sum']} SOL，受害者数 {row['victims']}。" if row['event_count'] > summary['event_count'].mean() else f"Slot {int(row['slot'])}, 攻击者 {row['attacker_signer']}：活动较低，可能为正常交易或投票。",
    axis=1
)

# Save
summary.to_csv(os.path.join(os.path.dirname(__file__), 'slot_attacker_inference.csv'), index=False)

print('攻击者与slot分析已保存到 slot_attacker_inference.csv。')
