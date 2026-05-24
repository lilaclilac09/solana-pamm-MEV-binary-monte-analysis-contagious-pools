import pandas as pd

# Paths (update if needed)
fat_sandwich_csv = "13_mev_comprehensive_analysis/outputs/from_02_mev_detection/all_fat_sandwich_only.csv"
df_clean_path = "outputs/pamm_clean_final.parquet"
out_csv = "13_mev_comprehensive_analysis/outputs/slot_validator_attacker_crossref.csv"

# Load fat sandwich events (CSV)
df_sandwich = pd.read_csv(fat_sandwich_csv)

# Load cleaned dataframe (parquet)
df_clean = pd.read_parquet(df_clean_path)

# Ensure slot, validator, and attacker columns exist
slot_col = 'slot' if 'slot' in df_sandwich.columns else None
validator_col = 'validator' if 'validator' in df_sandwich.columns else None
attacker_col = 'attacker_signer' if 'attacker_signer' in df_sandwich.columns else None

if not slot_col or not validator_col or not attacker_col:
    raise ValueError("Required columns missing in all_fat_sandwich_only.csv")

# Prepare output rows
output_rows = []

for idx, row in df_sandwich.iterrows():
    slot = row[slot_col]
    validator = row[validator_col]
    attacker = row[attacker_col]
    # Find matching row(s) in df_clean by slot
    matches = df_clean[df_clean['slot'] == slot]
    for _, match in matches.iterrows():
        output_rows.append({
            'slot': slot,
            'validator': validator,
            'attacker_signer': attacker,
            # Add any extra info from df_clean if needed
            'df_clean_validator': match.get('validator', ''),
            'df_clean_attacker': match.get('attacker_signer', ''),
        })

# Save to CSV
out_df = pd.DataFrame(output_rows)
out_df.to_csv(out_csv, index=False)
print(f"Wrote cross-referenced slot/validator/attacker info to {out_csv}")
