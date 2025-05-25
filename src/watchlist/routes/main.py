# src/watchlist/routes/main.py
import os
from flask import Blueprint, render_template, request, current_app, session
from ..models import WatchlistItem
from .. import db, htmx
from sqlalchemy import desc, asc, func
from .. import config

main_bp = Blueprint("main", __name__)


def get_watchlist_data(args):
    """Helper function to query watchlist data based on request args."""
    page = args.get("page", 1, type=int)
    search_term = args.get("search", "").strip()

    # Filters
    filter_status = args.get("filter_status", "all")
    filter_type = args.get("filter_type", "all")
    try:
        filter_years_str = args.getlist("filter_years")
        filter_years = [int(y) for y in filter_years_str if y.isdigit()]
    except ValueError:
        filter_years = []
        current_app.logger.warning("Invalid year filter value received.")

    try:
        rating_min_str = args.get("filter_rating_min", "").strip()
        filter_rating_min = int(rating_min_str) if rating_min_str.isdigit() else None
        if filter_rating_min is not None and not (1 <= filter_rating_min <= 10):
            filter_rating_min = None

        rating_max_str = args.get("filter_rating_max", "").strip()
        filter_rating_max = int(rating_max_str) if rating_max_str.isdigit() else None
        if filter_rating_max is not None and not (1 <= filter_rating_max <= 10):
            filter_rating_max = None

        if (
            filter_rating_min is not None
            and filter_rating_max is not None
            and filter_rating_min > filter_rating_max
        ):
            filter_rating_min, filter_rating_max = filter_rating_max, filter_rating_min
    except ValueError:
        filter_rating_min = None
        filter_rating_max = None
        current_app.logger.warning("Invalid rating filter value received.")

    # Sorting defaults
    sort_by = args.get("sort", config.DEFAULT_SORT_COLUMN)
    sort_order = args.get("order", config.DEFAULT_SORT_ORDER)
    if sort_order not in ["asc", "desc"]:
        sort_order = config.DEFAULT_SORT_ORDER
    if sort_by not in ["date_watched", "date_added", "title", "year", "rating"]:
        sort_by = config.DEFAULT_SORT_COLUMN

    # Pagination Size
    items_per_page = session.get("pagination_size", config.DEFAULT_ITEMS_PER_PAGE)
    if items_per_page not in config.VALID_PAGINATION_SIZES:
        items_per_page = config.DEFAULT_ITEMS_PER_PAGE
        session["pagination_size"] = items_per_page

    # Build Query
    query = WatchlistItem.query

    # Apply Filters
    if filter_status != "all":
        query = query.filter(WatchlistItem.status == filter_status)
    if filter_type != "all":
        query = query.filter(WatchlistItem.type == filter_type)
    if filter_years:
        query = query.filter(WatchlistItem.year.in_(filter_years))
    if filter_rating_min is not None or filter_rating_max is not None:
        query = query.filter(WatchlistItem.rating.isnot(None))
        if filter_rating_min is not None:
            query = query.filter(WatchlistItem.rating >= filter_rating_min)
        if filter_rating_max is not None:
            query = query.filter(WatchlistItem.rating <= filter_rating_max)
    if search_term:
        query = query.filter(WatchlistItem.title.ilike(f"%{search_term}%"))

    # Sorting logic using coalesce
    order_func = desc if sort_order == "desc" else asc
    sort_column_expression = None
    if sort_by == "title":
        sort_column_expression = func.lower(WatchlistItem.title)
    elif sort_by == "year":
        placeholder = (
            config.NULL_SORT_PLACEHOLDER["num_asc"]
            if sort_order == "asc"
            else config.NULL_SORT_PLACEHOLDER["num_desc"]
        )
        sort_column_expression = func.coalesce(WatchlistItem.year, placeholder)
    elif sort_by == "rating":
        placeholder = (
            config.NULL_SORT_PLACEHOLDER["rating_asc"]
            if sort_order == "asc"
            else config.NULL_SORT_PLACEHOLDER["rating_desc"]
        )
        sort_column_expression = func.coalesce(WatchlistItem.rating, placeholder)
    elif sort_by == "date_added":
        sort_column_expression = WatchlistItem.date_added
    elif sort_by == "date_watched":
        placeholder = (
            config.NULL_SORT_PLACEHOLDER["date_asc"]
            if sort_order == "asc"
            else config.NULL_SORT_PLACEHOLDER["date_desc"]
        )
        sort_column_expression = func.coalesce(WatchlistItem.date_watched, placeholder)

    if sort_column_expression is None:  # Fallback
        placeholder = (
            config.NULL_SORT_PLACEHOLDER["date_asc"]
            if sort_order == "asc"
            else config.NULL_SORT_PLACEHOLDER["date_desc"]
        )
        sort_column_expression = func.coalesce(WatchlistItem.date_watched, placeholder)

    final_sort_column = order_func(sort_column_expression)
    query = query.order_by(final_sort_column, desc(WatchlistItem.id))

    # Apply Pagination
    pagination = query.paginate(page=page, per_page=items_per_page, error_out=False)

    # Get Years for Filter
    distinct_years_query = (
        db.session.query(WatchlistItem.year)
        .filter(WatchlistItem.year.isnot(None))
        .distinct()
        .order_by(desc(WatchlistItem.year))
    )
    distinct_years = [y[0] for y in distinct_years_query.all()]

    # Return context dictionary
    return {
        "items": pagination.items,
        "pagination": pagination,
        "current_page": page,
        "items_per_page": items_per_page,
        "current_sort": sort_by,
        "current_order": sort_order,
        "current_filter_status": filter_status,
        "current_filter_type": filter_type,
        "current_filter_years": filter_years,
        "current_filter_rating_min": filter_rating_min,
        "current_filter_rating_max": filter_rating_max,
        "current_search": search_term,
        "distinct_years": distinct_years,
    }


@main_bp.route("/load_watchlist")
def load_watchlist():
    """HTMX route OR full page reload handler for the watchlist."""

    context = get_watchlist_data(request.args)

    if request.headers.get("HX-Request"):
        watchlist_html = render_template("_watchlist_items.html", **context)
        controls_html = render_template("_controls_bar_oob.html", **context)
        return watchlist_html + controls_html
    else:
        return render_template("index.html", **context)


@main_bp.route("/")
def index():
    """Renders the main page structure. Initial data loaded via HTMX."""
    context = get_watchlist_data(request.args)
    return render_template("index.html", **context)


@main_bp.route("/about")
def about():
    """Renders the About page."""
    return render_template(
        "about.html",
        version=config.APP_VERSION,
        feedback_url=os.environ.get("GOOGLE_APPS_SCRIPT_FEEDBACK_URL"),
        sheet_url=os.environ.get("GOOGLE_SHEET_PUBLIC_URL"),
    )
