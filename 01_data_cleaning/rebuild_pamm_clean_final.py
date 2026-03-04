#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def parse_account_update(item):
    if item is None:
        return None, None, None, None

    if isinstance(item, np.ndarray):
        if len(item) == 0:
            return None, None, None, None
        inner = item[0]
    else:
        if pd.isna(item):
            return None, None, None, None
        return None, None, None, None

    if not isinstance(inner, dict):
        return None, None, None, None

    return (
        inner.get("amm_name"),
        inner.get("account"),
        inner.get("is_pool"),
        inner.get("bytes_changed"),
    )


def save_missing_table(df: pd.DataFrame, csv_path: Path) -> None:
    na_count = df.isna().sum()
    na_ratio = (na_count / len(df) * 100).round(4)
    missing_table = pd.DataFrame(
        {
            "Column": na_count.index,
            "Missing Count": na_count.values,
            "Missing Ratio (%)": na_ratio.values,
        }
    ).sort_values("Missing Ratio (%)", ascending=False)
    missing_table.to_csv(csv_path, index=False)


def create_outputs(raw_parquet: Path, output_dir: Path, heatmap_sample_size: int = 20000) -> None:
    csv_dir = output_dir / "csv"
    images_dir = output_dir / "images"
    csv_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw data from: {raw_parquet}")
    df_original = pd.read_parquet(raw_parquet)
    print(f"Original rows: {len(df_original):,}")

    save_missing_table(df_original, csv_dir / "missing_table_original.csv")

    parsed_series = df_original["account_updates"].apply(parse_account_update)
    parsed_df = pd.DataFrame(
        parsed_series.tolist(),
        columns=["amm_trade", "account_trade", "is_pool_trade", "bytes_changed_trade"],
        index=df_original.index,
    )

    df_original = df_original.rename(columns={"amm": "amm_oracle"}, errors="ignore")
    df_fusion = pd.concat([df_original.copy(), parsed_df], axis=1)
    fusion_path = output_dir / "pamm_updates_fusion_parsed.parquet"
    df_fusion.to_parquet(fusion_path, index=False)
    print(f"Saved fused parquet: {fusion_path}")

    save_missing_table(df_fusion, csv_dir / "missing_table_fusion.csv")

    key_cols = [
        "kind",
        "amm_oracle",
        "amm_trade",
        "account_trade",
        "is_pool_trade",
        "bytes_changed_trade",
        "tx_idx",
        "us_since_first_shred",
        "trades",
    ]
    heat_cols = [col for col in key_cols if col in df_fusion.columns]
    if heat_cols:
        sample_size = min(heatmap_sample_size, len(df_fusion))
        sample_df = df_fusion[heat_cols].sample(n=sample_size, random_state=42)

        plt.figure(figsize=(12, 6))
        sns.heatmap(
            sample_df.isna(),
            cbar=False,
            cmap="viridis",
            yticklabels=False,
            linewidths=0,
        )
        plt.title("Missing Values Heatmap (Sampled Rows)")
        plt.xlabel("Columns")
        plt.tight_layout()
        plt.savefig(images_dir / "missing_values_heatmap_fusion.png", dpi=150)
        plt.close()

    df_fusion["datetime"] = pd.to_datetime(df_fusion["time"], unit="s", utc=True)
    if "us_since_first_shred" in df_fusion.columns:
        df_fusion["us_since_first_shred"] = df_fusion["us_since_first_shred"].astype(np.float64)
    else:
        df_fusion["us_since_first_shred"] = np.nan

    df_fusion["timing_missing"] = df_fusion["tx_idx"].isna() & df_fusion["us_since_first_shred"].isna()
    deleted_rows = df_fusion[df_fusion["timing_missing"]].copy()
    deleted_rows.to_csv(csv_dir / "pamm_deleted_timing_missing_rows.csv", index=False)

    df_clean = df_fusion[~df_fusion["timing_missing"]].copy()

    partial_missing_us = df_clean["us_since_first_shred"].isna().sum()
    if partial_missing_us > 0:
        print(
            f"Warning: {partial_missing_us:,} rows have missing us_since_first_shred after paired filter; filling with 0 for ms_time."
        )

    df_clean["ms_time"] = (
        df_clean["time"] * 1000 + df_clean["us_since_first_shred"].fillna(0) / 1000
    ).astype(np.int64)
    df_clean = df_clean.sort_values("ms_time").reset_index(drop=True)

    if "datetime" not in df_clean.columns:
        if "ms_time" in df_clean.columns:
            df_clean["datetime"] = pd.to_datetime(df_clean["ms_time"], unit="ms", utc=True, errors="coerce")
        elif "time" in df_clean.columns:
            df_clean["datetime"] = pd.to_datetime(df_clean["time"], unit="s", utc=True, errors="coerce")
        elif "slot" in df_clean.columns:
            genesis_time = pd.to_datetime("2020-03-16 00:00:00 UTC")
            slot_duration = pd.Timedelta(milliseconds=400)
            df_clean["datetime"] = genesis_time + (df_clean["slot"] * slot_duration)
        else:
            raise ValueError("Cannot create datetime: no time-like column found")

    total_events = len(df_clean)
    kind_counts = df_clean["kind"].value_counts() if "kind" in df_clean.columns else pd.Series(dtype="int64")
    oracle_count = int(kind_counts.get("ORACLE", 0))
    trade_count = int(kind_counts.get("TRADE", 0))

    if "datetime" in df_clean.columns and not df_clean["datetime"].isna().all():
        time_range = df_clean["datetime"].max() - df_clean["datetime"].min()
        total_seconds = time_range.total_seconds() if pd.notna(time_range) else 0
    else:
        total_seconds = 0

    oracle_freq = oracle_count / total_seconds if total_seconds > 0 else 0
    trade_freq = trade_count / total_seconds if total_seconds > 0 else 0

    if "datetime" in df_clean.columns:
        df_ts = df_clean.set_index("datetime")
        events_per_min = df_ts.resample("1min").size()
        oracle_per_min = df_ts[df_ts["kind"] == "ORACLE"].resample("1min").size() if "kind" in df_ts.columns else pd.Series(dtype="int64")
        trade_per_min = df_ts[df_ts["kind"] == "TRADE"].resample("1min").size() if "kind" in df_ts.columns else pd.Series(dtype="int64")

        plt.figure(figsize=(14, 6))
        events_per_min.plot(label="Total Events", color="gray", alpha=0.5)
        oracle_per_min.plot(label="ORACLE", color="blue", alpha=0.8)
        trade_per_min.plot(label="TRADE", color="red", alpha=0.7)
        plt.title("pAMM Events per Minute")
        plt.xlabel("Time")
        plt.ylabel("Events per Minute")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(images_dir / "pamm_events_per_minute.png", dpi=150)
        plt.close()

    if "kind" in df_clean.columns and not kind_counts.empty:
        plt.figure(figsize=(8, 6))
        kind_counts.plot.pie(autopct="%1.1f%%", colors=["#66b3ff", "#ff9999"])
        plt.title("Event Type Distribution (ORACLE vs TRADE)")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(images_dir / "event_type_distribution.png", dpi=150)
        plt.close()

    summary_data = {
        "Metric": [
            "Total Events",
            "ORACLE %",
            "TRADE %",
            "ORACLE Freq (per sec)",
            "TRADE Freq (per sec)",
            "Deleted Timing-Missing Rows",
        ],
        "Value": [
            total_events,
            f"{(oracle_count / total_events * 100):.2f}%" if total_events > 0 else "0.00%",
            f"{(trade_count / total_events * 100):.2f}%" if total_events > 0 else "0.00%",
            oracle_freq if total_seconds > 0 else "N/A",
            trade_freq if total_seconds > 0 else "N/A",
            int(deleted_rows.shape[0]),
        ],
    }
    pd.DataFrame(summary_data).to_csv(csv_dir / "pamm_toxic_mitigation_summary.csv", index=False)

    clean_parquet_path = output_dir / "pamm_clean_final.parquet"
    df_clean.to_parquet(clean_parquet_path, index=False)

    print("\nRebuild complete:")
    print(f"- Final cleaned parquet: {clean_parquet_path}")
    print(f"- Final rows: {len(df_clean):,}")
    print(f"- Final columns: {len(df_clean.columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild pamm_clean_final.parquet from a raw pAMM update parquet file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to raw parquet (e.g., pamm_updates_391876700_391976700.parquet)",
    )
    parser.add_argument(
        "--output-dir",
        default="01_data_cleaning/outputs",
        help="Directory for generated CSV/PNG/parquet outputs",
    )
    parser.add_argument(
        "--heatmap-sample-size",
        type=int,
        default=20000,
        help="Row sample size for missing-value heatmap",
    )

    args = parser.parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input parquet not found: {input_path}")

    create_outputs(input_path, output_dir, heatmap_sample_size=args.heatmap_sample_size)


if __name__ == "__main__":
    main()
