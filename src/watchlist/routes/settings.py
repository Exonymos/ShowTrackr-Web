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
)
from .. import config

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
