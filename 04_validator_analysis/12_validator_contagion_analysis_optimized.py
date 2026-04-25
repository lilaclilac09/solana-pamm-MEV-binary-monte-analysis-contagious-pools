"""
Vectorized version of 12_validator_contagion_analysis.py.

Subclasses the original ``ValidatorContagionAnalyzer`` and overrides the
five hottest methods. Replaces seven separate
``for X in df['col'].unique(): df[df['col'] == X]`` scans plus two
``df.iterrows()`` loops with single ``groupby`` passes.

The original class, dataclasses, and helper methods are unchanged and
imported directly, so behaviour, output schema, and printed summaries
all match the original.
"""

from __future__ import annotations

import importlib.util
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_ORIGINAL = _HERE / "12_validator_contagion_analysis.py"
_spec = importlib.util.spec_from_file_location("vca_original", _ORIGINAL)
_orig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_orig)

ValidatorHotspot = _orig.ValidatorHotspot
ValidatorContagionAnalyzer = _orig.ValidatorContagionAnalyzer


class ValidatorContagionAnalyzerOptimized(ValidatorContagionAnalyzer):
    """Drop-in replacement for ``ValidatorContagionAnalyzer`` with
    vectorized hotspot, contagion, cross-slot, ecosystem, and graph
    methods. All printed text and return values match the original
    class on the same input.
    """

    # ---- PART 1: vectorized hotspot identification --------------------
    def identify_validator_hotspots(self, top_n: int = 20,
                                    concentration_threshold: float = 0.01
                                    ) -> Dict[str, ValidatorHotspot]:
        if self.mev_data is None:
            raise ValueError("Load MEV data first with load_mev_data()")
        df = self.mev_data
        total_mev = len(df)

        # Single groupby produces every per-validator stat; the original
        # filtered df once per validator inside a Python loop. sort=False
        # preserves first-appearance order to keep tie-breaking
        # consistent with df['validator'].unique() iteration.
        agg = df.groupby('validator', sort=False).agg(
            mev_count=('validator', 'size'),
            unique_attackers=('attacker_signer', 'nunique'),
            unique_protocols=('amm_trade', 'nunique'),
            slots_active=('slot', 'nunique') if 'slot' in df.columns else ('validator', 'size'),
        )
        if 'slot' not in df.columns:
            agg['slots_active'] = (agg['mev_count'] // np.maximum(1, agg['unique_attackers'])).astype(int)

        agg['concentration'] = agg['mev_count'] / total_mev
        agg['avg_attacks_per_slot'] = agg['mev_count'] / np.maximum(1, agg['slots_active'])
        agg['risk_level'] = np.where(
            agg['concentration'] >= concentration_threshold, 'HIGH',
            np.where(agg['concentration'] >= concentration_threshold * 0.5, 'MEDIUM', 'LOW'),
        )

        # Use stable sort so ties keep first-appearance order, matching
        # the original Python `sorted(...)` behaviour on dict items.
        agg = agg.sort_values('mev_count', ascending=False, kind='stable').head(top_n)
        validator_stats = {
            validator: ValidatorHotspot(
                validator_address=validator,
                total_mev_count=int(row['mev_count']),
                unique_attackers=int(row['unique_attackers']),
                unique_protocols=int(row['unique_protocols']),
                concentration_ratio=float(row['concentration']),
                avg_attacks_per_slot=float(row['avg_attacks_per_slot']),
                slots_active=int(row['slots_active']),
                risk_level=str(row['risk_level']),
            )
            for validator, row in agg.iterrows()
        }
        self.hotspots = validator_stats

        print(f"\n{'='*70}")
        print(f"VALIDATOR HOTSPOT ANALYSIS")
        print(f"{'='*70}")
        print(f"\nTop {len(validator_stats)} Validators by MEV Concentration:\n")
        for i, (validator, hotspot) in enumerate(validator_stats.items(), 1):
            print(f"{i:2d}. {validator[:16]}...")
            print(f"    MEV Count: {hotspot.total_mev_count:,} ({hotspot.concentration_ratio*100:.2f}%)")
            print(f"    Attackers: {hotspot.unique_attackers} | Protocols: {hotspot.unique_protocols}")
            print(f"    Avg Attacks/Slot: {hotspot.avg_attacks_per_slot:.2f} | Risk: {hotspot.risk_level}")
            print()
        return self.hotspots

    # ---- PART 2: vectorized validator-AMM contagion -------------------
    def analyze_validator_amm_contagion(self, min_shared_attacks: int = 2) -> Dict[str, Any]:
        if self.mev_data is None:
            raise ValueError("Load MEV data first")
        df = self.mev_data
        results = {
            'validator_protocol_pairs': [],
            'high_risk_combinations': [],
            'contagion_pathways': [],
            'protocol_vulnerability_clusters': [],
            'attacker_specialization': {},
        }

        # One groupby replaces a Python iterrows loop building two
        # nested defaultdicts (validator -> protocol -> count and ->
        # set of attackers).
        grouped = df.groupby(['validator', 'amm_trade'])['attacker_signer']
        attacker_sets = grouped.apply(lambda s: set(s.unique()))
        counts = grouped.size()

        validator_protocol_attackers: Dict[str, Dict[str, set]] = defaultdict(dict)
        for (validator, protocol), aset in attacker_sets.items():
            validator_protocol_attackers[validator][protocol] = aset

        all_pairs: List[Dict[str, Any]] = []
        for (validator, protocol), count in counts.items():
            attackers = validator_protocol_attackers[validator][protocol]
            unique_attackers = len(attackers)
            all_pairs.append({
                'validator': validator,
                'protocol': protocol,
                'attack_count': int(count),
                'unique_attackers': unique_attackers,
                'risk_score': int(count) * unique_attackers,
                'attackers': list(attackers),
            })

        all_pairs.sort(key=lambda x: x['risk_score'], reverse=True)
        results['validator_protocol_pairs'] = all_pairs[:50]
        results['high_risk_combinations'] = [
            p for p in all_pairs if p['attack_count'] >= min_shared_attacks
        ][:20]

        # Helpers from the original (unchanged behaviour, inherited).
        results['contagion_pathways'] = self._detect_validator_level_contagion(
            validator_protocol_attackers
        )
        results['protocol_vulnerability_clusters'] = self._identify_protocol_vulnerability_clusters(
            validator_protocol_attackers, all_pairs
        )

        print(f"\n{'='*70}")
        print(f"VALIDATOR-AMM CONTAGION ANALYSIS")
        print(f"{'='*70}")
        print(f"\nHigh-Risk Validator-Protocol Combinations:\n")
        for pair in results['high_risk_combinations'][:10]:
            print(f"  {pair['validator'][:16]}... + {pair['protocol']}")
            print(f"    Attacks: {pair['attack_count']} | Unique Bots: {pair['unique_attackers']} | Risk: {pair['risk_score']}")
            print()
        print(f"\nDetected {len(results['contagion_pathways'])} Contagion Pathways")
        print(f"Identified {len(results['protocol_vulnerability_clusters'])} Vulnerability Clusters\n")
        return results

    # ---- PART 3: vectorized cross-slot pattern detection --------------
    def detect_cross_slot_patterns(self, slot_duration_ms: int = 400,
                                   time_column: str = 'ms_time') -> Dict[str, Any]:
        if self.mev_data is None:
            raise ValueError("Load MEV data first")
        df = self.mev_data
        if 'slot' not in df.columns or time_column not in df.columns:
            print("⚠ Warning: 'slot' or time column not available for cross-slot analysis")
            print("  (Analysis will be skipped)")
            return {'status': 'unavailable', 'reason': 'Missing slot or time columns'}

        results = {
            'multi_slot_attackers': [],
            'cross_slot_sandwiches': [],
            'slot_boundary_exploits': [],
            'temporal_attack_clusters': [],
        }

        # Single groupby gives sorted slot list per attacker; original
        # filtered the df once per attacker.
        slots_per_attacker = (
            df.groupby('attacker_signer')['slot']
            .apply(lambda s: sorted(s.unique()))
        )
        cross_slot_trades: List[Dict[str, Any]] = []
        for attacker, slot_list in slots_per_attacker.items():
            if len(slot_list) < 2:
                continue
            count = (df['attacker_signer'] == attacker).sum()
            if count < 3:
                continue
            for i in range(len(slot_list) - 1):
                gap = slot_list[i + 1] - slot_list[i]
                if gap <= 3:
                    cross_slot_trades.append({
                        'attacker': attacker,
                        'slot_sequence': [slot_list[i], slot_list[i + 1]],
                        'slot_gap': int(gap),
                        'attack_type': 'potential_2fast_bot',
                    })
        results['multi_slot_attackers'] = cross_slot_trades[:50]

        if 'fat_sandwich' in df.columns:
            fat = df[df['fat_sandwich'] == True]
            fat_grouped = fat.groupby('attacker_signer').agg(
                slots=('slot', lambda s: sorted(s.unique())),
                count=('slot', 'size'),
                protocols=('amm_trade', lambda s: list(s.unique())),
            )
            for attacker, row in fat_grouped.iterrows():
                if len(row['slots']) > 1:
                    results['cross_slot_sandwiches'].append({
                        'attacker': attacker,
                        'slots_involved': row['slots'],
                        'fat_sandwich_count': int(row['count']),
                        'protocols': row['protocols'],
                    })

        # Boundary exploits: vectorize the per-slot time normalization
        # via groupby().transform('min').
        df_slot = df[['slot', time_column, 'attacker_signer', 'amm_trade']].copy()
        df_slot['time_in_slot'] = df_slot[time_column] - df_slot.groupby('slot')[time_column].transform('min')
        boundary_mask = df_slot['time_in_slot'] > slot_duration_ms * 0.9
        if boundary_mask.any():
            boundary = df_slot[boundary_mask].groupby('slot').agg(
                boundary_trades=('attacker_signer', 'size'),
                attackers=('attacker_signer', 'nunique'),
                protocols=('amm_trade', 'nunique'),
            ).reset_index()
            boundary_list = [
                {
                    'slot': int(r['slot']),
                    'boundary_trades': int(r['boundary_trades']),
                    'attackers': int(r['attackers']),
                    'protocols': int(r['protocols']),
                }
                for _, r in boundary.iterrows()
            ]
            results['slot_boundary_exploits'] = sorted(
                boundary_list, key=lambda x: x['boundary_trades'], reverse=True
            )[:20]

        print(f"\n{'='*70}")
        print(f"CROSS-SLOT PATTERN DETECTION (2Fast Bot Analysis)")
        print(f"{'='*70}")
        print(f"\nMulti-Slot Attacker Patterns: {len(results['multi_slot_attackers'])}")
        print(f"Cross-Slot Fat Sandwiches: {len(results['cross_slot_sandwiches'])}")
        print(f"Slot Boundary Exploits: {len(results['slot_boundary_exploits'])}\n")
        return results

    # ---- PART 4: vectorized bot ecosystem mapping ---------------------
    def map_bot_ecosystem(self, top_n_bots: int = 50) -> Dict[str, Any]:
        if self.mev_data is None:
            raise ValueError("Load MEV data first")
        df = self.mev_data

        results = {
            'bot_count': 0,
            'top_bots': [],
            'bot_specialization_matrix': [],
            'validator_targeting': [],
            'infrastructure_indicators': {},
            'ecosystem_summary': {},
        }

        attack_type_cols = [c for c in ('sandwich', 'front_running', 'back_running', 'fat_sandwich')
                            if c in df.columns]
        has_confidence = 'confidence' in df.columns
        has_profit = 'net_profit_sol' in df.columns

        agg_kwargs: Dict[str, tuple] = {
            'attack_count': ('attacker_signer', 'size'),
            'unique_validators': ('validator', 'nunique'),
            'unique_protocols': ('amm_trade', 'nunique'),
        }
        for col in attack_type_cols:
            agg_kwargs[col] = (col, 'sum')
        if has_profit:
            agg_kwargs['total_profit_sol'] = ('net_profit_sol', 'sum')
            agg_kwargs['avg_profit_sol'] = ('net_profit_sol', 'mean')
        bot_df = df.groupby('attacker_signer').agg(**agg_kwargs)

        if has_confidence:
            conf = pd.to_numeric(df['confidence'], errors='coerce')
            mean_conf = conf.groupby(df['attacker_signer']).mean().fillna(0.5)
            bot_df['success_rate'] = mean_conf
        else:
            bot_df['success_rate'] = 0.5

        # Timing precision needs the full bot frame; original called a
        # helper per bot. Compute in one pass via groupby std.
        if 'time_diff_ms' in df.columns:
            std = df.groupby('attacker_signer')['time_diff_ms'].std().fillna(0)
            precision = (1.0 / (1.0 + std / 10.0)) * 100.0
            bot_df['timing_precision'] = precision.clip(upper=100)
            bot_df['timing_precision'] = bot_df['timing_precision'].fillna(50)
        else:
            bot_df['timing_precision'] = 50.0

        bot_df['infrastructure_score'] = (
            (bot_df['timing_precision'] / 100.0) * 3.0
            + bot_df['success_rate'] * 4.0
            + np.minimum(bot_df['unique_validators'] / 50.0, 1.0) * 3.0
        )

        # Preferred validators / protocols (top 5 each). Build via
        # groupby iteration -- Series.apply auto-unpacks dict returns.
        preferred_validators: Dict[str, Dict[str, int]] = {}
        preferred_protocols: Dict[str, Dict[str, int]] = {}
        for bot, group in df.groupby('attacker_signer'):
            preferred_validators[bot] = dict(group['validator'].value_counts().head(5))
            preferred_protocols[bot] = dict(group['amm_trade'].value_counts().head(5))

        # Build the bot_stats dict the helper methods expect.
        bot_stats: Dict[str, Dict[str, Any]] = {}
        for bot, row in bot_df.iterrows():
            attack_types = {col: int(row[col]) for col in attack_type_cols}
            bot_stats[bot] = {
                'attack_count': int(row['attack_count']),
                'unique_validators': int(row['unique_validators']),
                'unique_protocols': int(row['unique_protocols']),
                'attack_types': attack_types,
                'success_rate': float(row['success_rate']),
                'total_profit_sol': float(row['total_profit_sol']) if has_profit else 0.0,
                'avg_profit_sol': float(row['avg_profit_sol']) if has_profit else 0.0,
                'timing_precision': float(row['timing_precision']),
                'infrastructure_score': float(row['infrastructure_score']),
                'preferred_validators': preferred_validators.get(bot, {}),
                'preferred_protocols': preferred_protocols.get(bot, {}),
            }
        results['bot_count'] = len(bot_stats)

        top_bots_list = sorted(
            bot_stats.items(), key=lambda x: x[1]['attack_count'], reverse=True
        )[:top_n_bots]
        results['top_bots'] = [
            {
                'bot': bot,
                'attack_count': stats['attack_count'],
                'validators': stats['unique_validators'],
                'protocols': stats['unique_protocols'],
                'success_rate': stats['success_rate'],
                'infrastructure_score': stats['infrastructure_score'],
                'total_profit_sol': stats['total_profit_sol'],
            }
            for bot, stats in top_bots_list
        ]
        results['bot_specialization_matrix'] = self._analyze_bot_specialization(bot_stats)
        results['validator_targeting'] = self._analyze_bot_validator_targeting(df, top_bots_list)

        precision_scores = bot_df['timing_precision'].to_numpy()
        infra_scores = bot_df['infrastructure_score'].to_numpy()
        results['infrastructure_indicators'] = {
            'mean_timing_precision_ms': float(np.mean(precision_scores)),
            'min_timing_precision_ms': float(np.min(precision_scores)),
            'max_timing_precision_ms': float(np.max(precision_scores)),
            'mean_infrastructure_score': float(np.mean(infra_scores)),
            'high_quality_bots': int(np.sum(infra_scores > 0.7)),
        }

        print(f"\n{'='*70}")
        print(f"BOT ECOSYSTEM MAPPING")
        print(f"{'='*70}")
        print(f"\nTotal Unique Bots: {results['bot_count']}")
        print(f"High-Infrastructure Bots (score > 0.7): {results['infrastructure_indicators']['high_quality_bots']}")
        print(f"Mean Timing Precision: {results['infrastructure_indicators']['mean_timing_precision_ms']:.2f}ms")
        print(f"\nTop 10 Bots by Activity:\n")
        for i, info in enumerate(results['top_bots'][:10], 1):
            print(f"{i:2d}. {info['bot'][:16]}...")
            print(f"    Attacks: {info['attack_count']} | Validators: {info['validators']} | Protocols: {info['protocols']}")
            print(f"    Success Rate: {info['success_rate']:.2%} | Infrastructure: {info['infrastructure_score']:.2f}")
            print()
        return results

    # ---- export_contagion_graph: vectorize iterrows() at line 990 -----
    def export_contagion_graph(self, output_file: str = 'validator_contagion_graph.json'):
        if not self.hotspots:
            print("⚠ No hotspots analyzed. Run identify_validator_hotspots() first.")
            return

        graph_data: Dict[str, Any] = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'total_validators_analyzed': len(self.hotspots),
                'total_records': len(self.mev_data) if self.mev_data is not None else 0,
            },
        }

        for validator, hotspot in self.hotspots.items():
            graph_data['nodes'].append({
                'id': validator,
                'type': 'validator',
                'mev_count': hotspot.total_mev_count,
                'concentration': hotspot.concentration_ratio,
                'risk_level': hotspot.risk_level,
            })

        if self.mev_data is not None:
            # Replace iterrows() with one groupby producing the
            # validator -> set(attackers) map directly.
            validator_attackers: Dict[str, set] = (
                self.mev_data.groupby('validator')['attacker_signer']
                .apply(lambda s: set(s.unique()))
                .to_dict()
            )
            validators = list(self.hotspots.keys())
            for i, v1 in enumerate(validators):
                a1 = validator_attackers.get(v1, set())
                for v2 in validators[i + 1:]:
                    a2 = validator_attackers.get(v2, set())
                    shared = a1 & a2
                    if shared:
                        graph_data['edges'].append({
                            'source': v1,
                            'target': v2,
                            'shared_attackers': len(shared),
                            'strength': len(shared) / max(len(a1), len(a2)),
                        })

        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        print(f"✓ Exported contagion graph to {output_file}")
        return graph_data


def main():
    analyzer = ValidatorContagionAnalyzerOptimized()
    analyzer.load_mev_data('02_mev_detection/filtered_output/per_pamm_all_mev_with_validator.csv')
    t0 = time.perf_counter()
    hotspots = analyzer.identify_validator_hotspots(top_n=15)
    contagion = analyzer.analyze_validator_amm_contagion()
    cross_slot = analyzer.detect_cross_slot_patterns()
    ecosystem = analyzer.map_bot_ecosystem(top_n_bots=50)
    mitigations = analyzer.generate_mitigation_recommendations()
    analyzer.export_contagion_graph(
        '04_validator_analysis/validator_contagion_graph_optimized.json'
    )
    summary = analyzer.generate_summary_report()
    elapsed = time.perf_counter() - t0
    print(f"\n[optimized] total time: {elapsed*1000:.0f} ms")
    return {
        'hotspots': hotspots,
        'contagion': contagion,
        'cross_slot': cross_slot,
        'ecosystem': ecosystem,
        'mitigations': mitigations,
        'summary': summary,
    }


if __name__ == '__main__':
    main()
