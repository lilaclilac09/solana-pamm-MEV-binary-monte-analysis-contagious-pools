# Acceptance audit — 2026-11-22

Existing work checked against [ACCEPTANCE.md](../ACCEPTANCE.md) and repository instructions. No runtime code, analysis data, dependency manifest or deployment configuration changed.

| # | Item | Fails rule | Source rule | Fix |
|---|------|-----------|-------------|-----|
| 1 | Merged PRs #2, #3, #5, #6, #7, #8 | Missing §8 evidence closer; checker exits 1 for all six | §8, `verification.mdc` "Every final reply" | Not fixable after merge; recorded. PR #9 passes |
| 2 | PR #2 changed both existing HTML UI entrypoints without 390×844 still + interaction evidence | Required mobile still and interaction proof | §4, `ui-step-screenshot.mdc` | Captured local `app/index.html` anchor-navigation proof, local Dash chart hover, and actual public report scroll walkthrough, each as 390×844 PNGs plus animated WebP; production images are broken, so live walkthrough is failure evidence, not repaired-product acceptance |
| 3 | README calls public report an interactive live dashboard with full PDF view; lacks status + next action | Cannot claim unobserved production verification; status + next human action required | §2 and §5, `verification.mdc` / `ship-visible-mvp.mdc` | Added BLOCKED scoped to production visualizations, qualified link/body claims, and named owner restore-assets action respecting the deployment lock |

All seven API-fetched merged PR SHAs are ancestral to `origin/main` (exit 0 each). Pages API returns 404; deployments API returns a nonempty list including Production deployments. The public URL returns HTTP 200 and its HTML matches `public/index.html`; its title is `MEV Threat Intelligence: Visual Analysis - mev.aileen.xyz`. Reachability alone is not working visualization proof: the first PNG URL returns HTTP 200 with `Content-Type: text/html`, and its downloaded body matches the report HTML. Browser inspection shows `naturalWidth = 0` for the image. Repository `vercel.json` routes unmatched paths to `/public/index.html`, consistent with this response, and `public/` contains only the HTML and PDF, not the referenced PNGs. The complete live deployment's build/source mapping is unverified; no deployment was attempted.

Product surfaces and paths (all read-only):

- Public report: open `https://mev.aileena.xyz` → scroll to first visualization → observe image failure → read takeaways. This is blocker evidence, not a success path.
- Local Dash: install existing `requirements.txt` in an external venv → run `app/index.py` → open `http://127.0.0.1:8050/` → scroll to liquidity chart → hover BisonFi. Tooltip `(892K, 3.4)BisonFi` appeared; three Plotly charts loaded; browser page errors 0. No production parity or analytics ingestion claim.
- Existing local HTML: serve `app/` on loopback → open it → click Visualizations → inspect loaded chart. This records the other HTML entrypoint changed in PR #2, not an alternative implementation.

| blocked_on | evidence | impact | human_action | not_doing |
|------------|----------|--------|--------------|-----------|
| Production report visualization assets/routing | `/token_pair_fragility.png`: HTTP 200, content-type text/html, same report body; browser image naturalWidth 0 | degraded: page reachable but visualization acceptance incomplete | Review `DEPLOYMENT_LOCK_WARNING.md` and restore assets through the intended separately managed MEV deployment | No root Vercel deployment, no deployment/config rewrite, no localhost-as-production claim |

Checks: existing requirements installed in an external artifact venv for Dash rendering; seven app Python files compile without syntax errors; Flask test client gets HTTP 200 for `/`, `/_dash-layout`, `/_dash-dependencies`; real Playwright Chromium exercises the three surfaces; PNG dimensions and animated-WebP frame structure checked; draft acceptance checker and `git diff --check`. Root instructions list no application lint/test command. Research notebooks, external RPC probes, model retraining and dataset regeneration were not run for documentation changes; analytics delivery/ingestion and full PDF browser viewing were not verified. The local PDF exists (8,526,483 bytes), not proof of production PDF access.

Observed, no rule covers it: wide legacy tables/charts can overflow the 390px viewport; the acceptance source's no-overflow requirement is scoped to aileena.xyz `/`, not this report. No responsive redesign was attempted.

Artifacts outside git: `~/audit-artifacts/solana-pamm-MEV-binary-monte-analysis-contagious-pools/` contains seven PR bodies/check logs/file lists, ancestry/deployment/HTTP logs, `live.html`, `live-image-response`, local install/dev/browser logs; `initial-390x844.png`, `chart-hover-390x844.png`, `interaction.webp`; `app-static-initial-390x844.png`, `app-static-navigation-390x844.png`, `app-static-interaction.webp`; `live-initial-390x844.png`, `live-figure-390x844.png`, `live-scrolled-390x844.png`, `live-interaction.webp`; browser-check JSONs; and `pr-body.md`. WebPs are animated, not WebM/MP4 deliverables. Upload/attach these local artifacts before posting the draft; this audit opens no PR.
