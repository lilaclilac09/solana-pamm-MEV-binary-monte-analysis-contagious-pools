"""
Generate three MEV threat intelligence visualizations.

Supports loading updated values from a JSON data file.
"""

import argparse
import json
import os
import shutil

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_DATA = {
    "token_pair_fragility": {
        "headline_percent": 38.2,
        "pump_wsol_label": "PUMP/WSOL",
        "safe_pair_label": "SOL/USDC",
        "safe_pairs_label": "Blue-chip pairs",
        "points": {
            "pump_wsol": [1.5, 8.8],
            "safe_pair": [7.2, 3.0],
            "safe_pairs": [8.1, 2.6],
        },
    },
    "oracle_latency_window": {
        "headline_latency_seconds": 2.1,
        "headline_trade_percent": 34.7,
        "pool_latencies_us": {
            "HumidiFi": 2100000,
            "ZeroFi": 953483,
            "TesseraV": 524160,
            "SolFIV2": 524160,
            "GoonFi": 202230,
            "BisonFi": 137663,
            "SolFi": 101930,
            "AlphaQ": 99770,
        },
    },
    "mev_battlefield": {
        "pool_profits_sol": {
            "HumidiFi": 75.1,
            "BisonFi": 11.2,
            "GoonFi": 8.1,
            "TesseraV": 7.8,
            "SolFIV2": 7.2,
            "ZeroFi": 2.4,
            "OtherV2": 0,
        },
        "profit_share_percent": {
            "HumidiFi": 66.8,
            "BisonFi": 10.0,
            "GoonFi": 7.0,
            "TesseraV": 6.7,
            "SolFIV2": 6.7,
            "Others": 2.8,
        },
    },
}


def deep_merge(base, override):
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_data(data_file=None):
    if not data_file:
        return DEFAULT_DATA

    with open(data_file, "r", encoding="utf-8") as file:
        user_data = json.load(file)
    return deep_merge(DEFAULT_DATA, user_data)

# ==================== PLOT 1: Token Pair Fragility ====================
def create_token_pair_fragility(data, out_dir):
    section = data["token_pair_fragility"]
    points = section["points"]

    fig = plt.figure(figsize=(16, 10), facecolor='white')
    fig.suptitle('High-Risk Assets: Token Pair Fragility', fontsize=28, fontweight='bold', y=0.96)
    fig.text(0.5, 0.90, 'Editorial Threat Intelligence Briefing', fontsize=15, ha='center', color='#555555')

    # Left side: Large number panel
    left = fig.add_axes([0.02, 0.15, 0.28, 0.65])
    left.axis('off')
    left.add_patch(plt.Rectangle((0,0),1,1, fill=False, edgecolor='black', linewidth=2))
    left.text(0.5, 0.68, f"{section['headline_percent']:.1f}%", fontsize=110, fontweight='bold', ha='center', va='center', color='#8B0000')
    left.text(0.5, 0.35, f"({section['pump_wsol_label']} pair\ndominance in MEV attacks)", fontsize=14, ha='center', va='center', linespacing=1.3)

    # Right side: Four-quadrant scatter plot
    ax = fig.add_axes([0.35, 0.15, 0.62, 0.65])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Liquidity Depth', fontsize=16, labelpad=15, fontweight='bold')
    ax.set_ylabel('Volatility/Price Impact', fontsize=16, labelpad=15, fontweight='bold')

    # Axis labels
    ax.set_xticks([1, 9])
    ax.set_yticks([1, 9])
    ax.set_xticklabels(['Low', 'High'], fontsize=14, fontweight='bold')
    ax.set_yticklabels(['Low', 'High'], fontsize=14, fontweight='bold')

    # Quadrant dividers
    ax.axvline(5, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.axhline(5, color='gray', linestyle='--', alpha=0.4, linewidth=1)

    # Data points
    ax.scatter(points['pump_wsol'][0], points['pump_wsol'][1], s=1400, c='#e74c3c', edgecolor='white', linewidth=6, zorder=5)
    ax.scatter(points['safe_pair'][0], points['safe_pair'][1], s=650, c='#27ae60', edgecolor='white', linewidth=4, zorder=5)
    ax.scatter(points['safe_pairs'][0], points['safe_pairs'][1], s=580, c='#2ecc71', edgecolor='white', linewidth=4, zorder=5)

    # Labels
    ax.text(points['pump_wsol'][0], 9.6, section['pump_wsol_label'], fontsize=15, fontweight='bold', color='#8B0000', ha='center')
    ax.text(points['safe_pair'][0], 3.8, section['safe_pair_label'], fontsize=13, fontweight='bold', color='#2e7d32', ha='center')
    ax.text(8.5, 2.1, section['safe_pairs_label'], fontsize=12.5, color='#2e7d32', ha='center', fontweight='bold')

    # Annotations with arrows
    deadly_text = "The Deadly Triad (PUMP/WSOL): Combines\ntypical reserves <$50K (high slippage),\n15-40% 24h swings (wide oracle windows),\nand fragmented cross-pool liquidity."
    ax.annotate(deadly_text, xy=(points['pump_wsol'][0], points['pump_wsol'][1]), xytext=(3.5, 9.6),
                fontsize=11, ha='left', va='top',
                arrowprops=dict(arrowstyle='->', color='black', lw=2),
                bbox=dict(boxstyle="round,pad=0.6", facecolor='#fff5f5', edgecolor='#8B0000', linewidth=1.5, alpha=0.95))

    safe_text = "Safe Havens: Blue-chip pairs\n(SOL/USDC) with >$1M\nreserves showed 5.2x lower\nsandwich risk due to sub-\n0.5% price impact making\nattacks unprofitable."
    ax.annotate(safe_text, xy=(points['safe_pairs'][0], points['safe_pairs'][1]), xytext=(6.5, 5.5),
                fontsize=11, ha='right', va='top',
                arrowprops=dict(arrowstyle='->', color='black', lw=2),
                bbox=dict(boxstyle="round,pad=0.6", facecolor='#f0f8f0', edgecolor='#2e7d32', linewidth=1.5, alpha=0.95))

    # Bottom text bar
    bottom = fig.add_axes([0.02, 0.02, 0.96, 0.10])
    bottom.axis('off')
    bottom.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#f8f9fa', edgecolor='black', linewidth=2))
    bottom_text = "The PUMP/WSOL pair carries a 3.16x risk amplification factor. Attackers actively exploit its\nfragmented, thin order books simultaneously across HumidiFi and BisonFi."
    bottom.text(0.5, 0.5, bottom_text, fontsize=12, ha='center', va='center', linespacing=1.4, fontweight='medium')

    plt.savefig(os.path.join(out_dir, 'token_pair_fragility.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 1: token_pair_fragility.png generated')

# ==================== PLOT 2: Oracle Latency Window ====================
def create_oracle_latency_window(data, out_dir):
    section = data["oracle_latency_window"]

    fig = plt.figure(figsize=(16, 11.5), facecolor='white')
    fig.suptitle('Extraction Mechanics: The Oracle Latency Window', fontsize=26, fontweight='bold', y=0.96)

    # Top left: 2.1s card
    left_card = fig.add_axes([0.03, 0.78, 0.28, 0.15])
    left_card.axis('off')
    left_card.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#fff5f5', edgecolor='#8B0000', linewidth=2.5, linestyle='solid'))
    left_card.text(0.5, 0.65, f"{section['headline_latency_seconds']:.1f}s", fontsize=75, fontweight='bold', color='#8B0000', ha='center')
    left_card.text(0.5, 0.25, 'HumidiFi median oracle latency\n(Longest in ecosystem)', fontsize=12, ha='center', va='center', linespacing=1.2, fontweight='medium')

    # Top right: 34.7% card
    right_card = fig.add_axes([0.65, 0.78, 0.32, 0.15])
    right_card.axis('off')
    right_card.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#fff5f5', edgecolor='#8B0000', linewidth=2.5))
    right_card.text(0.5, 0.65, f"{section['headline_trade_percent']:.1f}%", fontsize=75, fontweight='bold', color='#8B0000', ha='center')
    right_card.text(0.5, 0.25, 'Trades executing within exactly\n50-200ms of an oracle update', fontsize=12, ha='center', va='center', linespacing=1.2, fontweight='medium')

    # Middle: Density plot
    ax = fig.add_axes([0.03, 0.32, 0.65, 0.42])
    x = np.linspace(-200, 300, 500)
    oracle = np.zeros_like(x)
    oracle[np.abs(x) < 5] = 4.2
    oracle[np.abs(x-5) < 8] = 1.8
    trade = np.zeros_like(x)
    trade[(x > -80) & (x < -30)] = 0.6
    trade[(x > 70) & (x < 130)] = 3.8

    ax.plot(x, oracle, color='#1f2a44', linewidth=4, label='ORACLE Update')
    ax.plot(x, trade, color='#8B0000', linewidth=4, label='TRADE Execution')

    ax.set_xlabel('Time (Relative to Oracle Update)', fontsize=14, labelpad=10, fontweight='bold')
    ax.set_ylabel('Events per Second Density', fontsize=14, labelpad=10, fontweight='bold')
    ax.set_xlim(-220, 320)
    ax.set_ylim(0, 4.5)
    ax.grid(True, alpha=0.2, linewidth=0.8)
    ax.legend(loc='upper left', frameon=True, fontsize=12, framealpha=0.95, edgecolor='gray')

    ax.annotate('Front-Running Clusters\nAttempting to preempt\npending updates', xy=(-70, 0.6), xytext=(-140, 2.2),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='black'), fontsize=11, ha='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#f8f9fa', edgecolor='#1f2a44', linewidth=1.5, alpha=0.98))

    ax.annotate('The Back-Running Swarm\nExploiting outdated prices\npost-update', xy=(105, 3.8), xytext=(170, 4.1),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='black'), fontsize=11, ha='left',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#fff5f5', edgecolor='#8B0000', linewidth=1.5, alpha=0.98))

    ax.text(0, 4.3, '0 (Update)', fontsize=11, ha='center', fontweight='bold')

    # Right side: Key Insight
    insight = fig.add_axes([0.71, 0.32, 0.26, 0.42])
    insight.axis('off')
    insight.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#e6f0ff', edgecolor='#1f2a44', linewidth=2.5))
    insight.text(0.5, 0.85, 'Key Insight', fontsize=16, fontweight='bold', ha='center', color='#1f2a44')
    insight.text(0.05, 0.68, 'Pools with >1 second oracle\nlatency suffer 2.3x higher\nsandwich attack rates.\n\nUnpredictable timing variance\ncreates unavoidable exposure\nwindows.', fontsize=11.5, va='top', linespacing=1.5, fontweight='medium')

    # Bottom: Bar chart
    bar_ax = fig.add_axes([0.03, 0.05, 0.94, 0.22])
    pools = list(section['pool_latencies_us'].keys())
    latencies = list(section['pool_latencies_us'].values())
    colors = ['#8B0000'] + ['#1f2a44']*7

    bars = bar_ax.barh(pools[::-1], latencies[::-1], color=colors[::-1], height=0.65)
    bar_ax.set_xlabel('Mean Latency (microseconds)', fontsize=14, labelpad=10, fontweight='bold')
    bar_ax.set_title('Top ORACLEs: Mean Update Latency Comparison', fontsize=15, pad=15, fontweight='bold')
    bar_ax.tick_params(axis='y', labelsize=12)

    for bar in bars:
        width = bar.get_width()
        bar_ax.text(width + 30000, bar.get_y() + bar.get_height()/2, f'{width:,.0f}μs',
                    va='center', fontsize=11, fontweight='bold')

    plt.savefig(os.path.join(out_dir, 'oracle_latency_window.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 2: oracle_latency_window.png generated')

# ==================== PLOT 3: MEV Battlefield ====================
def create_mev_battlefield(data, out_dir):
    section = data["mev_battlefield"]

    fig = plt.figure(figsize=(16, 10.5), facecolor='white')
    fig.suptitle('The MEV Battlefield: Protocol-Specific Vulnerability', fontsize=26, fontweight='bold', y=0.95)
    fig.text(0.5, 0.90, 'Editorial Threat Intelligence Briefing', fontsize=15, ha='center', color='#555555')

    # Left: Bar chart
    ax_bar = fig.add_axes([0.04, 0.22, 0.48, 0.62])
    pools = list(section['pool_profits_sol'].keys())
    profits = list(section['pool_profits_sol'].values())
    colors = ['#8B0000'] + ['#2e7d32']*5 + ['#1f2a44']

    bars = ax_bar.bar(pools, profits, color=colors, width=0.68)
    ax_bar.set_ylabel('Total Profit (SOL)', fontsize=15, labelpad=10, fontweight='bold')
    ax_bar.set_title('Total Profit by Pool (SOL)', fontsize=16, pad=12, fontweight='bold')
    ax_bar.grid(axis='y', alpha=0.25, linewidth=0.8)
    ax_bar.tick_params(axis='x', labelsize=12, labelrotation=0)
    ax_bar.tick_params(axis='y', labelsize=12)

    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax_bar.text(bar.get_x() + bar.get_width()/2, h + 1.5, f'{h:.1f}', ha='center', fontsize=12, fontweight='bold')

    ax_bar.text(0.5, -0.25, 'HumidiFi: $75.1 SOL extracted. 66.8% of profit\ndespite only 27% of attack volume.\n\nGoonFi: High frequency (258 attacks) but\nheavily suppressed total profit ($7.9 SOL).',
                transform=ax_bar.transAxes, ha='center', fontsize=11, linespacing=1.4, fontweight='medium')

    # Right: Large percentage
    fig.text(0.72, 0.68, f"{section['profit_share_percent']['HumidiFi']:.1f}%", fontsize=95, fontweight='bold', color='#8B0000', ha='center')

    # Pie chart
    ax_pie = fig.add_axes([0.62, 0.22, 0.35, 0.48])
    labels = list(section['profit_share_percent'].keys())
    sizes = list(section['profit_share_percent'].values())
    colors_pie = ['#8B0000', '#2e7d32', '#2e7d32', '#2e7d32', '#2e7d32', '#1f2a44']

    wedges, texts, autotexts = ax_pie.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    ax_pie.set_title('Profit Share by Pool', fontsize=15, pad=20, fontweight='bold')

    # Risk Implication box
    risk = fig.add_axes([0.62, 0.03, 0.35, 0.18])
    risk.axis('off')
    risk.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#e6f0ff', edgecolor='#1f2a44', linewidth=2.5))
    risk.text(0.5, 0.85, 'Risk Implication', fontsize=15, fontweight='bold', ha='center', color='#1f2a44')
    risk.text(0.05, 0.68, 'Extreme concentration\nindicates systemic\nvulnerability in\nHumidiFi.\n\nAttackers do not\nblanket the ecosystem;\nthey actively target\nspecific pools with\nknown oracle or\nliquidity weaknesses.',
              fontsize=11, va='top', linespacing=1.4, fontweight='medium')

    plt.savefig(os.path.join(out_dir, 'mev_battlefield.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 3: mev_battlefield.png generated')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate Section 5c visualization PNGs")
    parser.add_argument("--data-file", help="Path to JSON file with updated values", default=None)
    parser.add_argument("--out-dir", help="Output directory for generated PNGs", default="outputs")
    parser.add_argument("--copy-to-assets", help="Copy generated PNGs to this assets directory", default="app/assets")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    data = load_data(args.data_file)

    print('Generating visualizations...\n')
    create_token_pair_fragility(data, args.out_dir)
    create_oracle_latency_window(data, args.out_dir)
    create_mev_battlefield(data, args.out_dir)

    if args.copy_to_assets:
        os.makedirs(args.copy_to_assets, exist_ok=True)
        for name in [
            'token_pair_fragility.png',
            'oracle_latency_window.png',
            'mev_battlefield.png',
        ]:
            src = os.path.join(args.out_dir, name)
            dst = os.path.join(args.copy_to_assets, name)
            shutil.copy2(src, dst)
        print(f'\nCopied PNGs to {args.copy_to_assets}')

    print(f'\nAll visualizations complete! Check {args.out_dir}/ folder')
