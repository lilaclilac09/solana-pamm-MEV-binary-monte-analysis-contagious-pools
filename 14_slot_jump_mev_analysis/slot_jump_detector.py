#!/usr/bin/env python3
"""
Slot Jump Detector
==================

Analyzes Solana blockchain data to identify and classify slot jumps (skipped slots).
Distinguishes between accidental skips and intentional DobleZero-style behavior.

Author: MEV Analysis Team
Date: March 3, 2026
"""

import json
import argparse
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np


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
class SlotJumpEvent:
    """Represents a detected slot jump event"""
    start_slot: int
    end_slot: int
    jump_size: int  # Number of skipped slots
    expected_leader: str
    timestamp: str
    previous_block_time: Optional[float]
    next_block_time: Optional[float]
    jump_duration_ms: Optional[float]
    jump_type: str  # 'single', 'consecutive', 'burst'
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ValidatorSkipProfile:
    """Profile of a validator's slot skip behavior"""
    validator_pubkey: str
    total_assigned_slots: int
    total_skipped_slots: int
    skip_rate: float
    consecutive_skip_events: int
    max_consecutive_skips: int
    avg_skip_duration_ms: float
    skip_pattern_entropy: float  # Measure of skip randomness
    is_doblezero_candidate: bool
    

class SlotJumpDetector:
    """
    Detects and analyzes slot jumps in Solana blockchain data.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or "https://api.mainnet-beta.solana.com"
        self.slot_data = []
        self.jump_events = []
        self.validator_profiles = {}
        
    def load_slot_history(self, filepath: str) -> None:
        """Load historical slot data from file"""
        print(f"Loading slot history from {filepath}...")
        loaded = _load_json_safe(filepath)
        if isinstance(loaded, list):
            self.slot_data = loaded
        elif isinstance(loaded, dict):
            self.slot_data = loaded.get('data', loaded.get('slots', loaded.get('slot_history', [])))
        else:
            raise ValueError(f"Unexpected slot history format in {filepath}: {type(loaded)}")

        if not isinstance(self.slot_data, list):
            raise ValueError(f"Slot history payload must be a list after normalization: {filepath}")
        print(f"Loaded {len(self.slot_data)} slot records")
        
    def fetch_slot_history(self, start_epoch: int, end_epoch: int) -> List[Dict]:
        """
        Fetch slot history from Solana RPC (placeholder for real implementation)
        
        In production, this would query:
        - getBlockProduction for validator performance
        - getBlock for each slot to identify skips
        - getLeaderSchedule for expected leaders
        """
        print(f"Fetching slot data for epochs {start_epoch} to {end_epoch}...")
        print("NOTE: This is a placeholder. Real implementation requires RPC access.")
        
        # Placeholder: Generate sample data structure
        sample_data = []
        for epoch in range(start_epoch, end_epoch + 1):
            for slot_offset in range(432000):  # ~432k slots per epoch
                slot = epoch * 432000 + slot_offset
                sample_data.append({
                    'slot': slot,
                    'epoch': epoch,
                    'leader': f"validator_{slot % 100}",  # Placeholder
                    'produced': np.random.random() > 0.05,  # 5% skip rate
                    'timestamp': datetime.now().isoformat(),
                    'block_time': 0.4 if np.random.random() > 0.05 else None
                })
        
        return sample_data
    
    def detect_slot_jumps(self) -> List[SlotJumpEvent]:
        """
        Analyze slot data to detect jumps
        
        Returns:
            List of SlotJumpEvent objects
        """
        print("Detecting slot jumps...")
        jumps = []
        
        for i in range(1, len(self.slot_data)):
            prev_slot = self.slot_data[i - 1]
            curr_slot = self.slot_data[i]
            
            expected_slot = prev_slot['slot'] + 1
            actual_slot = curr_slot['slot']
            
            if actual_slot > expected_slot:
                # Slot jump detected
                jump_size = actual_slot - expected_slot
                
                # Determine jump type
                if jump_size == 1:
                    jump_type = 'single'
                elif jump_size <= 5:
                    jump_type = 'consecutive'
                else:
                    jump_type = 'burst'
                
                # Calculate timing information
                prev_time = prev_slot.get('block_time')
                curr_time = curr_slot.get('block_time')
                jump_duration = None
                
                if prev_time and curr_time:
                    jump_duration = (curr_time - prev_time) * 1000  # Convert to ms
                
                # Create event
                event = SlotJumpEvent(
                    start_slot=expected_slot,
                    end_slot=actual_slot - 1,
                    jump_size=jump_size,
                    expected_leader=self._get_expected_leader(expected_slot),
                    timestamp=curr_slot.get('timestamp', ''),
                    previous_block_time=prev_time,
                    next_block_time=curr_time,
                    jump_duration_ms=jump_duration,
                    jump_type=jump_type
                )
                
                jumps.append(event)
        
        self.jump_events = jumps
        print(f"Detected {len(jumps)} slot jump events")
        return jumps
    
    def _get_expected_leader(self, slot: int) -> str:
        """
        Get expected leader for a slot (placeholder implementation)
        
        Real implementation would query leader schedule
        """
        # Placeholder: return validator based on slot modulo
        return f"validator_{slot % 100}"
    
    def profile_validators(self) -> Dict[str, ValidatorSkipProfile]:
        """
        Create skip behavior profiles for each validator
        
        Returns:
            Dictionary mapping validator pubkey to ValidatorSkipProfile
        """
        print("Profiling validator skip behavior...")
        
        # Aggregate skip data by validator
        validator_stats = defaultdict(lambda: {
            'assigned': 0,
            'skipped': 0,
            'consecutive_skips': [],
            'skip_durations': [],
            'skip_positions': []  # Position in epoch for entropy calculation
        })
        
        # First pass: count assignments and skips
        for slot_record in self.slot_data:
            leader = slot_record.get('leader', '')
            produced = slot_record.get('produced', True)
            
            validator_stats[leader]['assigned'] += 1
            
            if not produced:
                validator_stats[leader]['skipped'] += 1
                validator_stats[leader]['skip_positions'].append(
                    slot_record['slot'] % 432000
                )
        
        # Second pass: identify consecutive skip patterns
        for event in self.jump_events:
            leader = event.expected_leader
            validator_stats[leader]['consecutive_skips'].append(event.jump_size)
            if event.jump_duration_ms:
                validator_stats[leader]['skip_durations'].append(event.jump_duration_ms)
        
        # Create profiles
        profiles = {}
        for validator, stats in validator_stats.items():
            if stats['assigned'] == 0:
                continue
            
            skip_rate = stats['skipped'] / stats['assigned']
            
            # Calculate skip pattern entropy
            entropy = self._calculate_skip_entropy(stats['skip_positions'])
            
            # Determine if validator exhibits DobleZero behavior
            # Criteria:
            # 1. Skip rate > 5%
            # 2. Low entropy (predictable pattern)
            # 3. Frequent consecutive skips
            is_doblezero = (
                skip_rate > 0.05 and
                entropy < 0.3 and
                len(stats['consecutive_skips']) > 5
            )
            
            profile = ValidatorSkipProfile(
                validator_pubkey=validator,
                total_assigned_slots=stats['assigned'],
                total_skipped_slots=stats['skipped'],
                skip_rate=skip_rate,
                consecutive_skip_events=len(stats['consecutive_skips']),
                max_consecutive_skips=max(stats['consecutive_skips']) if stats['consecutive_skips'] else 0,
                avg_skip_duration_ms=np.mean(stats['skip_durations']) if stats['skip_durations'] else 0.0,
                skip_pattern_entropy=entropy,
                is_doblezero_candidate=is_doblezero
            )
            
            profiles[validator] = profile
        
        self.validator_profiles = profiles
        print(f"Profiled {len(profiles)} validators")
        
        # Count DobleZero candidates
        doblezero_count = sum(1 for p in profiles.values() if p.is_doblezero_candidate)
        print(f"Identified {doblezero_count} potential DobleZero validators")
        
        return profiles
    
    def _calculate_skip_entropy(self, skip_positions: List[int]) -> float:
        """
        Calculate entropy of skip pattern to detect intentional vs random skips
        
        Higher entropy = more random (likely accidental)
        Lower entropy = more predictable (likely intentional DobleZero)
        """
        if not skip_positions:
            return 0.0
        
        # Normalize positions to 0-1 range
        max_pos = 432000  # Slots per epoch
        normalized = [p / max_pos for p in skip_positions]
        
        # Calculate histogram
        hist, _ = np.histogram(normalized, bins=20)
        hist = hist / hist.sum()  # Normalize to probabilities
        
        # Calculate Shannon entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10)) / np.log2(20)  # Normalized
        
        return entropy
    
    def export_results(self, output_path: str) -> None:
        """Export analysis results to JSON"""
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_slots_analyzed': len(self.slot_data),
            'total_jump_events': len(self.jump_events),
            'jump_events': [event.to_dict() for event in self.jump_events],
            'validator_profiles': {
                k: asdict(v) for k, v in self.validator_profiles.items()
            },
            'summary_statistics': self._calculate_summary_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {output_path}")
    
    def _calculate_summary_stats(self) -> Dict:
        """Calculate summary statistics"""
        if not self.jump_events:
            return {}
        
        jump_sizes = [e.jump_size for e in self.jump_events]
        durations = [e.jump_duration_ms for e in self.jump_events if e.jump_duration_ms]
        
        return {
            'total_jumps': len(self.jump_events),
            'single_jumps': sum(1 for e in self.jump_events if e.jump_type == 'single'),
            'consecutive_jumps': sum(1 for e in self.jump_events if e.jump_type == 'consecutive'),
            'burst_jumps': sum(1 for e in self.jump_events if e.jump_type == 'burst'),
            'avg_jump_size': np.mean(jump_sizes),
            'max_jump_size': max(jump_sizes),
            'avg_jump_duration_ms': np.mean(durations) if durations else None,
            'total_validators_profiled': len(self.validator_profiles),
            'doblezero_candidates': sum(
                1 for p in self.validator_profiles.values() 
                if p.is_doblezero_candidate
            )
        }
    
    def generate_report(self) -> str:
        """Generate human-readable analysis report"""
        stats = self._calculate_summary_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SLOT JUMP DETECTION ANALYSIS REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Slots Analyzed: {len(self.slot_data):,}

SLOT JUMP SUMMARY
─────────────────────────────────────────────────────────────
Total Jump Events:      {stats.get('total_jumps', 0):,}
  • Single Jumps:       {stats.get('single_jumps', 0):,}
  • Consecutive Jumps:  {stats.get('consecutive_jumps', 0):,}
  • Burst Jumps:        {stats.get('burst_jumps', 0):,}

Average Jump Size:      {stats.get('avg_jump_size', 0):.2f} slots
Maximum Jump Size:      {stats.get('max_jump_size', 0):,} slots
Average Duration:       {stats.get('avg_jump_duration_ms', 0):.2f} ms

VALIDATOR ANALYSIS
─────────────────────────────────────────────────────────────
Total Validators:       {stats.get('total_validators_profiled', 0):,}
DobleZero Candidates:   {stats.get('doblezero_candidates', 0):,}

TOP SKIP VALIDATORS (DobleZero Candidates)
─────────────────────────────────────────────────────────────
"""
        
        # Add top skip validators
        doblezero_validators = [
            (k, v) for k, v in self.validator_profiles.items()
            if v.is_doblezero_candidate
        ]
        doblezero_validators.sort(key=lambda x: x[1].skip_rate, reverse=True)
        
        for i, (validator, profile) in enumerate(doblezero_validators[:10], 1):
            report += f"\n{i}. {validator[:16]}..."
            report += f"\n   Skip Rate: {profile.skip_rate*100:.2f}%"
            report += f"\n   Consecutive Skip Events: {profile.consecutive_skip_events}"
            report += f"\n   Max Consecutive Skips: {profile.max_consecutive_skips}"
            report += f"\n   Pattern Entropy: {profile.skip_pattern_entropy:.3f}"
            report += "\n"
        
        report += "\n" + "═" * 62 + "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Detect and analyze slot jumps in Solana blockchain'
    )
    parser.add_argument(
        '--input-file',
        type=str,
        help='Path to slot history JSON file'
    )
    parser.add_argument(
        '--start-epoch',
        type=int,
        help='Start epoch for RPC fetch'
    )
    parser.add_argument(
        '--end-epoch',
        type=int,
        help='End epoch for RPC fetch'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/slot_jump_analysis.json',
        help='Output path for results JSON'
    )
    parser.add_argument(
        '--rpc-url',
        type=str,
        help='Solana RPC URL'
    )
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = SlotJumpDetector(rpc_url=args.rpc_url)
    
    # Load or fetch data
    if args.input_file:
        detector.load_slot_history(args.input_file)
    elif args.start_epoch and args.end_epoch:
        slot_data = detector.fetch_slot_history(args.start_epoch, args.end_epoch)
        detector.slot_data = slot_data
    else:
        print("Error: Must provide either --input-file or --start-epoch and --end-epoch")
        return 1
    
    # Run analysis
    detector.detect_slot_jumps()
    detector.profile_validators()
    
    # Generate and print report
    report = detector.generate_report()
    print(report)
    
    # Export results
    detector.export_results(args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
