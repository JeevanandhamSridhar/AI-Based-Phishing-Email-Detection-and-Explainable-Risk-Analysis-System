#!/usr/bin/env bash
# PhishGuard SOC: Linux / macOS 1-Click Launcher

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "======================================================================"
echo "          PHISHGUARD SOC: AI EMAIL RISK & FORENSIC PLATFORM"
echo "======================================================================"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH. Please install Python 3.10+."
    exit 1
fi

# 2. Check Node
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm is not installed or not in PATH. Please install Node.js 18+."
    exit 1
fi

# 3. Setup Backend Virtualenv
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    echo "[*] Creating Python virtual environment in backend/venv..."
    python3 -m venv venv
fi

echo "[*] Checking backend Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

# 4. Setup Frontend Node Modules
cd "$DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "[*] Installing frontend npm dependencies..."
    npm install --silent
fi

echo ""
echo "======================================================================"
echo "STARTING SERVICES"
echo "======================================================================"
echo "- Frontend Cyber-SOC UI:  http://127.0.0.1:5174/"
echo "- Backend API & Docs:     http://127.0.0.1:8001/docs"
echo "- Backend Health:         http://127.0.0.1:8001/api/health"
echo "======================================================================"
echo ""

# Start backend in background
cd "$DIR/backend"
source venv/bin/activate
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
BACKEND_PID=$!

# Start frontend
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
