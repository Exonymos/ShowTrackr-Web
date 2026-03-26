# make_release.py
# ShowTrackr Release Builder
# This script is used to create a release package for the ShowTrackr project.
# It copies specified files and folders from the project directory to a new release folder,
# and optionally creates a zip archive of the release folder.
import shutil
import json
import re
import sys
import fnmatch
from pathlib import Path
import tempfile
import subprocess

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


def copy_files_to_target_with_progress(target_dir):
    """Copies included files to the target directory with a progress bar."""
    total_files = 0
    for item_name in INCLUDE:
        src_path = PROJECT_ROOT / item_name
        if src_path.exists():
            total_files += count_files_to_copy(src_path, should_exclude)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "{task.completed}/{task.total} files",
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Copying files", total=total_files)
        for item_name in INCLUDE:
            src_path = PROJECT_ROOT / item_name
            if src_path.exists():
                try:
                    copy_with_filter(
                        src_path, target_dir / src_path.name, progress, task
                    )
                except Exception as e:
                    console.print(f"  [yellow]⚠️  Error copying {item_name}: {e}[/]")
            else:
                console.print(
                    f"  [yellow]⚠️  Warning: {item_name} not found, skipping.[/]"
                )


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


def run_tests_and_confirm_continue():
    """Runs tests and asks user to continue if they fail."""
    console.print("[bold blue]Running test suite with pytest before release...[/]")
    result = subprocess.run(
        [sys.executable, "-m", "pytest"], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        console.print("[bold green]✅ All tests passed![/]")
        return True
    else:
        console.print("[bold red]❌ Some tests failed![/]")
        console.print(
            "[yellow]See details by running: [bold]pytest -v[/] in your terminal.[/]"
        )
        cont = (
            prompt("Tests failed. Continue with release anyway? (y/n)", "n")
            .lower()
            .startswith("y")
        )
        if not cont:
            console.print("[bold yellow]Aborting release due to test failures.[/]")
            sys.exit(1)
        return True


def get_release_version_and_mode():
    """Prompts for version, validates it, and determines production mode."""
    while True:
        version_input = prompt("Enter version for release", get_version())
        prod_mode = False
        version = version_input
        if version_input.endswith("-P"):
            prod_mode = True
            version = version_input[:-2].strip()
        if validate_version(version):
            return version, prod_mode
        console.print(
            "\n[bold red]❌ Invalid version format. Please use x.x.x (e.g. 0.24.3, 0.2.4)[/]"
        )


def get_release_type_choice():
    """Prompts user for the type of release (zip only or folder)."""
    console.print("\nChoose release type:")
    console.print(
        "  [bold]1.[/] 📦  Create zip archive only (no folder, files zipped directly)"
    )
    console.print("  [bold]2.[/] 📁  Create release folder (optionally zip the folder)")
    console.print("")
    while True:
        choice = prompt("Enter 1 or 2", "2")
        if choice in ("1", "2"):
            return choice
        console.print("\n[bold red]❌ Invalid choice. Please enter 1 or 2.[/]")


def update_for_production_in_release(release_root, version, changes_list):
    """Updates files for production mode in the release directory."""

    # 1. package.json
    pkg_path = Path(release_root) / "package.json"
    try:
        if pkg_path.exists():
            with open(pkg_path, encoding="utf-8") as f:
                data = json.load(f)
            old_version = data.get("version", "")
            if old_version != version:
                data["version"] = version
                with open(pkg_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                changes_list.append(
                    ("package.json", f"Updated version: {old_version} → {version}")
                )
    except Exception as e:
        changes_list.append(("package.json", f"[ERROR] Could not update: {e}"))

    # 2. config.py
    config_path = Path(release_root) / "src" / "watchlist" / "config.py"
    try:
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            changed_config = False
            for line in lines:
                if line.strip().startswith("APP_VERSION"):
                    old = line.strip()
                    new = f'APP_VERSION = "{version}"\n'
                    if line != new:
                        new_lines.append(new)
                        changed_config = True
                        changes_list.append(
                            ("config.py", f"Updated APP_VERSION: {old} → {new.strip()}")
                        )
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            if changed_config:
                with open(config_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
    except Exception as e:
        changes_list.append(("config.py", f"[ERROR] Could not update: {e}"))


def show_changes_summary(changes_list):
    if not changes_list:
        console.print("[green]No files were changed for production release.[/]")
        return
    console.print("\n[bold cyan]Production Release Changes in Release Output:[/]")
    for fname, desc in changes_list:
        if "[ERROR]" in desc:
            console.print(f"[bold red]{fname}[/]: {desc}")
        else:
            console.print(f"[bold yellow]{fname}[/]: {desc}")


def create_zip_archive(zip_path, root_dir_for_archive, base_dir_to_archive):
    """Creates a zip archive."""
    console.print(f"\n[bold]Creating zip:[/] [green]{zip_path}[/]\n")
    try:
        shutil.make_archive(
            str(zip_path.with_suffix("")),
            "zip",
            root_dir=root_dir_for_archive,
            base_dir=base_dir_to_archive,
        )
        console.print(f"\n[bold green]✅ Zip archive created:[/] [cyan]{zip_path}[/]\n")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error creating zip archive: {e}[/]\n")
        sys.exit(1)


def handle_zip_only_release(
    release_name_base, version_str, prod_mode_flag, changes_list_ref
):
    """Handles the 'zip only' release process."""
    zip_name = f"{release_name_base}.zip"
    zip_path = PROJECT_ROOT / zip_name
    console.print(f"\n[bold]Preparing for zip-only release:[/] [green]{zip_path}[/]\n")

    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir_path = Path(tempdir_str)
        versioned_dir_in_temp = tempdir_path / release_name_base
        versioned_dir_in_temp.mkdir()

        copy_files_to_target_with_progress(versioned_dir_in_temp)

        if prod_mode_flag:
            update_for_production_in_release(
                versioned_dir_in_temp, version_str, changes_list_ref
            )

        create_zip_archive(zip_path, tempdir_path, release_name_base)


def handle_folder_release(
    release_name_base, version_str, prod_mode_flag, changes_list_ref
):
    """Handles the 'folder' release process."""
    release_folder_path = PROJECT_ROOT / release_name_base
    if release_folder_path.exists():
        console.print(
            f"\n[bold yellow]Removing existing release folder:[/] [cyan]{release_folder_path}[/]"
        )
        try:
            shutil.rmtree(release_folder_path)
        except Exception as e:
            console.print(f"[bold red]❌ Error removing folder: {e}[/]")
            sys.exit(1)

    console.print(
        f"\n[bold]Creating release folder:[/] [cyan]{release_folder_path}[/]\n"
    )
    try:
        release_folder_path.mkdir()
        copy_files_to_target_with_progress(release_folder_path)

        if prod_mode_flag:
            update_for_production_in_release(
                release_folder_path, version_str, changes_list_ref
            )

        console.print(
            f"\n[bold green]✅ Release folder created at:[/] [cyan]{release_folder_path}[/]\n"
        )
    except Exception as e:
        console.print(f"\n[bold red]❌ Error creating release folder: {e}[/]\n")
        sys.exit(1)

    do_zip_folder = (
        prompt("Also create zip archive of the folder? (y/n)", "y")
        .lower()
        .startswith("y")
    )
    if do_zip_folder:
        zip_name = f"{release_name_base}.zip"
        zip_path = PROJECT_ROOT / zip_name
        create_zip_archive(zip_path, PROJECT_ROOT, release_name_base)

        delete_folder_after_zip = (
            prompt(
                f"Delete the release folder ([cyan]{release_folder_path}[/])? (y/n)",
                "n",
            )
            .lower()
            .startswith("y")
        )
        if delete_folder_after_zip:
            try:
                shutil.rmtree(release_folder_path)
                console.print("[bold green]🗑️  Release folder deleted.[/]")
            except Exception as e:
                console.print(f"[bold red]❌ Error deleting release folder: {e}[/]")


def main():
    try:
        run_tests_and_confirm_continue()

        console.print(
            "\n[bold cyan]==============================[/]", justify="center"
        )
        console.print("[bold magenta]ShowTrackr Release Builder[/]", justify="center")
        console.print(
            "[bold cyan]==============================\n[/]", justify="center"
        )

        version, prod_mode = get_release_version_and_mode()
        production_changes = []  # To store descriptions of changes made for prod mode
        release_base_name = f"ShowTrackr-Web-v{version}"

        choice = get_release_type_choice()

        if choice == "1":
            handle_zip_only_release(
                release_base_name, version, prod_mode, production_changes
            )
        else:  # Choice == "2"
            handle_folder_release(
                release_base_name, version, prod_mode, production_changes
            )

        if prod_mode:
            see_summary = (
                prompt(
                    "Show what was changed for production release output? (y/n)", "n"
                )
                .lower()
                .startswith("y")
            )
            if see_summary:
                show_changes_summary(production_changes)

        console.print("[bold cyan]==============================[/]", justify="center")
        console.print("[bold magenta]Release Build Done![/]", justify="center")
        console.print(
            "[bold cyan]==============================\n[/]", justify="center"
        )

    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold yellow]Operation cancelled by user.[/]")
        sys.exit(0)
    except Exception as e:  # Catch any other unexpected error in main flow
        console.print(
            f"\n[bold red]❌ An unexpected error occurred during the release process: {e}[/]\n"
        )
        console.print_exception(show_locals=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
