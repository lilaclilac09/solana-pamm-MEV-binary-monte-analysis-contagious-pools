#!/usr/bin/env python3
"""
Count actual MEV pattern breakdown from filtered data
"""
import pandas as pd
from collections import Counter

# Read the filtered MEV data with all classifications
df = pd.read_csv('02_mev_detection/filtered_output/all_mev_with_classification.csv')

print(f"\n{'='*70}")
print(f"ACTUAL MEV PATTERN COUNTS (POST FALSE POSITIVE ELIMINATION)")
print(f"{'='*70}\n")
print(f"Total records in file: {len(df)}")
print(f"\nBreakdown by classification:")
print(f"{'-'*70}")

# Count by classification
classification_counts = df['classification'].value_counts()
print(classification_counts)

print(f"\n{'-'*70}")
print(f"\nSUCCESSFUL MEV ATTACKS (excluding FAILED_SANDWICH):")
print(f"{'-'*70}")

# Filter out failed sandwiches
successful_mev = df[df['classification'] != 'FAILED_SANDWICH']
print(f"Total successful MEV attacks: {len(successful_mev)}")

# Count successful attack types
successful_counts = successful_mev['classification'].value_counts()
print(f"\nSuccessful attack breakdown:")
for attack_type, count in successful_counts.items():
    print(f"  {attack_type:25s}: {count:4d} attacks")

print(f"\n{'='*70}")
print(f"DATA FOR VAL-AMM-3 FIGURE:")
print(f"{'='*70}\n")

# Create ordered list for visualization
attack_patterns = {
    'FAT_SANDWICH': successful_counts.get('FAT_SANDWICH', 0),
    'BACK_RUNNING': successful_counts.get('BACK_RUNNING', 0),
    'CLASSIC_SANDWICH': successful_counts.get('CLASSIC_SANDWICH', 0),
    'FRONT_RUNNING': successful_counts.get('FRONT_RUNNING', 0),
    'CROSS_SLOT': successful_counts.get('CROSS_SLOT', 0),
}

print("Pattern breakdown for figure:")
for pattern, count in attack_patterns.items():
    print(f"  {pattern:25s}: {count:4d}")

total_successful = sum(attack_patterns.values())
print(f"\nTotal successful MEV trades: {total_successful}")

# Export to Python list format
pattern_list = list(attack_patterns.values())
print(f"\nPython list for script: {pattern_list}")
print(f"Sum verification: {sum(pattern_list)}")

print(f"\n{'='*70}\n")
