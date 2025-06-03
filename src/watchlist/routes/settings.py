# src/watchlist/routes/settings.py
from flask import (
    Blueprint,
    render_template,
    session,
    request,
    make_response,
    current_app,
    url_for,
    redirect,
    send_file,
    flash,
)
from .. import config, db
from sqlalchemy.exc import SQLAlchemyError
from ..models import WatchlistItem
import json
from datetime import datetime, date, timezone
import io

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

ALLOWED_EXTENSIONS = {"json"}


# --- Helper Functions ---
def _allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[0] != ""
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def _validate_uploaded_file(request_files):
    """Validates the uploaded file."""
    if "backup_file" not in request_files:
        flash("No file part in the request.", "error")
        return None
    file = request_files["backup_file"]
    if file.filename == "":
        flash("No file selected for uploading.", "warning")
        return None
    if not file or not _allowed_file(file.filename):
        flash("Invalid file type. Please upload a .json file.", "error")
        return None
    return file


def _parse_imported_rating(raw_rating, item_title_for_log):
    """Parses and validates rating from imported item."""
    if raw_rating is None:
        return None
    try:
        item_rating_int = int(raw_rating)
        if 1 <= item_rating_int <= 10:
            return item_rating_int
        else:
            current_app.logger.warning(
                f"Rating {raw_rating} out of range for item '{item_title_for_log}'. Setting to None."
            )
            return None
    except ValueError:
        current_app.logger.warning(
            f"Invalid rating format '{raw_rating}' for item '{item_title_for_log}'. Setting to None."
        )
        return None


def _parse_imported_year(raw_year, item_title_for_log):
    """Parses and validates year from imported item."""
    if raw_year is None:
        return None
    try:
        item_year_int = int(raw_year)
        if 1800 <= item_year_int <= 2050:
            return item_year_int
        else:
            current_app.logger.warning(
                f"Year {raw_year} out of range for item '{item_title_for_log}'. Setting to None."
            )
            return None
    except ValueError:
        current_app.logger.warning(
            f"Invalid year format '{raw_year}' for item '{item_title_for_log}'. Setting to None."
        )
        return None


def _process_imported_item(raw_item: dict, items_skipped_list: list):
    """
    Processes a single raw item from the imported JSON data.
    Returns a WatchlistItem instance or None if skipped.
    Modifies items_skipped_list by reference if an item is skipped.
    """
    item_title_for_log = raw_item.get("title", "N/A")

    if not raw_item.get("title") or not raw_item.get("type"):
        items_skipped_list[0] += 1
        current_app.logger.warning(
            f"Skipping item due to missing title or type: {item_title_for_log}"
        )
        return None

    item_rating = _parse_imported_rating(raw_item.get("rating"), item_title_for_log)
    item_year = _parse_imported_year(raw_item.get("year"), item_title_for_log)

    new_item = WatchlistItem(
        title=raw_item.get("title"),
        type=raw_item.get("type"),
        year=item_year,
        tmdb_id=raw_item.get("tmdb_id"),
        imdb_id=raw_item.get("imdb_id"),
        boxd_id=raw_item.get("boxd_id"),
        overview=raw_item.get("overview"),
        poster_url=raw_item.get("poster_url"),
        status=raw_item.get("status", "Watched"),  # Default to Watched
        rating=item_rating,
        notes=raw_item.get("notes"),
    )

    # Date Added
    raw_date_added = raw_item.get("date_added")
    if raw_date_added:
        try:
            new_item.date_added = datetime.fromisoformat(raw_date_added)
        except ValueError:
            new_item.date_added = datetime.now(timezone.utc)
    else:
        new_item.date_added = datetime.now(timezone.utc)

    # Date Watched
    raw_date_watched = raw_item.get("date_watched")
    if raw_date_watched:
        try:
            new_item.date_watched = date.fromisoformat(raw_date_watched)
        except ValueError:
            new_item.date_watched = None  # Explicitly set to None on error
    else:
        new_item.date_watched = None

    return new_item


# --- Routes ---


@settings_bp.route("/", methods=["GET"])
def show_settings():
    """Display the settings page."""
    current_pagination_size = session.get(
        "pagination_size", config.DEFAULT_ITEMS_PER_PAGE
    )
    return render_template(
        "settings.html",
        valid_themes=config.VALID_THEMES,
        valid_pagination_sizes=config.VALID_PAGINATION_SIZES,
        current_pagination_size=current_pagination_size,
    )


@settings_bp.route("/set_theme", methods=["POST"])
def set_theme():
    """Set the theme using HTMX POST request."""
    theme = request.form.get("theme")
    if theme in config.VALID_THEMES:
        session["theme"] = theme
        current_app.logger.info(f"Theme set to: {theme}")
        response = make_response("", 200)
        response.headers["HX-Refresh"] = "true"
        return response
    else:
        current_app.logger.warning(f"Invalid theme selected: {theme}")
        return "Invalid theme", 400


@settings_bp.route("/set_pagination_size", methods=["POST"])
def set_pagination_size():
    """Set the number of items per page using HTMX POST."""
    try:
        size = int(request.form.get("pagination_size"))
        if size in config.VALID_PAGINATION_SIZES:
            session["pagination_size"] = size
            current_app.logger.info(f"Pagination size set to: {size}")
            response = make_response("", 200)
            response.headers["HX-Trigger"] = "loadWatchlist"
            response.headers["X-HX-Alert"] = f"Items per page set to {size}."
            response.headers["X-HX-Alert-Type"] = "success"
            return response
        else:
            current_app.logger.warning(f"Invalid pagination size selected: {size}")
            resp = make_response("Invalid size", 400)
            resp.headers["X-HX-Alert"] = "Invalid pagination size selected."
            resp.headers["X-HX-Alert-Type"] = "error"
            return resp
    except (ValueError, TypeError):
        current_app.logger.warning("Non-integer pagination size submitted.")
        resp = make_response("Invalid input", 400)
        resp.headers["X-HX-Alert"] = "Invalid pagination size input."
        resp.headers["X-HX-Alert-Type"] = "error"
        return resp


@settings_bp.route("/export_data", methods=["GET"])
def export_data_json():
    """Exports all watchlist items as a JSON file."""
    try:
        items = WatchlistItem.query.all()
        data_to_export = []
        for item in items:
            item_dict = {
                "title": item.title,
                "type": item.type,
                "year": item.year,
                "tmdb_id": item.tmdb_id,
                "imdb_id": item.imdb_id,
                "boxd_id": item.boxd_id,
                "overview": item.overview,
                "poster_url": item.poster_url,
                "status": item.status,
                "rating": item.rating,
                "notes": item.notes,
                "date_added": item.date_added.isoformat() if item.date_added else None,
                "date_watched": (
                    item.date_watched.isoformat() if item.date_watched else None
                ),
            }
            data_to_export.append(item_dict)

        json_data = json.dumps(data_to_export, indent=2)

        # Create a string IO buffer
        str_io = io.StringIO()
        str_io.write(json_data)
        str_io.seek(0)

        # Create a BytesIO buffer for send_file
        bytes_io = io.BytesIO(str_io.read().encode("utf-8"))
        bytes_io.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"showtrackr_backup_{timestamp}.json"

        return send_file(
            bytes_io,
            mimetype="application/json",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        current_app.logger.error(f"Error during data export: {e}", exc_info=True)
        flash("Error exporting data. Please check logs.", "error")
        return redirect(url_for("settings.show_settings"))


@settings_bp.route("/import_data", methods=["POST"])
def import_data_json():
    """Imports watchlist items from an uploaded JSON file, replacing existing data."""
    file = _validate_uploaded_file(request.files)
    if not file:
        return redirect(url_for("settings.show_settings"))

    try:
        json_data = file.read().decode("utf-8")
        imported_items_raw = json.loads(json_data)

        db.session.query(WatchlistItem).delete()  # CRITICAL: Delete existing items

        new_items_to_add = []
        items_skipped_list = [0]

        for raw_item in imported_items_raw:
            processed_item = _process_imported_item(raw_item, items_skipped_list)
            if processed_item:
                new_items_to_add.append(processed_item)

        if new_items_to_add:  # Only add if there are items, to avoid empty add_all call
            db.session.add_all(new_items_to_add)
        db.session.commit()

        success_msg = f"{len(new_items_to_add)} items imported successfully."
        if items_skipped_list[0] > 0:
            success_msg += f" {items_skipped_list[0]} items were skipped due to missing/invalid data."
        flash(success_msg, "success")

    except json.JSONDecodeError:
        flash("Invalid JSON file. Please upload a valid backup.", "error")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error during import: {e}", exc_info=True)
        flash("Database error during import. Data rolled back.", "error")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during data import: {e}", exc_info=True)
        flash(f"An unexpected error occurred during import: {str(e)}", "error")

    return redirect(url_for("settings.show_settings"))
