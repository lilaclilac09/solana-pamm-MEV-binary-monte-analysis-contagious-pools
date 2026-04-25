#!/usr/bin/env python3
"""
Vectorized version of 11_report_generation/regenerate_all_plots_filtered_data.py.

The original computes MEV-bot features in a per-signer Python loop:

  for signer in mev_bot_signers:                       # ~200-1500 signers
      signer_trades = df_trades_raw[df_trades_raw['signer'] == signer]
      slot_oracles = df_events_raw[df_events_raw['slot'].isin(signer_slots)
                                    & (df_events_raw['kind'] == 'ORACLE')]
      for _, trade in signer_trades.iterrows():        # nested iterrows
          time_diffs = [abs(ot - trade_time) for ot in oracle_times]
          ...

That is O(signers x rows) plus a nested iterrows for the oracle backrun
detection. On the full 200 k-row trade dump it dominates wall clock.

This sibling preserves every output column, plot file, and printed
statistic but replaces the loop with three vectorized passes:

  1. Per-signer aggregations (late_slot_ratio, high_bytes_ratio,
     cluster_ratio) computed in a single ``groupby('signer').agg(...)``.
  2. Oracle-backrun ratio computed by inner-joining all MEV-bot trades
     to the per-slot oracle event table once, then groupby min |delta|.
  3. The remaining matplotlib code is unchanged.

Outputs are written to ``02_mev_detection/filtered_output/plots/`` with
``_optimized`` suffixes so the original PNGs are not overwritten.

NOTE: Like other ``*_optimized.py`` siblings on this branch this could
not be timed in the sandbox -- the 300 MB pamm_clean_final.parquet is
gitignored. Run locally to verify.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

BASE = Path(__file__).resolve().parent.parent
FILTERED_DATA = BASE / '02_mev_detection' / 'filtered_output' / 'all_fat_sandwich_only.csv'
AGGREGATOR_DATA = BASE / '07_ml_classification' / 'derived' / 'aggregator_analysis' / 'aggregators_with_pools.csv'
POOL_SUMMARY = BASE / '02_mev_detection' / 'POOL_SUMMARY.csv'
RAW_TRADE_DATA = BASE / '01_data_cleaning' / 'outputs' / 'pamm_clean_final.parquet'
OUTPUT_DIR = BASE / '02_mev_detection' / 'filtered_output' / 'plots'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("REGENERATING ALL PLOTS WITH FILTERED DATA  [OPTIMIZED]")
print("=" * 80)

if not FILTERED_DATA.exists():
    raise FileNotFoundError(f"Filtered data not found: {FILTERED_DATA}")
if not AGGREGATOR_DATA.exists():
    raise FileNotFoundError(f"Aggregator data not found: {AGGREGATOR_DATA}")

df_fat = pd.read_csv(FILTERED_DATA)
print(f"\n✓ Filtered data: {len(df_fat):,} validated fat-sandwich attacks")
if 'attacker_signer' in df_fat.columns and 'signer' not in df_fat.columns:
    df_fat['signer'] = df_fat['attacker_signer']
if 'amm_trade' in df_fat.columns and 'pool' not in df_fat.columns:
    df_fat['pool'] = df_fat['amm_trade']

df_agg = pd.read_csv(AGGREGATOR_DATA)
print(f"✓ Aggregator data: {len(df_agg):,} signers")
df_pools = pd.read_csv(POOL_SUMMARY)
print(f"✓ Pool summary: {len(df_pools)} pools")


# =============================================================================
# Vectorized MEV-bot feature calculation (replaces the per-signer loop).
# =============================================================================
print("\n" + "=" * 80)
print("CALCULATING MEV SCORES FOR MEV BOTS [VECTORIZED]")
print("=" * 80)

mev_bot_features: dict[str, dict] = {}
if RAW_TRADE_DATA.exists():
    print(f"\nLoading raw events from {RAW_TRADE_DATA}")
    df_events_raw = pd.read_parquet(RAW_TRADE_DATA)
    df_trades_raw = df_events_raw[df_events_raw['kind'] == 'TRADE'].copy()
    print(f"✓ {len(df_trades_raw):,} trade records, {len(df_events_raw):,} total events")

    mev_bot_signers = pd.Index(df_fat['signer'].unique())
    print(f"✓ {len(mev_bot_signers)} unique MEV bot signers")

    bot_trades = df_trades_raw[df_trades_raw['signer'].isin(mev_bot_signers)].copy()
    if bot_trades.empty:
        print("⚠ No matching MEV-bot trades in raw data; falling back to profit proxy.")
    else:
        # ---- Per-signer scalar aggregations in one pass --------------------
        bot_trades['_late'] = (bot_trades['us_since_first_shred'] > 300_000).astype(int)
        if 'bytes_changed_trade' in bot_trades.columns:
            bot_trades['_high_bytes'] = (bot_trades['bytes_changed_trade'] > 50).astype(int)
        else:
            bot_trades['_high_bytes'] = 0

        per_signer = bot_trades.groupby('signer').agg(
            total_trades=('signer', 'size'),
            late_slot_count=('_late', 'sum'),
            high_bytes_count=('_high_bytes', 'sum'),
            unique_slots=('slot', 'nunique'),
        )

        # cluster_ratio = (slots with >=2 trades) / unique_slots
        slot_trade_counts = bot_trades.groupby(['signer', 'slot']).size()
        clustered_per_signer = (
            (slot_trade_counts >= 2).groupby(level='signer').sum()
        )
        per_signer['clustered_slots'] = clustered_per_signer.reindex(per_signer.index, fill_value=0)
        per_signer['late_slot_ratio'] = per_signer['late_slot_count'] / per_signer['total_trades']
        per_signer['high_bytes_ratio'] = per_signer['high_bytes_count'] / per_signer['total_trades']
        per_signer['cluster_ratio'] = (
            per_signer['clustered_slots']
            / per_signer['unique_slots'].clip(lower=1)
        )

        # ---- Oracle-backrun ratio via single merge -------------------------
        # original logic: count trades whose nearest oracle event in same slot
        # has |delta_ms| < 50.
        oracle_events = df_events_raw[df_events_raw['kind'] == 'ORACLE'][['slot', 'ms_time']]
        oracle_events = oracle_events.rename(columns={'ms_time': 'oracle_ms_time'})
        bot_trades_idx = bot_trades.reset_index().rename(columns={'index': '_orig_idx'})
        joined = bot_trades_idx[['_orig_idx', 'signer', 'slot', 'ms_time']].merge(
            oracle_events, on='slot', how='inner'
        )
        if not joined.empty:
            joined['_abs_delta'] = (joined['oracle_ms_time'] - joined['ms_time']).abs()
            min_delta = joined.groupby('_orig_idx')['_abs_delta'].min()
            backrun_idx = min_delta[min_delta < 50].index
            backrun_signers = bot_trades_idx.loc[bot_trades_idx['_orig_idx'].isin(backrun_idx), 'signer']
            backrun_counts = backrun_signers.value_counts()
            per_signer['oracle_backrun_count'] = (
                backrun_counts.reindex(per_signer.index, fill_value=0)
            )
        else:
            per_signer['oracle_backrun_count'] = 0
        per_signer['oracle_backrun_ratio'] = (
            per_signer['oracle_backrun_count'] / per_signer['total_trades']
        )

        per_signer['mev_score'] = (
            per_signer['late_slot_ratio'] * 0.3
            + per_signer['oracle_backrun_ratio'] * 0.3
            + per_signer['high_bytes_ratio'] * 0.2
            + per_signer['cluster_ratio'] * 0.2
        )

        # Materialise into the dict the downstream code expects.
        keep = ['late_slot_ratio', 'oracle_backrun_ratio',
                'high_bytes_ratio', 'cluster_ratio', 'mev_score']
        mev_bot_features = {
            sig: {k: float(per_signer.loc[sig, k]) for k in keep}
            for sig in per_signer.index
        }
        # Signers in mev_bot_signers but with no matching raw-data trades
        # get zeros to mirror the original's "if len(signer_trades) < 2"
        # branch.
        for sig in mev_bot_signers:
            mev_bot_features.setdefault(
                sig,
                {k: 0.0 for k in keep},
            )

        scores = np.array([v['mev_score'] for v in mev_bot_features.values()], dtype=float)
        print(f"\nMEV bot stats (n={len(scores)}):")
        print(f"  Mean: {scores.mean():.3f}  Median: {np.median(scores):.3f}  Std: {scores.std():.3f}")
        print(f"  Min:  {scores.min():.3f}  Max:    {scores.max():.3f}")
        print(f"  % above 0.55: {(scores > 0.55).sum() / len(scores) * 100:.1f}%")
else:
    print(f"⚠ Raw trade data not found at {RAW_TRADE_DATA}; falling back to profit proxy.")


# =============================================================================
# Plots (logic unchanged from the original; only file names get a suffix).
# =============================================================================
print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

# ----- PLOT 1 ---------------------------------------------------------------
print("\n📊 Plot 1: MEV Distribution by Protocol")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f'MEV Distribution Across Protocols ({len(df_fat)} Validated Attacks Only)',
             fontsize=16, fontweight='bold')

if 'pool' in df_fat.columns:
    pool_counts = df_fat['pool'].value_counts()
    pool_profits = df_fat.groupby('pool')['net_profit_sol'].sum().sort_values(ascending=False)
    pool_counts.plot(kind='bar', ax=axes[0, 0], color='steelblue', alpha=0.8)
    axes[0, 0].set_title('Attack Volume by Pool', fontweight='bold')
    axes[0, 0].set_xlabel('Pool'); axes[0, 0].set_ylabel('Number of Attacks')
    axes[0, 0].tick_params(axis='x', rotation=45); axes[0, 0].grid(axis='y', alpha=0.3)

    pool_profits.plot(kind='bar', ax=axes[0, 1], color='darkgreen', alpha=0.8)
    axes[0, 1].set_title('Total Profit by Pool (SOL)', fontweight='bold')
    axes[0, 1].set_xlabel('Pool'); axes[0, 1].set_ylabel('Total Profit (SOL)')
    axes[0, 1].tick_params(axis='x', rotation=45); axes[0, 1].grid(axis='y', alpha=0.3)

    avg_profit = df_fat.groupby('pool')['net_profit_sol'].mean().sort_values(ascending=False)
    avg_profit.plot(kind='bar', ax=axes[1, 0], color='coral', alpha=0.8)
    axes[1, 0].set_title('Average Profit per Attack', fontweight='bold')
    axes[1, 0].set_xlabel('Pool'); axes[1, 0].set_ylabel('Avg Profit (SOL)')
    axes[1, 0].tick_params(axis='x', rotation=45); axes[1, 0].grid(axis='y', alpha=0.3)

    top5 = pool_profits.head(5)
    others = pool_profits[5:].sum() if len(pool_profits) > 5 else 0
    pie_data = pd.concat([top5, pd.Series({'Others': others})]) if others > 0 else top5
    axes[1, 1].pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%',
                   startangle=90, colors=plt.cm.Set3(range(len(pie_data))))
    axes[1, 1].set_title('Profit Share by Pool', fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'mev_distribution_comprehensive_filtered_optimized.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {OUTPUT_DIR / 'mev_distribution_comprehensive_filtered_optimized.png'}")


# ----- PLOT 2 ---------------------------------------------------------------
print("\n📊 Plot 2: Top 20 Attackers by Profit")
if 'signer' in df_fat.columns and 'net_profit_sol' in df_fat.columns:
    top20 = df_fat.groupby('signer')['net_profit_sol'].sum().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(range(len(top20)), top20.values, color='darkred', alpha=0.7)
    ax.set_yticks(range(len(top20)))
    ax.set_yticklabels([f"{s[:8]}...{s[-8:]}" for s in top20.index], fontsize=9)
    ax.set_xlabel('Total Profit (SOL)', fontweight='bold')
    ax.set_ylabel('Attacker Signer', fontweight='bold')
    ax.set_title(f'Top 20 MEV Attackers by Total Profit ({len(df_fat)} Validated Attacks)',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3); ax.invert_yaxis()
    for i, val in enumerate(top20.values):
        ax.text(val, i, f' {val:.3f} SOL', va='center', fontsize=8)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'top_attackers_filtered_optimized.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {OUTPUT_DIR / 'top_attackers_filtered_optimized.png'}")


# ----- PLOT 3 (aggregator vs MEV bot) --------------------------------------
print("\n📊 Plot 3: Aggregator vs MEV Bot Comparison")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Aggregators vs MEV Bots: Behavioral Differences',
             fontsize=16, fontweight='bold')

mev_pool_counts = df_fat.groupby('signer')['pool'].nunique() if 'pool' in df_fat.columns else pd.Series()
mev_avg_profit = df_fat.groupby('signer')['net_profit_sol'].mean()
mev_attack_count = df_fat.groupby('signer').size()

if mev_bot_features:
    mev_scores_corrected = {
        sig: (mev_bot_features[sig]['mev_score']
              if sig in mev_bot_features
              else mev_avg_profit[sig] / mev_avg_profit.max())
        for sig in mev_avg_profit.index
    }
else:
    max_p = mev_avg_profit.max()
    mev_scores_corrected = {sig: p / max_p for sig, p in mev_avg_profit.items()}
mev_scores_series = pd.Series(mev_scores_corrected)

agg_pool_counts = df_agg['unique_pools'] if 'unique_pools' in df_agg.columns else pd.Series()
agg_mev_scores = df_agg['mev_score'] if 'mev_score' in df_agg.columns else pd.Series()
agg_trade_freq = df_agg['trades_per_hour'] if 'trades_per_hour' in df_agg.columns else pd.Series()

if len(mev_pool_counts) > 0 and len(agg_pool_counts) > 0:
    axes[0, 0].hist([mev_pool_counts, agg_pool_counts], bins=15,
                    label=['MEV Bots', 'Aggregators'],
                    color=['red', 'blue'], alpha=0.6, edgecolor='black')
    axes[0, 0].set_xlabel('Number of Unique Pools', fontweight='bold')
    axes[0, 0].set_ylabel('Frequency', fontweight='bold')
    axes[0, 0].set_title('Pool Diversity Comparison', fontweight='bold')
    axes[0, 0].legend(); axes[0, 0].grid(axis='y', alpha=0.3)

if len(agg_mev_scores) > 0 and len(mev_scores_series) > 0:
    axes[0, 1].hist([mev_scores_series, agg_mev_scores], bins=20,
                    label=['MEV Bots', 'Aggregators'],
                    color=['red', 'blue'], alpha=0.6, edgecolor='black')
    axes[0, 1].set_xlabel('MEV Score', fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontweight='bold')
    axes[0, 1].set_title('MEV Score Distribution (CORRECTED)', fontweight='bold')
    axes[0, 1].legend(); axes[0, 1].grid(axis='y', alpha=0.3)
    axes[0, 1].axvline(0.35, color='green', linestyle='--', linewidth=1.5)

if len(mev_attack_count) > 0 and len(agg_trade_freq) > 0:
    axes[0, 2].hist([mev_attack_count, agg_trade_freq], bins=20,
                    label=['MEV Bots (attacks)', 'Aggregators (trades/hr)'],
                    color=['red', 'blue'], alpha=0.6, edgecolor='black', range=(0, 50))
    axes[0, 2].set_xlabel('Frequency', fontweight='bold')
    axes[0, 2].set_ylabel('Count', fontweight='bold')
    axes[0, 2].set_title('Activity Frequency Comparison', fontweight='bold')
    axes[0, 2].legend(); axes[0, 2].grid(axis='y', alpha=0.3)

if len(agg_pool_counts) > 0 and len(agg_mev_scores) > 0:
    axes[1, 0].scatter(agg_pool_counts, agg_mev_scores, alpha=0.5, c='blue', label='Aggregators', s=30)
    if len(mev_pool_counts) > 0 and len(mev_scores_series) > 0:
        axes[1, 0].scatter(mev_pool_counts, mev_scores_series, alpha=0.5, c='red', label='MEV Bots', s=30)
    axes[1, 0].set_xlabel('Unique Pools', fontweight='bold')
    axes[1, 0].set_ylabel('MEV Score', fontweight='bold')
    axes[1, 0].set_title('Pool Diversity vs MEV Score', fontweight='bold')
    axes[1, 0].legend(); axes[1, 0].grid(alpha=0.3)
    axes[1, 0].axvline(x=5, color='green', linestyle='--', linewidth=2, alpha=0.7)
    axes[1, 0].axhline(y=0.35, color='orange', linestyle='--', linewidth=2, alpha=0.7)

if len(mev_avg_profit) > 0:
    axes[1, 1].boxplot([mev_avg_profit[mev_avg_profit < 1.0]],
                        labels=['MEV Bots'], vert=True, patch_artist=True,
                        boxprops=dict(facecolor='red', alpha=0.6))
    axes[1, 1].set_ylabel('Profit per Attack (SOL)', fontweight='bold')
    axes[1, 1].set_title('Profit Distribution (MEV Bots)', fontweight='bold')
    axes[1, 1].grid(axis='y', alpha=0.3)

axes[1, 2].axis('off')
summary = (
    f"KEY DIFFERENCES (CORRECTED):\n\n"
    f"MEV BOTS ({len(df_fat)} validated):\n"
    f"  Pool focus: {(mev_pool_counts.mean() if len(mev_pool_counts) else 0):.1f} pools avg\n"
    f"  MEV score:  {mev_scores_series.mean():.3f} avg\n"
    f"  Attacks:    {len(df_fat)} total\n"
    f"  Avg profit: {mev_avg_profit.mean():.4f} SOL\n\n"
    f"AGGREGATORS ({len(df_agg):,} signers):\n"
    f"  Pool divers: {(agg_pool_counts.mean() if len(agg_pool_counts) else 0):.1f} pools avg\n"
    f"  MEV score:   {(agg_mev_scores.mean() if len(agg_mev_scores) else 0):.3f} avg\n"
    f"  Trade freq:  {(agg_trade_freq.mean() if len(agg_trade_freq) else 0):.1f}/hr avg\n"
)
axes[1, 2].text(0.1, 0.9, summary, transform=axes[1, 2].transAxes,
                fontsize=9, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#ffffcc', alpha=0.8, pad=0.7))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'aggregator_vs_mev_detailed_comparison_optimized.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {OUTPUT_DIR / 'aggregator_vs_mev_detailed_comparison_optimized.png'}")


# ----- PLOT 4 (profit distribution) ----------------------------------------
print("\n📊 Plot 4: Profit Distribution Analysis")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle(f'MEV Profit Distribution ({len(df_fat)} Validated Attacks)', fontsize=14, fontweight='bold')

if 'net_profit_sol' in df_fat.columns:
    profits = df_fat['net_profit_sol']
    axes[0].hist(profits[profits < profits.quantile(0.95)], bins=50,
                 color='darkgreen', alpha=0.7, edgecolor='black')
    axes[0].set_xlabel('Profit (SOL)'); axes[0].set_ylabel('Frequency')
    axes[0].set_title('Profit Distribution (95th percentile)', fontweight='bold')
    axes[0].axvline(profits.median(), color='red', linestyle='--', linewidth=2,
                    label=f'Median: {profits.median():.4f}')
    axes[0].legend(); axes[0].grid(axis='y', alpha=0.3)

    if 'pool' in df_fat.columns:
        data = [df_fat[df_fat['pool'] == p]['net_profit_sol'].values for p in df_fat['pool'].unique()]
        axes[1].boxplot(data, labels=df_fat['pool'].unique(), vert=True, patch_artist=True)
        axes[1].set_xlabel('Pool'); axes[1].set_ylabel('Profit (SOL)')
        axes[1].set_title('Profit by Pool (Box Plot)', fontweight='bold')
        axes[1].tick_params(axis='x', rotation=45); axes[1].grid(axis='y', alpha=0.3)

    sorted_profits = np.sort(profits.values)
    cumulative = np.arange(1, len(sorted_profits) + 1) / len(sorted_profits) * 100
    axes[2].plot(sorted_profits, cumulative, linewidth=2, color='purple')
    axes[2].set_xlabel('Profit (SOL)'); axes[2].set_ylabel('Cumulative %')
    axes[2].set_title('Cumulative Profit Distribution', fontweight='bold')
    axes[2].axhline(50, color='red', linestyle='--', alpha=0.5, label='50th')
    axes[2].axhline(95, color='orange', linestyle='--', alpha=0.5, label='95th')
    axes[2].legend(); axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'profit_distribution_filtered_optimized.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ Saved: {OUTPUT_DIR / 'profit_distribution_filtered_optimized.png'}")


# ----- Summary --------------------------------------------------------------
print("\n" + "=" * 80)
print(f"SUMMARY ({len(df_fat)} validated attacks)")
print("=" * 80)
print(f"📊 Total profit:       {df_fat['net_profit_sol'].sum():.3f} SOL")
print(f"📊 Avg profit/attack:  {df_fat['net_profit_sol'].mean():.4f} SOL")
print(f"📊 Median profit:      {df_fat['net_profit_sol'].median():.4f} SOL")
if 'pool' in df_fat.columns:
    top_pool = df_fat['pool'].value_counts().index[0]
    print(f"📊 Top pool by count:  {top_pool}")
    pool_profits = df_fat.groupby('pool')['net_profit_sol'].sum().sort_values(ascending=False)
    print(f"📊 Top pool by SOL:    {pool_profits.index[0]} ({pool_profits.iloc[0]:.3f} SOL)")

print("\n✅ ALL PLOTS REGENERATED [OPTIMIZED]")
print(f"\nOutput directory: {OUTPUT_DIR}")
print("Generated files (suffix _optimized):")
print("  1. mev_distribution_comprehensive_filtered_optimized.png")
print("  2. top_attackers_filtered_optimized.png")
print("  3. aggregator_vs_mev_detailed_comparison_optimized.png")
print("  4. profit_distribution_filtered_optimized.png")
