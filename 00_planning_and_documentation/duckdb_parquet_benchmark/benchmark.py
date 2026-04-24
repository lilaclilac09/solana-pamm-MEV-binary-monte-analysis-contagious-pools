"""
Benchmark: pandas+CSV vs DuckDB+Parquet on this repo's actual datasets.

Measures the operations that dominate the 03_oracle_analysis and
08_monte_carlo_risk stages:
  1. Full file read
  2. Column-subset read
  3. Filtered read (WHERE-style)
  4. groupby + aggregate
  5. File size on disk

Each timed operation runs N_REPEATS times; reports median to reduce noise.
"""

from __future__ import annotations

import gc
import os
import statistics
import time
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow  # noqa: F401  (pandas uses pyarrow engine for parquet)

REPO_ROOT = Path(__file__).resolve().parents[2]
ORACLE_CSV = REPO_ROOT / "03_oracle_analysis/outputs/csv/oracle_slot_patterns.csv"
MC_CSV = (
    REPO_ROOT
    / "08_monte_carlo_risk/outputs/monte_carlo_harmony_multibuilder_binary_monte_carlo_20260224_220124.csv"
)

OUT_DIR = REPO_ROOT / "00_planning_and_documentation/duckdb_parquet_benchmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ORACLE_PARQUET = OUT_DIR / "oracle_slot_patterns.parquet"
MC_PARQUET = OUT_DIR / "monte_carlo_harmony.parquet"

N_REPEATS = 5


def _time(fn):
    gc.collect()
    samples = []
    for _ in range(N_REPEATS):
        t0 = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - t0)
        del result
        gc.collect()
    return statistics.median(samples)


def _size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def convert_to_parquet():
    if not ORACLE_PARQUET.exists():
        pd.read_csv(ORACLE_CSV).to_parquet(ORACLE_PARQUET, compression="snappy")
    if not MC_PARQUET.exists():
        pd.read_csv(MC_CSV).to_parquet(MC_PARQUET, compression="snappy")


def bench_oracle():
    print("\n=== oracle_slot_patterns (659K rows, 4 cols) ===")
    print(f"CSV     : {_size_mb(ORACLE_CSV):.1f} MB")
    print(f"Parquet : {_size_mb(ORACLE_PARQUET):.1f} MB")

    # 1. Full read
    t_csv = _time(lambda: pd.read_csv(ORACLE_CSV))
    t_pq = _time(lambda: pd.read_parquet(ORACLE_PARQUET))
    t_ddb = _time(
        lambda: duckdb.sql(f"SELECT * FROM read_parquet('{ORACLE_PARQUET}')").df()
    )
    _report("full read", t_csv, t_pq, t_ddb)

    # 2. Column subset (only slot + oracle_count)
    t_csv = _time(
        lambda: pd.read_csv(ORACLE_CSV, usecols=["slot", "oracle_count"])
    )
    t_pq = _time(
        lambda: pd.read_parquet(ORACLE_PARQUET, columns=["slot", "oracle_count"])
    )
    t_ddb = _time(
        lambda: duckdb.sql(
            f"SELECT slot, oracle_count FROM read_parquet('{ORACLE_PARQUET}')"
        ).df()
    )
    _report("column subset (2/4 cols)", t_csv, t_pq, t_ddb)

    # 3. Filtered read: oracle_count > 5
    t_csv = _time(
        lambda: pd.read_csv(ORACLE_CSV).query("oracle_count > 5")
    )
    t_pq = _time(
        lambda: pd.read_parquet(
            ORACLE_PARQUET, filters=[("oracle_count", ">", 5)]
        )
    )
    t_ddb = _time(
        lambda: duckdb.sql(
            f"SELECT * FROM read_parquet('{ORACLE_PARQUET}') WHERE oracle_count > 5"
        ).df()
    )
    _report("filter oracle_count > 5", t_csv, t_pq, t_ddb)

    # 4. groupby aggregate: top oracles by total count
    t_csv = _time(
        lambda: pd.read_csv(ORACLE_CSV)
        .groupby("amm_oracle")["oracle_count"]
        .sum()
        .reset_index()
    )
    t_pq = _time(
        lambda: pd.read_parquet(ORACLE_PARQUET)
        .groupby("amm_oracle")["oracle_count"]
        .sum()
        .reset_index()
    )
    t_ddb = _time(
        lambda: duckdb.sql(
            f"""
            SELECT amm_oracle, SUM(oracle_count) AS total
            FROM read_parquet('{ORACLE_PARQUET}')
            GROUP BY amm_oracle
            """
        ).df()
    )
    _report("groupby amm_oracle SUM", t_csv, t_pq, t_ddb)


def bench_monte_carlo():
    print("\n=== monte_carlo_harmony (100K rows, 10 cols) ===")
    print(f"CSV     : {_size_mb(MC_CSV):.1f} MB")
    print(f"Parquet : {_size_mb(MC_PARQUET):.1f} MB")

    # 1. Full read
    t_csv = _time(lambda: pd.read_csv(MC_CSV))
    t_pq = _time(lambda: pd.read_parquet(MC_PARQUET))
    t_ddb = _time(
        lambda: duckdb.sql(f"SELECT * FROM read_parquet('{MC_PARQUET}')").df()
    )
    _report("full read", t_csv, t_pq, t_ddb)

    # 2. groupby scenario -> total_loss stats (the common downstream op)
    t_csv = _time(
        lambda: pd.read_csv(MC_CSV)
        .groupby("scenario_name")["total_loss"]
        .agg(["mean", "std", "max"])
        .reset_index()
    )
    t_pq = _time(
        lambda: pd.read_parquet(MC_PARQUET)
        .groupby("scenario_name")["total_loss"]
        .agg(["mean", "std", "max"])
        .reset_index()
    )
    t_ddb = _time(
        lambda: duckdb.sql(
            f"""
            SELECT scenario_name,
                   AVG(total_loss)    AS mean_loss,
                   STDDEV(total_loss) AS std_loss,
                   MAX(total_loss)    AS max_loss
            FROM read_parquet('{MC_PARQUET}')
            GROUP BY scenario_name
            """
        ).df()
    )
    _report("groupby scenario agg", t_csv, t_pq, t_ddb)

    # 3. Filtered aggregate: high-risk cascades
    t_csv = _time(
        lambda: pd.read_csv(MC_CSV)
        .query("high_risk == 1 and cascades > 0")
        .groupby("scenario_name")["total_loss"]
        .sum()
    )
    t_pq = _time(
        lambda: pd.read_parquet(
            MC_PARQUET,
            filters=[("high_risk", "==", 1), ("cascades", ">", 0)],
        )
        .groupby("scenario_name")["total_loss"]
        .sum()
    )
    t_ddb = _time(
        lambda: duckdb.sql(
            f"""
            SELECT scenario_name, SUM(total_loss) AS total
            FROM read_parquet('{MC_PARQUET}')
            WHERE high_risk = 1 AND cascades > 0
            GROUP BY scenario_name
            """
        ).df()
    )
    _report("filter + groupby", t_csv, t_pq, t_ddb)


def _report(label: str, t_csv: float, t_pq: float, t_ddb: float):
    base = t_csv
    print(
        f"  {label:32s}  "
        f"pandas+CSV {t_csv*1000:7.1f} ms | "
        f"pandas+Parquet {t_pq*1000:7.1f} ms ({base/t_pq:5.2f}x) | "
        f"DuckDB+Parquet {t_ddb*1000:7.1f} ms ({base/t_ddb:5.2f}x)"
    )


if __name__ == "__main__":
    print(f"pandas {pd.__version__} | duckdb {duckdb.__version__}")
    print(f"repeats per op: {N_REPEATS} (median reported)")
    convert_to_parquet()
    bench_oracle()
    bench_monte_carlo()
