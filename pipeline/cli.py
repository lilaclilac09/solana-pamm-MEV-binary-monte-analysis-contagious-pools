import argparse, json
from pathlib import Path
from .catalog import CATALOG, validate_catalog, get_stage
from .contracts import StageContext
from .adapters import plan, run as run_stage
from .checkpoints import read_checkpoint

def main(argv=None):
    p=argparse.ArgumentParser(prog="python -m pipeline")
    sub=p.add_subparsers(dest="command", required=True)
    sub.add_parser("list"); sub.add_parser("validate")
    s=sub.add_parser("status"); s.add_argument("--run-dir", default="runs/default")
    r=sub.add_parser("run"); r.add_argument("stage", nargs="+"); r.add_argument("--run-dir", default="runs/default"); r.add_argument("--dry-run", action="store_true")
    q=sub.add_parser("resume"); q.add_argument("--run-dir", default="runs/default")
    a=p.parse_args(argv)
    if a.command == "list":
        for x in CATALOG.values(): print(f"{x.stage_id}\t{x.name}\tdeps={','.join(x.dependencies) or '-'}")
    elif a.command == "validate":
        errors=validate_catalog(); print("catalog valid" if not errors else "\n".join(errors)); return int(bool(errors))
    elif a.command == "status":
        root=Path(a.run_dir)
        for sid in CATALOG: print(json.dumps(read_checkpoint(root, sid) or {"stage_id":sid,"state":"pending"}))
    elif a.command == "run":
        root=Path(a.run_dir)
        for sid in a.stage:
            ctx=StageContext(root.name, get_stage(sid), root, dry_run=a.dry_run)
            print(json.dumps(plan(ctx) if a.dry_run else run_stage(ctx)))
    elif a.command == "resume":
        print("resume plan: inspect status and rerun pending stages")
    return 0

if __name__ == "__main__": raise SystemExit(main())
