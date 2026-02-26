#!/usr/bin/env python3
"""Generate a highest-value MEV case study (data + plot) from validated attacks."""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / "02_mev_detection" / "filtered_output" / "all_fat_sandwich_only.csv"
OUTPUT_DIR = BASE / "11_report_generation" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CASE_JSON = OUTPUT_DIR / "top_mev_case_study.json"
CASE_PLOT = OUTPUT_DIR / "top_mev_case_study.png"

if not DATA_FILE.exists():
    raise SystemExit(f"Missing data file: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

# Normalize column names
if "attacker_signer" in df.columns and "signer" not in df.columns:
    df["signer"] = df["attacker_signer"]
if "amm_trade" in df.columns and "pool" not in df.columns:
    df["pool"] = df["amm_trade"]

required_cols = ["signer", "pool", "validator", "net_profit_sol", "profit_sol", "cost_sol"]
for col in required_cols:
    if col not in df.columns:
        raise SystemExit(f"Missing required column: {col}")

# Highest-value single attack
case_row = df.loc[df["net_profit_sol"].idxmax()].copy()

# Aggregate context
total_profit = df["net_profit_sol"].sum()
attacker_total = df.groupby("signer")["net_profit_sol"].sum().sort_values(ascending=False)
attacker_rank = int(attacker_total.index.get_loc(case_row["signer"]) + 1)
attacker_profit = float(attacker_total.loc[case_row["signer"]])
attacker_attacks = int(df[df["signer"] == case_row["signer"]].shape[0])

pool_total = df.groupby("pool")["net_profit_sol"].sum().sort_values(ascending=False)
pool_rank = int(pool_total.index.get_loc(case_row["pool"]) + 1)
pool_profit = float(pool_total.loc[case_row["pool"]])
pool_attacks = int(df[df["pool"] == case_row["pool"]].shape[0])

case_profit = float(case_row["net_profit_sol"])
case_cost = float(case_row["cost_sol"])
case_gross = float(case_row["profit_sol"])

summary = {
    "case": {
        "signer": str(case_row["signer"]),
        "pool": str(case_row["pool"]),
        "validator": str(case_row["validator"]),
        "net_profit_sol": case_profit,
        "profit_sol": case_gross,
        "cost_sol": case_cost,
        "classification": str(case_row.get("classification", "FAT_SANDWICH")),
        "confidence": str(case_row.get("confidence", "high")),
    },
    "context": {
        "total_profit_sol": float(total_profit),
        "case_share_of_total_pct": float((case_profit / total_profit) * 100.0),
        "attacker_profit_sol": attacker_profit,
        "attacker_rank": attacker_rank,
        "attacker_attack_count": attacker_attacks,
        "attacker_share_of_total_pct": float((attacker_profit / total_profit) * 100.0),
        "pool_profit_sol": pool_profit,
        "pool_rank": pool_rank,
        "pool_attack_count": pool_attacks,
        "pool_share_of_total_pct": float((pool_profit / total_profit) * 100.0),
    },
}

CASE_JSON.write_text(json.dumps(summary, indent=2))

# Plot: case economics + context shares
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Highest-Value MEV Case Study", fontsize=14, fontweight="bold")

# Panel 1: economics
ax = axes[0]
labels = ["Cost", "Gross Profit", "Net Profit"]
values = [case_cost, case_gross, case_profit]
colors = ["#c0c0c0", "#2ecc71", "#1f77b4"]
ax.bar(labels, values, color=colors)
ax.set_ylabel("SOL")
ax.set_title("Transaction Economics")
for i, v in enumerate(values):
    ax.text(i, v + (max(values) * 0.02), f"{v:.3f}", ha="center", fontweight="bold")

# Panel 2: shares
ax = axes[1]
share_labels = ["Case % of Total", "Attacker % of Total", "Pool % of Total"]
share_values = [
    summary["context"]["case_share_of_total_pct"],
    summary["context"]["attacker_share_of_total_pct"],
    summary["context"]["pool_share_of_total_pct"],
]
ax.bar(share_labels, share_values, color=["#9b59b6", "#e67e22", "#16a085"])
ax.set_ylabel("Percent of Total MEV")
ax.set_title("Contextual Share")
for i, v in enumerate(share_values):
    ax.text(i, v + 0.3, f"{v:.2f}%", ha="center", fontweight="bold")

plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig(CASE_PLOT, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved: {CASE_JSON}")
print(f"Saved: {CASE_PLOT}")
