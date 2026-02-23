"""
Validator-AMM Risk Analysis with Mitigation Recommendations
Extracts high-risk pairs from heatmap and applies VALIDATOR_CONTAGION_FRAMEWORK mitigation strategies
"""

import os
import pandas as pd
import numpy as np
from collections import defaultdict
import json

ROOT = '/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis'
INPUT_FAT = os.path.join(ROOT, '13_mev_comprehensive_analysis', 'outputs', 'from_02_mev_detection', 'all_fat_sandwich_only.csv')
OUT_DIR = os.path.join(ROOT, '02_mev_detection', 'filtered_output')
REPORT_FILE = os.path.join(OUT_DIR, 'VALIDATOR_AMM_RISK_ANALYSIS.md')

print('[1] Loading fat sandwich data...')
fat_df = pd.read_csv(INPUT_FAT)

# Column mapping
amm_col = 'amm_trade' if 'amm_trade' in fat_df.columns else 'amm'
validator_col = 'validator'
attacker_col = 'attacker_signer' if 'attacker_signer' in fat_df.columns else 'attacker'
profit_col = 'net_profit_sol' if 'net_profit_sol' in fat_df.columns else 'profit_sol'
confidence_col = 'confidence' if 'confidence' in fat_df.columns else None

print(f'[2] Building validator-AMM risk matrix...')
# Create risk scores for each validator-AMM pair
risk_pairs = defaultdict(lambda: {
    'cases': 0,
    'total_profit': 0.0,
    'avg_profit': 0.0,
    'unique_attackers': set(),
    'confidence_high': 0,
    'confidence_med': 0,
    'confidence_low': 0
})

for _, row in fat_df.iterrows():
    validator = row[validator_col]
    amm = row[amm_col]
    pair_key = f"{validator}|{amm}"
    
    risk_pairs[pair_key]['cases'] += 1
    risk_pairs[pair_key]['total_profit'] += row[profit_col]
    risk_pairs[pair_key]['unique_attackers'].add(row[attacker_col])
    
    if confidence_col and pd.notna(row[confidence_col]):
        conf = str(row[confidence_col]).lower()
        if 'high' in conf:
            risk_pairs[pair_key]['confidence_high'] += 1
        elif 'med' in conf:
            risk_pairs[pair_key]['confidence_med'] += 1
        else:
            risk_pairs[pair_key]['confidence_low'] += 1

# Convert to list and calculate risk scores
risk_list = []
for pair_key, data in risk_pairs.items():
    validator, amm = pair_key.split('|')
    data['unique_attackers'] = len(data['unique_attackers'])
    data['avg_profit'] = data['total_profit'] / data['cases'] if data['cases'] > 0 else 0
    
    # Risk score: combination of case count, total profit, and attacker diversity
    risk_score = (
        (data['cases'] * 2) +                    # More cases = higher risk
        (data['total_profit'] * 10) +            # Higher profit = higher risk (10x weight)
        (data['unique_attackers'] * 0.5)         # More diverse attackers = more systemic
    )
    data['risk_score'] = risk_score
    
    risk_list.append({
        'validator': validator,
        'amm': amm,
        **data
    })

# Sort by risk score
risk_list_sorted = sorted(risk_list, key=lambda x: x['risk_score'], reverse=True)

print(f'[3] Identifying top 20 highest-risk validator-AMM pairs...')
top_20_risks = risk_list_sorted[:20]

# Calculate statistics
total_cases = sum(p['cases'] for p in risk_list_sorted)
top_20_cases = sum(p['cases'] for p in top_20_risks)
pct_top_20 = (top_20_cases / total_cases) * 100

total_profit = sum(p['total_profit'] for p in risk_list_sorted)
top_20_profit = sum(p['total_profit'] for p in top_20_risks)
pct_top_20_profit = (top_20_profit / total_profit) * 100

print(f'[4] Generating risk analysis report...')

# Mitigation strategies from framework
mitigations = {
    'slot_filter': {
        'name': 'Slot-Level MEV Filtering',
        'priority': 'HIGHEST',
        'impact': '60-70% reduction',
        'effort': 'MEDIUM',
        'implementation': 'Reject non-Jito bundles during high-MEV slots',
        'best_for': ['high_case_count', 'coordinated_attacks']
    },
    'twap_oracle': {
        'name': 'TWAP-Based Oracle Updates',
        'priority': 'HIGH',
        'impact': '50-60% reduction',
        'effort': 'MEDIUM',
        'implementation': 'Aggregate prices over 12 slots with randomized timing',
        'best_for': ['oracle_manipulation', 'repeated_attacks']
    },
    'commit_reveal': {
        'name': 'Commit-Reveal Transactions',
        'priority': 'MEDIUM',
        'impact': '80-90% reduction',
        'effort': 'HIGH',
        'implementation': 'Two-phase protocol: hide intent in phase 1, reveal in phase 2',
        'best_for': ['high_profit_attacks', 'timing_dependent']
    },
    'validator_diversity': {
        'name': 'Validator Diversity Routing',
        'priority': 'ONGOING',
        'impact': '20-30% reduction',
        'effort': 'LOW',
        'implementation': 'Route large trades to non-hotspot validators',
        'best_for': ['concentration_mitigation', 'load_distribution']
    }
}

# Generate report
with open(REPORT_FILE, 'w') as f:
    f.write("# Validator-AMM Risk Analysis with Mitigation Framework\n\n")
    f.write(f"**Analysis Date:** February 11, 2026\n")
    f.write(f"**Dataset:** 617 Fat Sandwich Cases\n")
    f.write(f"**Cross-Reference:** VALIDATOR_CONTAGION_FRAMEWORK.md\n\n")
    
    # Executive Summary
    f.write("## Executive Summary\n\n")
    f.write(f"- **Total Validator-AMM Pairs:** {len(risk_list_sorted)}\n")
    f.write(f"- **Top 20 Pairs Account For:** {top_20_cases} cases ({pct_top_20:.1f}% of total) and {top_20_profit:.2f} SOL ({pct_top_20_profit:.1f}% of profit)\n")
    f.write(f"- **Concentration Ratio:** Top 20 pairs = {pct_top_20:.1f}% of attack surface\n")
    f.write(f"- **Recommended Focus:** Target top 20 pairs first for maximum impact\n\n")
    
    # Top 20 High-Risk Pairs
    f.write("## Top 20 Highest-Risk Validator-AMM Pairs\n\n")
    f.write("| Rank | Validator | AMM | Cases | Total Profit | Avg Profit | Attackers | Risk Score | Recommendation |\n")
    f.write("|------|-----------|-----|-------|--------------|------------|-----------|------------|----------------|\n")
    
    for i, pair in enumerate(top_20_risks, 1):
        rec = "CRITICAL" if pair['risk_score'] > 100 else "HIGH" if pair['risk_score'] > 50 else "MEDIUM"
        validator_short = pair['validator'][:16]
        f.write(f"| {i} | {validator_short}... | {pair['amm']} | {pair['cases']} | {pair['total_profit']:.3f} | {pair['avg_profit']:.4f} | {pair['unique_attackers']} | {pair['risk_score']:.1f} | {rec} |\n")
    
    f.write("\n")
    
    # Risk Categories
    f.write("## Risk Categories\n\n")
    critical_pairs = [p for p in risk_list_sorted if p['risk_score'] > 100]
    high_pairs = [p for p in risk_list_sorted if 50 < p['risk_score'] <= 100]
    medium_pairs = [p for p in risk_list_sorted if 20 < p['risk_score'] <= 50]
    
    f.write(f"### CRITICAL Risk ({len(critical_pairs)} pairs)\n")
    f.write(f"**Definition:** Risk score > 100 (multiple high cases OR very high profit concentration)\n\n")
    for pair in critical_pairs[:10]:
        f.write(f"- **{pair['validator'][:20]}... + {pair['amm']}:** {pair['cases']} cases, {pair['total_profit']:.3f} SOL\n")
    if len(critical_pairs) > 10:
        f.write(f"- ... and {len(critical_pairs) - 10} more critical pairs\n")
    f.write("\n")
    
    f.write(f"### HIGH Risk ({len(high_pairs)} pairs)\n")
    f.write(f"**Definition:** Risk score 50-100 (significant attack frequency)\n")
    f.write(f"- Total cases in HIGH risk category: {sum(p['cases'] for p in high_pairs)}\n")
    f.write(f"- Total profit from HIGH risk: {sum(p['total_profit'] for p in high_pairs):.2f} SOL\n\n")
    
    f.write(f"### MEDIUM Risk ({len(medium_pairs)} pairs)\n")
    f.write(f"**Definition:** Risk score 20-50 (occasional exploitation)\n")
    f.write(f"- Total cases in MEDIUM risk: {sum(p['cases'] for p in medium_pairs)}\n\n")
    
    # Validator Concentration Analysis
    f.write("## Validator Concentration (Contagion Risk)\n\n")
    val_risk = defaultdict(lambda: {'cases': 0, 'profit': 0.0, 'amm_count': set()})
    for pair in risk_list_sorted:
        val_risk[pair['validator']]['cases'] += pair['cases']
        val_risk[pair['validator']]['profit'] += pair['total_profit']
        val_risk[pair['validator']]['amm_count'].add(pair['amm'])
    
    val_risk_list = sorted(
        [{'validator': v, **d, 'amm_count': len(d['amm_count'])} for v, d in val_risk.items()],
        key=lambda x: x['cases'],
        reverse=True
    )
    
    f.write("**Top Validators Enabling Contagion (hitting multiple AMMs):**\n\n")
    f.write("| Rank | Validator | Cases | AMMs Hit | Profit | Contagion Severity |\n")
    f.write("|------|-----------|-------|----------|--------|-------------------|\n")
    for i, val_info in enumerate(val_risk_list[:10], 1):
        severity = "CRITICAL" if val_info['amm_count'] >= 5 else "HIGH" if val_info['amm_count'] >= 3 else "MEDIUM"
        val_short = val_info['validator'][:16]
        f.write(f"| {i} | {val_short}... | {val_info['cases']} | {val_info['amm_count']} | {val_info['profit']:.3f} | {severity} |\n")
    
    f.write("\n")
    
    # Protocol Vulnerability Analysis
    f.write("## Protocol Vulnerability Ranking (from Validator-AMM Perspective)\n\n")
    protocol_risk = defaultdict(lambda: {'cases': 0, 'profit': 0.0, 'validators': set()})
    for pair in risk_list_sorted:
        protocol_risk[pair['amm']]['cases'] += pair['cases']
        protocol_risk[pair['amm']]['profit'] += pair['total_profit']
        protocol_risk[pair['amm']]['validators'].add(pair['validator'])
    
    protocol_risk_list = sorted(
        [{'protocol': p, 'cases': d['cases'], 'profit': d['profit'], 'validator_count': len(d['validators'])} 
         for p, d in protocol_risk.items()],
        key=lambda x: x['profit'],
        reverse=True
    )
    
    f.write("| Protocol | Cases | Total Profit | Unique Validators | Avg Profit/Case | Risk Level |\n")
    f.write("|----------|-------|--------------|-------------------|-----------------|----------|\n")
    for proto in protocol_risk_list:
        avg_prof = proto['profit'] / proto['cases'] if proto['cases'] > 0 else 0
        risk = "CRITICAL" if proto['profit'] > 15 else "HIGH" if proto['cases'] > 15 else "MEDIUM"
        f.write(f"| {proto['protocol']} | {proto['cases']} | {proto['profit']:.2f} | {proto['validator_count']} | {avg_prof:.4f} | {risk} |\n")
    
    f.write("\n")
    
    # Mitigation Recommendations
    f.write("## Mitigation Strategies Applied to High-Risk Pairs\n\n")
    
    for strategy_key, strategy in mitigations.items():
        f.write(f"### {strategy['name']}\n\n")
        f.write(f"**Priority:** {strategy['priority']}\n")
        f.write(f"**Expected Impact:** {strategy['impact']}\n")
        f.write(f"**Implementation Effort:** {strategy['effort']}\n")
        f.write(f"**How It Works:** {strategy['implementation']}\n\n")
        
        # Find best-fit pairs for this mitigation
        if 'high_case_count' in strategy['best_for']:
            best_pairs = [p for p in top_20_risks if p['cases'] > 5]
        elif 'oracle_manipulation' in strategy['best_for']:
            best_pairs = [p for p in top_20_risks if p['unique_attackers'] > 3]
        elif 'high_profit_attacks' in strategy['best_for']:
            best_pairs = [p for p in top_20_risks if p['total_profit'] > 2.0]
        elif 'concentration_mitigation' in strategy['best_for']:
            best_pairs = [p for p in val_risk_list if p['amm_count'] > 2][:5]
        else:
            best_pairs = top_20_risks[:3]
        
        f.write(f"**Best Applied To ({len(best_pairs)} pairs):**\n")
        for pair in best_pairs[:5]:
            if 'risk_score' in pair:
                f.write(f"- {pair['validator'][:16]}... + {pair['amm']}: {pair['cases']} cases, {pair['total_profit']:.3f} SOL\n")
            else:
                f.write(f"- {pair['validator'][:16]}... (hits {pair['amm_count']} AMMs, {pair['cases']} cases)\n")
        if len(best_pairs) > 5:
            f.write(f"- ... and {len(best_pairs) - 5} more\n")
        f.write("\n")
    
    # Implementation Roadmap
    f.write("## Prioritized Implementation Roadmap\n\n")
    f.write("### Phase 1 (Immediate - Week 1-2)\n")
    f.write("**Target:** CRITICAL risk pairs ({} pairs)\n\n".format(len(critical_pairs)))
    f.write("1. **Deploy Validator Diversity Routing** (LOW effort)\n")
    f.write("   - Route large trades away from HEL1US and DRpbCBMxVnDK\n")
    f.write("   - Expected: 20-30% reduction in top-2 validator attacks\n\n")
    f.write("2. **Monitor Slot-Level MEV Patterns** (prep work)\n")
    f.write("   - Instrument validators for high-MEV slot detection\n")
    f.write("   - Collect baseline data for filtering thresholds\n\n")
    
    f.write("### Phase 2 (Near-term - Week 3-4)\n")
    f.write("**Target:** HIGH risk pairs ({} pairs)\n\n".format(len(high_pairs)))
    f.write("1. **Enable Slot-Level MEV Filtering** (MEDIUM effort)\n")
    f.write("   - Implement on baseline validators (non-critical)\n")
    f.write("   - Expected: 60-70% reduction in coordinated attacks\n\n")
    f.write("2. **Coordinate TWAP Oracle Upgrades** (MEDIUM effort)\n")
    f.write("   - Start with HumidiFi (most vulnerable protocol)\n")
    f.write("   - Expected: 50-60% reduction in oracle-based attacks\n\n")
    
    f.write("### Phase 3 (Medium-term - Month 2)\n")
    f.write("**Target:** MEDIUM risk pairs ({} pairs)\n\n".format(len(medium_pairs)))
    f.write("1. **Implement Commit-Reveal for High-Value Trades** (HIGH effort)\n")
    f.write("   - Start with optional user opt-in\n")
    f.write("   - Expected: 80-90% reduction in sandwich attacks\n\n")
    f.write("2. **Cross-Protocol Coordination** (prep)\n")
    f.write("   - Align on consistent MEV filtering standards\n")
    f.write("   - Share attacker intelligence\n\n")
    
    # Risk Reduction Projections
    f.write("## Projected Risk Reduction\n\n")
    f.write("| Phase | Implementation | Estimated Attack Reduction | Residual Risk |\n")
    f.write("|-------|-----------------|----------------------------|-----------|\n")
    f.write("| 0 (Baseline) | None | 0% | 100% |\n")
    f.write("| 1 | Validator Diversity | 20-30% | 70-80% |\n")
    f.write("| 2 | + Slot Filtering + TWAP | 60-75% | 25-40% |\n")
    f.write("| 3 | + Commit-Reveal (opt-in) | 75-90% | 10-25% |\n\n")
    
    # Conclusion
    f.write("## Conclusion\n\n")
    f.write(f"The top 20 validator-AMM pairs represent **{pct_top_20:.1f}% of attack surface** ({top_20_cases} cases) ")
    f.write(f"and **{pct_top_20_profit:.1f}% of extracted MEV** ({top_20_profit:.2f} SOL).\n\n")
    f.write("**Recommended Action:** Focus mitigation efforts on the CRITICAL and HIGH risk pairs first.\n\n")
    f.write("**Key Insight:** Contagion is enabled by validator concentration (HEL1US processes 6% of fat sandwiches).\n")
    f.write("Reducing reliance on hotspot validators will have multiplicative downstream effects across all AMM pairs.\n\n")
    f.write("**Next Step:** Cross-reference specific protocols (e.g., HumidiFi) with their developer teams ")
    f.write("to coordinate TWAP oracle implementations on priority validators.\n")

print(f"✅ Report written to: {REPORT_FILE}")

# Create JSON export of top pairs for downstream analysis
print('[5] Exporting risk data as JSON...')
json_export = {
    'metadata': {
        'date': '2026-02-11',
        'total_fat_sandwich_cases': len(fat_df),
        'unique_pairs': len(risk_list_sorted),
        'critical_pairs': len(critical_pairs),
        'high_pairs': len(high_pairs)
    },
    'top_20_risk_pairs': [
        {
            'rank': i+1,
            'validator': p['validator'],
            'amm': p['amm'],
            'cases': int(p['cases']),
            'total_profit_sol': float(p['total_profit']),
            'avg_profit_sol': float(p['avg_profit']),
            'unique_attackers': int(p['unique_attackers']),
            'risk_score': float(p['risk_score']),
            'risk_level': 'CRITICAL' if p['risk_score'] > 100 else 'HIGH'
        }
        for i, p in enumerate(top_20_risks)
    ],
    'mitigations': {
        'slot_filtering': mitigations['slot_filter'],
        'twap_oracle': mitigations['twap_oracle'],
        'commit_reveal': mitigations['commit_reveal'],
        'validator_diversity': mitigations['validator_diversity']
    }
}

json_file = os.path.join(OUT_DIR, 'validator_amm_risk_analysis.json')
with open(json_file, 'w') as f:
    json.dump(json_export, f, indent=2)
print(f"✅ JSON export: {json_file}")

print("\n" + "="*80)
print("VALIDATOR-AMM RISK ANALYSIS COMPLETE")
print("="*80)
print(f"\nAll files saved to: {OUT_DIR}")
