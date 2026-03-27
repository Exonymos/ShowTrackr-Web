@echo off
setlocal
REM Run from anywhere — resolve project root relative to this script's location
cd /d "%~dp0.."

set SETUP_EXIT_CODE=1

echo.
echo --- SeriesScape Setup (Windows) ---
echo.

REM --- 1. Check Python ---
echo Checking for Python 3.10+...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo Please install Python 3.10 or newer from https://python.org
    echo and make sure "Add Python to PATH" is checked during installation.
    goto :finally
)
echo Python found.

REM --- 2. Check / install uv ---
echo Checking for uv...
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found. Installing uv via pip...
    python -m pip install uv --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install uv. Please install it manually:
        echo   https://docs.astral.sh/uv/getting-started/installation/
        goto :finally
    )
    uv --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: uv still not found after install attempt.
        echo Try restarting this terminal and running setup again.
        goto :finally
    )
    echo uv installed successfully.
) else (
    echo uv found.
)

REM --- 3. Install all dependencies via uv sync ---
echo.
echo Installing dependencies with uv sync...
uv sync
if errorlevel 1 (
    echo ERROR: uv sync failed. Check the output above for details.
    goto :finally
)
echo Dependencies installed successfully.

REM --- 4. Run the Python setup script inside the venv ---
echo.
echo Running SeriesScape setup script...
.venv\Scripts\python.exe scripts\setup.py
set SETUP_EXIT_CODE=%errorlevel%

:finally
echo.
if %SETUP_EXIT_CODE%==0 (
    echo Setup completed successfully.
    echo Run the app with: scripts\run.bat
) else (
    echo Setup failed. Please check the error messages above.
)
echo.
echo Press any key to exit...
pause >nul
endlocal
exit /b %SETUP_EXIT_CODE%
