#!/bin/bash
# Auto-Deploy MEV Dashboard to mev.aileen.xyz via Vercel
# Run: ./quick_deploy.sh

echo "🚀 MEV Dashboard - Quick Deploy to mev.aileen.xyz"
echo "=================================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
    echo ""
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found! Install Node.js from https://nodejs.org"
    exit 1
fi

echo "🔐 Step 1: Login to Vercel (opens browser)"
vercel login

echo ""
echo "📤 Step 2: Deploying to production..."
vercel --prod

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the deployment URL above (something like mev-dashboard-xxxx.vercel.app)"
echo "2. Go to: https://vercel.com/dashboard"
echo "3. Select your project → Settings → Domains"
echo "4. Add domain: mev.aileen.xyz"
echo "5. Update DNS at your domain host:"
echo "   Type: CNAME"
echo "   Name: mev"
echo "   Value: cname.vercel.com"
echo ""
echo "⏱️  Wait 5-15 minutes for DNS to propagate"
echo "🌐 Then visit: https://mev.aileen.xyz"
echo ""
