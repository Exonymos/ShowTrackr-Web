#!/bin/bash

echo "Activating virtual environment (.venv)..."
source ./.venv/bin/activate || {
    echo "ERROR: Failed to activate virtual environment in .venv. Ensure it exists and is set up correctly." >&2
    exit 1
}

echo "Setting environment variable..."
export FLASK_APP=src/watchlist

echo "Starting Flask application..."
python run.py

echo ""
echo "Application stopped."
read -p "Press Enter to close terminal..."
exit 0