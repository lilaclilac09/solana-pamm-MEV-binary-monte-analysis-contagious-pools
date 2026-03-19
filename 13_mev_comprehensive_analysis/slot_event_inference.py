import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

parquet_path = os.path.join(os.path.dirname(__file__), '../01_data_cleaning/outputs/pamm_clean_final.parquet')
df = pd.read_parquet(parquet_path)

# Group by slot and summarize
slot_summary = df.groupby('slot').agg(
    event_count=('slot', 'count'),
    min_time=('time', 'min'),
    max_time=('time', 'max'),
    unique_kinds=('kind', lambda x: x.nunique() if 'kind' in df.columns else 0)
).reset_index()

# Save summary
slot_summary.to_csv(os.path.join(os.path.dirname(__file__), 'slot_event_summary.csv'), index=False)

# Plot slot activity
plt.figure(figsize=(14, 6))
sns.barplot(x=slot_summary['slot'][:20], y=slot_summary['event_count'][:20], palette='viridis')
plt.title('Slot Activity (Top 20 Slots)')
plt.xlabel('Slot Number')
plt.ylabel('Event Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), 'slot_activity_chart.png'))
plt.show()

# Add inference for each slot
inferences = []
for _, row in slot_summary.iterrows():
    if row['event_count'] > slot_summary['event_count'].mean():
        inf = f"Slot {int(row['slot'])}: 活动密集，可能存在套利、抢先交易或高频DeFi操作。"
    else:
        inf = f"Slot {int(row['slot'])}: 活动较低，可能为正常交易或投票。"
    inferences.append(inf)

with open(os.path.join(os.path.dirname(__file__), 'slot_inferences.txt'), 'w', encoding='utf-8') as f:
    for inf in inferences:
        f.write(inf + '\n')

print('每个slot的推断已保存到 slot_inferences.txt。')
