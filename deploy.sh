#!/bin/bash
# MEV Threat Intelligence - Quick Deployment Script
# Usage: bash deploy.sh [step]
# $ bash deploy.sh local    # Test locally
# $ bash deploy.sh website  # Deploy to mev.aileena.xyz
# $ bash deploy.sh vercel   # Deploy to Vercel

set -e  # Exit on error

PROJECT_DIR="/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools"
SERVER="mev.aileena.xyz"
WEB_ROOT="/var/www/html"

echo "🚀 MEV Threat Intelligence Deployment Script"
echo "=============================================="

if [ "$1" == "local" ]; then
    echo ""
    echo "📍 STEP 1: Local Testing (Dash)"
    echo "================================"
    
    cd "$PROJECT_DIR"
    
    echo "✓ Activating environment..."
    source .venv/bin/activate
    
    echo "✓ Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo "✓ Starting Dash app on http://localhost:8050..."
    echo ""
    echo "🎯 You should see:"
    echo "   - Section 5b: TOP STORIES with 4 case studies"
    echo "   - Section 5c: 3 PNG visualizations"
    echo ""
    echo "Press Ctrl+C to stop server"
    echo "=============================================="
    
    cd app
    python index.py

elif [ "$1" == "website" ]; then
    echo ""
    echo "📍 STEP 2: Deploy Main Page to Website"
    echo "======================================="
    
    cd "$PROJECT_DIR"
    
    echo "✓ Files to deploy:"
    ls -lh index.html
    echo ""
    echo "✓ Assets to deploy:"
    ls -lh app/assets/
    echo ""
    
    echo "Copying main page to $SERVER..."
    scp index.html "$SERVER:$WEB_ROOT/"
    
    echo "Copying assets to $SERVER..."
    scp -r app/assets "$SERVER:$WEB_ROOT/"
    
    echo ""
    echo "✅ Deployment complete!"
    echo "Access at: https://$SERVER/"
    echo ""
    echo "✓ Verifying on server..."
    ssh "$SERVER" "ls -lh $WEB_ROOT/index.html && ls -lh $WEB_ROOT/assets/"

elif [ "$1" == "vercel" ]; then
    echo ""
    echo "📍 STEP 3: Deploy Dash to Vercel"
    echo "================================="
    
    cd "$PROJECT_DIR"
    
    echo "✓ Current git status:"
    git status
    
    echo ""
    echo "Adding files to git..."
    git add -A
    
    echo "Committing changes..."
    git commit -m "Deploy MEV threat intelligence: Sections 5b (TOP STORIES) + 5c (Visualizations)" || echo "No changes to commit"
    
    echo "Pushing to main (triggers Vercel auto-deploy)..."
    git push origin main
    
    echo ""
    echo "✅ Pushed to Vercel!"
    echo "Monitor deployment at: https://vercel.com/deployments"
    echo "Access dashboard at: https://your-project.vercel.app"

elif [ "$1" == "all" ]; then
    echo ""
    echo "🚀 Running all deployment steps..."
    echo ""
    
    bash "$0" local &
    read -p "Testing complete? Press Enter to continue..."
    
    bash "$0" website
    bash "$0" vercel
    
    echo ""
    echo "✅ All deployments complete!"
    echo "📊 Access your sites:"
    echo "   - Static page: https://$SERVER/"
    echo "   - Dashboard: https://your-project.vercel.app"

else
    echo "Usage: bash deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  local    - Test Dash app locally (http://localhost:8050)"
    echo "  website  - Deploy main page to $SERVER"
    echo "  vercel   - Deploy Dash app to Vercel (git push)"
    echo "  all      - Run all steps in sequence"
    echo ""
    echo "Examples:"
    echo "  $ bash deploy.sh local       # Start local testing"
    echo "  $ bash deploy.sh website     # Deploy static page"
    echo "  $ bash deploy.sh vercel      # Push to Vercel"
    echo ""
fi
