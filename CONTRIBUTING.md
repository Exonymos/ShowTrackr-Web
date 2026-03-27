# Contributing to SeriesScape

Thank you for considering contributing to SeriesScape! We appreciate your help in making this project better. Your
contributions help us create a more robust, reliable, and feature-rich application for everyone.

## How to Contribute

There are many ways to contribute, from reporting bugs to writing code:

1. **Reporting Issues:**
    - If you find a bug, have a suggestion, or want to request a feature, please check
      the [Issues Page](https://github.com/Exonymos/SeriesScape/issues) first to see if a similar item already exists.
    - If not, please [open a new issue](https://github.com/Exonymos/SeriesScape/issues/new/choose), providing as much
      detail as possible. For bugs, include steps to reproduce, expected behavior, and actual behavior. For features,
      describe the problem your feature solves and how it might work.

2. **Suggesting Enhancements:**
    - For new features or improvements to existing functionality, you can also start a discussion on
      the [Ideas Discussions page](https://github.com/Exonymos/SeriesScape/discussions/categories/ideas).

3. **Pull Requests (Code Contributions):**
    - If you'd like to contribute code, please follow these steps:
        - **Fork the Repository:** Create your own copy of the SeriesScape repository on GitHub.
        - **Create a Branch:** Create a descriptive branch name for your feature or bug fix from the `main` branch (
          e.g., `git checkout -b feature/new-keywords` or `git checkout -b fix/export-error-message`).
        - **Set Up Development Environment:** Follow the [Development Setup](#development-setup) section below.
        - **Make Changes:** Write your code, ensuring it adheres to the project's coding standards and style (
          see [Coding Standards & Quality](#coding-standards--quality)).
        - **Test Your Changes:** Add relevant tests for any new functionality or bug fixes. Ensure all tests pass by
          running `pytest`.
        - **Run Linters and Formatters:** Ensure your code is clean by running the tools described
          in [Coding Standards & Quality](#coding-standards--quality).
        - **Commit Changes:** Commit your work with clear and concise commit messages following conventional commits (
          e.g., `feat: Add new keywords`, `fix: Correct export error message`).
        - **Push to Your Fork:** Push your branch to your forked repository on GitHub (e.g.,
          `git push origin feature/add-new-keywords`).
        - **Open a Pull Request:** Go to the original SeriesScape repository on GitHub and open a pull request from your
          branch to the `main` branch. Provide a clear description of your changes, why they were made, and link to any
          relevant issues.

## Development Setup

1. **Prerequisites:** Ensure you have Python 3.10+ and [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
   installed. `uv` manages the virtual environment and all Python dependencies automatically.
2. **Fork and Clone:** Fork the repository and clone your fork locally.
3. **Install all dependencies** (creates the virtual environment automatically):
   ```bash
   uv sync
   ```
4. **Install JavaScript dependencies** (requires [pnpm](https://pnpm.io/installation)):
   ```bash
   pnpm install
   ```
5. **Follow the [Setup Guide](./docs/setup.md)** for `.env` creation and database initialisation. Running
   `scripts/setup.bat` (Windows) or `scripts/setup.sh` (Linux/macOS) after `uv sync` handles this automatically.
6. **Running the Application:** Refer to the [Run Guide](./docs/running.md).

## Coding Standards & Quality

To maintain code quality and consistency, we use several tools. Please ensure your contributions adhere to these
standards before submitting a pull request.

### Python (Backend)

- **Linting & Formatting (Ruff):** Handles both linting (PEP 8 compliance, errors, imports) and formatting in one tool.
    - Configuration: `pyproject.toml` (`[tool.ruff]`)
    - Check: `uv run ruff check .`
    - Apply fixes: `uv run ruff check --fix .`
    - Format: `uv run ruff format .`
- **Type Checking (Pyright / ty):** Static type analysis.
    - Configuration: `pyproject.toml`
    - Run Pyright: `uv run pyright`
    - Run ty: `uv run ty check`
    - _Note: The project is gradually adopting type hints. Aim to add type hints for new code._
- **Testing (pytest):**
    - Run all tests: `uv run pytest`
    - Run with coverage report: `uv run pytest --cov=apps/desktop/src/core --cov-report=term-missing`

### CSS (Frontend)

- **Building:** Minifies and optimises CSS.
    - Build: `pnpm run build:css`
    - Watch for changes: `pnpm run watch:css`

### JavaScript (Frontend)

- **Building:** Bundles and minifies JavaScript.
    - Build: `pnpm run build:js`
    - Watch for changes: `pnpm run watch:js`
- **Linting & Formatting (ESLint + Prettier):**
    - Check: `pnpm run lint:js` and `pnpm run format:check`
    - Apply fixes: `pnpm run lint:js:fix` then `pnpm run format:write`

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating
in this project, you agree to abide by its terms.

## Questions?

If you have questions about contributing, the codebase, or the tools used, feel free to open an issue and tag it as a "
question", or ask in the [Discussions section](https://github.com/Exonymos/SeriesScape/discussions).

Thank you for your contribution!
