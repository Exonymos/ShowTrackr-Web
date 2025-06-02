# Contributing to ShowTrackr

Thank you for considering contributing to ShowTrackr! We appreciate your help in making this project better. Your contributions help us create a more robust, reliable, and feature-rich application for everyone.

## How to Contribute

There are many ways to contribute, from reporting bugs to writing code:

1.  **Reporting Issues:**

    - If you find a bug, have a suggestion, or want to request a feature, please check the [Issues Page](https://github.com/Exonymos/showtrackr-web/issues) first to see if a similar item already exists.
    - If not, please [open a new issue](https://github.com/Exonymos/showtrackr-web/issues/new/choose), providing as much detail as possible. For bugs, include steps to reproduce, expected behavior, and actual behavior. For features, describe the problem your feature solves and how it might work.

2.  **Suggesting Enhancements:**

    - For new features or improvements to existing functionality, you can also start a discussion on the [Ideas Discussions page](https://github.com/Exonymos/ShowTrackr-Web/discussions/categories/ideas).

3.  **Pull Requests (Code Contributions):**
    - If you'd like to contribute code, please follow these steps:
      - **Fork the Repository:** Create your own copy of the ShowTrackr repository on GitHub.
      - **Create a Branch:** Create a descriptive branch name for your feature or bug fix from the `main` branch (e.g., `git checkout -b feature/new-keywords` or `git checkout -b fix/export-error-message`).
      - **Set Up Development Environment:** Follow the [Development Setup](#development-setup) section below.
      - **Make Changes:** Write your code, ensuring it adheres to the project's coding standards and style (see [Coding Standards & Quality](#coding-standards--quality)).
      - **Test Your Changes:** Add relevant tests for any new functionality or bug fixes. Ensure all tests pass by running `pytest`.
      - **Run Linters and Formatters:** Ensure your code is clean by running the tools described in [Coding Standards & Quality](#coding-standards--quality).
      - **Commit Changes:** Commit your work with clear and concise commit messages, following conventional commit a DCO sign-off (`git commit -s -m "feat: Add new keywords"`).
      - **Push to Your Fork:** Push your branch to your forked repository on GitHub (e.g., `git push origin feature/add-new-keywords`).
      - **Open a Pull Request:** Go to the original ShowTrackr repository on GitHub and open a pull request from your branch to the `main` branch of the ShowTrackr repository. Provide a clear description of your changes, why they were made, and link to any relevant issues.

## Development Setup

1.  **Prerequisites:** Ensure you have Python (3.10+), Node.js (LTS), and npm installed.
2.  **Fork and Clone:** Fork the repository and clone your fork locally.
3.  **Follow the Detailed [Setup Guide](./docs/setup.md):** This guide will walk you through:
    - Creating a Python virtual environment (`.venv`).
    - Installing Python application dependencies from `requirements.txt`.
    - Setting up the `.env` file and initializing the database.
4.  **Install Development Dependencies:**
    - Install Python development dependencies, make sure you are in the root directory of the project and your virtual environment is activated:
      ```bash
      pip install -r requirements-dev.txt
      ```
    - Install JavaScript development dependencies:
      ```bash
      npm install
      ```
5.  **Running the Application:** Refer to the [Run Guide](./docs/running.md).

## Coding Standards & Quality

To maintain code quality and consistency, we use several tools. Please ensure your contributions adhere to these standards by running the tools locally before submitting a pull request.

### Python (Backend)

- **Linting (Flake8):** Checks for PEP 8 compliance, errors, and complexity.
  - Configuration: `.flake8`
  - Run: `flake8 src tests run.py setup.py make_release.py`
- **Formatting (Black):** Enforces a consistent code style.
  - Configuration: `pyproject.toml`
  - Check: `black --diff --color .`
  - Apply: `black .`
- **Type Checking (Pyright):** Static type analysis.
  - Configuration: `pyproject.toml`
  - Run: `pyright`
  - _Note: The project will gradually adopt type hints. Aim to add type hints for new code and address Pyright warnings where feasible._
- **Security Analysis (Bandit):** Checks for common security vulnerabilities.
  - Run: `bandit -r -ll -ii --exclude "./migrations,./.venv" src tests run.py setup.py`
- **Test Coverage (Coverage.py):** Ensure tests cover your changes.
  - Configuration: `.coveragerc`
  - Run: `pytest --cov=src/watchlist --cov-report=term-missing --cov-report=html`
  - Review the HTML report in `coverage_html_report/index.html`.

### CSS (Frontend)

- **Building:** Minifies and Optimizes CSS files.
  - Build: `npm run build:css`
  - Watch for changes: `npm run watch:css`
  - This will generate the final CSS files in the appropriate directories.

### JavaScript (Frontend)

- **Building:** Minifies JavaScript files and bundles them.
  - Build: `npm run build:js`
  - Watch for changes: `npm run watch:js`
  - This will generate the final JavaScript files in the appropriate directories.
- **Linting (ESLint) & Formatting (Prettier):** For code quality and consistent style.
  - Configuration: `eslint.config.mjs`, `.prettierrc.js`, `.prettierignore`
  - Check: `npm run lint:js` and `npm run format:check`
  - Apply fixes/formatting: `npm run lint:js:fix` then `npm run format:write`

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Questions?

If you have questions about contributing, the codebase, or the tools used, feel free to open an issue and tag it as a "question", or ask in the [Discussions section](https://github.com/Exonymos/ShowTrackr-Web/discussions).

Thank you for your contribution!
