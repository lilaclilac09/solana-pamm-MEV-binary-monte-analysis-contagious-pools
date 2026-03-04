#!/usr/bin/env python3
"""
Oracle Staleness Analyzer
=========================

Analyzes how slot jumps create oracle price staleness windows that enable
MEV exploitation through liquidations, arbitrage, and other oracle-dependent attacks.

Author: MEV Analysis Team
Date: March 3, 2026
"""

import json
import argparse
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict


def _repair_invalid_json_escapes(raw_text: str) -> str:
    fixed_text = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', raw_text)
    fixed_text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', fixed_text)
    return fixed_text


def _load_json_safe(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file_handle:
        raw_text = file_handle.read()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        repaired_text = _repair_invalid_json_escapes(raw_text)
        if repaired_text != raw_text:
            print(f"⚠️ Repaired invalid JSON escape sequences in {filepath}")
            return json.loads(repaired_text)
        raise


@dataclass
class OracleStalenessEvent:
    """Oracle price staleness event during slot jump"""
    oracle_account: str
    oracle_type: str  # 'pyth', 'switchboard', 'chainlink'
    asset_symbol: str
    slot_jump_start: int
    slot_jump_end: int
    last_update_slot: int
    staleness_duration_slots: int
    staleness_duration_ms: float
    price_at_jump: float
    price_after_jump: float
    price_deviation_percent: float
    mev_opportunities_created: int
    

@dataclass
class LiquidationWindow:
    """Liquidation opportunity window created by oracle staleness"""
    defi_protocol: str
    asset: str
    oracle_account: str
    staleness_slots: int
    potential_liquidations: int
    total_liquidation_value_usd: float
    was_exploited: bool
    actual_mev_extracted_usd: float


class OracleStalenessAnalyzer:
    """
    Analyzes oracle price staleness during slot jumps and correlation with MEV
    """
    
    # Staleness thresholds (in slots)
    CRITICAL_STALENESS = 20   # >20 slots is critical
    WARNING_STALENESS = 10    # 10-20 slots is warning
    NORMAL_UPDATE_FREQ = 5    # Oracles should update every ~5 slots
    
    def __init__(self):
        self.slot_jumps = []
        self.oracle_updates = []
        self.mev_events = []
        self.staleness_events = []
        self.liquidation_windows = []
        
    def load_slot_jumps(self, filepath: str) -> None:
        """Load slot jump data"""
        print(f"Loading slot jump data from {filepath}...")
        data = _load_json_safe(filepath)
        self.slot_jumps = data.get('jump_events', [])
        print(f"Loaded {len(self.slot_jumps)} slot jump events")
        
    def load_oracle_updates(self, filepath: str) -> None:
        """Load oracle price update history"""
        print(f"Loading oracle update data from {filepath}...")
        loaded = _load_json_safe(filepath)
        if isinstance(loaded, list):
            self.oracle_updates = loaded
        elif isinstance(loaded, dict):
            self.oracle_updates = loaded.get('updates', loaded.get('data', []))
        else:
            raise ValueError(f"Unexpected oracle updates format in {filepath}: {type(loaded)}")

        if not isinstance(self.oracle_updates, list):
            raise ValueError(f"Oracle updates payload must be a list after normalization: {filepath}")
        print(f"Loaded {len(self.oracle_updates)} oracle updates")
        
    def load_mev_events(self, filepath: str) -> None:
        """Load MEV events"""
        print(f"Loading MEV event data from {filepath}...")
        loaded = _load_json_safe(filepath)
        if isinstance(loaded, list):
            self.mev_events = loaded
        elif isinstance(loaded, dict):
            self.mev_events = loaded.get('events', loaded.get('data', []))
        else:
            raise ValueError(f"Unexpected MEV event format in {filepath}: {type(loaded)}")

        if not isinstance(self.mev_events, list):
            raise ValueError(f"MEV event payload must be a list after normalization: {filepath}")
        print(f"Loaded {len(self.mev_events)} MEV events")
        
    def detect_staleness_events(self) -> List[OracleStalenessEvent]:
        """
        Detect oracle staleness events during slot jumps
        
        Returns:
            List of OracleStalenessEvent objects
        """
        print("Detecting oracle staleness events...")
        staleness_events = []
        
        # Group oracle updates by oracle account
        oracle_timelines = defaultdict(list)
        for update in self.oracle_updates:
            oracle_account = update.get('oracle_account', '')
            oracle_timelines[oracle_account].append(update)
        
        # Sort each timeline by slot
        for oracle_account in oracle_timelines:
            oracle_timelines[oracle_account].sort(key=lambda x: x.get('slot', 0))
        
        # Analyze each slot jump for oracle staleness
        for jump in self.slot_jumps:
            jump_start = jump['start_slot']
            jump_end = jump['end_slot']
            
            # Check each oracle for staleness during this jump
            for oracle_account, updates in oracle_timelines.items():
                event = self._analyze_oracle_during_jump(
                    oracle_account,
                    updates,
                    jump
                )
                
                if event:
                    staleness_events.append(event)
        
        self.staleness_events = staleness_events
        print(f"Detected {len(staleness_events)} oracle staleness events")
        
        return staleness_events
    
    def _analyze_oracle_during_jump(
        self,
        oracle_account: str,
        updates: List[Dict],
        jump: Dict
    ) -> Optional[OracleStalenessEvent]:
        """
        Analyze single oracle for staleness during a slot jump
        
        Returns:
            OracleStalenessEvent if staleness detected, None otherwise
        """
        jump_start = jump['start_slot']
        jump_end = jump['end_slot']
        
        # Find last update before jump
        last_update_before = None
        for update in updates:
            if update['slot'] < jump_start:
                last_update_before = update
            else:
                break
        
        # Find first update after jump
        first_update_after = None
        for update in updates:
            if update['slot'] > jump_end:
                first_update_after = update
                break
        
        if not last_update_before:
            return None
        
        # Calculate staleness duration
        staleness_slots = jump_end - last_update_before['slot']
        
        # Only report if staleness exceeds warning threshold
        if staleness_slots < self.WARNING_STALENESS:
            return None
        
        # Calculate price deviation if we have update after jump
        price_deviation = 0.0
        price_after = last_update_before.get('price', 0)
        
        if first_update_after:
            price_before = last_update_before.get('price', 0)
            price_after = first_update_after.get('price', 0)
            
            if price_before > 0:
                price_deviation = abs(
                    (price_after - price_before) / price_before * 100
                )
        
        # Estimate staleness duration in milliseconds
        staleness_ms = staleness_slots * 400  # ~400ms per slot
        
        # Count MEV opportunities in this window
        mev_count = sum(
            1 for mev in self.mev_events
            if jump_start <= mev.get('slot', 0) <= jump_end + 20  # Include post-jump window
            and mev.get('oracle_account') == oracle_account
        )
        
        return OracleStalenessEvent(
            oracle_account=oracle_account,
            oracle_type=last_update_before.get('oracle_type', 'unknown'),
            asset_symbol=last_update_before.get('asset_symbol', 'UNKNOWN'),
            slot_jump_start=jump_start,
            slot_jump_end=jump_end,
            last_update_slot=last_update_before['slot'],
            staleness_duration_slots=staleness_slots,
            staleness_duration_ms=staleness_ms,
            price_at_jump=last_update_before.get('price', 0),
            price_after_jump=price_after,
            price_deviation_percent=price_deviation,
            mev_opportunities_created=mev_count
        )
    
    def identify_liquidation_windows(self) -> List[LiquidationWindow]:
        """
        Identify liquidation opportunity windows created by oracle staleness
        
        Returns:
            List of LiquidationWindow objects
        """
        print("Identifying liquidation windows...")
        windows = []
        
        # Group staleness events by DeFi protocol/asset
        # (In real implementation, would query on-chain protocol state)
        
        for event in self.staleness_events:
            # Only consider critical staleness for liquidations
            if event.staleness_duration_slots < self.CRITICAL_STALENESS:
                continue
            
            # Find liquidation MEV events in the window
            liquidation_mev = [
                mev for mev in self.mev_events
                if (mev.get('mev_type') == 'liquidation' and
                    mev.get('oracle_account') == event.oracle_account and
                    event.slot_jump_start <= mev.get('slot', 0) <= event.slot_jump_end + 50)
            ]
            
            if liquidation_mev or event.price_deviation_percent > 1.0:
                # Significant deviation suggests liquidation opportunity
                total_value = sum(
                    mev.get('profit_usd', 0) for mev in liquidation_mev
                )
                
                window = LiquidationWindow(
                    defi_protocol=self._guess_protocol(event.oracle_account),
                    asset=event.asset_symbol,
                    oracle_account=event.oracle_account,
                    staleness_slots=event.staleness_duration_slots,
                    potential_liquidations=len(liquidation_mev),
                    total_liquidation_value_usd=total_value,
                    was_exploited=len(liquidation_mev) > 0,
                    actual_mev_extracted_usd=total_value
                )
                
                windows.append(window)
        
        self.liquidation_windows = windows
        print(f"Identified {len(windows)} liquidation windows")
        
        return windows
    
    def _guess_protocol(self, oracle_account: str) -> str:
        """Guess DeFi protocol from oracle account (placeholder)"""
        # In real implementation, would map oracle to known protocols
        return "UNKNOWN_PROTOCOL"
    
    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive statistics"""
        if not self.staleness_events:
            return {}
        
        staleness_durations = [
            e.staleness_duration_slots for e in self.staleness_events
        ]
        price_deviations = [
            e.price_deviation_percent for e in self.staleness_events
        ]
        
        # Categorize by severity
        critical = [e for e in self.staleness_events 
                   if e.staleness_duration_slots >= self.CRITICAL_STALENESS]
        warning = [e for e in self.staleness_events 
                  if self.WARNING_STALENESS <= e.staleness_duration_slots < self.CRITICAL_STALENESS]
        
        # MEV correlation
        events_with_mev = [e for e in self.staleness_events if e.mev_opportunities_created > 0]
        
        return {
            'total_staleness_events': len(self.staleness_events),
            'critical_staleness_events': len(critical),
            'warning_staleness_events': len(warning),
            'avg_staleness_duration_slots': np.mean(staleness_durations),
            'max_staleness_duration_slots': max(staleness_durations),
            'avg_price_deviation_percent': np.mean(price_deviations),
            'max_price_deviation_percent': max(price_deviations),
            'events_with_mev': len(events_with_mev),
            'mev_correlation_rate': len(events_with_mev) / len(self.staleness_events),
            'total_liquidation_windows': len(self.liquidation_windows),
            'exploited_windows': sum(1 for w in self.liquidation_windows if w.was_exploited),
            'total_liquidation_mev_usd': sum(
                w.actual_mev_extracted_usd for w in self.liquidation_windows
            )
        }
    
    def export_results(self, output_path: str) -> None:
        """Export analysis results"""
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'staleness_events': [asdict(e) for e in self.staleness_events],
            'liquidation_windows': [asdict(w) for w in self.liquidation_windows],
            'statistics': self.calculate_statistics()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {output_path}")
    
    def generate_report(self) -> str:
        """Generate human-readable analysis report"""
        stats = self.calculate_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║       ORACLE STALENESS & MEV IMPACT ANALYSIS REPORT          ║
╚══════════════════════════════════════════════════════════════╝

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STALENESS EVENTS SUMMARY
─────────────────────────────────────────────────────────────
Total Events:           {stats.get('total_staleness_events', 0):,}
  • Critical (>20 slots): {stats.get('critical_staleness_events', 0):,}
  • Warning (10-20):     {stats.get('warning_staleness_events', 0):,}

Average Duration:       {stats.get('avg_staleness_duration_slots', 0):.1f} slots
Maximum Duration:       {stats.get('max_staleness_duration_slots', 0):,} slots

PRICE IMPACT
─────────────────────────────────────────────────────────────
Avg Price Deviation:    {stats.get('avg_price_deviation_percent', 0):.2f}%
Max Price Deviation:    {stats.get('max_price_deviation_percent', 0):.2f}%

MEV CORRELATION
─────────────────────────────────────────────────────────────
Events with MEV:        {stats.get('events_with_mev', 0):,}
MEV Correlation Rate:   {stats.get('mev_correlation_rate', 0)*100:.1f}%

LIQUIDATION ANALYSIS
─────────────────────────────────────────────────────────────
Total Windows:          {stats.get('total_liquidation_windows', 0):,}
Exploited Windows:      {stats.get('exploited_windows', 0):,}
Total MEV Value:        ${stats.get('total_liquidation_mev_usd', 0):,.2f}

TOP STALENESS EVENTS (by MEV impact)
─────────────────────────────────────────────────────────────
"""
        
        # Sort staleness events by MEV impact
        sorted_events = sorted(
            self.staleness_events,
            key=lambda x: x.mev_opportunities_created,
            reverse=True
        )
        
        for i, event in enumerate(sorted_events[:10], 1):
            report += f"\n{i}. {event.asset_symbol} ({event.oracle_type})"
            report += f"\n   Staleness:    {event.staleness_duration_slots} slots"
            report += f"   ({event.staleness_duration_ms:.0f}ms)"
            report += f"\n   Price Change: {event.price_deviation_percent:.2f}%"
            report += f"\n   MEV Events:   {event.mev_opportunities_created}"
            report += "\n"
        
        report += "\n" + "═" * 62 + "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Analyze oracle staleness during slot jumps'
    )
    parser.add_argument(
        '--slot-jumps',
        type=str,
        required=True,
        help='Path to slot jump analysis JSON'
    )
    parser.add_argument(
        '--oracle-updates',
        type=str,
        required=True,
        help='Path to oracle update history JSON'
    )
    parser.add_argument(
        '--mev-events',
        type=str,
        required=True,
        help='Path to MEV events JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/oracle_staleness_analysis.json',
        help='Output path for results'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = OracleStalenessAnalyzer()
    
    # Load data
    analyzer.load_slot_jumps(args.slot_jumps)
    analyzer.load_oracle_updates(args.oracle_updates)
    analyzer.load_mev_events(args.mev_events)
    
    # Run analysis
    analyzer.detect_staleness_events()
    analyzer.identify_liquidation_windows()
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Export results
    analyzer.export_results(args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
