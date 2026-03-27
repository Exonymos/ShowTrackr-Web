# scripts/setup.py
# Run by setup.bat / setup.sh AFTER `uv sync` has already created the venv.
# This script handles only: .env creation and database initialisation.
import sys
import os
import platform
import secrets
import subprocess
from pathlib import Path

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

# --- Configuration ---
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent  # SeriesScape/
DESKTOP_APP_ROOT = PROJECT_ROOT / "apps" / "desktop"  # apps/desktop/
DATA_DIR = DESKTOP_APP_ROOT / "data"  # apps/desktop/data/
MIGRATIONS_DIR = DESKTOP_APP_ROOT / "migrations"  # apps/desktop/migrations/
PACKAGE_JSON_FILE = PROJECT_ROOT / "package.json"
ENV_FILE = DATA_DIR / ".env"  # gitignored, generated on setup
PYTHON_MIN_VERSION = (3, 10)

_is_windows = platform.system() == "Windows"
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = (
    VENV_DIR / "Scripts" / "python.exe"
    if _is_windows
    else VENV_DIR / "bin" / "python"
)
VENV_FLASK = (
    VENV_DIR / "Scripts" / "flask.exe"
    if _is_windows
    else VENV_DIR / "bin" / "flask"
)


# --- Helper Functions ---


def check_python_version():
    """Checks if the current Python version meets the minimum requirement."""
    console.print(
        f"Checking Python version ({'.'.join(map(str, PYTHON_MIN_VERSION))}+ required)..."
    )
    if sys.version_info < PYTHON_MIN_VERSION:
        console_stderr.print(
            f"ERROR: Python {sys.version.split()[0]} is too old.", style="bold red"
        )
        console_stderr.print(
            f"Please install Python {'.'.join(map(str, PYTHON_MIN_VERSION))} or newer.",
            style="yellow",
        )
        return False
    console.print(f"[green]Python {sys.version.split()[0]} — OK.[/green]")
    return True


def run_command(command, capture=False, check=True, cwd=PROJECT_ROOT, env=None,
                msg_on_fail="Command failed."):
    """Runs a subprocess command with consistent error handling."""
    try:
        command_str = [str(p) for p in command]
        console.print(f"Running: {' '.join(command_str)}")
        result = subprocess.run(
            command_str, capture_output=capture, check=check,
            cwd=cwd, env=env, text=True, encoding="utf-8",
        )
        if capture and result.stdout:
            console.print(result.stdout)
        if result.stderr and check:
            console_stderr.print(result.stderr)
        return True, result
    except FileNotFoundError:
        console_stderr.print(f"ERROR: Command not found: {command[0]}", style="bold red")
        console_stderr.print("Ensure the required program is installed and in your PATH.", style="yellow")
        return False, None
    except subprocess.CalledProcessError as e:
        console_stderr.print(f"ERROR: {msg_on_fail}", style="bold red")
        if e.stdout:
            console_stderr.print(e.stdout, style="red")
        if e.stderr:
            console_stderr.print(e.stderr, style="red")
        return False, e
    except Exception as e:
        console_stderr.print(f"ERROR: {msg_on_fail} ({e})", style="bold red")
        return False, e


def run_with_progress(description, func, *args, **kwargs):
    """Runs a callable inside a Rich spinner progress bar."""
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
        except Exception:
            progress.stop_task(task)
            raise


# --- Setup Steps ---


def setup_configuration_file():
    """Creates apps/desktop/data/.env if it does not exist."""
    console.print("\n[bold]Setting up configuration...[/bold]")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if ENV_FILE.exists():
        console.print(f"[yellow].env already exists at: {ENV_FILE} — skipping.[/yellow]")
        return True

    secret_key = secrets.token_hex(24)
    env_content = (
        "# Flask Secret Key (Required)\n"
        f"SECRET_KEY='{secret_key}'\n"
        "\n"
        "# Flask app module path (do not change)\n"
        "FLASK_APP=apps/desktop/src/core\n"
        "\n"
        "# Set to False for production\n"
        "FLASK_DEBUG=False\n"
        "\n"
        "# Database URL\n"
        "DATABASE_URL=sqlite:///./apps/desktop/data/database.db\n"
        "\n"
        "# Feedback URLs (optional)\n"
        "GOOGLE_APPS_SCRIPT_FEEDBACK_URL='https://script.google.com/macros/s/"
        "AKfycbwgakVifq4XkMRUMYvcRuR3083z6tn4cmjx7kwQCn5zNBwGJxEObKf5zGTI5an0A2rwvQ/exec'\n"
        "GOOGLE_SHEET_PUBLIC_URL='https://docs.google.com/spreadsheets/d/"
        "1OW1PQTpdOcJK3bWLHsjkNuHZBkXp_RpLMel4IlDMrLg'\n"
    )
    try:
        ENV_FILE.write_text(env_content, encoding="utf-8")
        console.print(f"[green]Created .env at: {ENV_FILE}[/green]")
    except IOError as e:
        console_stderr.print(f"[bold red]ERROR: Could not write .env: {e}[/bold red]")
        return False
    return True


def setup_database():
    """Initialises Flask-Migrate and applies migrations."""
    console.print("\n[bold]Setting up database...[/bold]")

    if not VENV_FLASK.exists():
        console_stderr.print(
            f"[bold red]ERROR: flask not found at {VENV_FLASK}.[/bold red]\n"
            "[yellow]Run [bold]uv sync[/] from the project root and try again.[/yellow]"
        )
        return False

    flask_env = os.environ.copy()
    flask_env["FLASK_APP"] = "apps/desktop/src/core"

    if not MIGRATIONS_DIR.exists():
        console.print("[yellow]Migrations folder not found — running 'flask db init'...[/yellow]")
        ok, _ = run_command(
            [VENV_FLASK, "db", "init"], env=flask_env,
            msg_on_fail="'flask db init' failed.",
        )
        if not ok:
            return False
        console.print("[yellow]Creating initial migration...[/yellow]")
        ok, _ = run_command(
            [VENV_FLASK, "db", "migrate", "-m", "Initial migration"],
            env=flask_env, msg_on_fail="'flask db migrate' failed.",
        )
        if not ok:
            return False

    def db_upgrade():
        subprocess.run(
            [str(VENV_FLASK), "db", "upgrade"],
            check=True, env=flask_env, cwd=PROJECT_ROOT,
        )

    try:
        run_with_progress("Applying database migrations", db_upgrade)
        console.print("[green]Database ready.[/green]")
    except Exception as e:
        console_stderr.print(f"[bold red]Database migration failed: {e}[/bold red]")
        return False
    return True


# --- Main ---


def main():
    import time

    start_time = time.perf_counter()
    console.rule("[bold cyan]SeriesScape Setup")
    console.print("[bold]Starting SeriesScape setup...[/bold]")
    os.chdir(PROJECT_ROOT)

    if not check_python_version():
        return False
    if not setup_configuration_file():
        return False
    if not setup_database():
        return False

    elapsed = time.perf_counter() - start_time
    mins, secs = divmod(int(elapsed), 60)
    time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
    console.rule(f"[bold green]Setup complete in {time_str}![/bold green]")
    console.print(
        "[bold green]Run the app with: "
        "scripts\\run.bat (Windows) or scripts/run.sh (Linux/macOS)[/bold green]"
    )
    return True


if __name__ == "__main__":
    try:
        sys.exit(0 if main() else 1)
    except Exception as e:
        if "console" in globals():
            console.print_exception()
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
