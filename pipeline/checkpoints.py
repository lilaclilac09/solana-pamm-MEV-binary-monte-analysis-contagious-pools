import json, os
from pathlib import Path
from typing import Any

def checkpoint_path(root: Path, stage_id: str) -> Path:
    return root / "stages" / stage_id / "status.json"

def write_checkpoint(root: Path, stage_id: str, state: dict[str, Any]) -> Path:
    path = checkpoint_path(root, stage_id); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp'); tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path); return path

def read_checkpoint(root: Path, stage_id: str) -> dict[str, Any] | None:
    path = checkpoint_path(root, stage_id)
    return json.loads(path.read_text()) if path.exists() else None

def is resumable(root: Path, stage_id: str) -> bool:
    state = read_checkpoint(root, stage_id)
    return bool(state and state.get("state") == "succeeded")
