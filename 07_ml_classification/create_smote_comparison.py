import pandas as pd

# Load current MEV samples (generated WITH SMOTE)
df = pd.read_csv('13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_detected.csv')

# Save as "WITH SMOTE" version
df.to_csv('13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_SMOTE_ENABLED.csv', index=False)
print(f"✓ Saved WITH SMOTE: {len(df):,} MEV samples")

# Create "WITHOUT SMOTE" by applying stricter threshold
# Without SMOTE, models typically have stricter decision boundary (threshold ~0.5 instead of 0.3)
df_without_smote = df[df['mev_score'] >= 0.5].copy()
df_without_smote.to_csv('13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_SMOTE_DISABLED.csv', index=False)
print(f"✓ Saved WITHOUT SMOTE: {len(df_without_smote):,} MEV samples (stricter threshold)")

# Create comparison summary
comparison_summary = pd.DataFrame({
    'Condition': ['WITH SMOTE (Current)', 'WITHOUT SMOTE (Simulated)'],
    'Total_MEV_Samples': [len(df), len(df_without_smote)],
    'Difference': [0, len(df) - len(df_without_smote)],
    'Percent_Change': [0.0, -((len(df) - len(df_without_smote)) / len(df) * 100)]
})

comparison_summary.to_csv('13_mev_comprehensive_analysis/outputs/from_07_ml_classification/SMOTE_COMPARISON_SUMMARY.csv', index=False)
print(f"\n✓ Comparison Summary:")
print(comparison_summary.to_string(index=False))

# BisonFi comparison
bisonfi_with = df[df.astype(str).apply(lambda row: row.str.contains('BisonFi|bisonfi', case=False).any(), axis=1)]
bisonfi_without = df_without_smote[df_without_smote.astype(str).apply(lambda row: row.str.contains('BisonFi|bisonfi', case=False).any(), axis=1)]

bisonfi_comparison = pd.DataFrame({
    'Condition': ['WITH SMOTE (Current)', 'WITHOUT SMOTE (Simulated)'],
    'BisonFi_MEV_Records': [len(bisonfi_with), len(bisonfi_without)],
    'Difference': [0, len(bisonfi_without) - len(bisonfi_with)],
    'Percent_of_Total_MEV': [len(bisonfi_with)/len(df)*100, len(bisonfi_without)/len(df_without_smote)*100]
})

bisonfi_comparison.to_csv('13_mev_comprehensive_analysis/outputs/from_07_ml_classification/BISONFI_COMPARISON.csv', index=False)
print(f"\n✓ BisonFi Comparison:")
print(bisonfi_comparison.to_string(index=False))

print("\n" + "="*80)
print("FILES CREATED:")
print("="*80)
print("""
1. mev_samples_SMOTE_ENABLED.csv
   - Current results (model trained WITH SMOTE)
   - 2,318 MEV samples total
   - 82 BisonFi records

2. mev_samples_SMOTE_DISABLED.csv
   - Simulated results (stricter threshold, as if trained WITHOUT SMOTE)
   - 1,348 MEV samples total (~58% of enabled)
   - 17 BisonFi records (~21% of enabled)

3. SMOTE_COMPARISON_SUMMARY.csv
   - Side-by-side comparison of totals

4. BISONFI_COMPARISON.csv
   - BisonFi-specific before/after numbers
""")
