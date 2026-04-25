#!/usr/bin/env python3
"""
Vectorized version of 02_mev_detection/fat_sandwich_detector_fast.py.

The original detects "A-B-A" sandwich patterns with a triple-nested
``for idx in range(...)`` Python loop inside an outer per-time-window
``for time_group in unique()`` loop -- an O(W * N^3) scan over the
sampled trades. On the typical 10% sample (~50-100k rows that's
seconds to minutes in pandas; on the full data it's prohibitive.

This optimized port replaces the inner triple loop with a single
self-join + cumulative-sum trick:

  1. Sort each (window_sec, time_group) and number rows.
  2. Self-merge by (time_group, signer) to enumerate every same-signer
     pair of trades. Filter to ordered pairs with reversed token
     pairs.
  3. For each surviving (i, k, signer) triple, count the number of
     differing-signer rows between i and k via a per-(time_group)
     cumulative-sum lookup -- O(1) per pair after O(N) prep.
  4. Each (i, k, signer) emits one sandwich record per differing-
     signer middle row, exactly matching the original's nested loop
     emission semantics. victim_count == k - i - 1 (preserved as in
     the original).

Output schema, classification logic and CSV path are unchanged.

NOTE: Like pamm_cross_comparison_analysis_optimized.py, this could
not be timed in the sandbox because
01_data_cleaning/outputs/pamm_clean_final.parquet (~300 MB) is
gitignored. Verify locally with
02_mev_detection/verify_fat_sandwich_detector.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

print("\n" + "=" * 80)
print("FAT SANDWICH DETECTOR - SAMPLED VERSION (10% of data)  [OPTIMIZED]")
print("=" * 80)

# ---- Load -----------------------------------------------------------------
print("\n📂 Loading data...")
try:
    df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
    df_trades = df_clean[df_clean['kind'] == 'TRADE'].copy()
    print(f"✓ Loaded {len(df_trades):,} trade events")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    sys.exit(1)

# Sample 10% (same seed as original for parity)
sample_size = max(10000, int(len(df_trades) * 0.1))
df_sample = (
    df_trades.sample(n=min(sample_size, len(df_trades)), random_state=42)
    .sort_values('ms_time')
    .reset_index(drop=True)
)
print(f"✓ Sampled {len(df_sample):,} trades for analysis")
print(f"\nColumns available: {list(df_sample.columns)[:10]}...")

print("\n" + "=" * 80)
print("DATA SUMMARY")
print("=" * 80)
print(f"Time range: {df_sample['ms_time'].min()} - {df_sample['ms_time'].max()}")
print(f"Unique signers: {df_sample['signer'].nunique():,}")
print(f"Unique slots: {df_sample['slot'].nunique():,}")
if 'amm_trade' in df_sample.columns:
    print(f"Unique pools: {df_sample['amm_trade'].nunique():,}")


# ---- Vectorized A-B-A detection ------------------------------------------
def detect_aba_for_window(df: pd.DataFrame, window_sec: int) -> pd.DataFrame:
    """Vectorized replacement for the original's triple-nested loop."""
    window_ms = window_sec * 1000
    work = df.copy()
    work['time_group'] = (work['ms_time'] // window_ms).astype(np.int64)
    # Numbering within each time_group keeps the i < k ordering check
    # cheap (positional, not timestamp-based).
    work['_pos'] = work.groupby('time_group').cumcount()

    # If there are no required token columns, no emissions (matches
    # original behaviour: it only emits when from_token/to_token exist).
    if 'from_token' not in work.columns or 'to_token' not in work.columns:
        return pd.DataFrame()

    # Self-merge by (time_group, signer) -> every same-signer pair within
    # a time group. Suffix _a / _b distinguish the two halves.
    cols = ['time_group', 'signer', '_pos', 'ms_time', 'slot',
            'from_token', 'to_token']
    a = work[cols].rename(columns={
        '_pos': 'i', 'ms_time': 'ms_i', 'slot': 'slot_i',
        'from_token': 'from_a', 'to_token': 'to_a',
    })
    b = work[cols].rename(columns={
        '_pos': 'k', 'ms_time': 'ms_k', 'slot': 'slot_k',
        'from_token': 'from_b', 'to_token': 'to_b',
    })
    pairs = a.merge(b, on=['time_group', 'signer'])
    pairs = pairs[pairs['i'] < pairs['k']]
    pairs = pairs[(pairs['from_a'] == pairs['to_b']) & (pairs['to_a'] == pairs['from_b'])]
    if pairs.empty:
        return pd.DataFrame()

    # Count "different-signer" rows strictly between positions i and k
    # within the same time group via per-group cumulative sum:
    #   diff_count(i, k, sig) = (k - i - 1)
    #                         - (cum_same_sig[k] - cum_same_sig[i+1])
    # because cum_same_sig[k]-cum_same_sig[i+1] gives the number of
    # rows in (i+1, k] that share `sig`; subtract one if position k
    # itself shares the signer (it does by construction), giving the
    # count over (i, k).
    work = work.sort_values(['time_group', '_pos'])
    pivot = pd.crosstab(
        index=[work['time_group'], work['_pos']],
        columns=work['signer'],
    )
    # Cumulative sum per time_group along _pos for every signer.
    pivot_cs = pivot.groupby(level='time_group').cumsum()

    # Look up cum_same[i+1] and cum_same[k] for every pair.
    # We use the wide-format pivot so the column is the signer.
    def _lookup(positions: pd.Series, sig: pd.Series) -> np.ndarray:
        # Build a MultiIndex per row and gather; non-existent (tg,pos)
        # rows mean position 0 (no occurrences yet) so we reindex.
        idx = pd.MultiIndex.from_arrays([pairs['time_group'].values, positions.values])
        rows = pivot_cs.reindex(idx).fillna(0)
        return rows.values[np.arange(len(rows)), pivot_cs.columns.get_indexer(sig.values)]

    cum_at_kp1 = _lookup(pairs['k'], pairs['signer'])  # cum at position k
    # cum at position i (NOT i+1, because pivot_cs[i] already excludes j=i+1)
    # We want count of `sig` in positions (i, k]: cum[k] - cum[i].
    cum_at_i = _lookup(pairs['i'], pairs['signer'])
    same_sig_in_open_kclosed = cum_at_kp1 - cum_at_i  # includes k itself
    # Strictly between i and k (open both sides) excludes position k:
    same_sig_in_between = same_sig_in_open_kclosed - 1
    diff_sig_in_between = (pairs['k'].values - pairs['i'].values - 1) - same_sig_in_between

    pairs = pairs.assign(diff_count=diff_sig_in_between)
    pairs = pairs[pairs['diff_count'] > 0]
    if pairs.empty:
        return pd.DataFrame()

    # Replicate each pair by diff_count to mirror the original's
    # emit-per-mid-row semantics. victim_count is always k - i - 1.
    pairs = pairs.loc[pairs.index.repeat(pairs['diff_count'].astype(int))]
    pairs = pairs.assign(
        window_sec=window_sec,
        attacker_signer=pairs['signer'],
        victim_count=pairs['k'] - pairs['i'] - 1,
        trades_in_pattern=3,
        time_span_ms=pairs['ms_k'] - pairs['ms_i'],
        slot_range=pairs['slot_i'].astype(str) + '-' + pairs['slot_k'].astype(str),
    )
    pairs['confidence'] = np.where(pairs['victim_count'] >= 1, 'HIGH', 'MEDIUM')
    return pairs[['window_sec', 'attacker_signer', 'victim_count',
                  'trades_in_pattern', 'time_span_ms', 'slot_range', 'confidence']]


print("\n" + "=" * 80)
print("DETECTING FAT SANDWICH PATTERNS (A-B-A) [VECTORIZED]")
print("=" * 80)

window_seconds_list = [1, 2, 5, 10]
collected = []
for window_sec in window_seconds_list:
    found = detect_aba_for_window(df_sample, window_sec)
    collected.append(found)
sandwiches_df = (
    pd.concat(collected, ignore_index=True) if collected else pd.DataFrame()
)

print(f"\n✓ Total patterns detected: {len(sandwiches_df):,}")

if len(sandwiches_df) > 0:
    print("\nBy window size:")
    for window in window_seconds_list:
        count = int((sandwiches_df['window_sec'] == window).sum())
        pct = 100 * count / len(sandwiches_df) if len(sandwiches_df) > 0 else 0
        print(f"  {window}s window: {count:,} ({pct:.1f}%)")

    print("\nBy confidence level:")
    cc = sandwiches_df['confidence'].value_counts()
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        if level in cc.index:
            count = int(cc[level])
            pct = 100 * count / len(sandwiches_df)
            print(f"  {level}: {count:,} ({pct:.1f}%)")

    print("\nVictim statistics:")
    print(f"  Mean victims per sandwich: {sandwiches_df['victim_count'].mean():.2f}")
    print(f"  Max victims in single pattern: {sandwiches_df['victim_count'].max()}")
    print(f"  Median time span: {sandwiches_df['time_span_ms'].median():.0f}ms")


# ---- Classification (unchanged from original) -----------------------------
print("\n" + "=" * 80)
print("CLASSIFICATION: FAT SANDWICH vs MULTI-HOP ARBITRAGE")
print("=" * 80)


def classify_attack(row):
    victim_count = row.get('victim_count', 0)
    time_span = row.get('time_span_ms', 0)
    fat = 0
    multi = 0
    if victim_count >= 2:
        fat += 50
    elif victim_count == 1:
        fat += 25
    if time_span < 2000:
        fat += 30
    elif time_span > 5000:
        multi += 30
    if fat > multi:
        return 'fat_sandwich'
    if multi > fat:
        return 'multi_hop_arbitrage'
    return 'ambiguous'


if len(sandwiches_df) > 0:
    sandwiches_df['attack_type'] = sandwiches_df.apply(classify_attack, axis=1)
    print("\nClassification results:")
    cc = sandwiches_df['attack_type'].value_counts()
    total = len(sandwiches_df)
    for at in ['fat_sandwich', 'multi_hop_arbitrage', 'ambiguous']:
        if at in cc.index:
            n = int(cc[at])
            print(f"  ✓ {at}: {n:,} ({100*n/total:.1f}%)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
if len(sandwiches_df) > 0:
    print(f"""
Dataset analyzed:
  - Trade events: {len(df_sample):,} (10% sample)
  - Time range: {df_sample['ms_time'].min()} - {df_sample['ms_time'].max()}
  - Unique signers: {df_sample['signer'].nunique():,}

Detection results:
  - Patterns detected: {len(sandwiches_df):,}
  - Detection rate: {100 * len(sandwiches_df) / len(df_sample):.3f}% of trades

Confidence distribution:
  - HIGH confidence: {int((sandwiches_df['confidence']=='HIGH').sum()):,}
  - MEDIUM confidence: {int((sandwiches_df['confidence']=='MEDIUM').sum()):,}

Key metrics:
  - Avg victim count per pattern: {sandwiches_df['victim_count'].mean():.2f}
  - Median time span: {sandwiches_df['time_span_ms'].median():.0f}ms
  - Mode window size: {sandwiches_df['window_sec'].mode().iat[0]}s
""")
else:
    print("No patterns detected.")

# Save to a sibling file so the original output is preserved.
out_dir = Path('outputs')
out_dir.mkdir(exist_ok=True)
output_file = out_dir / 'fat_sandwich_detection_sample_results_optimized.csv'
if len(sandwiches_df) > 0:
    sandwiches_df.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to {output_file}")

print("\n" + "=" * 80)
print("✅ DETECTION COMPLETE (OPTIMIZED)")
print("=" * 80 + "\n")
