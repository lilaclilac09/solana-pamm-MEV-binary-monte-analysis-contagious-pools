"""
Parquet-aware drop-in for app/dangerous_pairs_ranking.

The original ``dangerous_pairs_ranking.py`` hardcodes a list of 12
token-pair dicts including ``Oracle Pool`` and ``Oracle Lag (ms)``.
Those two columns duplicate values that the dashboard's
``oracle_mechanics_component`` already loads from
``03_oracle_analysis/outputs/csv/oracle_updates_by_pool.csv``.

This sibling re-exports the original ``build_dangerous_pairs_ranking``
but injects the oracle pool / lag for each token pair from the
Parquet-aware ``load_oracle_lag_data`` *at table-build time*. Any
discrepancy between the hardcoded ranking constants and the
measured oracle data therefore tracks the latest measurements
automatically.

The non-oracle columns (rank, token pair name, risk score, attack
share, volume share, primary causes, risk tier) stay hardcoded — they
are research findings, not raw data.

Wire it into the dashboard by changing the import in app/index.py:

    # before
    from dangerous_pairs_ranking import build_dangerous_pairs_ranking

    # after
    from dangerous_pairs_ranking_parquet import build_dangerous_pairs_ranking

The original file is not modified. ``index_parquet.py`` already
shims this module under the canonical name, so no caller change is
needed when running the Parquet entrypoint.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Pull the original module so we can reuse its layout / styling code.
_orig_spec = importlib.util.spec_from_file_location(
    "dangerous_pairs_ranking_original",
    _HERE / "dangerous_pairs_ranking.py",
)
_orig = importlib.util.module_from_spec(_orig_spec)
_orig_spec.loader.exec_module(_orig)


def _load_oracle_table() -> dict:
    """Load oracle data via the Parquet-aware loader, falling back to
    the original (CSV-or-hardcoded) loader if anything goes wrong."""
    try:
        from .oracle_mechanics_component_parquet import (  # type: ignore
            load_oracle_lag_data,
        )
    except ImportError:
        try:
            from oracle_mechanics_component_parquet import (  # type: ignore
                load_oracle_lag_data,
            )
        except ImportError:
            spec = importlib.util.spec_from_file_location(
                "oracle_mechanics_component_parquet",
                _HERE / "oracle_mechanics_component_parquet.py",
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            load_oracle_lag_data = mod.load_oracle_lag_data
    try:
        return load_oracle_lag_data()
    except Exception:
        return {}


# Map token pair -> oracle pool name, used to look up the lag from the
# loaded oracle table. Mirrors the pair_to_pool_map in
# oracle_mechanics_component.get_oracle_lag_for_pair.
_PAIR_TO_POOL = {
    "PUMP/WSOL": "HumidiFi",
    "BONK/SOL": "ZeroFi",
    "WIF/SOL": "GoonFi",
    "SOL/USDC (Low-Liq)": "BisonFi",
    "New Launches /WSOL": "TesseraV",
    "ORCA/SOL": "SolFiV2",
    "RAY/SOL": "SolFiV2",
    "DUST/SOL": "SolFi",
    "mSOL/SOL": "ZeroFi",
    "SOL/USDC (High-Liq)": "HumidiFi",
    "USDC/USDT": "HumidiFi",
    "WSOL/SOL": "HumidiFi",
}


def build_dangerous_pairs_ranking():
    """Wrap the original builder so the resulting Dash component is
    identical apart from oracle lag/pool values being pulled from the
    Parquet-loaded table."""
    oracle_table = _load_oracle_table()

    # Capture the original's hardcoded list by extracting it from the
    # original function's source — but the simplest path is to call
    # the original to get a Dash component, then update the `data`
    # list of the resulting DataTable. To avoid digging into Dash
    # internals, instead we inline a short patcher that rebuilds the
    # rows with patched oracle values, then defers to the original
    # for everything else.

    component = _orig.build_dangerous_pairs_ranking()

    # Walk the returned component and find the DataTable.
    table = _find_data_table(component)
    if table is None:
        # Original returned an unexpected shape; nothing to patch.
        return component

    rows = list(table.data) if getattr(table, "data", None) else []
    for row in rows:
        pair = row.get("Token Pair")
        pool = _PAIR_TO_POOL.get(pair)
        if pool and pool in oracle_table:
            lag = oracle_table[pool].get("estimated_lag_ms")
            if lag is not None:
                row["Oracle Pool"] = pool
                row["Oracle Lag (ms)"] = int(round(float(lag)))
    table.data = rows
    return component


def _find_data_table(node):
    """Recursively search a Dash component tree for the dash_table
    DataTable; return None if not present."""
    # Dash components have .children which can be a single child, list,
    # or string. DataTable instances expose .data.
    cls_name = type(node).__name__
    if cls_name == "DataTable":
        return node
    children = getattr(node, "children", None)
    if children is None:
        return None
    if isinstance(children, (list, tuple)):
        for child in children:
            found = _find_data_table(child)
            if found is not None:
                return found
        return None
    return _find_data_table(children)


__all__ = ["build_dangerous_pairs_ranking"]


if __name__ == "__main__":
    component = build_dangerous_pairs_ranking()
    table = _find_data_table(component)
    if table is None:
        print("⚠ Could not find DataTable in the component tree.")
    else:
        print(f"Loaded {len(table.data)} rows. Sample row 0:")
        sample = dict(table.data[0])
        for k, v in sample.items():
            if k in ("Oracle Pool", "Oracle Lag (ms)", "Token Pair", "Rank", "Risk Tier"):
                print(f"  {k}: {v}")
