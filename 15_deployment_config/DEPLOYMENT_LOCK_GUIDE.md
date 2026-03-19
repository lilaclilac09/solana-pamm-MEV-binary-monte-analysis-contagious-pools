# Deployment Lock & Isolation Guide

## Goals
- Prevent redeploying aileena.xyz from affecting mev.aileena.xyz
- Lock both sites from accidental Vercel updates

## Steps
1. **Separate Vercel Projects**: Ensure aileena.xyz and mev.aileena.xyz are in different Vercel projects with their own repos/folders.
2. **Remove Vercel Git Integration**: Disconnect GitHub/GitLab from Vercel for both projects. Only deploy manually via CLI if needed.
3. **Disable Automatic Deployments**: In Vercel dashboard, turn off all auto-deploy triggers.
4. **Restrict Access**: Limit Vercel project/team access to trusted users only.
5. **Manual Deploy Only**: Use only the provided scripts for mev.aileena.xyz. Do not use Vercel for this unless you fully understand the consequences.
6. **Add Warning Files**: Keep these DEPLOYMENT_LOCK_WARNING.md files in all deployment folders.
7. **(Optional) HTTP Auth**: For extra protection, add HTTP basic auth at the server or CDN level.

## If You Need to Update
- Double-check which domain/project you are deploying to.
- Never deploy from the root unless updating aileena.xyz.
- Never deploy from /mev unless updating mev.aileena.xyz.
- Review all scripts and configs before running.
