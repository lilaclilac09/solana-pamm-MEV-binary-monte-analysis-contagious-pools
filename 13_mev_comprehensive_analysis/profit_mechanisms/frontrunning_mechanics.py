"""
Front-Running Mechanics & Attack Execution Analysis
===================================================

Detailed analysis of:
1. How attacks are executed in transaction order
2. Price impact mechanisms
3. Multi-legged swap patterns
4. Attacker profit capture strategies
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

MEV_DATA_PATH = '../02_mev_detection/filtered_output/top20_profit_fat_sandwich.csv'

class FrontRunningAnalyzer:
    """Analyze front-running attack mechanics"""
    
    def __init__(self, mev_file):
        self.df = pd.read_csv(mev_file)
        
        # Calculate derived metrics if not present
        if 'roi' not in self.df.columns:
            self.df['roi'] = (
                self.df['net_profit_sol'] / self.df['cost_sol'] * 100
            )
        if 'profit_margin' not in self.df.columns:
            self.df['profit_margin'] = (
                self.df['net_profit_sol'] / self.df['profit_sol'] * 100
            )
        if 'cost_fraction' not in self.df.columns:
            self.df['cost_fraction'] = (
                self.df['cost_sol'] / self.df['profit_sol'] * 100
            )
        
        self.df['sandwich_size_category'] = pd.cut(
            self.df['fat_sandwich'],
            bins=[0, 100, 500, 1000, 2000, 5000],
            labels=['tiny', 'small', 'medium', 'large', 'massive']
        )
        
    def analyze_attack_execution_sequence(self):
        """Analyze the ordering and timing of attacks"""
        print("\n" + "="*80)
        print("ATTACK EXECUTION SEQUENCE ANALYSIS")
        print("="*80)
        
        # 1. Transaction count patterns
        print("\n### 1. TRANSACTION SEQUENCING ###")
        print(f"\nSandwich attack complexity distribution:")
        print(f"\n{'Category':<12} {'Count':<8} {'Avg Size':<12} {'Total Profit':<15} {'Median ROI':<12}")
        print("-" * 60)
        
        for category in ['tiny', 'small', 'medium', 'large', 'massive']:
            subset = self.df[self.df['sandwich_size_category'] == category]
            if len(subset) > 0:
                print(f"{category:<12} {len(subset):<8} {subset['fat_sandwich'].mean():<12.0f} {subset['net_profit_sol'].sum():<15.2f} {subset['roi'].median():<12.1f}%")
        
        # 2. Front-running vs back-running balance
        print("\n\n### 2. FRONT-RUN vs BACK-RUN DYNAMICS ###")
        
        # Classify attacks by strategy
        self.df['is_sandwich'] = (
            (self.df['fat_sandwich'] > 0) | 
            (self.df['front_running'] > 0) | 
            (self.df['back_running'] > 0)
        )
        
        sandwich_attacks = self.df[self.df['is_sandwich']].copy()
        
        sandwich_attacks['attack_type'] = 'sandwich'
        sandwich_attacks.loc[
            (sandwich_attacks['front_running'] > 0) & 
            (sandwich_attacks['back_running'] == 0),
            'attack_type'
        ] = 'front_only'
        sandwich_attacks.loc[
            (sandwich_attacks['back_running'] > 0) & 
            (sandwich_attacks['front_running'] == 0),
            'attack_type'
        ] = 'back_only'
        
        print(f"\nAttack strategy distribution:")
        for attack_type in sandwich_attacks['attack_type'].unique():
            subset = sandwich_attacks[sandwich_attacks['attack_type'] == attack_type]
            profit = subset['net_profit_sol'].sum()
            count = len(subset)
            pct = (count / len(sandwich_attacks)) * 100
            print(f"  {attack_type}: {count} cases ({pct:.1f}%) | Total profit: {profit:.2f} SOL")
        
        # 3. Completion success patterns
        print("\n\n### 3. COMPLETION SUCCESS PATTERNS ###")
        print(f"\nSandwich completion analysis:")
        print(f"  Total sandwich attacks: {len(sandwich_attacks)}")
        
        complete = sandwich_attacks[sandwich_attacks['sandwich_complete'] == 1]
        incomplete = sandwich_attacks[sandwich_attacks['sandwich_complete'] == 0]
        
        if len(complete) > 0:
            print(f"\n  ✅ SUCCESSFUL (sandwich closed):")
            print(f"     Count: {len(complete)}")
            print(f"     Avg transaction count: {complete['fat_sandwich'].mean():.0f}")
            print(f"     Avg net profit: {complete['net_profit_sol'].mean():.4f} SOL")
            print(f"     Avg ROI: {complete['roi'].mean():.2f}%")
            print(f"     This requires executing both front AND back run successfully")
        
        if len(incomplete) > 0:
            print(f"\n  ⚠️  INCOMPLETE (only front-run captured):")
            print(f"     Count: {len(incomplete)}")
            print(f"     Avg transaction count: {incomplete['fat_sandwich'].mean():.0f}")
            print(f"     Avg net profit: {incomplete['net_profit_sol'].mean():.4f} SOL")
            print(f"     Avg ROI: {incomplete['roi'].mean():.2f}%")
            print(f"     Still profitable - can capture price movement without back-run")
    
    def analyze_price_impact_mechanics(self):
        """Analyze how price impact generates profit"""
        print("\n" + "="*80)
        print("PRICE IMPACT & PROFIT GENERATION MECHANICS")
        print("="*80)
        
        print("\n### PROFIT EXTRACTION MECHANISM ###")
        print("\nTypical sandwich attack price impact:")
        print("""
        [INITIAL STATE]
        Pool: 100M Token A, 1000 SOL
        Price: 1 Token A = 0.01 SOL
        
        [PHASE 1: ATTACKER FRONT-RUN]
        Attacker: Buy 10M Token A (~100K SOL spent)
        New pool: 110M Token A, ~900 SOL
        New price: 1 Token A = 0.0082 SOL (moved unfavorably for buyers)
        
        [PHASE 2: VICTIM EXECUTES]
        Victim: Sells 20M Token A to pool
        Pool impact: Price falls further (more Token A dumped)
        Pool now: ~130M Token A, ~770 SOL
        New price: 1 Token A = 0.0059 SOL
        
        [PHASE 3: ATTACKER BACK-RUN]
        Attacker: Sells 10M Token A they bought in Phase 1
        They sell at ~0.0059 SOL (worse than Phase 1 at 0.0082)
        BUT: Overall market moved down due to victim's dump
        Relative to victim's entry: Attacker captured the spread
        """)
        
        # 2. Quantitative profit analysis
        print("\n### QUANTITATIVE PROFIT ANALYSIS ###")
        
        # Create profit categories
        self.df['profit_size'] = pd.cut(
            self.df['net_profit_sol'],
            bins=[0, 1, 2, 5, 10, 100],
            labels=['<1 SOL', '1-2 SOL', '2-5 SOL', '5-10 SOL', '>10 SOL']
        )
        
        print(f"\nProfit distribution:")
        profit_dist = self.df['profit_size'].value_counts().sort_index()
        for profit_range, count in profit_dist.items():
            subset = self.df[self.df['profit_size'] == profit_range]
            total = subset['net_profit_sol'].sum()
            pct = (count / len(self.df)) * 100
            print(f"  {profit_range}: {count} cases ({pct:.1f}%) | Total: {total:.2f} SOL")
        
        # 3. Cost efficiency for different profit levels
        print("\n### COST EFFICIENCY BY PROFIT SIZE ###")
        print(f"\n{'Profit Range':<15} {'Avg Cost (SOL)':<18} {'Avg ROI':<15} {'Success Rate':<15}")
        print("-" * 65)
        
        for profit_range in ['<1 SOL', '1-2 SOL', '2-5 SOL', '5-10 SOL', '>10 SOL']:
            subset = self.df[self.df['profit_size'] == profit_range]
            if len(subset) > 0:
                avg_cost = subset['cost_sol'].mean()
                avg_roi = subset['roi'].mean()
                success_rate = (subset['sandwich_complete'].sum() / len(subset)) * 100
                print(f"{profit_range:<15} {avg_cost:<18.4f} {avg_roi:<15.1f}% {success_rate:<15.1f}%")
    
    def analyze_transaction_ordering(self):
        """Analyze how transaction ordering enables attacks"""
        print("\n" + "="*80)
        print("TRANSACTION ORDERING & MEMPOOL POSITIONING")
        print("="*80)
        
        print("\n### HOW ATTACKERS POSITION TRANSACTIONS ###")
        print("""
        Solana MEV exploits transaction ordering:
        
        1. MEMPOOL OBSERVATION
           - Attacker runs validator node or connects to one
           - Observes pending transactions before finalization
           - Identifies profitable opportunities
        
        2. PRIORITY POSITIONING
           - Increase tip/fee to get ordered first
           - Priority fees ensure front-position
           - Or position by transaction hash ordering
        
        3. ATOMIC EXECUTION
           - All transactions in same block = atomic execution
           - Impossible for victim to reject mid-sandwich
           - Multi-leg swaps computed atomically
        
        4. PROFIT CAPTURE
           - Use helper wallets to obscure origin
           - Different amounts to evade detection
           - Multiple strategies in same block
        """)
        
        # Analyze transaction clustering
        print("\n### TRANSACTION CLUSTERING ANALYSIS ###")
        
        # Group by validator to see clustering
        validator_stats = self.df.groupby('validator').agg({
            'net_profit_sol': ['sum', 'mean', 'count'],
            'fat_sandwich': 'mean'
        }).round(2)
        validator_stats.columns = ['total_profit', 'avg_profit', 'num_attacks', 'avg_tx_count']
        validator_stats = validator_stats.sort_values('num_attacks', ascending=False)
        
        print(f"\nValidator clustering (high attack frequency):")
        print(f"  Unique validators: {len(validator_stats)}")
        print(f"  Max attacks on single validator: {int(validator_stats['num_attacks'].max())}")
        
        for idx, (validator, row) in enumerate(validator_stats.head(5).iterrows(), 1):
            print(f"\n  {idx}. {validator[:20]}...")
            print(f"     Total attacks: {int(row['num_attacks'])}")
            print(f"     Avg transactions per attack: {row['avg_tx_count']:.0f}")
            print(f"     Total profit: {row['total_profit']:.2f} SOL")
    
    def analyze_multi_swap_patterns(self):
        """Analyze complex multi-leg swap patterns"""
        print("\n" + "="*80)
        print("MULTI-LEG SWAP PATTERN ANALYSIS")
        print("="*80)
        
        print("\n### COMPLEX ATTACK PATTERNS ###")
        
        # Identify most complex attacks
        complex_attacks = self.df.nlargest(5, 'fat_sandwich')[
            ['amm_trade', 'attacker_signer', 'fat_sandwich', 'sandwich', 
             'front_running', 'back_running', 'profit_sol', 'net_profit_sol']
        ]
        
        print(f"\nTop 5 Most Complex Attacks (by transaction count):")
        for idx, (_, row) in enumerate(complex_attacks.iterrows(), 1):
            print(f"\n{idx}. {row['amm_trade']}")
            print(f"   Total transactions: {int(row['fat_sandwich'])}")
            print(f"   Front-run txs: {int(row['front_running'])}")
            print(f"   Sandwich txs: {int(row['sandwich'])}")
            print(f"   Back-run txs: {int(row['back_running'])}")
            print(f"   Gross profit: {row['profit_sol']:.2f} SOL")
            print(f"   Net profit: {row['net_profit_sol']:.2f} SOL")
        
        # Pattern correlation
        print("\n\n### TX COUNT vs PROFIT CORRELATION ###")
        
        correlation = self.df[['fat_sandwich', 'net_profit_sol', 'roi']].corr()
        print(f"\nCorrelation matrix:")
        print(f"  Transactions vs Profit: {correlation.loc['fat_sandwich', 'net_profit_sol']:.3f}")
        print(f"  Transactions vs ROI: {correlation.loc['fat_sandwich', 'roi']:.3f}")
        
        print(f"\nInterpretation:")
        if correlation.loc['fat_sandwich', 'net_profit_sol'] > 0.7:
            print(f"  ✓ Strong positive correlation: More complex attacks = higher profits")
        elif correlation.loc['fat_sandwich', 'net_profit_sol'] > 0.3:
            print(f"  ✓ Moderate correlation: Complexity helps but other factors matter")
        else:
            print(f"  ✓ Weak correlation: Transaction count alone doesn't determine profit")
    
    def analyze_attack_frequency_patterns(self):
        """Analyze patterns in attack frequency and persistence"""
        print("\n" + "="*80)
        print("ATTACK FREQUENCY & PERSISTENCE PATTERNS")
        print("="*80)
        
        print("\n### ATTACKER PERSISTENCE ###")
        
        attacker_counts = self.df['attacker_signer'].value_counts()
        print(f"\nAttacker activity distribution:")
        print(f"  Unique attackers: {len(attacker_counts)}")
        print(f"  Max attacks by single attacker: {attacker_counts.max()}")
        print(f"  Avg attacks per attacker: {attacker_counts.mean():.1f}")
        
        # Categorize by persistence
        one_time = len(attacker_counts[attacker_counts == 1])
        repeat = len(attacker_counts[attacker_counts >= 2])
        frequent = len(attacker_counts[attacker_counts >= 3])
        
        print(f"\nPersistence categories:")
        print(f"  One-time attackers: {one_time} ({one_time/len(attacker_counts)*100:.1f}%)")
        print(f"  Repeat attackers (2+ attacks): {repeat} ({repeat/len(attacker_counts)*100:.1f}%)")
        print(f"  Frequent attackers (3+ attacks): {frequent} ({frequent/len(attacker_counts)*100:.1f}%)")
        
        # Efficiency of repeat vs one-time
        repeat_df = self.df[self.df['attacker_signer'].isin(
            attacker_counts[attacker_counts >= 2].index
        )]
        onetime_df = self.df[self.df['attacker_signer'].isin(
            attacker_counts[attacker_counts == 1].index
        )]
        
        print(f"\nProfitability comparison:")
        print(f"  Repeat attackers avg ROI: {repeat_df['roi'].mean():.2f}%")
        print(f"  One-time attackers avg ROI: {onetime_df['roi'].mean():.2f}%")
        print(f"  (Repeat attackers usually more skilled/efficient)")
    
    def save_execution_report(self, output_dir='./outputs'):
        """Save execution analysis report"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save attack patterns
        execution_df = self.df[[
            'amm_trade', 'attacker_signer', 'validator',
            'fat_sandwich', 'front_running', 'back_running', 'sandwich',
            'sandwich_complete', 'profit_sol', 'cost_sol', 'net_profit_sol', 'roi'
        ]].sort_values('fat_sandwich', ascending=False)
        
        execution_df.to_csv(f'{output_dir}/attack_execution_patterns.csv', index=False)
        print(f"\n✅ Execution report saved to {output_dir}/attack_execution_patterns.csv")

def main():
    """Run front-running mechanics analysis"""
    try:
        analyzer = FrontRunningAnalyzer(MEV_DATA_PATH)
        
        # Run analyses
        analyzer.analyze_attack_execution_sequence()
        analyzer.analyze_price_impact_mechanics()
        analyzer.analyze_transaction_ordering()
        analyzer.analyze_multi_swap_patterns()
        analyzer.analyze_attack_frequency_patterns()
        
        # Save results
        analyzer.save_execution_report()
        
        print("\n" + "="*80)
        print("FRONT-RUNNING MECHANICS ANALYSIS COMPLETE")
        print("="*80)
        
    except FileNotFoundError as e:
        print(f"⚠️  Data file not found: {e}")
        print("Ensure MEV data file exists")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
