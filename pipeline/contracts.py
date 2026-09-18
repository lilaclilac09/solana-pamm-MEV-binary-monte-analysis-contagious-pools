from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

@dataclass(frozen=True)
class ArtifactSpec:
    name: str
    kind: str = "file"
    required: bool = False

@dataclass(frozen=True)
class StageSpec:
    stage_id: str
    name: str
    dependencies: tuple[str, ...] = ()
    inputs: tuple[ArtifactSpec, ...] = ()
    outputs: tuple[ArtifactSpec, ...] = ()
    entrypoint: str | None = None
    execution_kind: str = "adapter"

@dataclass
class StageContext:
    run_id: str
    stage: StageSpec
    root: Path
    config: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False
    logger: Callable[[str], None] = print
