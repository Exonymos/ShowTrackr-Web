# setup.py
import sys
import os
import platform
import secrets
import subprocess
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
    console.print(
        f"Checking Python Version ({'.'.join(map(str, PYTHON_MIN_VERSION))}+ required)..."
    )
    if sys.version_info < PYTHON_MIN_VERSION:
        console_stderr.print(
            f"ERROR: Python version {sys.version.split()[0]} is too old.",
            style="bold red",
        )
        console_stderr.print(
            f"Please install Python {'.'.join(map(str, PYTHON_MIN_VERSION))} or newer.",
            style="yellow",
        )
        return False
    console.print(f"Python version {sys.version.split()[0]} found. OK.")
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
        console.print(f"Running: {' '.join(command_str)}")
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
            console.print(result.stdout)
        if result.stderr and check:
            console_stderr.print(result.stderr)
        return True, result
    except FileNotFoundError:
        console_stderr.print(
            f"ERROR: Command not found: {command[0]}",
            style="bold red",
        )
        console_stderr.print(
            "Please ensure the required program is installed and in your PATH.",
            style="yellow",
        )
        return False, None
    except subprocess.CalledProcessError as e:
        console_stderr.print(
            f"ERROR: {msg_on_fail}",
            style="bold red",
        )
        if e.stdout:
            console_stderr.print(e.stdout, style="red")
        if e.stderr:
            console_stderr.print(e.stderr, style="red")
        return False, e
    except Exception as e:
        console_stderr.print(f"ERROR: {msg_on_fail} ({e})", style="bold red")
        return False, e


def check_npm():
    """Checks if npm is installed and available."""
    console.print("Checking for Node.js/npm...")
    success, _ = run_command(
        ["npm", "--version"], capture=True, check=False
    )  # Don't exit if npm not found
    if success:
        console.print("Node.js/npm found.")
        return True
    else:
        console_stderr.print("WARNING: npm (Node.js) not found or command failed.")
        console_stderr.print(
            "If you plan to modify CSS/JS, install Node.js from nodejs.org."
        )
        console_stderr.print("Skipping npm-related steps.")
        return False


def run_with_progress(description, func, *args, **kwargs):
    """Run a function with a Rich progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=None)
        try:
            result = func(*args, **kwargs)
            progress.update(task, description=f"{description} [green]done![/green]")
            progress.stop_task(task)
            return result
        except Exception as e:
            progress.stop_task(task)
            raise


def ensure_rich():
    try:
        from rich.console import Console

        return True
    except ImportError:
        print(
            "[!] 'rich' not found. Attempting to install rich into the virtual environment..."
        )
        # Find the rich version from requirements.txt
        import re

        rich_version = None
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                for line in f:
                    m = re.match(r"rich([<>=!~]+[\d\w\.]*)?", line.strip())
                    if m:
                        rich_version = line.strip()
                        break
        except Exception:
            # Exception ignored intentionally: fallback to plain output if rich version detection fails
            pass
        # Determine venv pip path
        venv_dir = Path(__file__).parent / ".venv"
        if platform.system() == "Windows":
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = venv_dir / "bin" / "pip"
        # If venv pip doesn't exist, fallback to system pip
        pip_cmd = (
            [str(pip_path)] if pip_path.exists() else [sys.executable, "-m", "pip"]
        )
        pip_cmd += ["install"]
        if rich_version:
            pip_cmd.append(rich_version)
        else:
            pip_cmd.append("rich")
        try:
            subprocess.check_call(pip_cmd)
            from rich.console import Console

            return True
        except Exception as e:
            print(
                f"[!] Failed to install 'rich'. Setup will continue with plain output. Error: {e}"
            )
            return False


if not ensure_rich():
    # Fallback: define dummy console objects that use print
    class DummyConsole:
        def print(self, *args, **kwargs):
            print(*args)

        def rule(self, *args, **kwargs):
            print("-" * 60)

        def print_exception(self, *args, **kwargs):
            import traceback

            traceback.print_exc()

    console = DummyConsole()
    console_stderr = DummyConsole()
    logger = None
else:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )
    from rich.traceback import install as rich_traceback_install
    from rich.logging import RichHandler
    import logging

    console = Console()
    console_stderr = Console(stderr=True)
    rich_traceback_install(show_locals=True, suppress=[])
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True, show_time=True, show_level=True, show_path=False
            )
        ],
    )
    logger = logging.getLogger("rich")


# --- Main Setup Logic ---
def main():
    import time

    start_time = time.perf_counter()
    console.rule("[bold cyan]ShowTrackr Setup")
    console.print("[bold]Starting ShowTrackr Setup...[/bold]")
    os.chdir(PROJECT_ROOT)

    if not check_python_version():
        return False

    # 1. Setup Virtual Environment
    console.print("\n[bold]Setting up Virtual Environment...[/bold]")
    if VENV_DIR.exists() and (VENV_DIR / "pyvenv.cfg").exists():
        console.print(
            f"[yellow]Virtual environment already exists at: {VENV_DIR}[/yellow]"
        )
    else:

        def create_venv():
            import venv

            venv.create(VENV_DIR, with_pip=True)

        try:
            run_with_progress("Creating virtual environment", create_venv)
            console.print("[green]Virtual environment created successfully.[/green]")
        except Exception as e:
            console_stderr.print(
                f"[bold red]ERROR: Failed to create virtual environment: {e}[/bold red]"
            )
            return False

    python_exe, pip_exe, flask_exe = get_venv_paths()
    if not python_exe.exists() or not pip_exe.exists():
        console_stderr.print(
            f"[bold red]ERROR: Could not find python/pip executables in {VENV_DIR}.[/bold red]"
        )
        console_stderr.print(
            "[yellow]Try deleting the .venv folder and running setup again.[/yellow]"
        )
        return False
    console.print("[green]Virtual environment paths located.[/green]")

    # 2. Install Python Dependencies
    console.print("\n[bold]Installing Python Dependencies...[/bold]")
    if not REQUIREMENTS_FILE.exists():
        console_stderr.print(
            f"[bold red]ERROR: {REQUIREMENTS_FILE} not found![/bold red]"
        )
        return False

    def pip_install():
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True
        )

    try:
        run_with_progress("Installing Python dependencies", pip_install)
        console.print("[green]Python dependencies installed successfully.[/green]")
    except Exception as e:
        console_stderr.print(
            f"[bold red]Failed to install Python dependencies: {e}[/bold red]"
        )
        return False

    # 3. Install Node Dependencies & Build Assets
    console.print("\n[bold]Setting up Frontend Assets (Node.js/npm)...[/bold]")
    npm_available = check_npm()
    if PACKAGE_JSON_FILE.exists() and npm_available:

        def npm_install():
            subprocess.run(["npm", "install"], check=True)

        try:
            run_with_progress("Installing npm packages", npm_install)
            console.print(
                "[green]Node.js/npm dependencies installed successfully.[/green]"
            )
        except Exception as e:
            console_stderr.print(f"[yellow]WARNING: npm install failed: {e}[/yellow]")
    elif PACKAGE_JSON_FILE.exists():
        console_stderr.print("[yellow]npm not found. Skipping Node.js steps.[/yellow]")
    else:
        console.print(
            "[yellow]package.json not found. Skipping Node steps (assuming CDN or no build needed).[/yellow]"
        )

    # 4. Setup Configuration (.env)
    console.print("\n[bold]Setting up Configuration...[/bold]")
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]Created data directory: {DATA_DIR}[/green]")
    if ENV_FILE.exists():
        console.print(f"[yellow].env file already exists at: {ENV_FILE}[/yellow]")
    else:
        secret_key = secrets.token_hex(24)
        env_content = f"""# Flask Secret Key (Required)
SECRET_KEY='{secret_key}'
FLASK_APP=src/watchlist
# Set to False for production
FLASK_DEBUG=True
DATABASE_URL=sqlite:///../data/database.db
GOOGLE_APPS_SCRIPT_FEEDBACK_URL='https://script.google.com/macros/s/AKfycbwgakVifq4XkMRUMYvcRuR3083z6tn4cmjx7kwQCn5zNBwGJxEObKf5zGTI5an0A2rwvQ/exec'
GOOGLE_SHEET_PUBLIC_URL='https://docs.google.com/spreadsheets/d/1OW1PQTpdOcJK3bWLHsjkNuHZBkXp_RpLMel4IlDMrLg'
"""
        try:
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write(env_content)
            console.print(f"[green]Created .env file at: {ENV_FILE}[/green]")
        except IOError as e:
            console_stderr.print(
                f"[bold red]ERROR: Failed to create .env file: {e}[/bold red]"
            )
            return False

    # 5. Setup Database
    console.print("\n[bold]Setting up Database...[/bold]")
    flask_env = os.environ.copy()
    flask_env["FLASK_APP"] = "src/watchlist"
    migrations_dir = PROJECT_ROOT / "migrations"

    # Ensure migrations folder exists, or initialize it
    if not migrations_dir.exists():
        console_stderr.print(
            f"[yellow]Migrations folder not found at: {migrations_dir}[/yellow]"
        )
        console_stderr.print(
            "[yellow]Initializing migrations folder with 'flask db init'...[/yellow]"
        )
        try:
            subprocess.run([str(flask_exe), "db", "init"], check=True, env=flask_env)
            console.print(
                f"[green]Migrations folder created at: {migrations_dir}[/green]"
            )
        except Exception as e:
            console_stderr.print(
                f"[bold red]ERROR: Could not initialize migrations folder: {e}[/bold red]"
            )
            return False
        # After initializing, create the initial migration
        console_stderr.print(
            "[yellow]Creating initial migration with 'flask db migrate'...[/yellow]"
        )
        try:
            subprocess.run(
                [str(flask_exe), "db", "migrate", "-m", "Initial migration"],
                check=True,
                env=flask_env,
            )
            console.print("[green]Initial migration created.[/green]")
        except Exception as e:
            console_stderr.print(
                f"[bold red]ERROR: Could not create initial migration: {e}[/bold red]"
            )
            return False

    def db_upgrade():
        subprocess.run([flask_exe, "db", "upgrade"], check=True, env=flask_env)

    try:
        run_with_progress("Applying database migrations", db_upgrade)
        console.print("[green]Database setup/checked successfully.[/green]")
    except Exception as e:
        console_stderr.print(f"[bold red]Database migration failed: {e}[/bold red]")
        return False

    elapsed = time.perf_counter() - start_time
    mins, secs = divmod(int(elapsed), 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
    console.rule(f"[bold green]Setup Complete in {time_str}![/bold green]")
    console.print(
        f"[bold green]You can now run the application using run.bat or ./run.sh[/bold green]"
    )
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        if "console" in globals():
            console.print_exception()
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
