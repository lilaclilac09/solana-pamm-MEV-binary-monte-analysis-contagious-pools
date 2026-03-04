#!/usr/bin/env python3
"""
Build a canonical two-class dataset for Figure 11 auditing/plotting.

Output columns:
- signer
- oracle_backrun_ratio
- binary_label (1=MEV, 0=non-MEV)
- class_label (MEV/non-MEV)
- source

MEV source:
- 13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_detected.csv

non-MEV source:
- signer list from 07_ml_classification/derived/aggregator_analysis/aggregators_with_pools.csv
- oracle_backrun_ratio recomputed from 01_data_cleaning/outputs/pamm_clean_final.parquet
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def compute_oracle_ratio_for_signers(events: pd.DataFrame, signers: set[str]) -> pd.DataFrame:
    trades = events.loc[(events["kind"] == "TRADE") & (events["signer"].astype(str).isin(signers)), ["signer", "slot", "ms_time"]].copy()
    oracles = events.loc[events["kind"] == "ORACLE", ["slot", "ms_time"]].copy()

    if trades.empty:
        return pd.DataFrame(columns=["signer", "oracle_backrun_ratio"])

    oracle_by_slot = {
        int(slot): grp["ms_time"].to_numpy()
        for slot, grp in oracles.groupby("slot", sort=False)
    }

    rows = []
    for signer, grp in trades.groupby("signer", sort=False):
        total = len(grp)
        if total == 0:
            continue
        count = 0
        for slot, t in zip(grp["slot"].to_numpy(), grp["ms_time"].to_numpy()):
            oracle_times = oracle_by_slot.get(int(slot))
            if oracle_times is None or len(oracle_times) == 0:
                continue
            if np.min(np.abs(oracle_times - t)) < 50:
                count += 1
        rows.append({"signer": str(signer), "oracle_backrun_ratio": count / total})

    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build canonical two-class Figure 11 dataset")
    parser.add_argument("--target-non-mev", type=int, default=1200, help="Number of non-MEV signers to include")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for non-MEV sampling")
    parser.add_argument(
        "--out",
        type=str,
        default="11_report_generation/outputs/figure11_canonical_dataset.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    mev_path = base / "13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_detected.csv"
    agg_path = base / "07_ml_classification/derived/aggregator_analysis/aggregators_with_pools.csv"
    raw_path = base / "01_data_cleaning/outputs/pamm_clean_final.parquet"
    out_path = base / args.out

    if not mev_path.exists():
        raise FileNotFoundError(f"Missing MEV file: {mev_path}")
    if not agg_path.exists():
        raise FileNotFoundError(f"Missing aggregator file: {agg_path}")
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw parquet: {raw_path}")

    mev_df = pd.read_csv(mev_path)
    required = {"signer", "oracle_backrun_ratio", "binary_label"}
    missing = required - set(mev_df.columns)
    if missing:
        raise ValueError(f"MEV dataset missing columns: {sorted(list(missing))}")

    mev_df = mev_df.copy()
    mev_df["signer"] = mev_df["signer"].astype(str)
    mev_df = mev_df[mev_df["binary_label"] == 1]
    mev_df = mev_df[["signer", "oracle_backrun_ratio"]].dropna().drop_duplicates("signer")
    mev_df["binary_label"] = 1
    mev_df["class_label"] = "MEV"
    mev_df["source"] = "mev_samples_detected"

    mev_signers = set(mev_df["signer"].tolist())

    agg_df = pd.read_csv(agg_path)
    if "signer" not in agg_df.columns:
        raise ValueError("Aggregator file must include signer column")

    candidates = agg_df["signer"].astype(str)
    candidates = candidates[~candidates.isin(mev_signers)]
    candidates = candidates.drop_duplicates().reset_index(drop=True)

    sample_n = min(args.target_non_mev, len(candidates))
    sampled_non_mev = set(candidates.sample(n=sample_n, random_state=args.seed).tolist())

    events = pd.read_parquet(raw_path, columns=["kind", "slot", "ms_time", "signer"])
    non_mev_features = compute_oracle_ratio_for_signers(events, sampled_non_mev)

    non_mev_df = non_mev_features.copy()
    non_mev_df["binary_label"] = 0
    non_mev_df["class_label"] = "non-MEV"
    non_mev_df["source"] = "aggregator_signers_recomputed"

    out_df = pd.concat([mev_df, non_mev_df], ignore_index=True)
    out_df = out_df.dropna(subset=["oracle_backrun_ratio"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print(f"Saved: {out_path}")
    print(f"Rows: {len(out_df):,}")
    print("Class counts:")
    print(out_df["class_label"].value_counts().to_string())
    print("Oracle ratio means:")
    print(out_df.groupby("class_label")["oracle_backrun_ratio"].mean().to_string())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
