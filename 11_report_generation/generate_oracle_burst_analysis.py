#!/usr/bin/env python3
"""Generate oracle update density and burst analysis plots for pAMM pools."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent.parent
INPUT_BURSTS = BASE / "03_oracle_analysis" / "outputs" / "csv" / "extreme_bursts_by_pool.csv"
INPUT_UPDATES = BASE / "03_oracle_analysis" / "outputs" / "csv" / "oracle_updates_by_pool.csv"
INPUT_OVERLAY = BASE / "03_oracle_analysis" / "oracle_trade_density_overlay.png"
OUTPUT_DIR = BASE / "11_report_generation" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_UPDATE_RATES = OUTPUT_DIR / "oracle_update_rates_by_pool.png"
OUT_BURST_DENSITY = OUTPUT_DIR / "oracle_burst_density_by_pool.png"
OUT_OVERLAY = OUTPUT_DIR / "oracle_trade_density_overlay.png"

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

if not INPUT_BURSTS.exists():
    raise SystemExit(f"Missing burst data: {INPUT_BURSTS}")
if not INPUT_UPDATES.exists():
    raise SystemExit(f"Missing update data: {INPUT_UPDATES}")

bursts = pd.read_csv(INPUT_BURSTS)
updates = pd.read_csv(INPUT_UPDATES)

# Normalize pool naming
if "amm_oracle" in bursts.columns and "pool" not in bursts.columns:
    bursts["pool"] = bursts["amm_oracle"]

# Burst aggregation by pool
burst_summary = bursts.groupby("pool").agg(
    burst_count=("oracle_count", "count"),
    max_oracle_count=("oracle_count", "max"),
    avg_oracle_count=("oracle_count", "mean"),
    avg_oracle_trade_ratio=("oracle_trade_ratio", "mean"),
).reset_index().sort_values("burst_count", ascending=False)

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

# Copy overlay plot if available
if INPUT_OVERLAY.exists():
    OUT_OVERLAY.write_bytes(INPUT_OVERLAY.read_bytes())

print(f"Saved: {OUT_UPDATE_RATES}")
print(f"Saved: {OUT_BURST_DENSITY}")
if INPUT_OVERLAY.exists():
    print(f"Saved: {OUT_OVERLAY}")
