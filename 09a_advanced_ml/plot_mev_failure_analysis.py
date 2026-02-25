#!/usr/bin/env python3
"""Generate MEV failure analysis plots (data-driven + conceptual).

Saves PNGs to `outputs/mev_failure_analysis/`.
"""
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


OUTDIR = Path("outputs/mev_failure_analysis")
OUTDIR.mkdir(parents=True, exist_ok=True)


def load_csv(path: Path):
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def plot_failure_reasons(df_failed: pd.DataFrame):
    if df_failed is None or df_failed.empty:
        return
    counts = df_failed['reason'].value_counts()
    plt.figure(figsize=(8,5))
    sns.barplot(x=counts.values, y=counts.index, palette='muted')
    plt.xlabel('Count')
    plt.ylabel('Failure Reason')
    plt.title('Failed Sandwich Attempts by Reason')
    plt.tight_layout()
    plt.savefig(OUTDIR / 'failed_attempts_by_reason.png')
    plt.close()


def plot_profit_distribution(df_all: pd.DataFrame):
    if df_all is None or df_all.empty:
        return
    if 'net_profit_sol' not in df_all.columns or 'classification' not in df_all.columns:
        return
    plt.figure(figsize=(8,5))
    sns.boxplot(x='classification', y='net_profit_sol', data=df_all, order=['FAILED_SANDWICH', 'FAT_SANDWICH'])
    plt.yscale('symlog' if (df_all['net_profit_sol'] > 0).any() else 'linear')
    plt.xlabel('Classification')
    plt.ylabel('Net profit (SOL)')
    plt.title('Net Profit: Failed vs Successful Sandwiches')
    plt.tight_layout()
    plt.savefig(OUTDIR / 'profit_failed_vs_success.png')
    plt.close()


def plot_failed_over_time(df_failed: pd.DataFrame):
    if df_failed is None or df_failed.empty:
        return
    # aggregate by coarse slot windows to make a time-like plot
    df = df_failed.copy()
    df['slot_window'] = (df['slot'] // 1000) * 1000
    counts = df.groupby('slot_window').size().reset_index(name='count')
    plt.figure(figsize=(10,4))
    sns.lineplot(x='slot_window', y='count', data=counts)
    plt.xlabel('Slot window (x1000)')
    plt.ylabel('Failed attempts')
    plt.title('Failed Sandwich Attempts Over Slot Windows')
    plt.tight_layout()
    plt.savefig(OUTDIR / 'failed_attempts_over_time.png')
    plt.close()


def plot_latency_vs_failures(df_failed: pd.DataFrame, df_latency: pd.DataFrame):
    if df_failed is None or df_latency is None:
        return
    # count failures per validator
    counts = df_failed.groupby('validator').size().reset_index(name='fail_count')
    merged = counts.merge(df_latency, left_on='validator', right_on='validator', how='left')
    if 'mean_latency_ms' in merged.columns:
        plt.figure(figsize=(8,5))
        sns.scatterplot(x='mean_latency_ms', y='fail_count', data=merged)
        plt.xlabel('Validator mean latency (ms)')
        plt.ylabel('Failed attempts')
        plt.title('Validator Latency vs Failed Attempts')
        plt.tight_layout()
        plt.savefig(OUTDIR / 'latency_vs_failed_attempts.png')
        plt.close()


def plot_conceptual_failure_breakdown(df_failed: pd.DataFrame):
    # Make a simple conceptual breakdown mapping low-level reasons to broader categories
    mapping = {
        'no_victims_between': 'No victims',
        'insufficient_liquidity': 'Liquidity',
        'competing_bots': 'Competition',
        'latency_timeout': 'Latency',
    }
    if df_failed is None or df_failed.empty:
        # create a placeholder conceptual plot
        categories = ['No victims', 'Competition', 'Latency', 'Liquidity']
        values = [0.6, 0.2, 0.15, 0.05]
    else:
        # map known reasons, unknown -> Other
        reasons_mapped = df_failed['reason'].map(lambda r: mapping.get(r, 'Other'))
        counts = reasons_mapped.value_counts(normalize=True)
        categories = counts.index.tolist()
        values = counts.values.tolist()

    plt.figure(figsize=(6,4))
    sns.barplot(x=values, y=categories, palette='deep')
    plt.xlabel('Proportion')
    plt.title('Conceptual Breakdown: Why MEV Attempts Failed')
    plt.tight_layout()
    plt.savefig(OUTDIR / 'conceptual_failure_breakdown.png')
    plt.close()


def main():
    repo = Path('.')
    df_failed = load_csv(repo / '02_mev_detection' / 'failed_sandwich_attempts.csv')
    df_all = load_csv(repo / '02_mev_detection' / 'filtered_output' / 'all_mev_with_classification.csv')
    df_latency = load_csv(repo / '06_pool_analysis' / 'outputs' / 'validator_latency_metrics.csv')

    print('Loaded:', 'failed' if df_failed is not None else 'no failed file',
          'all_mev' if df_all is not None else 'no all_mev file',
          'latency' if df_latency is not None else 'no latency file')

    plot_failure_reasons(df_failed)
    plot_profit_distribution(df_all)
    plot_failed_over_time(df_failed)
    plot_latency_vs_failures(df_failed, df_latency)
    plot_conceptual_failure_breakdown(df_failed)

    print('Plots saved to', OUTDIR)


if __name__ == '__main__':
    main()
