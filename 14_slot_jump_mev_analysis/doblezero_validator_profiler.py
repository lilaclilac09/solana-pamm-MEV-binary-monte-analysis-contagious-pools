#!/usr/bin/env python3
"""
DobleZero Validator Profiler
=============================

Identifies and profiles validators exhibiting DobleZero-style behavior:
intentional slot skipping strategies to optimize MEV extraction.

Author: MEV Analysis Team
Date: March 3, 2026
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict


@dataclass
class DobleZeroSignature:
    """Behavioral signature indicating DobleZero operation"""
    validator_pubkey: str
    confidence_score: float  # 0-1, how confident this is DobleZero
    skip_rate: float
    pattern_regularity: float  # How regular/predictable the skips are
    mev_correlation: float  # Correlation with MEV opportunities
    profitability_ratio: float  # MEV profit vs missed block rewards
    behavioral_flags: List[str]  # List of detected DobleZero indicators
    

@dataclass
class ValidatorEconomics:
    """Economic analysis of validator behavior"""
    validator_pubkey: str
    total_blocks_produced: int
    total_blocks_skipped: int
    estimated_block_rewards_usd: float
    estimated_mev_extracted_usd: float
    opportunity_cost_usd: float  # Missed block rewards from skips
    net_profit_usd: float
    is_profitable_strategy: bool


class DobleZeroProfiler:
    """
    Profiles validators to identify DobleZero behavior patterns
    """
    
    # Economic constants (approximate)
    BLOCK_REWARD_SOL = 0.01  # Approximate Solana block reward
    SOL_PRICE_USD = 100.0    # Placeholder SOL price
    
    # DobleZero detection thresholds
    MIN_SKIP_RATE = 0.03              # Min 3% skip rate
    MAX_PATTERN_ENTROPY = 0.4         # Max entropy for "intentional"
    MIN_MEV_CORRELATION = 0.5         # Min correlation with MEV
    MIN_PROFITABILITY_RATIO = 1.2     # Must profit 20%+ from strategy
    
    def __init__(self):
        self.validators = {}
        self.validator_mev = defaultdict(list)
        self.doblezero_candidates = []
        
    def load_validator_profiles(self, filepath: str) -> None:
        """Load validator skip profiles from slot jump analysis"""
        print(f"Loading validator profiles from {filepath}...")
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.validators = data.get('validator_profiles', {})
        print(f"Loaded {len(self.validators)} validator profiles")
        
    def load_mev_data(self, filepath: str) -> None:
        """Load MEV extraction data"""
        print(f"Loading MEV data from {filepath}...")
        with open(filepath, 'r') as f:
            mev_events = json.load(f)
        
        # Organize MEV by validator
        for event in mev_events:
            validator = event.get('block_leader', '')
            if validator:
                self.validator_mev[validator].append(event)
        
        print(f"Loaded MEV data for {len(self.validator_mev)} validators")
        
    def identify_doblezero_validators(self) -> List[DobleZeroSignature]:
        """
        Identify validators exhibiting DobleZero behavior
        
        Returns:
            List of DobleZeroSignature objects, sorted by confidence
        """
        print("Analyzing validators for DobleZero signatures...")
        candidates = []
        
        for validator_key, profile in self.validators.items():
            # Calculate DobleZero indicators
            signature = self._analyze_validator(validator_key, profile)
            
            # Filter by confidence threshold
            if signature.confidence_score > 0.5:
                candidates.append(signature)
        
        # Sort by confidence
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.doblezero_candidates = candidates
        print(f"Identified {len(candidates)} DobleZero candidates")
        
        return candidates
    
    def _analyze_validator(self, validator_key: str, profile: Dict) -> DobleZeroSignature:
        """
        Analyze individual validator for DobleZero behavior
        
        DobleZero indicators:
        1. High skip rate (but not too high - total failure)
        2. Low pattern entropy (intentional, not random)
        3. Correlation with MEV opportunities
        4. Economic profitability of the strategy
        5. Specific skip patterns (e.g., skip low-MEV slots)
        """
        skip_rate = profile.get('skip_rate', 0.0)
        entropy = profile.get('skip_pattern_entropy', 1.0)
        
        # Get MEV data for this validator
        validator_mev = self.validator_mev.get(validator_key, [])
        total_mev = sum(mev.get('profit_usd', 0) for mev in validator_mev)
        
        # Calculate MEV correlation
        mev_correlation = self._calculate_mev_correlation(
            profile,
            validator_mev
        )
        
        # Calculate economic profitability
        economics = self._calculate_economics(profile, total_mev)
        profitability_ratio = (
            economics.net_profit_usd / economics.estimated_block_rewards_usd
            if economics.estimated_block_rewards_usd > 0 else 0
        )
        
        # Detect behavioral flags
        flags = self._detect_behavioral_flags(
            profile,
            validator_mev,
            economics
        )
        
        # Calculate overall confidence score
        confidence = self._calculate_confidence_score(
            skip_rate,
            entropy,
            mev_correlation,
            profitability_ratio,
            flags
        )
        
        # Pattern regularity (inverse of entropy)
        pattern_regularity = 1.0 - entropy
        
        return DobleZeroSignature(
            validator_pubkey=validator_key,
            confidence_score=confidence,
            skip_rate=skip_rate,
            pattern_regularity=pattern_regularity,
            mev_correlation=mev_correlation,
            profitability_ratio=profitability_ratio,
            behavioral_flags=flags
        )
    
    def _calculate_mev_correlation(
        self,
        profile: Dict,
        mev_events: List[Dict]
    ) -> float:
        """
        Calculate correlation between skip behavior and MEV extraction
        
        High correlation suggests intentional skipping of low-MEV slots
        """
        if not mev_events:
            return 0.0
        
        # Simple heuristic: ratio of MEV events to produced blocks
        blocks_produced = profile.get('total_assigned_slots', 1) - profile.get('total_skipped_slots', 0)
        
        if blocks_produced == 0:
            return 0.0
        
        mev_per_block = len(mev_events) / blocks_produced
        
        # Normalize to 0-1 scale (assume max ~2 MEV events per block for normalization)
        correlation = min(mev_per_block / 2.0, 1.0)
        
        return correlation
    
    def _calculate_economics(
        self,
        profile: Dict,
        total_mev_usd: float
    ) -> ValidatorEconomics:
        """Calculate economic impact of validator strategy"""
        blocks_produced = profile.get('total_assigned_slots', 0) - profile.get('total_skipped_slots', 0)
        blocks_skipped = profile.get('total_skipped_slots', 0)
        
        # Estimated block rewards
        block_rewards = blocks_produced * self.BLOCK_REWARD_SOL * self.SOL_PRICE_USD
        
        # Opportunity cost (missed rewards from skipped blocks)
        opportunity_cost = blocks_skipped * self.BLOCK_REWARD_SOL * self.SOL_PRICE_USD
        
        # Net profit (MEV gained - opportunity cost)
        net_profit = total_mev_usd - opportunity_cost
        
        is_profitable = net_profit > 0
        
        return ValidatorEconomics(
            validator_pubkey=profile.get('validator_pubkey', ''),
            total_blocks_produced=blocks_produced,
            total_blocks_skipped=blocks_skipped,
            estimated_block_rewards_usd=block_rewards,
            estimated_mev_extracted_usd=total_mev_usd,
            opportunity_cost_usd=opportunity_cost,
            net_profit_usd=net_profit,
            is_profitable_strategy=is_profitable
        )
    
    def _detect_behavioral_flags(
        self,
        profile: Dict,
        mev_events: List[Dict],
        economics: ValidatorEconomics
    ) -> List[str]:
        """
        Detect specific behavioral flags indicating DobleZero operation
        
        Returns:
            List of detected flag names
        """
        flags = []
        
        # Flag 1: High skip rate
        if profile.get('skip_rate', 0) > self.MIN_SKIP_RATE:
            flags.append('HIGH_SKIP_RATE')
        
        # Flag 2: Regular skip pattern
        if profile.get('skip_pattern_entropy', 1.0) < self.MAX_PATTERN_ENTROPY:
            flags.append('REGULAR_PATTERN')
        
        # Flag 3: Consecutive skips
        if profile.get('consecutive_skip_events', 0) > 10:
            flags.append('FREQUENT_CONSECUTIVE_SKIPS')
        
        # Flag 4: Long skip bursts
        if profile.get('max_consecutive_skips', 0) > 5:
            flags.append('LONG_SKIP_BURSTS')
        
        # Flag 5: Economic profitability
        if economics.is_profitable_strategy:
            flags.append('PROFITABLE_STRATEGY')
        
        # Flag 6: High MEV extraction
        if economics.estimated_mev_extracted_usd > economics.estimated_block_rewards_usd:
            flags.append('MEV_EXCEEDS_BLOCK_REWARDS')
        
        # Flag 7: MEV concentration
        if len(mev_events) > 0:
            avg_mev = economics.estimated_mev_extracted_usd / len(mev_events)
            if avg_mev > 100:  # High average MEV per event
                flags.append('HIGH_VALUE_MEV_FOCUS')
        
        return flags
    
    def _calculate_confidence_score(
        self,
        skip_rate: float,
        entropy: float,
        mev_correlation: float,
        profitability: float,
        flags: List[str]
    ) -> float:
        """
        Calculate overall confidence that this is DobleZero behavior
        
        Weighted combination of multiple factors
        """
        # Component scores (0-1 each)
        skip_score = min(skip_rate / 0.15, 1.0)  # Normalize to 15% skip rate max
        pattern_score = 1.0 - entropy  # Low entropy = high score
        mev_score = mev_correlation
        profit_score = min(profitability / 2.0, 1.0)  # Normalize to 2x profitability
        
        # Behavioral flags score
        flag_score = len(flags) / 7.0  # Max 7 flags
        
        # Weighted average
        weights = {
            'skip': 0.15,
            'pattern': 0.25,
            'mev': 0.25,
            'profit': 0.20,
            'flags': 0.15
        }
        
        confidence = (
            weights['skip'] * skip_score +
            weights['pattern'] * pattern_score +
            weights['mev'] * mev_score +
            weights['profit'] * profit_score +
            weights['flags'] * flag_score
        )
        
        return confidence
    
    def export_results(self, output_path: str) -> None:
        """Export DobleZero profiling results"""
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_validators_analyzed': len(self.validators),
            'doblezero_candidates_found': len(self.doblezero_candidates),
            'candidates': [asdict(c) for c in self.doblezero_candidates],
            'summary_statistics': self._generate_summary()
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {output_path}")
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if not self.doblezero_candidates:
            return {}
        
        confidences = [c.confidence_score for c in self.doblezero_candidates]
        skip_rates = [c.skip_rate for c in self.doblezero_candidates]
        
        # Count common flags
        all_flags = []
        for candidate in self.doblezero_candidates:
            all_flags.extend(candidate.behavioral_flags)
        
        flag_counts = defaultdict(int)
        for flag in all_flags:
            flag_counts[flag] += 1
        
        return {
            'high_confidence_count': sum(1 for c in confidences if c > 0.8),
            'medium_confidence_count': sum(1 for c in confidences if 0.5 < c <= 0.8),
            'avg_confidence_score': np.mean(confidences),
            'avg_skip_rate': np.mean(skip_rates),
            'most_common_flags': dict(sorted(
                flag_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        }
    
    def generate_report(self) -> str:
        """Generate human-readable profiling report"""
        summary = self._generate_summary()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║         DOBLEZERO VALIDATOR PROFILING REPORT                 ║
╚══════════════════════════════════════════════════════════════╝

Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DETECTION SUMMARY
─────────────────────────────────────────────────────────────
Total Validators:       {len(self.validators):,}
DobleZero Candidates:   {len(self.doblezero_candidates):,}
  • High Confidence:    {summary.get('high_confidence_count', 0):,}
  • Medium Confidence:  {summary.get('medium_confidence_count', 0):,}

Average Skip Rate:      {summary.get('avg_skip_rate', 0)*100:.2f}%
Average Confidence:     {summary.get('avg_confidence_score', 0):.3f}

TOP BEHAVIORAL FLAGS
─────────────────────────────────────────────────────────────
"""
        
        for flag, count in summary.get('most_common_flags', {}).items():
            report += f"{flag:30s} {count:4d}\n"
        
        report += f"""
TOP 10 DOBLEZERO CANDIDATES
─────────────────────────────────────────────────────────────
"""
        
        for i, candidate in enumerate(self.doblezero_candidates[:10], 1):
            report += f"\n{i}. {candidate.validator_pubkey[:32]}..."
            report += f"\n   Confidence:      {candidate.confidence_score:.3f}"
            report += f"\n   Skip Rate:       {candidate.skip_rate*100:.2f}%"
            report += f"\n   Pattern Regular: {candidate.pattern_regularity:.3f}"
            report += f"\n   MEV Correlation: {candidate.mev_correlation:.3f}"
            report += f"\n   Profitability:   {candidate.profitability_ratio:.2f}x"
            report += f"\n   Flags:           {', '.join(candidate.behavioral_flags[:3])}"
            report += "\n"
        
        report += "\n" + "═" * 62 + "\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Profile validators for DobleZero behavior'
    )
    parser.add_argument(
        '--validator-profiles',
        type=str,
        required=True,
        help='Path to validator profiles JSON from slot_jump_detector'
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
        default='data/doblezero_profiles.json',
        help='Output path for results'
    )
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.5,
        help='Minimum confidence score for DobleZero classification'
    )
    
    args = parser.parse_args()
    
    # Initialize profiler
    profiler = DobleZeroProfiler()
    
    # Load data
    profiler.load_validator_profiles(args.validator_profiles)
    profiler.load_mev_data(args.mev_data)
    
    # Run analysis
    profiler.identify_doblezero_validators()
    
    # Generate report
    report = profiler.generate_report()
    print(report)
    
    # Export results
    profiler.export_results(args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
