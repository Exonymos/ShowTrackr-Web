<div align="center">

# ShowTrackr

**Track your shows and movies with ease!**

[![License: GPL v3](https://img.shields.io/github/license/Exonymos/showtrackr-web?color=brightgreen)](https://opensource.org/licenses/GPL-3.0)
[![GitHub issues](https://img.shields.io/github/issues/Exonymos/showtrackr-web)](https://github.com/Exonymos/showtrackr-web/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/Exonymos/showtrackr-web)](https://github.com/Exonymos/showtrackr-web/commits/main)
<br>
[![GitHub Repo stars](https://img.shields.io/github/stars/Exonymos/showtrackr-web?style=social)](https://github.com/Exonymos/showtrackr-web/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Exonymos/showtrackr-web?style=social)](https://github.com/Exonymos/showtrackr-web/network/members)

ShowTrackr is a simple, personal, locally-run web application designed to help you keep track of movies and TV shows you want to watch or have already watched. It focuses on manual entry, giving you full control over your watchlist data without relying on external services. Built with Flask, HTMX, and DaisyUI.

</div>

## Table of Contents

- [ShowTrackr](#showtrackr)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [Previews](#previews)
  - [Getting Started](#getting-started)
    - [Quick Start](#quick-start)
    - [Detailed Setup](#detailed-setup)
  - [Running the Application](#running-the-application)
  - [Contributing](#contributing)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)

## Overview

ShowTrackr provides a private, free, and straightforward way to manage your media watchlist directly on your own computer. No cloud accounts, no tracking, just your list.

It uses a modern web stack (Python/Flask backend, HTMX for dynamic frontend updates without page reloads) and is styled with Tailwind CSS and DaisyUI for a clean and themeable interface. Data is stored locally in a simple SQLite database file.

➡️ **Learn more about [Features](https://github.com/Exonymos/ShowTrackr-Web/wiki/Features)**

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Key Features

- **Manual Entry:** Add Movies/TV Shows with details (Title, Type, Year, Status, Rating, Dates, IDs, Notes, Poster).
- **Dynamic List View:** Browse your watchlist with date grouping, poster previews, star ratings, and quick links.
- **Filtering:** Narrow down your list by Status, Type, Release Year, and Rating Range.
- **Sorting:** Order your list by Date Watched/Added, Title, Year, or Rating (Asc/Desc).
- **Pagination:** Configurable items per page and direct page input.
- **Editing & Deleting:** Full control over your entries via a modal interface.
- **Themeable:** Choose from various DaisyUI themes.
- **Local First:** All data stays on your machine in `data/database.db`.

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Previews

![ShowTrackr Preview](https://raw.githubusercontent.com/Exonymos/ShowTrackr-Web/refs/heads/main/previews/home_cupcake_1.png "Home Page - Cupcake Theme")

More previews are available in the [Previews folder](./previews/).

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Getting Started

### Quick Start

For users familiar with Python and virtual environments:

1.  Clone/Download the repository.
2.  Navigate to the project directory.
3.  Run the setup script for your OS (`./setup.sh` or `.\setup.bat`).
4.  Configure `data/.env` (especially `SECRET_KEY`).
5.  Run the application script (`./run.sh` or `.\run.bat` or `python run.py`).
6.  Access in your browser (usually `http://127.0.0.1:5000`).

### Detailed Setup

For detailed step-by-step instructions covering Python installation, virtual environments, dependencies, and configuration, please see:

➡️ **[Detailed Setup Guide](https://github.com/Exonymos/ShowTrackr-Web/wiki/Setup)**

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Running the Application

Once set up, run the application using the provided scripts. They handle activating the environment (if needed), applying database migrations, and starting the web server.

➡️ **[Running the Application Guide](https://github.com/Exonymos/ShowTrackr-Web/wiki/Running)**

Access the application by opening `http://127.0.0.1:5000` (or the address shown in your terminal) in your web browser.

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Exonymos/showtrackr-web/issues).

Please read the contribution guidelines before submitting pull requests:

➡️ **[Contribution Guidelines](./CONTRIBUTING.md)**

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## License

This project is distributed under the **GNU General Public License v3.0**.

See [LICENSE](./LICENSE) for more information.

<p align="right">(<a href="#showtrackr">back to top</a>)</p>

## Acknowledgements

ShowTrackr is built using several fantastic open-source projects:

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [HTMX](https://htmx.org/)
- [SQLite](https://www.sqlite.org/)
- [SQLAlchemy](https://sqlalchemy.org/) / [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Alembic](https://alembic.sqlalchemy.org/) / [Flask-Migrate](https://flask-migrate.readthedocs.io/)
- [Tailwind CSS](https://tailwindcss.com/)
- [DaisyUI](https://daisyui.com/)
- [Simple Icons](https://simpleicons.org/)

<p align="right">(<a href="#showtrackr">back to top</a>)</p>
