# ShowTrackr - Running the Application

This guide explains how to run the ShowTrackr application after you have successfully completed the [Setup Guide](./setup.md).

## Using the Run Scripts (Recommended)

The project provides convenient scripts to start the application. These scripts handle activating the virtual environment, ensuring database migrations are up-to-date, and launching the Flask development server.

1.  **Open your Terminal:**

    - **Windows:** Open Command Prompt or PowerShell.
    - **Linux:** Open your preferred terminal application.

2.  **Navigate to Project Directory:** Change your current directory to the root of the ShowTrackr project (e.g., `cd path/to/ShowTrackr-Web`).

3.  **Execute the Run Script:**

    - **Windows:**

      ```batch
      run.bat
      ```

    - **Linux:**

      ```bash
      bash run.sh
      ```

      (If you haven't already, you might need to make it executable first: `chmod +x run.sh`, then you can run `./run.sh`)

The script will output messages indicating its progress:

- Activating virtual environment...
- Ensuring database migrations are up-to-date...
- Starting Flask development server...
- It will typically end with lines like:
  ```
   * Running on http://127.0.0.1:5000
  Press CTRL+C to quit.
  ```

## Manual Execution (Alternative)

If you prefer or if the scripts have issues, you can run the necessary commands manually:

1.  **Activate Virtual Environment:**

    - Ensure you are in the project root directory.
    - **Windows (Command Prompt):** `.\.venv\Scripts\activate.bat`
    - **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
    - **Linux:** `source .venv/bin/activate`
      Your prompt should now indicate the active virtual environment (e.g., `(.venv)`).

2.  **Set `FLASK_APP` (if necessary):**
    Flask needs to know where your application is. This is usually handled by the `.env` file, but you can set it explicitly if needed.

    - **Windows (Command Prompt):** `set FLASK_APP=src/watchlist`
    - **Windows (PowerShell):** `$env:FLASK_APP="src/watchlist"`
    - **Linux:** `export FLASK_APP="src/watchlist"`

3.  **Apply Database Migrations:**
    This ensures your database schema is current.

    ```bash
    flask db upgrade
    ```

4.  **Start the Flask Server:**
    This command starts the development web server.

    ```bash
    flask run
    ```

    You will see output indicating the server is running, usually on `http://127.0.0.1:5000`.

## Accessing ShowTrackr in Your Browser

Once the server is running (either via script or manually), open your web browser (e.g., Chrome, Firefox, Edge) and go to:

➡️ **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You should see the ShowTrackr application.
