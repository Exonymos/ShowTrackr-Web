# src/watchlist/routes/main.py
import os
from flask import Blueprint, render_template, request, current_app, session
from ..models import WatchlistItem
from .. import db
from sqlalchemy import desc, asc, func
from .. import config

main_bp = Blueprint("main", __name__)


def _parse_filter_args(args):
    """Parses and validates filter arguments from the request."""
    filter_status = args.get("filter_status", "all")
    filter_type = args.get("filter_type", "all")

    try:
        filter_years_str = args.getlist("filter_years")
        filter_years = [int(y) for y in filter_years_str if y.isdigit()]
    except ValueError:
        filter_years = []
        current_app.logger.warning("Invalid year filter value received.")

    filter_rating_min = None
    filter_rating_max = None
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
        current_app.logger.warning("Invalid rating filter value received.")

    return {
        "status": filter_status,
        "type": filter_type,
        "years": filter_years,
        "rating_min": filter_rating_min,
        "rating_max": filter_rating_max,
    }


def _parse_sort_args(args):
    """Parses and validates sorting arguments."""
    sort_by = args.get("sort", config.DEFAULT_SORT_COLUMN)
    sort_order = args.get("order", config.DEFAULT_SORT_ORDER)
    if sort_order not in ["asc", "desc"]:
        sort_order = config.DEFAULT_SORT_ORDER
    if sort_by not in ["date_watched", "date_added", "title", "year", "rating"]:
        sort_by = config.DEFAULT_SORT_COLUMN
    return sort_by, sort_order


def _get_pagination_params(args):
    """Gets pagination parameters."""
    page = args.get("page", 1, type=int)
    items_per_page = session.get("pagination_size", config.DEFAULT_ITEMS_PER_PAGE)
    if items_per_page not in config.VALID_PAGINATION_SIZES:
        items_per_page = config.DEFAULT_ITEMS_PER_PAGE
        session["pagination_size"] = items_per_page
    return page, items_per_page


def _apply_filters_to_query(query, filters, search_term):
    """Applies parsed filters and search term to the SQLAlchemy query."""
    if filters["status"] != "all":
        query = query.filter(WatchlistItem.status == filters["status"])
    if filters["type"] != "all":
        query = query.filter(WatchlistItem.type == filters["type"])
    if filters["years"]:
        query = query.filter(WatchlistItem.year.in_(filters["years"]))

    if filters["rating_min"] is not None or filters["rating_max"] is not None:
        query = query.filter(WatchlistItem.rating.isnot(None))
        if filters["rating_min"] is not None:
            query = query.filter(WatchlistItem.rating >= filters["rating_min"])
        if filters["rating_max"] is not None:
            query = query.filter(WatchlistItem.rating <= filters["rating_max"])

    if search_term:
        query = query.filter(WatchlistItem.title.ilike(f"%{search_term}%"))
    return query


def _apply_sorting_to_query(query, sort_by, sort_order):
    """Applies sorting logic to the SQLAlchemy query."""
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

    # Fallback if sort_by is somehow invalid
    if sort_column_expression is None:
        placeholder = (
            config.NULL_SORT_PLACEHOLDER["date_asc"]
            if sort_order == "asc"
            else config.NULL_SORT_PLACEHOLDER["date_desc"]
        )
        sort_column_expression = func.coalesce(WatchlistItem.date_watched, placeholder)

    final_sort_column = order_func(sort_column_expression)
    return query.order_by(final_sort_column, desc(WatchlistItem.id))


def _get_distinct_years():
    """Fetches distinct years from watchlist items for filter dropdown."""
    distinct_years_query = (
        db.session.query(WatchlistItem.year)
        .filter(WatchlistItem.year.isnot(None))
        .distinct()
        .order_by(desc(WatchlistItem.year))
    )
    return [y[0] for y in distinct_years_query.all()]


def get_watchlist_data(args):
    """Helper function to query watchlist data based on request args."""
    search_term = args.get("search", "").strip()
    filters = _parse_filter_args(args)
    sort_by, sort_order = _parse_sort_args(args)
    page, items_per_page = _get_pagination_params(args)

    query = WatchlistItem.query
    query = _apply_filters_to_query(query, filters, search_term)
    query = _apply_sorting_to_query(query, sort_by, sort_order)

    pagination = query.paginate(page=page, per_page=items_per_page, error_out=False)
    distinct_years = _get_distinct_years()

    return {
        "items": pagination.items,
        "pagination": pagination,
        "current_page": page,
        "items_per_page": items_per_page,
        "current_sort": sort_by,
        "current_order": sort_order,
        "current_filter_status": filters["status"],
        "current_filter_type": filters["type"],
        "current_filter_years": filters["years"],
        "current_filter_rating_min": filters["rating_min"],
        "current_filter_rating_max": filters["rating_max"],
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
