#!/usr/bin/env python3
"""Quick test of the contagious vulnerability analyzer."""

import pandas as pd
from contagious_vulnerability_analyzer import ContagiousVulnerabilityAnalyzer

print("=" * 70)
print("TESTING CONTAGIOUS VULNERABILITY ANALYZER")
print("=" * 70)

# Initialize and load data
analyzer = ContagiousVulnerabilityAnalyzer()
mev_df = analyzer.load_mev_data('02_mev_detection/per_pamm_all_mev_with_validator.csv')

print(f"\n✓ Data loaded and normalized")
print(f"  Shape: {mev_df.shape}")
print(f"  Columns: {list(mev_df.columns)[:10]}...")

print(f"\nPools in data:")
print(mev_df['pool'].value_counts())

# Test trigger pool identification
print(f"\n{'=' * 70}")
print("Testing Trigger Pool Identification")
print(f"{'=' * 70}")
trigger_analysis = analyzer.identify_trigger_pool(mev_df)
print(f"\nTrigger Pool: {trigger_analysis['trigger_pool']}")
print(f"Characteristics:")
for key, val in trigger_analysis['trigger_characteristics'].items():
    print(f"  - {key}: {val}")

if trigger_analysis['downstream_pools_identified']:
    print(f"\nDownstream Pools (Top 3):")
    for pool_info in trigger_analysis['downstream_pools_identified'][:3]:
        print(f"  - {pool_info['pool']}: {pool_info['overlap_percentage']:.1f}% overlap")

# Test cascade analysis
print(f"\n{'=' * 70}")
print("Testing Cascade Rate Analysis")
print(f"{'=' * 70}")
cascade_analysis = analyzer.analyze_cascade_rates(mev_df, trigger_pool=trigger_analysis['trigger_pool'], time_window_ms=5000)
print(f"\nCascade Rates:")
for key, val in cascade_analysis['cascade_rates'].items():
    print(f"  - {key}: {val}")

# Generate report
print(f"\n{'=' * 70}")
print("Generating Comprehensive Report")
print(f"{'=' * 70}")
report = analyzer.generate_contagion_report(
    mev_df=mev_df,
    oracle_df=None,
    output_path='contagion_report.json'
)

print(f"\n✓ Report generated successfully")
print(f"  Output: contagion_report.json")
print(f"\nKey Finding: {report.get('key_finding', 'N/A')}")

exec_summary = report.get('executive_summary', {})
print(f"\nExecutive Summary:")
print(f"  Cascade Rate: {exec_summary.get('cascade_rate_percentage', 0):.1f}%")
print(f"  Critical Risk Pools: {exec_summary.get('critical_risk_pools', [])}")

print(f"\n✓ Analysis complete!")
