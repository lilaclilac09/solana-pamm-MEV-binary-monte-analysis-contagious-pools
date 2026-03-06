#!/usr/bin/env python3
"""
Comprehensive Data Consistency Validator for MEV Analysis
Checks for inconsistencies in net_profit, top attackers, and data integrity across all files
"""

import pandas as pd
import os
import hashlib
from pathlib import Path
import numpy as np

# ANSI color codes for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{RESET}\n")

def print_error(text):
    print(f"{RED}❌ ERROR: {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  WARNING: {text}{RESET}")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def get_file_hash(filepath):
    """Calculate MD5 hash of file for comparison"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def check_duplicate_files():
    """Check for duplicate files in different directories"""
    print_header("1. CHECKING FOR DUPLICATE FILES")
    
    file_pairs = [
        (
            '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv',
            '02_mev_detection/filtered_output/all_fat_sandwich_only.csv'
        ),
        (
            '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_mev_with_classification.csv',
            '02_mev_detection/filtered_output/all_mev_with_classification.csv'
        ),
        (
            '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/top10_fat_sandwich.csv',
            '02_mev_detection/filtered_output/top10_fat_sandwich.csv'
        ),
        (
            '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/top20_profit_fat_sandwich.csv',
            '02_mev_detection/filtered_output/top20_profit_fat_sandwich.csv'
        ),
    ]
    
    inconsistencies = []
    
    for file1, file2 in file_pairs:
        if os.path.exists(file1) and os.path.exists(file2):
            hash1 = get_file_hash(file1)
            hash2 = get_file_hash(file2)
            
            if hash1 != hash2:
                print_error(f"Files differ:")
                print(f"  - {file1}")
                print(f"  - {file2}")
                inconsistencies.append((file1, file2))
                
                # Compare content
                try:
                    df1 = pd.read_csv(file1)
                    df2 = pd.read_csv(file2)
                    print(f"    File 1: {len(df1)} rows, {len(df1.columns)} columns")
                    print(f"    File 2: {len(df2)} rows, {len(df2.columns)} columns")
                    
                    if len(df1) != len(df2):
                        print_error(f"    Row count mismatch: {len(df1)} vs {len(df2)}")
                except Exception as e:
                    print_error(f"    Could not compare: {e}")
            else:
                print_success(f"Files identical: {os.path.basename(file1)}")
        elif os.path.exists(file1):
            print_warning(f"Only exists in 13_mev_comprehensive_analysis: {os.path.basename(file1)}")
        elif os.path.exists(file2):
            print_warning(f"Only exists in 02_mev_detection: {os.path.basename(file2)}")
    
    return inconsistencies

def check_net_profit_consistency():
    """Check net_profit values across all files"""
    print_header("2. CHECKING NET_PROFIT CONSISTENCY")
    
    # Load main filtered data
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    
    if not os.path.exists(main_file):
        print_error(f"Main file not found: {main_file}")
        return False
    
    df_main = pd.read_csv(main_file)
    print(f"Loaded main file: {len(df_main)} records")
    
    # Check for net_profit column
    profit_col = None
    for col in ['net_profit_sol', 'net_profit', 'profit_sol', 'profit']:
        if col in df_main.columns:
            profit_col = col
            break
    
    if profit_col is None:
        print_error("No profit column found in main file!")
        print(f"Available columns: {', '.join(df_main.columns)}")
        return False
    
    print_success(f"Using profit column: {profit_col}")
    
    # Analyze profit data
    print(f"\nProfit Statistics:")
    print(f"  Total profit: {df_main[profit_col].sum():.6f} SOL")
    print(f"  Mean profit: {df_main[profit_col].mean():.6f} SOL")
    print(f"  Median profit: {df_main[profit_col].median():.6f} SOL")
    print(f"  Min profit: {df_main[profit_col].min():.6f} SOL")
    print(f"  Max profit: {df_main[profit_col].max():.6f} SOL")
    
    # Check for anomalies
    zero_profit = df_main[df_main[profit_col] == 0]
    negative_profit = df_main[df_main[profit_col] < 0]
    null_profit = df_main[df_main[profit_col].isna()]
    
    if len(zero_profit) > 0:
        print_error(f"Found {len(zero_profit)} records with ZERO profit in filtered data!")
        print(f"  Sample indices: {zero_profit.index.tolist()[:5]}")
    
    if len(negative_profit) > 0:
        print_error(f"Found {len(negative_profit)} records with NEGATIVE profit!")
        print(f"  Sample indices: {negative_profit.index.tolist()[:5]}")
    
    if len(null_profit) > 0:
        print_error(f"Found {len(null_profit)} records with NULL profit!")
    
    if len(zero_profit) == 0 and len(negative_profit) == 0 and len(null_profit) == 0:
        print_success("All profit values are positive and valid!")
    
    return True

def check_top_attackers_consistency():
    """Check top attacker rankings across different files"""
    print_header("3. CHECKING TOP ATTACKERS CONSISTENCY")
    
    # Load main file
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df_main = pd.read_csv(main_file)
    
    # Find signer column
    signer_col = None
    for col in ['signer', 'attacker_signer', 'attacker', 'wallet']:
        if col in df_main.columns:
            signer_col = col
            break
    
    if signer_col is None:
        print_error("No signer column found!")
        return False
    
    # Find profit column
    profit_col = None
    for col in ['net_profit_sol', 'net_profit', 'profit_sol', 'profit']:
        if col in df_main.columns:
            profit_col = col
            break
    
    # Calculate top attackers from main file
    top_attackers_calculated = df_main.groupby(signer_col).agg({
        profit_col: 'sum',
        signer_col: 'count'
    }).rename(columns={signer_col: 'attack_count', profit_col: 'total_profit'})
    top_attackers_calculated = top_attackers_calculated.sort_values('total_profit', ascending=False)
    
    print(f"\nTop 10 Attackers (calculated from {len(df_main)} records):")
    print("-" * 80)
    for i, (signer, row) in enumerate(top_attackers_calculated.head(10).iterrows(), 1):
        print(f"{i:2d}. {signer}: {row['total_profit']:.6f} SOL ({int(row['attack_count'])} attacks)")
    
    # Load and compare with top10 file if it exists
    top10_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/top10_fat_sandwich.csv'
    if os.path.exists(top10_file):
        print(f"\nComparing with {top10_file}:")
        df_top10 = pd.read_csv(top10_file)
        
        # Find relevant columns
        top10_signer_col = None
        for col in ['signer', 'attacker_signer', 'attacker', 'wallet']:
            if col in df_top10.columns:
                top10_signer_col = col
                break
        
        top10_profit_col = None
        for col in ['total_profit', 'total_profit_sol', 'net_profit_sol', 'profit']:
            if col in df_top10.columns:
                top10_profit_col = col
                break
        
        if top10_signer_col and top10_profit_col:
            # Compare top 10
            calculated_top10 = top_attackers_calculated.head(10)
            file_top10_signers = df_top10[top10_signer_col].tolist()
            calc_top10_signers = calculated_top10.index.tolist()
            
            if file_top10_signers == calc_top10_signers:
                print_success("Top 10 attacker order matches!")
            else:
                print_error("Top 10 attacker order MISMATCH!")
                print("\nFrom file:")
                for i, row in df_top10.iterrows():
                    print(f"  {i+1}. {row[top10_signer_col]}: {row[top10_profit_col]:.6f} SOL")
                
                print("\nCalculated:")
                for i, (signer, row) in enumerate(calculated_top10.iterrows(), 1):
                    print(f"  {i}. {signer}: {row['total_profit']:.6f} SOL")
    
    # Load and compare with top20 profit file
    top20_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/top20_profit_fat_sandwich.csv'
    if os.path.exists(top20_file):
        print(f"\nChecking {top20_file}:")
        df_top20 = pd.read_csv(top20_file)
        print(f"  Contains {len(df_top20)} records")
        
        # Check if these are truly the top 20
        calculated_top20_signers = set(top_attackers_calculated.head(20).index)
        
        # Find signer column in top20 file
        if signer_col in df_top20.columns:
            file_top20_signers = set(df_top20[signer_col].unique())
            
            if calculated_top20_signers == file_top20_signers:
                print_success(f"Top 20 profit attackers match!")
            else:
                missing = calculated_top20_signers - file_top20_signers
                extra = file_top20_signers - calculated_top20_signers
                if missing:
                    print_error(f"Missing from file: {missing}")
                if extra:
                    print_error(f"Extra in file: {extra}")
    
    return True

def check_classification_consistency():
    """Check that all records in filtered file have correct classification"""
    print_header("4. CHECKING CLASSIFICATION CONSISTENCY")
    
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    print(f"Analyzing {len(df)} filtered records...")
    
    # Check for classification column
    if 'mev_type' in df.columns:
        classification_counts = df['mev_type'].value_counts()
        print(f"\nClassification breakdown:")
        for mev_type, count in classification_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {mev_type}: {count} ({pct:.1f}%)")
        
        # All should be FAT_SANDWICH
        non_fat_sandwich = df[df['mev_type'] != 'FAT_SANDWICH']
        if len(non_fat_sandwich) > 0:
            print_error(f"Found {len(non_fat_sandwich)} non-FAT_SANDWICH records in filtered file!")
            print(f"  Types: {non_fat_sandwich['mev_type'].value_counts()}")
        else:
            print_success("All records are FAT_SANDWICH as expected!")
    else:
        print_warning("No mev_type column found")
    
    return True

def check_aggregator_separation():
    """Verify that aggregators and MEV bots are properly separated"""
    print_header("5. CHECKING AGGREGATOR/MEV SEPARATION")
    
    # Load filtered MEV data
    mev_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df_mev = pd.read_csv(mev_file)
    
    # Load aggregator list
    agg_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/aggregators_with_pools.csv'
    if not os.path.exists(agg_file):
        print_warning(f"Aggregator file not found: {agg_file}")
        return True
    
    df_agg = pd.read_csv(agg_file)
    
    # Find signer column in MEV data
    signer_col = None
    for col in ['signer', 'attacker_signer', 'attacker']:
        if col in df_mev.columns:
            signer_col = col
            break
    
    # Find signer column in aggregator data
    agg_signer_col = None
    for col in ['signer', 'aggregator_signer', 'wallet']:
        if col in df_agg.columns:
            agg_signer_col = col
            break
    
    if signer_col and agg_signer_col:
        mev_signers = set(df_mev[signer_col].unique())
        agg_signers = set(df_agg[agg_signer_col].unique())
        
        overlap = mev_signers & agg_signers
        
        print(f"MEV attackers: {len(mev_signers)}")
        print(f"Aggregators: {len(agg_signers)}")
        print(f"Overlap: {len(overlap)}")
        
        if len(overlap) > 0:
            print_error(f"Found {len(overlap)} signers in BOTH MEV and aggregator lists!")
            print(f"  Examples: {list(overlap)[:5]}")
            
            # Check impact
            overlap_records = df_mev[df_mev[signer_col].isin(overlap)]
            print(f"  Affected MEV records: {len(overlap_records)}")
            
            if 'net_profit_sol' in overlap_records.columns:
                overlap_profit = overlap_records['net_profit_sol'].sum()
                total_profit = df_mev['net_profit_sol'].sum()
                print(f"  Affected profit: {overlap_profit:.6f} SOL ({overlap_profit/total_profit*100:.1f}%)")
        else:
            print_success("No overlap between MEV attackers and aggregators!")
    
    return True

def generate_summary_report():
    """Generate a summary report of all inconsistencies found"""
    print_header("VALIDATION SUMMARY")
    
    # Reload main file for final statistics
    main_file = '13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv'
    df = pd.read_csv(main_file)
    
    print(f"Main Dataset: {main_file}")
    print(f"  Total records: {len(df)}")
    print(f"  Unique attackers: {df['signer'].nunique() if 'signer' in df.columns else 'Unknown'}")
    
    if 'net_profit_sol' in df.columns:
        print(f"  Total profit: {df['net_profit_sol'].sum():.6f} SOL")
        print(f"  Average profit: {df['net_profit_sol'].mean():.6f} SOL")
    
    if 'pool' in df.columns:
        print(f"  Unique pools: {df['pool'].nunique()}")
    
    print(f"\nValidation complete!")

def main():
    print_header("MEV DATA CONSISTENCY VALIDATION")
    print(f"Working directory: {os.getcwd()}")
    
    # Run all checks
    check_duplicate_files()
    check_net_profit_consistency()
    check_top_attackers_consistency()
    check_classification_consistency()
    check_aggregator_separation()
    generate_summary_report()

if __name__ == '__main__':
    main()
