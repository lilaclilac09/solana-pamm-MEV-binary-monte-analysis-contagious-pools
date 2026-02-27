#!/bin/bash

# Quick Start Script for Solana MEV Dashboard
# This script sets up and runs the dashboard locally

set -e  # Exit on error

echo "🚀 Solana MEV Dashboard - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment variables..."
    cp .env.template .env
    echo "✅ Created .env file from template"
    echo "📝 Please edit .env and add your API keys before enabling live data"
else
    echo "✅ Environment file (.env) already exists"
fi

echo ""
echo "════════════════════════════════════════"
echo "🎉 Setup complete!"
echo "════════════════════════════════════════"
echo ""
echo "📊 Starting dashboard..."
echo "🌐 Access at: http://127.0.0.1:8050"
echo ""
echo "Press Ctrl+C to stop the server"
echo "────────────────────────────────────────"
echo ""

# Run the dashboard
python mev_dashboard.py
