# Dashboard deployment — Parquet-aware path

This file documents how to run the Parquet-routing entrypoint
(`app/index_parquet.py`) locally and what would need to change on
Vercel to make it useful there. **No deploy config has been changed by
this branch** — the modifications below are presented as opt-in
recipes.

## Local / standalone Dash server

The Parquet entrypoint works out of the box once the converters have
been run at least once:

```bash
python3 03_oracle_analysis/convert_csv_to_parquet.py
python3 02_mev_detection/convert_filtered_output_to_parquet.py
python3 app/index_parquet.py        # browse to http://127.0.0.1:8050
# or, with gunicorn:
gunicorn -b 127.0.0.1:8050 --chdir app index_parquet:server
```

Behaviour: `app/index_parquet.py` pre-installs three Parquet-aware
sibling modules (`oracle_mechanics_component_parquet`,
`mev_forensics_section_parquet`, `dangerous_pairs_ranking_parquet`)
under their canonical names so the unmodified `index.py` automatically
uses them. If a Parquet sibling is missing on disk the loaders fall
back to CSV (and ultimately the original hardcoded defaults), so the
dashboard never breaks if the converters haven't been run.

## Current Vercel state (do not assume Python runs there)

Two facts about the existing config that surprised me, so flagging
them explicitly:

1. **`vercel.json` deploys static HTML only** — the only `builds`
   entry is `public/index.html` with `@vercel/static`. There is no
   `@vercel/python` build target, so the Dash app is *not* the page
   Vercel currently serves. Switching the entrypoint from
   `index:server` to `index_parquet:server` therefore has zero effect
   on the live deployment as configured today.

2. **`.vercelignore` excludes every numbered stage directory plus
   `*.csv` and `*.parquet`**. Even if a Python runtime were added,
   none of the data files referenced by the dashboard's loaders would
   be uploaded.

## Recipe to actually serve the Dash app from Vercel

Apply *all four* of the following steps. (None of them are committed
on this branch — pasting them is a deploy-config change you'll want to
review.)

1. Add a Python build target to `vercel.json`:

   ```json
   {
     "version": 2,
     "builds": [
       { "src": "public/index.html", "use": "@vercel/static" },
       { "src": "app/index_parquet.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*\\.pdf)", "dest": "/public/$1" },
       { "src": "/public/(.*)", "dest": "/public/$1" },
       { "src": "/dashboard(/.*)?", "dest": "/app/index_parquet.py" },
       { "src": "/(.*)", "dest": "/public/index.html" }
     ]
   }
   ```

2. Whitelist the parquet outputs in `.vercelignore`. Example: replace

   ```
   *.csv
   *.parquet
   ```

   with explicit allowlist entries:

   ```
   # Block everything by default
   *.csv
   *.parquet
   # Re-allow only what the dashboard reads
   !02_mev_detection/filtered_output/parquet/*.parquet
   !03_oracle_analysis/outputs/parquet/*.parquet
   ```

   and similarly remove the matching numbered-stage directory excludes
   (or keep them and rely on `!`-allowlist re-includes — gitignore /
   vercelignore semantics are the same).

3. Make sure `requirements.txt` on the deploy includes the new deps
   (already done by an earlier commit on this branch: pyarrow,
   duckdb, matplotlib, seaborn).

4. Smoke-test by visiting `/dashboard` after deployment.

## Why I didn't just commit the deploy change

This branch's standing rule is "don't delete originals and don't
break shared state". `vercel.json` and `.vercelignore` decide what
actually ships to your visitors; flipping them silently is the kind
of action I should pause on. If you want me to apply the recipe
above, tell me explicitly and I'll do it as a separate single-purpose
commit so you can revert it independently.
