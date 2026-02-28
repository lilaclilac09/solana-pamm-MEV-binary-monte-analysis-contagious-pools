#!/bin/bash

# Heroku Quick Setup Script for MEV Dashboard

echo "🚀 Heroku Deployment Setup for MEV Dashboard"
echo "=================================================="
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found!"
    echo ""
    echo "Install with: brew install heroku"
    echo "Or download: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI found ($(heroku --version))"
echo ""

# Check if logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Not logged in to Heroku"
    echo "Running: heroku login"
    heroku login
fi

echo "✅ Logged in to Heroku"
echo ""

# Ask for app name
read -p "Enter Heroku app name (e.g., mev-dashboard): " APP_NAME

if [ -z "$APP_NAME" ]; then
    APP_NAME="mev-dashboard"
fi

echo "📝 App name: $APP_NAME"
echo ""

# Create app
echo "🚀 Creating Heroku app: $APP_NAME"
heroku create "$APP_NAME" || echo "⚠️  App might already exist"

echo ""
echo "📦 Deploying from current directory..."
echo ""

# Deploy
git push heroku main

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app: https://$APP_NAME.herokuapp.com"
echo ""
echo "Next steps:"
echo "1. heroku open                    (Opens in browser)"
echo "2. heroku logs --tail             (View logs)"
echo "3. heroku domains:add mev.aileena.xyz  (Add custom domain)"
echo ""
