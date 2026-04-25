"""
Local verification script for fat_sandwich_detector_fast_optimized.py.

Runs the original and the optimized detector back to back, times each,
diffs the resulting CSVs (after canonical sort, since the original
emits rows in iteration order which doesn't match the merge order of
the vectorized version).

Run from any directory:

    python3 02_mev_detection/verify_fat_sandwich_detector.py

The original writes outputs/fat_sandwich_detection_sample_results.csv
and the optimized writes
outputs/fat_sandwich_detection_sample_results_optimized.csv;
both live under 02_mev_detection/outputs/. Originals are not touched.
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
ORIG = HERE / "fat_sandwich_detector_fast.py"
OPT = HERE / "fat_sandwich_detector_fast_optimized.py"
OUT_DIR = HERE / "outputs"

ORIG_OUT = OUT_DIR / "fat_sandwich_detection_sample_results.csv"
OPT_OUT = OUT_DIR / "fat_sandwich_detection_sample_results_optimized.csv"


def run_script(path: Path, label: str) -> float:
    print(f"\n=== Running {label}: {path.name} ===")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(path.name)],
        cwd=str(HERE),
        check=False,
    )
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        print(f"  ! {label} exited {proc.returncode}", file=sys.stderr)
    print(f"  → {label} wall clock: {elapsed:.2f} s")
    return elapsed


def diff_csvs(a: Path, b: Path) -> tuple[bool, str]:
    if not a.exists():
        return (False, f"missing original CSV: {a}")
    if not b.exists():
        return (False, f"missing optimized CSV: {b}")
    df_a = pd.read_csv(a)
    df_b = pd.read_csv(b)
    if list(df_a.columns) != list(df_b.columns):
        return (False, f"column mismatch:\n  orig: {list(df_a.columns)}\n  opt:  {list(df_b.columns)}")
    if len(df_a) != len(df_b):
        return (False, f"row count differs: orig={len(df_a)} opt={len(df_b)}")
    sa = df_a.sort_values(list(df_a.columns)).reset_index(drop=True)
    sb = df_b.sort_values(list(df_b.columns)).reset_index(drop=True)
    if sa.equals(sb):
        return (True, f"{len(sa)} rows × {len(sa.columns)} cols match exactly")
    # Fallback: report which column has differences
    diffs = []
    for col in sa.columns:
        ne = (sa[col] != sb[col]).sum()
        if ne:
            diffs.append(f"  {col}: {int(ne)} rows differ")
    return (False, "row-content mismatch:\n" + "\n".join(diffs))


def main() -> int:
    parquet = REPO_ROOT / "01_data_cleaning/outputs/pamm_clean_final.parquet"
    if not parquet.exists():
        print(f"Cannot run verification: {parquet} not found.", file=sys.stderr)
        print("Place the parquet at that path and re-run.", file=sys.stderr)
        return 2
    if not ORIG.exists() or not OPT.exists():
        print("Detector scripts missing.", file=sys.stderr)
        return 2

    OUT_DIR.mkdir(exist_ok=True)
    if ORIG_OUT.exists():
        ORIG_OUT.unlink()
    if OPT_OUT.exists():
        OPT_OUT.unlink()

    t_orig = run_script(ORIG, "original")
    t_opt = run_script(OPT, "optimized")

    print("\n" + "=" * 64)
    print(f"TIMING:  original {t_orig:.2f}s  vs  optimized {t_opt:.2f}s")
    if t_opt > 0:
        print(f"SPEEDUP: {t_orig / t_opt:.2f}x")
    print("=" * 64)

    ok, msg = diff_csvs(ORIG_OUT, OPT_OUT)
    marker = "✓" if ok else "✗"
    print(f"\n{marker} CSV diff: {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
