#!/usr/bin/env python3
"""
Parse CU data from Solana validator logs (if you have them).

This script reads Solana logs or output files and extracts CU consumption metrics.
Useful if you collected logs from a validator or development environment.

Usage:
  python extract_cu_from_logs.py --logfile solana_logs.txt --output cu_data.csv
"""

import re
import argparse
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class LogParser:
    """Parse Solana transaction logs for CU data"""
    
    # Regex patterns for common log formats
    PATTERNS = {
        # Solana standard: "Program consumed X compute units"
        'standard_consumed': r'Program consumed (\d+) compute units',
        
        # Anchor logs: specific instruction markers
        'anchor_parse': r'Program log: Starting (?:parse|instruction) (\w+)',
        'anchor_op': r'Program log: (.+?) (operation|step)',
        
        # Custom markers (adjust for your program)
        'make_escrow': r'make_escrow|execute_swap',
        'blind_update': r'blind(\_)?update',
        'fast_update': r'fast(\_)?update|quick',
        'full_update': r'full(\_)?update|complete',
        
        # Curve detection
        'curve_a': r'curve.?a|linear',
        'curve_b': r'curve.?b',
        'curve_c': r'curve.?c|polynomial',
        'mixed': r'mixed|multi.?curve',
        
        # Direction detection
        'buy': r'\bbuy\b|purchase|acquisition',
        'sell': r'\bsell\b|disposal|liquidation',
    }
    
    def __init__(self):
        self.records: List[Dict] = []
    
    def extract_cu_value(self, line: str) -> Optional[int]:
        """Extract CU number from log line"""
        match = re.search(self.PATTERNS['standard_consumed'], line)
        if match:
            return int(match.group(1))
        return None
    
    def detect_operation_type(self, log_block: str) -> Optional[str]:
        """Infer operation type from log block"""
        log_lower = log_block.lower()
        
        # Determine operation category
        if re.search(self.PATTERNS['make_escrow'], log_lower):
            op_type = 'swap'
        elif re.search(self.PATTERNS['blind_update'], log_lower):
            return 'blind_update'
        elif re.search(self.PATTERNS['fast_update'], log_lower):
            return 'fast_update'
        elif re.search(self.PATTERNS['full_update'], log_lower):
            op_type = 'full_update'
            
            # Determine scope
            if 'oracle' in log_lower:
                return 'full_update_oracle'
            elif 'both' in log_lower or 'bid_all' in log_lower and 'ask_all' in log_lower:
                return 'full_update_both'
            elif 'bid' in log_lower:
                return 'full_update_bid'
            elif 'ask' in log_lower:
                return 'full_update_ask'
            else:
                return 'full_update'
        else:
            return None
        
        # For swaps: determine curve and direction
        if op_type == 'swap':
            direction = 'buy' if re.search(self.PATTERNS['buy'], log_lower) else 'sell'
            
            if re.search(self.PATTERNS['curve_c'], log_lower):
                curve = 'c'
            elif re.search(self.PATTERNS['curve_b'], log_lower):
                curve = 'b'
            elif re.search(self.PATTERNS['mixed'], log_lower):
                curve = 'mixed'
            else:
                curve = 'a'
            
            return f'swap_{direction}_{curve}'
        
        return None
    
    def parse_file(
        self,
        logfile: str,
        delimiter: str = '---',
        verbose: bool = True
    ) -> List[Dict]:
        """
        Parse log file for CU data.
        
        Assumes each transaction is delimited by a separator line.
        """
        self.records = []
        
        if not Path(logfile).exists():
            print(f"❌ File not found: {logfile}")
            return []
        
        with open(logfile, 'r') as f:
            content = f.read()
        
        # Split into transaction blocks
        blocks = content.split(delimiter)
        
        if verbose:
            print(f"📖 Parsing {len(blocks)} transaction blocks...")
        
        processed = 0
        for block_idx, block in enumerate(blocks):
            if not block.strip():
                continue
            
            # Extract CU value
            cu = None
            for line in block.split('\n'):
                cu_val = self.extract_cu_value(line)
                if cu_val:
                    cu = cu_val
                    break
            
            if not cu:
                continue
            
            # Detect operation type
            operation = self.detect_operation_type(block)
            if not operation:
                operation = 'unknown'
            
            # Create record
            record = {
                'operation': operation,
                'cu': cu,
                'timestamp': datetime.now().isoformat(),
                'slot': block_idx,
                'tx_hash': f'log_{block_idx:06d}',
                'base_cu': None,
                'remaining_cu': None
            }
            self.records.append(record)
            processed += 1
        
        if verbose:
            print(f"✓ Extracted {processed} CU measurements from {logfile}")
        
        return self.records
    
    def parse_csv_logs(
        self,
        csv_file: str,
        cu_column: str = 'compute_units',
        operation_column: Optional[str] = None,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Parse existing CSV file that already has CU data.
        
        Useful if you already have a structured export from validator.
        """
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return []
        
        self.records = []
        
        if cu_column not in df.columns:
            print(f"❌ Column '{cu_column}' not found. Available: {list(df.columns)}")
            return []
        
        for idx, row in df.iterrows():
            # Get CU value
            cu = row[cu_column]
            if pd.isna(cu):
                continue
            
            # Get operation type (from column or infer from other fields)
            if operation_column and operation_column in df.columns:
                operation = row[operation_column]
            else:
                # Try to infer from row data
                operation = self._infer_from_row(row)
            
            record = {
                'operation': operation,
                'cu': int(cu),
                'timestamp': row.get('timestamp', datetime.now().isoformat()),
                'slot': int(row.get('slot', idx)),
                'tx_hash': row.get('tx_hash', f'csv_{idx:06d}'),
                'base_cu': None,
                'remaining_cu': None
            }
            self.records.append(record)
        
        if verbose:
            print(f"✓ Parsed {len(self.records)} records from {csv_file}")
        
        return self.records
    
    def _infer_from_row(self, row: Dict) -> str:
        """Try to infer operation from row data"""
        row_str = ' '.join([str(v).lower() for v in row.values()])
        
        if 'swap' in row_str:
            return 'unknown_swap'
        elif 'update' in row_str:
            return 'unknown_update'
        else:
            return 'unknown'
    
    def save_to_csv(self, output_path: str = 'outputs/cu_benchmark_logs.csv') -> str:
        """Save parsed records to CSV"""
        if not self.records:
            print("⚠️  No records to save")
            return output_path
        
        df = pd.DataFrame(self.records)
        df.to_csv(output_path, index=False)
        
        print(f"✅ Saved {len(df)} records to {output_path}")
        print("\n📊 Distribution by operation:")
        print(df['operation'].value_counts())
        
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Parse Solana logs for CU data'
    )
    
    # Source selection
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--logfile',
        help='Parse Solana log text file'
    )
    source_group.add_argument(
        '--csv',
        help='Parse CSV file with CU data'
    )
    
    # Options
    parser.add_argument(
        '--output',
        default='outputs/cu_benchmark_logs.csv',
        help='Output CSV path'
    )
    parser.add_argument(
        '--cu-column',
        default='compute_units',
        help='Name of CU column in CSV'
    )
    parser.add_argument(
        '--op-column',
        help='Name of operation column in CSV (optional)'
    )
    parser.add_argument(
        '--delimiter',
        default='---',
        help='Transaction delimiter in log file'
    )
    
    args = parser.parse_args()
    
    # Run parsing
    log_parser = LogParser()
    
    if args.logfile:
        log_parser.parse_file(
            logfile=args.logfile,
            delimiter=args.delimiter,
            verbose=True
        )
    else:
        log_parser.parse_csv_logs(
            csv_file=args.csv,
            cu_column=args.cu_column,
            operation_column=args.op_column,
            verbose=True
        )
    
    # Save results
    output_path = log_parser.save_to_csv(args.output)
    print(f"\n🚀 Ready for heatmap! Open CU_PERCENTILE_HEATMAP.ipynb with {output_path}")


if __name__ == '__main__':
    main()
