# run.py
import os
import subprocess
import sys
from pathlib import Path
import platform

# Ensure the script is running from the project root directory
project_root = Path(__file__).parent.resolve()
os.chdir(project_root)

# --- Virtual Environment Check (More Robust) ---
# Check if the Python executable being used is from the expected venv path
expected_venv_path = project_root / ".venv"
is_windows = platform.system() == "Windows"

# Construct expected executable path based on OS
if is_windows:
    expected_executable = expected_venv_path / "Scripts" / "python.exe"
else:
    expected_executable = expected_venv_path / "bin" / "python"

# Resolve paths to handle potential symlinks etc.
try:
    current_executable = Path(sys.executable).resolve()
    expected_executable = expected_executable.resolve()
except OSError:
    # Handle potential errors during path resolution if venv doesn't exist fully
    current_executable = Path(sys.executable)


if current_executable != expected_executable:
    print("--- WARNING ---")
    print("It looks like the virtual environment (.venv) is not activated,")
    print("or you are running this script with a different Python interpreter.")
    print(f"Expected venv: {expected_venv_path}")
    print(f"Current Python: {sys.executable}")
    print("\nPlease activate the environment first:")
    if is_windows:
        print(f"> .\\.venv\\Scripts\\activate")
        print("Or run setup.bat / run.bat")
    else:
        print(f"$ source ./.venv/bin/activate")
        print("Or run setup.sh / run.sh")
    print("------------")
    # Decide whether to exit or continue
    # sys.exit("Exiting due to inactive venv.")
    print("Continuing, but dependency issues or unexpected behavior may occur.")
    print("------------")


print("Ensuring database migrations are up-to-date...")
try:
    # Use sys.executable to ensure we're using the python from the (potentially) activated venv
    subprocess.run(
        [sys.executable, "-m", "flask", "db", "upgrade"],
        check=True,
        cwd=project_root,
        capture_output=True,
    )  # Capture output
    print("Database migrations checked/applied successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error running database migrations: {e}", file=sys.stderr)
    print(f"Stderr: {e.stderr.decode()}", file=sys.stderr)
    print(
        "Please check your database configuration and migration files.", file=sys.stderr
    )
    sys.exit(1)  # Exit if migrations fail
except FileNotFoundError:
    print(
        "Error: 'flask' command not found. Is Flask installed and the venv activated?",
        file=sys.stderr,
    )
    sys.exit(1)

# --- Start Development Server ---
print("Starting Flask development server...")
print("Access at: http://127.0.0.1:5000")
print("Press CTRL+C to quit.")
print("---")

try:
    # Add src to path to allow direct import
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))

    from watchlist import create_app

    app = create_app()

    # Use Flask's run command via subprocess for better integration with Flask-Migrate context
    # and standard Flask behavior, rather than app.run() directly here.
    # The run.bat/run.sh scripts will execute this python run.py script.
    # app.run() is generally for the simplest cases or when not using the cli.

    # We let run.bat/run.sh call this script, which prepares things,
    # then they can call `flask run` if preferred, or we can keep `app.run` here.
    # Keeping app.run() for simplicity as originally designed for this script.
    app.run(host="127.0.0.1", port=5000)  # debug=True is handled by .env via create_app

except ImportError as e:
    print(f"Error importing application: {e}", file=sys.stderr)
    print(
        "Ensure all dependencies are installed (`pip install -r requirements.txt`)",
        file=sys.stderr,
    )
    print("Try running the setup script (setup.bat or setup.sh).", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    # Catch potential port binding errors etc.
    print(
        f"An error occurred while trying to run the Flask application: {e}",
        file=sys.stderr,
    )
    import traceback

    traceback.print_exc()  # Print full traceback for debugging
    sys.exit(1)
