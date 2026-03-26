#!/bin/bash
# Run from anywhere — resolve project root relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "--- ShowTrackr-Web Launcher (Linux/macOS) ---"
echo ""

VENV_PYTHON=".venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment not found." >&2
    echo "Please run scripts/setup.sh first to set up the project." >&2
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

export FLASK_APP="apps/desktop/src/core"

echo "Starting ShowTrackr-Web..."
"$VENV_PYTHON" scripts/run.py

echo ""
echo "Application stopped."
read -p "Press Enter to close terminal..."
exit 0
