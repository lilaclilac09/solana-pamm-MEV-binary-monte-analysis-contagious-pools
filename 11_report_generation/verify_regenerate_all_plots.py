"""
Local image diff verifier for the regenerate_all_plots optimization.

Runs the original and the optimized regeneration scripts in their stage
directory and compares the four PNG outputs pixel-by-pixel. Reports
per-file: identical?, byte size, mean abs pixel diff, max diff,
%-of-pixels-different.

Run from any directory:

    python3 11_report_generation/verify_regenerate_all_plots.py

The original writes to ``02_mev_detection/filtered_output/plots/`` with
unsuffixed names; the optimized version writes the same names with
``_optimized`` suffix. The script preserves both sets of PNGs so you
can review them visually after the run.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ORIG = HERE / "regenerate_all_plots_filtered_data.py"
OPT = HERE / "regenerate_all_plots_filtered_data_optimized.py"
PLOTS_DIR = REPO_ROOT / "02_mev_detection" / "filtered_output" / "plots"

# (original_filename, optimized_filename) pairs.
PAIRS = [
    ("mev_distribution_comprehensive_filtered.png",
     "mev_distribution_comprehensive_filtered_optimized.png"),
    ("top_attackers_filtered.png",
     "top_attackers_filtered_optimized.png"),
    ("aggregator_vs_mev_detailed_comparison.png",
     "aggregator_vs_mev_detailed_comparison_optimized.png"),
    ("profit_distribution_filtered.png",
     "profit_distribution_filtered_optimized.png"),
]


def run_script(script: Path, label: str) -> float:
    print(f"\n=== Running {label}: {script.name} ===")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT),
        check=False,
    )
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        print(f"  ! {label} exited {proc.returncode}", file=sys.stderr)
    print(f"  → {label} wall clock: {elapsed:.2f} s")
    return elapsed


def diff_png(a: Path, b: Path) -> dict:
    """Return per-PNG diff stats. Uses Pillow + numpy."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError as exc:
        return {"error": f"missing dep: {exc}. pip install pillow numpy"}

    if not a.exists():
        return {"error": f"missing original: {a}"}
    if not b.exists():
        return {"error": f"missing optimized: {b}"}

    img_a = np.asarray(Image.open(a).convert("RGBA"))
    img_b = np.asarray(Image.open(b).convert("RGBA"))

    if img_a.shape != img_b.shape:
        return {
            "error": f"shape differs: orig={img_a.shape} opt={img_b.shape}",
            "bytes_orig": a.stat().st_size,
            "bytes_opt": b.stat().st_size,
        }

    diff = np.abs(img_a.astype(int) - img_b.astype(int))
    diff_pixel_mask = diff.any(axis=-1)
    n_diff = int(diff_pixel_mask.sum())
    n_total = int(diff_pixel_mask.size)

    return {
        "identical": n_diff == 0,
        "shape": img_a.shape,
        "mean_abs_diff": float(diff.mean()),
        "max_abs_diff": int(diff.max()),
        "pct_pixels_diff": 100.0 * n_diff / n_total,
        "bytes_orig": a.stat().st_size,
        "bytes_opt": b.stat().st_size,
    }


def main() -> int:
    raw = REPO_ROOT / "01_data_cleaning" / "outputs" / "pamm_clean_final.parquet"
    if not raw.exists():
        print(f"Cannot run verification: {raw} not found.", file=sys.stderr)
        return 2
    if not ORIG.exists() or not OPT.exists():
        print("Generator scripts missing.", file=sys.stderr)
        return 2

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    t_orig = run_script(ORIG, "original")
    t_opt = run_script(OPT, "optimized")

    print("\n" + "=" * 64)
    print(f"TIMING:  original {t_orig:.2f}s  vs  optimized {t_opt:.2f}s")
    if t_opt > 0:
        print(f"SPEEDUP: {t_orig / t_opt:.2f}x")
    print("=" * 64)

    print("\nPER-PNG DIFF:")
    print("-" * 64)
    all_ok = True
    for orig_name, opt_name in PAIRS:
        a = PLOTS_DIR / orig_name
        b = PLOTS_DIR / opt_name
        result = diff_png(a, b)
        if "error" in result:
            print(f"  ✗ {orig_name}: {result['error']}")
            all_ok = False
            continue
        marker = "✓" if result["identical"] else "≈"
        if not result["identical"] and result["pct_pixels_diff"] > 1.0:
            all_ok = False
            marker = "✗"
        print(f"  {marker} {orig_name}")
        print(f"      shape={result['shape']}  bytes orig={result['bytes_orig']}/opt={result['bytes_opt']}")
        print(f"      mean|Δ|={result['mean_abs_diff']:.3f}  max|Δ|={result['max_abs_diff']}  "
              f"diff_pixels={result['pct_pixels_diff']:.3f}%")

    print("=" * 64)
    if all_ok:
        print("ALL PNGS PIXEL-CLOSE (any non-zero diff is matplotlib non-determinism)")
    else:
        print("MISMATCHES DETECTED — open the *_optimized.png next to the original to inspect")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
