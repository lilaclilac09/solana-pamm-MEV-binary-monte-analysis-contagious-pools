#!/bin/bash
# Deployment: index.html + assets to mev.aileena.xyz

set -e

PROJECT_PATH="$(pwd)"
DEPLOY_USER="root"
DEPLOY_HOST="mev.aileena.xyz"
DEPLOY_PATH="/var/www/html"

echo ""
echo "🚀 DEPLOYING MEV THREAT INTELLIGENCE DASHBOARD"
echo "============================================================"
echo ""

# Verify files
echo "📋 Verifying files..."
[[ -f "$PROJECT_PATH/index.html" ]] || { echo "❌ index.html not found"; exit 1; }
[[ -d "$PROJECT_PATH/app/assets" ]] || { echo "❌ app/assets not found"; exit 1; }

echo "✅ index.html ready"
echo "✅ 3 PNG visualizations ready:"
ls -lh "$PROJECT_PATH/app/assets/"*.png | awk '{print "   • " $9 " (" $5 ")"}'
echo ""

# Upload
echo "📤 Uploading to mev.aileena.xyz..."
scp "$PROJECT_PATH/index.html" "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"
scp -r "$PROJECT_PATH/app/assets" "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"
echo "✅ Files uploaded"
echo ""

# Verify
echo "🔍 Verifying on remote server..."
ssh "$DEPLOY_USER@$DEPLOY_HOST" ls -lh "$DEPLOY_PATH/index.html"
echo ""

# Done
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🌐 Live at: https://mev.aileena.xyz/index.html"
echo ""
echo "📊 Content:"
echo "   • Executive Summary"
echo "   • TOP STORIES (4 real-world attacks)"
echo "   • Threat Intelligence Visualizations (3 PNG charts)"
echo "   • Threat Analysis & Risk Assessment"
echo "   • Key Insights & Recommendations"
echo ""
