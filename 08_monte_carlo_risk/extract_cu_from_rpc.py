#!/usr/bin/env python3
"""
Extract CU (Compute Unit) data from Solana RPC transactions.

This script queries your Prop AMM program on Solana and extracts CU consumption
for each operation type, building a dataset for the CU Percentile Heatmap.

Usage:
  python extract_cu_from_rpc.py --program <PROGRAM_ID> --limit 1000 --output cu_benchmark_logs.csv
"""

import json
import argparse
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import base58

try:
    from solders.rpc.responses import GetTransactionResp
    import httpx
except ImportError:
    print("⚠️  Install required packages:")
    print("  pip install solders httpx")
    raise


@dataclass
class CURecord:
    """Represents one CU measurement"""
    operation: str
    cu: int
    timestamp: str
    slot: int
    tx_hash: str
    base_cu: Optional[int] = None
    remaining_cu: Optional[int] = None
    
    def to_dict(self):
        return {
            'operation': self.operation,
            'cu': self.cu,
            'timestamp': self.timestamp,
            'slot': self.slot,
            'tx_hash': self.tx_hash,
            'base_cu': self.base_cu,
            'remaining_cu': self.remaining_cu
        }


class CUExtractor:
    """Extract CU data from Solana transactions"""
    
    # Operation name mappings (inferred from logs/instruction data)
    OPERATION_NAMES = {
        'blind_update': 'BlindUpdate / blindupdate',
        'fast_update_all': 'FastUpdate / all',
        'full_update_oracle': 'FullUpdate / oracle-only',
        'full_update_bid': 'FullUpdate / bid-all',
        'full_update_ask': 'FullUpdate / ask-all',
        'full_update_both': 'FullUpdate / both-all',
        'swap_sell_a': 'Swap Sell / Curve A',
        'swap_sell_b': 'Swap Sell / Curve B',
        'swap_sell_c': 'Swap Sell / Curve C',
        'swap_sell_mixed': 'Swap Sell / mixed',
        'swap_buy_a': 'Swap Buy / Curve A',
        'swap_buy_b': 'Swap Buy / Curve B',
        'swap_buy_c': 'Swap Buy / Curve C',
        'swap_buy_mixed': 'Swap Buy / mixed',
    }
    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        """Initialize with RPC endpoint"""
        self.rpc_url = rpc_url
        self.client = httpx.Client(timeout=30.0)
        self.records: List[CURecord] = []
        
    def __del__(self):
        """Cleanup HTTP client"""
        if hasattr(self, 'client'):
            self.client.close()
    
    def _rpc_call(self, method: str, params: list) -> dict:
        """Make RPC call to Solana validator"""
        payload = {
            'jsonrpc': '2.0',
            'id': '1',
            'method': method,
            'params': params
        }
        try:
            response = self.client.post(
                self.rpc_url,
                json=payload,
                timeout=30.0
            )
            result = response.json()
            if 'error' in result:
                print(f"⚠️  RPC Error: {result['error']}")
                return {}
            return result.get('result', {})
        except Exception as e:
            print(f"❌ RPC call failed: {e}")
            return {}
    
    def extract_operation_type(self, logs: List[str], instruction_data: str) -> Optional[str]:
        """
        Infer operation type from transaction logs and instruction data.
        
        Look for markers like:
        - "parse" + "make_escrow" → Swap operation
        - "new" + "blindupdate" → BlindUpdate
        - "close" → FullUpdate
        - Instruction discriminator analysis
        """
        log_text = '\n'.join(logs).lower()
        
        # Check for specific operation markers
        if 'make_escrow' in log_text or 'execute_swap' in log_text:
            # Parse direction and curve from logs or instruction
            if 'sell' in log_text:
                if 'curve_c' in log_text or 'polynomial' in log_text:
                    return 'swap_sell_c'
                elif 'curve_b' in log_text:
                    return 'swap_sell_b'
                elif 'mixed' in log_text:
                    return 'swap_sell_mixed'
                else:
                    return 'swap_sell_a'
            elif 'buy' in log_text:
                if 'curve_c' in log_text or 'polynomial' in log_text:
                    return 'swap_buy_c'
                elif 'curve_b' in log_text:
                    return 'swap_buy_b'
                elif 'mixed' in log_text:
                    return 'swap_buy_mixed'
                else:
                    return 'swap_buy_a'
        
        if 'blindupdate' in log_text or 'blind_update' in log_text:
            return 'blind_update'
        
        if 'fast_update' in log_text or 'quick_oracle' in log_text:
            return 'fast_update_all'
        
        if 'full_update' in log_text or 'complete_update' in log_text:
            if 'oracle' in log_text:
                return 'full_update_oracle'
            elif 'bid' in log_text and 'ask' in log_text:
                return 'full_update_both'
            elif 'bid' in log_text or 'bid_side' in log_text:
                return 'full_update_bid'
            elif 'ask' in log_text or 'ask_side' in log_text:
                return 'full_update_ask'
        
        return None
    
    def extract_cu_from_tx(self, tx_data: Dict) -> Optional[Tuple[int, Optional[str]]]:
        """
        Extract CU consumed from transaction response.
        
        Returns: (cu_consumed, operation_type)
        """
        if not tx_data:
            return None
        
        try:
            # Method 1: unitsConsumed field (newer Solana versions)
            if 'meta' in tx_data and 'computeUnitsConsumed' in tx_data['meta']:
                cu = tx_data['meta']['computeUnitsConsumed']
            
            # Method 2: Parse from logs
            elif 'meta' in tx_data and 'logMessages' in tx_data['meta']:
                logs = tx_data['meta']['logMessages']
                cu = self._parse_cu_from_logs(logs)
            else:
                return None
            
            # Extract operation type
            logs = tx_data['meta'].get('logMessages', []) if 'meta' in tx_data else []
            instruction_data = tx_data.get('transaction', {}).get('message', {}).get('instructions', [{}])[0].get('data', '')
            operation = self.extract_operation_type(logs, instruction_data)
            
            return (cu, operation)
        except Exception as e:
            print(f"⚠️  Error extracting CU: {e}")
            return None
    
    def _parse_cu_from_logs(self, logs: List[str]) -> Optional[int]:
        """Parse CU value from program logs"""
        for log in logs:
            if 'consumed' in log.lower() and 'compute' in log.lower():
                # Try to extract number: "Program consumed X compute units"
                try:
                    parts = log.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            return int(part)
                except:
                    pass
        return None
    
    def get_program_transactions(
        self,
        program_id: str,
        limit: int = 1000,
        before_sig: Optional[str] = None
    ) -> List[str]:
        """Get transaction signatures for a program"""
        params = [program_id, {'limit': min(limit, 1000)}]
        if before_sig:
            params[1]['before'] = before_sig
        
        result = self._rpc_call('getSignaturesForAddress', params)
        return [tx['signature'] for tx in result] if isinstance(result, list) else []
    
    def fetch_transaction(self, signature: str) -> Optional[Dict]:
        """Fetch full transaction data"""
        result = self._rpc_call('getTransaction', [signature, {'encoding': 'json', 'maxSupportedTransactionVersion': 0}])
        return result
    
    def collect_cu_data(
        self,
        program_id: str,
        limit: int = 1000,
        operation_filter: Optional[str] = None,
        verbose: bool = True
    ) -> List[CURecord]:
        """
        Collect CU data from recent transactions to program.
        
        Args:
            program_id: Solana program public key
            limit: Max transactions to query
            operation_filter: Only include specific operation (e.g., 'swap_buy')
            verbose: Print progress
        
        Returns:
            List of CURecord with CU measurements
        """
        self.records = []
        
        if verbose:
            print(f"📡 Querying {limit} transactions for program {program_id[:8]}...")
        
        # Get transaction signatures
        before_sig = None
        total_fetched = 0
        collected_per_op = {}
        
        while total_fetched < limit:
            batch_limit = min(limit - total_fetched, 100)
            sigs = self.get_program_transactions(program_id, limit=batch_limit, before_sig=before_sig)
            
            if not sigs:
                if verbose:
                    print(f"✓ No more signatures found")
                break
            
            for sig in sigs:
                if total_fetched >= limit:
                    break
                
                # Fetch transaction
                tx_data = self.fetch_transaction(sig)
                if not tx_data:
                    continue
                
                # Extract CU
                cu_data = self.extract_cu_from_tx(tx_data)
                if not cu_data:
                    continue
                
                cu_consumed, operation_type = cu_data
                
                # Skip if operation doesn't match filter
                if operation_filter and operation_type != operation_filter:
                    continue
                
                # Create mapped operation name
                mapped_op = self.OPERATION_NAMES.get(operation_type or 'unknown', 'unknown')
                
                # Create record
                slot = tx_data.get('slot', 0)
                timestamp = datetime.now().isoformat()
                
                record = CURecord(
                    operation=mapped_op,
                    cu=cu_consumed,
                    timestamp=timestamp,
                    slot=slot,
                    tx_hash=sig
                )
                self.records.append(record)
                
                # Track collection
                collected_per_op[mapped_op] = collected_per_op.get(mapped_op, 0) + 1
                total_fetched += 1
                
                if verbose and total_fetched % 50 == 0:
                    print(f"  Progress: {total_fetched}/{limit} txs")
            
            before_sig = sigs[-1]
        
        if verbose:
            print(f"\n✅ Collected {len(self.records)} CU measurements")
            print("\nOperations found:")
            for op, count in sorted(collected_per_op.items()):
                print(f"  {op}: {count}")
        
        return self.records
    
    def save_to_csv(self, output_path: str = 'outputs/cu_benchmark_logs.csv') -> str:
        """Save collected records to CSV"""
        if not self.records:
            print("⚠️  No records to save")
            return output_path
        
        df = pd.DataFrame([r.to_dict() for r in self.records])
        df.to_csv(output_path, index=False)
        print(f"✅ Saved {len(df)} records to {output_path}")
        
        # Print summary
        print("\n📊 Summary Statistics:")
        print(df.groupby('operation')['cu'].agg(['count', 'min', 'mean', 'max']) .round(0))
        
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Extract CU data from Solana Prop AMM transactions'
    )
    parser.add_argument(
        '--program',
        required=True,
        help='Solana program ID to query'
    )
    parser.add_argument(
        '--rpc',
        default='https://api.mainnet-beta.solana.com',
        help='RPC endpoint (default: mainnet)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Max transactions to query'
    )
    parser.add_argument(
        '--output',
        default='outputs/cu_benchmark_logs.csv',
        help='Output CSV path'
    )
    parser.add_argument(
        '--operation',
        help='Filter to specific operation type'
    )
    
    args = parser.parse_args()
    
    # Run extraction
    extractor = CUExtractor(rpc_url=args.rpc)
    extractor.collect_cu_data(
        program_id=args.program,
        limit=args.limit,
        operation_filter=args.operation,
        verbose=True
    )
    
    # Save results
    output_path = extractor.save_to_csv(args.output)
    print(f"\n🚀 Ready for heatmap! Next: Open CU_PERCENTILE_HEATMAP.ipynb and point to {output_path}")


if __name__ == '__main__':
    main()
