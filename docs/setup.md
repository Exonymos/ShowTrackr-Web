# SeriesScape - Detailed Setup Guide

This guide provides detailed instructions for setting up the SeriesScape application on your local machine.

## Prerequisites

1. **Python 3.10+:** Required to run the application.
    - **Check:** `python --version` or `python3 --version` in your terminal.
    - **Download:** [python.org/downloads/](https://www.python.org/downloads/)
    - **Installation Note (Windows):** Check **"Add Python to PATH"** during installation.

2. **uv:** The project uses `uv` to manage the virtual environment and all Python dependencies. The setup scripts will
   attempt to install it automatically if it is missing.
    - **Check:** `uv --version`
    - **Manual install:
      ** [docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

3. **Git (Optional):** Only needed if you want to clone the repository. You can download the code as a ZIP file
   otherwise.

## Getting the Code

### Download the latest release (Recommended for most users)

1. Go to the GitHub releases
   page: [github.com/Exonymos/SeriesScape/releases/latest](https://github.com/Exonymos/SeriesScape/releases/latest)
2. Download `SeriesScape-vX.X.X.zip` (where X.X.X is the version number).
3. Extract the ZIP file to a location of your choice.
4. Open your terminal and navigate into the extracted folder.

### Clone the repository (For developers / contributors)

**Method A: Downloading ZIP**

1. Go to [github.com/Exonymos/SeriesScape](https://github.com/Exonymos/SeriesScape).
2. Click the green **"<> Code"** button and select **"Download ZIP"**.
3. Extract and navigate into the folder.

**Method B: Using Git**

```bash
git clone https://github.com/Exonymos/SeriesScape.git
cd SeriesScape
```

## Setup Steps

All commands below should be run from the project's root directory (`SeriesScape/`).

### Recommended: Using Setup Scripts (Easiest)

The project provides setup scripts that handle everything automatically — checking Python, installing `uv`, installing
all dependencies, generating your `.env` file, and initialising the database.

- **Windows:**

  ```batch
  scripts\setup.bat
  ```

- **Linux/macOS:**

  ```bash
  chmod +x scripts/setup.sh   # Only needed once
  bash scripts/setup.sh
  ```

Once complete, skip straight to [Running the Application](./running.md).

---

### Manual Setup

**1. Install dependencies with uv**

`uv` automatically creates and manages the virtual environment (`.venv`) in the project root.

```bash
uv sync --all-groups
```

> The `--all-groups` flag ensures that all development dependencies are installed. You can omit it if you only need
> production dependencies.

This installs all application and development dependencies declared in `pyproject.toml`.

**2. Configure the `.env` file**

The setup script generates this automatically. If setting up manually:

- Navigate to `apps/desktop/data/` (create it if it doesn't exist).
- Copy `apps/desktop/data/.env.example` to `apps/desktop/data/.env`.
- Open `.env` and replace `CHANGE_ME` with a strong, random secret key. Generate one with:

  ```bash
  python -c "import secrets; print(secrets.token_hex(24))"
  ```

  Your `.env` should look like this:

  ```dotenv
  SECRET_KEY='your_generated_key_here'
  FLASK_APP=apps/desktop/src/core
  FLASK_DEBUG=True
  DATABASE_URL=sqlite:///./apps/desktop/data/database.db
  GOOGLE_APPS_SCRIPT_FEEDBACK_URL=''
  GOOGLE_SHEET_PUBLIC_URL=''
  ```

- **Security:** The `apps/desktop/data/` directory (including `.env` and your database) is listed in `.gitignore`. Never
  commit it.

**3. Initialise the database (first time only)**

Set the `FLASK_APP` environment variable and run the migration commands:

- **Windows (PowerShell):**

  ```powershell
  $env:FLASK_APP = "apps/desktop/src/core"
  .venv\Scripts\flask.exe db init
  .venv\Scripts\flask.exe db migrate -m "Initial migration"
  .venv\Scripts\flask.exe db upgrade
  ```

- **Linux/macOS:**

  ```bash
  export FLASK_APP="apps/desktop/src/core"
  .venv/bin/flask db init
  .venv/bin/flask db migrate -m "Initial migration"
  .venv/bin/flask db upgrade
  ```

You only need to run these once for a fresh setup. On subsequent runs, the run scripts apply any pending migrations
automatically.

---

Setup is complete! You can now proceed to [Running the Application](./running.md).
