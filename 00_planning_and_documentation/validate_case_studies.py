#!/usr/bin/env python3
"""
Case Study Data Consistency Validator
Compares case study data across JSON source, Python dashboard, HTML report, and academic PDF generator.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
import sys

# Canonical source
JSON_SOURCE = "outputs/mev_attack_case_studies.json"
PYTHON_DASHBOARD = "app/attack_case_studies.py"
HTML_REPORT = "index.html"
ACADEMIC_REPORT = "11_report_generation/generate_academic_report.py"

class CaseStudyValidator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.canonical_data = {}
        self.errors = []
        self.warnings = []
        
    def load_canonical_json(self):
        """Load canonical JSON source"""
        json_path = self.base_path / JSON_SOURCE
        if not json_path.exists():
            self.errors.append(f"❌ Canonical JSON not found: {json_path}")
            return False
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        for case in data:
            case_id = case['attack_id']
            self.canonical_data[case_id] = {
                'title': case['attack_title'],
                'token_pair': case['token_pair'],
                'attacker': case['attacker_info']['signer_address'],
                'net_profit_sol': case['profit_breakdown']['net_profit_sol'],
                'roi_percentage': case['profit_breakdown']['roi_percentage'],
                'victim_order_intent': case['victim_info']['order_intent'],
                'victim_order_size': case['victim_info']['order_size_tokens'],
                'victim_loss_sol': case['pool_metrics']['victim_impact'].get('victim_loss_sol', 
                    case['pool_metrics']['victim_impact'].get('victim_loss_usdc', 0)),
                'attack_type': case['attack_characteristics']['type'],
                'frontrun_input_amount': case['attack_sequence']['frontrun']['position_details']['input_amount'],
                'frontrun_input_token': case['attack_sequence']['frontrun']['position_details']['input_token'],
                'victim_input_amount': case['attack_sequence']['victim_execution']['details']['input_amount'],
                'victim_input_token': case['attack_sequence']['victim_execution']['details']['input_token'],
                'victim_output_token': case['attack_sequence']['victim_execution']['details']['output_token'],
            }
        
        print(f"✅ Loaded {len(self.canonical_data)} canonical case studies from JSON")
        return True
    
    def validate_python_dashboard(self):
        """Validate Python dashboard consistency"""
        py_path = self.base_path / PYTHON_DASHBOARD
        if not py_path.exists():
            self.errors.append(f"❌ Python dashboard not found: {py_path}")
            return
        
        with open(py_path, 'r') as f:
            content = f.read()
        
        print("\n🔍 Validating Python Dashboard (app/attack_case_studies.py)...")
        
        # Case 1: JUP/WSOL
        case1_match = re.search(r'"profit":\s*"([\d.]+)\s*SOL"', content)
        case1_roi_match = re.search(r'"roi":\s*"(\d+)%"', content)
        
        canonical_case1 = self.canonical_data.get('CASE-001-460701000')
        if canonical_case1:
            if case1_match:
                py_profit = float(case1_match.group(1))
                canonical_profit = round(canonical_case1['net_profit_sol'], 3)
                if abs(py_profit - canonical_profit) > 0.01:
                    self.errors.append(
                        f"❌ Case 1 profit mismatch: Python {py_profit} SOL vs JSON {canonical_profit} SOL"
                    )
                else:
                    print(f"  ✅ Case 1 profit matches: {py_profit} SOL")
            
            if case1_roi_match:
                py_roi = int(case1_roi_match.group(1))
                canonical_roi = int(canonical_case1['roi_percentage'])
                if abs(py_roi - canonical_roi) > 5:
                    self.errors.append(
                        f"❌ Case 1 ROI mismatch: Python {py_roi}% vs JSON {canonical_roi}%"
                    )
                else:
                    print(f"  ✅ Case 1 ROI matches: {py_roi}%")
        
        # Case 2: PYTH/WSOL - Check for wrong descriptions
        if "800K PYTH buy" in content:
            self.errors.append(
                "❌ Case 2 has wrong victim action: says '800K PYTH buy' but should be '750K WSOL to buy PYTH'"
            )
        
        if '"profit": "3.312 SOL"' in content:
            canonical_case2 = self.canonical_data.get('CASE-002-461628000')
            if canonical_case2:
                canonical_profit = round(canonical_case2['net_profit_sol'], 3)
                if abs(3.312 - canonical_profit) > 0.01:
                    self.errors.append(
                        f"❌ Case 2 profit mismatch: Python 3.312 SOL vs JSON {canonical_profit} SOL"
                    )
                else:
                    print(f"  ✅ Case 2 profit matches: 3.312 SOL")
        
        # Case 2: Check ROI
        case2_roi_match = re.search(r'"roi":\s*"552%"', content)
        if case2_roi_match:
            canonical_case2 = self.canonical_data.get('CASE-002-461628000')
            if canonical_case2:
                canonical_roi = int(canonical_case2['roi_percentage'])
                if abs(552 - canonical_roi) > 5:
                    self.errors.append(
                        f"❌ Case 2 ROI mismatch: Python 552% vs JSON {canonical_roi}%"
                    )
    
    def validate_html_report(self):
        """Validate HTML report consistency"""
        html_path = self.base_path / HTML_REPORT
        if not html_path.exists():
            self.errors.append(f"❌ HTML report not found: {html_path}")
            return
        
        with open(html_path, 'r') as f:
            content = f.read()
        
        print("\n🔍 Validating HTML Report (index.html)...")
        
        # Case 2: Check for wrong victim trade description
        if "1.2M PYTH → WSOL" in content or "1.2M PYTH" in content:
            self.errors.append(
                "❌ HTML Case 2 has wrong victim trade: says '1.2M PYTH → WSOL' but should be '750K WSOL → PYTH'"
            )
        
        # Check profit values
        if "0.571 SOL" in content:
            print("  ⚠️  Case 1 profit in HTML: 0.571 SOL (need to verify against JSON)")
        
        if "3.312 SOL" in content:
            print("  ⚠️  Case 2 profit in HTML: 3.312 SOL (need to verify against JSON)")
    
    def validate_academic_report(self):
        """Validate academic report generator consistency"""
        report_path = self.base_path / ACADEMIC_REPORT
        if not report_path.exists():
            self.errors.append(f"❌ Academic report generator not found: {report_path}")
            return
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        print("\n🔍 Validating Academic Report Generator (11_report_generation/generate_academic_report.py)...")
        
        # Case 2: Check for wrong attacker signer
        if "AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R" in content:
            canonical_case2 = self.canonical_data.get('CASE-002-461628000')
            if canonical_case2:
                canonical_attacker = canonical_case2['attacker']
                if canonical_attacker != "AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R":
                    self.errors.append(
                        f"❌ Academic report Case 2 wrong attacker: has AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R "
                        f"but JSON says {canonical_attacker}"
                    )
        
        # Check for 800K PYTH
        if "800K PYTH" in content:
            self.errors.append(
                "❌ Academic report Case 2 has wrong victim trade: says '800K PYTH' but should be '750K WSOL → PYTH'"
            )
        
        # Check ROI values
        if "552%" in content:
            canonical_case2 = self.canonical_data.get('CASE-002-461628000')
            if canonical_case2:
                canonical_roi = int(canonical_case2['roi_percentage'])
                if abs(552 - canonical_roi) > 5:
                    self.warnings.append(
                        f"⚠️  Academic report Case 2 ROI: 552% vs JSON {canonical_roi}%"
                    )
    
    def print_canonical_summary(self):
        """Print canonical data summary"""
        print("\n" + "="*80)
        print("📋 CANONICAL DATA SUMMARY (from JSON)")
        print("="*80)
        
        for case_id, data in self.canonical_data.items():
            print(f"\n{case_id}: {data['title']}")
            print(f"  Token Pair: {data['token_pair']}")
            print(f"  Attacker: {data['attacker'][:20]}...")
            print(f"  Attack Type: {data['attack_type']}")
            print(f"  Victim Action: {data['victim_order_intent']}")
            print(f"    - Input: {data['victim_input_amount']} {data['victim_input_token']}")
            print(f"    - Output: {data['victim_output_token']}")
            print(f"  Attacker Frontrun: {data['frontrun_input_amount']} {data['frontrun_input_token']}")
            print(f"  Victim Loss: {data['victim_loss_sol']} SOL")
            print(f"  Net Profit: {data['net_profit_sol']} SOL")
            print(f"  ROI: {data['roi_percentage']}%")
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*80)
        print("📊 VALIDATION REPORT")
        print("="*80)
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND: {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ No errors found!")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
        
        print("\n" + "="*80)
        if self.errors:
            print("❌ VALIDATION FAILED - Inconsistencies detected")
            return False
        else:
            print("✅ VALIDATION PASSED")
            return True

def main():
    base_path = Path(__file__).parent
    
    validator = CaseStudyValidator(base_path)
    
    # Load canonical data
    if not validator.load_canonical_json():
        print("Failed to load canonical JSON source")
        sys.exit(1)
    
    # Print canonical summary
    validator.print_canonical_summary()
    
    # Run validations
    validator.validate_python_dashboard()
    validator.validate_html_report()
    validator.validate_academic_report()
    
    # Print report
    success = validator.print_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
