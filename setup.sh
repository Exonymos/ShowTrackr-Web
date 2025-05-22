#!/bin/bash

echo "--- ShowTrackr Setup Launcher (Linux/macOS) ---"

# Check for Python 3.10+
echo "Checking for Python 3.10+..."
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31mERROR: python3 command could not be found. Please install Python 3.10 or newer.\033[0m" >&2
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info[0], sys.version_info[1]))')
if [[ $(echo -e "$PYTHON_VERSION < 3.10" | awk '{if ($1 < $3) print "yes"; else print "no"}') == "yes" ]]; then
    echo -e "\033[1;31mERROR: Python 3.10+ required. Found $PYTHON_VERSION.\033[0m" >&2
    exit 1
fi
echo "Python $PYTHON_VERSION found."

# Check for pip
echo "Checking for pip..."
if ! python3 -m pip --version &> /dev/null; then
    echo -e "\033[1;33mWARNING: pip not found for Python 3.\033[0m\n"
    echo "Attempting to install pip..."
    if ! python3 -m ensurepip --upgrade &> /dev/null; then
        echo -e "\033[1;31mERROR: Failed to install pip. Please install it manually.\033[0m" >&2
        exit 1
    fi
    # Re-check pip after install
    if ! python3 -m pip --version &> /dev/null; then
        echo -e "\033[1;31mERROR: pip still not found after installation attempt.\033[0m" >&2
        exit 1
    fi
fi

echo "All Python prerequisites found."

# Run the Python setup script
python3 setup.py
SETUP_EXIT_CODE=$?

if [ $SETUP_EXIT_CODE -eq 0 ]; then
    echo -e "\033[1;32mPython setup script completed successfully.\033[0m"
    echo "To activate the virtual environment, run: source .venv/bin/activate"
    echo "Then run the application using: ./run.sh"
else
    echo -e "\033[1;31mPython setup script failed. Please check the error messages above.\033[0m" >&2
fi

echo ""
read -p "Press Enter to exit..."
exit $SETUP_EXIT_CODE