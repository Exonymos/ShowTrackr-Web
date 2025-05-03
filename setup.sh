#!/bin/bash

echo "--- ShowTrackr Setup Launcher (Linux/macOS) ---"

# Check for Python 3
echo "Checking for Python 3.10+..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 command could not be found. Please install Python 3.10 or newer." >&2
    exit 1
fi

python3 -c 'import sys; exit(1) if sys.version_info < (3,10) else exit(0)' || { echo "ERROR: Python 3.10+ required." >&2; exit 1; }
echo "Python 3 found. Proceeding with setup script..."
echo ""

# Run the Python setup script
python3 setup.py

# Capture the exit code from setup.py
SETUP_EXIT_CODE=$?

echo ""
echo "Setup script finished."
read -p "Press Enter to exit..." # Keep window open
exit $SETUP_EXIT_CODE