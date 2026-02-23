#!/usr/bin/env python3
import pandas as pd
import numpy as np

print("="*80)
print("EXPLORING AVAILABLE DATA FOR GMM ANALYSIS")
print("="*80)

# Load cleaned data
try:
    df_clean = pd.read_parquet('01_data_cleaning/outputs/pamm_clean_final.parquet')
    print("\n✅ Cleaned data loaded successfully")
    print(f"   Shape: {df_clean.shape}")
    print(f"\n   Columns ({len(df_clean.columns)}):")
    for i, col in enumerate(df_clean.columns):
        print(f"     {i+1}. {col}")
    
except Exception as e:
    print(f"Error loading cleaned data: {e}")

# Check MEV data
try:
    df_mev = pd.read_csv('02_mev_detection/per_pamm_all_mev_with_validator.csv')
    print("\n✅ MEV data loaded successfully")
    print(f"   Shape: {df_mev.shape}")
    print(f"   Columns: {list(df_mev.columns)}")
except Exception as e:
    print(f"Error loading MEV data: {e}")
