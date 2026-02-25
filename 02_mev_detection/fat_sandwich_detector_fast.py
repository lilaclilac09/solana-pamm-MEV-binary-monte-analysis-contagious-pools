#!/usr/bin/env python3
"""
Fat Sandwich Detector - FAST SAMPLED VERSION
Demonstrates detection on 10% sample of trades
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys

print("\n" + "="*80)
print("FAT SANDWICH DETECTOR - SAMPLED VERSION (10% of data)")
print("="*80)

# Load data
print("\n📂 Loading data...")
try:
    df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
    df_trades = df_clean[df_clean['kind'] == 'TRADE'].copy()
    print(f"✓ Loaded {len(df_trades):,} trade events")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    sys.exit(1)

# Sample 10% for faster processing
sample_size = max(10000, int(len(df_trades) * 0.1))
df_sample = df_trades.sample(n=min(sample_size, len(df_trades)), random_state=42).sort_values('ms_time')
print(f"✓ Sampled {len(df_sample):,} trades for analysis")

# Key columns
print(f"\nColumns available: {list(df_sample.columns)[:10]}...")

# Basic analysis
print("\n" + "="*80)
print("DATA SUMMARY")
print("="*80)
print(f"Time range: {df_sample['ms_time'].min()} - {df_sample['ms_time'].max()}")
print(f"Unique signers: {df_sample['signer'].nunique():,}")
print(f"Unique slots: {df_sample['slot'].nunique():,}")

if 'amm_trade' in df_sample.columns:
    print(f"Unique pools: {df_sample['amm_trade'].nunique():,}")

# ==============================================================================
# DETECTION: Look for A-B-A patterns (basic sandwich signature)
# ==============================================================================

print("\n" + "="*80)
print("DETECTING FAT SANDWICH PATTERNS (A-B-A)")
print("="*80)

sandwiches_detected = []
window_seconds_list = [1, 2, 5, 10]

for window_sec in window_seconds_list:
    window_ms = window_seconds_list = [1000, 2000, 5000, 10000]
    window_ms = window_sec * 1000
    
    # Group trades by time windows
    df_sample['time_group'] = (df_sample['ms_time'] // window_ms).astype(int)
    
    for time_group in df_sample['time_group'].unique():
        group_trades = df_sample[df_sample['time_group'] == time_group].sort_values('ms_time')
        
        if len(group_trades) < 3:  # Need at least 3 trades for A-B-A
            continue
        
        # Look for A-B-A pattern (same signer at start/end)
        for idx in range(len(group_trades) - 2):
            trade_a = group_trades.iloc[idx]
            trade_a_idx = idx
            
            # Find victim trades (different signer)
            for mid_idx in range(idx + 1, len(group_trades) - 1):
                trade_b = group_trades.iloc[mid_idx]
                if trade_b['signer'] == trade_a['signer']:
                    continue
                
                # Look for second A trade (same signer as first)
                for end_idx in range(mid_idx + 1, len(group_trades)):
                    trade_a2 = group_trades.iloc[end_idx]
                    if trade_a2['signer'] != trade_a['signer']:
                        continue
                    
                    # Check if token pairs reverse (hallmark of sandwich)
                    if 'from_token' in group_trades.columns and 'to_token' in group_trades.columns:
                        a_pair = (trade_a['from_token'], trade_a['to_token'])
                        a2_pair = (trade_a2['from_token'], trade_a2['to_token'])
                        
                        # Reversed if second A swaps the token pair
                        if a_pair[0] == a2_pair[1] and a_pair[1] == a2_pair[0]:
                            sandwiches_detected.append({
                                'window_sec': window_sec,
                                'attacker_signer': trade_a['signer'],
                                'victim_count': end_idx - idx - 1,
                                'trades_in_pattern': 3,
                                'time_span_ms': trade_a2['ms_time'] - trade_a['ms_time'],
                                'slot_range': f"{trade_a['slot']}-{trade_a2['slot']}",
                                'confidence': 'HIGH' if end_idx - idx - 1 >= 1 else 'MEDIUM'
                            })

sandwiches_df = pd.DataFrame(sandwiches_detected)

print(f"\n✓ Total patterns detected: {len(sandwiches_df):,}")

if len(sandwiches_df) > 0:
    print("\nBy window size:")
    for window in window_seconds_list:
        count = len(sandwiches_df[sandwiches_df['window_sec'] == window])
        pct = 100 * count / len(sandwiches_df) if len(sandwiches_df) > 0 else 0
        print(f"  {window}s window: {count:,} ({pct:.1f}%)")
    
    print("\nBy confidence level:")
    confidence_counts = sandwiches_df['confidence'].value_counts()
    for conf_level in ['HIGH', 'MEDIUM', 'LOW']:
        if conf_level in confidence_counts.index:
            count = confidence_counts[conf_level]
            pct = 100 * count / len(sandwiches_df)
            print(f"  {conf_level}: {count:,} ({pct:.1f}%)")
    
    print("\nVictim statistics:")
    print(f"  Mean victims per sandwich: {sandwiches_df['victim_count'].mean():.2f}")
    print(f"  Max victims in single pattern: {sandwiches_df['victim_count'].max()}")
    print(f"  Median time span: {sandwiches_df['time_span_ms'].median():.0f}ms")

# ==============================================================================
# CLASSIFICATION: Differentiate Fat Sandwich vs Multi-Hop
# ==============================================================================

print("\n" + "="*80)
print("CLASSIFICATION: FAT SANDWICH vs MULTI-HOP ARBITRAGE")
print("="*80)

def classify_attack(pattern_row):
    """
    Classify as Fat Sandwich or Multi-Hop based on characteristics
    """
    # Fat sandwich indicators
    victim_count = pattern_row.get('victim_count', 0)
    time_span = pattern_row.get('time_span_ms', 0)
    
    # High victim count + tight time window = Fat Sandwich
    fat_sandwich_score = 0
    multi_hop_score = 0
    
    if victim_count >= 2:
        fat_sandwich_score += 50  # Multiple victims = sandwich indicator
    elif victim_count == 1:
        fat_sandwich_score += 25
    
    if time_span < 2000:  # < 2 seconds = sandwich
        fat_sandwich_score += 30
    elif time_span > 5000:  # > 5 seconds = multi-hop
        multi_hop_score += 30
    
    # Determine classification
    if fat_sandwich_score > multi_hop_score:
        return 'fat_sandwich'
    elif multi_hop_score > fat_sandwich_score:
        return 'multi_hop_arbitrage'
    else:
        return 'ambiguous'

if len(sandwiches_df) > 0:
    sandwiches_df['attack_type'] = sandwiches_df.apply(classify_attack, axis=1)
    
    print("\nClassification results:")
    classification_counts = sandwiches_df['attack_type'].value_counts()
    total = len(sandwiches_df)
    
    for attack_type in ['fat_sandwich', 'multi_hop_arbitrage', 'ambiguous']:
        if attack_type in classification_counts.index:
            count = classification_counts[attack_type]
            pct = 100 * count / total
            print(f"  ✓ {attack_type}: {count:,} ({pct:.1f}%)")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"""
Dataset analyzed:
  - Trade events: {len(df_sample):,} (10% sample)
  - Time range: {df_sample['ms_time'].min()} - {df_sample['ms_time'].max()}
  - Unique signers: {df_sample['signer'].nunique():,}
  
Detection results:
  - Patterns detected: {len(sandwiches_df):,}
  - Detection rate: {100 * len(sandwiches_df) / len(df_sample):.3f}% of trades
  
Confidence distribution:
  - HIGH confidence: {len(sandwiches_df[sandwiches_df['confidence']=='HIGH']) if len(sandwiches_df) > 0 else 0:,}
  - MEDIUM confidence: {len(sandwiches_df[sandwiches_df['confidence']=='MEDIUM']) if len(sandwiches_df) > 0 else 0:,}

Key metrics (if patterns found):
  - Avg victim count per pattern: {sandwiches_df['victim_count'].mean():.2f if len(sandwiches_df) > 0 else 0:.2f}
  - Median time span: {sandwiches_df['time_span_ms'].median():.0f if len(sandwiches_df) > 0 else 0:.0f}ms
  - Mode window size: {sandwiches_df['window_sec'].mode()[0] if len(sandwiches_df) > 0 else 'N/A'}s
""")

# Save results
if len(sandwiches_df) > 0:
    output_file = 'outputs/fat_sandwich_detection_sample_results.csv'
    sandwiches_df.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to {output_file}")

print("\n" + "="*80)
print("✅ DETECTION COMPLETE")
print("="*80 + "\n")
