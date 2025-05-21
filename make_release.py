# make_release.py
import os
import shutil
import json
import re
import sys
import fnmatch
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
except ImportError:
    print("\n[!] The 'rich' library is required. Install it with: pip install rich\n")
    sys.exit(1)

console = Console()

# --- CONFIGURABLE ---
# Files/folders to include (relative to project root)
INCLUDE = [
    "docs",
    "src",
    ".gitignore",
    "LICENSE",
    "package.json",
    "README.md",
    "requirements.txt",
    "run.bat",
    "run.py",
    "run.sh",
    "setup.bat",
    "setup.py",
    "setup.sh",
]
# Files/folders to exclude (relative to project root, supports glob patterns)
EXCLUDE = [
    "src/**/__pycache__",
    "src/**/__pycache__/*",
]

PROJECT_ROOT = Path(__file__).parent.resolve()


def get_version():
    pkg_json = PROJECT_ROOT / "package.json"
    if pkg_json.exists():
        with open(pkg_json, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    return "0.0.0"


def validate_version(version):
    """Validate version string to match x.x.x where x is one or more digits."""
    return bool(re.fullmatch(r"\d+\.\d+\.\d+", version))


def prompt(msg, default=None):
    try:
        if default:
            return input(f"{msg} [{default}]: ") or default
        return input(f"{msg}: ")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]Operation cancelled by user.[/]")
        sys.exit(0)


def should_exclude(path):
    rel = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    for ex in EXCLUDE:
        if fnmatch.fnmatch(rel, ex):
            return True
    return False


def count_files_to_copy(src, filter_func):
    src = Path(src)
    if src.is_file():
        return 0 if filter_func(src) else 1
    count = 0
    for item in src.rglob("*"):
        if item.is_file() and not filter_func(item):
            count += 1
    return count


def copy_with_filter(src, dst, progress=None, task_id=None):
    src = Path(src)
    dst = Path(dst)
    if src.is_dir():
        if should_exclude(src):
            return
        if not dst.exists():
            dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            copy_with_filter(item, dst / item.name, progress, task_id)
    elif src.is_file():
        if should_exclude(src):
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if progress and task_id is not None:
            progress.advance(task_id)


def main():
    try:
        console.print(
            "\n[bold cyan]==============================[/]", justify="center"
        )
        console.print("[bold magenta]ShowTrackr Release Builder[/]", justify="center")
        console.print(
            "[bold cyan]==============================\n[/]", justify="center"
        )
        # Version input with validation
        while True:
            version = prompt("Enter version for release", get_version())
            if validate_version(version):
                break
            console.print(
                "\n[bold red]❌ Invalid version format. Please use x.x.x (e.g. 0.24.3, 0.2.4)[/]"
            )
        release_name = f"ShowTrackr-Web-v{version}"
        console.print("\nChoose release type:")
        console.print(
            "  [bold]1.[/] 📦  Create zip archive only (no folder, files zipped directly)"
        )
        console.print(
            "  [bold]2.[/] 📁  Create release folder (optionally zip the folder)"
        )
        console.print("")
        while True:
            choice = prompt("Enter 1 or 2", "2")
            if choice in ("1", "2"):
                break
            console.print("\n[bold red]❌ Invalid choice. Please enter 1 or 2.[/]")
        if choice == "1":
            zip_name = f"{release_name}.zip"
            zip_path = PROJECT_ROOT / zip_name
            console.print(f"\n[bold]Creating zip:[/] [green]{zip_path}[/]\n")
            import tempfile

            try:
                with tempfile.TemporaryDirectory() as tempdir:
                    tempdir = Path(tempdir)
                    versioned_dir = tempdir / release_name
                    versioned_dir.mkdir()
                    # Count total files for progress
                    total_files = 0
                    for item in INCLUDE:
                        src = PROJECT_ROOT / item
                        if src.exists():
                            total_files += count_files_to_copy(src, should_exclude)
                    with Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        "[progress.percentage]{task.percentage:>3.0f}%",
                        "{task.completed}/{task.total} files",
                        TimeElapsedColumn(),
                        console=console,
                    ) as progress:
                        task = progress.add_task("Copying files", total=total_files)
                        for item in INCLUDE:
                            src = PROJECT_ROOT / item
                            if src.exists():
                                try:
                                    copy_with_filter(
                                        src, versioned_dir / src.name, progress, task
                                    )
                                except Exception as e:
                                    console.print(
                                        f"  [yellow]⚠️  Error copying {item}: {e}[/]"
                                    )
                            else:
                                console.print(
                                    f"  [yellow]⚠️  Warning: {item} not found, skipping.[/]"
                                )
                    shutil.make_archive(
                        str(zip_path.with_suffix("")),
                        "zip",
                        root_dir=tempdir,
                        base_dir=release_name,
                    )
                console.print(
                    f"\n[bold green]✅ Zip archive created:[/] [cyan]{zip_path}[/]\n"
                )
            except Exception as e:
                console.print(f"\n[bold red]❌ Error creating zip archive: {e}[/]\n")
                sys.exit(1)
        else:
            release_folder = PROJECT_ROOT / release_name
            if release_folder.exists():
                console.print(
                    f"\n[bold yellow]Removing existing release folder:[/] [cyan]{release_folder}[/]"
                )
                try:
                    shutil.rmtree(release_folder)
                except Exception as e:
                    console.print(f"[bold red]❌ Error removing folder: {e}[/]")
                    sys.exit(1)
            console.print(
                f"\n[bold]Creating release folder:[/] [cyan]{release_folder}[/]\n"
            )
            try:
                release_folder.mkdir()
                total_files = 0
                for item in INCLUDE:
                    src = PROJECT_ROOT / item
                    if src.exists():
                        total_files += count_files_to_copy(src, should_exclude)
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    "{task.completed}/{task.total} files",
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Copying files", total=total_files)
                    for item in INCLUDE:
                        src = PROJECT_ROOT / item
                        if src.exists():
                            try:
                                copy_with_filter(
                                    src, release_folder / src.name, progress, task
                                )
                            except Exception as e:
                                console.print(
                                    f"  [yellow]⚠️  Error copying {item}: {e}[/]"
                                )
                        else:
                            console.print(
                                f"  [yellow]⚠️  Warning: {item} not found, skipping.[/]"
                            )
                console.print(
                    f"\n[bold green]✅ Release folder created at:[/] [cyan]{release_folder}[/]\n"
                )
            except Exception as e:
                console.print(f"\n[bold red]❌ Error creating release folder: {e}[/]\n")
                sys.exit(1)
            do_zip = (
                prompt("Also create zip archive of the folder? (y/n)", "y")
                .lower()
                .startswith("y")
            )
            if do_zip:
                zip_name = f"{release_name}.zip"
                zip_path = PROJECT_ROOT / zip_name
                console.print(f"\n[bold]Creating zip:[/] [green]{zip_path}[/]\n")
                import tempfile

                try:
                    with tempfile.TemporaryDirectory() as tempdir:
                        tempdir = Path(tempdir)
                        versioned_dir = tempdir / release_name
                        shutil.copytree(release_folder, versioned_dir)
                        shutil.make_archive(
                            str(zip_path.with_suffix("")),
                            "zip",
                            root_dir=tempdir,
                            base_dir=release_name,
                        )
                    console.print(
                        f"\n[bold green]✅ Zip archive created:[/] [cyan]{zip_path}[/]\n"
                    )
                except Exception as e:
                    console.print(
                        f"\n[bold red]❌ Error creating zip archive: {e}[/]\n"
                    )
                    sys.exit(1)
            # Offer to delete the release folder after zipping
            if do_zip:
                console.print(
                    f"[bold]Delete the release folder ([cyan]{release_folder}[/])? (y/n)[/] [n]:",
                    highlight=False,
                )
                delete_folder = prompt("", "n").lower().startswith("y")
                if delete_folder:
                    try:
                        shutil.rmtree(release_folder)
                        console.print(f"[bold green]🗑️  Release folder deleted.[/]")
                    except Exception as e:
                        console.print(
                            f"[bold red]❌ Error deleting release folder: {e}[/]"
                        )
        console.print("[bold cyan]==============================[/]", justify="center")
        console.print("[bold magenta]Release Build Done![/]", justify="center")
        console.print(
            "[bold cyan]==============================\n[/]", justify="center"
        )
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]Operation cancelled by user.[/]")
        sys.exit(0)


if __name__ == "__main__":
    main()
