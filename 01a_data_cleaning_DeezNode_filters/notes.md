# 01A Data Cleaning Deeznode Filters

## Process

- Cell 1: print; bot_address_filter; write
- Cell 2: print; sandwiches_df.to_csv(sandwiches_csv_path, index; write
- Cell 3: plt.savefig(validators_chart_path, dpi; plt.savefig(top_bots_chart_path, dpi; write; plt.savefig(sandwich_validators_chart_path, dpi

## Results

### Execution Outputs

1. Total rows: 5,506,090
2. Available columns: ['slot', 'time', 'validator', 'tx_idx', 'sig', 'signer', 'kind', 'amm_oracle', 'account_updates', 'trades', 'us_since_first_shred', 'amm_trade', 'account_trade', 'is_pool_trade', 'b...
3. account_updates type: <class 'numpy.ndarray'>
4. account_updates length: 1
5. account_updates[0] type: <class 'dict'>
6. account_updates sample: [{'account': 'ELp3rjbAncW8FLAPvmWS6vjG4FXFLDo1HiKh4PhQBgvx', 'amm_name': 'HumidiFi', 'bytes_changed': 6, 'is_pool': True}]
7. Extracted 5,892,841 total addresses from account_updates
8. Parsed accounts (bot address) matches: 0
9. Total matches (bot address OR validator address): 0
10. No matches found.
11. DEBUG: validator_counts is None: False
12. ✓ Saved 24,215 sandwich patterns to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/sandwich_patterns.csv
13. ✓ Saved 367,162 fat sandwich patterns to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/fat_sandwich_patterns.csv
14. ✓ Saved top 20 validators to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/top_validators_by_volume.csv
15. ✓ Saved top sandwich validators to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01a_data_cleaning_DeezNode_filters/outputs/csv/top_validators_by_sandwich_count.csv

### Generated Files

- `outputs/images/missing_values_heatmap.png` (34.90 KB)
- `outputs/images/top_validators_by_volume.png` (190.07 KB)
- `outputs/images/top_validators_by_sandwich_count.png` (151.77 KB)
- `outputs/images/fat_sandwich_distribution.png` (38.49 KB)
- `outputs/images/fat_sandwich_victim_distribution.png` (39.95 KB)
- `outputs/images/top_mev_bot_signers.png` (116.26 KB)
- `outputs/csv/sandwich_patterns.csv` (7.37 MB)
- `outputs/csv/top_mev_bot_signers.csv` (0.51 KB)
- `outputs/csv/fat_sandwich_patterns.csv` (5043.14 MB)
- `outputs/csv/top_validators_by_sandwich_count.csv` (0.74 KB)
- `outputs/csv/missing_values_summary.csv` (0.36 KB)
- `outputs/csv/top_validators_by_volume.csv` (1.03 KB)
- `outputs/csv/rows_with_missing_values.csv` (3093.04 MB)

**Total output size:** 8144.11 MB

