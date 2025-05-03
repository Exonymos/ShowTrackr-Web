# setup.py
import os
import subprocess
import sys
import platform
import venv
import secrets
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.resolve()
VENV_DIR = PROJECT_ROOT / ".venv"
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
PACKAGE_JSON_FILE = PROJECT_ROOT / "package.json"
ENV_FILE = DATA_DIR / ".env"
PYTHON_MIN_VERSION = (3, 10)  # Require Python 3.10+

# --- Helper Functions ---


def check_python_version():
    """Checks if the current Python version meets the minimum requirement."""
    print(
        f"--- Checking Python Version ({'.'.join(map(str, PYTHON_MIN_VERSION))}+ required)..."
    )
    if sys.version_info < PYTHON_MIN_VERSION:
        print(
            f"ERROR: Python version {sys.version.split()[0]} is too old.",
            file=sys.stderr,
        )
        print(
            f"Please install Python {'.'.join(map(str, PYTHON_MIN_VERSION))} or newer.",
            file=sys.stderr,
        )
        return False
    print(f"Python version {sys.version.split()[0]} found. OK.")
    return True


def get_venv_paths():
    """Determines the paths for executables within the virtual environment."""
    is_windows = platform.system() == "Windows"
    if is_windows:
        bin_dir = VENV_DIR / "Scripts"
        python_exe = bin_dir / "python.exe"
        pip_exe = bin_dir / "pip.exe"
        flask_exe = bin_dir / "flask.exe"
    else:
        bin_dir = VENV_DIR / "bin"
        python_exe = bin_dir / "python"
        pip_exe = bin_dir / "pip"
        flask_exe = bin_dir / "flask"
    return python_exe, pip_exe, flask_exe


def run_command(
    command,
    capture=False,
    check=True,
    cwd=PROJECT_ROOT,
    env=None,
    msg_on_fail="Command failed.",
):
    """Runs a command using subprocess, handling errors."""
    try:
        command_str = [str(part) for part in command]
        print(f"Running: {' '.join(command_str)}")
        result = subprocess.run(
            command_str,
            capture_output=capture,
            check=check,
            cwd=cwd,
            env=env,
            text=True,
            encoding="utf-8",
        )
        if capture:
            print(result.stdout)
        if result.stderr and check:
            print(result.stderr, file=sys.stderr)
        return True, result
    except FileNotFoundError:
        print(f"ERROR: Command not found: {command[0]}", file=sys.stderr)
        print(
            "Please ensure the required program is installed and in your PATH.",
            file=sys.stderr,
        )
        return False, None
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {msg_on_fail}", file=sys.stderr)
        print(f"Command: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"Return Code: {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(f"Output:\n{e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"Error Output:\n{e.stderr}", file=sys.stderr)
        return False, e
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred running command: {command}",
            file=sys.stderr,
        )
        print(e, file=sys.stderr)
        return False, e


def check_npm():
    """Checks if npm is installed and available."""
    print("--- Checking for Node.js/npm...")
    success, _ = run_command(
        ["npm", "--version"], capture=True, check=False
    )  # Don't exit if npm not found
    if success:
        print("Node.js/npm found.")
        return True
    else:
        print("WARNING: npm (Node.js) not found or command failed.")
        print("If you plan to modify CSS/JS, install Node.js from nodejs.org.")
        print("Skipping npm-related steps.")
        return False


# --- Main Setup Logic ---
def main():
    print("--- Starting ShowTrackr Setup ---")
    os.chdir(PROJECT_ROOT)  # Ensure we are in the correct directory

    if not check_python_version():
        return False  # Stop if Python version is too low

    # 1. Setup Virtual Environment
    print("\n--- Setting up Virtual Environment ---")
    if VENV_DIR.exists() and (VENV_DIR / "pyvenv.cfg").exists():
        print(f"Virtual environment already exists at: {VENV_DIR}")
    else:
        print(f"Creating virtual environment at: {VENV_DIR}...")
        try:
            venv.create(VENV_DIR, with_pip=True)
            print("Virtual environment created successfully.")
        except Exception as e:
            print(f"ERROR: Failed to create virtual environment: {e}", file=sys.stderr)
            return False

    # Get paths within the venv
    python_exe, pip_exe, flask_exe = get_venv_paths()

    # Verify executables exist
    if not python_exe.exists() or not pip_exe.exists():
        print(
            f"ERROR: Could not find python/pip executables in {VENV_DIR}.",
            file=sys.stderr,
        )
        print(
            "Virtual environment might be corrupted. Try deleting the .venv folder and running setup again.",
            file=sys.stderr,
        )
        return False
    print("Virtual environment paths located.")

    # 2. Install Python Dependencies
    print("\n--- Installing Python Dependencies ---")
    if not REQUIREMENTS_FILE.exists():
        print(f"ERROR: {REQUIREMENTS_FILE} not found!", file=sys.stderr)
        return False

    success, _ = run_command(
        [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE],
        msg_on_fail="Failed to install Python dependencies.",
    )
    if not success:
        return False
    print("Python dependencies installed successfully.")

    # 3. Install Node Dependencies & Build Assets
    print("\n--- Setting up Frontend Assets (Node.js/npm) ---")
    npm_available = check_npm()
    if PACKAGE_JSON_FILE.exists():
        if npm_available:
            # Install Node dependencies
            success, _ = run_command(
                ["npm", "install"], msg_on_fail="npm install failed."
            )
            if not success:
                return False
            print("Node dependencies installed successfully.")

            # Build assets
            print("Building frontend assets (CSS/JS)...")
            success, _ = run_command(
                ["npm", "run", "build:css"], msg_on_fail="npm run build:css failed."
            )
            if not success:
                return False
            print("Frontend assets built successfully.")
        else:
            print("package.json found, but npm not available. Skipping Node steps.")
            print("App might not display correctly without built assets.")
    else:
        print(
            "package.json not found. Skipping Node steps (assuming CDN or no build needed)."
        )

    # 4. Setup Configuration (.env)
    print("\n--- Setting up Configuration ---")
    if not DATA_DIR.exists():
        print(f"Creating data directory: {DATA_DIR}")
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if ENV_FILE.exists():
        print(f".env file already exists at: {ENV_FILE}")
    else:
        print(f"Creating .env file at: {ENV_FILE}")
        secret_key = secrets.token_hex(24)
        env_content = f"""# Flask Secret Key (Required)
SECRET_KEY='{secret_key}'

# Flask App Configuration
FLASK_APP=src/watchlist

# Flask Debug Mode (Set to False for production!)
FLASK_DEBUG=True

# Database URL
DATABASE_URL=sqlite:///../data/database.db
"""
        try:
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write(env_content)
            print("Generated .env file with a new SECRET_KEY.")
        except IOError as e:
            print(f"ERROR: Could not write .env file: {e}", file=sys.stderr)
            return False

    # 5. Setup Database
    print("\n--- Setting up Database ---")
    # Ensure Flask uses the correct app context by setting env var for the subprocess
    flask_env = os.environ.copy()
    flask_env["FLASK_APP"] = "src/watchlist"
    # Get the path to the flask executable within the venv
    python_exe, pip_exe, flask_exe = get_venv_paths()
    migrations_dir = PROJECT_ROOT / "migrations"

    print("Attempting database upgrade...")
    success, result = run_command(
        [flask_exe, "db", "upgrade"],
        capture=True,
        check=False,
        env=flask_env,
        msg_on_fail="flask db upgrade command failed.",
    )

    # If upgrade failed (likely because migrations folder doesn't exist yet)
    if not success or (result and result.returncode != 0):
        print("Database upgrade failed or no migrations found (might be first run).")
        print("Attempting flask db init...")

        # Check if migrations folder exists. If so, something else is wrong with upgrade.
        if (PROJECT_ROOT / "migrations").exists():
            print(
                "ERROR: 'migrations' folder exists, but 'flask db upgrade' failed.",
                file=sys.stderr,
            )
            print("Check previous error messages or database state.", file=sys.stderr)
            return False

        # Run flask db init
        success_init, _ = run_command(
            [flask_exe, "db", "init"],
            env=flask_env,
            msg_on_fail="flask db init failed.",
        )
        if not success_init:
            return False

        # Create an initial migration for the database
        print("Creating initial database migration...")
        success_migrate, _ = run_command(
            [flask_exe, "db", "migrate", "-m", "Initial migration"],
            env=flask_env,
            msg_on_fail="flask db migrate failed.",
        )
        if not success_migrate:
            return False

        # Try upgrade again now that init and migrate are done
        print("Attempting database upgrade again...")
        success_upgrade_again, _ = run_command(
            [flask_exe, "db", "upgrade"],
            env=flask_env,
            msg_on_fail="flask db upgrade failed after init/stamp.",
        )
        if not success_upgrade_again:
            return False

    print("Database setup/checked successfully.")

    print("\n--- Setup Complete! ---")
    print("You can now run the application using run.bat or ./run.sh")
    return True


if __name__ == "__main__":
    if main():
        sys.exit(0)  # Success
    else:
        print("\n--- Setup Failed! ---", file=sys.stderr)
        sys.exit(1)  # Failure
