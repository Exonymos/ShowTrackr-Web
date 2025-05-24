# src/watchlist/routes/items.py
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
    current_app,
    session,
)
import unicodedata
from ..models import WatchlistItem
from .. import db, htmx
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime

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


@items_bp.route("/items/save", methods=["POST"])
def save_item():
    """Handle saving new or updated items via HTMX POST."""
    item_id = request.form.get("item_id")
    is_new_item = not item_id
    error_messages = []

    form_data_dict = request.form.to_dict()

    try:
        if is_new_item:
            item = WatchlistItem()
        else:
            item = db.session.get(WatchlistItem, int(item_id))
            if not item:
                resp = make_response(
                    "<p class='text-error'>Error: Item not found.</p>", 404
                )
                return resp

        # Update fields from form
        item.title = form_data_dict.get("title", "").strip()
        item.type = form_data_dict.get("type")
        year_str = form_data_dict.get("year", "").strip()
        if year_str:
            if year_str.isdigit():
                year_val = int(year_str)
                if not (1800 <= year_val <= 2050):
                    error_messages.append("Year must be between 1800 and 2050.")
                    item.year = None
                else:
                    item.year = year_val
            else:
                error_messages.append("Year must be a valid number.")
                item.year = None
        else:
            item.year = None

        item.overview = form_data_dict.get("overview", "").strip() or None
        item.poster_url = form_data_dict.get("poster_url", "").strip() or None
        item.status = form_data_dict.get("status")

        # Handle empty rating string
        rating_str = form_data_dict.get("rating", "").strip()
        if rating_str:
            if rating_str.isdigit():
                rating_val = int(rating_str)
                if not (1 <= rating_val <= 10):
                    error_messages.append("Rating must be between 1 and 10.")
                    item.rating = None
                else:
                    item.rating = rating_val
            else:
                error_messages.append("Rating must be a valid number.")
                item.rating = None
        else:
            item.rating = None

        item.notes = form_data_dict.get("notes", "").strip() or None
        item.tmdb_id = form_data_dict.get("tmdb_id", "").strip() or None
        item.imdb_id = form_data_dict.get("imdb_id", "").strip() or None
        item.boxd_id = form_data_dict.get("boxd_id", "").strip() or None

        # Handle Date Watched
        date_watched_str = form_data_dict.get("date_watched", "").strip()
        if date_watched_str:
            try:
                # Attempt to parse YYYY-MM-DD format
                item.date_watched = date.fromisoformat(date_watched_str)
            except ValueError:
                # Handle invalid date format
                error_messages.append(
                    "Invalid Date Watched format. Please use YYYY-MM-DD."
                )
                item.date_watched = None
        else:
            item.date_watched = None

        # Basic Validation (Server-Side)
        if not item.title:
            error_messages.append("Title is required.")
        if item.type not in ["movie", "tv"]:
            error_messages.append("Invalid type selected.")
        if item.status not in ["Plan to Watch", "Watched"]:
            error_messages.append("Invalid status selected.")

        # Check collected errors
        if error_messages:
            form_render_item = (
                db.session.get(WatchlistItem, int(item_id))
                if not is_new_item
                else WatchlistItem()
            )
            form_render_item.title = form_data_dict.get("title", "")
            form_render_item.type = form_data_dict.get("type")
            form_render_item.year_str = form_data_dict.get("year", "")
            form_render_item.overview = form_data_dict.get("overview", "")
            form_render_item.poster_url = form_data_dict.get("poster_url", "")
            form_render_item.status = form_data_dict.get("status")
            form_render_item.rating_str = form_data_dict.get("rating", "")
            form_render_item.notes = form_data_dict.get("notes", "")
            form_render_item.tmdb_id = form_data_dict.get("tmdb_id", "")
            form_render_item.imdb_id = form_data_dict.get("imdb_id", "")
            form_render_item.boxd_id = form_data_dict.get("boxd_id", "")

            if item.date_watched and isinstance(item.date_watched, date):
                form_render_item.date_watched_str = item.date_watched.isoformat()
            else:
                form_render_item.date_watched_str = date_watched_str

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
        current_app.logger.error(f"Database error saving item: {e}", exc_info=True)
        form_render_item = (
            WatchlistItem(**form_data_dict)
            if is_new_item
            else db.session.get(WatchlistItem, int(item_id))
        )
        if form_render_item:  # Repopulate with form data if item exists
            for key, value in form_data_dict.items():
                if hasattr(form_render_item, key):
                    setattr(form_render_item, key, value)
            form_render_item.date_watched_str = form_data_dict.get("date_watched", "")
            form_render_item.year_str = form_data_dict.get("year", "")
            form_render_item.rating_str = form_data_dict.get("rating", "")
        resp = make_response(
            render_template(
                "_add_edit_item_form.html",
                item=form_render_item,
                errors=["Database error saving item. Please try again."],
            ),
            500,
        )
        resp.headers["X-HX-Alert"] = "Database error. Please try again."
        resp.headers["X-HX-Alert-Type"] = "error"
        return resp

    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Form data conversion error: {e}", exc_info=True)
        form_render_item = (
            WatchlistItem(**form_data_dict)
            if is_new_item
            else db.session.get(WatchlistItem, int(item_id))
        )
        if form_render_item:
            for key, value in form_data_dict.items():
                if hasattr(form_render_item, key):
                    setattr(form_render_item, key, value)
            form_render_item.date_watched_str = form_data_dict.get("date_watched", "")
            form_render_item.year_str = form_data_dict.get("year", "")
            form_render_item.rating_str = form_data_dict.get("rating", "")

        resp = make_response(
            render_template(
                "_add_edit_item_form.html",
                item=form_render_item,
                errors=[
                    f"Invalid data submitted (e.g., non-numeric year/rating): {e}."
                ],
            ),
            400,
        )
        resp.headers["X-HX-Alert"] = "Invalid data in form."
        resp.headers["X-HX-Alert-Type"] = "error"
        return resp

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error saving item: {e}", exc_info=True)
        resp = make_response(
            render_template(
                "_form_error.html",
                message="An unexpected server error occurred. Please check logs.",
            ),
            500,
        )
        resp.headers["X-HX-Alert"] = "An unexpected server error occurred."
        resp.headers["X-HX-Alert-Type"] = "error"
        return resp


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
