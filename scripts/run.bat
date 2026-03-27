@echo off
setlocal
REM Run from anywhere - resolve project root relative to this script's location
cd /d "%~dp0.."

echo.
echo --- SeriesScape Launcher (Windows) ---
echo.

REM Use the venv Python directly - no manual activation needed
set VENV_PYTHON=.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment not found.
    echo Please run scripts\setup.bat first to set up the project.
    echo.
    pause
    exit /b 1
)

set FLASK_APP=apps/desktop/src/core

echo Starting SeriesScape...
"%VENV_PYTHON%" scripts\run.py

echo.
echo Application stopped.
pause
endlocal
