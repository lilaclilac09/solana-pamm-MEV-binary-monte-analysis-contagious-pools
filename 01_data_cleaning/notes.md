# 01 Data Cleaning

## Process

- Cell 1: df_fusion.to_parquet(fusion_path, index; print
- Cell 2: plt.savefig(pie_chart_path, dpi; print; plt.savefig(time_series_path, dpi
- Cell 3: df_clean.to_parquet(clean_parquet_path, index; print

## Results

### Execution Outputs

1. Original data loaded successfully. Total rows: 5,526,137
2. Original columns: ['slot', 'time', 'validator', 'tx_idx', 'sig', 'signer', 'kind', 'amm', 'account_updates', 'trades', 'us_since_first_shred']
3. Column  Missing Count  Missing Ratio (%)
4. Parsing success rate (amm_trade non-null): 100.00%
5. Fused table generated and saved to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01_data_cleaning/outputs/pamm_updates_fusion_parsed.parquet
6. Fused table columns: ['slot', 'time', 'validator', 'tx_idx', 'sig', 'signer', 'kind', 'amm_oracle', 'account_updates', 'trades', 'us_since_first_shred', 'amm_trade', 'account_trade', 'is_pool_trade', ...
7. First 5 rows of fused table (key columns):
8. kind amm_oracle amm_trade                                 account_trade  \
9. Heatmap displayed and saved to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01_data_cleaning/outputs/images/missing_values_heatmap_fusion.png
10. Paired missing timing rows (tx_idx & us_since_first_shred): 20,047
11. Using cleaned fused table for analysis. Total rows: 5,506,090
12. Available columns: ['slot', 'time', 'validator', 'tx_idx', 'sig', 'signer', 'kind', 'amm_oracle', 'account_updates', 'trades', 'us_since_first_shred', 'amm_trade', 'account_trade', 'is_pool_trade', 'b...
13. - Total events: 5,506,090
14. - Total duration: 39735.00 seconds
15. Pie chart saved to: /Users/aileen/Downloads/pamm/solana-pamm-analysis/notebooks/01_data_cleaning/outputs/images/event_type_distribution.png

### Generated Files

- `outputs/pamm_updates_fusion_parsed.parquet` (602.06 MB)
- `outputs/pamm_clean_final.parquet` (579.24 MB)
- `outputs/images/missing_values_heatmap_fusion.png` (46.22 KB)
- `outputs/images/pamm_events_per_minute.png` (242.44 KB)
- `outputs/images/event_type_distribution.png` (35.05 KB)
- `outputs/csv/missing_table_fusion.csv` (0.31 KB)
- `outputs/csv/pamm_toxic_mitigation_summary.csv` (0.20 KB)
- `outputs/csv/pamm_deleted_timing_missing_rows.csv` (9.68 MB)
- `outputs/csv/missing_table_original.csv` (0.22 KB)

**Total output size:** 1191.30 MB

