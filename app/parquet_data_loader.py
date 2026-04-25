"""
Parquet-aware data loader for the Dash dashboard (opt-in).

Existing dashboard components call ``pd.read_csv(path)`` directly. When
the converters in ``03_oracle_analysis/`` and
``02_mev_detection/`` have been run, a Parquet sibling exists for every
CSV under ``outputs/parquet/`` (much smaller, much faster to read).

This module provides a single entry point ``read_table(csv_path)`` that:
  1. Looks for a Parquet sibling at ``<dir>/parquet/<stem>.parquet`` or
     ``<dir>/<stem>.parquet`` — whichever exists.
  2. Falls back to the original CSV path if no Parquet copy exists yet.
  3. Resolves both relative and Vercel-deployed absolute paths via the
     same multi-candidate lookup the existing components use.

Use it from any dashboard component without touching the original
files:

    from app.parquet_data_loader import read_table
    df = read_table("03_oracle_analysis/outputs/csv/oracle_updates_by_pool.csv")

If the corresponding ``oracle_updates_by_pool.parquet`` is on disk the
loader uses it; otherwise it transparently reads the CSV.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

_DEPLOY_ROOTS = (
    Path(__file__).resolve().parent.parent,
    Path.cwd(),
    Path("/var/task"),
    Path("/var/task/user"),
)


def _resolve(relative: Path) -> Optional[Path]:
    """Same resolution logic as app/oracle_mechanics_component.py
    so this drops cleanly into the existing components."""
    for root in _DEPLOY_ROOTS:
        candidate = root / relative
        if candidate.exists():
            return candidate
    return None


def _parquet_sibling(csv_path: Path) -> Path:
    """Preferred Parquet location:
       <stage>/outputs/parquet/<stem>.parquet
    Mirrors the layout produced by 03_oracle_analysis/convert_csv_to_parquet.py
    and 02_mev_detection/convert_filtered_output_to_parquet.py."""
    stem = csv_path.stem
    parent = csv_path.parent
    if parent.name == "csv":
        return parent.parent / "parquet" / f"{stem}.parquet"
    return parent / "parquet" / f"{stem}.parquet"


def read_table(path: str | Path, **kwargs) -> pd.DataFrame:
    """Read a tabular file, preferring a Parquet sibling if available.

    ``kwargs`` are forwarded to ``pd.read_parquet`` or ``pd.read_csv``
    as appropriate. ``columns=[...]`` works on both backends, so the
    common case "give me only these columns" benefits from Parquet's
    column pruning whenever the Parquet exists.
    """
    rel = Path(path)
    csv_resolved = _resolve(rel)

    # Try the Parquet sibling against every deploy root.
    pq_rel = _parquet_sibling(rel)
    pq_resolved = _resolve(pq_rel)

    # Also check Parquet sibling next to the resolved CSV (in case the
    # whole stage tree is cwd-relative).
    if pq_resolved is None and csv_resolved is not None:
        candidate = _parquet_sibling(csv_resolved)
        if candidate.exists():
            pq_resolved = candidate

    if pq_resolved is not None:
        # pd.read_parquet doesn't accept all read_csv kwargs; filter.
        pq_kwargs = {k: v for k, v in kwargs.items() if k in {"columns", "engine"}}
        return pd.read_parquet(pq_resolved, **pq_kwargs)

    if csv_resolved is None:
        raise FileNotFoundError(f"Neither CSV nor Parquet sibling found for {path}")
    return pd.read_csv(csv_resolved, **kwargs)


def storage_used(path: str | Path) -> dict:
    """Return whether Parquet is in use plus path/size info, useful for
    logging on Vercel cold starts."""
    rel = Path(path)
    pq = _resolve(_parquet_sibling(rel))
    if pq is not None:
        return {"backend": "parquet", "path": str(pq), "bytes": pq.stat().st_size}
    csv = _resolve(rel)
    if csv is not None:
        return {"backend": "csv", "path": str(csv), "bytes": csv.stat().st_size}
    return {"backend": "none", "path": None, "bytes": 0}


if __name__ == "__main__":
    # Quick self-test against one of the converted oracle CSVs.
    paths = [
        "03_oracle_analysis/outputs/csv/oracle_updates_by_pool.csv",
        "03_oracle_analysis/outputs/csv/oracle_slot_patterns.csv",
        "02_mev_detection/filtered_output/all_fat_sandwich_only.csv",
    ]
    for p in paths:
        info = storage_used(p)
        print(f"  {p}\n    backend={info['backend']}  bytes={info['bytes']}  path={info['path']}")
        try:
            df = read_table(p)
            print(f"    -> read OK, shape={df.shape}")
        except Exception as exc:
            print(f"    -> read FAILED: {exc}")
