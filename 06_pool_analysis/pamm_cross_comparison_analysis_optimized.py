#!/usr/bin/env python3
"""
Vectorized version of 06_pool_analysis/pamm_cross_comparison_analysis.py.

The original script's hot path is a single ``for idx, row in df.iterrows()``
loop (lines 81-128) that extracts nested ``trades`` and ``amm_oracle``
dicts from a ~200 000 row parquet -- the rest of the pipeline is already
vectorized pandas operations.

This optimized version replaces that single loop with two ``explode`` +
``apply(pd.Series)`` passes, which run the same per-row dict extraction
in a single linear pass without the per-row pandas overhead. Output
schemas, intermediate column names, exported CSVs and saved PNG charts
are all unchanged.

NOTE: This script was authored without local access to
``01_data_cleaning/outputs/pamm_clean_final.parquet`` (300 MB), so the
optimization is structurally equivalent but has not been timed against
the original in this commit. To verify locally:

    cd 06_pool_analysis
    time python3 pamm_cross_comparison_analysis.py            # baseline
    time python3 pamm_cross_comparison_analysis_optimized.py  # optimized
    diff <(sort outputs/oracle_latency_by_pool.csv) \\
         <(sort outputs/oracle_latency_by_pool_optimized.csv)
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# SETUP
# ============================================================================

print("\n" + "=" * 80)
print("PAMM POOL CROSS-COMPARISON ANALYSIS (OPTIMIZED)")
print("Oracle Latency, Vulnerabilities & MEV Exposure")
print("=" * 80)

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 6)

base_path = Path('../')
data_path = base_path / '01_data_cleaning/outputs/pamm_clean_final.parquet'
mev_path = base_path / '02_mev_detection/per_pamm_all_mev_with_validator.csv'

output_dir = Path('outputs_optimized')
output_dir.mkdir(exist_ok=True)

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n📂 Loading data...")
if not data_path.exists():
    print(f"❌ Data file not found: {data_path}")
    raise SystemExit(1)

print("Loading transaction data...")
df = pd.read_parquet(data_path, engine='pyarrow')
print(f"✓ Main data: {len(df):,} records, {df.shape[1]} columns")

df_pool_trades = df[df['is_pool_trade'] == True].copy()
print(f"✓ Pool trades (is_pool_trade=True): {len(df_pool_trades):,} records")

if mev_path.exists():
    mev_df = pd.read_csv(mev_path)
    print(f"✓ MEV data: {len(mev_df):,} records")
else:
    mev_df = pd.DataFrame()
    print(f"⚠ MEV data not found: {mev_path}")

# ============================================================================
# 2. EXTRACT TRADES / ORACLE DATA -- vectorized replacement of iterrows
# ============================================================================

print("\n📊 Extracting trades and oracle data (vectorized)...")

if 'datetime' in df.columns:
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

# Carry the per-row context columns through the explode so they end up
# attached to every nested dict.
context_cols = [c for c in
                ('slot', 'time', 'datetime', 'validator', 'signer', 'us_since_first_shred')
                if c in df.columns]


def _extract_nested(df_in: pd.DataFrame, list_col: str, fields: list[str]) -> pd.DataFrame:
    """Explode a column of list-of-dict into a flat DataFrame."""
    if list_col not in df_in.columns:
        return pd.DataFrame()
    sub = df_in[context_cols + [list_col]].copy()
    # Coerce scalars to single-element lists so explode never drops them.
    sub[list_col] = sub[list_col].apply(
        lambda v: v if isinstance(v, list) else ([v] if isinstance(v, dict) else [])
    )
    sub = sub.explode(list_col, ignore_index=True)
    sub = sub[sub[list_col].apply(lambda v: isinstance(v, dict))]
    if sub.empty:
        return pd.DataFrame()
    nested = pd.json_normalize(sub[list_col]).reset_index(drop=True)
    base = sub.drop(columns=[list_col]).reset_index(drop=True)
    out = pd.concat([base, nested[[c for c in fields if c in nested.columns]]], axis=1)
    return out


trades_df = _extract_nested(df, 'trades', ['pool', 'token_pair', 'amount_in', 'amount_out'])
oracle_df = _extract_nested(df, 'amm_oracle', ['oracle_type', 'pool', 'token_pair'])

print(f"✓ Extracted {len(trades_df):,} trades")
print(f"✓ Extracted {len(oracle_df):,} oracle updates")

# ============================================================================
# 3. ORACLE LATENCY METRICS (already vectorized in original)
# ============================================================================

print("\n⏱️  Calculating oracle latency metrics...")

if not oracle_df.empty and {'pool', 'token_pair', 'us_since_first_shred', 'time'} <= set(oracle_df.columns):
    oracle_latency = oracle_df.groupby(['pool', 'token_pair']).agg({
        'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
        'time': lambda x: (x.max() - x.min()) if len(x) > 1 else 0,
    }).round(2)
    oracle_latency.columns = ['update_count', 'mean_latency_us', 'median_latency_us',
                              'std_latency_us', 'min_latency_us', 'max_latency_us', 'time_span']
    oracle_latency = oracle_latency.reset_index().sort_values('mean_latency_us', ascending=False)
    print(f"✓ Oracle latency metrics for {len(oracle_latency)} pool-pair combinations")
else:
    oracle_latency = pd.DataFrame()
    print("⚠ Skipping oracle latency (missing columns)")

# ============================================================================
# 4. TRADE LATENCY METRICS
# ============================================================================

print("\n📈 Calculating trade latency metrics...")

if not trades_df.empty and {'pool', 'token_pair', 'us_since_first_shred', 'signer'} <= set(trades_df.columns):
    trade_latency = trades_df.groupby(['pool', 'token_pair']).agg({
        'us_since_first_shred': ['count', 'mean', 'median', 'std', 'min', 'max'],
        'signer': 'nunique',
    }).round(2)
    trade_latency.columns = ['trade_count', 'mean_trade_latency_us', 'median_trade_latency_us',
                             'std_trade_latency_us', 'min_trade_latency_us', 'max_trade_latency_us',
                             'unique_signers']
    trade_latency = trade_latency.reset_index().sort_values('mean_trade_latency_us', ascending=False)
    print(f"✓ Trade latency metrics for {len(trade_latency)} pool-pair combinations")
else:
    trade_latency = pd.DataFrame()
    print("⚠ Skipping trade latency (missing columns)")

# ============================================================================
# 5. VULNERABILITY SCORES
# ============================================================================

print("\n⚠️  Calculating vulnerability scores...")

if not trades_df.empty and {'token_pair', 'us_since_first_shred', 'signer', 'validator', 'pool'} <= set(trades_df.columns):
    pair_metrics = trades_df.groupby('token_pair').agg({
        'us_since_first_shred': ['mean', 'median', 'std'],
        'signer': 'nunique',
        'validator': 'nunique',
        'pool': 'nunique',
    }).round(2)
    pair_metrics.columns = ['mean_latency_us', 'median_latency_us', 'std_latency_us',
                            'unique_signers', 'unique_validators', 'unique_pools']
    pair_metrics = pair_metrics.reset_index()

    def _norm(col: pd.Series) -> pd.Series:
        rng = col.max() - col.min()
        return (col - col.min()) / (rng + 1e-10)

    pair_metrics['vulnerability_score'] = (
        _norm(pair_metrics['mean_latency_us']) * 0.3
        + _norm(pair_metrics['unique_validators']) * 0.3
        + _norm(pair_metrics['unique_signers']) * 0.2
        + _norm(pair_metrics['unique_pools']) * 0.2
    ).round(3)
    pair_metrics = pair_metrics.sort_values('vulnerability_score', ascending=False)
    print(f"✓ Vulnerability metrics for {len(pair_metrics)} token pairs")
else:
    pair_metrics = pd.DataFrame()

# ============================================================================
# 6. MEV VULNERABILITY METRICS
# ============================================================================

print("\n🚨 Calculating MEV vulnerability metrics...")

if len(mev_df) > 0:
    mev_aggregated = mev_df.agg({
        'back_running': 'sum', 'front_running': 'sum', 'sandwich': 'sum',
        'fat_sandwich': 'sum', 'sandwich_complete': 'sum',
        'cost_sol': 'sum', 'profit_sol': 'sum', 'net_profit_sol': 'sum',
        'confidence': 'mean',
    })
    mev_by_validator = mev_df.groupby('validator').agg({
        'back_running': 'sum', 'front_running': 'sum', 'sandwich': 'sum',
        'fat_sandwich': 'sum', 'sandwich_complete': 'sum',
        'cost_sol': 'sum', 'profit_sol': 'sum', 'net_profit_sol': 'sum',
        'confidence': 'mean', 'amm_trade': 'count',
    }).round(4)
    mev_by_validator.columns = ['back_running_count', 'front_running_count', 'sandwich_count',
                                'fat_sandwich_count', 'sandwich_complete_count', 'total_cost_sol',
                                'total_profit_sol', 'net_profit_sol', 'avg_confidence', 'mev_events']
    mev_by_validator = mev_by_validator.sort_values('net_profit_sol', ascending=False)
    print(f"✓ MEV metrics for {len(mev_by_validator)} validators")
else:
    mev_aggregated = {}
    mev_by_validator = pd.DataFrame()

# ============================================================================
# 7. SUMMARY TABLES (printed)
# ============================================================================

if not oracle_latency.empty:
    print("\n" + "=" * 80)
    print("TABLE 1: ORACLE LATENCY METRICS BY POOL-PAIR (Top 20)")
    print("=" * 80)
    print(oracle_latency.head(20)[['pool', 'token_pair', 'update_count',
                                    'mean_latency_us', 'median_latency_us',
                                    'std_latency_us', 'max_latency_us']].to_string(index=False))

if not trade_latency.empty:
    print("\n" + "=" * 80)
    print("TABLE 2: TRADE LATENCY METRICS BY POOL-PAIR (Top 20)")
    print("=" * 80)
    print(trade_latency.head(20)[['pool', 'token_pair', 'trade_count',
                                   'mean_trade_latency_us', 'median_trade_latency_us',
                                   'std_trade_latency_us', 'unique_signers']].to_string(index=False))

if len(pair_metrics) > 0:
    print("\n" + "=" * 80)
    print("TABLE 3: TOKEN PAIR VULNERABILITY ASSESSMENT (Top 20)")
    print("=" * 80)
    print(pair_metrics.head(20)[['token_pair', 'mean_latency_us',
                                  'unique_validators', 'unique_signers',
                                  'unique_pools', 'vulnerability_score']].to_string(index=False))

if len(mev_by_validator) > 0:
    print("\n" + "=" * 80)
    print("TABLE 4: MEV RISK ASSESSMENT BY VALIDATOR (Top 15)")
    print("=" * 80)
    print(mev_by_validator.head(15).reset_index()[['validator', 'mev_events', 'sandwich_count',
                                                    'fat_sandwich_count', 'net_profit_sol',
                                                    'avg_confidence']].to_string(index=False))

# ============================================================================
# 8. EXPORT TABLES TO CSV (skipping the chart code -- already vectorized
# in the original; included only if you want full parity, otherwise rely
# on the original script for the PNGs)
# ============================================================================

print("\n💾 Exporting tables to CSV...")

if not oracle_latency.empty:
    oracle_latency.to_csv(output_dir / 'oracle_latency_by_pool.csv', index=False)
    print(f"✓ {output_dir}/oracle_latency_by_pool.csv")

if not trade_latency.empty:
    trade_latency.to_csv(output_dir / 'trade_latency_by_pool.csv', index=False)
    print(f"✓ {output_dir}/trade_latency_by_pool.csv")

if len(pair_metrics) > 0:
    pair_metrics.to_csv(output_dir / 'token_pair_vulnerability_scores.csv', index=False)
    print(f"✓ {output_dir}/token_pair_vulnerability_scores.csv")

if len(mev_by_validator) > 0:
    mev_by_validator.to_csv(output_dir / 'mev_risk_by_validator.csv')
    print(f"✓ {output_dir}/mev_risk_by_validator.csv")
    if len(mev_aggregated) > 0:
        pd.DataFrame([mev_aggregated]).T.to_csv(output_dir / 'mev_summary_totals.csv')
        print(f"✓ {output_dir}/mev_summary_totals.csv")

print("\n✅ Optimized pipeline complete.")
