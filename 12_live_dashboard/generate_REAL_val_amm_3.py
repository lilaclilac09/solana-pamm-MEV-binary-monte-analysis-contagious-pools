#!/usr/bin/env python3
"""
Generate REAL VAL-AMM-3 Figure - POST FALSE POSITIVE ELIMINATION
MEV Attack Pattern Comparison (After FP Filtering: 636 Validated MEV Trades)
Data Source: 02_mev_detection/filtered_output/all_mev_with_classification.csv
Validated data: 617 Fat Sandwich + 19 Multi-Hop Arbitrage = 636 total attacks
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# REAL MEV PATTERN DATA - POST FALSE POSITIVE ELIMINATION
# Data source: all_mev_with_classification.csv (validated attacks only, FAILED_SANDWICH excluded)
# Total: 636 validated MEV trades (down from 1,501 raw detections)
# Breakdown:
#   - Fat Sandwich: 617 attacks (97.0%)
#   - Multi-Hop Arbitrage: 19 attacks (3.0%)
#   - Back-Running, Classic Sandwich, Front-Running, Cross-Slot: 0 (eliminated as false positives)
mev_patterns_data = pd.DataFrame({
    'Pattern': ['Fat Sandwich\n(Validator-Controlled)', 'Multi-Hop Arbitrage'],
    'Trades': [617, 19],  # ACTUAL post-FP counts from database
})

# Calculate percentages
total_trades = mev_patterns_data['Trades'].sum()
mev_patterns_data['Percentage'] = (mev_patterns_data['Trades'] / total_trades * 100).round(1)

# Sort by trade count descending
mev_patterns_data = mev_patterns_data.sort_values('Trades', ascending=False).reset_index(drop=True)

# Define colors
color_map = {
    'Fat Sandwich\n(Validator-Controlled)': '#FF6B9D',  # Pink
    'Multi-Hop Arbitrage': '#1ABC9C',                    # Teal
}

colors = [color_map[pattern] for pattern in mev_patterns_data['Pattern']]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left: Horizontal bar chart
bars = ax1.barh(mev_patterns_data['Pattern'], mev_patterns_data['Trades'], 
                color=colors, edgecolor='white', linewidth=1.5)
ax1.set_xlabel('Number of Validated Attacks', fontsize=12, fontweight='bold')
ax1.set_ylabel('Attack Pattern', fontsize=12, fontweight='bold')
ax1.set_title('MEV Pattern Comparison: Validated Attack Counts', fontsize=13, fontweight='bold', pad=15)
ax1.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
ax1.set_axisbelow(True)

# Add value labels on bars
for i, (pattern, trades, pct) in enumerate(zip(
    mev_patterns_data['Pattern'], 
    mev_patterns_data['Trades'],
    mev_patterns_data['Percentage']
)):
    ax1.text(trades + 10, i, f'{trades} attacks ({pct}%)', 
             va='center', fontsize=11, fontweight='bold')

# Right: Pie chart
wedges, texts, autotexts = ax2.pie(
    mev_patterns_data['Trades'], 
    labels=mev_patterns_data['Pattern'],
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'white', 'linewidth': 2.5}
)

# Make percentage text more visible
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')

ax2.set_title('MEV Pattern Distribution', fontsize=13, fontweight='bold', pad=15)

# Overall title
fig.suptitle(
    'Figure VAL-AMM-3: MEV Attack Pattern Comparison Across Validator-AMM Pairs\n' +
    f'(Post-False Positive Elimination: {total_trades} Validated MEV Attacks)',
    fontsize=14,
    fontweight='bold',
    y=0.98
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save the figure
output_path = 'REAL_VAL_AMM_3.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✅ Figure saved: {output_path}")

print()
print("=" * 80)
print("📊 REAL VAL-AMM-3 DATA - POST FALSE POSITIVE ELIMINATION")
print("=" * 80)
print(f"   Data Source: 02_mev_detection/filtered_output/all_mev_with_classification.csv")
print(f"   Total Validated MEV Attacks: {total_trades}")
print(f"   Raw Detections (pre-FP filter): 1,501")
print(f"   Failed Sandwich Attempts: 865 (eliminated)")
print(f"   False Positive Elimination Rate: 57.6%")
print()
print("   Attack Pattern Breakdown (Validated Attacks Only):")
for _, row in mev_patterns_data.iterrows():
    print(f"     • {row['Pattern']:<40} {row['Trades']:>3} attacks ({row['Percentage']:>5.1f}%)")
print()
print("=" * 80)
print()
print("🔍 KEY INSIGHTS (POST FALSE POSITIVE ELIMINATION):")
print("   - Fat Sandwich (Validator-Controlled) DOMINATES: 617 attacks (97.0%)")
print("   - Multi-Hop Arbitrage: 19 attacks (3.0%)")
print()
print("   ⚠️  Other patterns (Back-Running, Classic Sandwich, Front-Running, Cross-Slot):")
print("       ALL eliminated as false positives - NO validated attacks in final dataset")
print()
print("   ✓  FP Elimination process:")
print("       - Raw detections: 1,501 total MEV events detected")
print("       - Failed attempts: 865 FAILED_SANDWICH (no profit, incomplete)")
print("       - Validated attacks: 636 profitable MEV attacks")
print("       - Primary pattern: Fat Sandwich (validator-controlled multi-block attacks)")
print("=" * 80)

# Show the plot
plt.show()
