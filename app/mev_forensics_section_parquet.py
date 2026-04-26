"""
Parquet-aware drop-in for app/mev_forensics_section.

The original loads four CSVs in helper functions:
  _load_fat_df              -> all_fat_sandwich_only.csv
  _load_all_mev_df          -> all_mev_with_classification.csv
  _load_pool_summary_df     -> POOL_SUMMARY.csv
  _load_validator_relationships_df -> validator_relationships.csv

This sibling re-exports every public symbol from the original but
patches each loader to use ``app.parquet_data_loader.read_table``,
which auto-prefers a Parquet sibling when one exists (after running
``02_mev_detection/convert_filtered_output_to_parquet.py``) and silently
falls back to the original CSV. Empty-DataFrame fallbacks are
preserved.

Wire it into the dashboard by changing the import in app/index.py:

    # before
    from mev_forensics_section import build_mev_forensics_section

    # after
    from mev_forensics_section_parquet import build_mev_forensics_section

The original file is not modified.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).resolve().parent

# ---- import original ------------------------------------------------------
_orig_spec = importlib.util.spec_from_file_location(
    "mev_forensics_section_original",
    _HERE / "mev_forensics_section.py",
)
_orig = importlib.util.module_from_spec(_orig_spec)
_orig_spec.loader.exec_module(_orig)

# ---- import Parquet loader (multi-fallback like oracle_mechanics_component_parquet) ----
try:
    from .parquet_data_loader import read_table  # type: ignore
except ImportError:
    try:
        from app.parquet_data_loader import read_table  # type: ignore
    except ImportError:
        _ploader_spec = importlib.util.spec_from_file_location(
            "parquet_data_loader",
            _HERE / "parquet_data_loader.py",
        )
        _ploader = importlib.util.module_from_spec(_ploader_spec)
        _ploader_spec.loader.exec_module(_ploader)
        read_table = _ploader.read_table


def _safe_read(rel_path: str, fallback_columns: list[str]) -> pd.DataFrame:
    try:
        df = read_table(rel_path)
        if df is None:
            return pd.DataFrame(columns=fallback_columns)
        return df
    except (FileNotFoundError, OSError):
        return pd.DataFrame(columns=fallback_columns)


def _load_fat_df() -> pd.DataFrame:
    return _safe_read(
        "02_mev_detection/filtered_output/all_fat_sandwich_only.csv",
        ["amm_trade", "attacker_signer", "validator",
         "net_profit_sol", "confidence", "classification"],
    )


def _load_all_mev_df() -> pd.DataFrame:
    return _safe_read(
        "02_mev_detection/filtered_output/all_mev_with_classification.csv",
        ["amm_trade", "attacker_signer", "validator", "classification"],
    )


def _load_pool_summary_df() -> pd.DataFrame:
    return _safe_read(
        "02_mev_detection/filtered_output/POOL_SUMMARY.csv",
        ["pool", "unique_attackers", "unique_validators",
         "total_mev_events", "net_profit_sol", "avg_profit_per_event"],
    )


def _load_validator_relationships_df() -> pd.DataFrame:
    return _safe_read(
        "validator_relationships.csv",
        ["validator_1", "validator_2", "shared_attackers", "strength"],
    )


# Patch the helpers in the original module so build_mev_forensics_section
# (which closes over module-level names) uses the Parquet-aware versions.
_orig._load_fat_df = _load_fat_df
_orig._load_all_mev_df = _load_all_mev_df
_orig._load_pool_summary_df = _load_pool_summary_df
_orig._load_validator_relationships_df = _load_validator_relationships_df

# ---- re-export public surface --------------------------------------------
build_mev_forensics_section = _orig.build_mev_forensics_section

__all__ = [
    "build_mev_forensics_section",
    "_load_fat_df",
    "_load_all_mev_df",
    "_load_pool_summary_df",
    "_load_validator_relationships_df",
]


if __name__ == "__main__":
    fat = _load_fat_df()
    allmev = _load_all_mev_df()
    pools = _load_pool_summary_df()
    vrel = _load_validator_relationships_df()
    print(f"fat_df:        {fat.shape}    cols={list(fat.columns)[:6]}")
    print(f"all_mev_df:    {allmev.shape} cols={list(allmev.columns)[:6]}")
    print(f"pool_summary:  {pools.shape}  cols={list(pools.columns)[:6]}")
    print(f"validator_rel: {vrel.shape}   cols={list(vrel.columns)[:6]}")
