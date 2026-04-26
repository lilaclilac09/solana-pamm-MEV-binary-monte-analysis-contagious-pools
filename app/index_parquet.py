#!/usr/bin/env python3
"""
Parquet-routing entrypoint for the Dash dashboard.

Original entrypoint ``app/index.py`` loads four sub-components:
  - dangerous_pairs_ranking      (no data I/O — pure Python dicts)
  - mev_forensics_section        (reads 4 CSVs)
  - oracle_mechanics_component   (reads 1 CSV)
  - risk_formulation_component   (no data I/O — pure code)

This file pre-installs the ``*_parquet`` variants under the canonical
module names in ``sys.modules`` so the unmodified original ``index.py``
sees Parquet-aware loaders for the two CSV-reading components, then
exposes the resulting Dash ``app`` / ``server``.

Use this in your Vercel/local entrypoint (e.g. swap the WSGI target
from ``index:server`` to ``index_parquet:server``); the original files
are not touched.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _shim(canonical_name: str, parquet_filename: str) -> None:
    """Import a Parquet-aware sibling under the original module name so
    ``from <canonical_name> import ...`` resolves to it."""
    path = HERE / parquet_filename
    spec = importlib.util.spec_from_file_location(canonical_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load shim {parquet_filename} as {canonical_name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[canonical_name] = mod
    spec.loader.exec_module(mod)


# Install the shims BEFORE importing index.py.
_shim("oracle_mechanics_component", "oracle_mechanics_component_parquet.py")
_shim("mev_forensics_section", "mev_forensics_section_parquet.py")
_shim("dangerous_pairs_ranking", "dangerous_pairs_ranking_parquet.py")

# Make sure the original index.py's local imports resolve.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Now load the unmodified original index.py.
_index_spec = importlib.util.spec_from_file_location(
    "_dashboard_index_original",
    HERE / "index.py",
)
if _index_spec is None or _index_spec.loader is None:
    raise ImportError("Cannot find app/index.py")
_index = importlib.util.module_from_spec(_index_spec)
_index_spec.loader.exec_module(_index)

# Re-export the entrypoint surface.
app = _index.app
server = _index.server

__all__ = ["app", "server"]


if __name__ == "__main__":
    # Local dev convenience.
    print("Dashboard wired through Parquet-aware components.")
    print(f"  oracle_mechanics_component -> {sys.modules['oracle_mechanics_component'].__file__}")
    print(f"  mev_forensics_section      -> {sys.modules['mev_forensics_section'].__file__}")
    print("Run with: gunicorn index_parquet:server  (or Dash dev server)")
    try:
        app.run(debug=False, host="127.0.0.1", port=8050)
    except AttributeError:
        # Older Dash uses run_server.
        app.run_server(debug=False, host="127.0.0.1", port=8050)
