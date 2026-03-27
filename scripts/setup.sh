#!/bin/bash
# Run from anywhere — resolve project root relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "--- SeriesScape Setup (Linux/macOS) ---"
echo ""

# --- 1. Check Python ---
echo "Checking for Python 3.10+..."
if ! command -v python3 &>/dev/null; then
    echo -e "\033[1;31mERROR: python3 not found. Install Python 3.10+ from https://python.org\033[0m" >&2
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_OK=$(python3 -c 'import sys; print("yes" if sys.version_info >= (3,10) else "no")')
if [ "$PY_OK" != "yes" ]; then
    echo -e "\033[1;31mERROR: Python 3.10+ required. Found $PY_VER\033[0m" >&2
    exit 1
fi
echo "Python $PY_VER found."
echo ""
# --- 2. Check / install uv ---
echo "Checking for uv..."
if ! command -v uv &>/dev/null; then
    echo "uv not found. Installing via pip..."
    python3 -m pip install uv --quiet
    if ! command -v uv &>/dev/null; then
        echo -e "\033[1;31mERROR: uv still not found after install attempt.\033[0m" >&2
        echo "Install manually: https://docs.astral.sh/uv/getting-started/installation/" >&2
        exit 1
    fi
    echo "uv installed successfully."
else
    echo "uv found."
fi
echo ""

# --- 3. Install all dependencies via uv sync ---
echo "Installing dependencies with uv sync..."
if ! uv sync; then
    echo -e "\033[1;31mERROR: uv sync failed. Check the output above.\033[0m" >&2
    exit 1
fi
echo "Dependencies installed successfully."
echo ""
# --- 4. Run Python setup script inside the venv ---
echo "Running SeriesScape setup script..."
.venv/bin/python scripts/setup.py
SETUP_EXIT_CODE=$?

echo ""
if [ $SETUP_EXIT_CODE -eq 0 ]; then
    echo -e "\033[1;32mSetup completed successfully.\033[0m"
    echo "Run the app with: scripts/run.sh"
else
    echo -e "\033[1;31mSetup failed. Check the messages above.\033[0m" >&2
fi
echo ""
read -p "Press Enter to exit..."
exit $SETUP_EXIT_CODE
