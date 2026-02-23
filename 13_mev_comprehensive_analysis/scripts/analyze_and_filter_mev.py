"""
Analyze and Filter MEV CSVs: Remove Multi-Hop (FP) Cases, Keep Fat Sandwich Cases

This script:
1. Loads all MEV CSV files from 02_mev_detection
2. Classifies each case as Fat Sandwich vs Multi-Hop Arbitrage
3. Filters out multi-hop cases
4. Keeps only top MEV score cases
5. Generates clean output files
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
MEV_DETECTION_DIR = "/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis/02_mev_detection"
OUTPUT_DIR = f"{MEV_DETECTION_DIR}/filtered_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Files to process
CSV_FILES = {
    "top10_mev": f"{MEV_DETECTION_DIR}/per_pamm_top10_mev_with_validator.csv",
    "all_mev": f"{MEV_DETECTION_DIR}/per_pamm_all_mev_with_validator.csv",
    "mev_verification": f"{MEV_DETECTION_DIR}/mev_attacker_verification.csv",
    "mev_confidence": f"{MEV_DETECTION_DIR}/mev_confidence_breakdown.csv"
}


def classify_fat_sandwich_vs_multihop(row):
    """
    Classify a MEV case as Fat Sandwich or Multi-Hop Arbitrage
    
    Rules:
    - Fat Sandwich: sandwich_complete > 0, has front-run & back-run on same pair
    - Multi-Hop: front_running > 0, multiple different pools, no clear sandwich
    - Failed: Failed sandwich attempts or no profit
    """
    
    sandwich_count = row.get('sandwich', 0)
    sandwich_complete = row.get('sandwich_complete', 0)
    fat_sandwich = row.get('fat_sandwich', 0)
    front_running = row.get('front_running', 0)
    back_running = row.get('back_running', 0)
    net_profit = row.get('net_profit_sol', 0)
    confidence = row.get('confidence', 'medium')
    
    # Convert to numeric if needed
    try:
        sandwich_complete = float(sandwich_complete) if pd.notna(sandwich_complete) else 0
        fat_sandwich = float(fat_sandwich) if pd.notna(fat_sandwich) else 0
        sandwich_count = float(sandwich_count) if pd.notna(sandwich_count) else 0
        net_profit = float(net_profit) if pd.notna(net_profit) else 0
    except:
        return 'UNKNOWN'
    
    # Classification logic
    if net_profit == 0 or pd.isna(net_profit):
        return 'FAILED_SANDWICH'
    
    if sandwich_complete > 0 and fat_sandwich > 0:
        return 'FAT_SANDWICH'
    
    if sandwich_count > 0 and sandwich_complete > 0:
        return 'FAT_SANDWICH'
    
    if front_running > 0 or back_running > 0:
        return 'MULTI_HOP_ARBITRAGE'
    
    return 'UNCLEAR'


def process_mev_files():
    """Process all MEV CSV files and filter out multi-hop cases"""
    
    print("="*80)
    print("MEV ANALYSIS: Removing Multi-Hop (FP) Cases, Keeping Fat Sandwich")
    print("="*80)
    print()
    
    # Load main MEV file
    print(f"Loading {CSV_FILES['top10_mev']}...")
    df_top10 = pd.read_csv(CSV_FILES['top10_mev'])
    print(f"  - Loaded {len(df_top10)} rows")
    print(f"  - Columns: {list(df_top10.columns)}")
    print()
    
    print(f"Loading {CSV_FILES['all_mev']}...")
    df_all_mev = pd.read_csv(CSV_FILES['all_mev'])
    print(f"  - Loaded {len(df_all_mev)} rows")
    print()
    
    # Classify each case
    print("Classifying MEV cases as Fat Sandwich vs Multi-Hop...")
    df_all_mev['classification'] = df_all_mev.apply(classify_fat_sandwich_vs_multihop, axis=1)
    
    # Get classification counts
    class_counts = df_all_mev['classification'].value_counts()
    print("\nClassification Results (ALL MEV):")
    print(class_counts)
    print()
    
    # Filter out multi-hop and failed cases (keep only FAT_SANDWICH)
    df_fat_sandwich = df_all_mev[df_all_mev['classification'] == 'FAT_SANDWICH'].copy()
    
    print(f"After filtering out Multi-Hop & Failed cases:")
    print(f"  - Fat Sandwich cases: {len(df_fat_sandwich)}")
    print(f"  - Rows removed: {len(df_all_mev) - len(df_fat_sandwich)}")
    print()
    
    # Get top MEV scores
    print("Top 10 Fat Sandwich cases by net_profit_sol:")
    df_fat_sandwich_top = df_fat_sandwich.nlargest(10, 'net_profit_sol')
    print(df_fat_sandwich_top[['amm_trade', 'attacker_signer', 'net_profit_sol', 'fat_sandwich', 'sandwich', 'confidence']])
    print()
    
    # Save filtered files
    output_files = {
        'all_fat_sandwich': f"{OUTPUT_DIR}/all_fat_sandwich_only.csv",
        'top10_fat_sandwich': f"{OUTPUT_DIR}/top10_fat_sandwich.csv",
        'all_mev_classified': f"{OUTPUT_DIR}/all_mev_with_classification.csv",
        'top_profit_fat_sandwich': f"{OUTPUT_DIR}/top20_profit_fat_sandwich.csv"
    }
    
    print("Saving filtered output files...")
    
    # Save all fat sandwich cases
    df_fat_sandwich.to_csv(output_files['all_fat_sandwich'], index=False)
    print(f"✓ {output_files['all_fat_sandwich']}")
    
    # Save top 10 fat sandwich cases
    df_fat_sandwich_top.to_csv(output_files['top10_fat_sandwich'], index=False)
    print(f"✓ {output_files['top10_fat_sandwich']}")
    
    # Save all MEV with classification (for reference)
    df_all_mev.to_csv(output_files['all_mev_classified'], index=False)
    print(f"✓ {output_files['all_mev_classified']}")
    
    # Save top 20 by profit
    df_fat_sandwich_top20_profit = df_fat_sandwich.nlargest(20, 'net_profit_sol')
    df_fat_sandwich_top20_profit.to_csv(output_files['top_profit_fat_sandwich'], index=False)
    print(f"✓ {output_files['top_profit_fat_sandwich']}")
    
    # Also process top10 file
    print()
    print("Processing top10_mev file...")
    df_top10['classification'] = df_top10.apply(classify_fat_sandwich_vs_multihop, axis=1)
    
    class_counts_top10 = df_top10['classification'].value_counts()
    print("Classification Results (TOP 10):")
    print(class_counts_top10)
    print()
    
    df_top10_fat_sandwich = df_top10[df_top10['classification'] == 'FAT_SANDWICH'].copy()
    df_top10.to_csv(f"{OUTPUT_DIR}/top10_mev_with_classification.csv", index=False)
    df_top10_fat_sandwich.to_csv(f"{OUTPUT_DIR}/top10_mev_fat_sandwich_only.csv", index=False)
    print(f"✓ {OUTPUT_DIR}/top10_mev_with_classification.csv")
    print(f"✓ {OUTPUT_DIR}/top10_mev_fat_sandwich_only.csv")
    print(f"  - Fat Sandwich cases in top10: {len(df_top10_fat_sandwich)} / {len(df_top10)}")
    
    # Summary statistics
    print()
    print("="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"All MEV cases: {len(df_all_mev)}")
    print(f"  - Fat Sandwich: {len(df_fat_sandwich)} ({100*len(df_fat_sandwich)/len(df_all_mev):.1f}%)")
    print(f"  - Multi-Hop: {len(df_all_mev[df_all_mev['classification']=='MULTI_HOP_ARBITRAGE'])} ({100*len(df_all_mev[df_all_mev['classification']=='MULTI_HOP_ARBITRAGE'])/len(df_all_mev):.1f}%)")
    print(f"  - Failed: {len(df_all_mev[df_all_mev['classification']=='FAILED_SANDWICH'])} ({100*len(df_all_mev[df_all_mev['classification']=='FAILED_SANDWICH'])/len(df_all_mev):.1f}%)")
    print()
    
    # Top cases by AMM
    print("Top Fat Sandwich by AMM:")
    for amm in df_fat_sandwich['amm_trade'].unique():
        df_amm = df_fat_sandwich[df_fat_sandwich['amm_trade'] == amm]
        top_case = df_amm.nlargest(1, 'net_profit_sol')
        if len(top_case) > 0:
            profit = top_case['net_profit_sol'].values[0]
            count = len(df_amm)
            print(f"  {amm}: {count} cases, max profit: {profit:.4f} SOL")
    
    print()
    print("All output files saved to:", OUTPUT_DIR)
    print()
    

if __name__ == "__main__":
    process_mev_files()
