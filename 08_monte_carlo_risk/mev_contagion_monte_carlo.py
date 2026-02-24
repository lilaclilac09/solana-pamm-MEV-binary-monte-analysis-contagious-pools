"""
Binary Monte Carlo Simulation for MEV Contagion + Infrastructure Scenarios
==========================================================================

Stochastic simulation testing:
- Baseline (current Jito) vs BAM privacy vs Harmony multi-builder
- Different oracle lag distributions  
- Impact on skipped-slot probability (congestion from failed attacks)

This module generates:
- Monte Carlo simulation results (100k+ iterations)
- Infrastructure scenario comparisons (Jito, BAM, Harmony)
- Quantified risk metrics (cascades, slots jumped, economic loss)
- Visualizations (distributions, comparisons, correlations)

Author: MEV Contagion Analysis Framework
Date: 2026-02-24
"""

import numpy as np
import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class ContagionMonteCarlo:
    """Binary Monte Carlo simulation for MEV contagion under different infrastructure scenarios."""
    
    def __init__(self, output_dir: str = './outputs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Scenario parameters (modifiable)
        self.scenarios = {
            'jito_baseline': {
                'name': 'Jito Baseline (Current)',
                'base_trigger_prob': 0.15,
                'cascade_rate': 0.801,
                'visibility_reduction': 0.0,
                'description': 'Current state with centralized MEV auctions'
            },
            'bam_privacy': {
                'name': 'BAM Privacy (65% visibility reduction)',
                'base_trigger_prob': 0.15,
                'cascade_rate': 0.801,
                'visibility_reduction': 0.65,
                'description': 'With encrypted transactions & threshold encryption'
            },
            'harmony_multibuilder': {
                'name': 'Harmony Multi-Builder (40% reduction + competition)',
                'base_trigger_prob': 0.15,
                'cascade_rate': 0.801,
                'visibility_reduction': 0.40,
                'competition_factor': 0.8,  # 20% reduction from competition
                'description': 'With multi-builder competition & validator separation'
            }
        }
        
        # Physical/network parameters
        self.network_params = {
            'oracle_lag_ms': 180,      # BisonFi baseline
            'slot_time_ms': 400,       # Solana slot ~ 400ms
            'runs_per_slot': 5,        # Possible cascade attempts per slot
            'skipped_slot_threshold': 3  # Jumps > 3 → high congestion risk
        }
        
        self.results = {}
        self.summary_stats = {}
        
    def load_contagion_report(self, report_path: str) -> Dict:
        """Load real cascade rate data from contagion_report.json."""
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            cascade_analysis = report.get('sections', {}).get('cascade_rate_analysis', {})
            cascade_rates = cascade_analysis.get('cascade_rates', {})
            
            actual_cascade_pct = cascade_rates.get('cascade_percentage', 0.0)
            print(f"✓ Loaded contagion report")
            print(f"  Actual cascade rate: {actual_cascade_pct:.2f}%")
            
            # Extract attack probabilities for downstream pools
            attack_probs = report.get('sections', {}).get('attack_probability_analysis', {})
            downstream_probs = attack_probs.get('downstream_attack_probabilities', [])
            
            return {
                'cascade_percentage': actual_cascade_pct,
                'downstream_pools': downstream_probs,
                'trigger_attacks_total': cascade_rates.get('trigger_attacks_total', 593)
            }
        except FileNotFoundError:
            print(f"⚠ Contagion report not found at {report_path}, using defaults")
            return {'cascade_percentage': 0.0, 'downstream_pools': []}
    
    def simulate_scenario(self,
                         scenario_key: str,
                         n_sims: int = 100_000,
                         oracle_lag_ms: Optional[float] = None,
                         real_cascade_data: Optional[Dict] = None) -> pd.DataFrame:
        """
        Run binary Monte Carlo simulation for a specific scenario.
        
        Parameters:
        -----------
        scenario_key : str
            'jito_baseline', 'bam_privacy', or 'harmony_multibuilder'
        n_sims : int
            Number of simulations to run (default: 100,000)
        oracle_lag_ms : float, optional
            Override default oracle lag (default: 180ms)
        real_cascade_data : dict, optional
            Real data from contagion_report.json
            
        Returns:
        --------
        pd.DataFrame
            Simulation results with columns: sim, trigger, cascades, slots_jumped, 
            total_loss, scenario, infrastructure_gap
        """
        
        scenario = self.scenarios[scenario_key]
        oracle_lag = oracle_lag_ms or self.network_params['oracle_lag_ms']
        
        # Extract parameters
        base_trigger_prob = scenario['base_trigger_prob']
        cascade_rate_base = scenario['cascade_rate']
        visibility_red = scenario['visibility_reduction']
        
        # Apply visibility reduction to cascade rate
        # More visibility → more predictable cascades → higher effective cascade rate
        effective_cascade_rate = cascade_rate_base * (1 - visibility_red)
        
        # Multi-builder competition reduces cascades further
        if 'competition_factor' in scenario:
            effective_cascade_rate *= scenario['competition_factor']
        
        results = []
        
        for sim in range(n_sims):
            # ===== STAGE 1: Binary trigger (attack initiated?) =====
            trigger = np.random.rand() < base_trigger_prob
            
            if trigger:
                # ===== STAGE 2: Binary cascade attempts =====
                # How many cascade opportunities in this slot?
                runs_per_slot = self.network_params['runs_per_slot']
                cascades = np.random.binomial(runs_per_slot, effective_cascade_rate)
                
                # ===== STAGE 3: Slot jumps (congestion proxy) =====
                # Each successful cascade causes latency → measured in "slots"
                # Assume: cascade takes 100-700ms, slot is 400ms
                if cascades > 0:
                    cascade_times = np.random.uniform(100, 700, cascades)
                    total_cascade_time = np.sum(cascade_times)
                    slots_jumped = int(np.ceil(total_cascade_time / self.network_params['slot_time_ms']))
                else:
                    slots_jumped = 0
                
                # ===== STAGE 4: Economic impact =====
                # Loss = base loss + oracle lag impact
                loss_per_cascade = 50 + oracle_lag * 0.3
                total_loss = cascades * loss_per_cascade + np.random.normal(0, 20)  # Add noise
                total_loss = max(0, total_loss)
                
                # ===== STAGE 5: Infrastructure gap =====
                # Quantify protection: how much this infra reduced damage vs baseline
                if scenario_key == 'jito_baseline':
                    infra_gap = 0.0
                else:
                    # Gap = (baseline_loss - scenario_loss) / baseline_loss
                    baseline_loss = 5 * (50 + oracle_lag * 0.3)  # Assume 5 cascades in jito
                    infra_gap = max(0, (baseline_loss - total_loss) / baseline_loss) if baseline_loss > 0 else 0
                
                results.append({
                    'sim': sim,
                    'trigger': int(trigger),
                    'cascades': int(cascades),
                    'slots_jumped': int(slots_jumped),
                    'total_loss': float(total_loss),
                    'scenario': scenario_key,
                    'scenario_name': scenario['name'],
                    'infra_gap': float(infra_gap),
                    'high_risk': int(slots_jumped > self.network_params['skipped_slot_threshold']),
                    'oracle_lag_ms': float(oracle_lag)
                })
            else:
                # No attack triggered
                results.append({
                    'sim': sim,
                    'trigger': 0,
                    'cascades': 0,
                    'slots_jumped': 0,
                    'total_loss': 0.0,
                    'scenario': scenario_key,
                    'scenario_name': scenario['name'],
                    'infra_gap': 0.0,
                    'high_risk': 0,
                    'oracle_lag_ms': float(oracle_lag)
                })
        
        df = pd.DataFrame(results)
        self.results[scenario_key] = df
        
        # Compute summary statistics
        self._compute_summary_stats(scenario_key, df)
        
        return df
    
    def _compute_summary_stats(self, scenario_key: str, df: pd.DataFrame):
        """Compute and store summary statistics for a scenario."""
        
        # Filter to triggered attacks only for more meaningful stats
        triggered = df[df['trigger'] == 1]
        
        stats = {
            'n_sims': len(df),
            'attack_rate': df['trigger'].mean(),
            'attack_rate_pct': df['trigger'].mean() * 100,
            'mean_cascades': triggered['cascades'].mean() if len(triggered) > 0 else 0.0,
            'median_cascades': triggered['cascades'].median() if len(triggered) > 0 else 0.0,
            'p90_cascades': triggered['cascades'].quantile(0.90) if len(triggered) > 0 else 0.0,
            'p99_cascades': triggered['cascades'].quantile(0.99) if len(triggered) > 0 else 0.0,
            'mean_slots_jumped': triggered['slots_jumped'].mean() if len(triggered) > 0 else 0.0,
            'p90_slots_jumped': triggered['slots_jumped'].quantile(0.90) if len(triggered) > 0 else 0.0,
            'p99_slots_jumped': triggered['slots_jumped'].quantile(0.99) if len(triggered) > 0 else 0.0,
            'mean_loss': triggered['total_loss'].mean() if len(triggered) > 0 else 0.0,
            'p90_loss': triggered['total_loss'].quantile(0.90) if len(triggered) > 0 else 0.0,
            'high_risk_rate': df['high_risk'].mean(),
            'high_risk_pct': df['high_risk'].mean() * 100,
            'mean_infra_gap': df['infra_gap'].mean()
        }
        
        self.summary_stats[scenario_key] = stats
        return stats
    
    def run_all_scenarios(self, n_sims: int = 100_000, 
                         contagion_report: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Run simulations for all infrastructure scenarios."""
        
        print("\n" + "="*80)
        print("BINARY MONTE CARLO: MEV CONTAGION + INFRASTRUCTURE SCENARIOS")
        print("="*80)
        
        # Load real contagion data if available
        real_data = None
        if contagion_report:
            real_data = self.load_contagion_report(contagion_report)
        
        # Run each scenario
        for scenario_key in self.scenarios.keys():
            print(f"\n▶ Running {self.scenarios[scenario_key]['name']}...")
            print(f"  Simulations: {n_sims:,}")
            
            df = self.simulate_scenario(scenario_key, n_sims, real_cascade_data=real_data)
            
            stats = self.summary_stats[scenario_key]
            print(f"  ✓ Attack rate: {stats['attack_rate_pct']:.2f}%")
            print(f"  ✓ Mean cascades (when triggered): {stats['mean_cascades']:.2f}")
            print(f"  ✓ P90 slots jumped: {stats['p90_slots_jumped']:.2f}")
            print(f"  ✓ High risk events: {stats['high_risk_pct']:.2f}%")
            print(f"  ✓ Mean infra gap: {stats['mean_infra_gap']:.2%}")
        
        return self.results
    
    def save_results(self, tag: str = ''):
        """Save all results to CSV files."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag_str = f"_{tag}" if tag else ""
        
        # Save individual scenario results
        for scenario_key, df in self.results.items():
            filename = f"monte_carlo_{scenario_key}{tag_str}_{timestamp}.csv"
            filepath = self.output_dir / filename
            df.to_csv(filepath, index=False)
            print(f"✓ Saved {len(df):,} simulation results → {filepath.name}")
        
        # Save summary statistics
        summary_df = pd.DataFrame(self.summary_stats).T
        summary_filename = f"monte_carlo_summary{tag_str}_{timestamp}.csv"
        summary_filepath = self.output_dir / summary_filename
        summary_df.to_csv(summary_filepath)
        print(f"✓ Saved summary statistics → {summary_filename}")
        
        return summary_filepath
    
    def generate_comparison_table(self) -> pd.DataFrame:
        """Generate infrastructure comparison table."""
        
        comparison = []
        
        for scenario_key, stats in self.summary_stats.items():
            scenario = self.scenarios[scenario_key]
            
            comparison.append({
                'Infrastructure': scenario['name'],
                'Attack Rate %': f"{stats['attack_rate_pct']:.2f}%",
                'Mean Cascades': f"{stats['mean_cascades']:.2f}",
                'P90 Cascades': f"{stats['p90_cascades']:.2f}",
                'P90 Slots': f"{stats['p90_slots_jumped']:.2f}",
                'Mean Loss': f"${stats['mean_loss']:.2f}",
                'High Risk %': f"{stats['high_risk_pct']:.2f}%",
                'Inefficiency vs Baseline': f"{stats['mean_infra_gap']:.1%}"
            })
        
        return pd.DataFrame(comparison)
    
    def plot_cascade_distributions(self, figsize: Tuple[int, int] = (14, 8)):
        """Plot cascade distributions across scenarios."""
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        colors = sns.color_palette("husl", len(self.results))
        
        # Plot 1: Cascade distribution
        ax = axes[0, 0]
        for (scenario_key, df), color in zip(self.results.items(), colors):
            triggered = df[df['trigger'] == 1]
            ax.hist(triggered['cascades'], bins=20, alpha=0.5, label=self.scenarios[scenario_key]['name'], color=color)
        ax.set_xlabel('Number of Cascades (per triggered attack)')
        ax.set_ylabel('Frequency')
        ax.set_title('Cascade Distribution by Infrastructure')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Slots jumped distribution
        ax = axes[0, 1]
        for (scenario_key, df), color in zip(self.results.items(), colors):
            triggered = df[df['trigger'] == 1]
            ax.hist(triggered['slots_jumped'], bins=20, alpha=0.5, label=self.scenarios[scenario_key]['name'], color=color)
        ax.set_xlabel('Slots Jumped (congestion proxy)')
        ax.set_ylabel('Frequency')
        ax.set_title('Slot Jump Distribution by Infrastructure')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Loss distribution
        ax = axes[1, 0]
        for (scenario_key, df), color in zip(self.results.items(), colors):
            triggered = df[df['trigger'] == 1]
            ax.hist(triggered['total_loss'], bins=20, alpha=0.5, label=self.scenarios[scenario_key]['name'], color=color)
        ax.set_xlabel('Total Loss ($)')
        ax.set_ylabel('Frequency')
        ax.set_title('Economic Loss Distribution by Infrastructure')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Summary statistics comparison
        ax = axes[1, 1]
        metrics = ['attack_rate_pct', 'mean_cascades', 'p90_slots_jumped', 'high_risk_pct']
        x = np.arange(len(metrics))
        width = 0.25
        
        for i, (scenario_key, stats) in enumerate(self.summary_stats.items()):
            values = [
                stats['attack_rate_pct'],
                stats['mean_cascades'],
                stats['p90_slots_jumped'],
                stats['high_risk_pct']
            ]
            ax.bar(x + i*width, values, width, label=self.scenarios[scenario_key]['name'], color=colors[i])
        
        ax.set_ylabel('Value')
        ax.set_title('Key Metrics Comparison')
        ax.set_xticks(x + width)
        ax.set_xticklabels(['Attack %', 'Mean Cascades', 'P90 Slots', 'High Risk %'], rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Save figure
        filename = f"monte_carlo_cascade_distributions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"\n✓ Saved visualization → {filename}")
        
        return fig
    
    def plot_infrastructure_comparison(self, figsize: Tuple[int, int] = (14, 8)):
        """Create detailed infrastructure comparison visualizations."""
        
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
        
        scenarios_list = list(self.results.keys())
        colors = sns.color_palette("husl", len(scenarios_list))
        
        # === Row 1: Risk metrics by infrastructure ===
        ax1 = fig.add_subplot(gs[0, :])
        
        metrics_data = {
            'Attack Rate (%)': [self.summary_stats[s]['attack_rate_pct'] for s in scenarios_list],
            'High Risk Events (%)': [self.summary_stats[s]['high_risk_pct'] for s in scenarios_list],
            'Mean Cascades': [self.summary_stats[s]['mean_cascades'] for s in scenarios_list],
            'P90 Slots': [self.summary_stats[s]['p90_slots_jumped'] for s in scenarios_list]
        }
        
        x = np.arange(len(scenarios_list))
        width = 0.2
        
        for i, (metric, values) in enumerate(metrics_data.items()):
            # Normalize for comparison
            max_val = max(values) if max(values) > 0 else 1
            normalized = [v / max_val * 100 for v in values]
            ax1.bar(x + i*width, normalized, width, label=metric, alpha=0.8)
        
        ax1.set_ylabel('Normalized Risk Score (%)')
        ax1.set_title('Risk Comparison: Normalized Metrics', fontweight='bold')
        ax1.set_xticks(x + 1.5*width)
        ax1.set_xticklabels([self.scenarios[s]['name'].split('(')[0] for s in scenarios_list], rotation=15, ha='right')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # === Row 2: Percentile analysis ===
        ax2 = fig.add_subplot(gs[1, 0])
        
        percentiles = [50, 75, 90, 95, 99]
        for scenario_key, color in zip(scenarios_list, colors):
            df = self.results[scenario_key]
            triggered = df[df['trigger'] == 1]
            values = [triggered['slots_jumped'].quantile(p/100) for p in percentiles]
            ax2.plot(percentiles, values, marker='o', label=self.scenarios[scenario_key]['name'], 
                    color=color, linewidth=2)
        
        ax2.set_xlabel('Percentile')
        ax2.set_ylabel('Slots Jumped')
        ax2.set_title('Slots Jumped Percentiles', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # === Loss efficiency ===
        ax3 = fig.add_subplot(gs[1, 1])
        
        loss_data = [self.summary_stats[s]['mean_loss'] for s in scenarios_list]
        scenario_names = [self.scenarios[s]['name'].split('(')[0] for s in scenarios_list]
        
        bars = ax3.bar(range(len(scenarios_list)), loss_data, color=colors, alpha=0.8)
        ax3.set_ylabel('Mean Loss ($)')
        ax3.set_title('Average Economic Loss', fontweight='bold')
        ax3.set_xticks(range(len(scenarios_list)))
        ax3.set_xticklabels(scenario_names, rotation=15, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.0f}', ha='center', va='bottom', fontsize=9)
        
        # === Infrastructure gap (protection benefit) ===
        ax4 = fig.add_subplot(gs[2, :])
        
        gap_data = [self.summary_stats[s]['mean_infra_gap'] for s in scenarios_list]
        
        bars = ax4.bar(range(len(scenarios_list)), gap_data, color=colors, alpha=0.8)
        ax4.set_ylabel('Infrastructure Efficiency Gap (%)')
        ax4.set_title('Protection Benefit vs Jito Baseline', fontweight='bold')
        ax4.set_xticks(range(len(scenarios_list)))
        ax4.set_xticklabels(scenario_names, rotation=15, ha='right')
        ax4.set_ylim([0, max(gap_data) * 1.2 if gap_data else 1])
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1%}', ha='center', va='bottom', fontsize=10)
        
        plt.suptitle('MEV Contagion: Infrastructure Scenario Comparison', 
                    fontsize=14, fontweight='bold', y=0.995)
        
        # Save
        filename = f"infrastructure_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ Saved infrastructure comparison → {filename}")
        
        return fig


def main():
    """Run complete Monte Carlo analysis."""
    
    # Initialize simulator
    mc = ContagionMonteCarlo(output_dir='./outputs')
    
    # Run simulations (100k iterations per scenario)
    results = mc.run_all_scenarios(n_sims=100_000, contagion_report='../contagion_report.json')
    
    # Print comparison table
    print("\n" + "="*80)
    print("INFRASTRUCTURE COMPARISON TABLE")
    print("="*80)
    comparison = mc.generate_comparison_table()
    print(comparison.to_string(index=False))
    
    # Save results
    mc.save_results(tag='comprehensive')
    
    # Generate visualizations
    mc.plot_cascade_distributions()
    mc.plot_infrastructure_comparison()
    
    print("\n✓ Monte Carlo analysis complete")
    print(f"✓ Results saved to {mc.output_dir}")
    
    return mc


if __name__ == '__main__':
    mc = main()
