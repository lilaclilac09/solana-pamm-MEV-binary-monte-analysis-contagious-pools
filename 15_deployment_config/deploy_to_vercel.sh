#!/bin/bash

# 🚀 TOP STORIES & MEV THREAT INTELLIGENCE DEPLOYMENT SCRIPT
# Deploys Dash dashboard + visualizations to Vercel + mev.aileen.xyz

set -e

echo "🎯 MEV Threat Intelligence Deployment Pipeline"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify all files exist
echo -e "${BLUE}Step 1: Verifying deployment files...${NC}"
files_to_check=(
    "TOP_STORIES_ATTACK_CASE_STUDIES.md"
    "MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html"
    "app/index.py"
    "app/assets/token_pair_fragility.png"
    "app/assets/oracle_latency_window.png"
    "app/assets/mev_battlefield.png"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${YELLOW}⚠️${NC} Missing: $file"
    fi
done

echo ""

# Step 2: Check git status
echo -e "${BLUE}Step 2: Preparing git for deployment...${NC}"
git status --short || true

echo ""
echo -e "${YELLOW}Before proceeding, ensure:${NC}"
echo "  1. You've committed TOP STORIES content"
echo "  2. requirements.txt includes: dash, plotly, pandas"
echo "  3. vercel.json is configured for Python"
echo ""

# Step 3: Stage files for deployment
echo -e "${BLUE}Step 3: Staging files for git...${NC}"
git add TOP_STORIES_*.md TOP_STORIES_*.html MEV_THREAT_INTELLIGENCE_*.html
git add app/index.py app/assets/
git add requirements.txt vercel.json
echo -e "${GREEN}✅ Files staged${NC}"

echo ""

# Step 4: Create commit
echo -e "${BLUE}Step 4: Creating deployment commit...${NC}"
git commit -m "Deploy: TOP STORIES attack case studies + MEV threat intelligence visualizations

- Added Section 5b: TOP STORIES with 4 attack case studies
- Added Section 5c: Threat Intelligence Visualizations (3 PNG plots)
- Token Pair Fragility (38.2% PUMP/WSOL risk analysis)
- Oracle Latency Window (2.1s HumidiFi vulnerability)
- MEV Battlefield (66.8% protocol concentration)
- All visualizations at 300 DPI for publication quality" || true

echo ""

# Step 5: Push to git
echo -e "${BLUE}Step 5: Pushing to git (Vercel triggers auto-deploy)...${NC}"
read -p "Push to main branch? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo -e "${GREEN}✅ Pushed to git - Vercel deploying...${NC}"
else
    echo "Skipped git push"
fi

echo ""

# Step 6: Instructions for mev.aileen.xyz deployment
echo -e "${BLUE}Step 6: Manual deployment to mev.aileen.xyz${NC}"
echo ""
echo "Option A: SFTP Upload (if you have server access)"
echo "  scp MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html user@mev.aileen.xyz:/var/www/html/"
echo "  scp TOP_STORIES_mev_aileen.html user@mev.aileen.xyz:/var/www/html/"
echo "  scp -r app/assets/ user@mev.aileen.xyz:/var/www/html/"
echo ""

echo "Option B: AWS S3 Upload"
echo "  aws s3 cp MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html s3://your-bucket/"
echo "  aws s3 sync app/assets/ s3://your-bucket/assets/"
echo ""

echo "Option C: Vercel Static Export"
echo "  Manual: Copy to vercel/public/ folder and redeploy"
echo ""

# Step 7: Summary
echo -e "${GREEN}🎉 Deployment Summary${NC}"
echo ""
echo "✅ Dash Dashboard:"
echo "   - Section 5b: TOP STORIES (4 attack case studies)"
echo "   - Section 5c: Threat Intelligence Visualizations (3 PNG plots)"
echo "   - Sections 5b & 5c integrated with /assets/ image references"
echo ""
echo "✅ Website Assets (Ready to upload):"
echo "   - MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html (17K)"
echo "   - token_pair_fragility.png (394K)"
echo "   - oracle_latency_window.png (526K)"
echo "   - mev_battlefield.png (443K)"
echo ""
echo "📍 URLs:"
echo "   Dashboard: https://your-vercel-project.vercel.app"
echo "   Website: https://mev.aileen.xyz/MEV_THREAT_INTELLIGENCE_VISUAL_ANALYSIS.html"
echo ""
echo -e "${YELLOW}⏰ Check Vercel deployment progress:${NC}"
echo "   https://vercel.com/deployments"
echo ""
