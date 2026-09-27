@echo off
title PhishGuard SOC: Launcher
echo ======================================================================
echo           PHISHGUARD SOC: AI EMAIL RISK & FORENSIC PLATFORM
echo ======================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

:: 2. Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

:: 3. Setup Backend Virtualenv
cd /d "%~dp0backend"
if not exist "venv" (
    echo [*] Creating Python virtual environment in backend/venv...
    python -m venv venv
)

echo [*] Checking backend Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

:: 4. Setup Frontend Node Modules
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo [*] Installing frontend npm dependencies...
    call npm install --silent
)

:: 5. Launch Backend in new window
cd /d "%~dp0backend"
echo [*] Starting FastAPI Backend on http://127.0.0.1:8001...
start "PhishGuard Backend (FastAPI)" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"

:: 6. Launch Frontend in new window
cd /d "%~dp0frontend"
echo [*] Starting Vite Frontend on http://127.0.0.1:5174...
start "PhishGuard Frontend (Vite)" cmd /k "npm run dev"

echo.
echo ======================================================================
echo SYSTEM LAUNCHED SUCCESSFULLY!
echo.
echo - Frontend Cyber-SOC UI:  http://127.0.0.1:5174/
echo - Backend API & Docs:     http://127.0.0.1:8001/docs
echo - Backend Health:         http://127.0.0.1:8001/api/health
echo ======================================================================
echo.
pause
