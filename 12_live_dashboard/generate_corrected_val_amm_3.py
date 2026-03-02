#!/usr/bin/env python3
"""
Generate Corrected VAL-AMM-3 Figure
MEV Attack Pattern Comparison (Post-False Positive Elimination)
Total MEV Trades: 650 (down from ~2,131)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Corrected data after false positive elimination
mev_patterns_data = pd.DataFrame({
    'Pattern': ['Fat Sandwich', 'Back-Running (DeezNode)', 'Classic Sandwich', 
                'Front-Running', 'Cross-Slot (2Fast)'],
    'Count': [312, 135, 95, 62, 46],
    'Percentage': [48.0, 20.8, 14.6, 9.5, 7.1]
})

# Sort by count descending
mev_patterns_data = mev_patterns_data.sort_values('Count', ascending=False).reset_index(drop=True)

# Define colors (pink/red for Fat Sandwich and Front-Running, purple for Back-Running, teal/cyan for others)
color_map = {
    'Fat Sandwich': '#FF6B9D',           # Pink
    'Front-Running': '#FF4757',          # Red
    'Back-Running (DeezNode)': '#9B59B6', # Purple
    'Classic Sandwich': '#1ABC9C',       # Teal
    'Cross-Slot (2Fast)': '#3498DB'      # Cyan
}

colors = [color_map[pattern] for pattern in mev_patterns_data['Pattern']]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left: Horizontal bar chart
bars = ax1.barh(mev_patterns_data['Pattern'], mev_patterns_data['Count'], color=colors, edgecolor='white', linewidth=1.5)
ax1.set_xlabel('Number of Trades', fontsize=12, fontweight='bold')
ax1.set_ylabel('Attack Pattern', fontsize=12, fontweight='bold')
ax1.set_title('MEV Pattern Comparison: Trade Counts', fontsize=13, fontweight='bold', pad=15)
ax1.set_xlim(0, 350)
ax1.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
ax1.set_axisbelow(True)

# Add value labels on bars
for i, (pattern, count) in enumerate(zip(mev_patterns_data['Pattern'], mev_patterns_data['Count'])):
    ax1.text(count + 7, i, str(count), va='center', fontsize=11, fontweight='bold')

# Right: Pie chart
wedges, texts, autotexts = ax2.pie(
    mev_patterns_data['Count'], 
    labels=mev_patterns_data['Pattern'],
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    textprops={'fontsize': 10, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'white', 'linewidth': 2.5}
)

# Make percentage text more visible
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

ax2.set_title('MEV Pattern Distribution', fontsize=13, fontweight='bold', pad=15)

# Overall title
fig.suptitle(
    'Figure VAL-AMM-3: MEV Attack Pattern Comparison Across Validator-AMM Pairs\n(Post-False Positive Elimination: 650 Total MEV Trades)',
    fontsize=14,
    fontweight='bold',
    y=0.98
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save the figure
output_path = 'corrected_val_amm_3.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Figure saved to: {output_path}")

print()
print("=" * 70)
print("📊 CORRECTED VAL-AMM-3 DATA SUMMARY")
print("=" * 70)
print(f"   Total MEV Trades: {mev_patterns_data['Count'].sum()}")
print(f"   Most Common Pattern: {mev_patterns_data.iloc[0]['Pattern']}")
print(f"   └─ {mev_patterns_data.iloc[0]['Count']} trades ({mev_patterns_data.iloc[0]['Percentage']}%)")
print()
print("   Pattern Breakdown:")
for _, row in mev_patterns_data.iterrows():
    print(f"     • {row['Pattern']:<25} {row['Count']:>3} trades ({row['Percentage']:>4.1f}%)")
print("=" * 70)
print()

# Show the plot
plt.show()
