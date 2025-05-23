@echo off
setlocal
set SETUP_EXIT_CODE=1

echo.
echo --- ShowTrackr Setup Launcher (Windows) ---

echo Checking for Python 3.10+...
python --version > nul 2>&1
if errorlevel 1 (
echo ERROR: Python not found in PATH.
echo Please install Python 3.10 or newer from python.org
echo and ensure it's added to your PATH during installation.
echo Setup cannot continue.
goto :finally
)

echo Checking for pip...
python -m pip --version > nul 2>&1
if errorlevel 1 (
  echo WARNING: pip not found for Python.
  echo Attempting to install pip...
  python -m ensurepip --upgrade > nul 2>&1
  if errorlevel 1 (
    echo ERROR: Failed to install pip. Please install it manually.
    goto :finally
  )
  REM Re-check pip after installation
  python -m pip --version > nul 2>&1
  if errorlevel 1 (
    echo ERROR: pip still not found after installation attempt.
    goto :finally
  )
)

echo All Python prerequisites found.

REM Run the Python setup script
python setup.py

set SETUP_EXIT_CODE=%errorlevel%

:finally
echo.
if %SETUP_EXIT_CODE%==0 (
echo Python setup script completed successfully.
echo To activate the virtual environment, run: .\.venv\Scripts\activate
echo Then run the application using: .\run.bat
) else (
echo Python setup script failed. Please check the error messages above.
)
echo.
echo Press any key to exit...
pause > nul
exit /b %SETUP_EXIT_CODE%
endlocal