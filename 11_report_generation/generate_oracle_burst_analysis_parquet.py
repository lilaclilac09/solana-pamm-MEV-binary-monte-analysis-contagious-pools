#!/usr/bin/env python3
"""Parquet+DuckDB version of generate_oracle_burst_analysis.py.

Reads the Parquet outputs produced by
03_oracle_analysis/convert_csv_to_parquet.py instead of the CSVs, and
performs the burst aggregation via DuckDB SQL (group-by pushed into
the columnar engine).

Outputs are written to the same plot files as the original script but
suffixed with _parquet so both versions can coexist.
"""
from pathlib import Path
import time

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE = Path(__file__).resolve().parent.parent
INPUT_BURSTS = BASE / "03_oracle_analysis" / "outputs" / "parquet" / "extreme_bursts_by_pool.parquet"
INPUT_UPDATES = BASE / "03_oracle_analysis" / "outputs" / "parquet" / "oracle_updates_by_pool.parquet"
INPUT_OVERLAY = BASE / "03_oracle_analysis" / "oracle_trade_density_overlay.png"
OUTPUT_DIR = BASE / "11_report_generation" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_UPDATE_RATES = OUTPUT_DIR / "oracle_update_rates_by_pool_parquet.png"
OUT_BURST_DENSITY = OUTPUT_DIR / "oracle_burst_density_by_pool_parquet.png"
OUT_OVERLAY = OUTPUT_DIR / "oracle_trade_density_overlay_parquet.png"

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

if not INPUT_BURSTS.exists():
    raise SystemExit(
        f"Missing burst Parquet: {INPUT_BURSTS}\n"
        "Run 03_oracle_analysis/convert_csv_to_parquet.py first."
    )
if not INPUT_UPDATES.exists():
    raise SystemExit(
        f"Missing update Parquet: {INPUT_UPDATES}\n"
        "Run 03_oracle_analysis/convert_csv_to_parquet.py first."
    )

t_start = time.perf_counter()

# Burst aggregation pushed into DuckDB. The bursts table uses `amm_oracle`
# as the pool key (mirroring the original script's column normalization),
# so we COALESCE pool/amm_oracle to get the same result.
con = duckdb.connect()
burst_summary = con.sql(
    f"""
    SELECT
        COALESCE(pool, amm_oracle) AS pool,
        COUNT(oracle_count)        AS burst_count,
        MAX(oracle_count)          AS max_oracle_count,
        AVG(oracle_count)          AS avg_oracle_count,
        AVG(oracle_trade_ratio)    AS avg_oracle_trade_ratio
    FROM read_parquet('{INPUT_BURSTS}')
    GROUP BY COALESCE(pool, amm_oracle)
    ORDER BY burst_count DESC
    """
).df()

# Updates table is small — read straight into pandas for plotting.
updates = pd.read_parquet(INPUT_UPDATES)

# Plot: Oracle update rates by pool
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

updates_sorted = updates.sort_values("updates_per_second", ascending=False)
axes[0].bar(updates_sorted["pool"], updates_sorted["updates_per_second"], color="#1f77b4")
axes[0].set_title("Oracle Update Rate by Pool (updates/sec)", fontweight="bold")
axes[0].set_ylabel("Updates per second")
axes[0].set_xlabel("Pool")
axes[0].tick_params(axis="x", rotation=45, labelsize=9)

updates_sorted = updates.sort_values("updates_per_slot", ascending=False)
axes[1].bar(updates_sorted["pool"], updates_sorted["updates_per_slot"], color="#ff7f0e")
axes[1].set_title("Oracle Update Density by Pool (updates/slot)", fontweight="bold")
axes[1].set_ylabel("Updates per slot")
axes[1].set_xlabel("Pool")
axes[1].tick_params(axis="x", rotation=45, labelsize=9)

plt.tight_layout()
plt.savefig(OUT_UPDATE_RATES, dpi=300, bbox_inches="tight")
plt.close()

# Plot: Burst density by pool
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

burst_sorted = burst_summary.sort_values("burst_count", ascending=False)
axes[0].bar(burst_sorted["pool"], burst_sorted["burst_count"], color="#2ca02c")
axes[0].set_title("Oracle Burst Count by Pool", fontweight="bold")
axes[0].set_ylabel("Burst windows")
axes[0].set_xlabel("Pool")
axes[0].tick_params(axis="x", rotation=45, labelsize=9)

burst_sorted = burst_summary.sort_values("max_oracle_count", ascending=False)
axes[1].bar(burst_sorted["pool"], burst_sorted["max_oracle_count"], color="#d62728")
axes[1].set_title("Max Oracle Updates in Burst Window", fontweight="bold")
axes[1].set_ylabel("Max updates per burst window")
axes[1].set_xlabel("Pool")
axes[1].tick_params(axis="x", rotation=45, labelsize=9)

plt.tight_layout()
plt.savefig(OUT_BURST_DENSITY, dpi=300, bbox_inches="tight")
plt.close()

if INPUT_OVERLAY.exists():
    OUT_OVERLAY.write_bytes(INPUT_OVERLAY.read_bytes())

elapsed = time.perf_counter() - t_start
print(f"Saved: {OUT_UPDATE_RATES}")
print(f"Saved: {OUT_BURST_DENSITY}")
if INPUT_OVERLAY.exists():
    print(f"Saved: {OUT_OVERLAY}")
print(f"Total time: {elapsed*1000:.0f} ms")
