"""
Parquet-aware drop-in for app/oracle_mechanics_component.

The original component reads
``03_oracle_analysis/outputs/csv/oracle_updates_by_pool.csv`` directly
via ``pd.read_csv``. This sibling re-exports every public symbol from
the original but overrides ``load_oracle_lag_data`` to use
``app.parquet_data_loader.read_table``, which auto-prefers a Parquet
sibling when one exists (after running
``03_oracle_analysis/convert_csv_to_parquet.py``) and silently falls
back to the original CSV otherwise.

Wire it into the dashboard by changing the import:

    # before
    from oracle_mechanics_component import (
        get_oracle_lag_for_pair,
        build_oracle_lag_explanation,
        build_oracle_lag_visualization,
    )

    # after
    from oracle_mechanics_component_parquet import (
        get_oracle_lag_for_pair,
        build_oracle_lag_explanation,
        build_oracle_lag_visualization,
    )

The original file is not modified.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# Re-export every public symbol from the original module so that
# downstream imports keep working unchanged.
_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "oracle_mechanics_component_original",
    _HERE / "oracle_mechanics_component.py",
)
_orig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_orig)

# These public callables are passthroughs.
get_oracle_lag_for_pair = _orig.get_oracle_lag_for_pair
build_oracle_lag_explanation = _orig.build_oracle_lag_explanation
build_oracle_lag_visualization = _orig.build_oracle_lag_visualization

# Try to use the new Parquet-aware loader; fall back to CSV path
# verbatim if it isn't on the import path (e.g. tests outside app/).
try:
    from .parquet_data_loader import read_table  # type: ignore
except ImportError:
    try:
        from app.parquet_data_loader import read_table  # type: ignore
    except ImportError:
        # Final fallback: load the helper file directly.
        _ploader_spec = importlib.util.spec_from_file_location(
            "parquet_data_loader",
            _HERE / "parquet_data_loader.py",
        )
        _ploader = importlib.util.module_from_spec(_ploader_spec)
        _ploader_spec.loader.exec_module(_ploader)
        read_table = _ploader.read_table


def load_oracle_lag_data() -> dict:
    """Parquet-preferring drop-in for the original ``load_oracle_lag_data``.

    Reads ``oracle_updates_by_pool`` via ``read_table`` (which prefers
    Parquet over CSV when a sibling exists) and computes the same
    ``estimated_lag_ms`` formula. On any error the function falls back
    to the original CSV-based loader to preserve the original
    hardcoded-defaults behaviour.
    """
    try:
        df = read_table("03_oracle_analysis/outputs/csv/oracle_updates_by_pool.csv")
    except (FileNotFoundError, OSError):
        return _orig.load_oracle_lag_data()

    if df is None or df.empty or 'pool' not in df.columns:
        return _orig.load_oracle_lag_data()

    oracle_data: dict = {}
    for pool, updates_per_slot in zip(df['pool'], df['updates_per_slot']):
        # Same formula as the original: lag_ms = 400ms / updates_per_slot
        estimated_lag_ms = round(400 / max(float(updates_per_slot), 0.1), 0)
        oracle_data[pool] = {
            "updates_per_slot": float(updates_per_slot),
            "estimated_lag_ms": estimated_lag_ms,
        }
    return oracle_data


__all__ = [
    "load_oracle_lag_data",
    "get_oracle_lag_for_pair",
    "build_oracle_lag_explanation",
    "build_oracle_lag_visualization",
]


if __name__ == "__main__":
    data = load_oracle_lag_data()
    print(f"Loaded oracle data for {len(data)} pools")
    for pool, info in sorted(data.items(),
                             key=lambda kv: kv[1].get('estimated_lag_ms', 0)):
        print(f"  {pool:12s}  updates/slot={info['updates_per_slot']:.2f}  "
              f"lag_ms={info['estimated_lag_ms']:.0f}")
