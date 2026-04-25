"""
Vectorized version of 06_pool_analysis/pool_coordination_network_analysis.py.

Subclasses the original ``PoolCoordinationAnalyzer`` and overrides the
hottest methods. The biggest wins are:

1. ``build_attacker_pool_graph`` — replaces an iterrows loop over MEV
   rows + an O(N^2) Python double-loop over attackers (with set
   intersection per pair) with a single ``crosstab`` + sparse matrix
   product. Yields the same NetworkX graph and edge weights.

2. ``detect_bisonfi_humidifi_correlation`` — original iterates the MEV
   df once to bucket attackers, then iterates the *whole* df again
   *per shared attacker* (O(shared_attackers x rows)). Replaced with
   a single groupby producing per-attacker pool counts.

3. ``detect_pool_coordination`` — replaces iterrows building a
   per-signer trade list with a sorted groupby; cluster detection
   stays Python-loop but only over each signer's already-sorted
   trades, not over the whole df.

4. ``analyze_pool_impact_timing`` — replaces the per-signer filter
   loop with a single groupby aggregate.

5. ``detect_bisonfi_oracle_bursts`` — replaces the per-token-pair
   filter loop with groupby + transform.

6. ``cross_protocol_burst_correlation`` — replaces an O(attacks x
   bursts) Python double-loop with a vectorized ``searchsorted``
   against the sorted burst timeline.

All public method signatures and return shapes are preserved.
"""

from __future__ import annotations

import importlib.util
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import networkx as nx
import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ORIGINAL = _HERE / "pool_coordination_network_analysis.py"
_spec = importlib.util.spec_from_file_location("pcn_original", _ORIGINAL)
_orig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_orig)

PoolCoordinationAnalyzer = _orig.PoolCoordinationAnalyzer


class PoolCoordinationAnalyzerOptimized(PoolCoordinationAnalyzer):
    """Drop-in replacement with vectorized hot paths."""

    @staticmethod
    def _resolve_attacker_pool(mev_df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        for col in ('attacker_address', 'signer', 'attacker_signer'):
            if col in mev_df.columns:
                attacker = mev_df[col]
                break
        else:
            raise KeyError("MEV frame missing attacker column "
                           "(expected one of attacker_address/signer/attacker_signer)")
        for col in ('pool_address', 'pool', 'amm_trade'):
            if col in mev_df.columns:
                pool = mev_df[col]
                break
        else:
            raise KeyError("MEV frame missing pool column "
                           "(expected one of pool_address/pool/amm_trade)")
        return attacker, pool

    # ---- 1. Coordination graph -----------------------------------------
    def build_attacker_pool_graph(self, mev_df: pd.DataFrame,
                                  min_interaction_weight: int = 2) -> nx.Graph:
        graph = nx.Graph()
        attackers_s, pools_s = self._resolve_attacker_pool(mev_df)
        clean = pd.DataFrame({'attacker': attackers_s, 'pool': pools_s}).dropna()

        for attacker, pool in zip(clean['attacker'], clean['pool']):
            graph.add_node(f"attacker_{attacker}", node_type='attacker')
            graph.add_node(f"pool_{pool}", node_type='pool')
            self.attacker_pool_mapping[attacker].add(pool)
            self.pool_attacker_mapping[pool].add(attacker)

        # Original: O(A^2) Python set intersections. Vectorized: build a
        # binary attacker x pool indicator matrix and multiply by its
        # transpose to get the shared-pool count between every attacker
        # pair in one BLAS call.
        ind = pd.crosstab(clean['attacker'], clean['pool'])
        ind = (ind > 0).astype(np.int64)
        attackers = ind.index.to_list()
        if len(attackers) >= 2:
            shared = ind.to_numpy() @ ind.to_numpy().T
            np.fill_diagonal(shared, 0)
            ii, jj = np.where(shared >= min_interaction_weight)
            seen = set()
            pool_cols = ind.columns.to_numpy()
            for i, j in zip(ii, jj):
                if i >= j:
                    continue
                key = (i, j)
                if key in seen:
                    continue
                seen.add(key)
                weight = int(shared[i, j])
                # Recover the actual shared-pool list for this pair.
                mask = (ind.iloc[i].to_numpy() & ind.iloc[j].to_numpy()).astype(bool)
                shared_pools = pool_cols[mask].tolist()
                graph.add_edge(
                    f"attacker_{attackers[i]}",
                    f"attacker_{attackers[j]}",
                    weight=weight,
                    shared_pools=shared_pools,
                )

        self.coordination_graph = graph
        return graph

    # ---- 2. BisonFi/HumidiFi correlation -------------------------------
    def detect_bisonfi_humidifi_correlation(self, mev_df: pd.DataFrame) -> Dict:
        attackers_s, pools_s = self._resolve_attacker_pool(mev_df)
        clean = pd.DataFrame({
            'attacker': attackers_s,
            'pool_lower': pools_s.astype(str).str.lower(),
        }).dropna(subset=['attacker'])

        bisonfi_mask = clean['pool_lower'].str.contains('bisonfi', na=False)
        humidifi_mask = clean['pool_lower'].str.contains('humidifi', na=False)

        bisonfi_attackers = set(clean.loc[bisonfi_mask, 'attacker'].unique())
        humidifi_attackers = set(clean.loc[humidifi_mask, 'attacker'].unique())
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
                'shared_signers': list(shared_attackers)[:10],
            },
        }

        # Original: per shared-attacker, full df scan (O(shared * rows)).
        # Optimized: one groupby gives per-attacker counts in each pool.
        if shared_attackers:
            shared_df = clean[clean['attacker'].isin(shared_attackers)]
            counts = (
                shared_df.assign(
                    is_bisonfi=shared_df['pool_lower'].str.contains('bisonfi', na=False).astype(int),
                    is_humidifi=shared_df['pool_lower'].str.contains('humidifi', na=False).astype(int),
                )
                .groupby('attacker')
                .agg(bisonfi_interactions=('is_bisonfi', 'sum'),
                     humidifi_interactions=('is_humidifi', 'sum'))
            )
            edges = []
            for attacker, row in counts.iterrows():
                bf = int(row['bisonfi_interactions'])
                hf = int(row['humidifi_interactions'])
                if bf > 0 and hf > 0:
                    edges.append({
                        'attacker': attacker,
                        'bisonfi_interactions': bf,
                        'humidifi_interactions': hf,
                        'correlation_strength': min(bf, hf),
                    })
            results['coordination_edges'] = sorted(
                edges, key=lambda x: x['correlation_strength'], reverse=True
            )[:10]
        else:
            results['coordination_edges'] = []
        return results

    # ---- 3. Pool coordination sequences --------------------------------
    def detect_pool_coordination(self, trades_df: pd.DataFrame,
                                 token_pair: str = None,
                                 time_window_ms: int = 5000) -> Dict:
        results = {
            'coordinated_sequences': [],
            'pool_pairs_by_frequency': [],
            'temporal_patterns': [],
            'total_sequences_found': 0,
            'average_sequence_length': 0,
        }
        if trades_df is None or trades_df.empty:
            return results

        df = trades_df.copy()
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if token_pair:
            df = df[df['token_pair'].astype(str).str.contains(token_pair, case=False, na=False)]
        if df.empty:
            return results

        # Resolve signer / pool / amount columns up front (vectorized).
        signer_col = 'signer' if 'signer' in df.columns else 'attacker_address'
        pool_col = 'pool_address' if 'pool_address' in df.columns else 'pool'
        amount_col = 'amount' if 'amount' in df.columns else 'trade_amount'

        df = df.dropna(subset=[signer_col]).sort_values([signer_col, 'timestamp'])

        all_sequences: List[Dict] = []
        pool_pair_counter: Counter = Counter()

        # One pass over the sorted df, grouped by signer. The clustering
        # logic stays the same but no longer pays per-row DataFrame
        # access cost.
        for signer, group in df.groupby(signer_col, sort=False):
            timestamps = group['timestamp'].tolist()
            pools = group[pool_col].tolist()
            amounts = (
                group[amount_col].fillna(0).tolist()
                if amount_col in group.columns
                else [0] * len(group)
            )
            token_pairs = (
                group['token_pair'].tolist()
                if 'token_pair' in group.columns
                else [None] * len(group)
            )
            if len(timestamps) < 2:
                continue
            cluster_idx = [0]
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[cluster_idx[0]]).total_seconds() * 1000
                if gap <= time_window_ms:
                    cluster_idx.append(i)
                else:
                    self._maybe_emit_cluster(
                        signer, cluster_idx, pools, amounts, timestamps,
                        token_pairs, gap, all_sequences, pool_pair_counter,
                    )
                    cluster_idx = [i]
            # tail cluster
            if len(cluster_idx) >= 2:
                tail_gap = (timestamps[cluster_idx[-1]] - timestamps[cluster_idx[0]]).total_seconds() * 1000
                self._maybe_emit_cluster(
                    signer, cluster_idx, pools, amounts, timestamps,
                    token_pairs, tail_gap, all_sequences, pool_pair_counter,
                )

        results['coordinated_sequences'] = sorted(
            all_sequences, key=lambda x: x['total_amount'], reverse=True
        )[:50]
        results['pool_pairs_by_frequency'] = [
            {'pool_1': p[0], 'pool_2': p[1], 'frequency': c}
            for p, c in pool_pair_counter.most_common(20)
        ]
        results['total_sequences_found'] = len(all_sequences)
        if all_sequences:
            results['average_sequence_length'] = float(np.mean(
                [s['num_pools'] for s in all_sequences]
            ))
        return results

    @staticmethod
    def _maybe_emit_cluster(signer, cluster_idx, pools, amounts, timestamps,
                            token_pairs, span, all_sequences, pool_pair_counter):
        cluster_pools = [pools[k] for k in cluster_idx]
        unique_pools = len(set(cluster_pools))
        if unique_pools < 2:
            return
        all_sequences.append({
            'signer': signer,
            'num_pools': unique_pools,
            'pool_sequence': cluster_pools,
            'timestamps': [timestamps[k].isoformat() for k in cluster_idx],
            'time_span_ms': span,
            'total_amount': float(sum(amounts[k] for k in cluster_idx)),
        })
        for j in range(len(cluster_pools) - 1):
            pair = tuple(sorted([cluster_pools[j], cluster_pools[j + 1]]))
            pool_pair_counter[pair] += 1

    # ---- 4. Pool impact timing -----------------------------------------
    def analyze_pool_impact_timing(self, pool_trades_df: pd.DataFrame) -> Dict:
        results = {
            'pool_activity_timeline': [],
            'trigger_pools': [],
            'cascade_patterns': [],
        }
        if pool_trades_df is None or pool_trades_df.empty:
            return results
        df = pool_trades_df.sort_values(['signer', 'timestamp'])
        gaps_ms = (
            df.groupby('signer')['timestamp']
            .diff().dt.total_seconds() * 1000
        )
        df = df.assign(_gap_ms=gaps_ms)
        agg = df.groupby('signer').agg(
            trade_count=('signer', 'size'),
            avg_gap_ms=('_gap_ms', 'mean'),
            min_gap_ms=('_gap_ms', 'min'),
            max_gap_ms=('_gap_ms', 'max'),
        )
        agg = agg[agg['trade_count'] > 1]
        for signer, row in agg.iterrows():
            results['pool_activity_timeline'].append({
                'signer': signer,
                'trade_count': int(row['trade_count']),
                'avg_gap_ms': float(row['avg_gap_ms']) if pd.notna(row['avg_gap_ms']) else None,
                'min_gap_ms': float(row['min_gap_ms']) if pd.notna(row['min_gap_ms']) else None,
                'max_gap_ms': float(row['max_gap_ms']) if pd.notna(row['max_gap_ms']) else None,
            })
        return results

    # ---- 5. Oracle bursts ----------------------------------------------
    def detect_bisonfi_oracle_bursts(self, bisonfi_trades_df: pd.DataFrame,
                                     amplitude_threshold: float = 2.0) -> Dict:
        results = {'detected_bursts': [], 'burst_timeline': [], 'burst_statistics': {}}
        if bisonfi_trades_df is None or len(bisonfi_trades_df) < 10:
            return results

        df = bisonfi_trades_df.sort_values(['token_pair', 'timestamp']).copy()
        price_col = 'price' if 'price' in df.columns else 'amount'

        # Vectorized pct_change per token pair via groupby transform.
        df['_change_pct'] = df.groupby('token_pair')[price_col].pct_change() * 100
        stats = df.groupby('token_pair')['_change_pct'].agg(['mean', 'std']).rename(
            columns={'mean': '_mean', 'std': '_std'}
        )
        df = df.merge(stats, left_on='token_pair', right_index=True, how='left')
        df['_z'] = (df['_change_pct'] - df['_mean']) / df['_std']
        bursts_mask = df['_change_pct'].notna() & (df['_std'] > 0) & (df['_z'].abs() > amplitude_threshold)
        bursts = df[bursts_mask][['timestamp', 'token_pair', '_change_pct', '_z']]
        results['detected_bursts'] = sorted(
            [
                {
                    'timestamp': r['timestamp'].isoformat(),
                    'token_pair': r['token_pair'],
                    'price_change_pct': float(r['_change_pct']),
                    'z_score': float(r['_z']),
                    'amplitude': abs(float(r['_z'])),
                }
                for _, r in bursts.iterrows()
            ],
            key=lambda x: x['amplitude'], reverse=True,
        )[:50]
        for token_pair, row in stats.iterrows():
            results['burst_statistics'][token_pair] = {
                'mean_change': float(row['_mean']) if pd.notna(row['_mean']) else 0.0,
                'std_change': float(row['_std']) if pd.notna(row['_std']) else 0.0,
                'num_bursts': int((bursts['token_pair'] == token_pair).sum()),
            }
        return results

    # ---- 6. Cross-protocol burst correlation ---------------------------
    def cross_protocol_burst_correlation(self, bisonfi_bursts: List[Dict],
                                         other_protocol_trades: pd.DataFrame,
                                         time_window_ms: int = 1000) -> Dict:
        results = {
            'burst_correlation_analysis': [],
            'contagion_percentage': 0.0,
            'statistical_significance': 0.0,
            'evidence_summary': {},
        }
        if not bisonfi_bursts or other_protocol_trades is None or other_protocol_trades.empty:
            return results

        df = other_protocol_trades.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        burst_df = pd.DataFrame(bisonfi_bursts)
        burst_df['timestamp'] = pd.to_datetime(burst_df['timestamp'])
        burst_df = burst_df.sort_values('timestamp').reset_index(drop=True)

        # For each attack, find the latest burst happening before it (or
        # exactly at it). searchsorted is O(log B) per attack vs the
        # original O(B) Python loop.
        burst_ts = burst_df['timestamp'].to_numpy()
        attack_ts = df['timestamp'].to_numpy()
        idx = np.searchsorted(burst_ts, attack_ts, side='right') - 1
        valid = idx >= 0
        time_lag_ms = np.full(len(df), np.nan)
        time_lag_ms[valid] = (
            (attack_ts[valid] - burst_ts[idx[valid]]).astype('timedelta64[ms]').astype(np.int64)
        )
        within_window = valid & (time_lag_ms >= 0) & (time_lag_ms <= time_window_ms)

        matched_attacks = int(within_window.sum())
        total_attacks = len(df)
        contagion_pct = matched_attacks / total_attacks * 100 if total_attacks else 0.0

        records = []
        for i in np.flatnonzero(within_window):
            burst = burst_df.iloc[idx[i]]
            attack = df.iloc[i]
            records.append({
                'attack_timestamp': attack['timestamp'].isoformat(),
                'burst_timestamp': burst['timestamp'].isoformat(),
                'time_lag_ms': float(time_lag_ms[i]),
                'burst_token_pair': burst['token_pair'],
                'burst_amplitude': float(burst['amplitude']) if 'amplitude' in burst else float(abs(burst.get('z_score', 0))),
                'attack_token_pair': attack.get('token_pair', 'unknown'),
            })
        results['contagion_percentage'] = contagion_pct
        results['matched_attacks'] = matched_attacks
        results['total_attacks_analyzed'] = total_attacks
        results['burst_correlation_analysis'] = sorted(records, key=lambda x: x['time_lag_ms'])[:100]

        if total_attacks > 0 and len(burst_df) > 0:
            burst_time_range = (burst_df['timestamp'].iloc[-1] - burst_df['timestamp'].iloc[0]).total_seconds() * 1000
            if burst_time_range > 0:
                expected_matches = total_attacks * len(burst_df) * time_window_ms / burst_time_range
                std_matches = np.sqrt(expected_matches * (1 - expected_matches / total_attacks))
                if std_matches > 0:
                    results['statistical_significance'] = float(
                        (matched_attacks - expected_matches) / std_matches
                    )

        results['evidence_summary'] = {
            'interpretation': (
                f"{contagion_pct:.1f}% of attacks on other protocols occur within "
                f"{time_window_ms}ms of BisonFi oracle bursts. "
                f"Z-score: {results['statistical_significance']:.2f} "
                f"(significant if |Z| > 2.0)"
            ),
            'contagion_confirmed': contagion_pct > 90.0 and results['statistical_significance'] > 2.0,
        }
        return results


if __name__ == "__main__":
    print("PoolCoordinationAnalyzerOptimized module loaded")
