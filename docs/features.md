# ShowTrackr - Features Guide

This document details the core features of ShowTrackr (as of v0.3.0).

## 1. Main Interface

- **Header:** Displays the application name ("ShowTrackr") and provides a link back to the main page. Contains a Settings icon (⚙️) linking to the Settings page. The header remains fixed at the top as you scroll.
- **Welcome Section:** Greets the user and provides quick access to adding new items via the prominent "Add Item" button. Also includes a theme selector dropdown for quick visual changes.
- **Controls Bar:** Located below the welcome section (and hidden on Settings/About pages). Contains:
  - **Filters Dropdown:** Filter your watchlist by Status, Type, Release Year, and Rating Range. An indicator dot appears if any filters are active.
  - **Search Bar:** Quickly search your watchlist by title. Includes a clear button and supports <kbd>Ctrl</kbd> + <kbd>K</kbd> to focus the search input instantly.
  - **Sort Dropdown:** Sort your watchlist by Date Watched, Date Added, Title, Release Year, or Rating. Clicking the same sort toggles between ascending and descending. Sorting is case-insensitive for titles and places items with missing data last.
- **Watchlist Area:** The main section where your tracked movies and TV shows are displayed in a list format.
- **Footer:** Contains the application name, motto, etc. It includes links for the project's repository and the About page.

## 2. Adding & Editing Items

- **Access:** Click the "Add Item" button in the welcome section or the "Edit" icon (📝) next to an existing item in the watchlist. Both actions open a modal window.
- **Modal Form:** Allows manual input/editing of all item details:
  - **Title:** (Required) The name of the movie or show.
  - **Type:** (Required) Select "Movie" or "TV Show".
  - **Release Year:** Optional year of release.
  - **Status:** (Required) "Watched" or "Plan to Watch" (defaults to "Watched" for new items).
  - **Rating:** Optional rating from 1 to 10 (displayed as stars in the list).
  - **Date Watched:** Optional date (YYYY-MM-DD) when the item was watched. Used for display and sorting.
  - **Overview:** Optional brief summary.
  - **Poster URL:** Optional direct URL to an image poster. If blank, a placeholder ("Movie"/"TV") is shown.
  - **External IDs:** Optional IDs for IMDb (e.g., `tt1234567`), TMDb (e.g., `12345`), and Letterboxd (e.g., `abcd`) used for generating quick links.
  - **Notes:** Optional personal notes or reminders.
- **Saving:** Click "Save Item". The data is saved to the local database via an HTMX request, the modal closes, and the watchlist updates automatically. A success toast notification appears.
- **Canceling:** Click "Cancel" or the "✕" icon to close the modal without saving.
- **Unsaved Changes Warning:** If you modify the form and try to close the modal without saving, a confirmation prompt will appear.
- **Deleting:** When editing an existing item, a "Delete" button is available. Clicking it prompts for confirmation before permanently removing the item from the database via HTMX.

## 3. Viewing the Watchlist

- **Layout:** Items are displayed in a list view.
- **Columns:**
  - **Month/Day:** Shows the month (MMM) and year (YYYY) stacked, followed by the day (DD) in a larger font. This primarily uses the "Date Watched". If "Date Watched" is not set, it falls back to "Date Added". Dates are grouped visually; the Month/Year block is only shown if it's different from the row above (when sorted by date).
  - **Poster:** Displays the poster image if a URL was provided. Hovering over the poster shows a larger preview tooltip. Otherwise, a placeholder with "Movie" or "TV" is shown.
  - **Title:** The item's title (clickable to open the edit modal).
  - **Year:** The release year.
  - **Rating:** Displays the rating numerically followed by a star icon (e.g., "8 ⭐").
  - **Link:** Displays the highest priority available external link icon (IMDb > Letterboxd > TMDb) if the corresponding ID was entered. Clicking the icon opens the external site in a new tab.
  - **Edit:** An edit icon (📝) to open the edit modal for that item.
- **Pagination:**
  - Items are displayed in pages (default 15 items per page, configurable in Settings).
  - Controls (`< Prev | Page X of Y | Next >`) appear below the list.
  - Clicking Prev/Next loads the respective page via HTMX.
  - You can directly type a page number into the input field and press Enter to jump to that page.

## 4. Filtering, Searching, and Sorting

- **Filters:** Filter your watchlist by Status (All, Watched, Plan to Watch), Type (All, Movies, TV Shows), Release Year (checkboxes), and Rating Range (min/max).
- **Search:** Instantly search your watchlist by title using the search bar in the controls bar. Use <kbd>Ctrl</kbd> + <kbd>K</kbd> to focus the search input. Clear the search with a single click.
- **Sort:** Sort your watchlist by Date Watched, Date Added, Title, Release Year, or Rating. Sorting is case-insensitive for titles and places items with missing data last. Toggle sort direction by clicking the same sort option.

## 5. Settings Page

- Accessed via the Settings icon (⚙️) in the header.
- **Theme Selector:** Choose from a wide range of DaisyUI themes. The entire UI updates instantly on selection.
- **Pagination Size:** Select the number of items to display per page (10, 15, 20, 30, 40, 50). Changes take effect on the next watchlist load (e.g., navigating pages or applying filters/sorts).
- **Database Management:**
  - **Export Data:** Download your entire watchlist as a JSON backup file.
  - **Import Data:** Restore your watchlist from a previously exported JSON file. The app validates imported data and skips any invalid entries, providing clear error messages for malformed files or data.
  - **Error Handling:** Improved feedback and error messages for invalid imports or file types.
- **Validation:** Additional validation for pagination size and theme selection.

## 6. About Page

- Accessed via the Info icon (ℹ️) link in the footer.
- Displays information using tabs:
  - **About:** Project description, purpose, creator, version, features, technology credits.
  - **Changelog:** Version history using a timeline format, with each version's changes described in plain language.
  - **Feedback:** Submit feedback directly from the app, including a form that sends feedback to a public Google Sheet. Optionally includes basic browser/OS info for debugging.
