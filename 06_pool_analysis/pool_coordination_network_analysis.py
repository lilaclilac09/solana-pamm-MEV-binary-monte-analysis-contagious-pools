"""
Pool Coordination Network Analysis
Analyzes attacker-pool coordination patterns, adjacent pool activity, and cross-protocol timing alignment.

Key components:
1. Coordination Network Analysis: NetworkX-based attacker-pool coordination graphs
2. Adjacent Pool Pattern Detection: Temporal trade sequence tracking across PropAMMs
3. Cross-Protocol Timing Alignment: BisonFi oracle bursts vs other protocol trade timestamps
"""

import pandas as pd
import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import json
from pathlib import Path


class PoolCoordinationAnalyzer:
    """Analyzes coordination patterns between attackers and pools."""
    
    def __init__(self, mev_data_path: str = None, trades_data_path: str = None):
        """
        Initialize the analyzer.
        
        Parameters:
        -----------
        mev_data_path : str
            Path to MEV detection results CSV
        trades_data_path : str
            Path to trades data CSV
        """
        self.mev_data = None
        self.trades_data = None
        self.coordination_graph = nx.Graph()
        self.attacker_pool_mapping = defaultdict(set)
        self.pool_attacker_mapping = defaultdict(set)
        self.temporal_patterns = {}
        
        if mev_data_path:
            self.load_mev_data(mev_data_path)
        if trades_data_path:
            self.load_trades_data(trades_data_path)
    
    def load_mev_data(self, path: str):
        """Load MEV detection data."""
        self.mev_data = pd.read_csv(path)
        print(f"Loaded MEV data: {len(self.mev_data)} records")
    
    def load_trades_data(self, path: str):
        """Load trades data."""
        self.trades_data = pd.read_csv(path)
        print(f"Loaded trades data: {len(self.trades_data)} records")
    
    # ==================== PART 1: COORDINATION NETWORK ANALYSIS ====================
    
    def build_attacker_pool_graph(self, mev_df: pd.DataFrame, 
                                   min_interaction_weight: int = 2) -> nx.Graph:
        """
        Build a coordination graph where nodes are attackers/pools and 
        edges represent shared activity/signers.
        
        Parameters:
        -----------
        mev_df : pd.DataFrame
            MEV detection results with columns: attacker_address, token_pair, pool_address
        min_interaction_weight : int
            Minimum number of shared interactions to create an edge
        
        Returns:
        --------
        nx.Graph
            Coordination network graph
        """
        graph = nx.Graph()
        
        # Build attacker-pool relationships
        for _, row in mev_df.iterrows():
            attacker = row.get('attacker_address', row.get('signer'))
            pool = row.get('pool_address', row.get('pool'))
            
            if pd.isna(attacker) or pd.isna(pool):
                continue
            
            # Add nodes
            graph.add_node(f"attacker_{attacker}", node_type='attacker')
            graph.add_node(f"pool_{pool}", node_type='pool')
            
            # Track mappings
            self.attacker_pool_mapping[attacker].add(pool)
            self.pool_attacker_mapping[pool].add(attacker)
        
        # Calculate shared pool matrix to find coordinating attackers
        attackers = list(self.attacker_pool_mapping.keys())
        for i, attacker1 in enumerate(attackers):
            for attacker2 in attackers[i+1:]:
                shared_pools = self.attacker_pool_mapping[attacker1] & \
                               self.attacker_pool_mapping[attacker2]
                
                if len(shared_pools) >= min_interaction_weight:
                    weight = len(shared_pools)
                    graph.add_edge(f"attacker_{attacker1}", 
                                  f"attacker_{attacker2}", 
                                  weight=weight, 
                                  shared_pools=list(shared_pools))
        
        self.coordination_graph = graph
        return graph
    
    def analyze_strong_coordinators(self, graph: nx.Graph = None, 
                                     top_n: int = 10) -> Dict:
        """
        Identify strongly coordinated attacker groups.
        
        Parameters:
        -----------
        graph : nx.Graph
            Coordination network (uses self.coordination_graph if None)
        top_n : int
            Number of top coordinators to return
        
        Returns:
        --------
        Dict
            Analysis of coordinated attackers and pools
        """
        if graph is None:
            graph = self.coordination_graph
        
        results = {
            'top_coordinators': [],
            'coordination_clusters': [],
            'high_weight_edges': [],
            'pool_exploitation_hubs': []
        }
        
        # Get top coordinating attackers by degree
        attacker_nodes = [n for n, attr in graph.nodes(data=True) 
                         if attr.get('node_type') == 'attacker']
        
        degree_dict = dict(graph.degree(attacker_nodes, weight='weight'))
        top_attackers = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results['top_coordinators'] = [
            {'attacker': node.replace('attacker_', ''), 'coordination_weight': weight}
            for node, weight in top_attackers
        ]
        
        # Find cliques (tight coordination groups)
        cliques = list(nx.find_cliques(graph.subgraph(attacker_nodes)))
        results['coordination_clusters'] = [
            {
                'cluster_size': len(clique),
                'attackers': [n.replace('attacker_', '') for n in clique],
                'density': nx.density(graph.subgraph(clique))
            }
            for clique in cliques if len(clique) >= 3
        ]
        
        # High-weight edges (strong coordination patterns)
        high_weight_edges = [(u, v, data['weight']) 
                           for u, v, data in graph.edges(data=True) 
                           if data['weight'] >= 3]
        high_weight_edges.sort(key=lambda x: x[2], reverse=True)
        
        results['high_weight_edges'] = [
            {
                'attacker1': edge[0].replace('attacker_', ''),
                'attacker2': edge[1].replace('attacker_', ''),
                'shared_pools': edge[2]
            }
            for edge in high_weight_edges[:top_n]
        ]
        
        # Identify pools with highest attacker concentration
        pool_nodes = [n for n, attr in graph.nodes(data=True) 
                     if attr.get('node_type') == 'pool']
        pool_degree = dict(graph.degree(pool_nodes))
        
        results['pool_exploitation_hubs'] = [
            {'pool': node.replace('pool_', ''), 'num_attackers': degree}
            for node, degree in sorted(pool_degree.items(), 
                                      key=lambda x: x[1], reverse=True)[:top_n]
        ]
        
        return results
    
    def detect_bisonfi_humidifi_correlation(self, mev_df: pd.DataFrame) -> Dict:
        """
        Analyze correlation between BisonFi and HumidiFi attacks by same signers.
        Look for high edge weights in the coordination graph between these two pools.
        
        Parameters:
        -----------
        mev_df : pd.DataFrame
            MEV data with pool and attacker information
        
        Returns:
        --------
        Dict
            Correlation metrics and evidence
        """
        bisonfi_attackers = set()
        humidifi_attackers = set()
        
        for _, row in mev_df.iterrows():
            pool = str(row.get('pool_address', row.get('pool', ''))).lower()
            attacker = row.get('attacker_address', row.get('signer'))
            
            if 'bisonfi' in pool.lower():
                bisonfi_attackers.add(attacker)
            elif 'humidifi' in pool.lower():
                humidifi_attackers.add(attacker)
        
        shared_attackers = bisonfi_attackers & humidifi_attackers
        
        results = {
            'bisonfi_attacker_count': len(bisonfi_attackers),
            'humidifi_attacker_count': len(humidifi_attackers),
            'shared_attackers': len(shared_attackers),
            'shared_attacker_percentage': (
                len(shared_attackers) / max(len(bisonfi_attackers), 1) * 100 
                if bisonfi_attackers else 0
            ),
            'evidence': {
                'bisonfi_unique': bisonfi_attackers - humidifi_attackers,
                'humidifi_unique': humidifi_attackers - bisonfi_attackers,
                'shared_signers': list(shared_attackers)[:10]  # Top 10 for display
            }
        }
        
        # Find edges in coordination graph for BisonFi->HumidiFi
        coordination_edges = []
        for attacker in shared_attackers:
            bisonfi_interactions = 0
            humidifi_interactions = 0
            
            for _, row in mev_df.iterrows():
                if row.get('attacker_address', row.get('signer')) == attacker:
                    pool = str(row.get('pool_address', row.get('pool', ''))).lower()
                    if 'bisonfi' in pool.lower():
                        bisonfi_interactions += 1
                    elif 'humidifi' in pool.lower():
                        humidifi_interactions += 1
            
            if bisonfi_interactions > 0 and humidifi_interactions > 0:
                coordination_edges.append({
                    'attacker': attacker,
                    'bisonfi_interactions': bisonfi_interactions,
                    'humidifi_interactions': humidifi_interactions,
                    'correlation_strength': min(bisonfi_interactions, humidifi_interactions)
                })
        
        results['coordination_edges'] = sorted(
            coordination_edges, 
            key=lambda x: x['correlation_strength'], 
            reverse=True
        )[:10]
        
        return results
    
    # ==================== PART 2: ADJACENT POOL PATTERN DETECTION ====================
    
    def detect_pool_coordination(self, trades_df: pd.DataFrame, 
                                 token_pair: str = None,
                                 time_window_ms: int = 5000) -> Dict:
        """
        Detect temporal sequences of trades across different pools for same token pair.
        This identifies when attackers target adjacent pools in sequence.
        
        Parameters:
        -----------
        trades_df : pd.DataFrame
            Trades data with columns: timestamp, pool, token_pair, signer, amount
        token_pair : str
            Specific token pair to analyze (e.g., 'PUMP/WSOL'). If None, analyzes all.
        time_window_ms : int
            Time window in milliseconds to consider trades as "coordinated"
        
        Returns:
        --------
        Dict
            Detected pool coordination patterns
        """
        results = {
            'coordinated_sequences': [],
            'pool_pairs_by_frequency': [],
            'temporal_patterns': [],
            'total_sequences_found': 0,
            'average_sequence_length': 0
        }
        
        # Ensure timestamp is datetime
        trades_df = trades_df.copy()
        if 'timestamp' in trades_df.columns:
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        
        # Filter by token pair if specified
        if token_pair:
            filtered = trades_df[trades_df['token_pair'].str.contains(
                token_pair, case=False, na=False)]
        else:
            filtered = trades_df
        
        if len(filtered) == 0:
            return results
        
        # Group by signer to find their trade sequences
        signer_sequences = defaultdict(list)
        
        for _, row in filtered.iterrows():
            signer = row.get('signer', row.get('attacker_address'))
            if pd.notna(signer):
                signer_sequences[signer].append({
                    'timestamp': row['timestamp'],
                    'pool': row.get('pool_address', row.get('pool')),
                    'amount': row.get('amount', row.get('trade_amount')),
                    'token_pair': row.get('token_pair')
                })
        
        # Analyze sequences for coordination patterns
        all_sequences = []
        pool_pair_counter = Counter()
        
        for signer, trades in signer_sequences.items():
            # Sort trades by timestamp
            trades = sorted(trades, key=lambda x: x['timestamp'])
            
            if len(trades) < 2:
                continue
            
            # Find coordinated clusters (trades within time_window)
            cluster = [trades[0]]
            
            for i in range(1, len(trades)):
                time_diff = (trades[i]['timestamp'] - cluster[0]['timestamp']).total_seconds() * 1000
                
                if time_diff <= time_window_ms:
                    cluster.append(trades[i])
                else:
                    # Analyze completed cluster
                    if len(cluster) >= 2:
                        unique_pools = len(set(t['pool'] for t in cluster))
                        if unique_pools >= 2:
                            sequence_record = {
                                'signer': signer,
                                'num_pools': unique_pools,
                                'pool_sequence': [t['pool'] for t in cluster],
                                'timestamps': [t['timestamp'].isoformat() for t in cluster],
                                'time_span_ms': time_diff,
                                'total_amount': sum(t['amount'] if pd.notna(t['amount']) else 0 
                                                  for t in cluster)
                            }
                            all_sequences.append(sequence_record)
                            
                            # Track pool pairs
                            pools = [t['pool'] for t in cluster]
                            for j in range(len(pools) - 1):
                                pair = tuple(sorted([pools[j], pools[j+1]]))
                                pool_pair_counter[pair] += 1
                    
                    cluster = [trades[i]]
        
        results['coordinated_sequences'] = sorted(
            all_sequences, 
            key=lambda x: x['total_amount'], 
            reverse=True
        )[:50]
        
        results['pool_pairs_by_frequency'] = [
            {
                'pool_1': pair[0],
                'pool_2': pair[1],
                'frequency': count
            }
            for pair, count in pool_pair_counter.most_common(20)
        ]
        
        results['total_sequences_found'] = len(all_sequences)
        if all_sequences:
            results['average_sequence_length'] = np.mean(
                [s['num_pools'] for s in all_sequences]
            )
        
        return results
    
    def analyze_pool_impact_timing(self, pool_trades_df: pd.DataFrame) -> Dict:
        """
        Analyze the timing of trades when an attacker targets multiple pools.
        Identifies if there's a dominant "trigger" pool.
        
        Parameters:
        -----------
        pool_trades_df : pd.DataFrame
            Trades from a specific pool with attacker information
        
        Returns:
        --------
        Dict
            Timing patterns and trigger pool analysis
        """
        results = {
            'pool_activity_timeline': [],
            'trigger_pools': [],
            'cascade_patterns': []
        }
        
        # Group by signer to find their activity patterns
        for signer in pool_trades_df['signer'].unique():
            signer_trades = pool_trades_df[
                pool_trades_df['signer'] == signer
            ].sort_values('timestamp')
            
            if len(signer_trades) > 1:
                time_gaps = signer_trades['timestamp'].diff().dt.total_seconds() * 1000
                
                results['pool_activity_timeline'].append({
                    'signer': signer,
                    'trade_count': len(signer_trades),
                    'avg_gap_ms': time_gaps.mean(),
                    'min_gap_ms': time_gaps.min(),
                    'max_gap_ms': time_gaps.max()
                })
        
        return results
    
    # ==================== PART 3: CROSS-PROTOCOL TIMING ALIGNMENT ====================
    
    def detect_bisonfi_oracle_bursts(self, bisonfi_trades_df: pd.DataFrame,
                                     amplitude_threshold: float = 2.0) -> Dict:
        """
        Detect oracle price bursts on BisonFi that could trigger cascading attacks.
        
        Parameters:
        -----------
        bisonfi_trades_df : pd.DataFrame
            BisonFi trades with price information
        amplitude_threshold : float
            Standard deviations from mean to consider as "burst"
        
        Returns:
        --------
        Dict
            Detected oracle bursts with timing and amplitude
        """
        results = {
            'detected_bursts': [],
            'burst_timeline': [],
            'burst_statistics': {}
        }
        
        if len(bisonfi_trades_df) < 10:
            return results
        
        # Calculate price volatility by token pair
        for token_pair in bisonfi_trades_df['token_pair'].unique():
            token_trades = bisonfi_trades_df[
                bisonfi_trades_df['token_pair'] == token_pair
            ].sort_values('timestamp').copy()
            
            if len(token_trades) < 5:
                continue
            
            # Calculate price changes
            if 'price' in token_trades.columns:
                price_changes = token_trades['price'].pct_change() * 100
            else:
                # Estimate from amount differences
                price_changes = token_trades['amount'].pct_change() * 100
            
            mean_change = price_changes.mean()
            std_change = price_changes.std()
            
            # Detect bursts
            bursts = []
            for idx, (ts, change) in enumerate(zip(token_trades['timestamp'], price_changes)):
                if pd.notna(change) and std_change > 0:
                    z_score = (change - mean_change) / std_change
                    if abs(z_score) > amplitude_threshold:
                        bursts.append({
                            'timestamp': ts.isoformat(),
                            'token_pair': token_pair,
                            'price_change_pct': float(change),
                            'z_score': float(z_score),
                            'amplitude': abs(z_score)
                        })
            
            results['detected_bursts'].extend(bursts)
            results['burst_statistics'][token_pair] = {
                'mean_change': float(mean_change),
                'std_change': float(std_change),
                'num_bursts': len(bursts)
            }
        
        results['detected_bursts'] = sorted(
            results['detected_bursts'], 
            key=lambda x: x['amplitude'], 
            reverse=True
        )[:50]
        
        return results
    
    def cross_protocol_burst_correlation(self, bisonfi_bursts: List[Dict],
                                        other_protocol_trades: pd.DataFrame,
                                        time_window_ms: int = 1000) -> Dict:
        """
        Correlate BisonFi oracle bursts with attack execution on other protocols.
        Measures the percentage of attacks that follow BisonFi bursts.
        
        Parameters:
        -----------
        bisonfi_bursts : List[Dict]
            Detected BisonFi oracle bursts
        other_protocol_trades : pd.DataFrame
            Trades from other protocols with timestamp
        time_window_ms : int
            Time window after burst to check for correlated attacks (ms)
        
        Returns:
        --------
        Dict
            Cross-protocol correlation analysis with statistical significance
        """
        results = {
            'burst_correlation_analysis': [],
            'contagion_percentage': 0.0,
            'statistical_significance': 0.0,
            'evidence_summary': {}
        }
        
        if len(bisonfi_bursts) == 0 or len(other_protocol_trades) == 0:
            return results
        
        other_protocol_trades = other_protocol_trades.copy()
        other_protocol_trades['timestamp'] = pd.to_datetime(
            other_protocol_trades['timestamp']
        )
        
        matched_attacks = 0
        total_attacks = len(other_protocol_trades)
        
        attack_correlations = []
        
        for _, attack in other_protocol_trades.iterrows():
            attack_time = attack['timestamp']
            
            # Check if there was a BisonFi burst in the lookback window
            correlating_burst = None
            min_time_diff = float('inf')
            
            for burst in bisonfi_bursts:
                burst_time = pd.to_datetime(burst['timestamp'])
                time_diff = (attack_time - burst_time).total_seconds() * 1000
                
                # Attack should follow burst within time_window
                if 0 <= time_diff <= time_window_ms:
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        correlating_burst = burst
            
            if correlating_burst:
                matched_attacks += 1
                attack_correlations.append({
                    'attack_timestamp': attack_time.isoformat(),
                    'burst_timestamp': correlating_burst['timestamp'],
                    'time_lag_ms': min_time_diff,
                    'burst_token_pair': correlating_burst['token_pair'],
                    'burst_amplitude': correlating_burst['amplitude'],
                    'attack_token_pair': attack.get('token_pair', 'unknown')
                })
        
        contagion_pct = (matched_attacks / total_attacks * 100) if total_attacks > 0 else 0
        
        results['contagion_percentage'] = contagion_pct
        results['matched_attacks'] = matched_attacks
        results['total_attacks_analyzed'] = total_attacks
        results['burst_correlation_analysis'] = sorted(
            attack_correlations, 
            key=lambda x: x['time_lag_ms']
        )[:100]
        
        # Calculate statistical significance (Z-score against random distribution)
        if total_attacks > 0 and len(bisonfi_bursts) > 0:
            # Expected random match rate
            burst_time_range = (
                pd.to_datetime(bisonfi_bursts[-1]['timestamp']) - 
                pd.to_datetime(bisonfi_bursts[0]['timestamp'])
            ).total_seconds() * 1000
            
            if burst_time_range > 0:
                expected_matches = (total_attacks * len(bisonfi_bursts) * 
                                   time_window_ms / burst_time_range)
                std_matches = np.sqrt(expected_matches * (1 - expected_matches / total_attacks))
                
                if std_matches > 0:
                    z_score = (matched_attacks - expected_matches) / std_matches
                    results['statistical_significance'] = float(z_score)
        
        results['evidence_summary'] = {
            'interpretation': (
                f"{contagion_pct:.1f}% of attacks on other protocols occur within "
                f"{time_window_ms}ms of BisonFi oracle bursts. "
                f"Z-score: {results['statistical_significance']:.2f} "
                f"(significant if |Z| > 2.0)"
            ),
            'contagion_confirmed': contagion_pct > 90.0 and results['statistical_significance'] > 2.0
        }
        
        return results
    
    # ==================== REPORTING ====================
    
    def generate_comprehensive_report(self, output_path: str = None) -> Dict:
        """
        Generate comprehensive coordination analysis report.
        
        Parameters:
        -----------
        output_path : str
            Path to save JSON report
        
        Returns:
        --------
        Dict
            Complete analysis report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_sections': {
                'network_analysis': self.analyze_strong_coordinators(),
                'bisonfi_humidifi_correlation': (
                    self.detect_bisonfi_humidifi_correlation(self.mev_data) 
                    if self.mev_data is not None else None
                ),
                'pool_coordination': (
                    self.detect_pool_coordination(self.trades_data) 
                    if self.trades_data is not None else None
                )
            }
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to {output_path}")
        
        return report


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Example usage
    analyzer = PoolCoordinationAnalyzer()
    
    # Example: Load data and analyze
    # analyzer.load_mev_data("path/to/mev_data.csv")
    # analyzer.load_trades_data("path/to/trades_data.csv")
    
    # Build coordination network
    # graph = analyzer.build_attacker_pool_graph(analyzer.mev_data)
    
    # Analyze strong coordinators
    # coordination_results = analyzer.analyze_strong_coordinators(top_n=10)
    
    # Detect BisonFi-HumidiFi correlation
    # bisonfi_humidifi = analyzer.detect_bisonfi_humidifi_correlation(analyzer.mev_data)
    
    # Detect pool coordination patterns
    # pool_coordination = analyzer.detect_pool_coordination(analyzer.trades_data, token_pair="PUMP/WSOL")
    
    # Detect oracle bursts and cross-protocol correlation
    # bisonfi_bursts = analyzer.detect_bisonfi_oracle_bursts(bisonfi_trades_df)
    # cross_protocol = analyzer.cross_protocol_burst_correlation(bisonfi_bursts, other_protocol_trades)
    
    print("Pool Coordination Network Analysis module loaded successfully")
