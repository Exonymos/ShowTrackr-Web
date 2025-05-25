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
        current_app.logger.error(f"Error during data export: {e}")
        flash("Error exporting data. Please check logs.", "error")
        return redirect(url_for("settings.show_settings"))


ALLOWED_EXTENSIONS = {"json"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[0] != ""
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@settings_bp.route("/import_data", methods=["POST"])
def import_data_json():
    """Imports watchlist items from an uploaded JSON file, replacing existing data."""
    if "backup_file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for("settings.show_settings"))

    file = request.files["backup_file"]

    if file.filename == "":
        flash("No file selected for uploading.", "warning")
        return redirect(url_for("settings.show_settings"))

    if file and allowed_file(file.filename):
        try:
            # Read and parse the JSON file
            json_data = file.read().decode("utf-8")
            imported_items_raw = json.loads(json_data)

            # CRITICAL: Delete existing items
            db.session.query(WatchlistItem).delete()

            new_items_to_add = []
            items_skipped = 0

            for raw_item in imported_items_raw:
                # Basic validation for required fields
                if not raw_item.get("title") or not raw_item.get("type"):
                    items_skipped += 1
                    current_app.logger.warning(
                        f"Skipping item due to missing title or type: {raw_item.get('title', 'N/A')}"
                    )
                    continue

                # rating and year validation
                raw_rating = raw_item.get("rating")
                item_rating = None
                if raw_rating is not None:
                    try:
                        item_rating_int = int(raw_rating)
                        if 1 <= item_rating_int <= 10:
                            item_rating = item_rating_int
                        else:
                            current_app.logger.warning(
                                f"Rating {raw_rating} out of range for item '{raw_item.get('title', 'N/A')}'. Setting to None."
                            )
                    except ValueError:
                        current_app.logger.warning(
                            f"Invalid rating format '{raw_rating}' for item '{raw_item.get('title', 'N/A')}'. Setting to None."
                        )

                raw_year = raw_item.get("year")
                item_year = None
                if raw_year is not None:
                    try:
                        item_year_int = int(raw_year)
                        if 1800 <= item_year_int <= 2050:
                            item_year = item_year_int
                        else:
                            current_app.logger.warning(
                                f"Year {raw_year} out of range for item '{raw_item.get('title', 'N/A')}'. Setting to None."
                            )
                    except ValueError:
                        current_app.logger.warning(
                            f"Invalid year format '{raw_year}' for item '{raw_item.get('title', 'N/A')}'. Setting to None."
                        )

                new_item = WatchlistItem(
                    title=raw_item.get("title"),
                    type=raw_item.get("type"),
                    year=item_year,
                    tmdb_id=raw_item.get("tmdb_id"),
                    imdb_id=raw_item.get("imdb_id"),
                    boxd_id=raw_item.get("boxd_id"),
                    overview=raw_item.get("overview"),
                    poster_url=raw_item.get("poster_url"),
                    status=raw_item.get("status", "Watched"),
                    rating=item_rating,
                    notes=raw_item.get("notes"),
                )

                if raw_item.get("date_added"):
                    try:
                        new_item.date_added = datetime.fromisoformat(
                            raw_item.get("date_added")
                        )
                    except ValueError:
                        new_item.date_added = datetime.now(timezone.utc)
                else:
                    new_item.date_added = datetime.now(timezone.utc)

                if raw_item.get("date_watched"):
                    try:
                        new_item.date_watched = date.fromisoformat(
                            raw_item.get("date_watched")
                        )
                    except ValueError:
                        new_item.date_watched = None

                new_items_to_add.append(new_item)

            db.session.add_all(new_items_to_add)
            db.session.commit()

            success_msg = f"{len(new_items_to_add)} items imported successfully."
            if items_skipped > 0:
                success_msg += (
                    f" {items_skipped} items were skipped due to missing data."
                )
            flash(success_msg, "success")

        except json.JSONDecodeError:
            flash("Invalid JSON file. Please upload a valid backup.", "error")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error during import: {e}")
            flash("Database error during import. Data rolled back.", "error")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during data import: {e}")
            flash(f"An unexpected error occurred during import: {str(e)}", "error")

        return redirect(url_for("settings.show_settings"))
    else:
        flash("Invalid file type. Please upload a .json file.", "error")
        return redirect(url_for("settings.show_settings"))
