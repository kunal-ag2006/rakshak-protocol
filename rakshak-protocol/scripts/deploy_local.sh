#!/usr/bin/env bash
# ==============================================================================
#  Rakshak Protocol - Local Deployment & Launch Script
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "======================================================================"
echo "  🚀 Starting Rakshak Protocol Local Deployment (FastAPI + Dashboard)"
echo "======================================================================"

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "[1/3] Running Unit Tests..."
python3 -m unittest discover tests

echo "[2/3] Starting Command & Dispatch Server on http://127.0.0.1:8000 ..."
echo "      Dashboard will be accessible at: http://127.0.0.1:8000"
echo "      API Docs will be accessible at:      http://127.0.0.1:8000/docs"
echo "----------------------------------------------------------------------"
exec python3 -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload
