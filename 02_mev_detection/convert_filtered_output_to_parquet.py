"""
Convert 02_mev_detection/filtered_output CSVs to Parquet (snappy).

Mirrors 03_oracle_analysis/convert_csv_to_parquet.py: writes Parquet
copies alongside the original CSVs without modifying or deleting them.

Outputs go to: 02_mev_detection/filtered_output/parquet/
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

STAGE_DIR = Path(__file__).resolve().parent
CSV_DIR = STAGE_DIR / "filtered_output"
PARQUET_DIR = CSV_DIR / "parquet"
PARQUET_DIR.mkdir(parents=True, exist_ok=True)


def convert_one(csv_path: Path) -> tuple[float, int, int]:
    parquet_path = PARQUET_DIR / (csv_path.stem + ".parquet")
    t0 = time.perf_counter()
    df = pd.read_csv(csv_path)
    df.to_parquet(parquet_path, compression="snappy", index=False)
    elapsed = time.perf_counter() - t0
    return elapsed, csv_path.stat().st_size, parquet_path.stat().st_size


def main() -> None:
    csv_files = sorted(p for p in CSV_DIR.glob("*.csv") if p.is_file())
    if not csv_files:
        print(f"No CSV files found in {CSV_DIR}")
        return

    print(f"Converting {len(csv_files)} CSV files in {CSV_DIR}")
    print(f"Writing Parquet to {PARQUET_DIR}\n")

    total_csv = 0
    total_pq = 0
    for csv_path in csv_files:
        try:
            elapsed, csv_size, pq_size = convert_one(csv_path)
        except Exception as exc:
            print(f"  {csv_path.name:48s}  SKIP ({exc.__class__.__name__}: {exc})")
            continue
        total_csv += csv_size
        total_pq += pq_size
        ratio = csv_size / pq_size if pq_size else float("inf")
        print(
            f"  {csv_path.name:48s}  "
            f"{csv_size/1024:7.1f} KB -> {pq_size/1024:6.1f} KB  "
            f"({ratio:5.1f}x)  in {elapsed*1000:6.0f} ms"
        )

    if total_pq:
        print(
            f"\nTotal: {total_csv/1024:.1f} KB CSV -> "
            f"{total_pq/1024:.1f} KB Parquet "
            f"({total_csv/total_pq:.1f}x smaller)"
        )


if __name__ == "__main__":
    main()
