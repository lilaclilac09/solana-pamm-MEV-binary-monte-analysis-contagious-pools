# Rebuild `pamm_clean_final.parquet`

This script rebuilds data-cleaning artifacts only and does **not** modify website/app code.

## Script

- `01_data_cleaning/rebuild_pamm_clean_final.py`

## Run

From project root:

```bash
python 01_data_cleaning/rebuild_pamm_clean_final.py \
  --input /path/to/your/pamm_updates_391876700_391976700.parquet \
  --output-dir 01_data_cleaning/outputs
```

## Outputs generated

- `01_data_cleaning/outputs/pamm_updates_fusion_parsed.parquet`
- `01_data_cleaning/outputs/pamm_clean_final.parquet`
- `01_data_cleaning/outputs/csv/missing_table_original.csv`
- `01_data_cleaning/outputs/csv/missing_table_fusion.csv`
- `01_data_cleaning/outputs/csv/pamm_deleted_timing_missing_rows.csv`
- `01_data_cleaning/outputs/csv/pamm_toxic_mitigation_summary.csv`
- `01_data_cleaning/outputs/images/missing_values_heatmap_fusion.png`
- `01_data_cleaning/outputs/images/event_type_distribution.png`
- `01_data_cleaning/outputs/images/pamm_events_per_minute.png`

## Optional

Lower memory load for heatmap generation:

```bash
python 01_data_cleaning/rebuild_pamm_clean_final.py \
  --input /path/to/raw.parquet \
  --heatmap-sample-size 5000
```
