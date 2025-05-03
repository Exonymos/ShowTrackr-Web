@echo off
setlocal

echo --- ShowTrackr Setup Launcher (Windows) ---

REM Check for Python
echo Checking for Python 3.10+...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH. 
    echo Please install Python 3.10 or newer from python.org 
    echo and ensure it's added to your PATH during installation.
    echo Setup cannot continue.
    goto :finally
)
echo Python found. Proceeding with setup script...
echo(

REM Run the Python setup script
python setup.py

REM Capture the exit code from setup.py
set SETUP_EXIT_CODE=%errorlevel%

:finally
echo(
echo Setup script finished. Press any key to exit.
pause > nul
exit /b %SETUP_EXIT_CODE%

endlocal