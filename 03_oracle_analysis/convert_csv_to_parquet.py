"""
Convert 03_oracle_analysis CSV outputs to Parquet (snappy).

Writes Parquet copies alongside the original CSVs without modifying or
deleting them. Downstream consumers can opt in by reading the .parquet
file instead of the .csv.

Outputs go to: 03_oracle_analysis/outputs/parquet/
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

STAGE_DIR = Path(__file__).resolve().parent
CSV_DIR = STAGE_DIR / "outputs" / "csv"
PARQUET_DIR = STAGE_DIR / "outputs" / "parquet"
PARQUET_DIR.mkdir(parents=True, exist_ok=True)


def convert_one(csv_path: Path) -> tuple[float, int, int]:
    parquet_path = PARQUET_DIR / (csv_path.stem + ".parquet")
    t0 = time.perf_counter()
    df = pd.read_csv(csv_path)
    df.to_parquet(parquet_path, compression="snappy", index=False)
    elapsed = time.perf_counter() - t0
    return elapsed, csv_path.stat().st_size, parquet_path.stat().st_size


def main() -> None:
    csv_files = sorted(CSV_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {CSV_DIR}")
        return

    print(f"Converting {len(csv_files)} CSV files in {CSV_DIR}")
    print(f"Writing Parquet to {PARQUET_DIR}\n")

    total_csv = 0
    total_pq = 0
    for csv_path in csv_files:
        elapsed, csv_size, pq_size = convert_one(csv_path)
        total_csv += csv_size
        total_pq += pq_size
        ratio = csv_size / pq_size if pq_size else float("inf")
        print(
            f"  {csv_path.name:42s}  "
            f"{csv_size/1024/1024:7.2f} MB -> {pq_size/1024/1024:6.2f} MB  "
            f"({ratio:5.1f}x)  in {elapsed*1000:6.0f} ms"
        )

    print(
        f"\nTotal: {total_csv/1024/1024:.1f} MB CSV -> "
        f"{total_pq/1024/1024:.1f} MB Parquet "
        f"({total_csv/total_pq:.1f}x smaller)"
    )


if __name__ == "__main__":
    main()
