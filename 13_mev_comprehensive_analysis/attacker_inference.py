import pandas as pd
import os

# 路径
attack_path = os.path.join(os.path.dirname(__file__), 'outputs/from_02_mev_detection/all_fat_sandwich_only.csv')

# 加载数据
df_attack = pd.read_csv(attack_path)

# 聚合分析
summary = df_attack.groupby('attacker_signer').agg(
    event_count=('fat_sandwich', 'sum'),
    profit_sum=('net_profit_sol', 'sum'),
    main_type=('classification', lambda x: x.value_counts().index[0] if len(x) else 'Unknown')
).reset_index()

# 推断
summary['inference'] = summary.apply(
    lambda row: f"攻击者 {row['attacker_signer']}：主要通过 {row['main_type']}，事件数 {row['event_count']}，获利 {row['profit_sum']} SOL。" if row['event_count'] > summary['event_count'].mean() else f"攻击者 {row['attacker_signer']}：活动较低，可能为普通套利或投票。",
    axis=1
)

# 保存
summary.to_csv(os.path.join(os.path.dirname(__file__), 'attacker_inference.csv'), index=False)
print('攻击者聚合与推断已保存到 attacker_inference.csv。')
