# run.py
import os
import subprocess
import sys
from pathlib import Path
import platform

# Ensure the script is running from the project root directory
project_root = Path(__file__).parent.resolve()
os.chdir(project_root)

# --- Virtual Environment Check  ---
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


try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )
    from rich.traceback import install as rich_traceback_install

    console = Console()
    rich_traceback_install(show_locals=True, suppress=[])
except ImportError:
    # Fallback to standard print/logging
    console = None

# --- Virtual Environment Warning ---
if current_executable != expected_executable:
    if console:
        console.rule("[bold yellow]Virtual Environment Warning")
        console.print(
            ":warning: [yellow]It looks like the virtual environment (.venv) is not activated, or you are running this script with a different Python interpreter.[/yellow]"
        )
        console.print(f"[bold]Expected venv:[/] [cyan]{expected_venv_path}[/]")
        console.print(f"[bold]Current Python:[/] [magenta]{sys.executable}[/]")
        console.print("\n[bold]Please activate the environment first:[/]")
        if is_windows:
            console.print("[green]> .\\.venv\\Scripts\\activate[/]")
            console.print("Or run setup.bat / run.bat")
        else:
            console.print("[green]$ source ./.venv/bin/activate[/]")
            console.print("Or run setup.sh / run.sh")
        console.print(
            "[yellow]Continuing, but dependency issues or unexpected behavior may occur.[/yellow]"
        )
        console.rule()
    else:
        print("--- WARNING ---")
        print("It looks like the virtual environment (.venv) is not activated,")
        print("or you are running this script with a different Python interpreter.")
        print(f"Expected venv: {expected_venv_path}")
        print(f"Current Python: {sys.executable}")
        print("\nPlease activate the environment first:")
        if is_windows:
            print("> .\\.venv\\Scripts\\activate")
            print("Or run setup.bat / run.bat")
        else:
            print("$ source ./.venv/bin/activate")
            print("Or run setup.sh / run.sh")
        print("------------")
        print("Continuing, but dependency issues or unexpected behavior may occur.")
        print("------------")

# --- Database Migration Progress ---
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    if console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Ensuring database migrations are up-to-date...", total=None
            )
            try:
                subprocess.run(
                    [sys.executable, "-m", "flask", "db", "upgrade"],
                    check=True,
                    cwd=project_root,
                    capture_output=True,
                )
                progress.update(
                    task,
                    description="Database migrations checked/applied successfully.",
                )
                progress.stop_task(task)
                console.print(
                    "[green]Database migrations checked/applied successfully.[/green]"
                )
            except subprocess.CalledProcessError as e:
                progress.stop_task(task)
                console.print(f"[bold red]Error running database migrations:[/] {e}")
                console.print(f"[red]Stderr:[/] {e.stderr.decode()}")
                console.print(
                    "[yellow]Please check your database configuration and migration files.[/]"
                )
                sys.exit(1)
            except FileNotFoundError:
                progress.stop_task(task)
                console.print(
                    "[bold red]Error: 'flask' command not found. Is Flask installed and the venv activated?"
                )
                sys.exit(1)
    else:
        print("Ensuring database migrations are up-to-date...")
        try:
            subprocess.run(
                [sys.executable, "-m", "flask", "db", "upgrade"],
                check=True,
                cwd=project_root,
                capture_output=True,
            )
            print("Database migrations checked/applied successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running database migrations: {e}", file=sys.stderr)
            print(f"Stderr: {e.stderr.decode()}", file=sys.stderr)
            print(
                "Please check your database configuration and migration files.",
                file=sys.stderr,
            )
            sys.exit(1)
        except FileNotFoundError:
            print(
                "Error: 'flask' command not found. Is Flask installed and the venv activated?",
                file=sys.stderr,
            )
            sys.exit(1)

# --- Start Development Server ---
try:
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    from watchlist import create_app

    app = create_app()
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        if console:
            console.print("[green]Flask development server started![/green]")
            console.print("[bold]Access at:[/] [cyan]http://127.0.0.1:5000[/]")
            console.print("[bold]Press CTRL+C to quit.[/]")
        else:
            print("Flask development server started!")
            print("Access at: http://127.0.0.1:5000")
            print("Press CTRL+C to quit.")
    app.run(host="127.0.0.1", port=5000)
    # will test for flask run
except ImportError as e:
    if console:
        console.print(f"[bold red]Error importing application:[/] {e}")
        console.print(
            "[yellow]Ensure all dependencies are installed (`pip install -r requirements.txt`)"
        )
        console.print("Try running the setup script (setup.bat or setup.sh).")
    else:
        print(f"Error importing application: {e}", file=sys.stderr)
        print(
            "Ensure all dependencies are installed (`pip install -r requirements.txt`)",
            file=sys.stderr,
        )
        print("Try running the setup script (setup.bat or setup.sh).", file=sys.stderr)
    sys.exit(1)
except KeyboardInterrupt:
    if console:
        console.print("[yellow]\nServer stopped by user (Ctrl+C). Goodbye![/yellow]")
    else:
        print("\nServer stopped by user (Ctrl+C). Goodbye!")
    sys.exit(0)
except Exception as e:
    if console:
        console.print(
            f"[bold red]An error occurred while trying to run the Flask application:[/] {e}"
        )
        console.print_exception()
    else:
        print(
            f"An error occurred while trying to run the Flask application: {e}",
            file=sys.stderr,
        )
        import traceback

        traceback.print_exc()
    sys.exit(1)
