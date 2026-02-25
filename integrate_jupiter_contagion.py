#!/usr/bin/env python3
"""
Integration: Jupiter Multi-Hop Detection + Contagion Analysis

This script shows how to combine the Jupiter routing tags with your 
existing contagion analysis to measure impact amplification by routing type.

Usage:
    python3 integrate_jupiter_contagion.py
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def load_tagged_data():
    """Load the Jupiter-tagged dataset."""
    path = Path('01_data_cleaning/outputs/pamm_clean_with_jupiter_tags.parquet')
    if not path.exists():
        print("❌ Error: pamm_clean_with_jupiter_tags.parquet not found.")
        print("   Run 02_jupiter_multihop_analysis.ipynb first.")
        return None
    
    df = pd.read_parquet(path)
    print(f"✅ Loaded {len(df):,} rows with Jupiter tags")
    return df


def summary_by_routing_type(df):
    """Generate summary statistics by routing type."""
    print("\n" + "="*80)
    print("SUMMARY: TRANSACTION DISTRIBUTION BY ROUTING TYPE")
    print("="*80)
    
    summary = df.groupby(['is_multihop', 'kind']).agg({
        'sig': 'count',
        'amm_trade': 'nunique',
        'bytes_changed_trade': ['mean', 'sum']
    }).round(2)
    
    summary.columns = ['tx_count', 'unique_amms', 'avg_impact', 'total_impact']
    summary['pct_of_total'] = summary['tx_count'] / len(df) * 100
    
    print(summary)
    return summary


def multihop_contagion_vectors(df):
    """Identify which pools are most affected by multi-hop contagion."""
    print("\n" + "="*80)
    print("CONTAGION VECTORS: Which Prop AMMs get hit by multi-hop routes?")
    print("="*80)
    
    # Multi-hop transactions only
    multihop = df[df['is_multihop']].copy()
    
    # By AMM
    amm_impact = multihop.groupby('amm_trade').agg({
        'sig': 'count',
        'bytes_changed_trade': ['mean', 'sum'],
        'hop_count': 'mean'
    }).round(2)
    
    amm_impact.columns = ['multihop_tx_count', 'avg_impact', 'total_impact', 'avg_hops']
    amm_impact = amm_impact.sort_values('multihop_tx_count', ascending=False)
    
    # Cross-reference with total transactions per AMM
    total_by_amm = df.groupby('amm_trade').size()
    amm_impact['pct_of_amm_volume'] = (amm_impact['multihop_tx_count'] / total_by_amm * 100).round(2)
    
    print(amm_impact.head(15))
    return amm_impact


def route_composition_analysis(df):
    """Analyze which DEX pairs are routing through your pAMM."""
    print("\n" + "="*80)
    print("ROUTE COMPOSITION: Most common multi-hop routes")
    print("="*80)
    
    multihop = df[df['is_multihop']].copy()
    
    top_routes = multihop['route_key'].value_counts().head(20)
    
    for idx, (route, count) in enumerate(top_routes.items(), 1):
        pct = count / len(multihop) * 100
        print(f"{idx:2d}. {route:50s}  {count:>8,} txs  ({pct:>5.1f}%)")
    
    return top_routes


def contagion_amplification_by_routing(df):
    """
    Measure impact amplification: multi-hop vs single-hop vs direct.
    
    Higher bytes_changed_trade = more pool state disturbance = more contagion risk.
    """
    print("\n" + "="*80)
    print("CONTAGION AMPLIFICATION: Impact by Routing Type")
    print("="*80)
    
    impact_by_type = df.groupby(['is_multihop', 'is_singlehop']).agg({
        'bytes_changed_trade': ['mean', 'std', 'min', 'max', 'sum'],
        'sig': 'count'
    }).round(2)
    
    impact_by_type.columns = ['mean_impact', 'std_impact', 'min_impact', 'max_impact', 'total_impact', 'tx_count']
    
    # Calculate amplification ratios
    multihop_mean = df[df['is_multihop']]['bytes_changed_trade'].mean()
    singlehop_mean = df[df['is_singlehop']]['bytes_changed_trade'].mean()
    direct_mean = df[df['is_direct']]['bytes_changed_trade'].mean()
    
    print(f"\n📊 Average Impact (bytes_changed_trade):")
    print(f"   Multi-Hop (2+):   {multihop_mean:>8.2f} bytes")
    print(f"   Single-Hop (1):   {singlehop_mean:>8.2f} bytes")
    print(f"   Direct (0):       {direct_mean:>8.2f} bytes")
    
    print(f"\n📈 Amplification Ratios:")
    print(f"   Multi-Hop vs Single-Hop:  {multihop_mean / singlehop_mean:.2f}x")
    print(f"   Multi-Hop vs Direct:      {multihop_mean / direct_mean:.2f}x")
    print(f"   Single-Hop vs Direct:     {singlehop_mean / direct_mean:.2f}x")
    
    print(f"\nImpact Table:")
    print(impact_by_type)
    
    return {
        'multihop_mean': multihop_mean,
        'singlehop_mean': singlehop_mean,
        'direct_mean': direct_mean,
        'multihop_vs_single_amplification': multihop_mean / singlehop_mean,
        'multihop_vs_direct_amplification': multihop_mean / direct_mean,
    }


def temporal_contagion_analysis(df):
    """Analyze how multi-hop contagion evolves over time."""
    print("\n" + "="*80)
    print("TEMPORAL ANALYSIS: Multi-Hop Contagion Over Time")
    print("="*80)
    
    df['hour'] = df['datetime'].dt.floor('h')
    
    hourly = df.groupby('hour').agg({
        'is_multihop': ['sum', lambda x: x.sum() / len(x) * 100],
        'bytes_changed_trade': ['mean'],
        'sig': 'count'
    }).round(2)
    
    hourly.columns = ['multihop_count', 'multihop_pct', 'avg_impact', 'total_tx']
    
    print(hourly.head(24))
    
    # Correlation: when multi-hop % is high, is average impact also high?
    correlation = hourly['multihop_pct'].corr(hourly['avg_impact'])
    print(f"\n📊 Correlation (multi-hop % vs average impact): {correlation:.3f}")
    if correlation > 0.3:
        print("   ✅ Strong signal: high multi-hop % correlates with higher impact disturbance")
    else:
        print("   ⚠️  Weak signal: size of effect doesn't strongly correlate with volume")
    
    return hourly


def event_type_breakdown(df):
    """Break down multi-hop by event type (ORACLE, TRADE, etc.)."""
    print("\n" + "="*80)
    print("EVENT TYPE BREAKDOWN: Multi-Hop Distribution")
    print("="*80)
    
    breakdown = df.groupby(['kind', 'is_multihop']).agg({
        'sig': 'count',
        'bytes_changed_trade': 'mean'
    }).round(2)
    
    breakdown.columns = ['tx_count', 'avg_impact']
    
    print(breakdown)
    
    # What % of TRADES are multi-hop vs ORACLE?
    trades_multihop_pct = df[df['kind'] == 'TRADE']['is_multihop'].sum() / len(df[df['kind'] == 'TRADE']) * 100
    oracles_multihop_pct = df[df['kind'] == 'ORACLE']['is_multihop'].sum() / len(df[df['kind'] == 'ORACLE']) * 100
    
    print(f"\n📊 Multi-Hop Share by Event Type:")
    print(f"   TRADE events that are multi-hop:  {trades_multihop_pct:.1f}%")
    print(f"   ORACLE events that are multi-hop: {oracles_multihop_pct:.1f}%")
    
    return breakdown


def save_analysis_report(df, outdir='02_mev_detection'):
    """Save comprehensive analysis report."""
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)
    
    report = {
        'metadata': {
            'total_transactions': int(len(df)),
            'datetime_range': {
                'start': str(df['datetime'].min()),
                'end': str(df['datetime'].max()),
            },
            'analysis_date': pd.Timestamp.now().isoformat(),
        },
        'routing_summary': {
            'multihop_count': int(df['is_multihop'].sum()),
            'multihop_pct': float(df['is_multihop'].sum() / len(df) * 100),
            'singlehop_count': int(df['is_singlehop'].sum()),
            'singlehop_pct': float(df['is_singlehop'].sum() / len(df) * 100),
            'direct_count': int(df['is_direct'].sum()),
            'direct_pct': float(df['is_direct'].sum() / len(df) * 100),
        },
        'contagion_metrics': {
            'multihop_mean_impact': float(df[df['is_multihop']]['bytes_changed_trade'].mean()),
            'singlehop_mean_impact': float(df[df['is_singlehop']]['bytes_changed_trade'].mean()),
            'direct_mean_impact': float(df[df['is_direct']]['bytes_changed_trade'].mean()),
            'amplification_multihop_vs_direct': float(
                df[df['is_multihop']]['bytes_changed_trade'].mean() / df[df['is_direct']]['bytes_changed_trade'].mean()
            ),
        },
        'top_amms_by_multihop_volume': df[df['is_multihop']].groupby('amm_trade')['sig'].count().nlargest(10).to_dict(),
    }
    
    report_path = outdir / 'jupiter_contagion_analysis.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis report saved: {report_path}")
    return report_path


def main():
    """Main integration pipeline."""
    print("\n" + "="*80)
    print("🚀 JUPITER MULTI-HOP + CONTAGION ANALYSIS PIPELINE")
    print("="*80)
    
    # Load data
    df = load_tagged_data()
    if df is None:
        return
    
    # Run all analyses
    summary_by_routing_type(df)
    multihop_contagion_vectors(df)
    route_composition_analysis(df)
    contagion_amplification_by_routing(df)
    temporal_contagion_analysis(df)
    event_type_breakdown(df)
    
    # Save report
    save_analysis_report(df)
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print("\n📊 Key outputs:")
    print("   - Multi-hop transaction share (%)")
    print("   - Contagion amplification ratios (by routing type)")
    print("   - Top affected Prop AMMs")
    print("   - Temporal patterns")
    print("   - JSON report in 02_mev_detection/")


if __name__ == '__main__':
    main()
