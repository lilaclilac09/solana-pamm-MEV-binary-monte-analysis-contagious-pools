#!/bin/bash

# Render Deployment Quick Start Script
# Run this before deploying to Render

set -e  # Exit on error

echo "🚀 Preparing MEV Dashboard for Render Deployment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "mev_dashboard.py" ]; then
    echo "❌ Error: mev_dashboard.py not found!"
    echo "   Make sure you're in the 12_live_dashboard/ directory"
    exit 1
fi

echo "✅ Found mev_dashboard.py"

# Check for requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

echo "✅ Found requirements.txt"

# Check for Procfile
if [ ! -f "Procfile" ]; then
    echo "⚠️  Warning: Procfile not found (but not required for Render)"
fi

echo "✅ Found Procfile"

# Verify key files exist
echo ""
echo "📋 Checking configuration..."

# Check if app is properly defined
if grep -q "app = dash.Dash" mev_dashboard.py; then
    echo "✅ Dash app is defined"
else
    echo "❌ Dash app definition not found"
    exit 1
fi

if grep -q "server = app.server" mev_dashboard.py; then
    echo "✅ Server variable is defined (required for gunicorn)"
else
    echo "❌ Server variable not found (required: server = app.server)"
    exit 1
fi

if grep -q "gunicorn" requirements.txt; then
    echo "✅ Gunicorn is in requirements.txt"
else
    echo "❌ Gunicorn not found in requirements.txt"
    exit 1
fi

echo ""
echo "🔍 Testing local dependencies..."

# Test if Python can import key modules
python3 -c "
try:
    import dash
    print('✅ dash')
except ImportError:
    print('⚠️  dash not installed (will be installed on Render)')
" 2>/dev/null || echo "⚠️  dash not installed (will be installed on Render)"

python3 -c "
try:
    import flask
    print('✅ flask')
except ImportError:
    print('⚠️  flask not installed (will be installed on Render)')
" 2>/dev/null || echo "⚠️  flask not installed (will be installed on Render)"

python3 -c "
try:
    import plotly
    print('✅ plotly')
except ImportError:
    print('⚠️  plotly not installed (will be installed on Render)')
" 2>/dev/null || echo "⚠️  plotly not installed (will be installed on Render)"

echo ""
echo "📝 Git Status Check..."

if ! git status > /dev/null 2>&1; then
    echo "⚠️  Not in a git repository!"
    echo "   Initialize with: git init && git remote add origin <repo>"
    echo "   Then: git add . && git commit -m 'Initial commit'"
else
    echo "✅ Git repository found"
    
    # Check if files are staged
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Uncommitted changes detected. Commit before deploying:"
        echo ""
        git status --short
        echo ""
        echo "   Run: git add . && git commit -m 'Your message'"
    else
        echo "✅ All changes committed"
    fi
    
    # Check if remote exists
    if git remote get-url origin > /dev/null 2>&1; then
        echo "✅ Git remote configured"
    else
        echo "⚠️  No git remote found (add with: git remote add origin <URL>)"
    fi
fi

echo ""
echo "=================================================="
echo "✅ Pre-deployment checks complete!"
echo ""
echo "Next steps:"
echo "1. Commit changes: git add . && git commit -m 'message'"
echo "2. Push to GitHub: git push origin main"
echo "3. Go to https://render.com/dashboard"
echo "4. Create new Web Service"
echo "5. Use these commands:"
echo ""
echo "   Build Command:"
echo "   pip install -r 12_live_dashboard/requirements.txt"
echo ""
echo "   Start Command:"
echo "   cd 12_live_dashboard && gunicorn --bind 0.0.0.0:\$PORT --workers 2 --timeout 120 mev_dashboard:server"
echo ""
echo "6. Click Create Web Service"
echo "7. Wait 5-10 minutes for deployment"
echo "8. Access at: https://mev-dashboard.onrender.com (or your custom domain)"
echo ""
