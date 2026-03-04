#!/usr/bin/env python3
"""
Audit Figure 11 class separation and fail fast when class filtering/mapping is broken.

Checks:
1) required feature + class column exist
2) label normalization and unmapped labels
3) class sample counts
4) class-mask uniqueness (detect same-mask bug)
5) significance tests (Mann-Whitney U, KS) and Cliff's delta effect size

Usage:
    python 11_report_generation/audit_figure11_class_separation.py
    python 11_report_generation/audit_figure11_class_separation.py --input path/to/data.csv --plot-out outputs/figure11_oracle_boxplot.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    from scipy.stats import ks_2samp, mannwhitneyu
except Exception:
    ks_2samp = None
    mannwhitneyu = None


def cliffs_delta(x: np.ndarray, y: np.ndarray) -> float:
    x2 = x.reshape(-1, 1)
    gt = np.sum(x2 > y)
    lt = np.sum(x2 < y)
    return float((gt - lt) / (len(x) * len(y)))


def normalize_labels(raw: pd.Series) -> tuple[pd.Series, set[str]]:
    s = raw.astype(str).str.strip().str.lower()
    label_map = {
        "1": "MEV",
        "mev": "MEV",
        "mev bot": "MEV",
        "mev_bot": "MEV",
        "true": "MEV",
        "0": "non-MEV",
        "non-mev": "non-MEV",
        "non mev": "non-MEV",
        "non_mev": "non-MEV",
        "non-dev": "non-MEV",
        "false": "non-MEV",
        "normal": "non-MEV",
        "nonmev": "non-MEV",
    }
    mapped = s.map(label_map)
    unmapped = set(s[mapped.isna()].dropna().unique().tolist())
    return mapped, unmapped


def find_input_file(base: Path, explicit_input: str | None, feature_col: str, class_col: str) -> Path:
    if explicit_input:
        p = Path(explicit_input)
        if not p.exists():
            raise FileNotFoundError(f"Input file not found: {p}")
        return p

    candidates = [
        base / "13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_detected.csv",
        base / "13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_SMOTE_DISABLED.csv",
        base / "13_mev_comprehensive_analysis/outputs/from_07_ml_classification/mev_samples_SMOTE_ENABLED.csv",
        base / "02_mev_detection/filtered_output/mev_attacker_verification.csv",
    ]

    viable = []
    reasons = []
    for c in candidates:
        if not c.exists():
            reasons.append(f"{c}: missing file")
            continue

        try:
            probe = pd.read_csv(c, nrows=5000)
        except Exception as exc:
            reasons.append(f"{c}: unreadable ({exc})")
            continue

        if feature_col not in probe.columns or class_col not in probe.columns:
            reasons.append(
                f"{c}: missing required columns feature={feature_col in probe.columns}, class={class_col in probe.columns}"
            )
            continue

        mapped, _ = normalize_labels(probe[class_col])
        cls = set(mapped.dropna().unique().tolist())
        if cls == {"MEV", "non-MEV"}:
            viable.append(c)
        else:
            reasons.append(f"{c}: classes={sorted(list(cls))} (need both MEV and non-MEV)")

    if viable:
        return viable[0]

    reason_txt = "\n".join(reasons)
    raise FileNotFoundError(
        "No candidate dataset with both MEV and non-MEV classes was found. "
        "Pass --input explicitly.\nCandidate scan:\n"
        f"{reason_txt}"
    )


def validate_and_audit(df: pd.DataFrame, feature_col: str, class_col: str) -> dict:
    missing_cols = [c for c in [feature_col, class_col] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    out: dict = {}
    out["rows_total"] = int(len(df))
    out["class_col"] = class_col
    out["feature_col"] = feature_col

    work = df[[class_col, feature_col]].copy()
    work = work.dropna(subset=[feature_col])

    mapped, unmapped = normalize_labels(work[class_col])
    work["class_norm"] = mapped

    out["unique_raw_labels"] = sorted(work[class_col].astype(str).str.strip().unique().tolist())
    out["unmapped_labels"] = sorted(list(unmapped))

    if unmapped:
        raise ValueError(f"Unmapped labels found in {class_col}: {sorted(list(unmapped))}")

    work = work.dropna(subset=["class_norm"])
    counts = work["class_norm"].value_counts().to_dict()
    out["class_counts"] = {k: int(v) for k, v in counts.items()}

    expected = {"MEV", "non-MEV"}
    got = set(counts.keys())
    if got != expected:
        raise ValueError(f"Expected classes {expected}, got {got}. Counts: {counts}")

    mev_mask = work["class_norm"] == "MEV"
    non_mask = work["class_norm"] == "non-MEV"

    if np.array_equal(mev_mask.values, non_mask.values):
        raise ValueError("Class masks are identical (likely same-filter bug).")

    if int(mev_mask.sum()) == 0 or int(non_mask.sum()) == 0:
        raise ValueError(f"Empty class after filtering. Counts: {counts}")

    x = work.loc[mev_mask, feature_col].to_numpy(dtype=float)
    y = work.loc[non_mask, feature_col].to_numpy(dtype=float)

    out["summary"] = {
        "MEV": {
            "count": int(len(x)),
            "mean": float(np.mean(x)),
            "median": float(np.median(x)),
            "std": float(np.std(x)),
            "q10": float(np.quantile(x, 0.1)),
            "q90": float(np.quantile(x, 0.9)),
        },
        "non-MEV": {
            "count": int(len(y)),
            "mean": float(np.mean(y)),
            "median": float(np.median(y)),
            "std": float(np.std(y)),
            "q10": float(np.quantile(y, 0.1)),
            "q90": float(np.quantile(y, 0.9)),
        },
    }

    out["cliffs_delta"] = cliffs_delta(x, y)

    if mannwhitneyu and ks_2samp:
        out["mann_whitney_p"] = float(mannwhitneyu(x, y, alternative="two-sided").pvalue)
        out["ks_p"] = float(ks_2samp(x, y).pvalue)
    else:
        out["mann_whitney_p"] = None
        out["ks_p"] = None

    return out


def maybe_plot(df: pd.DataFrame, feature_col: str, class_col: str, plot_out: Path) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    work = df[[class_col, feature_col]].dropna().copy()
    work["class_norm"], _ = normalize_labels(work[class_col])
    work = work.dropna(subset=["class_norm"])

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=work, x="class_norm", y=feature_col, order=["MEV", "non-MEV"])
    sns.stripplot(
        data=work.sample(min(2000, len(work)), random_state=42),
        x="class_norm",
        y=feature_col,
        order=["MEV", "non-MEV"],
        alpha=0.25,
        size=2,
        color="black",
    )
    plt.title(f"Figure 11 Audit: {feature_col} by class")
    plt.xlabel("Class")
    plt.ylabel(feature_col)
    plot_out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(plot_out, dpi=160)
    plt.close()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Figure 11 class separation")
    parser.add_argument("--input", type=str, default=None, help="CSV input file")
    parser.add_argument("--feature", type=str, default="oracle_backrun_ratio", help="Feature column to audit")
    parser.add_argument("--class-col", type=str, default="binary_label", help="Class label column")
    parser.add_argument("--plot-out", type=str, default=None, help="Optional output png path")
    parser.add_argument("--json-out", type=str, default=None, help="Optional output json path")
    args = parser.parse_args(list(argv) if argv is not None else None)

    base = Path(__file__).resolve().parent.parent
    src = find_input_file(base, args.input, args.feature, args.class_col)

    print(f"Using input: {src}")
    df = pd.read_csv(src)

    result = validate_and_audit(df, args.feature, args.class_col)
    print(json.dumps(result, indent=2))

    if args.plot_out:
        maybe_plot(df, args.feature, args.class_col, Path(args.plot_out))
        print(f"Saved plot: {args.plot_out}")

    if args.json_out:
        outp = Path(args.json_out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Saved json: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
