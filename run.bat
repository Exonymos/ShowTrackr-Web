@echo off
echo Activating virtual environment...
call .\.venv\Scripts\activate || (
    echo ERROR: Failed to activate virtual environment in .venv. Ensure it exists and is set up correctly.
    pause
    exit /b 1
)

echo Setting environment variables...
set FLASK_APP=src/watchlist

echo Starting Flask application...
python run.py

echo Application stopped.
pause