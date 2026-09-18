from pathlib import Path
from .contracts import StageContext
from .checkpoints import write_checkpoint

def plan(ctx: StageContext) -> dict:
    return {"stage_id": ctx.stage.stage_id, "entrypoint": ctx.stage.entrypoint, "mode": "plan-only"}

def run(ctx: StageContext) -> dict:
    # Deliberately does not execute or modify legacy stage files yet.
    result = {"stage_id": ctx.stage.stage_id, "state": "succeeded", "mode": "adapter-placeholder"}
    write_checkpoint(ctx.root, ctx.stage.stage_id, result)
    return result
