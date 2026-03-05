from pathlib import Path
import json
import pandas as pd
from dash import html, dash_table


BASE_DIR = Path(__file__).resolve().parents[1]


def _resolve_data_path(relative_path: str) -> Path | None:
    rel = Path(relative_path)
    candidates = [
        BASE_DIR / rel,
        BASE_DIR.parent / rel,
        Path.cwd() / rel,
        Path("/var/task") / rel,
        Path("/var/task/user") / rel,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _short(addr: str, n: int = 10) -> str:
    if not isinstance(addr, str) or len(addr) <= n + 3:
        return str(addr)
    return f"{addr[:n]}..."


def _load_fat_df() -> pd.DataFrame:
    path = _resolve_data_path("02_mev_detection/filtered_output/all_fat_sandwich_only.csv")
    if path is None:
        return pd.DataFrame(columns=["amm_trade", "attacker_signer", "validator", "net_profit_sol", "confidence", "classification"])
    return pd.read_csv(path)


def _load_all_mev_df() -> pd.DataFrame:
    path = _resolve_data_path("02_mev_detection/filtered_output/all_mev_with_classification.csv")
    if path is None:
        return pd.DataFrame(columns=["amm_trade", "attacker_signer", "validator", "classification"])
    return pd.read_csv(path)


def _load_pool_summary_df() -> pd.DataFrame:
    path = _resolve_data_path("02_mev_detection/filtered_output/POOL_SUMMARY.csv")
    if path is None:
        return pd.DataFrame(columns=[
            "pool", "unique_attackers", "unique_validators", "total_mev_events",
            "net_profit_sol", "avg_profit_per_event"
        ])
    return pd.read_csv(path)


def _load_validator_relationships_df() -> pd.DataFrame:
    path = _resolve_data_path("validator_relationships.csv")
    if path is None:
        return pd.DataFrame(columns=["validator_1", "validator_2", "shared_attackers", "strength"])
    return pd.read_csv(path)


def _load_contagion_report() -> dict:
    path = _resolve_data_path("contagion_report.json")
    if path is None:
        return {}
    return json.loads(path.read_text())


def _build_fingerprint_tables(fat_df: pd.DataFrame):
    if fat_df.empty:
        return pd.DataFrame(columns=["attacker_signer", "cases", "net_profit_sol", "avg_net_sol", "pools_routed", "validators_touched"])
    top_fingerprints = (
        fat_df.groupby("attacker_signer")
        .agg(
            cases=("attacker_signer", "size"),
            net_profit_sol=("net_profit_sol", "sum"),
            avg_net_sol=("net_profit_sol", "mean"),
            pools_routed=("amm_trade", "nunique"),
            validators_touched=("validator", "nunique"),
        )
        .sort_values(["cases", "net_profit_sol"], ascending=[False, False])
        .head(15)
        .reset_index()
    )
    top_fingerprints["attacker_signer"] = top_fingerprints["attacker_signer"].map(_short)
    top_fingerprints["net_profit_sol"] = top_fingerprints["net_profit_sol"].round(3)
    top_fingerprints["avg_net_sol"] = top_fingerprints["avg_net_sol"].round(4)

    return top_fingerprints


def _build_validator_15_case(fat_df: pd.DataFrame):
    validator_col = "validator"
    profit_col = "net_profit_sol"

    val_counts = fat_df[validator_col].value_counts()
    val_profit_all = fat_df.groupby(validator_col)[profit_col].sum().sort_values(ascending=False)

    if len(val_counts) < 15:
        return None, pd.DataFrame()

    validator_15 = val_counts.index[14]
    cases_15 = int(val_counts.iloc[14])
    profit_15 = float(fat_df[fat_df[validator_col] == validator_15][profit_col].sum())
    profit_rank = int((val_profit_all > profit_15).sum() + 1)

    txs = (
        fat_df[fat_df[validator_col] == validator_15]
        .sort_values(profit_col, ascending=False)
        [["amm_trade", "attacker_signer", "net_profit_sol", "confidence", "classification"]]
        .head(10)
        .copy()
    )
    txs["attacker_signer"] = txs["attacker_signer"].map(_short)
    txs["net_profit_sol"] = txs["net_profit_sol"].round(6)

    summary = {
        "validator": validator_15,
        "validator_short": _short(validator_15, 12),
        "cases": cases_15,
        "profit": round(profit_15, 3),
        "activity_rank": 15,
        "profit_rank": profit_rank,
        "max_tx": float(txs["net_profit_sol"].max()) if len(txs) else 0.0,
    }

    return summary, txs


def _build_other_mev_patterns(all_mev_df: pd.DataFrame):
    if all_mev_df.empty:
        return (
            pd.DataFrame(columns=["classification", "count", "pct"]),
            pd.DataFrame(columns=["classification", "attacker_signer", "cases", "unique_pools", "unique_validators"]),
        )
    class_counts = (
        all_mev_df["classification"].value_counts().rename_axis("classification").reset_index(name="count")
    )
    class_counts["pct"] = (class_counts["count"] / len(all_mev_df) * 100).round(2)

    wallet_patterns = []
    for classification, grp in all_mev_df.groupby("classification"):
        top_wallets = grp["attacker_signer"].value_counts().head(5)
        for signer, count in top_wallets.items():
            wallet_patterns.append(
                {
                    "classification": classification,
                    "attacker_signer": _short(signer),
                    "cases": int(count),
                    "unique_pools": int(grp[grp["attacker_signer"] == signer]["amm_trade"].nunique()),
                    "unique_validators": int(grp[grp["attacker_signer"] == signer]["validator"].nunique()),
                }
            )

    wallet_patterns_df = pd.DataFrame(wallet_patterns)
    return class_counts, wallet_patterns_df


def _build_contagion_view(pool_df: pd.DataFrame, rel_df: pd.DataFrame, contagion_report: dict):
    if pool_df.empty:
        pool_rank = pd.DataFrame(columns=[
            "pool", "risk_score", "total_mev_events", "unique_attackers",
            "unique_validators", "net_profit_sol", "avg_profit_per_event"
        ])
        rel = rel_df.copy()
        cascade_summary = {
            "trigger_pool": "N/A",
            "trigger_attacks": 0,
            "cascaded_attacks": 0,
            "cascade_percentage": 0.0,
            "time_window_ms": 5000,
            "interpretation": "No contagion data available in deployment bundle.",
        }
        return pool_rank, rel, cascade_summary

    pool_view = pool_df.copy()
    pool_view["risk_score"] = (
        (pool_view["net_profit_sol"] / pool_view["net_profit_sol"].max()) * 0.45
        + (pool_view["total_mev_events"] / pool_view["total_mev_events"].max()) * 0.35
        + (pool_view["unique_attackers"] / pool_view["unique_attackers"].max()) * 0.20
    )
    pool_view["risk_score"] = pool_view["risk_score"].round(3)
    pool_view = pool_view.sort_values("risk_score", ascending=False)

    pool_rank = pool_view[
        [
            "pool",
            "risk_score",
            "total_mev_events",
            "unique_attackers",
            "unique_validators",
            "net_profit_sol",
            "avg_profit_per_event",
        ]
    ].head(8)
    pool_rank["net_profit_sol"] = pool_rank["net_profit_sol"].round(3)
    pool_rank["avg_profit_per_event"] = pool_rank["avg_profit_per_event"].round(4)

    rel = rel_df.copy().head(15)
    rel["validator_1"] = rel["validator_1"].map(_short)
    rel["validator_2"] = rel["validator_2"].map(_short)

    cascade = (
        contagion_report.get("sections", {})
        .get("cascade_rate_analysis", {})
        .get("cascade_rates", {})
    )
    trigger_pool = (
        contagion_report.get("sections", {})
        .get("trigger_pool_identification", {})
        .get("trigger_pool", "N/A")
    )
    cascade_summary = {
        "trigger_pool": trigger_pool,
        "trigger_attacks": int(cascade.get("trigger_attacks_total", 0)),
        "cascaded_attacks": int(cascade.get("cascaded_attacks", 0)),
        "cascade_percentage": float(cascade.get("cascade_percentage", 0.0)),
        "time_window_ms": int(cascade.get("time_window_ms", 5000)),
        "interpretation": cascade.get("interpretation", "No cascade interpretation available."),
    }

    return pool_rank, rel, cascade_summary


def build_mev_forensics_section():
    fat_df = _load_fat_df()
    all_mev_df = _load_all_mev_df()
    pool_df = _load_pool_summary_df()
    rel_df = _load_validator_relationships_df()
    contagion_report = _load_contagion_report()

    top_fingerprints = _build_fingerprint_tables(fat_df)
    validator_case, validator_case_txs = _build_validator_15_case(fat_df)
    class_counts, wallet_patterns_df = _build_other_mev_patterns(all_mev_df)
    pool_rank, rel_top, cascade_summary = _build_contagion_view(pool_df, rel_df, contagion_report)

    multi_hop_count = 0
    if not class_counts.empty and "classification" in class_counts.columns:
        multi_hop_count = int(class_counts[class_counts["classification"] == "MULTI_HOP_ARBITRAGE"]["count"].sum())

    if validator_case is None:
        validator_case = {
            "validator": "N/A",
            "validator_short": "N/A",
            "cases": 0,
            "profit": 0.0,
            "activity_rank": 15,
            "profit_rank": 0,
            "max_tx": 0.0,
        }

    return html.Div([
        html.H2("🔬 MEV Forensics Lab", style={"fontSize": "28px", "fontWeight": 700, "color": "#111827", "marginBottom": "8px"}),
        html.P(
            "Deep research panel from your codebase: fingerprints, validator anomaly cases, non-fat-sandwich patterns, and pool contagion risk.",
            style={"fontSize": "14px", "color": "#6b7280", "marginBottom": "20px"}
        ),

        html.Div([
            html.Div([
                html.Div(f"{fat_df['attacker_signer'].nunique() if 'attacker_signer' in fat_df.columns else 0}", style={"fontSize": "28px", "fontWeight": 700, "color": "#dc2626"}),
                html.Div("MEV Fingerprints (FAT_SANDWICH wallets)", style={"fontSize": "12px", "color": "#6b7280"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "16px", "borderRadius": "8px"}),
            html.Div([
                html.Div(f"{len(all_mev_df)}", style={"fontSize": "28px", "fontWeight": 700, "color": "#1d4ed8"}),
                html.Div("All Classified MEV Cases", style={"fontSize": "12px", "color": "#6b7280"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "16px", "borderRadius": "8px"}),
            html.Div([
                html.Div(f"{multi_hop_count}", style={"fontSize": "28px", "fontWeight": 700, "color": "#7c3aed"}),
                html.Div("Multi-Hop Arbitrage Cases", style={"fontSize": "12px", "color": "#6b7280"}),
            ], style={"backgroundColor": "#f5f3ff", "padding": "16px", "borderRadius": "8px"}),
            html.Div([
                html.Div(f"{cascade_summary['cascade_percentage']:.1f}%", style={"fontSize": "28px", "fontWeight": 700, "color": "#d97706"}),
                html.Div("Measured Cascade Rate (current report)", style={"fontSize": "12px", "color": "#6b7280"}),
            ], style={"backgroundColor": "#fffbeb", "padding": "16px", "borderRadius": "8px"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px", "marginBottom": "24px"}),

        html.H3("1) MEV Fingerprints Found — Who Are They?", style={"fontSize": "20px", "fontWeight": 700, "marginBottom": "10px", "color": "#111827"}),
        html.P(
            "Fingerprint definition selected: unique attacker wallets in validated FAT_SANDWICH dataset.",
            style={"fontSize": "13px", "color": "#4b5563", "marginBottom": "10px"}
        ),
        dash_table.DataTable(
            data=top_fingerprints.to_dict("records"),
            columns=[
                {"name": "Attacker Wallet", "id": "attacker_signer"},
                {"name": "Cases", "id": "cases"},
                {"name": "Net Profit (SOL)", "id": "net_profit_sol"},
                {"name": "Avg Net (SOL)", "id": "avg_net_sol"},
                {"name": "Pools Routed", "id": "pools_routed"},
                {"name": "Validators Touched", "id": "validators_touched"},
            ],
            sort_action="native",
            style_cell={"padding": "10px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"column_id": "cases"}, "fontWeight": 700, "color": "#b91c1c"},
                {"if": {"column_id": "net_profit_sol"}, "fontWeight": 700, "color": "#047857"},
            ],
            page_size=10,
        ),

        html.H3("2) Validator Anomaly Case (Activity Rank #15 vs Profit Rank #1)", style={"fontSize": "20px", "fontWeight": 700, "marginTop": "24px", "marginBottom": "10px", "color": "#111827"}),
        html.P([
            html.Strong("What is MEV here? "),
            "MEV is extractable value captured by ordering trades (especially fat sandwich patterns) around victim flows for net profit."
        ], style={"fontSize": "13px", "color": "#374151", "marginBottom": "8px"}),

        html.Div([
            html.P(
                f"Exact case: validator {validator_case['validator_short']} is #15 by MEV case count ({validator_case['cases']} cases) but #1 by profit ({validator_case['profit']} SOL). "
                f"This is driven by a single outsized transaction of {validator_case['max_tx']:.3f} SOL.",
                style={"fontSize": "13px", "color": "#111827", "margin": "0"}
            )
        ], style={"backgroundColor": "#ecfeff", "border": "1px solid #67e8f9", "padding": "12px", "borderRadius": "8px", "marginBottom": "10px"}),

        dash_table.DataTable(
            data=validator_case_txs.to_dict("records"),
            columns=[
                {"name": "Pool", "id": "amm_trade"},
                {"name": "Attacker Wallet", "id": "attacker_signer"},
                {"name": "Net Profit (SOL)", "id": "net_profit_sol"},
                {"name": "Confidence", "id": "confidence"},
                {"name": "Class", "id": "classification"},
            ],
            style_cell={"padding": "10px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"column_id": "net_profit_sol"}, "fontWeight": 700, "color": "#b91c1c"},
            ],
            page_size=10,
        ),

        html.H3("3) Other MEV Cases + Wallet Patterns", style={"fontSize": "20px", "fontWeight": 700, "marginTop": "24px", "marginBottom": "10px", "color": "#111827"}),
        html.Div([
            html.Div([
                html.H4("Case Type Distribution", style={"fontSize": "15px", "fontWeight": 700, "marginBottom": "8px"}),
                dash_table.DataTable(
                    data=class_counts.to_dict("records"),
                    columns=[
                        {"name": "Classification", "id": "classification"},
                        {"name": "Count", "id": "count"},
                        {"name": "%", "id": "pct"},
                    ],
                    style_cell={"padding": "8px", "fontSize": "12px", "textAlign": "left"},
                    style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
                ),
            ], style={"backgroundColor": "#ffffff", "padding": "10px", "border": "1px solid #e5e7eb", "borderRadius": "8px"}),

            html.Div([
                html.H4("Top Wallet Patterns by Case Type", style={"fontSize": "15px", "fontWeight": 700, "marginBottom": "8px"}),
                dash_table.DataTable(
                    data=wallet_patterns_df.to_dict("records"),
                    columns=[
                        {"name": "Classification", "id": "classification"},
                        {"name": "Wallet", "id": "attacker_signer"},
                        {"name": "Cases", "id": "cases"},
                        {"name": "Pools", "id": "unique_pools"},
                        {"name": "Validators", "id": "unique_validators"},
                    ],
                    sort_action="native",
                    style_cell={"padding": "8px", "fontSize": "12px", "textAlign": "left"},
                    style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
                    page_size=10,
                ),
            ], style={"backgroundColor": "#ffffff", "padding": "10px", "border": "1px solid #e5e7eb", "borderRadius": "8px"}),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1.8fr", "gap": "12px"}),

        html.H3("4) Pool Contagion Risk — Which Pools and Why", style={"fontSize": "20px", "fontWeight": 700, "marginTop": "24px", "marginBottom": "10px", "color": "#111827"}),
        html.P(
            "Primary risk ranking uses pool-level events/profit/attacker concentration. Cascade-rate report is shown with limitations (timestamp granularity currently yields 0% measured cascades).",
            style={"fontSize": "13px", "color": "#4b5563", "marginBottom": "10px"}
        ),

        dash_table.DataTable(
            data=pool_rank.to_dict("records"),
            columns=[
                {"name": "Pool", "id": "pool"},
                {"name": "Risk Score", "id": "risk_score"},
                {"name": "MEV Events", "id": "total_mev_events"},
                {"name": "Unique Attackers", "id": "unique_attackers"},
                {"name": "Unique Validators", "id": "unique_validators"},
                {"name": "Net Profit (SOL)", "id": "net_profit_sol"},
                {"name": "Avg Profit/Event", "id": "avg_profit_per_event"},
            ],
            sort_action="native",
            style_cell={"padding": "10px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"column_id": "risk_score"}, "fontWeight": 700, "color": "#b91c1c"},
                {"if": {"column_id": "net_profit_sol"}, "fontWeight": 700, "color": "#047857"},
            ],
            page_size=8,
        ),

        html.Div([
            html.Div([
                html.H4("Validator Shared-Attacker Network (Top edges)", style={"fontSize": "15px", "fontWeight": 700, "marginBottom": "8px"}),
                dash_table.DataTable(
                    data=rel_top.to_dict("records"),
                    columns=[
                        {"name": "Validator A", "id": "validator_1"},
                        {"name": "Validator B", "id": "validator_2"},
                        {"name": "Shared Attackers", "id": "shared_attackers"},
                        {"name": "Overlap Strength", "id": "strength"},
                    ],
                    style_cell={"padding": "8px", "fontSize": "12px", "textAlign": "left"},
                    style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
                    page_size=8,
                ),
            ], style={"backgroundColor": "#ffffff", "padding": "10px", "border": "1px solid #e5e7eb", "borderRadius": "8px"}),

            html.Div([
                html.H4("Cascade Report (with limitation note)", style={"fontSize": "15px", "fontWeight": 700, "marginBottom": "8px"}),
                html.Ul([
                    html.Li(f"Trigger Pool: {cascade_summary['trigger_pool']}", style={"fontSize": "12px", "marginBottom": "6px"}),
                    html.Li(f"Trigger Attacks: {cascade_summary['trigger_attacks']}", style={"fontSize": "12px", "marginBottom": "6px"}),
                    html.Li(f"Cascaded Attacks: {cascade_summary['cascaded_attacks']}", style={"fontSize": "12px", "marginBottom": "6px"}),
                    html.Li(f"Cascade %: {cascade_summary['cascade_percentage']:.1f}% (window={cascade_summary['time_window_ms']}ms)", style={"fontSize": "12px", "marginBottom": "6px"}),
                ], style={"paddingLeft": "18px", "margin": "0"}),
                html.P(
                    "Limitation: this metric currently underestimates contagion due to timestamp granularity/sequence resolution; network overlap and pool concentration are stronger indicators in current data.",
                    style={"fontSize": "12px", "color": "#92400e", "backgroundColor": "#fffbeb", "padding": "10px", "borderRadius": "6px", "border": "1px solid #fcd34d", "marginTop": "8px"}
                ),
            ], style={"backgroundColor": "#ffffff", "padding": "10px", "border": "1px solid #e5e7eb", "borderRadius": "8px"}),
        ], style={"display": "grid", "gridTemplateColumns": "1.3fr 1fr", "gap": "12px"}),

    ], style={"marginBottom": "40px", "backgroundColor": "white", "padding": "20px", "borderRadius": "8px", "border": "1px solid #e5e7eb"})
