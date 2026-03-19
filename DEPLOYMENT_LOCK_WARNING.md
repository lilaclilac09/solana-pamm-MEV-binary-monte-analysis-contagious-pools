# 🚫 WARNING: DEPLOYMENT LOCKED

This project is locked against accidental Vercel redeploys.

- Do NOT deploy from this root unless you intend to update aileena.xyz only.
- mev.aileena.xyz is deployed separately from /mev and must not be affected by root redeploys.
- Remove all Vercel Git integrations and disable automatic deployments.
- Only use manual deployment scripts for mev.aileena.xyz.

## How to Lock Further
- Restrict Vercel project/team access.
- Remove Vercel tokens from CI/CD.
- Add HTTP auth or server-level protection if needed.
