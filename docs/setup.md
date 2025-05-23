# ShowTrackr - Detailed Setup Guide

This guide provides detailed instructions for setting up the ShowTrackr application on your local machine.

## Prerequisites

1.  **Python:** You need Python installed. Version 3.13 or newer is recommended.

    - **Check Installation:** Open your terminal or command prompt and type `python --version` or `python3 --version`.
    - **Download:** If you don't have Python or need a newer version, download it from the official website: [python.org/downloads/](https://www.python.org/downloads/)
    - **Installation Note:** During installation (especially on Windows), ensure you check the box that says **"Add Python X.Y to PATH"**.

2.  **pip:** Python package manager. It comes bundled with Python installations. You can check if it's installed by running `pip --version` or `pip3 --version` in your terminal. If it's not installed, you can install it by following the instructions on the [pip installation page](https://pip.pypa.io/en/stable/installation/).

3.  **venv:** Python virtual environment module. The setup script will attempt to install it if missing. You may need to install it manually if you encounter issues.

4.  **Git (Optional):** Required only if you want to clone the repository directly. You can download the code as a ZIP file otherwise. [Git Download](https://git-scm.com/downloads)

## Getting the Code

Choose one of the following methods:

### Download the latest release

You can download the latest release of the ShowTrackr code from the GitHub repository. This is the recommended method for most users.

1.  Go to the GitHub repository releases: [ShowTrackr-Web](https://github.com/Exonymos/ShowTrackr-Web/releases/latest)
2.  Make sure the release have the latest version.
3.  Click on "ShowTrackr-Web-vX.X.X.zip" (where X.X.X is the version number).
4.  Save the ZIP file to your computer.
5.  Extract the ZIP file to a location of your choice.
6.  Open your terminal or command prompt and navigate into the extracted folder (e.g., `cd path/to/ShowTrackr-Web-vX.X.X`).

### Clone the repository

**Method A: Downloading ZIP**

1.  Go to the GitHub repository: [github.com/Exonymos/ShowTrackr-Web](https://github.com/Exonymos/ShowTrackr-Web)
2.  Click the green "<> Code" button.
3.  Select "Download ZIP".
4.  Extract the downloaded ZIP file to a location of your choice.
5.  Open your terminal or command prompt and navigate into the extracted folder (e.g., `cd path/to/ShowTrackr-Web-main`).

**Method B: Using Git (needs Git installed)**

1.  Download and install Git from [git-scm.com](https://git-scm.com/downloads) if you haven't already.
2.  Open your terminal or command prompt.
3.  Navigate to the directory where you want to clone the repository (e.g., `cd path/to/your/directory`).
4.  Run the following command to clone the repository:

    ```bash
    git clone https://github.com/Exonymos/ShowTrackr-Web.git
    ```

5.  Navigate into the cloned directory:

    ```bash
    cd ShowTrackr-Web
    ```

## Setup Steps

These steps assume you are in the project's root directory (`ShowTrackr-Web`) in your terminal.

**Recommended: Using Setup Scripts (Easiest)**

The project includes convenience scripts to automate the setup process (creating the virtual environment and installing requirements):

- **Linux/macOS:**

  ```bash
  chmod +x setup.sh  # Make executable (only need to do once)
  ./setup.sh
  ```

- **Windows:**

  ```bash
  setup.bat
  ```

After running the setup script, **you still need to perform Step 3 (Configure `.env`) manually.** Remember to activate the virtual environment (`source .venv/bin/activate` or `.\.venv\Scripts\activate`) before running the application.

---

**Manual Setup (If you prefer to do it yourself)**

**1. Create and Activate Virtual Environment (Highly Recommended)**

A virtual environment keeps the project's dependencies separate from your global Python installation.

- **Create:**

  ```bash
  python -m venv .venv
  ```

  (If `python` doesn't work, try `python3`)

- **Activate:**

  - **Windows (Command Prompt):** `.\.venv\Scripts\activate.bat`
  - **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
    (If you get an execution policy error, run PowerShell as Administrator and execute: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`. Then try activating again.)
  - **Linux:** `source .venv/bin/activate`

  You should see `(.venv)` at the beginning of your terminal prompt after activation.

**2. Install Dependencies**

Ensure your virtual environment is active. Then run:

```bash
pip install -r requirements.txt
```

This command reads the `requirements.txt` file and installs all the necessary Python libraries (Flask, SQLAlchemy, HTMX, etc.) into your virtual environment.

**3. Configure Environment Variables (`.env` file)**

The application needs a secret key for security. This is stored in a `.env` file within the `data/` directory.

- **Navigate to `data/`:** If the `data` directory doesn't exist, create it.
- **Create `.env`:** Create a file named exactly `.env` (note the leading dot) inside the `data/` directory.
- **Add Content:** Copy and paste the following into the `.env` file:

  ```dotenv
  # Flask Secret Key (Required)
  # IMPORTANT: Replace with a strong, unique secret key!
  SECRET_KEY='YOUR_SUPER_SECRET_KEY_HERE'

  # Flask App Configuration
  FLASK_APP=src/watchlist

  # Flask Debug Mode
  # IMPORTANT: Set FLASK_DEBUG=False for production/deployment!
  FLASK_DEBUG=True

  # Database URL
  # Path relative to the src/watchlist directory where Flask runs
  DATABASE_URL=sqlite:///../data/database.db

  # Feedback URL
  GOOGLE_APPS_SCRIPT_FEEDBACK_URL='https://script.google.com/macros/s/AKfycbwgakVifq4XkMRUMYvcRuR3083z6tn4cmjx7kwQCn5zNBwGJxEObKf5zGTI5an0A2rwvQ/exec'
  GOOGLE_SHEET_PUBLIC_URL='https://docs.google.com/spreadsheets/d/1OW1PQTpdOcJK3bWLHsjkNuHZBkXp_RpLMel4IlDMrLg'
  ```

- **Generate Secret Key:** Replace `'YOUR_SUPER_SECRET_KEY_HERE'` with a strong, random key. You can generate one using Python in your terminal:

  ```bash
  python -c "import secrets; print(secrets.token_hex(24))"
  ```

  Copy the output and paste it between the single quotes for `SECRET_KEY=`. It should look something like this:

  ```dotenv
  SECRET_KEY='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
  ```

- **Security:** The `.gitignore` file is configured to prevent the `data/` directory (including `.env` and your database) from being accidentally committed to Git. **Never share your `.env` file or commit it to version control.**

**4. Initialize the Database (First Time Only)**

If this is your first time setting up the project, you need to initialize the database and create the tables:

Make sure you have activated your virtual environment and set the environment variables.

- **Check if `.venv` is active:** You should see `(.venv)` at the beginning of your terminal prompt. If not, activate it using the command from [Step 1](#setup-steps).
- **Set environment variables:**

  - **Windows (Command Prompt):** `set FLASK_APP=src/watchlist`
  - **Windows (PowerShell):** `$env:FLASK_APP="src/watchlist"`
  - **Linux:** `export FLASK_APP="src/watchlist"`

- **If the `migrations/` folder does not exist, run:**

  ```bash
  flask db init
  ```

- **Create the initial migration:**

  ```bash
  flask db migrate -m "Initial migration"
  ```

- **Apply the migration to create the tables:**

  ```bash
  flask db upgrade
  ```

You only need to run these commands once for a new setup, or after changing the database models.

---

Setup is complete! You can now proceed to [Running the Application](./running.md).
