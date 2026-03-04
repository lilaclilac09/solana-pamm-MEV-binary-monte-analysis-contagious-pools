#!/usr/bin/env python3
"""
Slot Jump MEV Visualization Generator
======================================

Creates visualizations for slot jump and DobleZero MEV analysis.

Author: MEV Analysis Team
Date: March 3, 2026
"""

import json
import argparse
import re
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List

# Set visualization style
sns.set_style("whitegrid")
sns.set_palette("husl")


def _repair_invalid_json_escapes(raw_text: str) -> str:
    fixed_text = re.sub(r'(?<!\\)\\u(?![0-9a-fA-F]{4})', r'\\\\u', raw_text)
    fixed_text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', fixed_text)
    return fixed_text


def _load_json_safe(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file_handle:
        raw_text = file_handle.read()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        repaired_text = _repair_invalid_json_escapes(raw_text)
        if repaired_text != raw_text:
            print(f"⚠️ Repaired invalid JSON escape sequences in {filepath}")
            return json.loads(repaired_text)
        raise


class SlotJumpVisualizer:
    """Generate visualizations for slot jump MEV analysis"""
    
    def __init__(self, output_dir: str = "outputs/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self, filepath: str) -> Dict:
        """Load analysis results JSON"""
        return _load_json_safe(filepath)
    
    def plot_jump_distribution(self, slot_data: Dict, filename: str = "jump_distribution.png"):
        """Plot distribution of slot jump sizes"""
        jumps = slot_data.get('jump_events', [])
        jump_sizes = [j['jump_size'] for j in jumps]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(jump_sizes, bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Jump Size (slots)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Distribution of Slot Jump Sizes', fontsize=14, fontweight='bold')
        ax1.grid(alpha=0.3)
        
        # Box plot by type
        jump_types = {}
        for jump in jumps:
            jtype = jump['jump_type']
            if jtype not in jump_types:
                jump_types[jtype] = []
            jump_types[jtype].append(jump['jump_size'])
        
        ax2.boxplot(jump_types.values(), labels=jump_types.keys())
        ax2.set_xlabel('Jump Type', fontsize=12)
        ax2.set_ylabel('Jump Size (slots)', fontsize=12)
        ax2.set_title('Jump Size by Type', fontsize=14, fontweight='bold')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created: {filename}")
    
    def plot_mev_correlation(self, correlation_data: Dict, filename: str = "mev_correlation.png"):
        """Plot MEV correlation with slot jumps"""
        window_stats = correlation_data.get('window_statistics', [])
        
        # Organize by window type
        pre_jump = [w for w in window_stats if w['window_type'] == 'pre_jump']
        during_jump = [w for w in window_stats if w['window_type'] == 'during_jump']
        post_jump = [w for w in window_stats if w['window_type'] == 'post_jump']
        
        # Extract MEV values
        pre_values = [w['total_mev_value_usd'] for w in pre_jump]
        during_values = [w['total_mev_value_usd'] for w in during_jump]
        post_values = [w['total_mev_value_usd'] for w in post_jump]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Bar plot of averages
        window_labels = ['Pre-Jump', 'During Jump', 'Post-Jump']
        avg_values = [
            np.mean(pre_values) if pre_values else 0,
            np.mean(during_values) if during_values else 0,
            np.mean(post_values) if post_values else 0
        ]
        
        bars = ax1.bar(window_labels, avg_values, color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.7)
        ax1.set_ylabel('Average MEV Value (USD)', fontsize=12)
        ax1.set_title('MEV Value by Time Window', fontsize=14, fontweight='bold')
        ax1.grid(alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.2f}',
                    ha='center', va='bottom', fontsize=10)
        
        # Box plot comparison
        data_to_plot = []
        labels = []
        if pre_values:
            data_to_plot.append(pre_values)
            labels.append('Pre')
        if during_values:
            data_to_plot.append(during_values)
            labels.append('During')
        if post_values:
            data_to_plot.append(post_values)
            labels.append('Post')
        
        if data_to_plot:
            bp = ax2.boxplot(data_to_plot, labels=labels, patch_artist=True)
            colors = ['#3498db', '#e74c3c', '#2ecc71']
            for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax2.set_ylabel('MEV Value (USD)', fontsize=12)
            ax2.set_xlabel('Time Window', fontsize=12)
            ax2.set_title('MEV Distribution by Window', fontsize=14, fontweight='bold')
            ax2.grid(alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created: {filename}")
    
    def plot_doblezero_profiles(self, doblezero_data: Dict, filename: str = "doblezero_profiles.png"):
        """Plot DobleZero validator profiles"""
        candidates = doblezero_data.get('candidates', [])
        
        if not candidates:
            print("No DobleZero candidates to plot")
            return
        
        # Get top 15 candidates
        top_candidates = sorted(candidates, key=lambda x: x['confidence_score'], reverse=True)[:15]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Confidence scores
        names = [f"V{i+1}" for i in range(len(top_candidates))]
        confidences = [c['confidence_score'] for c in top_candidates]
        
        bars = ax1.barh(names, confidences, color='#e74c3c', alpha=0.7)
        ax1.set_xlabel('Confidence Score', fontsize=12)
        ax1.set_title('DobleZero Confidence Scores (Top 15)', fontsize=14, fontweight='bold')
        ax1.axvline(x=0.7, color='green', linestyle='--', label='High Confidence Threshold')
        ax1.legend()
        ax1.grid(alpha=0.3, axis='x')
        
        # 2. Skip rate vs MEV correlation
        skip_rates = [c['skip_rate'] * 100 for c in top_candidates]
        mev_corr = [c['mev_correlation'] for c in top_candidates]
        
        scatter = ax2.scatter(skip_rates, mev_corr, s=100, alpha=0.6, c=confidences, cmap='RdYlGn')
        ax2.set_xlabel('Skip Rate (%)', fontsize=12)
        ax2.set_ylabel('MEV Correlation', fontsize=12)
        ax2.set_title('Skip Rate vs MEV Correlation', fontsize=14, fontweight='bold')
        ax2.grid(alpha=0.3)
        plt.colorbar(scatter, ax=ax2, label='Confidence')
        
        # 3. Pattern regularity distribution
        regularities = [c['pattern_regularity'] for c in top_candidates]
        ax3.hist(regularities, bins=15, color='#3498db', alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Pattern Regularity', fontsize=12)
        ax3.set_ylabel('Count', fontsize=12)
        ax3.set_title('Skip Pattern Regularity Distribution', fontsize=14, fontweight='bold')
        ax3.axvline(x=0.6, color='red', linestyle='--', label='High Regularity')
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        # 4. Profitability ratios
        profit_ratios = [c['profitability_ratio'] for c in top_candidates]
        colors_profit = ['green' if p > 1.2 else 'orange' for p in profit_ratios]
        
        ax4.barh(names, profit_ratios, color=colors_profit, alpha=0.7)
        ax4.set_xlabel('Profitability Ratio', fontsize=12)
        ax4.set_title('Economic Profitability (MEV/Block Rewards)', fontsize=14, fontweight='bold')
        ax4.axvline(x=1.0, color='black', linestyle='-', linewidth=0.5, label='Break Even')
        ax4.axvline(x=1.2, color='green', linestyle='--', linewidth=1, label='Profitable Strategy')
        ax4.legend()
        ax4.grid(alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created: {filename}")
    
    def plot_oracle_staleness(self, staleness_data: Dict, filename: str = "oracle_staleness.png"):
        """Plot oracle staleness analysis"""
        events = staleness_data.get('staleness_events', [])
        
        if not events:
            print("No staleness events to plot")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Staleness duration distribution
        durations = [e['staleness_duration_slots'] for e in events]
        ax1.hist(durations, bins=30, color='#e67e22', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Staleness Duration (slots)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Oracle Staleness Duration Distribution', fontsize=14, fontweight='bold')
        ax1.axvline(x=10, color='yellow', linestyle='--', label='Warning (10 slots)')
        ax1.axvline(x=20, color='red', linestyle='--', label='Critical (20 slots)')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. Price deviation scatter
        durations_for_scatter = [e['staleness_duration_slots'] for e in events]
        price_devs = [e['price_deviation_percent'] for e in events]
        
        ax2.scatter(durations_for_scatter, price_devs, alpha=0.6, s=50)
        ax2.set_xlabel('Staleness Duration (slots)', fontsize=12)
        ax2.set_ylabel('Price Deviation (%)', fontsize=12)
        ax2.set_title('Staleness vs Price Deviation', fontsize=14, fontweight='bold')
        ax2.grid(alpha=0.3)
        
        # 3. MEV opportunities by staleness
        mev_counts = [e['mev_opportunities_created'] for e in events]
        categories = ['0', '1-2', '3-5', '6-10', '>10']
        categorized = {cat: 0 for cat in categories}
        
        for count in mev_counts:
            if count == 0:
                categorized['0'] += 1
            elif count <= 2:
                categorized['1-2'] += 1
            elif count <= 5:
                categorized['3-5'] += 1
            elif count <= 10:
                categorized['6-10'] += 1
            else:
                categorized['>10'] += 1
        
        ax3.bar(categories, categorized.values(), color='#9b59b6', alpha=0.7)
        ax3.set_xlabel('MEV Opportunities Created', fontsize=12)
        ax3.set_ylabel('Number of Staleness Events', fontsize=12)
        ax3.set_title('MEV Opportunities per Staleness Event', fontsize=14, fontweight='bold')
        ax3.grid(alpha=0.3, axis='y')
        
        # 4. Oracle type breakdown
        oracle_types = {}
        for event in events:
            otype = event.get('oracle_type', 'unknown')
            oracle_types[otype] = oracle_types.get(otype, 0) + 1
        
        ax4.pie(oracle_types.values(), labels=oracle_types.keys(), autopct='%1.1f%%', startangle=90)
        ax4.set_title('Staleness Events by Oracle Type', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created: {filename}")
    
    def generate_all_visualizations(
        self,
        slot_data_path: str,
        correlation_data_path: str,
        doblezero_data_path: str,
        staleness_data_path: str
    ):
        """Generate all visualizations"""
        print("Generating visualizations...")
        print(f"Output directory: {self.output_dir}")
        
        try:
            slot_data = self.load_data(slot_data_path)
            self.plot_jump_distribution(slot_data)
        except Exception as e:
            print(f"Warning: Could not create jump distribution plot: {e}")
        
        try:
            correlation_data = self.load_data(correlation_data_path)
            self.plot_mev_correlation(correlation_data)
        except Exception as e:
            print(f"Warning: Could not create MEV correlation plot: {e}")
        
        try:
            doblezero_data = self.load_data(doblezero_data_path)
            self.plot_doblezero_profiles(doblezero_data)
        except Exception as e:
            print(f"Warning: Could not create DobleZero profiles plot: {e}")
        
        try:
            staleness_data = self.load_data(staleness_data_path)
            self.plot_oracle_staleness(staleness_data)
        except Exception as e:
            print(f"Warning: Could not create oracle staleness plot: {e}")
        
        print(f"\n✓ Visualizations complete! Check {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate visualizations for slot jump MEV analysis'
    )
    parser.add_argument(
        '--slot-data',
        type=str,
        default='data/slot_jump_analysis.json',
        help='Path to slot jump analysis JSON'
    )
    parser.add_argument(
        '--correlation-data',
        type=str,
        default='data/mev_slot_correlation.json',
        help='Path to MEV correlation JSON'
    )
    parser.add_argument(
        '--doblezero-data',
        type=str,
        default='data/doblezero_profiles.json',
        help='Path to DobleZero profiles JSON'
    )
    parser.add_argument(
        '--staleness-data',
        type=str,
        default='data/oracle_staleness_analysis.json',
        help='Path to oracle staleness JSON'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs/visualizations',
        help='Output directory for plots'
    )
    
    args = parser.parse_args()
    
    visualizer = SlotJumpVisualizer(output_dir=args.output_dir)
    
    visualizer.generate_all_visualizations(
        slot_data_path=args.slot_data,
        correlation_data_path=args.correlation_data,
        doblezero_data_path=args.doblezero_data,
        staleness_data_path=args.staleness_data
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
