#!/usr/bin/env python3
"""
Extract comprehensive validator and signer information for PDF report update
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Base directory
base_dir = Path(__file__).parent

# Load data from JSON files
print("Loading validator and signer data...")

# Load validator contagion graph
with open(base_dir / 'validator_contagion_graph.json', 'r') as f:
    validator_graph = json.load(f)

# Load contagion report with attacker signers
with open(base_dir / 'contagion_report.json', 'r') as f:
    contagion_data = json.load(f)

print(f"✓ Loaded validator contagion graph with {len(validator_graph['nodes'])} validators")
print(f"✓ Loaded contagion report")

# Extract validator information
validators_info = {}
for node in validator_graph['nodes']:
    validators_info[node['id']] = {
        'address': node['id'],
        'mev_count': node['mev_count'],
        'concentration': f"{node['concentration']:.4%}",
        'risk_level': node['risk_level']
    }

print(f"\n📊 VALIDATOR SUMMARY")
print(f"Total validators: {len(validators_info)}")
print(f"Total MEV events: {validator_graph['metadata']['total_records']}")

# Extract signer/attacker information
signers_by_validator = defaultdict(set)
signers_info = {}

# Parse contagion report to extract signers and their associated validators
try:
    if isinstance(contagion_data, dict) and 'results' in contagion_data:
        for result in contagion_data['results']:
            if 'attacker_signer' in result:
                attacker_signer = result['attacker_signer']
                if 'validator' in result:
                    validator = result['validator']
                    signers_by_validator[validator].add(attacker_signer)
                    if attacker_signer not in signers_info:
                        signers_info[attacker_signer] = {
                            'address': attacker_signer,
                            'validators': set(),
                            'mev_activities': 0
                        }
                    signers_info[attacker_signer]['validators'].add(validator)
                    signers_info[attacker_signer]['mev_activities'] += 1
except:
    print("Note: Could not parse signer data from contagion_report.json")

print(f"\n👥 SIGNER SUMMARY")
print(f"Total unique signers/attackers: {len(signers_info)}")

# Extract shared attacker information from edges
print(f"\n🔗 VALIDATOR RELATIONSHIPS")
print(f"Total validator pairs with shared attackers: {len(validator_graph['edges'])}")

# Generate comprehensive report data
report_data = {
    'validators': [],
    'signers': [],
    'validator_relationships': []
}

# Add validator data
for validator_id, validator_info in sorted(validators_info.items(), 
                                           key=lambda x: x[1]['mev_count'], 
                                           reverse=True):
    report_data['validators'].append({
        'rank': len(report_data['validators']) + 1,
        'address': validator_info['address'][:12] + '...' + validator_info['address'][-8:],
        'full_address': validator_info['address'],
        'mev_events': validator_info['mev_count'],
        'concentration': validator_info['concentration'],
        'risk_level': validator_info['risk_level'],
        'associated_signers': len(signers_by_validator.get(validator_id, set()))
    })

# Add signer data
for signer_id, signer_info in sorted(signers_info.items(), 
                                    key=lambda x: x[1]['mev_activities'], 
                                    reverse=True):
    report_data['signers'].append({
        'address': signer_id[:12] + '...' + signer_id[-8:],
        'full_address': signer_id,
        'validator_count': len(signer_info['validators']),
        'validators_used': ', '.join([v[:12] + '...' for v in sorted(list(signer_info['validators']))]),
        'mev_events': signer_info['mev_activities']
    })

# Add high-strength validator relationships
for edge in sorted(validator_graph['edges'], 
                   key=lambda x: x['shared_attackers'], 
                   reverse=True)[:20]:
    source_val = validators_info.get(edge['source'])
    target_val = validators_info.get(edge['target'])
    if source_val and target_val:
        report_data['validator_relationships'].append({
            'validator_1': edge['source'][:12] + '...',
            'validator_2': edge['target'][:12] + '...',
            'shared_attackers': edge['shared_attackers'],
            'strength': f"{edge['strength']:.2%}"
        })

# Save report data to CSV files for easy viewing
print("\n📁 Saving extracted data...")

# Save validators
validators_df = pd.DataFrame(report_data['validators'])
validators_csv = base_dir / 'validators_full_list.csv'
validators_df.to_csv(validators_csv, index=False)
print(f"✓ Saved {len(validators_df)} validators to {validators_csv.name}")

# Save signers
signers_df = pd.DataFrame(report_data['signers'])
signers_csv = base_dir / 'signers_full_list.csv'
signers_df.to_csv(signers_csv, index=False)
print(f"✓ Saved {len(signers_df)} signers to {signers_csv.name}")

# Save relationships
relationships_df = pd.DataFrame(report_data['validator_relationships'])
relationships_csv = base_dir / 'validator_relationships.csv'
relationships_df.to_csv(relationships_csv, index=False)
print(f"✓ Saved {len(relationships_df)} validator relationships to {relationships_csv.name}")

# Create summary for PDF
summary_text = f"""
VALIDATOR AND SIGNER COMPREHENSIVE ANALYSIS
Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}

=== EXECUTIVE SUMMARY ===
• Total Validators Analyzed: {len(validators_info)}
• Total MEV Events: {validator_graph['metadata']['total_records']:,}
• Unique Signers/Attackers: {len(signers_info)}
• High-Risk Validators: {sum(1 for v in validators_info.values() if v['risk_level'] == 'HIGH')}

=== TOP 10 VALIDATORS BY MEV CONCENTRATION ===
"""

for idx, val in enumerate(report_data['validators'][:10], 1):
    summary_text += f"\n{idx}. {val['full_address']}"
    summary_text += f"\n   MEV Events: {val['mev_events']}"
    summary_text += f"\n   Concentration: {val['concentration']}"
    summary_text += f"\n   Risk Level: {val['risk_level']}"
    summary_text += f"\n   Associated Signers: {val['associated_signers']}\n"

summary_text += f"\n=== TOP 10 SIGNERS BY ACTIVITY ===\n"
for idx, sig in enumerate(report_data['signers'][:10], 1):
    summary_text += f"\n{idx}. {sig['full_address']}"
    summary_text += f"\n   MEV Events: {sig['mev_events']}"
    summary_text += f"\n   Validators Used: {sig['validator_count']}\n"

# Save summary
summary_file = base_dir / 'VALIDATOR_SIGNER_ANALYSIS_SUMMARY.txt'
with open(summary_file, 'w') as f:
    f.write(summary_text)
print(f"✓ Saved summary to {summary_file.name}")

print("\n✅ Extraction complete!")
print(f"\nFiles generated:")
print(f"  1. validators_full_list.csv - Complete validator information")
print(f"  2. signers_full_list.csv - Complete signer/attacker information")
print(f"  3. validator_relationships.csv - High-strength validator relationships")
print(f"  4. VALIDATOR_SIGNER_ANALYSIS_SUMMARY.txt - Human-readable summary")
