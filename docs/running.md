# SeriesScape - Running the Application

This guide explains how to run the SeriesScape application after you have successfully completed
the [Setup Guide](./setup.md).

## Using the Run Scripts (Recommended)

The project provides convenient scripts to start the application. These scripts check that migrations are up-to-date and
launch the Flask development server.

1. **Open your Terminal:**
    - **Windows:** Open Command Prompt or PowerShell.
    - **Linux/macOS:** Open your preferred terminal application.

2. **Navigate to the project root directory** (e.g., `cd path/to/SeriesScape`).

3. **Execute the run script:**
    - **Windows:**

      ```batch
      scripts\run.bat
      ```

    - **Linux/macOS:**

      ```bash
      bash scripts/run.sh
      ```

      (Make it executable first if needed: `chmod +x scripts/run.sh`, then `./scripts/run.sh`)

The script will output progress messages and end with something like:

```
Flask development server started!
Access at: http://127.0.0.1:5000
Press CTRL+C to quit.
 * Running on http://127.0.0.1:5000
```

## Manual Execution (Alternative)

If you prefer to run commands directly:

1. **Apply any pending database migrations:**

    - **Windows (PowerShell):**

      ```powershell
      $env:FLASK_APP = "apps/desktop/src/core"
      .venv\Scripts\flask.exe db upgrade
      ```

    - **Linux/macOS:**

      ```bash
      export FLASK_APP="apps/desktop/src/core"
      .venv/bin/flask db upgrade
      ```

2. **Start the Flask development server:**

    - **Windows:**

      ```powershell
      .venv\Scripts\flask.exe run
      ```

    - **Linux/macOS:**

      ```bash
      .venv/bin/flask scripts/run
      ```

## Accessing SeriesScape in Your Browser

Once the server is running, open your web browser and go to:

➡️ **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You should see the SeriesScape application. Press **Ctrl+C** in the terminal to stop the server.
