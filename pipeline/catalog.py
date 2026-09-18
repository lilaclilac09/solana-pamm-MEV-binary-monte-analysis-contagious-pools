from .contracts import ArtifactSpec, StageSpec

_IDS = ["00","01","01a","01b","02","03","04","05","06","07","08","09a","10","11","12","13","14","15","16","17"]
_NAMES = {"00":"planning","01":"data-cleaning","01a":"deeznode-filters","01b":"jito-tip-filter","02":"mev-detection","03":"oracle-analysis","04":"validator-analysis","05":"token-pair-analysis","06":"pool-analysis","07":"ml-classification","08":"monte-carlo-risk","09a":"advanced-ml","10":"advanced-fp-solution","11":"report-generation","12":"live-dashboard","13":"comprehensive-analysis","14":"slot-jump-analysis","15":"deployment-config","16":"harmonic-validation","17":"realtime-db-etl"}

def _deps(i: int) -> tuple[str, ...]:
    return () if i == 0 else (_IDS[i-1],)

def build_catalog() -> dict[str, StageSpec]:
    return {sid: StageSpec(sid, _NAMES[sid], _deps(i), (ArtifactSpec("upstream-manifest", required=False),), (ArtifactSpec("stage-manifest"),), f"{sid}_{_NAMES[sid]}") for i, sid in enumerate(_IDS)}

CATALOG = build_catalog()

def get_stage(stage_id: str) -> StageSpec:
    try: return CATALOG[stage_id]
    except KeyError as exc: raise ValueError(f"Unknown stage: {stage_id}") from exc

def validate_catalog() -> list[str]:
    errors = []
    for sid, stage in CATALOG.items():
        errors.extend(f"{sid}: unknown dependency {d}" for d in stage.dependencies if d not in CATALOG)
    return errors
