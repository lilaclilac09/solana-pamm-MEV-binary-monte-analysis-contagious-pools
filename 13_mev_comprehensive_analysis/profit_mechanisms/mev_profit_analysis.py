"""
MEV Profit Mechanisms Analysis
=============================

Comprehensive analysis of how MEV attackers:
1. Execute front-running trades
2. Generate profits from sandwich attacks
3. Manage transaction costs vs profits
4. Exploit price differences and atomic patterns
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Data path
MEV_DATA_PATH = '../02_mev_detection/filtered_output/top20_profit_fat_sandwich.csv'
CLEAN_DATA_PATH = '../01_data_cleaning/outputs/pamm_clean_final.parquet'

class MEVProfitAnalyzer:
    """Analyze MEV profit generation mechanisms"""
    
    def __init__(self, mev_file, clean_file):
        """Initialize analyzer with MEV and clean data"""
        self.mev_df = pd.read_csv(mev_file)
        self.clean_df = pd.read_parquet(clean_file)
        self.results = {}
        
    def analyze_profit_generation(self):
        """Analyze how profits are generated"""
        print("\n" + "="*80)
        print("MEV PROFIT GENERATION MECHANISMS")
        print("="*80)
        
        # 1. Overall profit statistics
        print("\n### 1. PROFIT STATISTICS ###")
        print(f"Total cases analyzed: {len(self.mev_df)}")
        print(f"Total gross profit: {self.mev_df['profit_sol'].sum():.2f} SOL")
        print(f"Total transaction costs: {self.mev_df['cost_sol'].sum():.2f} SOL")
        print(f"Total net profit: {self.mev_df['net_profit_sol'].sum():.2f} SOL")
        
        print(f"\nPer-transaction statistics:")
        print(f"  Avg gross profit: {self.mev_df['profit_sol'].mean():.4f} SOL")
        print(f"  Avg transaction cost: {self.mev_df['cost_sol'].mean():.4f} SOL")
        print(f"  Avg net profit: {self.mev_df['net_profit_sol'].mean():.4f} SOL")
        print(f"  Median net profit: {self.mev_df['net_profit_sol'].median():.4f} SOL")
        print(f"  Max profit: {self.mev_df['net_profit_sol'].max():.4f} SOL")
        print(f"  Min profit: {self.mev_df['net_profit_sol'].min():.4f} SOL")
        
        # 2. Profit margin analysis
        print("\n### 2. PROFIT MARGIN ANALYSIS ###")
        self.mev_df['profit_margin'] = (
            self.mev_df['net_profit_sol'] / self.mev_df['profit_sol'] * 100
        )
        self.mev_df['roi'] = (
            self.mev_df['net_profit_sol'] / self.mev_df['cost_sol'] * 100
        )
        
        print(f"Average profit margin (net/gross): {self.mev_df['profit_margin'].mean():.2f}%")
        print(f"Average ROI (net profit/cost): {self.mev_df['roi'].mean():.2f}%")
        print(f"Median ROI: {self.mev_df['roi'].median():.2f}%")
        
        # 3. Attack type analysis
        print("\n### 3. PROFIT BY ATTACK TYPE ###")
        attack_types = {
            'Fat Sandwich': self.mev_df[self.mev_df['fat_sandwich'] > 0],
            'Front Running': self.mev_df[self.mev_df['front_running'] > 0],
            'Back Running': self.mev_df[self.mev_df['back_running'] > 0],
            'Sandwich': self.mev_df[self.mev_df['sandwich'] > 0]
        }
        
        for attack_type, df_subset in attack_types.items():
            if len(df_subset) > 0:
                print(f"\n{attack_type}:")
                print(f"  Occurrences: {len(df_subset)}")
                print(f"  Total net profit: {df_subset['net_profit_sol'].sum():.2f} SOL")
                print(f"  Avg net profit: {df_subset['net_profit_sol'].mean():.4f} SOL")
                print(f"  Avg ROI: {df_subset['roi'].mean():.2f}%")
        
        # 4. Cost efficiency analysis
        print("\n### 4. COST EFFICIENCY ANALYSIS ###")
        self.mev_df['cost_fraction'] = (
            self.mev_df['cost_sol'] / self.mev_df['profit_sol'] * 100
        )
        
        print(f"Average cost as % of gross profit: {self.mev_df['cost_fraction'].mean():.2f}%")
        print(f"Median cost as % of gross profit: {self.mev_df['cost_fraction'].median():.2f}%")
        
        cost_efficiency = pd.cut(
            self.mev_df['cost_fraction'],
            bins=[0, 10, 25, 50, 100],
            labels=['<10%', '10-25%', '25-50%', '>50%']
        )
        print(f"\nCost efficiency distribution:")
        print(cost_efficiency.value_counts().sort_index())
        
        self.results['profit_analysis'] = {
            'total_net_profit': self.mev_df['net_profit_sol'].sum(),
            'avg_net_profit': self.mev_df['net_profit_sol'].mean(),
            'avg_roi': self.mev_df['roi'].mean(),
            'avg_cost_fraction': self.mev_df['cost_fraction'].mean()
        }
        
    def analyze_sandwich_mechanics(self):
        """Analyze how sandwich attacks are executed"""
        print("\n" + "="*80)
        print("SANDWICH ATTACK EXECUTION MECHANICS")
        print("="*80)
        
        sandwich_df = self.mev_df[self.mev_df['sandwich'] > 0].copy()
        print(f"\nTotal sandwich attacks: {len(sandwich_df)}")
        
        # 1. Sandwich size distribution
        print("\n### 1. SANDWICH POSITIONING ###")
        print(f"Total transactions in sandwich attacks: {sandwich_df['sandwich'].sum()}")
        print(f"Average transactions per sandwich: {sandwich_df['sandwich'].mean():.1f}")
        
        sandwich_bins = pd.cut(
            sandwich_df['sandwich'],
            bins=[0, 1, 3, 5, 10, 1000],
            labels=['1tx', '2-3tx', '4-5tx', '6-10tx', '>10tx']
        )
        print(f"\nSandwich size distribution:")
        print(sandwich_bins.value_counts().sort_index())
        
        # 2. Sandwich completion rates
        print("\n### 2. SANDWICH COMPLETION RATES ###")
        completion_rate = (sandwich_df['sandwich_complete'].sum() / len(sandwich_df)) * 100
        print(f"Successful sandwich completions: {sandwich_df['sandwich_complete'].sum()}/{len(sandwich_df)} ({completion_rate:.1f}%)")
        
        complete = sandwich_df[sandwich_df['sandwich_complete'] == 1]
        incomplete = sandwich_df[sandwich_df['sandwich_complete'] == 0]
        
        if len(complete) > 0:
            print(f"\nCompleted sandwiches:")
            print(f"  Avg net profit: {complete['net_profit_sol'].mean():.4f} SOL")
            print(f"  Avg ROI: {complete['roi'].mean():.2f}%")
        
        if len(incomplete) > 0:
            print(f"\nIncomplete sandwiches:")
            print(f"  Avg net profit: {incomplete['net_profit_sol'].mean():.4f} SOL")
            print(f"  Avg ROI: {incomplete['roi'].mean():.2f}%")
            print(f"  (Still profitable even without completion)")
        
        # 3. Pool participation in sandwiches
        print("\n### 3. POOLS EXPLOITED BY SANDWICHES ###")
        pool_counts = sandwich_df['amm_trade'].value_counts()
        print(f"\nTop 10 pools exploited:")
        for pool, count in pool_counts.head(10).items():
            pool_data = sandwich_df[sandwich_df['amm_trade'] == pool]
            avg_profit = pool_data['net_profit_sol'].mean()
            total_profit = pool_data['net_profit_sol'].sum()
            print(f"  {pool}: {count} attacks, {total_profit:.2f} SOL total, {avg_profit:.4f} SOL avg")
        
        self.results['sandwich_mechanics'] = {
            'total_attacks': len(sandwich_df),
            'completion_rate': completion_rate,
            'avg_sandwich_size': sandwich_df['sandwich'].mean()
        }
        
    def analyze_frontrun_mechanics(self):
        """Analyze front-running execution"""
        print("\n" + "="*80)
        print("FRONT-RUNNING EXECUTION MECHANICS")
        print("="*80)
        
        fr_df = self.mev_df[self.mev_df['front_running'] > 0].copy()
        print(f"\nTotal front-running attacks: {len(fr_df)}")
        
        if len(fr_df) > 0:
            print(f"Total transactions exploited: {fr_df['front_running'].sum()}")
            print(f"Avg transactions per attack: {fr_df['front_running'].mean():.1f}")
            
            print(f"\nProfit statistics:")
            print(f"  Total net profit: {fr_df['net_profit_sol'].sum():.2f} SOL")
            print(f"  Avg net profit: {fr_df['net_profit_sol'].mean():.4f} SOL")
            print(f"  Avg ROI: {fr_df['roi'].mean():.2f}%")
            
            print(f"\nCost efficiency:")
            print(f"  Avg cost fraction: {fr_df['cost_fraction'].mean():.2f}%")
        else:
            print("No front-running cases in top 20")
        
    def analyze_attacker_behavior(self):
        """Analyze individual attacker patterns"""
        print("\n" + "="*80)
        print("ATTACKER BEHAVIOR PATTERNS")
        print("="*80)
        
        # 1. Top attackers
        print("\n### 1. TOP ATTACKERS BY PROFIT ###")
        attacker_profits = self.mev_df.groupby('attacker_signer').agg({
            'net_profit_sol': ['sum', 'mean', 'count'],
            'roi': 'mean',
            'cost_fraction': 'mean'
        }).round(4)
        attacker_profits.columns = ['total_profit', 'avg_profit', 'num_attacks', 'avg_roi', 'avg_cost_fraction']
        attacker_profits = attacker_profits.sort_values('total_profit', ascending=False)
        
        print(f"\nTop 10 attackers:")
        for idx, (signer, row) in enumerate(attacker_profits.head(10).iterrows(), 1):
            print(f"{idx}. {signer[:16]}...")
            print(f"   Total profit: {row['total_profit']:.2f} SOL | Attacks: {int(row['num_attacks'])}")
            print(f"   Avg profit: {row['avg_profit']:.4f} SOL | Avg ROI: {row['avg_roi']:.2f}%")
        
        # 2. Attacker specialization
        print("\n### 2. ATTACKER SPECIALIZATION ###")
        attacker_focus = self.mev_df.groupby('attacker_signer').agg({
            'fat_sandwich': 'sum',
            'front_running': 'sum',
            'sandwich': 'sum',
            'back_running': 'sum'
        })
        
        attacker_focus['primary_attack'] = attacker_focus.idxmax(axis=1)
        specialization = attacker_focus['primary_attack'].value_counts()
        print(f"\nAttacker specialization (primary attack type):")
        for attack_type, count in specialization.items():
            pct = (count / len(attacker_focus)) * 100
            print(f"  {attack_type}: {count} attackers ({pct:.1f}%)")
        
        self.results['attacker_patterns'] = {
            'top_attacker': attacker_profits.index[0],
            'top_attacker_profit': float(attacker_profits.iloc[0]['total_profit']),
            'num_unique_attackers': len(attacker_profits)
        }
        
    def analyze_validator_relationship(self):
        """Analyze validator and attacker relationships"""
        print("\n" + "="*80)
        print("VALIDATOR & ATTACKER RELATIONSHIPS")
        print("="*80)
        
        # 1. Validator concentration
        print("\n### 1. VALIDATOR CONCENTRATION ###")
        validator_counts = self.mev_df['validator'].value_counts()
        print(f"Unique validators involved: {len(validator_counts)}")
        print(f"Total profit across validators: {self.mev_df.groupby('validator')['net_profit_sol'].sum().sum():.2f} SOL")
        
        print(f"\nTop 10 validators by attack frequency:")
        for idx, (validator, count) in enumerate(validator_counts.head(10).items(), 1):
            val_data = self.mev_df[self.mev_df['validator'] == validator]
            avg_profit = val_data['net_profit_sol'].mean()
            total_profit = val_data['net_profit_sol'].sum()
            print(f"{idx}. {validator[:16]}... - {count} attacks, {total_profit:.2f} SOL total")
        
        # 2. Validator-attacker pairings
        print("\n### 2. VALIDATOR-ATTACKER PAIRINGS ###")
        pairs = self.mev_df.groupby(['validator', 'attacker_signer']).size().reset_index(name='count')
        pairs = pairs.sort_values('count', ascending=False)
        print(f"\nMost frequent validator-attacker pairs:")
        for idx, (_, row) in enumerate(pairs.head(5).iterrows(), 1):
            pair_data = self.mev_df[
                (self.mev_df['validator'] == row['validator']) &
                (self.mev_df['attacker_signer'] == row['attacker_signer'])
            ]
            profit = pair_data['net_profit_sol'].sum()
            print(f"{idx}. {row['attacker_signer'][:12]}... → {row['validator'][:12]}...")
            print(f"   Frequency: {int(row['count'])} | Profit: {profit:.2f} SOL")
        
    def analyze_pool_exploitation(self):
        """Analyze which pools are most exploited"""
        print("\n" + "="*80)
        print("POOL EXPLOITATION ANALYSIS")
        print("="*80)
        
        # 1. Most exploited pools
        print("\n### 1. MOST EXPLOITED POOLS ###")
        pool_stats = self.mev_df.groupby('amm_trade').agg({
            'net_profit_sol': ['sum', 'mean', 'count'],
            'cost_sol': 'mean',
            'confidence': lambda x: (x == 'high').sum() / len(x) * 100
        }).round(4)
        pool_stats.columns = ['total_profit', 'avg_profit', 'num_attacks', 'avg_cost', 'high_confidence_pct']
        pool_stats = pool_stats.sort_values('total_profit', ascending=False)
        
        print(f"\nTop 15 exploited pools:")
        for idx, (pool, row) in enumerate(pool_stats.head(15).iterrows(), 1):
            print(f"{idx}. {pool}")
            print(f"   Total profit: {row['total_profit']:.2f} SOL | Attacks: {int(row['num_attacks'])}")
            print(f"   Avg profit per attack: {row['avg_profit']:.4f} SOL")
            print(f"   High confidence: {row['high_confidence_pct']:.1f}%")
        
        # 2. Pool vulnerability metrics
        print("\n### 2. POOL VULNERABILITY METRICS ###")
        vulnerable_pools = pool_stats[pool_stats['num_attacks'] >= 3]
        print(f"\nPools with 3+ attacks: {len(vulnerable_pools)}")
        print(f"Total attacks on vulnerable pools: {int(vulnerable_pools['num_attacks'].sum())}")
        print(f"Total profit from vulnerable pools: {vulnerable_pools['total_profit'].sum():.2f} SOL")
        
        self.results['pool_analysis'] = {
            'total_pools_exploited': len(pool_stats),
            'most_exploited_pool': pool_stats.index[0],
            'most_exploited_pool_profit': float(pool_stats.iloc[0]['total_profit'])
        }
        
    def analyze_confidence_patterns(self):
        """Analyze confidence scores and success patterns"""
        print("\n" + "="*80)
        print("CONFIDENCE & VERIFICATION ANALYSIS")
        print("="*80)
        
        # 1. Confidence distribution
        print("\n### 1. CONFIDENCE DISTRIBUTION ###")
        confidence_counts = self.mev_df['confidence'].value_counts()
        for conf, count in confidence_counts.items():
            conf_data = self.mev_df[self.mev_df['confidence'] == conf]
            profit = conf_data['net_profit_sol'].sum()
            pct = (count / len(self.mev_df)) * 100
            print(f"{conf}: {count} cases ({pct:.1f}%) | Total profit: {profit:.2f} SOL")
        
        # 2. High confidence analysis
        print("\n### 2. HIGH CONFIDENCE VS OTHERS ###")
        high_conf = self.mev_df[self.mev_df['confidence'] == 'high']
        low_conf = self.mev_df[self.mev_df['confidence'] != 'high']
        
        print(f"\nHigh confidence attacks:")
        print(f"  Count: {len(high_conf)}")
        print(f"  Avg ROI: {high_conf['roi'].mean():.2f}%")
        print(f"  Success rate: {(high_conf['sandwich_complete'].sum() / len(high_conf) * 100):.1f}%")
        
        if len(low_conf) > 0:
            print(f"\nOther confidence levels:")
            print(f"  Count: {len(low_conf)}")
            print(f"  Avg ROI: {low_conf['roi'].mean():.2f}%")
    
    def save_results(self, output_dir='./outputs'):
        """Save analysis results"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save summary
        summary_df = self.mev_df[[
            'amm_trade', 'attacker_signer', 'validator',
            'profit_sol', 'cost_sol', 'net_profit_sol',
            'roi', 'profit_margin', 'confidence'
        ]].sort_values('net_profit_sol', ascending=False)
        summary_df.to_csv(f'{output_dir}/mev_profit_summary.csv', index=False)
        
        # Save attacker analysis
        attacker_stats = self.mev_df.groupby('attacker_signer').agg({
            'net_profit_sol': ['sum', 'mean', 'count'],
            'roi': 'mean',
            'fat_sandwich': 'sum',
            'sandwich': 'sum'
        }).round(4)
        attacker_stats.columns = ['total_profit', 'avg_profit', 'num_attacks', 'avg_roi', 'fat_sandwiches', 'sandwiches']
        attacker_stats = attacker_stats.sort_values('total_profit', ascending=False)
        attacker_stats.to_csv(f'{output_dir}/attacker_statistics.csv')
        
        # Save pool analysis
        pool_stats = self.mev_df.groupby('amm_trade').agg({
            'net_profit_sol': ['sum', 'mean', 'count'],
            'confidence': lambda x: (x == 'high').sum(),
            'validator': 'nunique'
        }).round(4)
        pool_stats.columns = ['total_profit', 'avg_profit', 'num_attacks', 'high_confidence_attacks', 'unique_validators']
        pool_stats = pool_stats.sort_values('total_profit', ascending=False)
        pool_stats.to_csv(f'{output_dir}/pool_exploitation_statistics.csv')
        
        # Save results summary
        with open(f'{output_dir}/analysis_summary.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Results saved to {output_dir}/")

def main():
    """Run complete MEV profit analysis"""
    try:
        analyzer = MEVProfitAnalyzer(MEV_DATA_PATH, CLEAN_DATA_PATH)
        
        # Run all analyses
        analyzer.analyze_profit_generation()
        analyzer.analyze_sandwich_mechanics()
        analyzer.analyze_frontrun_mechanics()
        analyzer.analyze_attacker_behavior()
        analyzer.analyze_validator_relationship()
        analyzer.analyze_pool_exploitation()
        analyzer.analyze_confidence_patterns()
        
        # Save results
        analyzer.save_results()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except FileNotFoundError as e:
        print(f"⚠️  Data file not found: {e}")
        print("Ensure you're running from the correct directory with access to MEV data")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
