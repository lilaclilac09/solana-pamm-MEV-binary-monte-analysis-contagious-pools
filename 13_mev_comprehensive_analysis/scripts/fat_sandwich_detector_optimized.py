"""
OPTIMIZED FAT SANDWICH vs MULTI-HOP DETECTOR
=============================================

Single unified module combining:
- Fat sandwich detection (rolling time windows)
- Attack classification (Fat Sandwich vs Multi-Hop Arbitrage)
- Comprehensive analysis

Removes duplications from:
- improved_fat_sandwich_detection.py
- 10_advanced_FP_solution notebooks
- FAT_SANDWICH_VS_MULTIHOP_CLASSIFICATION.md

Author: MEV Analysis Suite
Date: 2026-02-04
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class FatSandwichDetector:
    """Unified detector for Fat Sandwich and Multi-Hop Arbitrage patterns."""
    
    def __init__(self, df_trades, verbose=True):
        """
        Initialize detector with trade data.
        
        Parameters:
        -----------
        df_trades : DataFrame
            Trade events with columns: signer, ms_time, slot, amm_trade, 
                                       from_token, to_token, validator, etc.
        verbose : bool
            Print progress messages
        """
        self.df_trades = df_trades.sort_values('ms_time').reset_index(drop=True)
        self.verbose = verbose
        
        if verbose:
            print(f"✓ Loaded {len(df_trades):,} trade events")
            print(f"✓ Time range: {df_trades['ms_time'].min()} to {df_trades['ms_time'].max()}")
            print(f"✓ Unique signers: {df_trades['signer'].nunique():,}")
    
    def detect_fat_sandwiches(self, window_seconds=[1, 2, 5, 10], 
                               min_trades=5, max_victim_ratio=0.8, 
                               min_attacker_trades=2):
        """
        Detect fat sandwich patterns using rolling time windows.
        
        Parameters:
        -----------
        window_seconds : list
            Time window sizes in seconds
        min_trades : int
            Minimum trades per window
        max_victim_ratio : float
            Max victim/total ratio filter
        min_attacker_trades : int
            Min consecutive attacker trades
        
        Returns:
        --------
        results_df : DataFrame
            Detected fat sandwiches
        stats : dict
            Detection statistics
        """
        if self.verbose:
            print("\n" + "="*80)
            print("SCANNING FOR FAT SANDWICHES (Rolling Time Windows)")
            print("="*80)
        
        fat_sandwiches = []
        stats = {w: 0 for w in window_seconds}
        stats.update({
            'total_windows_checked': 0,
            'passed_aba_pattern': 0,
            'passed_victim_ratio': 0,
            'passed_token_pair': 0,
            'high_confidence': 0,
            'medium_confidence': 0
        })
        
        # Group by AMM pool
        amm_groups = list(self.df_trades.groupby('amm_trade')) if 'amm_trade' in self.df_trades.columns else [('All', self.df_trades)]
        
        for amm_name, amm_trades in amm_groups:
            amm_trades = amm_trades.sort_values('ms_time').reset_index(drop=True)
            
            # For each time window size
            for window_sec in window_seconds:
                window_ms = window_sec * 1000
                i = 0
                
                while i < len(amm_trades):
                    start_time = amm_trades.iloc[i]['ms_time']
                    end_time = start_time + window_ms
                    
                    # Get all trades in window
                    window_mask = (amm_trades['ms_time'] >= start_time) & (amm_trades['ms_time'] <= end_time)
                    window_trades = amm_trades[window_mask].copy()
                    
                    stats['total_windows_checked'] += 1
                    
                    if len(window_trades) < min_trades:
                        i += 1
                        continue
                    
                    # Check A-B-A pattern
                    signers = window_trades['signer'].tolist()
                    if signers[0] != signers[-1]:
                        i += 1
                        continue
                    
                    stats['passed_aba_pattern'] += 1
                    attacker = signers[0]
                    middle_signers = set(signers[1:-1])
                    attacker_count = signers.count(attacker)
                    
                    if attacker_count < min_attacker_trades or len(middle_signers) == 0 or attacker in middle_signers:
                        i += 1
                        continue
                    
                    # Check victim ratio (filter aggregator routing)
                    victim_ratio = len(middle_signers) / len(window_trades)
                    if victim_ratio > max_victim_ratio:
                        i += 1
                        continue
                    
                    stats['passed_victim_ratio'] += 1
                    
                    # Validate token pair reversal if available
                    token_pair_valid = True
                    if 'from_token' in window_trades.columns and 'to_token' in window_trades.columns:
                        attacker_trades = window_trades[window_trades['signer'] == attacker]
                        if len(attacker_trades) >= 2:
                            first_trade = attacker_trades.iloc[0]
                            last_trade = attacker_trades.iloc[-1]
                            first_pair = (first_trade['from_token'], first_trade['to_token'])
                            last_pair = (last_trade['from_token'], last_trade['to_token'])
                            if first_pair[0] != last_pair[1] or first_pair[1] != last_pair[0]:
                                token_pair_valid = False
                    
                    if not token_pair_valid:
                        i += 1
                        continue
                    
                    stats['passed_token_pair'] += 1
                    
                    # Confidence scoring
                    confidence_score = 0
                    confidence_reasons = []
                    
                    if victim_ratio < 0.3:
                        confidence_score += 3
                        confidence_reasons.append('low_victim_ratio')
                    elif victim_ratio < 0.5:
                        confidence_score += 2
                    
                    if attacker_count >= 3:
                        confidence_score += 2
                        confidence_reasons.append('multiple_attacker_trades')
                    
                    if token_pair_valid and 'from_token' in window_trades.columns:
                        confidence_score += 2
                        confidence_reasons.append('token_pair_reversal')
                    
                    if window_sec <= 2:
                        confidence_score += 1
                        confidence_reasons.append('short_window')
                    
                    if len(middle_signers) >= 3:
                        confidence_score += 1
                        confidence_reasons.append('multiple_victims')
                    
                    # Determine confidence level
                    if confidence_score >= 6:
                        confidence = 'high'
                        stats['high_confidence'] += 1
                    elif confidence_score >= 4:
                        confidence = 'medium'
                        stats['medium_confidence'] += 1
                    else:
                        confidence = 'low'
                    
                    stats[window_sec] += 1
                    
                    # Record detection
                    fat_sandwiches.append({
                        'amm_trade': amm_name,
                        'attacker_signer': attacker,
                        'victim_count': len(middle_signers),
                        'victim_signers': list(middle_signers),
                        'total_trades': len(window_trades),
                        'attacker_trades': attacker_count,
                        'victim_ratio': victim_ratio,
                        'window_seconds': window_sec,
                        'start_time_ms': start_time,
                        'end_time_ms': min(end_time, window_trades.iloc[-1]['ms_time']),
                        'actual_time_span_ms': window_trades.iloc[-1]['ms_time'] - window_trades.iloc[0]['ms_time'],
                        'start_slot': window_trades.iloc[0]['slot'] if 'slot' in window_trades.columns else None,
                        'end_slot': window_trades.iloc[-1]['slot'] if 'slot' in window_trades.columns else None,
                        'validator': window_trades.iloc[0]['validator'] if 'validator' in window_trades.columns else None,
                        'confidence': confidence,
                        'confidence_score': confidence_score,
                        'confidence_reasons': ','.join(confidence_reasons),
                        'token_pair_validated': token_pair_valid and 'from_token' in window_trades.columns
                    })
                    
                    i += max(1, attacker_count // 2)
        
        results_df = pd.DataFrame(fat_sandwiches)
        
        if self.verbose:
            self._print_detection_summary(results_df, stats, window_seconds)
        
        return results_df, stats
    
    def classify_attack(self, cluster_trades, attacker_signer, verbose=False):
        """
        Classify a single attack as Fat Sandwich or Multi-Hop Arbitrage.
        
        Returns:
        --------
        classification : dict with attack_type, confidence, scores, and reasoning
        """
        
        # Victim analysis
        cluster_sorted = cluster_trades.sort_values('ms_time').reset_index(drop=True)
        attacker_indices = cluster_sorted[cluster_sorted['signer'] == attacker_signer].index.tolist()
        
        if len(attacker_indices) < 2:
            return {'attack_type': 'unknown', 'confidence': 0.0}
        
        first_idx = attacker_indices[0]
        last_idx = attacker_indices[-1]
        middle_trades = cluster_sorted.iloc[first_idx + 1:last_idx]
        victim_signers = middle_trades['signer'].unique().tolist()
        victim_signers = [v for v in victim_signers if v != attacker_signer]
        has_victims = len(victim_signers) >= 2
        
        # Token structure
        signer_trades = cluster_sorted[cluster_sorted['signer'] == attacker_signer].sort_values('ms_time')
        if 'from_token' in signer_trades.columns and 'to_token' in signer_trades.columns:
            token_pairs = signer_trades[['from_token', 'to_token']].apply(
                lambda row: tuple(sorted([row['from_token'], row['to_token']])), axis=1
            ).nunique()
            same_pair = token_pairs == 1
        else:
            token_pairs = 1
            same_pair = True
        
        # Pool diversity
        unique_pools = signer_trades['amm_trade'].nunique() if 'amm_trade' in signer_trades.columns else 1
        
        # Cycle routing
        is_cycle = False
        cycle_confidence = 0.0
        if len(signer_trades) >= 2 and 'from_token' in signer_trades.columns:
            token_path = [signer_trades.iloc[0]['from_token']]
            for _, trade in signer_trades.iterrows():
                token_path.append(trade['to_token'])
            
            is_cycle = token_path[0] == token_path[-1] or token_path[-1] in ['SOL', 'USDC']
            if is_cycle:
                cycle_confidence = 0.5 + (0.2 if len(signer_trades) >= 3 else 0)
        
        # Score Fat Sandwich
        fs_score = 0.0
        if has_victims:
            fs_score += 0.35
        if same_pair:
            fs_score += 0.25
        if unique_pools <= 2:
            fs_score += 0.20
        
        # Score Multi-Hop
        mh_score = 0.0
        if is_cycle and cycle_confidence >= 0.5:
            mh_score += cycle_confidence * 0.35
        if token_pairs >= 3:
            mh_score += 0.25
        if unique_pools >= 3:
            mh_score += 0.20
        if not has_victims:
            mh_score += 0.20
        
        # Determine type
        if fs_score > mh_score + 0.15:
            attack_type = 'fat_sandwich'
            confidence = min(fs_score, 1.0)
        elif mh_score > fs_score + 0.15:
            attack_type = 'multi_hop_arbitrage'
            confidence = min(mh_score, 1.0)
        else:
            attack_type = 'ambiguous'
            confidence = max(fs_score, mh_score)
        
        return {
            'attack_type': attack_type,
            'confidence': confidence,
            'fat_sandwich_score': min(fs_score, 1.0),
            'multi_hop_score': min(mh_score, 1.0),
            'victim_count': len(victim_signers),
            'token_pairs': token_pairs,
            'unique_pools': unique_pools,
            'is_cycle': is_cycle
        }
    
    def classify_all_attacks(self, detected_attacks_df, show_progress=True):
        """Classify all detected attacks."""
        results = []
        total = len(detected_attacks_df)
        
        for i, (idx, attack_row) in enumerate(detected_attacks_df.iterrows()):
            if show_progress and i % max(1, total // 10) == 0:
                print(f"  Classifying: {i}/{total}")
            
            # Extract cluster
            cluster = self.df_trades[
                (self.df_trades['slot'] >= attack_row['start_slot']) &
                (self.df_trades['slot'] <= attack_row['end_slot']) &
                (self.df_trades['ms_time'] >= attack_row['start_time_ms']) &
                (self.df_trades['ms_time'] <= attack_row['end_time_ms'])
            ].copy()
            
            if len(cluster) == 0:
                continue
            
            # Classify
            classification = self.classify_attack(cluster, attack_row['attacker_signer'])
            
            # Add to row
            for key, value in classification.items():
                attack_row[key] = value
            
            results.append(attack_row)
        
        classified_df = pd.DataFrame(results)
        
        if show_progress and len(results) > 0:
            print(f"  Completed: {total}/{total}")
            print("\n📊 Classification Summary:")
            if 'attack_type' in classified_df.columns:
                counts = classified_df['attack_type'].value_counts()
                for atype, count in counts.items():
                    pct = count / len(classified_df) * 100
                    print(f"   {atype:25s}: {count:>5,} ({pct:>5.1f}%)")
        
        return classified_df
    
    def _print_detection_summary(self, results_df, stats, window_seconds):
        """Print detection summary."""
        print(f"✓ Total detections: {len(results_df):,}")
        print("\nBy Time Window:")
        for w in window_seconds:
            count = stats[w]
            pct = (count / len(results_df) * 100) if len(results_df) > 0 else 0
            print(f"  {w}s: {count:>6,} ({pct:>5.1f}%)")
        
        print("\nBy Confidence:")
        print(f"  High:   {stats['high_confidence']:>6,}")
        print(f"  Medium: {stats['medium_confidence']:>6,}")
        low_conf = len(results_df) - stats['high_confidence'] - stats['medium_confidence']
        print(f"  Low:    {low_conf:>6,}")
        
        print("\nValidation Pass Rates:")
        total_checked = stats['total_windows_checked']
        if total_checked > 0:
            print(f"  Windows checked: {total_checked:,}")
            print(f"  A-B-A pattern: {stats['passed_aba_pattern']:,} ({stats['passed_aba_pattern']/total_checked*100:.1f}%)")
            print(f"  Victim ratio: {stats['passed_victim_ratio']:,}")
            print(f"  Token pair: {stats['passed_token_pair']:,}")


def load_data(data_path=None):
    """Load clean data with fallback."""
    if data_path is None:
        data_path = Path('01_data_cleaning/outputs/pamm_clean_final.parquet')
    
    if not Path(data_path).exists():
        # Try relative from workspace
        alt_path = Path('/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis/01_data_cleaning/outputs/pamm_clean_final.parquet')
        if alt_path.exists():
            data_path = alt_path
        else:
            raise FileNotFoundError(f"Data file not found at {data_path}")
    
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    print(f"✓ Loaded {len(df):,} records")
    return df


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("FAT SANDWICH vs MULTI-HOP ARBITRAGE DETECTOR (OPTIMIZED)")
    print("="*80 + "\n")
    
    # Load data
    df_clean = load_data()
    
    # Filter to trades only
    df_trades = df_clean[df_clean['kind'] == 'TRADE'].copy()
    print(f"✓ Filtered to {len(df_trades):,} TRADE events\n")
    
    # Initialize detector
    detector = FatSandwichDetector(df_trades, verbose=True)
    
    # Run detection
    print("\n1️⃣  DETECTING FAT SANDWICHES...")
    detected_sandwiches, detection_stats = detector.detect_fat_sandwiches(
        window_seconds=[1, 2, 5, 10],
        min_trades=5,
        max_victim_ratio=0.8
    )
    
    if len(detected_sandwiches) == 0:
        print("❌ No fat sandwiches detected")
        return
    
    # Classify attacks
    print("\n2️⃣  CLASSIFYING ATTACKS...")
    classified_results = detector.classify_all_attacks(detected_sandwiches)
    
    # Summary statistics
    print("\n3️⃣  ANALYSIS SUMMARY")
    print("="*80)
    
    if len(classified_results) > 0:
        print(f"\nTop Attackers:")
        top_attackers = classified_results['attacker_signer'].value_counts().head(10)
        for i, (attacker, count) in enumerate(top_attackers.items(), 1):
            print(f"  {i:2d}. {attacker[:44]:44s}: {count:>4,} attacks")
        
        print(f"\nAttack Type Distribution:")
        attack_types = classified_results['attack_type'].value_counts()
        for atype, count in attack_types.items():
            pct = count / len(classified_results) * 100
            print(f"  {atype:25s}: {count:>5,} ({pct:>5.1f}%)")
        
        print(f"\nConfidence Levels:")
        avg_confidence = classified_results['confidence'].mean()
        print(f"  Average: {avg_confidence:.2%}")
        print(f"  High (≥0.8): {(classified_results['confidence'] >= 0.8).sum():,}")
        print(f"  Medium (0.5-0.8): {((classified_results['confidence'] >= 0.5) & (classified_results['confidence'] < 0.8)).sum():,}")
        print(f"  Low (<0.5): {(classified_results['confidence'] < 0.5).sum():,}")
        
        # Save results
        output_path = 'fat_sandwich_classification_results.parquet'
        classified_results.to_parquet(output_path)
        print(f"\n✓ Results saved to {output_path}")
        
        # Show sample results
        print(f"\n📋 Sample Results (first 5 attacks):")
        print("-"*80)
        cols = ['attacker_signer', 'attack_type', 'confidence', 'victim_count', 
                'unique_pools', 'window_seconds']
        for col in cols:
            if col not in classified_results.columns:
                cols.remove(col)
        
        for i, row in classified_results.head(5).iterrows():
            print(f"\nAttack #{i+1}:")
            print(f"  Attacker:      {row['attacker_signer'][:44]}")
            print(f"  Type:          {row['attack_type']}")
            print(f"  Confidence:    {row['confidence']:.1%}")
            print(f"  Victims:       {row.get('victim_count', 'N/A')}")
            print(f"  Token Pairs:   {row.get('token_pairs', 'N/A')}")
            print(f"  Pools:         {row.get('unique_pools', 'N/A')}")
            print(f"  Time Span:     {row['actual_time_span_ms']/1000:.2f}s")


if __name__ == "__main__":
    main()
