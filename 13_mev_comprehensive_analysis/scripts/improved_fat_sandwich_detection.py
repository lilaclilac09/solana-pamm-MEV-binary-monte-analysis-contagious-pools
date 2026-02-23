"""
Improved Fat Sandwich Detection with Rolling Time Windows

This module implements accurate fat sandwich detection using:
1. True rolling time windows (1s, 2s, 5s, 10s)
2. Multiple verification mechanisms
3. Precise millisecond-based timing

Author: Optimized MEV Detection System
Date: 2026-02-04
"""

import pandas as pd
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


def detect_fat_sandwich_time_window(
    trades_df,
    window_seconds=[1, 2, 5, 10],
    min_trades=5,
    max_victim_ratio=0.8,
    min_attacker_trades=2,
    verbose=True
):
    """
    Detect fat sandwich patterns using true rolling time windows.
    
    Parameters:
    -----------
    trades_df : DataFrame
        All TRADE events with columns: ['signer', 'ms_time', 'slot', 'validator', 
                                        'amm_trade', 'from_token', 'to_token']
    window_seconds : list
        Time window sizes in seconds (default: [1, 2, 5, 10])
    min_trades : int
        Minimum number of trades in window to consider (default: 5)
    max_victim_ratio : float
        Maximum victim/total ratio to avoid aggregator routing (default: 0.8)
    min_attacker_trades : int
        Minimum attacker trades (front + back) (default: 2)
    verbose : bool
        Print progress messages
    
    Returns:
    --------
    results_df : DataFrame
        Detected fat sandwich patterns with confidence scores
    stats : dict
        Detection statistics
    """
    
    if verbose:
        print("=" * 80)
        print("IMPROVED FAT SANDWICH DETECTION: Rolling Time Windows")
        print("=" * 80)
        print(f"Dataset: {len(trades_df):,} TRADE events")
        print(f"Time windows: {window_seconds} seconds")
        print(f"Min trades per window: {min_trades}")
        print(f"Max victim ratio: {max_victim_ratio * 100:.0f}%")
        print()
    
    # Ensure data is sorted by time
    trades_df = trades_df.sort_values('ms_time').reset_index(drop=True)
    
    fat_sandwiches = []
    detection_stats = {window: 0 for window in window_seconds}
    detection_stats['total_windows_checked'] = 0
    detection_stats['passed_aba_pattern'] = 0
    detection_stats['passed_victim_ratio'] = 0
    detection_stats['passed_token_pair'] = 0
    detection_stats['high_confidence'] = 0
    detection_stats['medium_confidence'] = 0
    
    # Group by PropAMM (sandwiches happen within same pool)
    amm_groups = trades_df.groupby('amm_trade') if 'amm_trade' in trades_df.columns else [('All', trades_df)]
    
    for amm_name, amm_trades in amm_groups:
        if verbose and len(amm_groups) > 1:
            print(f"Processing {amm_name}: {len(amm_trades):,} trades...")
        
        amm_trades = amm_trades.sort_values('ms_time').reset_index(drop=True)
        
        # Iterate through each time window size
        for window_sec in window_seconds:
            window_ms = window_sec * 1000
            
            # Sliding window detection
            i = 0
            while i < len(amm_trades):
                start_time = amm_trades.loc[i, 'ms_time']
                end_time = start_time + window_ms
                
                # Get all trades in this window
                window_mask = (amm_trades['ms_time'] >= start_time) & (amm_trades['ms_time'] <= end_time)
                window_trades = amm_trades[window_mask]
                
                detection_stats['total_windows_checked'] += 1
                
                # Check minimum trade count
                if len(window_trades) < min_trades:
                    i += 1
                    continue
                
                # Extract signers
                signers = window_trades['signer'].tolist()
                first_signer = signers[0]
                last_signer = signers[-1]
                
                # ============================================================
                # VALIDATION 1: A-B-A Pattern Check
                # ============================================================
                if first_signer != last_signer:
                    i += 1
                    continue
                
                detection_stats['passed_aba_pattern'] += 1
                attacker = first_signer
                
                # Extract middle signers (potential victims)
                middle_signers = signers[1:-1]
                unique_middle = set(middle_signers)
                
                # Must have at least 1 victim
                if len(unique_middle) == 0:
                    i += 1
                    continue
                
                # Victim cannot be the attacker (avoid wash trading)
                if attacker in unique_middle:
                    i += 1
                    continue
                
                # Count attacker's trades in window
                attacker_count = signers.count(attacker)
                if attacker_count < min_attacker_trades:
                    i += 1
                    continue
                
                # ============================================================
                # VALIDATION 2: Victim Ratio Check (Aggregator Filter)
                # ============================================================
                victim_ratio = len(unique_middle) / len(window_trades)
                if victim_ratio > max_victim_ratio:
                    # Likely aggregator routing, not MEV
                    i += 1
                    continue
                
                detection_stats['passed_victim_ratio'] += 1
                
                # ============================================================
                # VALIDATION 3: Token Pair Consistency (If Available)
                # ============================================================
                token_pair_valid = True
                if 'from_token' in window_trades.columns and 'to_token' in window_trades.columns:
                    attacker_trades = window_trades[window_trades['signer'] == attacker]
                    
                    if len(attacker_trades) >= 2:
                        # Check first and last attacker trades
                        first_trade = attacker_trades.iloc[0]
                        last_trade = attacker_trades.iloc[-1]
                        
                        first_pair = (first_trade['from_token'], first_trade['to_token'])
                        last_pair = (last_trade['from_token'], last_trade['to_token'])
                        
                        # Sandwich should have reversed token pair: (A,B) → (B,A)
                        if first_pair[0] != last_pair[1] or first_pair[1] != last_pair[0]:
                            token_pair_valid = False
                
                if not token_pair_valid:
                    i += 1
                    continue
                
                detection_stats['passed_token_pair'] += 1
                
                # ============================================================
                # CONFIDENCE SCORING
                # ============================================================
                confidence_score = 0
                confidence_reasons = []
                
                # Factor 1: Low victim ratio (more concentrated attack)
                if victim_ratio < 0.3:
                    confidence_score += 3
                    confidence_reasons.append('low_victim_ratio')
                elif victim_ratio < 0.5:
                    confidence_score += 2
                
                # Factor 2: Multiple attacker trades
                if attacker_count >= 3:
                    confidence_score += 2
                    confidence_reasons.append('multiple_attacker_trades')
                
                # Factor 3: Token pair reversal validated
                if token_pair_valid and 'from_token' in window_trades.columns:
                    confidence_score += 2
                    confidence_reasons.append('token_pair_reversal')
                
                # Factor 4: Short time window (more aggressive)
                if window_sec <= 2:
                    confidence_score += 1
                    confidence_reasons.append('short_window')
                
                # Factor 5: Multiple victims
                if len(unique_middle) >= 3:
                    confidence_score += 1
                    confidence_reasons.append('multiple_victims')
                
                # Determine final confidence
                if confidence_score >= 6:
                    confidence = 'high'
                    detection_stats['high_confidence'] += 1
                elif confidence_score >= 4:
                    confidence = 'medium'
                    detection_stats['medium_confidence'] += 1
                else:
                    confidence = 'low'
                
                # ============================================================
                # RECORD DETECTION
                # ============================================================
                detection_stats[window_sec] += 1
                
                fat_sandwiches.append({
                    'amm_trade': amm_name,
                    'attacker_signer': attacker,
                    'victim_count': len(unique_middle),
                    'victim_signers': list(unique_middle),
                    'total_trades': len(window_trades),
                    'attacker_trades': attacker_count,
                    'victim_ratio': victim_ratio,
                    'window_seconds': window_sec,
                    'window_ms': window_ms,
                    'start_slot': window_trades.iloc[0]['slot'] if 'slot' in window_trades.columns else None,
                    'end_slot': window_trades.iloc[-1]['slot'] if 'slot' in window_trades.columns else None,
                    'slot_span': window_trades.iloc[-1]['slot'] - window_trades.iloc[0]['slot'] if 'slot' in window_trades.columns else None,
                    'start_time_ms': start_time,
                    'end_time_ms': min(end_time, window_trades.iloc[-1]['ms_time']),
                    'actual_time_span_ms': window_trades.iloc[-1]['ms_time'] - window_trades.iloc[0]['ms_time'],
                    'validator': window_trades.iloc[0]['validator'] if 'validator' in window_trades.columns else None,
                    'confidence': confidence,
                    'confidence_score': confidence_score,
                    'confidence_reasons': ','.join(confidence_reasons),
                    'token_pair_validated': token_pair_valid and 'from_token' in window_trades.columns
                })
                
                # Move to next potential window
                # Skip ahead to avoid counting the same pattern multiple times
                i += max(1, attacker_count // 2)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(fat_sandwiches)
    
    if verbose:
        print()
        print("=" * 80)
        print("DETECTION RESULTS")
        print("=" * 80)
        print(f"Total fat sandwiches detected: {len(results_df):,}")
        print()
        print("By Time Window:")
        for window in window_seconds:
            count = detection_stats[window]
            pct = (count / len(results_df) * 100) if len(results_df) > 0 else 0
            print(f"  {window}s window: {count:>6,} ({pct:>5.1f}%)")
        print()
        print("By Confidence:")
        print(f"  High:   {detection_stats['high_confidence']:>6,} ({detection_stats['high_confidence']/len(results_df)*100:.1f}%)" if len(results_df) > 0 else "  High: 0")
        print(f"  Medium: {detection_stats['medium_confidence']:>6,} ({detection_stats['medium_confidence']/len(results_df)*100:.1f}%)" if len(results_df) > 0 else "  Medium: 0")
        print(f"  Low:    {len(results_df) - detection_stats['high_confidence'] - detection_stats['medium_confidence']:>6,}")
        print()
        print("Validation Pass Rates:")
        print(f"  Windows checked: {detection_stats['total_windows_checked']:,}")
        print(f"  Passed A-B-A pattern: {detection_stats['passed_aba_pattern']:,} ({detection_stats['passed_aba_pattern']/detection_stats['total_windows_checked']*100:.2f}%)" if detection_stats['total_windows_checked'] > 0 else "  Passed A-B-A: 0")
        print(f"  Passed victim ratio: {detection_stats['passed_victim_ratio']:,}")
        print(f"  Passed token pair: {detection_stats['passed_token_pair']:,}")
        print()
    
    return results_df, detection_stats


def detect_cycle_routing(cluster_trades, signer):
    """
    Detect if a signer executes a cycle routing pattern (Multi-Hop Arbitrage).
    
    A cycle is detected when:
    - Signer's to_token in trade N equals from_token in trade N+1
    - Eventually returns to starting token (SOL, USDC, or other base asset)
    - No intermediate victims needed
    
    Parameters:
    -----------
    cluster_trades : DataFrame
        All trades in a specific cluster/window
    signer : str
        Signer address to check
    
    Returns:
    --------
    cycle_info : dict
        {
            'is_cycle': bool,
            'cycle_path': list,
            'cycle_length': int,
            'starting_token': str,
            'ending_token': str,
            'net_balance_change': dict,
            'confidence': float
        }
    """
    signer_trades = cluster_trades[cluster_trades['signer'] == signer].sort_values('ms_time')
    
    if len(signer_trades) < 2 or 'from_token' not in signer_trades.columns:
        return {
            'is_cycle': False,
            'cycle_path': [],
            'cycle_length': 0,
            'starting_token': None,
            'ending_token': None,
            'net_balance_change': {},
            'confidence': 0.0
        }
    
    # Build token path
    token_path = []
    trade_list = signer_trades[['from_token', 'to_token']].values.tolist()
    
    if len(trade_list) == 0:
        return {
            'is_cycle': False,
            'cycle_path': [],
            'cycle_length': 0,
            'starting_token': None,
            'ending_token': None,
            'net_balance_change': {},
            'confidence': 0.0
        }
    
    # First token is the starting asset
    starting_token = trade_list[0][0]
    token_path.append(starting_token)
    
    # Build path: from_token → to_token → to_token of next → etc.
    for from_tok, to_tok in trade_list:
        token_path.append(to_tok)
    
    ending_token = token_path[-1]
    
    # Check if it's a cycle (returns to starting token or common base assets)
    is_cycle = ending_token == starting_token or ending_token in ['SOL', 'USDC']
    
    # Calculate net balance change for all tokens
    net_balance = {}
    for from_tok, to_tok in trade_list:
        net_balance[from_tok] = net_balance.get(from_tok, 0) - 1
        net_balance[to_tok] = net_balance.get(to_tok, 0) + 1
    
    # Remove tokens that net to zero (they're intermediate routers)
    net_balance_nonzero = {k: v for k, v in net_balance.items() if v != 0}
    
    # Confidence scoring for cycle detection
    confidence = 0.0
    if is_cycle:
        confidence += 0.3  # Base score for path returning to start
    if len(trade_list) >= 3:
        confidence += 0.2  # Multiple hops suggests deliberate routing
    if len(net_balance_nonzero) <= 1:
        confidence += 0.2  # Nearly zero net balance (true arbitrage)
    if len(set(token_path[:-1])) >= len(trade_list):
        confidence += 0.2  # All intermediate tokens are different (no repeated pairs)
    
    return {
        'is_cycle': is_cycle,
        'cycle_path': token_path,
        'cycle_length': len(trade_list),
        'starting_token': starting_token,
        'ending_token': ending_token,
        'net_balance_change': net_balance,
        'confidence': min(confidence, 1.0)
    }


def identify_token_structure(cluster_trades, signer):
    """
    Identify if a signer uses same token pair throughout (Fat Sandwich)
    or different pairs in a cycle (Multi-Hop Arbitrage).
    
    Parameters:
    -----------
    cluster_trades : DataFrame
        All trades in a cluster
    signer : str
        Signer address to analyze
    
    Returns:
    --------
    structure_info : dict
        {
            'unique_token_pairs': int,
            'token_pairs': list,
            'is_same_pair_throughout': bool,
            'pair_consistency': float,
            'pattern_type': str  # 'same_pair' or 'multi_hop'
        }
    """
    signer_trades = cluster_trades[cluster_trades['signer'] == signer].sort_values('ms_time')
    
    if len(signer_trades) < 2 or 'from_token' not in signer_trades.columns:
        return {
            'unique_token_pairs': 0,
            'token_pairs': [],
            'is_same_pair_throughout': False,
            'pair_consistency': 0.0,
            'pattern_type': 'unknown'
        }
    
    # Get all token pairs
    token_pairs = signer_trades[['from_token', 'to_token']].apply(
        lambda row: tuple(sorted([row['from_token'], row['to_token']])), axis=1
    ).unique().tolist()
    
    # Check consistency
    pair_consistency = 1.0 / len(token_pairs) if len(token_pairs) > 0 else 0.0
    is_same_pair = len(token_pairs) == 1
    
    pattern_type = 'same_pair' if is_same_pair else 'multi_hop'
    
    return {
        'unique_token_pairs': len(token_pairs),
        'token_pairs': token_pairs,
        'is_same_pair_throughout': is_same_pair,
        'pair_consistency': pair_consistency,
        'pattern_type': pattern_type
    }


def analyze_pool_diversity(cluster_trades, signer):
    """
    Analyze pool diversity for a signer's trades.
    
    Similar pools = same AMM protocol handling same token pair
    Diverse pools = different protocols or different token pairs
    
    Parameters:
    -----------
    cluster_trades : DataFrame
        All trades in cluster
    signer : str
        Signer address
    
    Returns:
    --------
    pool_info : dict
        {
            'unique_pools': int,
            'pools': list,
            'avg_pools_per_pair': float,
            'pool_diversity_score': float,
            'likely_attack_type': str
        }
    """
    signer_trades = cluster_trades[cluster_trades['signer'] == signer].sort_values('ms_time')
    
    if len(signer_trades) == 0:
        return {
            'unique_pools': 0,
            'pools': [],
            'avg_pools_per_pair': 0.0,
            'pool_diversity_score': 0.0,
            'likely_attack_type': 'unknown'
        }
    
    if 'amm_trade' not in signer_trades.columns:
        # If no pool info, use proxy: count unique transaction indices
        unique_pools = len(signer_trades)
    else:
        unique_pools = signer_trades['amm_trade'].nunique()
    
    pools = signer_trades['amm_trade'].unique().tolist() if 'amm_trade' in signer_trades.columns else []
    
    # Get token pair count
    if 'from_token' in signer_trades.columns:
        token_pairs = signer_trades[['from_token', 'to_token']].apply(
            lambda row: tuple(sorted([row['from_token'], row['to_token']])), axis=1
        ).nunique()
    else:
        token_pairs = 1
    
    avg_pools_per_pair = unique_pools / token_pairs if token_pairs > 0 else unique_pools
    
    # Pool diversity scoring
    if unique_pools >= 3 and token_pairs >= 3:
        pool_diversity_score = 1.0
        likely_attack_type = 'multi_hop_arbitrage'
    elif unique_pools >= 3 and token_pairs == 1:
        pool_diversity_score = 0.6
        likely_attack_type = 'fat_sandwich'
    elif unique_pools <= 2:
        pool_diversity_score = 0.2
        likely_attack_type = 'fat_sandwich'
    else:
        pool_diversity_score = 0.5
        likely_attack_type = 'ambiguous'
    
    return {
        'unique_pools': unique_pools,
        'pools': pools,
        'avg_pools_per_pair': avg_pools_per_pair,
        'pool_diversity_score': pool_diversity_score,
        'likely_attack_type': likely_attack_type
    }


def detect_victims_in_cluster(cluster_trades, attacker_signer):
    """
    Detect wrapped victims between attacker's front-run and back-run.
    
    Parameters:
    -----------
    cluster_trades : DataFrame
        All trades in a time window
    attacker_signer : str
        Suspected attacker address
    
    Returns:
    --------
    victim_info : dict
        {
            'victim_count': int,
            'victim_signers': list,
            'victim_ratio': float,
            'has_mandatory_victims': bool,  # At least 2 for Fat Sandwich
            'suspected_victims': list of indices
        }
    """
    cluster_sorted = cluster_trades.sort_values('ms_time').reset_index(drop=True)
    attacker_indices = cluster_sorted[cluster_sorted['signer'] == attacker_signer].index.tolist()
    
    if len(attacker_indices) < 2:
        return {
            'victim_count': 0,
            'victim_signers': [],
            'victim_ratio': 0.0,
            'has_mandatory_victims': False,
            'suspected_victims': []
        }
    
    # Find trades between first and last attacker trade
    first_attack_idx = attacker_indices[0]
    last_attack_idx = attacker_indices[-1]
    
    middle_trades = cluster_sorted.iloc[first_attack_idx + 1 : last_attack_idx]
    
    victim_signers = middle_trades['signer'].unique().tolist()
    # Remove attacker from victim list if present
    victim_signers = [v for v in victim_signers if v != attacker_signer]
    
    victim_ratio = len(middle_trades) / len(cluster_sorted) if len(cluster_sorted) > 0 else 0
    has_mandatory_victims = len(victim_signers) >= 2
    
    return {
        'victim_count': len(victim_signers),
        'victim_signers': victim_signers,
        'victim_ratio': victim_ratio,
        'has_mandatory_victims': has_mandatory_victims,
        'suspected_victims': middle_trades.index.tolist()
    }


def classify_mev_attack(
    cluster_trades,
    attacker_signer,
    oracle_burst_in_slot=None,
    verbose=False
):
    """
    Classify an MEV attack as either Fat Sandwich (B91) or Multi-Hop Arbitrage (Cycle Trading).
    
    Scoring system:
    ---------------
    Fat Sandwich indicators:
    - Mandatory wrapped victims (weight: 0.35)
    - Same token pair throughout (weight: 0.25)
    - Low pool diversity (weight: 0.20)
    - Oracle burst correlation (weight: 0.20)
    
    Multi-Hop Arbitrage indicators:
    - Cycle routing pattern (weight: 0.35)
    - Multiple different token pairs (weight: 0.25)
    - High pool diversity (weight: 0.20)
    - Pool imbalance trigger (weight: 0.20)
    
    Parameters:
    -----------
    cluster_trades : DataFrame
        All trades in a cluster/window
    attacker_signer : str
        Address of suspected attacker
    oracle_burst_in_slot : bool, optional
        Whether an oracle burst occurred in this slot
    verbose : bool
        Print classification details
    
    Returns:
    --------
    classification : dict
        {
            'attack_type': 'fat_sandwich' | 'multi_hop_arbitrage' | 'ambiguous',
            'confidence': float (0-1),
            'fat_sandwich_score': float (0-1),
            'multi_hop_score': float (0-1),
            'reasoning': dict with component scores,
            'recommendations': list of indicators considered
        }
    """
    
    # Collect all indicators
    victim_info = detect_victims_in_cluster(cluster_trades, attacker_signer)
    token_structure = identify_token_structure(cluster_trades, attacker_signer)
    pool_info = analyze_pool_diversity(cluster_trades, attacker_signer)
    cycle_info = detect_cycle_routing(cluster_trades, attacker_signer)
    
    # Fat Sandwich scoring
    fs_score = 0.0
    fs_reasons = {}
    
    # 1. Mandatory victims (0.35 weight)
    if victim_info['has_mandatory_victims']:
        fs_score += 0.35
        fs_reasons['wrapped_victims'] = 1.0
    else:
        fs_reasons['wrapped_victims'] = 0.0
    
    # 2. Same token pair throughout (0.25 weight)
    if token_structure['is_same_pair_throughout']:
        fs_score += 0.25
        fs_reasons['same_token_pair'] = 1.0
    else:
        fs_reasons['same_token_pair'] = 0.0
    
    # 3. Low pool diversity (0.20 weight)
    if pool_info['unique_pools'] <= 2:
        fs_score += 0.20
        fs_reasons['low_pool_diversity'] = 1.0
    elif pool_info['unique_pools'] <= 3:
        fs_score += 0.10
        fs_reasons['low_pool_diversity'] = 0.5
    else:
        fs_reasons['low_pool_diversity'] = 0.0
    
    # 4. Oracle burst correlation (0.20 weight)
    if oracle_burst_in_slot:
        fs_score += 0.20
        fs_reasons['oracle_burst_trigger'] = 1.0
    else:
        fs_reasons['oracle_burst_trigger'] = 0.0
    
    # Multi-Hop Arbitrage scoring
    mh_score = 0.0
    mh_reasons = {}
    
    # 1. Cycle routing pattern (0.35 weight)
    if cycle_info['is_cycle'] and cycle_info['confidence'] >= 0.5:
        mh_score += cycle_info['confidence'] * 0.35
        mh_reasons['cycle_routing'] = cycle_info['confidence']
    else:
        mh_reasons['cycle_routing'] = 0.0
    
    # 2. Multiple different token pairs (0.25 weight)
    if token_structure['unique_token_pairs'] >= 3:
        mh_score += 0.25
        mh_reasons['multiple_token_pairs'] = 1.0
    elif token_structure['unique_token_pairs'] >= 2:
        mh_score += 0.12
        mh_reasons['multiple_token_pairs'] = 0.5
    else:
        mh_reasons['multiple_token_pairs'] = 0.0
    
    # 3. High pool diversity (0.20 weight)
    if pool_info['unique_pools'] >= 3:
        mh_score += 0.20
        mh_reasons['high_pool_diversity'] = 1.0
    elif pool_info['unique_pools'] >= 2:
        mh_score += 0.10
        mh_reasons['high_pool_diversity'] = 0.5
    else:
        mh_reasons['high_pool_diversity'] = 0.0
    
    # 4. No mandatory victims (0.20 weight)
    if not victim_info['has_mandatory_victims']:
        mh_score += 0.20
        mh_reasons['no_wrapped_victims'] = 1.0
    else:
        mh_reasons['no_wrapped_victims'] = 0.0
    
    # Determine attack type and confidence
    score_diff = abs(fs_score - mh_score)
    total_score = fs_score + mh_score
    
    if fs_score > mh_score + 0.15:
        attack_type = 'fat_sandwich'
        confidence = min(fs_score, 1.0)
    elif mh_score > fs_score + 0.15:
        attack_type = 'multi_hop_arbitrage'
        confidence = min(mh_score, 1.0)
    else:
        attack_type = 'ambiguous'
        confidence = 1.0 - (score_diff / max(total_score, 1.0))
    
    classification = {
        'attack_type': attack_type,
        'confidence': confidence,
        'fat_sandwich_score': min(fs_score, 1.0),
        'multi_hop_score': min(mh_score, 1.0),
        'reasoning': {
            'fat_sandwich_indicators': fs_reasons,
            'multi_hop_indicators': mh_reasons,
            'victim_info': {
                'count': victim_info['victim_count'],
                'has_wrapped_victims': victim_info['has_mandatory_victims'],
                'ratio': victim_info['victim_ratio']
            },
            'token_structure': {
                'unique_pairs': token_structure['unique_token_pairs'],
                'is_same_pair': token_structure['is_same_pair_throughout']
            },
            'pool_analysis': {
                'unique_pools': pool_info['unique_pools'],
                'diversity_score': pool_info['pool_diversity_score']
            },
            'cycle_routing': {
                'is_cycle': cycle_info['is_cycle'],
                'cycle_confidence': cycle_info['confidence'],
                'path': cycle_info['cycle_path']
            }
        },
        'recommendations': []
    }
    
    # Add recommendations
    if attack_type == 'fat_sandwich':
        classification['recommendations'] = [
            f"Wrapped victims detected: {victim_info['victim_count']}",
            f"Operates on same token pair: {token_structure['is_same_pair_throughout']}",
            f"Uses {pool_info['unique_pools']} pools targeting same pair",
            "Extract value from victim slippage"
        ]
    elif attack_type == 'multi_hop_arbitrage':
        classification['recommendations'] = [
            f"No wrapped victims (arbitrage only)",
            f"Complex cycle routing with {token_structure['unique_token_pairs']} token pairs",
            f"Routes through {pool_info['unique_pools']} diverse pools",
            "Exploits pool imbalances rather than victim slippage"
        ]
    else:
        classification['recommendations'] = [
            "Pattern characteristics are mixed",
            "Requires manual review of specific trades",
            f"Fat Sandwich score: {fs_score:.2f}",
            f"Multi-Hop Arbitrage score: {mh_score:.2f}"
        ]
    
    if verbose:
        print("=" * 80)
        print(f"ATTACK CLASSIFICATION: {attack_type.upper()}")
        print(f"Confidence: {confidence:.2%}")
        print("=" * 80)
        print()
        print("Component Scores:")
        print(f"  Fat Sandwich Score:      {fs_score:.3f}")
        print(f"  Multi-Hop Arb Score:     {mh_score:.3f}")
        print()
        print("Fat Sandwich Indicators:")
        for indicator, score in fs_reasons.items():
            print(f"  {indicator:30s}: {score:.2f}")
        print()
        print("Multi-Hop Indicators:")
        for indicator, score in mh_reasons.items():
            print(f"  {indicator:30s}: {score:.2f}")
        print()
        print("Detailed Reasoning:")
        for key, value in classification['reasoning'].items():
            print(f"  {key}: {value}")
        print()
        print("Recommendations:")
        for i, rec in enumerate(classification['recommendations'], 1):
            print(f"  {i}. {rec}")
        print()
    
    return classification


def analyze_fat_sandwich_results(results_df, verbose=True):
    """
    Analyze detected fat sandwich patterns.
    
    Parameters:
    -----------
    results_df : DataFrame
        Results from detect_fat_sandwich_time_window()
    verbose : bool
        Print analysis
    
    Returns:
    --------
    analysis : dict
        Statistical analysis of results
    """
    
    if len(results_df) == 0:
        if verbose:
            print("No fat sandwiches detected.")
        return {}
    
    analysis = {}
    
    # Time span statistics
    analysis['avg_time_span_ms'] = results_df['actual_time_span_ms'].mean()
    analysis['median_time_span_ms'] = results_df['actual_time_span_ms'].median()
    analysis['max_time_span_ms'] = results_df['actual_time_span_ms'].max()
    analysis['min_time_span_ms'] = results_df['actual_time_span_ms'].min()
    
    # Victim statistics
    analysis['avg_victims'] = results_df['victim_count'].mean()
    analysis['max_victims'] = results_df['victim_count'].max()
    analysis['total_unique_victims'] = len(set([v for victims in results_df['victim_signers'] for v in victims]))
    
    # Attacker statistics
    analysis['unique_attackers'] = results_df['attacker_signer'].nunique()
    analysis['most_active_attackers'] = results_df['attacker_signer'].value_counts().head(10).to_dict()
    
    # Slot statistics
    if 'slot_span' in results_df.columns:
        analysis['avg_slot_span'] = results_df['slot_span'].mean()
        analysis['max_slot_span'] = results_df['slot_span'].max()
        analysis['single_slot_attacks'] = (results_df['slot_span'] == 0).sum()
        analysis['multi_slot_attacks'] = (results_df['slot_span'] > 0).sum()
    
    # Validator statistics
    if 'validator' in results_df.columns:
        analysis['unique_validators'] = results_df['validator'].nunique()
        analysis['top_validators'] = results_df['validator'].value_counts().head(10).to_dict()
    
    # AMM statistics
    if 'amm_trade' in results_df.columns:
        analysis['amms_affected'] = results_df['amm_trade'].nunique()
        analysis['top_amms'] = results_df['amm_trade'].value_counts().head(10).to_dict()
    
    if verbose:
        print("=" * 80)
        print("STATISTICAL ANALYSIS")
        print("=" * 80)
        print()
        print("Time Span Statistics:")
        print(f"  Average: {analysis['avg_time_span_ms']:.0f}ms ({analysis['avg_time_span_ms']/1000:.2f}s)")
        print(f"  Median:  {analysis['median_time_span_ms']:.0f}ms ({analysis['median_time_span_ms']/1000:.2f}s)")
        print(f"  Maximum: {analysis['max_time_span_ms']:.0f}ms ({analysis['max_time_span_ms']/1000:.2f}s)")
        print(f"  Minimum: {analysis['min_time_span_ms']:.0f}ms ({analysis['min_time_span_ms']/1000:.2f}s)")
        print()
        
        print("Victim Statistics:")
        print(f"  Average victims per attack: {analysis['avg_victims']:.1f}")
        print(f"  Maximum victims in single attack: {analysis['max_victims']}")
        print(f"  Total unique victims: {analysis['total_unique_victims']:,}")
        print()
        
        print("Attacker Statistics:")
        print(f"  Unique attackers: {analysis['unique_attackers']:,}")
        print(f"  Top 5 most active attackers:")
        for i, (attacker, count) in enumerate(list(analysis['most_active_attackers'].items())[:5], 1):
            print(f"    {i}. {attacker[:44]:44s}: {count:>4,} attacks")
        print()
        
        if 'slot_span' in results_df.columns:
            print("Slot Statistics:")
            print(f"  Average slot span: {analysis['avg_slot_span']:.2f} slots")
            print(f"  Maximum slot span: {analysis['max_slot_span']} slots")
            print(f"  Single-slot attacks: {analysis['single_slot_attacks']:,} ({analysis['single_slot_attacks']/len(results_df)*100:.1f}%)")
            print(f"  Multi-slot attacks: {analysis['multi_slot_attacks']:,} ({analysis['multi_slot_attacks']/len(results_df)*100:.1f}%)")
            print()
        
        if 'validator' in results_df.columns:
            print("Validator Statistics:")
            print(f"  Validators affected: {analysis['unique_validators']:,}")
            print(f"  Top 5 validators by attack count:")
            for i, (validator, count) in enumerate(list(analysis['top_validators'].items())[:5], 1):
                print(f"    {i}. {validator[:44]:44s}: {count:>4,} attacks")
            print()
        
        if 'amm_trade' in results_df.columns:
            print("PropAMM Statistics:")
            print(f"  PropAMMs affected: {analysis['amms_affected']}")
            print(f"  Top 5 PropAMMs by attack count:")
            for i, (amm, count) in enumerate(list(analysis['top_amms'].items())[:5], 1):
                print(f"    {i}. {amm:20s}: {count:>4,} attacks")
            print()
    
    return analysis


def compare_detection_methods(old_results_count, new_results_df, verbose=True):
    """
    Compare old and new detection methods.
    
    Parameters:
    -----------
    old_results_count : int
        Number of detections from old method
    new_results_df : DataFrame
        Results from new method
    verbose : bool
        Print comparison
    
    Returns:
    --------
    comparison : dict
        Comparison statistics
    """
    
    new_count = len(new_results_df)
    reduction = old_results_count - new_count
    reduction_pct = (reduction / old_results_count * 100) if old_results_count > 0 else 0
    
    # Calculate average time span for new results
    avg_time_new = new_results_df['actual_time_span_ms'].mean() / 1000 if len(new_results_df) > 0 else 0
    max_time_new = new_results_df['actual_time_span_ms'].max() / 1000 if len(new_results_df) > 0 else 0
    
    comparison = {
        'old_method_count': old_results_count,
        'new_method_count': new_count,
        'reduction': reduction,
        'reduction_percentage': reduction_pct,
        'avg_time_span_seconds': avg_time_new,
        'max_time_span_seconds': max_time_new,
        'quality_improvement': 'high' if reduction_pct > 50 else 'medium' if reduction_pct > 30 else 'low'
    }
    
    if verbose:
        print("=" * 80)
        print("METHOD COMPARISON: Old vs New")
        print("=" * 80)
        print()
        print(f"Old Method (No Time Limit):")
        print(f"  Detections: {old_results_count:,}")
        print(f"  Issues: Detected patterns spanning hours")
        print(f"  Example: 5.5 hour 'sandwich' with 102 victims")
        print()
        print(f"New Method (Rolling Time Windows):")
        print(f"  Detections: {new_count:,}")
        print(f"  Reduction: {reduction:,} ({reduction_pct:.1f}%)")
        print(f"  Average time span: {avg_time_new:.2f} seconds")
        print(f"  Maximum time span: {max_time_new:.2f} seconds")
        print()
        print(f"Quality Assessment: {comparison['quality_improvement'].upper()}")
        if reduction_pct > 70:
            print("  ✅ Excellent - Removed majority of false positives")
        elif reduction_pct > 50:
            print("  ✅ Good - Significant false positive reduction")
        elif reduction_pct > 30:
            print("  ⚠️  Moderate - Some improvement")
        else:
            print("  ❌ Low - May need parameter adjustment")
        print()
    
    return comparison


if __name__ == "__main__":
    print("Improved Fat Sandwich Detection Module")
    print("This module should be imported and used in notebooks/scripts")
    print()
    print("Example usage:")
    print("""
    from improved_fat_sandwich_detection import (
        detect_fat_sandwich_time_window,
        classify_mev_attack,
        classify_mev_attacks_batch,
        detect_cycle_routing,
        analyze_pool_diversity
    )
    
    # Load your data
    df_trades = pd.read_parquet('pamm_clean_final.parquet')
    df_trades = df_trades[df_trades['kind'] == 'TRADE']
    
    # Run detection
    results, stats = detect_fat_sandwich_time_window(
        df_trades,
        window_seconds=[1, 2, 5, 10],
        min_trades=5,
        max_victim_ratio=0.8
    )
    
    # Classify attacks by type
    classified_results = classify_mev_attacks_batch(
        df_trades,
        results,
        verbose=True
    )
    
    # Get detailed classification for a specific attack
    for idx, row in results.head(1).iterrows():
        cluster = df_trades[
            (df_trades['slot'] >= row['start_slot']) &
            (df_trades['slot'] <= row['end_slot']) &
            (df_trades['ms_time'] >= row['start_time_ms']) &
            (df_trades['ms_time'] <= row['end_time_ms'])
        ]
        classification = classify_mev_attack(cluster, row['attacker_signer'], verbose=True)
    """)


def classify_mev_attacks_batch(df_all_trades, detected_attacks_df, verbose=False, show_progress=True):
    """
    Batch classify all detected attacks as Fat Sandwich vs Multi-Hop Arbitrage.
    
    Parameters:
    -----------
    df_all_trades : DataFrame
        Complete trades DataFrame
    detected_attacks_df : DataFrame
        Results from detect_fat_sandwich_time_window()
    verbose : bool
        Print detailed classification for each attack
    show_progress : bool
        Show progress bar
    
    Returns:
    --------
    classified_df : DataFrame
        Original dataframe with added classification columns:
        - attack_type: 'fat_sandwich' | 'multi_hop_arbitrage' | 'ambiguous'
        - classification_confidence: float 0-1
        - fat_sandwich_score: float 0-1
        - multi_hop_score: float 0-1
        - cycle_routing_detected: bool
        - unique_pools_used: int
        - victim_count: int
    """
    
    classified_results = []
    
    total = len(detected_attacks_df)
    for i, (idx, attack_row) in enumerate(detected_attacks_df.iterrows()):
        if show_progress and i % max(1, total // 10) == 0:
            print(f"Classifying attacks: {i}/{total}")
        
        # Extract cluster trades for this attack
        cluster_trades = df_all_trades[
            (df_all_trades['slot'] >= attack_row['start_slot']) &
            (df_all_trades['slot'] <= attack_row['end_slot']) &
            (df_all_trades['ms_time'] >= attack_row['start_time_ms']) &
            (df_all_trades['ms_time'] <= attack_row['end_time_ms'])
        ].copy()
        
        if len(cluster_trades) == 0:
            continue
        
        # Classify
        classification = classify_mev_attack(
            cluster_trades,
            attack_row['attacker_signer'],
            verbose=verbose
        )
        
        # Collect cycle routing info
        cycle_info = detect_cycle_routing(cluster_trades, attack_row['attacker_signer'])
        pool_info = analyze_pool_diversity(cluster_trades, attack_row['attacker_signer'])
        
        # Create result row
        result_row = attack_row.to_dict()
        result_row['attack_type'] = classification['attack_type']
        result_row['classification_confidence'] = classification['confidence']
        result_row['fat_sandwich_score'] = classification['fat_sandwich_score']
        result_row['multi_hop_score'] = classification['multi_hop_score']
        result_row['cycle_routing_detected'] = cycle_info['is_cycle']
        result_row['cycle_confidence'] = cycle_info['confidence']
        result_row['unique_pools_used'] = pool_info['unique_pools']
        result_row['victim_count_detected'] = classification['reasoning']['victim_info']['count']
        
        classified_results.append(result_row)
    
    classified_df = pd.DataFrame(classified_results)
    
    if show_progress:
        print(f"Completed: {total}/{total}")
        print()
        print("Classification Summary:")
        if 'attack_type' in classified_df.columns:
            counts = classified_df['attack_type'].value_counts()
            for atype, count in counts.items():
                pct = count / len(classified_df) * 100
                print(f"  {atype:25s}: {count:>5,} ({pct:>5.1f}%)")
        print()
    
    return classified_df
