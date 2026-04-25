"""
Local verification script for pamm_cross_comparison_analysis_optimized.py.

The optimized variant could not be benchmarked in the sandbox because
01_data_cleaning/outputs/pamm_clean_final.parquet (~300 MB) is gitignored
and not present. Run this on a checkout that does have the parquet to:

  1. Time the original vs optimized scripts.
  2. Diff the four output CSVs (oracle/trade latency, vulnerability,
     MEV-by-validator) and report any column-level numerical
     discrepancy.

Usage:

    python3 06_pool_analysis/verify_pamm_cross_comparison.py

The original writes to ``06_pool_analysis/outputs/`` and the optimized
to ``06_pool_analysis/outputs_optimized/``; this script compares the
two directories.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ORIG_SCRIPT = HERE / "pamm_cross_comparison_analysis.py"
OPT_SCRIPT = HERE / "pamm_cross_comparison_analysis_optimized.py"

ORIG_OUT = HERE / "outputs"
OPT_OUT = HERE / "outputs_optimized"

CSV_FILES = [
    "oracle_latency_by_pool.csv",
    "trade_latency_by_pool.csv",
    "token_pair_vulnerability_scores.csv",
    "mev_risk_by_validator.csv",
]


def run_script(script: Path, label: str) -> float:
    print(f"\n=== Running {label}: {script.name} ===")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script.name)],
        cwd=str(HERE),
        check=False,
    )
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        print(f"  ! {label} exited with code {proc.returncode}")
    print(f"  → {label} wall clock: {elapsed:.2f} s")
    return elapsed


def diff_csv(name: str) -> tuple[bool, str]:
    """Return (match, message). Match = True iff content equals after
    canonical sort."""
    path_a = ORIG_OUT / name
    path_b = OPT_OUT / name
    if not path_a.exists():
        return (False, f"missing original output: {path_a}")
    if not path_b.exists():
        return (False, f"missing optimized output: {path_b}")

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    if list(df_a.columns) != list(df_b.columns):
        return (False, f"columns differ: {list(df_a.columns)} vs {list(df_b.columns)}")

    sort_cols = [c for c in df_a.columns if df_a[c].dtype == object]
    sort_cols = sort_cols[:2] if sort_cols else list(df_a.columns[:2])
    df_a_sorted = df_a.sort_values(sort_cols).reset_index(drop=True)
    df_b_sorted = df_b.sort_values(sort_cols).reset_index(drop=True)

    if len(df_a_sorted) != len(df_b_sorted):
        return (False, f"row count differs: {len(df_a_sorted)} vs {len(df_b_sorted)}")

    diffs = []
    for col in df_a_sorted.columns:
        a = df_a_sorted[col]
        b = df_b_sorted[col]
        if a.dtype.kind in "fiu":
            try:
                if not pd.testing.assert_series_equal(a, b, check_exact=False, rtol=1e-6, atol=1e-6) is None:
                    pass
            except AssertionError as exc:
                diffs.append(f"  numeric mismatch in {col}: {exc}".replace("\n", " "))
        else:
            if not a.equals(b):
                ne = (a != b).sum()
                diffs.append(f"  string mismatch in {col}: {ne} rows differ")

    if diffs:
        return (False, "\n".join(diffs))
    return (True, f"{len(df_a_sorted)} rows × {len(df_a_sorted.columns)} cols match")


def main() -> int:
    if not ORIG_SCRIPT.exists() or not OPT_SCRIPT.exists():
        print("Scripts missing; aborting.", file=sys.stderr)
        return 2

    parquet = REPO_ROOT / "01_data_cleaning/outputs/pamm_clean_final.parquet"
    if not parquet.exists():
        print(f"Cannot run verification: {parquet} not found.", file=sys.stderr)
        print("Place the parquet at that path and re-run.", file=sys.stderr)
        return 2

    # Wipe old optimized outputs to ensure a clean comparison.
    if OPT_OUT.exists():
        shutil.rmtree(OPT_OUT)
    ORIG_OUT.mkdir(parents=True, exist_ok=True)

    t_orig = run_script(ORIG_SCRIPT, "original")
    t_opt = run_script(OPT_SCRIPT, "optimized")

    print("\n" + "=" * 64)
    print(f"TIMING:  original {t_orig:.2f}s  vs  optimized {t_opt:.2f}s")
    if t_opt > 0:
        print(f"SPEEDUP: {t_orig / t_opt:.2f}x")
    print("=" * 64)

    print("\nDIFFING OUTPUT CSVS")
    print("-" * 64)
    all_match = True
    for name in CSV_FILES:
        ok, msg = diff_csv(name)
        marker = "✓" if ok else "✗"
        print(f"  {marker} {name}: {msg}")
        all_match = all_match and ok

    print("=" * 64)
    print("ALL OUTPUTS MATCH" if all_match else "MISMATCHES DETECTED")
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
