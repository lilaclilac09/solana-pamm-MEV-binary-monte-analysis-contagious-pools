"""
Generate three MEV threat intelligence visualizations
"""

import matplotlib.pyplot as plt
import numpy as np

# ==================== PLOT 1: Token Pair Fragility ====================
def create_token_pair_fragility():
    fig = plt.figure(figsize=(15, 9.5), facecolor='white')
    fig.suptitle('High-Risk Assets: Token Pair Fragility', fontsize=24, fontweight='bold', y=0.95)
    fig.text(0.5, 0.89, 'Editorial Threat Intelligence Briefing', fontsize=14, ha='center', color='gray')

    # Left side: Large number panel
    left = fig.add_axes([0.02, 0.15, 0.28, 0.65])
    left.axis('off')
    left.add_patch(plt.Rectangle((0,0),1,1, fill=False, edgecolor='black', linewidth=1.5))
    left.text(0.5, 0.68, '38.2%', fontsize=95, fontweight='bold', ha='center', va='center')
    left.text(0.5, 0.35, '(PUMP/WSOL pair\ndominance in MEV attacks)', fontsize=13, ha='center', va='center', linespacing=1.2)

    # Right side: Four-quadrant scatter plot
    ax = fig.add_axes([0.35, 0.15, 0.62, 0.65])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Liquidity Depth', fontsize=14, labelpad=15)
    ax.set_ylabel('Volatility/Price Impact', fontsize=14, labelpad=15)

    # Axis labels
    ax.set_xticks([1, 9])
    ax.set_yticks([1, 9])
    ax.set_xticklabels(['Low', 'High'], fontsize=12)
    ax.set_yticklabels(['Low', 'High'], fontsize=12)

    # Quadrant dividers
    ax.axvline(5, color='gray', linestyle='--', alpha=0.4, linewidth=1)
    ax.axhline(5, color='gray', linestyle='--', alpha=0.4, linewidth=1)

    # Data points
    ax.scatter(1.5, 8.8, s=1400, c='#e74c3c', edgecolor='white', linewidth=6, zorder=5)
    ax.scatter(7.2, 3.0, s=650, c='#27ae60', edgecolor='white', linewidth=4, zorder=5)
    ax.scatter(8.1, 2.6, s=580, c='#2ecc71', edgecolor='white', linewidth=4, zorder=5)

    # Labels
    ax.text(1.5, 9.6, 'PUMP/WSOL', fontsize=14, fontweight='bold', color='#c0392b', ha='center')
    ax.text(7.2, 3.8, 'SOL/USDC', fontsize=12, fontweight='bold', color='darkgreen', ha='center')
    ax.text(8.5, 2.1, 'Blue-chip pairs', fontsize=11.5, color='darkgreen', ha='center')

    # Annotations with arrows
    deadly_text = "The Deadly Triad (PUMP/WSOL): Combines\ntypical reserves <$50K (high slippage),\n15-40% 24h swings (wide oracle windows),\nand fragmented cross-pool liquidity."
    ax.annotate(deadly_text, xy=(1.5, 8.8), xytext=(3.5, 9.6),
                fontsize=10, ha='left', va='top',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9))

    safe_text = "Safe Havens: Blue-chip pairs\n(SOL/USDC) with >$1M\nreserves showed 5.2x lower\nsandwich risk due to sub-\n0.5% price impact making\nattacks unprofitable."
    ax.annotate(safe_text, xy=(8.1, 2.6), xytext=(6.5, 5.5),
                fontsize=10, ha='right', va='top',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9))

    # Bottom text bar
    bottom = fig.add_axes([0.02, 0.02, 0.96, 0.10])
    bottom.axis('off')
    bottom.add_patch(plt.Rectangle((0,0),1,1, fill=False, edgecolor='black', linewidth=1.5))
    bottom_text = "The PUMP/WSOL pair carries a 3.16x risk amplification factor. Attackers actively exploit its\nfragmented, thin order books simultaneously across HumidiFi and BisonFi."
    bottom.text(0.5, 0.5, bottom_text, fontsize=11, ha='center', va='center', linespacing=1.3)

    plt.savefig('outputs/token_pair_fragility.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 1: token_pair_fragility.png generated')

# ==================== PLOT 2: Oracle Latency Window ====================
def create_oracle_latency_window():
    fig = plt.figure(figsize=(15, 11), facecolor='white')
    fig.suptitle('Extraction Mechanics: The Oracle Latency Window', fontsize=22, fontweight='bold', y=0.96)

    # Top left: 2.1s card
    left_card = fig.add_axes([0.03, 0.78, 0.28, 0.15])
    left_card.axis('off')
    left_card.add_patch(plt.Rectangle((0,0),1,1, fill=False, edgecolor='#8B0000', linewidth=2, linestyle='solid'))
    left_card.text(0.5, 0.65, '2.1s', fontsize=68, fontweight='bold', color='#8B0000', ha='center')
    left_card.text(0.5, 0.25, 'HumidiFi median oracle latency\n(Longest in ecosystem)', fontsize=11, ha='center', va='center', linespacing=1.1)

    # Top right: 34.7% card
    right_card = fig.add_axes([0.65, 0.78, 0.32, 0.15])
    right_card.axis('off')
    right_card.add_patch(plt.Rectangle((0,0),1,1, fill=False, edgecolor='#8B0000', linewidth=2))
    right_card.text(0.5, 0.65, '34.7%', fontsize=68, fontweight='bold', color='#8B0000', ha='center')
    right_card.text(0.5, 0.25, 'Trades executing within exactly\n50-200ms of an oracle update', fontsize=11, ha='center', va='center', linespacing=1.1)

    # Middle: Density plot
    ax = fig.add_axes([0.03, 0.32, 0.65, 0.42])
    x = np.linspace(-200, 300, 500)
    oracle = np.zeros_like(x)
    oracle[np.abs(x) < 5] = 4.2
    oracle[np.abs(x-5) < 8] = 1.8
    trade = np.zeros_like(x)
    trade[(x > -80) & (x < -30)] = 0.6
    trade[(x > 70) & (x < 130)] = 3.8

    ax.plot(x, oracle, color='#1f2a44', linewidth=3.5, label='ORACLE Update')
    ax.plot(x, trade, color='#9b2d30', linewidth=3.5, label='TRADE Execution')

    ax.set_xlabel('Time (Relative to Oracle Update)', fontsize=12)
    ax.set_ylabel('Events per Second Density', fontsize=12)
    ax.set_xlim(-220, 320)
    ax.set_ylim(0, 4.5)
    ax.grid(True, alpha=0.15)
    ax.legend(loc='upper left', frameon=False, fontsize=11)

    ax.annotate('Front-Running Clusters\nAttempting to preempt\npending updates', xy=(-70, 0.6), xytext=(-140, 2.2),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'), fontsize=10, ha='center',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.95))

    ax.annotate('The Back-Running Swarm\nExploiting outdated prices\npost-update', xy=(105, 3.8), xytext=(170, 4.1),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'), fontsize=10, ha='left',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='white', alpha=0.95))

    ax.text(0, 4.3, '0 (Update)', fontsize=10, ha='center', fontweight='bold')

    # Right side: Key Insight
    insight = fig.add_axes([0.71, 0.32, 0.26, 0.42])
    insight.axis('off')
    insight.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#e6f0ff', edgecolor='#1f2a44', linewidth=2))
    insight.text(0.5, 0.85, 'Key Insight', fontsize=14, fontweight='bold', ha='center', color='#1f2a44')
    insight.text(0.05, 0.68, 'Pools with >1 second oracle\nlatency suffer 2.3x higher\nsandwich attack rates.\n\nUnpredictable timing variance\ncreates unavoidable exposure\nwindows.', fontsize=10.5, va='top', linespacing=1.4)

    # Bottom: Bar chart
    bar_ax = fig.add_axes([0.03, 0.05, 0.94, 0.22])
    pools = ['HumidiFi', 'ZeroFi', 'TesseraV', 'SolFIV2', 'GoonFi', 'BisonFi', 'SolFi', 'AlphaQ']
    latencies = [2100000, 953483, 524160, 524160, 202230, 137663, 101930, 99770]
    colors = ['#8B0000'] + ['#1f2a44']*7

    bars = bar_ax.barh(pools[::-1], latencies[::-1], color=colors[::-1], height=0.6)
    bar_ax.set_xlabel('Mean Latency (microseconds)', fontsize=12)
    bar_ax.set_title('Top ORACLEs: Mean Update Latency Comparison', fontsize=13, pad=15)

    for bar in bars:
        width = bar.get_width()
        bar_ax.text(width + 30000, bar.get_y() + bar.get_height()/2, f'{width:,.0f}μs',
                    va='center', fontsize=10, fontweight='bold')

    plt.savefig('outputs/oracle_latency_window.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 2: oracle_latency_window.png generated')

# ==================== PLOT 3: MEV Battlefield ====================
def create_mev_battlefield():
    fig = plt.figure(figsize=(14.5, 10), facecolor='white')
    fig.suptitle('The MEV Battlefield: Protocol-Specific Vulnerability', fontsize=22, fontweight='bold', y=0.95)
    fig.text(0.5, 0.90, 'Editorial Threat Intelligence Briefing', fontsize=13, ha='center', color='gray')

    # Left: Bar chart
    ax_bar = fig.add_axes([0.04, 0.22, 0.48, 0.62])
    pools = ['HumidiFi', 'BisonFi', 'GoonFi', 'TesseraV', 'SolFIV2', 'ZeroFi', 'OtherV2']
    profits = [75.1, 11.2, 8.1, 7.8, 7.2, 2.4, 0]
    colors = ['#8B0000'] + ['#2e7d32']*5 + ['#1f2a44']

    bars = ax_bar.bar(pools, profits, color=colors, width=0.65)
    ax_bar.set_ylabel('Total Profit (SOL)', fontsize=12)
    ax_bar.set_title('Total Profit by Pool (SOL)', fontsize=13, pad=10)
    ax_bar.grid(axis='y', alpha=0.2)

    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax_bar.text(bar.get_x() + bar.get_width()/2, h + 1.5, f'{h:.1f}', ha='center', fontweight='bold')

    ax_bar.text(0.5, -0.25, 'HumidiFi: $75.1 SOL extracted. 66.8% of profit\ndespite only 27% of attack volume.\n\nGoonFi: High frequency (258 attacks) but\nheavily suppressed total profit ($7.9 SOL).',
                transform=ax_bar.transAxes, ha='center', fontsize=10, linespacing=1.3)

    # Right: Large percentage
    fig.text(0.72, 0.68, '66.8%', fontsize=85, fontweight='bold', color='#8B0000', ha='center')

    # Pie chart
    ax_pie = fig.add_axes([0.62, 0.22, 0.35, 0.48])
    sizes = [66.8, 10.0, 7.0, 6.7, 6.7, 2.8]
    labels = ['HumidiFi', 'BisonFi', 'GoonFi', 'TesseraV', 'SolFIV2', 'Others']
    colors_pie = ['#8B0000', '#2e7d32', '#2e7d32', '#2e7d32', '#2e7d32', '#1f2a44']

    wedges, texts, autotexts = ax_pie.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 10})
    ax_pie.set_title('Profit Share by Pool', fontsize=13, pad=20)

    # Risk Implication box
    risk = fig.add_axes([0.62, 0.03, 0.35, 0.18])
    risk.axis('off')
    risk.add_patch(plt.Rectangle((0,0),1,1, fill=True, facecolor='#e6f0ff', edgecolor='#1f2a44', linewidth=2))
    risk.text(0.5, 0.85, 'Risk Implication', fontsize=13, fontweight='bold', ha='center')
    risk.text(0.05, 0.68, 'Extreme concentration\nindicates systemic\nvulnerability in\nHumidiFi.\n\nAttackers do not\nblanket the ecosystem;\nthey actively target\nspecific pools with\nknown oracle or\nliquidity weaknesses.',
              fontsize=10, va='top', linespacing=1.3)

    plt.savefig('outputs/mev_battlefield.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ Plot 3: mev_battlefield.png generated')

if __name__ == '__main__':
    import os
    os.makedirs('outputs', exist_ok=True)
    
    print('🎨 Generating visualizations...\n')
    create_token_pair_fragility()
    create_oracle_latency_window()
    create_mev_battlefield()
    print('\n✨ All visualizations complete! Check outputs/ folder')
