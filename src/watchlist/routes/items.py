# src/watchlist/routes/items.py
from flask import (
    Blueprint,
    render_template,
    request,
    make_response,
    current_app,
)
import unicodedata
from ..models import WatchlistItem
from .. import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

items_bp = Blueprint("items", __name__)


def safe_header_value(value):
    # Normalize and encode to latin-1
    if value is None:
        return ""
    return (
        unicodedata.normalize("NFKD", str(value))
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


@items_bp.route("/items/add/form", methods=["GET"])
def add_item_form():
    """Return the HTML form for adding a new item (for modal)."""
    return render_template("_add_edit_item_form.html", item=None)


@items_bp.route("/items/edit/form/<int:item_id>", methods=["GET"])
def edit_item_form(item_id):
    """Return the HTML form for editing an existing item (for modal)."""
    item = db.session.get(WatchlistItem, item_id)
    if not item:
        return "<p class='text-error'>Item not found.</p>", 404
    return render_template("_add_edit_item_form.html", item=item)


def _get_or_create_item(item_id_str):
    """Fetches an existing item or creates a new one."""
    if not item_id_str:
        return WatchlistItem(), True  # New item
    try:
        item_id = int(item_id_str)
        item = db.session.get(WatchlistItem, item_id)
        if not item:
            return None, False  # Item not found
        return item, False  # Existing item
    except ValueError:
        return None, False  # Invalid item_id format


def _parse_year(year_str, error_messages):
    """Parses and validates the year string."""
    if not year_str:
        return None
    if year_str.isdigit():
        year_val = int(year_str)
        if not (1800 <= year_val <= 2050):
            error_messages.append("Year must be between 1800 and 2050.")
            return None
        return year_val
    else:
        error_messages.append("Year must be a valid number.")
        return None


def _parse_rating(rating_str, error_messages):
    """Parses and validates the rating string."""
    if not rating_str:
        return None
    if rating_str.isdigit():
        rating_val = int(rating_str)
        if not (1 <= rating_val <= 10):
            error_messages.append("Rating must be between 1 and 10.")
            return None
        return rating_val
    else:
        error_messages.append("Rating must be a valid number.")
        return None


def _parse_date_watched(date_watched_str, error_messages):
    """Parses and validates the date_watched string."""
    if not date_watched_str:
        return None
    try:
        return date.fromisoformat(date_watched_str)
    except ValueError:
        error_messages.append("Invalid Date Watched format. Please use YYYY-MM-DD.")
        return None


def _apply_form_data_to_item(item, form_data, error_messages):
    """Applies validated form data to the WatchlistItem object."""
    item.title = form_data.get("title", "").strip()
    item.type = form_data.get("type")
    item.year = _parse_year(form_data.get("year", "").strip(), error_messages)
    item.overview = form_data.get("overview", "").strip() or None
    item.poster_url = form_data.get("poster_url", "").strip() or None
    item.status = form_data.get("status")
    item.rating = _parse_rating(form_data.get("rating", "").strip(), error_messages)
    item.notes = form_data.get("notes", "").strip() or None
    item.tmdb_id = form_data.get("tmdb_id", "").strip() or None
    item.imdb_id = form_data.get("imdb_id", "").strip() or None
    item.boxd_id = form_data.get("boxd_id", "").strip() or None
    item.date_watched = _parse_date_watched(
        form_data.get("date_watched", "").strip(), error_messages
    )

    # Basic Validation (Server-Side)
    if not item.title:
        error_messages.append("Title is required.")
    if item.type not in ["movie", "tv"]:
        error_messages.append("Invalid type selected.")
    if item.status not in [
        "Plan to Watch",
        "Watched",
    ]:
        error_messages.append("Invalid status selected.")


def _prepare_error_response(
    form_data, item_id_str, error_messages, original_item_date_watched_str=""
):
    """Prepares the HTTP response when validation errors occur."""
    # Re-create a temporary item with submitted data for form re-rendering
    form_render_item = WatchlistItem()
    if item_id_str:
        try:
            original_item = db.session.get(WatchlistItem, int(item_id_str))
            if original_item:
                form_render_item = original_item  # Use original as base
        except ValueError:
            pass

    # Populate with form data that was submitted
    form_render_item.title = form_data.get("title", "")
    form_render_item.type = form_data.get("type")
    form_render_item.year_str = form_data.get("year", "")
    form_render_item.overview = form_data.get("overview", "")
    form_render_item.poster_url = form_data.get("poster_url", "")
    form_render_item.status = form_data.get("status")
    form_render_item.rating_str = form_data.get("rating", "")
    form_render_item.notes = form_data.get("notes", "")
    form_render_item.tmdb_id = form_data.get("tmdb_id", "")
    form_render_item.imdb_id = form_data.get("imdb_id", "")
    form_render_item.boxd_id = form_data.get("boxd_id", "")
    form_render_item.date_watched_str = form_data.get(
        "date_watched", original_item_date_watched_str
    )

    resp = make_response(
        render_template(
            "_add_edit_item_form.html",
            item=form_render_item,
            errors=error_messages,
        ),
        400,
    )
    resp.headers["X-HX-Alert"] = "Please correct the errors below."
    resp.headers["X-HX-Alert-Type"] = "error"
    return resp


def _prepare_exception_response(
    form_data, item_id_str, exception_message, status_code=500, is_new_item_flag=False
):
    """Prepares the HTTP response for general exceptions."""
    current_app.logger.error(f"Error saving item: {exception_message}", exc_info=True)

    form_render_item = WatchlistItem()
    if not is_new_item_flag and item_id_str:
        try:
            item_from_db = db.session.get(WatchlistItem, int(item_id_str))
            if item_from_db:
                form_render_item = item_from_db
        except ValueError:
            pass

    # Repopulate with form data
    for key, value in form_data.items():
        if hasattr(form_render_item, key):
            setattr(form_render_item, key, value)
    form_render_item.date_watched_str = form_data.get("date_watched", "")
    form_render_item.year_str = form_data.get("year", "")
    form_render_item.rating_str = form_data.get("rating", "")

    error_list = [str(exception_message)]
    if status_code == 500 and "Database error" not in str(exception_message):
        error_list = ["Database error saving item. Please try again."]

    resp = make_response(
        render_template(
            "_add_edit_item_form.html",
            item=form_render_item,
            errors=error_list,
        ),
        status_code,
    )
    alert_message = (
        "Database error. Please try again."
        if status_code == 500
        else "Invalid data in form."
    )
    if "unexpected server error" in str(exception_message).lower():
        alert_message = "An unexpected server error occurred."

    resp.headers["X-HX-Alert"] = alert_message
    resp.headers["X-HX-Alert-Type"] = "error"
    return resp


@items_bp.route("/items/save", methods=["POST"])
def save_item():
    """Handle saving new or updated items via HTMX POST."""
    item_id_str = request.form.get("item_id")
    form_data = request.form.to_dict()
    error_messages = []

    item, is_new_item = _get_or_create_item(item_id_str)

    if item is None:
        return make_response("<p class='text-error'>Error: Item not found.</p>", 404)

    original_date_watched_str = (
        item.date_watched.isoformat()
        if item.date_watched and not is_new_item
        else form_data.get("date_watched", "")
    )

    try:
        _apply_form_data_to_item(item, form_data, error_messages)

        if error_messages:
            return _prepare_error_response(
                form_data, item_id_str, error_messages, original_date_watched_str
            )

        if is_new_item:
            db.session.add(item)
        db.session.commit()

        resp = make_response("", 200)
        resp.headers["HX-Trigger"] = "loadWatchlist"
        resp.headers["X-Close-Modal"] = "true"
        resp.headers["X-HX-Alert"] = safe_header_value(
            f"Item '{item.title}' saved successfully!"
        )
        resp.headers["X-HX-Alert-Type"] = "success"
        return resp

    except SQLAlchemyError as e:
        db.session.rollback()
        return _prepare_exception_response(
            form_data, item_id_str, f"Database error saving item: {e}", 500, is_new_item
        )
    except (
        ValueError
    ) as e:  # Catches potential errors from int() conversion if not handled by parsers
        db.session.rollback()
        return _prepare_exception_response(
            form_data, item_id_str, f"Invalid data submitted: {e}", 400, is_new_item
        )
    except Exception as e:
        db.session.rollback()
        return _prepare_exception_response(
            form_data,
            item_id_str,
            f"An unexpected server error occurred: {e}",
            500,
            is_new_item,
        )


@items_bp.route("/items/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Handle deleting an item via HTMX DELETE."""
    try:
        item = db.session.get(WatchlistItem, item_id)
        if item:
            item_title = item.title
            db.session.delete(item)
            db.session.commit()

            resp = make_response("", 200)
            resp.headers["HX-Trigger"] = "loadWatchlist"
            resp.headers["X-HX-Alert"] = safe_header_value(
                f"Item '{item_title}' deleted successfully!"
            )
            resp.headers["X-HX-Alert-Type"] = "success"
            resp.headers["X-Close-Modal"] = "true"
            return resp
        else:
            # Item not found
            resp = make_response("<p class='text-error'>Item not found.</p>", 404)
            resp.headers["HX-Retarget"] = "#messages"
            resp.headers["HX-Reswap"] = "innerHTML"
            return resp

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting item {item_id}: {e}")
        resp = make_response(
            "<p class='text-error'>Database error deleting item.</p>", 500
        )
        resp.headers["HX-Retarget"] = "#messages"
        resp.headers["HX-Reswap"] = "innerHTML"
        return resp
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error deleting item {item_id}: {e}")
        resp = make_response(
            "<p class='text-error'>An unexpected error occurred.</p>", 500
        )
        resp.headers["HX-Retarget"] = "#messages"
        resp.headers["HX-Reswap"] = "innerHTML"
        return resp
