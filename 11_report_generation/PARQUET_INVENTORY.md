# Parquet Inventory

Last updated: 2026-03-04

## Core datasets

- `01_data_cleaning/outputs/pamm_clean_final.parquet` (rebuilt)
- `01_data_cleaning/outputs/pamm_updates_fusion_parsed.parquet` (rebuilt)
- `01_data_cleaning/outputs/pamm_clean_with_jupiter_tags.parquet` (rebuilt)

## Shared absolute-path copies

- `/Users/aileen/Downloads/pamm/pamm_clean_final.parquet`
- `/Users/aileen/Downloads/pamm/pamm_updates_fusion_parsed.parquet`
- `/Users/aileen/Downloads/pamm/pamm_updates_391876700_391976700.parquet` (raw input)

## Jupiter parsed outputs

- `02_mev_detection/outputs/pamm_clean_with_jupiter_tags.parquet`
- `02_mev_detection/jupiter_analysis/outputs/real_mev_sandwiches.parquet`
- `02_mev_detection/jupiter_analysis/outputs/aggregator_false_positives.parquet`
- `02_mev_detection/jupiter_analysis/outputs/ambiguous_transactions.parquet`
- `02_mev_detection/jupiter_analysis/outputs/legitimate_multihop_bots.parquet`
- `02_mev_detection/jupiter_analysis/outputs/normal_trades.parquet`

## Rebuild commands

From project root:

```bash
python 01_data_cleaning/rebuild_pamm_clean_final.py \
  --input /Users/aileen/Downloads/pamm/pamm_updates_391876700_391976700.parquet \
  --output-dir 01_data_cleaning/outputs

python 02_mev_detection/jupiter_analysis/export_jupiter_tags.py

mkdir -p 02_mev_detection/outputs
cp -f 01_data_cleaning/outputs/pamm_clean_with_jupiter_tags.parquet 02_mev_detection/outputs/pamm_clean_with_jupiter_tags.parquet

cd 02_mev_detection
python jupiter_analysis/separate_mev_from_aggregators.py
python jupiter_analysis/refine_mev_detection.py
```
