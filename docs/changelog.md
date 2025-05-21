# ShowTrackr - Changelog

Version history for the ShowTrackr application.

---

## Table of Contents

- [0.3.0 - 2025-05-21](#030---2025-05-21)
- [0.2.1 - 2025-05-09](#021---2025-05-09)
- [0.2.0 - 2025-05-02](#020---2025-05-02)
- [0.1.1 - 2025-04-25](#011---2025-04-25)
- [0.1.0 - 2025-04-18](#010---2025-04-18)

---

## [[0.3.0]](https://github.com/Exonymos/ShowTrackr-Web/releases/tag/0.3.0) - 2025-05-21

### Added

- Data export and import functionality for watchlist items via the Settings page (JSON format).
- Comprehensive test suite for WatchlistItem model, settings, and item management routes.
- Extensive tests for data import/export, validation, and error handling.
- Additional validation for pagination size and theme selection in settings.
- Improved error handling and user feedback for invalid import files and malformed data.

### Changed

- Updated dependencies, including Flask upgraded to 3.1.1.
- Enhanced validation logic for watchlist item fields (year, rating, date formats).
- Improved setup scripts and documentation for environment and database initialization.
- Improved test coverage and reliability for settings and item routes.

### Fixed

- Fixed issues with invalid or missing data during import (skips and logs problematic items).
- Fixed error handling for malformed JSON and invalid file types during import.
- Fixed session and configuration handling in tests for more robust test isolation.
- Fixed minor issues in pagination and theme selection logic.

<div align="right">
  <a href="#table-of-contents">Back to Top</a>
</div>

---

## [[0.2.1]](https://github.com/Exonymos/ShowTrackr-Web/releases/tag/0.2.1) - 2025-05-09

### Added

- Search functionality for TV shows and movies by title.
- Shortcut key for search input field (Ctrl + K).
- Feedback form for users to share their thoughts on the application.
- Feedback collection in an online Google Sheet for easy access and management. You can view the feedback Google Sheet [here](https://docs.google.com/spreadsheets/d/1OW1PQTpdOcJK3bWLHsjkNuHZBkXp_RpLMel4IlDMrLg).

<div align="right">
  <a href="#table-of-contents">Back to Top</a>
</div>

---

## [[0.2.0]](https://github.com/Exonymos/ShowTrackr-Web/releases/tag/0.2.0) - 2025-05-02

### Added

- `date_watched` field to database model and add/edit form.
- Filtering functionality by Status, Type, Release Year (Checkboxes), and Rating Range via filter dropdown.
- Sorting functionality by Date Watched, Date Added, Title, Year, and Rating via sort dropdown.
- Ascending/Descending toggle for sorting options.
- Nulls-last logic for sorting nullable fields (Year, Rating, Date Watched).
- Out-of-Band (OOB) HTMX swaps to update filter/sort control UI dynamically.
- About page (`/about`) with tabs for About, Changelog, and Feedback sections.
- Changelog timeline using DaisyUI component.
- Info icon link in footer pointing to the About page.

### Changed

- Refactored watchlist loading route (`/load_watchlist`) to handle both HTMX partial requests and full page reloads correctly, fixing errors when refreshing pages with filter/sort parameters in the URL.
- Refactored some functions for better readability and maintainability.

### Fixed

- Filter "Reset" button functionality restored.
- Case-insensitive sorting for Titles.
- Corrected minor styling issues on About page tabs (`tabs-lifted`).
- Ensured filter/sort controls are hidden on the About page.

<div align="right">
  <a href="#table-of-contents">Back to Top</a>
</div>

---

## [0.1.1] - 2025-04-25

### Added

- List view now displays grouped Month/Day based primarily on `date_watched`.
- Visual star-based rating display (e.g., "8 ⭐").
- SVG icons for external quick links (IMDb, TMDb, Letterboxd).
- Poster hover tooltip showing a larger preview.
- User setting on Settings page to configure pagination size (10-50 items).
- Direct page number input in pagination controls.
- Custom 404 and 500 error page templates styled with DaisyUI.
- JavaScript warning prompt for unsaved changes when closing the add/edit modal.
- Favicon files (`.ico`, `.png`).
- "Inter" font via Google Fonts.
- Theme selector added to welcome section for quick access.

### Changed

- Updated project name to "ShowTrackr" and added motto.
- Updated footer layout using DaisyUI components and added creator/repo links.
- Refined overall color scheme to use theme-aware DaisyUI base colors instead of fixed colors.
- Improved list view column alignment (centering).
- Improved poster placeholder appearance (theme-aware background, "Movie"/"TV" text).
- Improved UI feedback using DaisyUI Toasts instead of browser alerts.
- Improved reliability of add/edit modal closing after successful save/delete.
- Changed default items per page from 20 to 15.

### Fixed

- Resolved `AttributeError: 'HTMX' object has no attribute 'on'` error by ensuring HTMX is correctly initialized.
- Corrected database `OperationalError` related to `NULLS LAST` syntax in SQLite by switching to `func.coalesce` for sorting.

<div align="right">
  <a href="#table-of-contents">Back to Top</a>
</div>

---

## [0.1.0] - 2025-04-18

### Added

- Initial project structure (Flask, Blueprints, `src/`, `data/`).
- Core dependencies (`Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-HTMX`, `python-dotenv`).
- Basic `WatchlistItem` database model.
- Database initialization and migration setup using Flask-Migrate.
- Core application setup in `src/watchlist/__init__.py`.
- Basic routes for main page (`/`), add/edit forms, saving, deleting.
- Templates: `base.html`, `index.html`, `_watchlist_items.html`, `_add_edit_item_form.html`, `settings.html`, `_form_error.html`.
- Functionality: Add, View (List), Edit, Delete items via HTMX modals.
- Basic list view layout mimicking user-provided image.
- Basic pagination controls (Prev/Next).
- Settings page with Theme switcher (Light, Cupcake, Dark, Dracula).
- Local SQLite database storage in `data/database.db`.
- Configuration via `data/.env` file (`SECRET_KEY`, `FLASK_APP`, etc.).

<div align="right">
  <a href="#table-of-contents">Back to Top</a>
</div>
