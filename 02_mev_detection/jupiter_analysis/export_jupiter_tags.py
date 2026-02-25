#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

# Load data
data_path = '01_data_cleaning/outputs/pamm_clean_final.parquet'
df = pd.read_parquet(data_path)

# Add hop detection if not already there
if 'hop_count' not in df.columns:
    def count_hops(trades_array):
        if trades_array is None or (isinstance(trades_array, float) and np.isnan(trades_array)):
            return 0
        if isinstance(trades_array, np.ndarray):
            return len(trades_array)
        if isinstance(trades_array, list):
            return len(trades_array)
        return 0

    def get_route_key(trades_array):
        """Get a string representation of the route for grouping."""
        hops = count_hops(trades_array)
        if hops == 0:
            return 'no_route'
        
        if isinstance(trades_array, np.ndarray):
            trades_list = trades_array.tolist()
        else:
            trades_list = trades_array if isinstance(trades_array, list) else []
        
        amms = []
        for trade in trades_list:
            if isinstance(trade, dict) and 'amm' in trade:
                amm_short = trade['amm'][:4] if len(trade['amm']) >= 4 else trade['amm']
                amms.append(amm_short)
        
        if not amms:
            return f'hops_{hops}'
        
        return '->'.join(amms)

    print("Computing hop counts and route keys...")
    df['hop_count'] = df['trades'].apply(count_hops)
    df['route_key'] = df['trades'].apply(get_route_key)
    df['is_multihop'] = df['hop_count'] > 1
    df['is_singlehop'] = df['hop_count'] == 1
    df['is_direct'] = df['hop_count'] == 0

# Save tagged dataset
output_dir = '01_data_cleaning/outputs'
os.makedirs(output_dir, exist_ok=True)

tagged_path = os.path.join(output_dir, 'pamm_clean_with_jupiter_tags.parquet')
df.to_parquet(tagged_path, index=False)

# Create summary CSV
summary_stats = pd.DataFrame({
    'Metric': [
        'Total Transactions',
        'Multi-Hop (2+ hops)',
        'Single-Hop (1 hop)',
        'Direct (0 hops)',
        'Multi-Hop %',
        'Single-Hop %',
        'Direct %',
    ],
    'Value': [
        len(df),
        int(df['is_multihop'].sum()),
        int(df['is_singlehop'].sum()),
        int(df['is_direct'].sum()),
        f"{df['is_multihop'].sum() / len(df) * 100:.2f}%",
        f"{df['is_singlehop'].sum() / len(df) * 100:.2f}%",
        f"{df['is_direct'].sum() / len(df) * 100:.2f}%",
    ]
})

summary_csv = os.path.join(output_dir, 'jupiter_routing_summary.csv')
summary_stats.to_csv(summary_csv, index=False)

print("="*70)
print("✓ JUPITER ROUTING ANALYSIS COMPLETE")
print("="*70)
print(f"\nFiles saved:")
print(f"  • {tagged_path}")
print(f"  • {summary_csv}")
print(f"\nSummary:")
print(summary_stats.to_string(index=False))
