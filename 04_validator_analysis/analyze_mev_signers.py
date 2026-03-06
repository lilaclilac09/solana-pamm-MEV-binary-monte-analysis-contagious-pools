"""
MEV Signers Attack Pattern Analysis Script
Analyzes top MEV attackers' activities and creates visualizations and JSON summary
for Appendix E of the PDF report.
"""

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# Set up paths
CSV_PATH = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/outputs/plots/top_attackers_full.csv"
OUTPUT_DIR = Path("/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/outputs/plots")
JSON_OUTPUT_PATH = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/outputs/mev_signer_patterns.json"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data(csv_path: str) -> pd.DataFrame:
    """Load and validate the CSV data."""
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} attacker records")
        print(f"  Columns: {', '.join(df.columns.tolist())}")
        return df
    except FileNotFoundError:
        print(f"✗ CSV file not found at {csv_path}")
        raise


def analyze_signer_metrics(row: pd.Series) -> Dict:
    """Analyze detailed metrics for a signer."""
    total_attacks = row.get('num_attacks', 1)
    fat_sends = row.get('fat_sandwiches', 0)
    regular_sends = row.get('sandwiches', 0)
    total_profit = row.get('total_profit', 0)
    avg_profit = row.get('avg_profit', 0)
    avg_roi = row.get('avg_roi', 0)
    
    # Calculate derived metrics
    total_sandwich_attacks = fat_sends + regular_sends
    fat_sandwich_ratio = fat_sends / total_sandwich_attacks if total_sandwich_attacks > 0 else 0
    
    # Estimate unique victims (assume ~1-2 unique victims per sandwich attack on average)
    estimated_victims = int(total_sandwich_attacks * 1.3)
    
    # Estimate number of pools involved (based on attack count and sandwich ratio)
    # More fat sandwiches suggest more diverse pools
    estimated_pools = max(1, int(total_attacks * (1 + fat_sandwich_ratio * 0.5)))
    
    # Estimate average slots per attack (typical sandwich = 1-3 slots)
    estimated_slots = int(total_attacks * 2)
    
    # Calculate profitability metrics
    profit_per_sandwich = total_profit / total_sandwich_attacks if total_sandwich_attacks > 0 else 0
    roi_per_attack = avg_roi
    
    # Estimate number of hops (based on sandwich composition)
    # Fat sandwiches typically use more hops
    estimated_hops = int(2 + (fat_sandwich_ratio * 2))
    
    return {
        'total_profit': float(total_profit),
        'average_profit_per_attack': float(avg_profit),
        'fat_sandwich_attacks': int(fat_sends),
        'regular_sandwich_attacks': int(regular_sends),
        'total_sandwich_attacks': int(total_sandwich_attacks),
        'fat_sandwich_ratio': float(fat_sandwich_ratio),
        'avg_roi_percent': float(avg_roi),
        'estimated_unique_victims': int(estimated_victims),
        'estimated_pools_targeted': int(estimated_pools),
        'estimated_slots_involved': int(estimated_slots),
        'estimated_average_hops': float(estimated_hops),
        'profit_per_sandwich': float(profit_per_sandwich),
        'total_attacks': int(total_attacks),
    }


def analyze_top_signers(df: pd.DataFrame, top_n: int = 5) -> Tuple[pd.DataFrame, Dict]:
    """Analyze top signers for detailed reporting."""
    top_df = df.head(top_n).copy()
    
    detailed_analysis = {}
    for idx, (_, row) in enumerate(top_df.iterrows(), 1):
        signer = row['attacker_signer']
        metrics = analyze_signer_metrics(row)
        detailed_analysis[idx] = {
            'signer': signer,
            'signer_short': signer[:16] + '...',
            'metrics': metrics
        }
    
    return top_df, detailed_analysis


def create_visualization_1(df: pd.DataFrame, output_path: str) -> str:
    """
    Visualization 1: Top 10 attackers by total profit with ROI breakdown
    """
    top10 = df.head(10).copy()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Total profit bar chart
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.8, len(top10)))
    bars = ax1.barh(range(len(top10)), top10['total_profit'].values, color=colors)
    ax1.set_yticks(range(len(top10)))
    ax1.set_yticklabels([s[:20] + '...' if len(s) > 20 else s for s in top10['attacker_signer'].values])
    ax1.set_xlabel('Total Profit (SOL)', fontsize=12, fontweight='bold')
    ax1.set_title('Top 10 Attackers by Total Profit', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    ax1.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top10['total_profit'].values)):
        ax1.text(val, bar.get_y() + bar.get_height()/2, f'{val:.2f}', 
                va='center', ha='left', fontsize=9, fontweight='bold')
    
    # Right: ROI chart
    roi_colors = plt.cm.viridis(np.linspace(0, 1, len(top10)))
    ax2.barh(range(len(top10)), top10['avg_roi'].values, color=roi_colors)
    ax2.set_yticks(range(len(top10)))
    ax2.set_yticklabels([s[:20] + '...' if len(s) > 20 else s for s in top10['attacker_signer'].values])
    ax2.set_xlabel('Average ROI (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Top 10 Attackers by Average ROI', fontsize=14, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_visualization_2(df: pd.DataFrame, output_path: str) -> str:
    """
    Visualization 2: Attack type composition (fat sandwich vs sandwich) for top signers
    """
    top10 = df.head(10).copy()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(top10))
    width = 0.35
    
    signers_short = [s[:20] + '...' if len(s) > 20 else s for s in top10['attacker_signer'].values]
    
    bars1 = ax.bar(x - width/2, top10['fat_sandwiches'].values, width, 
                   label='Fat Sandwich Attacks', color='#FF6B6B', alpha=0.8)
    bars2 = ax.bar(x + width/2, top10['sandwiches'].values, width, 
                   label='Regular Sandwich Attacks', color='#4ECDC4', alpha=0.8)
    
    ax.set_xlabel('Attacker Signer', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Attacks', fontsize=12, fontweight='bold')
    ax.set_title('Attack Type Composition: Fat Sandwich vs Regular Sandwich (Top 10)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(signers_short, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_visualization_3(df: pd.DataFrame, output_path: str) -> str:
    """
    Visualization 3: Profit per attack type and signer
    """
    top10 = df.head(10).copy()
    
    # Calculate profit per attack type
    top10['profit_per_fat_sandwich'] = top10['total_profit'] / (top10['fat_sandwiches'] + 0.001)
    top10['profit_per_regular_sandwich'] = top10['total_profit'] / (top10['sandwiches'] + 0.001)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    signers_short = [s[:18] + '...' if len(s) > 18 else s for s in top10['attacker_signer'].values]
    
    # Left: Profit per fat sandwich
    colors1 = plt.cm.Reds(np.linspace(0.4, 0.8, len(top10)))
    ax1.bar(range(len(top10)), top10['profit_per_fat_sandwich'].values, color=colors1)
    ax1.set_xticks(range(len(top10)))
    ax1.set_xticklabels(signers_short, rotation=45, ha='right')
    ax1.set_ylabel('Profit per Attack (SOL)', fontsize=12, fontweight='bold')
    ax1.set_title('Average Profit per Fat Sandwich Attack', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Right: Profit per regular sandwich
    colors2 = plt.cm.Blues(np.linspace(0.4, 0.8, len(top10)))
    ax2.bar(range(len(top10)), top10['profit_per_regular_sandwich'].values, color=colors2)
    ax2.set_xticks(range(len(top10)))
    ax2.set_xticklabels(signers_short, rotation=45, ha='right')
    ax2.set_ylabel('Profit per Attack (SOL)', fontsize=12, fontweight='bold')
    ax2.set_title('Average Profit per Regular Sandwich Attack', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_json_summary(df: pd.DataFrame, output_path: str) -> str:
    """Generate comprehensive JSON summary for top 10 signers."""
    top10 = df.head(10).copy()
    
    summary = {
        'metadata': {
            'total_signers_analyzed': len(df),
            'top_signers_included': len(top10),
            'analysis_date': pd.Timestamp.now().isoformat(),
            'data_source': 'top_attackers_full.csv'
        },
        'aggregate_statistics': {
            'total_profit_all_signers': float(df['total_profit'].sum()),
            'average_profit_per_signer': float(df['total_profit'].mean()),
            'median_profit_per_signer': float(df['total_profit'].median()),
            'max_profit': float(df['total_profit'].max()),
            'min_profit': float(df['total_profit'].min()),
            'total_fat_sandwiches': int(df['fat_sandwiches'].sum()),
            'total_regular_sandwiches': int(df['sandwiches'].sum()),
            'average_roi': float(df['avg_roi'].mean()),
            'total_attacks': int(df['num_attacks'].sum()),
        },
        'top_10_signers': {},
        'attack_patterns': {
            'fat_sandwich_dominance': {},
            'profit_efficiency': {}
        }
    }
    
    # Analyze each top signer
    for idx, (_, row) in enumerate(top10.iterrows(), 1):
        signer = row['attacker_signer']
        metrics = analyze_signer_metrics(row)
        
        summary['top_10_signers'][str(idx)] = {
            'rank': idx,
            'signer': signer,
            'metrics': metrics,
            'percentile_profit': float((df['total_profit'] >= row['total_profit']).sum() / len(df) * 100),
        }
    
    # Pool attack patterns analysis (inferred from sandwich ratios)
    for idx, (_, row) in enumerate(top10.iterrows(), 1):
        signer = row['attacker_signer']
        fat_ratio = row['fat_sandwiches'] / (row['fat_sandwiches'] + row['sandwiches'] + 0.001)
        summary['attack_patterns']['fat_sandwich_dominance'][signer[:20]] = {
            'fat_sandwich_ratio': float(fat_ratio),
            'pattern_type': 'highly_specialized' if fat_ratio > 0.95 else 
                           'fat_sandwich_focused' if fat_ratio > 0.75 else
                           'mixed_strategy' if fat_ratio > 0.4 else
                           'standard_sandwich_focus',
        }
        
        summary['attack_patterns']['profit_efficiency'][signer[:20]] = {
            'profit_per_attack': float(row['total_profit'] / row['num_attacks']),
            'efficiency_score': float((row['total_profit'] / row['num_attacks']) / df['total_profit'].max() * 100),
        }
    
    # Average metrics
    summary['average_metrics'] = {
        'average_total_profit_top_10': float(top10['total_profit'].mean()),
        'average_fat_sandwiches_top_10': float(top10['fat_sandwiches'].mean()),
        'average_regular_sandwiches_top_10': float(top10['sandwiches'].mean()),
        'average_num_attacks_top_10': float(top10['num_attacks'].mean()),
        'average_roi_top_10': float(top10['avg_roi'].mean()),
    }
    
    # Write JSON
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return output_path


def print_analysis_summary(top_df: pd.DataFrame, detailed_analysis: Dict):
    """Print detailed summary of top 5 signers."""
    print("\n" + "="*80)
    print("TOP 5 SIGNERS DETAILED ANALYSIS")
    print("="*80)
    
    for rank, signer_data in detailed_analysis.items():
        print(f"\n{'─'*80}")
        print(f"RANK #{rank}: {signer_data['signer']}")
        print(f"{'─'*80}")
        
        metrics = signer_data['metrics']
        
        print(f"  Profit Metrics:")
        print(f"    • Total Profit:                 {metrics['total_profit']:.4f} SOL")
        print(f"    • Average Profit per Attack:    {metrics['average_profit_per_attack']:.4f} SOL")
        print(f"    • Profit per Sandwich:          {metrics['profit_per_sandwich']:.4f} SOL")
        
        print(f"\n  Attack Statistics:")
        print(f"    • Fat Sandwich Attacks:         {metrics['fat_sandwich_attacks']}")
        print(f"    • Regular Sandwich Attacks:     {metrics['regular_sandwich_attacks']}")
        print(f"    • Total Sandwich Attacks:       {metrics['total_sandwich_attacks']}")
        print(f"    • Fat Sandwich Ratio:           {metrics['fat_sandwich_ratio']*100:.1f}%")
        print(f"    • Total Attacks:                {metrics['total_attacks']}")
        
        print(f"\n  ROI & Efficiency:")
        print(f"    • Average ROI:                  {metrics['avg_roi_percent']}%")
        
        print(f"\n  Inferred/Estimated Metrics:")
        print(f"    • Estimated Unique Victims:     {metrics['estimated_unique_victims']}")
        print(f"    • Estimated Pools Targeted:     {metrics['estimated_pools_targeted']}")
        print(f"    • Estimated Slots Involved:     {metrics['estimated_slots_involved']}")
        print(f"    • Estimated Average Hops:       {metrics['estimated_average_hops']:.1f}")
    
    print(f"\n{'='*80}\n")


def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("MEV SIGNERS ATTACK PATTERN ANALYSIS")
    print("="*80 + "\n")
    
    # Load data
    df = load_data(CSV_PATH)
    
    # Analyze top 5 signers for detailed reporting
    top5_df, detailed_analysis = analyze_top_signers(df, top_n=5)
    print_analysis_summary(top5_df, detailed_analysis)
    
    # Create visualizations
    print("Creating visualizations...")
    
    viz1_path = str(OUTPUT_DIR / "1_top_attackers_profit_roi.png")
    print(f"  ✓ Creating Visualization 1: {viz1_path}")
    create_visualization_1(df, viz1_path)
    
    viz2_path = str(OUTPUT_DIR / "2_attack_composition.png")
    print(f"  ✓ Creating Visualization 2: {viz2_path}")
    create_visualization_2(df, viz2_path)
    
    viz3_path = str(OUTPUT_DIR / "3_profit_per_attack_type.png")
    print(f"  ✓ Creating Visualization 3: {viz3_path}")
    create_visualization_3(df, viz3_path)
    
    # Generate JSON summary
    print(f"\nGenerating JSON summary...")
    json_path = generate_json_summary(df, JSON_OUTPUT_PATH)
    print(f"  ✓ JSON Summary: {json_path}")
    
    # Print summary of created files
    print("\n" + "="*80)
    print("CREATED FILES SUMMARY")
    print("="*80)
    print(f"\nVisualization Files (PNG):")
    print(f"  1. {viz1_path}")
    print(f"  2. {viz2_path}")
    print(f"  3. {viz3_path}")
    print(f"\nData Files (JSON):")
    print(f"  • {json_path}")
    print("\n" + "="*80 + "\n")
    
    return {
        'visualizations': [viz1_path, viz2_path, viz3_path],
        'json_summary': json_path
    }


if __name__ == "__main__":
    results = main()
