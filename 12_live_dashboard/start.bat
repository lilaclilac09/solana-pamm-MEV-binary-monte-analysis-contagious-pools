@echo off
REM Quick Start Script for Solana MEV Dashboard (Windows)
REM This script sets up and runs the dashboard locally

echo.
echo ========================================
echo   Solana MEV Dashboard - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo Dependencies installed
echo.

REM Check if .env exists
if not exist ".env" (
    echo Setting up environment variables...
    copy .env.template .env
    echo Created .env file from template
    echo Please edit .env and add your API keys before enabling live data
) else (
    echo Environment file (.env) already exists
)

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo Starting dashboard...
echo Access at: http://127.0.0.1:8050
echo.
echo Press Ctrl+C to stop the server
echo ----------------------------------------
echo.

REM Run the dashboard
python mev_dashboard.py
