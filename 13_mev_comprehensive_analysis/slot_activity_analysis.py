import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned parquet file
df = pd.read_parquet('../../01_data_cleaning/outputs/pamm_clean_final.parquet')

# Get unique slot numbers and their counts
grouped = df['slot'].value_counts().sort_index()

# Plot slot activity
plt.figure(figsize=(14, 6))
sns.barplot(x=grouped.index[:20], y=grouped.values[:20], palette='viridis')
plt.title('Slot Activity (Top 20 Slots)')
plt.xlabel('Slot Number')
plt.ylabel('Event Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('slot_activity_chart.png')
plt.show()

# Inference: Most events are concentrated in a few slots, indicating possible block clustering or high activity periods.
print('Inference: Most events are concentrated in a few slots, indicating possible block clustering or high activity periods.')
