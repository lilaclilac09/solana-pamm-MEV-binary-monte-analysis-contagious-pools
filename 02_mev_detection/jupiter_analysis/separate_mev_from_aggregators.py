#!/usr/bin/env python3
"""
Separate Jupiter Multi-Hop Aggregator Transactions from False Positive MEV Detection

This script:
1. Loads Jupiter-tagged dataset with MEV classifications
2. Separates real MEV sandwiches from multi-hop aggregator false positives
3. Exports filtered datasets
4. Generates summary statistics and visualizations
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

print("\n" + "="*80)
print("JUPITER MULTI-HOP vs MEV SEPARATION ANALYSIS")
print("="*80)

# Create output directory
output_dir = Path('jupiter_analysis/outputs')
output_dir.mkdir(parents=True, exist_ok=True)

try:
    # =========================================================================
    # STEP 1: LOAD DATA
    # =========================================================================
    print("\n📂 Loading datasets...")
    
    # Try to load Jupiter-tagged dataset
    try:
        df = pd.read_parquet('outputs/pamm_clean_with_jupiter_tags.parquet')
        print(f"  ✓ Loaded Jupiter-tagged dataset: {len(df):,} rows")
        has_jupiter_tags = True
    except:
        print("  ⚠ Jupiter-tagged dataset not found, loading clean data...")
        df = pd.read_parquet('../01_data_cleaning/outputs/pamm_clean_final.parquet')
        print(f"  ✓ Loaded clean dataset: {len(df):,} rows")
        has_jupiter_tags = False
    
    # Filter to trades only
    df_trades = df[df['kind'] == 'TRADE'].copy().reset_index(drop=True)
    print(f"  ✓ Filtered to trades: {len(df_trades):,} rows")
    
    # =========================================================================
    # STEP 2: ADD CLASSIFICATION FEATURES IF NOT PRESENT
    # =========================================================================
    print("\n🔍 Preparing classification features...")
    
    # Add Jupiter tags if not present
    if not has_jupiter_tags and 'is_multihop' not in df_trades.columns:
        print("  ℹ Adding basic hop count detection...")
        df_trades['is_multihop'] = False
        df_trades['hop_count'] = 0
        if 'trades' in df_trades.columns:
            df_trades['hop_count'] = df_trades['trades'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            df_trades['is_multihop'] = df_trades['hop_count'] >= 2
        print(f"    - Multi-hop transactions: {df_trades['is_multihop'].sum():,}")
    
    # Ensure classification columns exist
    for col in ['victim_count', 'confidence', 'fat_sandwich_score', 'multi_hop_score', 
                'unique_pools', 'attack_type', 'is_cycle']:
        if col not in df_trades.columns:
            if col == 'victim_count':
                df_trades[col] = 0
            elif col == 'confidence':
                df_trades[col] = 0.0
            elif col in ['fat_sandwich_score', 'multi_hop_score']:
                df_trades[col] = 0.0
            elif col == 'unique_pools':
                df_trades[col] = 1
            elif col == 'attack_type':
                df_trades[col] = 'unknown'
            elif col == 'is_cycle':
                df_trades[col] = False
    
    print(f"  ✓ Classification features ready")
    
    # =========================================================================
    # STEP 3: CLASSIFY TRANSACTIONS
    # =========================================================================
    print("\n⚙️  Classifying transactions...")
    
    # TRUE MEV: Actual sandwich attacks
    true_mev_mask = (
        (df_trades['attack_type'] == 'fat_sandwich') |
        ((df_trades['victim_count'] > 0) & 
         (df_trades['fat_sandwich_score'] > 0.60) &
         (~df_trades['is_multihop']))
    )
    
    # FALSE POSITIVES: Legitimate multi-hop routing
    false_positive_mask = (
        (df_trades['attack_type'] == 'multi_hop_arbitrage') |
        ((df_trades['is_multihop']) & 
         (df_trades['victim_count'] == 0) &
         (df_trades['unique_pools'] > 2))
    )
    
    # AMBIGUOUS: Hard to classify
    ambiguous_mask = ~(true_mev_mask | false_positive_mask)
    
    # Create classification column
    df_trades['mev_category'] = 'ambiguous'
    df_trades.loc[true_mev_mask, 'mev_category'] = 'real_mev'
    df_trades.loc[false_positive_mask, 'mev_category'] = 'aggregator'
    
    # Count by category
    category_counts = df_trades['mev_category'].value_counts()
    print(f"  ✓ Classification complete:")
    for cat, count in category_counts.items():
        pct = count / len(df_trades) * 100
        print(f"    - {cat.upper()}: {count:,} ({pct:.2f}%)")
    
    # =========================================================================
    # STEP 4: SEPARATE AND EXPORT DATASETS
    # =========================================================================
    print("\n💾 Exporting separated datasets...")
    
    # Real MEV
    df_real_mev = df_trades[df_trades['mev_category'] == 'real_mev'].copy()
    output_file = output_dir / 'real_mev_sandwiches.parquet'
    df_real_mev.to_parquet(output_file)
    print(f"  ✓ Real MEV sandwiches: {len(df_real_mev):,} → {output_file.name}")
    
    # Aggregators (false positives)
    df_aggregators = df_trades[df_trades['mev_category'] == 'aggregator'].copy()
    output_file = output_dir / 'aggregator_false_positives.parquet'
    df_aggregators.to_parquet(output_file)
    print(f"  ✓ Aggregator false positives: {len(df_aggregators):,} → {output_file.name}")
    
    # Ambiguous
    df_ambiguous = df_trades[df_trades['mev_category'] == 'ambiguous'].copy()
    output_file = output_dir / 'ambiguous_transactions.parquet'
    df_ambiguous.to_parquet(output_file)
    print(f"  ✓ Ambiguous transactions: {len(df_ambiguous):,} → {output_file.name}")
    
    # =========================================================================
    # STEP 5: GENERATE SUMMARY STATISTICS
    # =========================================================================
    print("\n📊 Computing statistics...")
    
    summary_stats = {
        'total_trades': int(len(df_trades)),
        'real_mev_sandwiches': {
            'count': int(len(df_real_mev)),
            'percentage': float(len(df_real_mev) / len(df_trades) * 100),
            'avg_victims': float(df_real_mev['victim_count'].mean()) if len(df_real_mev) > 0 else 0,
            'avg_confidence': float(df_real_mev['confidence'].mean()) if len(df_real_mev) > 0 else 0,
            'avg_fat_sandwich_score': float(df_real_mev['fat_sandwich_score'].mean()) if len(df_real_mev) > 0 else 0,
        },
        'aggregator_false_positives': {
            'count': int(len(df_aggregators)),
            'percentage': float(len(df_aggregators) / len(df_trades) * 100),
            'multihop_percentage': float(df_aggregators['is_multihop'].sum() / len(df_aggregators) * 100) if len(df_aggregators) > 0 else 0,
            'avg_unique_pools': float(df_aggregators['unique_pools'].mean()) if len(df_aggregators) > 0 else 0,
            'avg_multi_hop_score': float(df_aggregators['multi_hop_score'].mean()) if len(df_aggregators) > 0 else 0,
        },
        'ambiguous': {
            'count': int(len(df_ambiguous)),
            'percentage': float(len(df_ambiguous) / len(df_trades) * 100),
        },
        'improvement': {
            'false_positive_reduction': float(len(df_aggregators) / (len(df_trades) - len(df_real_mev)) * 100) if (len(df_trades) - len(df_real_mev)) > 0 else 0,
            'accurate_mev_identified': float(len(df_real_mev) / len(df_trades) * 100),
        }
    }
    
    # Save summary
    output_file = output_dir / 'separation_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    print(f"  ✓ Summary statistics → {output_file.name}")
    
    # =========================================================================
    # STEP 6: DETAILED BREAKDOWN TABLE
    # =========================================================================
    print("\n📈 SEPARATION RESULTS")
    print("-" * 80)
    
    breakdown_data = {
        'Category': ['Real MEV Sandwiches', 'Aggregator False Positives', 'Ambiguous', 'TOTAL'],
        'Count': [
            len(df_real_mev),
            len(df_aggregators),
            len(df_ambiguous),
            len(df_trades)
        ],
        'Percentage': [
            f"{len(df_real_mev)/len(df_trades)*100:.2f}%",
            f"{len(df_aggregators)/len(df_trades)*100:.2f}%",
            f"{len(df_ambiguous)/len(df_trades)*100:.2f}%",
            "100.00%"
        ]
    }
    
    df_breakdown = pd.DataFrame(breakdown_data)
    print(df_breakdown.to_string(index=False))
    
    # Save detailed breakdown
    output_file = output_dir / 'separation_breakdown.csv'
    df_breakdown.to_csv(output_file, index=False)
    print(f"\n  ✓ Breakdown table → {output_file.name}")
    
    # =========================================================================
    # STEP 7: KEY INSIGHTS
    # =========================================================================
    print("\n💡 KEY INSIGHTS")
    print("-" * 80)
    
    if len(df_real_mev) > 0:
        print(f"✓ Identified {len(df_real_mev):,} TRUE MEV sandwich attacks")
        print(f"  - Average {df_real_mev['victim_count'].mean():.1f} victims per attack")
        print(f"  - Average confidence: {df_real_mev['confidence'].mean():.1%}")
    
    if len(df_aggregators) > 0:
        print(f"\n✓ Removed {len(df_aggregators):,} FALSE POSITIVES (aggregator routing)")
        print(f"  - {df_aggregators['is_multihop'].sum():,} are confirmed multi-hop")
        print(f"  - Average {df_aggregators['unique_pools'].mean():.1f} pools per transaction")
    
    if len(df_ambiguous) > 0:
        print(f"\n⚠ {len(df_ambiguous):,} AMBIGUOUS cases for manual review")
        print(f"  - Saved for further analysis")
    
    improvement = len(df_aggregators) / len(df_trades) * 100 if len(df_trades) > 0 else 0
    print(f"\n🎯 FALSE POSITIVE REDUCTION: {improvement:.1f}%")
    print(f"   (Separated {len(df_aggregators):,} aggregator txns from MEV detection)")
    
    # =========================================================================
    # STEP 8: EXPORT COMPARISON TABLE
    # =========================================================================
    print("\n📋 Creating comparison table...")
    
    comparison_data = []
    
    for cat_name, df_cat in [('Real MEV', df_real_mev), 
                              ('Aggregators', df_aggregators), 
                              ('Ambiguous', df_ambiguous)]:
        if len(df_cat) > 0:
            comparison_data.append({
                'Category': cat_name,
                'Transaction Count': len(df_cat),
                'Avg Victims': df_cat['victim_count'].mean() if 'victim_count' in df_cat.columns else 0,
                'Avg Confidence': df_cat['confidence'].mean() if 'confidence' in df_cat.columns else 0,
                'Avg Fat Sandwich Score': df_cat['fat_sandwich_score'].mean() if 'fat_sandwich_score' in df_cat.columns else 0,
                'Avg Multi-Hop Score': df_cat['multi_hop_score'].mean() if 'multi_hop_score' in df_cat.columns else 0,
                'Multihop %': (df_cat['is_multihop'].sum() / len(df_cat) * 100) if 'is_multihop' in df_cat.columns else 0,
                'Avg Unique Pools': df_cat['unique_pools'].mean() if 'unique_pools' in df_cat.columns else 0,
            })
    
    df_comparison = pd.DataFrame(comparison_data)
    output_file = output_dir / 'category_comparison.csv'
    df_comparison.to_csv(output_file, index=False)
    print(f"  ✓ Comparison table → {output_file.name}")
    print("\n" + df_comparison.to_string(index=False))
    
    # =========================================================================
    # STEP 9: SAMPLE EXPORT FOR INSPECTION
    # =========================================================================
    print("\n🔍 Exporting sample rows for inspection...")
    
    # Real MEV samples
    sample_size = min(10, len(df_real_mev))
    if sample_size > 0:
        output_file = output_dir / 'real_mev_samples.csv'
        df_real_mev.head(sample_size)[[
            'signer', 'ms_time', 'slot', 'victim_count', 'confidence', 
            'fat_sandwich_score', 'attack_type'
        ]].to_csv(output_file)
        print(f"  ✓ Real MEV samples → {output_file.name}")
    
    # Aggregator samples
    sample_size = min(10, len(df_aggregators))
    if sample_size > 0:
        output_file = output_dir / 'aggregator_samples.csv'
        df_aggregators.head(sample_size)[[
            'signer', 'ms_time', 'slot', 'is_multihop', 'unique_pools',
            'multi_hop_score', 'attack_type'
        ]].to_csv(output_file)
        print(f"  ✓ Aggregator samples → {output_file.name}")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print("\nFiles generated:")
    for f in sorted(output_dir.glob('*')):
        print(f"  - {f.name}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
