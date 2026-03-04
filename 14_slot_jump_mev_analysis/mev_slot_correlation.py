#!/usr/bin/env python3
"""
MEV-Slot Jump Correlation Analyzer
===================================

Analyzes the correlation between slot jumps and MEV extraction events.
Tests hypotheses about how slot jumps create or enhance MEV opportunities.

Author: MEV Analysis Team
Date: March 3, 2026
"""

import json
import argparse
import re
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from scipy import stats
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


def _json_scalar_default(obj):
    if isinstance(obj, np.generic):
        return obj.item()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@dataclass
class MEVSlotCorrelation:
    """Correlation between MEV event and slot jump"""
    mev_transaction_id: str
    mev_type: str  # 'sandwich', 'arbitrage', 'liquidation'
    mev_profit_usd: float
    slot: int
    nearest_jump_slot: int
    slots_after_jump: int
    jump_size: int
    jump_type: str
    correlation_strength: float  # 0-1, how likely jump enabled this MEV
    

@dataclass
class SlotWindowMEVStats:
    """MEV statistics for a time window around slot jumps"""
    window_type: str  # 'pre_jump', 'during_jump', 'post_jump'
    window_start_slot: int
    window_end_slot: int
    total_mev_transactions: int
    total_mev_value_usd: float
    avg_mev_per_tx: float
    sandwich_count: int
    arbitrage_count: int
    liquidation_count: int
    unique_attackers: int


class MEVSlotCorrelationAnalyzer:
    """
    Analyzes correlation between slot jumps and MEV activity
    """
    
    # Time windows for analysis (in slots)
    PRE_JUMP_WINDOW = 10   # Slots before jump
    POST_JUMP_WINDOW = 20  # Slots after jump
    
    def __init__(self):
        self.slot_jumps = []
        self.mev_events = []
        self.correlations = []
        self.window_stats = []
        
    def load_slot_jumps(self, filepath: str) -> None:
        """Load slot jump analysis results"""
        print(f"Loading slot jump data from {filepath}...")
        data = _load_json_safe(filepath)
        self.slot_jumps = data.get('jump_events', [])
        print(f"Loaded {len(self.slot_jumps)} slot jump events")
        
    def load_mev_events(self, filepath: str) -> None:
        """Load MEV event data"""
        print(f"Loading MEV event data from {filepath}...")
        self.mev_events = _load_json_safe(filepath)
        print(f"Loaded {len(self.mev_events)} MEV events")
        
    def correlate_mev_with_jumps(self) -> List[MEVSlotCorrelation]:
        """
        Find correlations between MEV events and slot jumps
        
        Returns:
            List of MEVSlotCorrelation objects
        """
        print("Correlating MEV events with slot jumps...")
        correlations = []
        
        # Create slot jump lookup for fast access
        jump_map = {}
        for jump in self.slot_jumps:
            for slot in range(jump['start_slot'], jump['end_slot'] + 1):
                jump_map[slot] = jump
        
        # Analyze each MEV event
        for mev in self.mev_events:
            mev_slot = mev.get('slot', 0)
            
            # Find nearest slot jump
            nearest_jump = self._find_nearest_jump(mev_slot)
            
            if nearest_jump:
                slots_after = mev_slot - nearest_jump['end_slot']
                
                # Calculate correlation strength
                # Stronger if MEV happened soon after jump
                correlation = self._calculate_correlation_strength(
                    slots_after,
                    nearest_jump['jump_size'],
                    mev.get('mev_type', '')
                )
                
                corr_obj = MEVSlotCorrelation(
                    mev_transaction_id=mev.get('signature', ''),
                    mev_type=mev.get('mev_type', 'unknown'),
                    mev_profit_usd=mev.get('profit_usd', 0.0),
                    slot=mev_slot,
                    nearest_jump_slot=nearest_jump['start_slot'],
                    slots_after_jump=slots_after,
                    jump_size=nearest_jump['jump_size'],
                    jump_type=nearest_jump['jump_type'],
                    correlation_strength=correlation
                )
                
                correlations.append(corr_obj)
        
        self.correlations = correlations
        print(f"Found {len(correlations)} MEV-jump correlations")
        
        return correlations
    
    def _find_nearest_jump(self, slot: int) -> Dict:
        """Find the nearest previous slot jump to a given slot"""
        nearest = None
        min_distance = float('inf')
        
        for jump in self.slot_jumps:
            if jump['end_slot'] <= slot:
                distance = slot - jump['end_slot']
                if distance < min_distance:
                    min_distance = distance
                    nearest = jump
        
        return nearest
    
    def _calculate_correlation_strength(
        self,
        slots_after: int,
        jump_size: int,
        mev_type: str
    ) -> float:
        """
        Calculate correlation strength (0-1)
        
        Factors:
        - Proximity to jump (closer = stronger)
        - Jump size (larger jumps = more MEV opportunity)
        - MEV type (liquidations more correlated with oracle staleness)
        """
        # Base correlation from proximity (exponential decay)
        if slots_after < 0:
            proximity_score = 0.0
        else:
            # Half-life of 10 slots
            proximity_score = np.exp(-0.0693 * slots_after)
        
        # Jump size multiplier (normalize to 1-5 slots)
        jump_multiplier = min(jump_size / 5.0, 2.0)
        
        # MEV type multiplier
        type_multipliers = {
            'liquidation': 1.5,  # Highly correlated with oracle staleness
            'arbitrage': 1.3,    # Correlated with price discrepancies
            'sandwich': 1.0,     # Less directly correlated
        }
        type_multiplier = type_multipliers.get(mev_type, 1.0)
        
        # Combined score (capped at 1.0)
        correlation = min(
            proximity_score * jump_multiplier * type_multiplier,
            1.0
        )
        
        return correlation
    
    def analyze_windows(self) -> List[SlotWindowMEVStats]:
        """
        Analyze MEV activity in windows around slot jumps
        
        Compares:
        - Pre-jump window (baseline)
        - During jump
        - Post-jump window (MEV spike?)
        """
        print("Analyzing MEV activity in time windows...")
        window_stats = []
        
        for jump in self.slot_jumps:
            start = jump['start_slot']
            end = jump['end_slot']
            
            # Define windows
            windows = [
                ('pre_jump', start - self.PRE_JUMP_WINDOW, start - 1),
                ('during_jump', start, end),
                ('post_jump', end + 1, end + self.POST_JUMP_WINDOW)
            ]
            
            for window_type, win_start, win_end in windows:
                # Filter MEV events in window
                window_mev = [
                    mev for mev in self.mev_events
                    if win_start <= mev.get('slot', 0) <= win_end
                ]
                
                if window_mev:
                    stats_obj = self._calculate_window_stats(
                        window_type,
                        win_start,
                        win_end,
                        window_mev
                    )
                    window_stats.append(stats_obj)
        
        self.window_stats = window_stats
        print(f"Analyzed {len(window_stats)} time windows")
        
        return window_stats
    
    def _calculate_window_stats(
        self,
        window_type: str,
        start_slot: int,
        end_slot: int,
        mev_events: List[Dict]
    ) -> SlotWindowMEVStats:
        """Calculate MEV statistics for a time window"""
        total_value = sum(mev.get('profit_usd', 0.0) for mev in mev_events)
        
        # Count by type
        type_counts = defaultdict(int)
        for mev in mev_events:
            type_counts[mev.get('mev_type', 'unknown')] += 1
        
        # Unique attackers
        attackers = set(mev.get('attacker', '') for mev in mev_events)
        
        return SlotWindowMEVStats(
            window_type=window_type,
            window_start_slot=start_slot,
            window_end_slot=end_slot,
            total_mev_transactions=len(mev_events),
            total_mev_value_usd=total_value,
            avg_mev_per_tx=total_value / len(mev_events) if mev_events else 0.0,
            sandwich_count=type_counts['sandwich'],
            arbitrage_count=type_counts['arbitrage'],
            liquidation_count=type_counts['liquidation'],
            unique_attackers=len(attackers)
        )
    
    def statistical_tests(self) -> Dict:
        """
        Perform statistical tests on MEV-jump correlations
        
        Tests:
        1. T-test: MEV value in post-jump vs pre-jump windows
        2. Chi-square: MEV type distribution differences
        3. Correlation: Jump size vs MEV value
        """
        print("Performing statistical tests...")
        
        # Separate window stats by type
        pre_jump = [w for w in self.window_stats if w.window_type == 'pre_jump']
        post_jump = [w for w in self.window_stats if w.window_type == 'post_jump']
        
        results = {}
        
        # Test 1: MEV value comparison (pre vs post)
        if pre_jump and post_jump:
            pre_values = [w.total_mev_value_usd for w in pre_jump]
            post_values = [w.total_mev_value_usd for w in post_jump]
            
            t_stat, p_value = stats.ttest_ind(post_values, pre_values)
            
            results['mev_value_test'] = {
                'test': 'Independent t-test',
                'hypothesis': 'MEV value increases after slot jumps',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'mean_pre_jump': np.mean(pre_values),
                'mean_post_jump': np.mean(post_values),
                'percent_increase': (
                    (np.mean(post_values) - np.mean(pre_values)) / 
                    np.mean(pre_values) * 100
                ) if np.mean(pre_values) > 0 else 0
            }
        
        # Test 2: Correlation between jump size and MEV value
        if self.correlations:
            jump_sizes = [c.jump_size for c in self.correlations]
            mev_values = [c.mev_profit_usd for c in self.correlations]
            
            correlation, p_value = stats.pearsonr(jump_sizes, mev_values)
            
            results['jump_size_correlation'] = {
                'test': 'Pearson correlation',
                'hypothesis': 'Larger jumps correlate with higher MEV',
                'correlation_coefficient': float(correlation),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        # Test 3: MEV spike frequency after jumps
        if post_jump:
            # Define "spike" as value > 1.5x median
            median_mev = np.median([w.total_mev_value_usd for w in self.window_stats])
            spike_threshold = median_mev * 1.5
            
            post_jump_spikes = sum(
                1 for w in post_jump 
                if w.total_mev_value_usd > spike_threshold
            )
            spike_rate = post_jump_spikes / len(post_jump)
            
            results['mev_spike_analysis'] = {
                'test': 'Spike frequency analysis',
                'spike_threshold_usd': float(spike_threshold),
                'post_jump_spike_rate': float(spike_rate),
                'total_post_jump_windows': len(post_jump),
                'spike_count': post_jump_spikes
            }
        
        print("Statistical tests complete")
        return results
    
    def export_results(self, output_path: str) -> None:
        """Export correlation analysis results"""
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_mev_events': len(self.mev_events),
            'total_slot_jumps': len(self.slot_jumps),
            'correlations': [asdict(c) for c in self.correlations],
            'window_statistics': [asdict(w) for w in self.window_stats],
            'statistical_tests': self.statistical_tests(),
            'summary': self._generate_summary()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=_json_scalar_default)
        
        print(f"Results exported to {output_path}")
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        high_correlation = [
            c for c in self.correlations 
            if c.correlation_strength > 0.7
        ]
        
        post_jump = [w for w in self.window_stats if w.window_type == 'post_jump']
        
        return {
            'total_correlations': len(self.correlations),
            'high_correlation_count': len(high_correlation),
            'avg_correlation_strength': np.mean([
                c.correlation_strength for c in self.correlations
            ]) if self.correlations else 0,
            'total_correlated_mev_value': sum([
                c.mev_profit_usd for c in high_correlation
            ]),
            'avg_post_jump_mev_value': np.mean([
                w.total_mev_value_usd for w in post_jump
            ]) if post_jump else 0,
            'liquidation_correlation_rate': sum(
                1 for c in high_correlation if c.mev_type == 'liquidation'
            ) / len(high_correlation) if high_correlation else 0
        }
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        stats = self.statistical_tests()
        summary = self._generate_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║       MEV-SLOT JUMP CORRELATION ANALYSIS REPORT              ║
╚══════════════════════════════════════════════════════════════╝

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATA SUMMARY
─────────────────────────────────────────────────────────────
Total MEV Events:       {len(self.mev_events):,}
Total Slot Jumps:       {len(self.slot_jumps):,}
Correlations Found:     {summary['total_correlations']:,}
High Correlations:      {summary['high_correlation_count']:,}

CORRELATION STRENGTH
─────────────────────────────────────────────────────────────
Average Strength:       {summary['avg_correlation_strength']:.3f}
Total Correlated Value: ${summary['total_correlated_mev_value']:,.2f}

STATISTICAL TESTS
─────────────────────────────────────────────────────────────
"""
        
        # Add test results
        if 'mev_value_test' in stats:
            test = stats['mev_value_test']
            report += f"\n1. MEV Value Post-Jump Test"
            report += f"\n   • Mean Pre-Jump:  ${test['mean_pre_jump']:,.2f}"
            report += f"\n   • Mean Post-Jump: ${test['mean_post_jump']:,.2f}"
            report += f"\n   • Increase:       {test['percent_increase']:.1f}%"
            report += f"\n   • P-value:        {test['p_value']:.4f}"
            report += f"\n   • Significant:    {'YES ✓' if test['significant'] else 'NO ✗'}"
            report += "\n"
        
        if 'jump_size_correlation' in stats:
            test = stats['jump_size_correlation']
            report += f"\n2. Jump Size Correlation"
            report += f"\n   • Correlation:    {test['correlation_coefficient']:.3f}"
            report += f"\n   • P-value:        {test['p_value']:.4f}"
            report += f"\n   • Significant:    {'YES ✓' if test['significant'] else 'NO ✗'}"
            report += "\n"
        
        if 'mev_spike_analysis' in stats:
            test = stats['mev_spike_analysis']
            report += f"\n3. Post-Jump MEV Spikes"
            report += f"\n   • Spike Rate:     {test['post_jump_spike_rate']*100:.1f}%"
            report += f"\n   • Spike Count:    {test['spike_count']}"
            report += f"\n   • Threshold:      ${test['spike_threshold_usd']:,.2f}"
            report += "\n"
        
        report += "\n" + "═" * 62 + "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Analyze correlation between slot jumps and MEV events'
    )
    parser.add_argument(
        '--slot-data',
        type=str,
        required=True,
        help='Path to slot jump analysis JSON'
    )
    parser.add_argument(
        '--mev-data',
        type=str,
        required=True,
        help='Path to MEV events JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/mev_slot_correlation.json',
        help='Output path for results'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = MEVSlotCorrelationAnalyzer()
    
    # Load data
    analyzer.load_slot_jumps(args.slot_data)
    analyzer.load_mev_events(args.mev_data)
    
    # Run analysis
    analyzer.correlate_mev_with_jumps()
    analyzer.analyze_windows()
    
    # Generate report
    report = analyzer.generate_report()
    print(report)
    
    # Export results
    analyzer.export_results(args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
