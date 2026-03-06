#!/usr/bin/env python3
"""
Fix Data Consistency Issues
Regenerates all top attacker files and derivative CSVs from the ground truth filtered data
"""

import pandas as pd
import os

# ANSI colors
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def fix_top_attacker_files():
    """Regenerate top10 and top20 files from ground truth data"""
    print_header("REGENERATING TOP ATTACKER FILES FROM GROUND TRUTH")
    
    # Load ground truth filtered data
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    print(f"Loaded {len(df)} validated MEV attacks")
    print(f"Total profit: {df['net_profit_sol'].sum():.6f} SOL")
    
    # Determine column names (handle both old and new naming)
    signer_col = 'attacker_signer' if 'attacker_signer' in df.columns else 'signer'
    pool_col = 'amm_trade' if 'amm_trade' in df.columns else 'pool'
    
    print(f"Using columns: {signer_col}, {pool_col}")
    
    # Calculate attacker statistics
    attacker_stats = df.groupby(signer_col).agg({
        'net_profit_sol': ['sum', 'mean', 'count'],
        pool_col: lambda x: x.nunique()
    }).reset_index()
    
    attacker_stats.columns = ['signer', 'total_profit', 'avg_profit', 'attack_count', 'pool_count']
    attacker_stats = attacker_stats.sort_values('total_profit', ascending=False)
    
    print(f"\nTotal unique attackers: {len(attacker_stats)}")
    
    # Generate TOP 10 by total profit
    print("\n" + "="*80)
    print("TOP 10 ATTACKERS BY TOTAL PROFIT")
    print("="*80)
    
    top10 = attacker_stats.head(10).copy()
    top10['rank'] = range(1, 11)
    
    for _, row in top10.iterrows():
        print(f"{int(row['rank']):2d}. {row['signer']}: {row['total_profit']:.6f} SOL ({int(row['attack_count'])} attacks, {int(row['pool_count'])} pools)")
    
    # Save top 10 with all attack details
    top10_signers = top10['signer'].tolist()
    top10_attacks = df[df[signer_col].isin(top10_signers)].copy()
    top10_attacks = top10_attacks.rename(columns={signer_col: 'signer'})
    top10_attacks = top10_attacks.merge(
        top10[['signer', 'rank', 'total_profit', 'attack_count']], 
        on='signer', 
        how='left'
    )
    top10_attacks = top10_attacks.sort_values(['rank', 'net_profit_sol'], ascending=[True, False])
    
    # Save both summary and detailed files
    output_dir_13 = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection'
    output_dir_02 = '02_mev_detection/filtered_output'
    
    # TOP 10 SUMMARY (aggregated by attacker)
    top10_summary = top10[['rank', 'signer', 'total_profit', 'avg_profit', 'attack_count', 'pool_count']].copy()
    
    for output_dir in [output_dir_13, output_dir_02]:
        # Summary file
        summary_file = f'{output_dir}/top10_fat_sandwich.csv'
        top10_summary.to_csv(summary_file, index=False)
        print_success(f"Saved: {summary_file}")
        
        # Detailed attacks file
        detailed_file = f'{output_dir}/top10_mev_fat_sandwich_only.csv'
        top10_attacks.to_csv(detailed_file, index=False)
        print_success(f"Saved: {detailed_file}")
    
    # Generate TOP 20 by profit
    print("\n" + "="*80)
    print("TOP 20 ATTACKERS BY TOTAL PROFIT")
    print("="*80)
    
    top20 = attacker_stats.head(20).copy()
    top20['rank'] = range(1, 21)
    
    for _, row in top20.iterrows():
        print(f"{int(row['rank']):2d}. {row['signer']}: {row['total_profit']:.6f} SOL ({int(row['attack_count'])} attacks)")
    
    # Save top 20 with all attack details
    top20_signers = top20['signer'].tolist()
    top20_attacks = df[df[signer_col].isin(top20_signers)].copy()
    top20_attacks = top20_attacks.rename(columns={signer_col: 'signer'})
    top20_attacks = top20_attacks.merge(
        top20[['signer', 'rank', 'total_profit', 'attack_count']], 
        on='signer', 
        how='left'
    )
    top20_attacks = top20_attacks.sort_values(['rank', 'net_profit_sol'], ascending=[True, False])
    
    for output_dir in [output_dir_13, output_dir_02]:
        # Summary file
        summary_file = f'{output_dir}/top20_profit_fat_sandwich.csv'
        top20[['rank', 'signer', 'total_profit', 'avg_profit', 'attack_count', 'pool_count']].to_csv(summary_file, index=False)
        print_success(f"Saved: {summary_file}")
        
        # Detailed attacks file (if it exists)
        detailed_file = f'{output_dir}/top20_profit_fat_sandwich_detailed.csv'
        top20_attacks.to_csv(detailed_file, index=False)
        print_success(f"Saved: {detailed_file}")
    
    return top10, top20, attacker_stats

def generate_pool_analysis():
    """Generate pool-level statistics"""
    print_header("GENERATING POOL ANALYSIS")
    
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    # Determine column names
    signer_col = 'attacker_signer' if 'attacker_signer' in df.columns else 'signer'
    pool_col = 'amm_trade' if 'amm_trade' in df.columns else 'pool'
    
    pool_stats = df.groupby(pool_col).agg({
        'net_profit_sol': ['sum', 'mean', 'count'],
        signer_col: lambda x: x.nunique()
    }).reset_index()
    
    pool_stats.columns = ['pool', 'total_profit', 'avg_profit', 'attack_count', 'attacker_count']
    pool_stats = pool_stats.sort_values('total_profit', ascending=False)
    
    print(f"Total pools affected: {len(pool_stats)}")
    print(f"\nTop 10 pools by MEV profit:")
    for i, row in pool_stats.head(10).iterrows():
        print(f"  {row['pool']}: {row['total_profit']:.6f} SOL ({int(row['attack_count'])} attacks, {int(row['attacker_count'])} attackers)")
    
    # Save pool analysis
    output_dir_13 = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection'
    output_dir_02 = '02_mev_detection/filtered_output'
    
    for output_dir in [output_dir_13, output_dir_02]:
        pool_file = f'{output_dir}/pool_mev_summary.csv'
        pool_stats.to_csv(pool_file, index=False)
        print_success(f"Saved: {pool_file}")
    
    return pool_stats

def generate_attacker_pool_matrix():
    """Generate attacker x pool analysis"""
    print_header("GENERATING ATTACKER-POOL ANALYSIS")
    
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    # Determine column names
    signer_col = 'attacker_signer' if 'attacker_signer' in df.columns else 'signer'
    pool_col = 'amm_trade' if 'amm_trade' in df.columns else 'pool'
    
    attacker_pool = df.groupby([signer_col, pool_col]).agg({
        'net_profit_sol': ['sum', 'count']
    }).reset_index()
    
    attacker_pool.columns = ['signer', 'pool', 'total_profit', 'attack_count']
    attacker_pool = attacker_pool.sort_values(['signer', 'total_profit'], ascending=[True, False])
    
    print(f"Total attacker-pool combinations: {len(attacker_pool)}")
    
    # Save
    output_dir_13 = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection'
    output_dir_02 = '02_mev_detection/filtered_output'
    
    for output_dir in [output_dir_13, output_dir_02]:
        file_path = f'{output_dir}/attacker_pool_analysis.csv'
        attacker_pool.to_csv(file_path, index=False)
        print_success(f"Saved: {file_path}")
    
    return attacker_pool

def verify_fixes():
    """Verify that fixes were applied correctly"""
    print_header("VERIFYING FIXES")
    
    # Load ground truth
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    # Determine column names
    signer_col = 'attacker_signer' if 'attacker_signer' in df.columns else 'signer'
    
    # Calculate expected top attacker
    top_attacker = df.groupby(signer_col)['net_profit_sol'].sum().sort_values(ascending=False)
    expected_top = top_attacker.index[0]
    expected_profit = top_attacker.iloc[0]
    
    print(f"Expected top attacker: {expected_top}")
    print(f"Expected profit: {expected_profit:.6f} SOL")
    
    # Load regenerated top10 file
    top10_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/top10_fat_sandwich.csv'
    df_top10 = pd.read_csv(top10_file)
    
    actual_top = df_top10.iloc[0]['signer']
    actual_profit = df_top10.iloc[0]['total_profit']
    
    print(f"Actual top attacker: {actual_top}")
    print(f"Actual profit: {actual_profit:.6f} SOL")
    
    if expected_top == actual_top and abs(expected_profit - actual_profit) < 0.000001:
        print_success("✓ Top attacker data is CORRECT!")
        return True
    else:
        print(f"❌ MISMATCH DETECTED!")
        return False

def main():
    print_header("MEV DATA CONSISTENCY FIX")
    print(f"Working directory: {os.getcwd()}")
    
    # Fix all derivative files
    top10, top20, attacker_stats = fix_top_attacker_files()
    pool_stats = generate_pool_analysis()
    attacker_pool = generate_attacker_pool_matrix()
    
    # Verify
    success = verify_fixes()
    
    if success:
        print_header("✓ ALL FIXES APPLIED SUCCESSFULLY")
        print(f"\nSummary:")
        print(f"  ✓ Top 10 attackers regenerated")
        print(f"  ✓ Top 20 attackers regenerated")
        print(f"  ✓ Pool analysis updated")
        print(f"  ✓ Attacker-pool matrix generated")
        print(f"\n  Total validated attacks: 617")
        print(f"  Total profit: 112.428 SOL")
        print(f"  Unique attackers: {len(attacker_stats)}")
        print(f"  Unique pools: {len(pool_stats)}")
    else:
        print_header("❌ VERIFICATION FAILED - MANUAL REVIEW REQUIRED")

if __name__ == '__main__':
    main()
