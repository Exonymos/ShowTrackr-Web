# tests/routes/test_main_routes.py
import pytest
from flask import url_for, session as flask_session
from src.watchlist.models import WatchlistItem
from src.watchlist import db as main_db, config
from datetime import date, datetime, timezone
from tests.conftest import add_test_item
from unittest.mock import patch


def test_index_page_loads(client):
    """Test that the index page loads correctly."""
    response = client.get(url_for("main.index"))
    assert response.status_code == 200
    assert b"ShowTrackr" in response.data  # Check for app name
    assert b"Welcome to ShowTrackr!" in response.data
    # Check for the div that HTMX will populate
    assert b'<div id="watchlist-content"' in response.data


def test_load_watchlist_htmx(client, db_session):
    """Test the /load_watchlist route via HTMX request."""
    item = add_test_item(db_session, title="Test Item for HTMX")
    db_session.commit()
    response = client.get(
        url_for("main.load_watchlist"), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert b"Test Item for HTMX" in response.data  # Check for the test item
    # Check for table from _watchlist_items.html
    assert b'<table class="table w-full table-fixed">' in response.data
    # Check for controls bar from _controls_bar_oob.html
    assert b'<div id="controls-bar"' in response.data
    assert b'hx-swap-oob="outerHTML:#controls-bar"' in response.data

    # Clean up
    main_db.session.delete(item)
    main_db.session.commit()


def test_load_watchlist_htmx_empty(client):
    """Test the /load_watchlist route via HTMX when no items exist."""
    # Clear the watchlist
    WatchlistItem.query.delete()
    main_db.session.commit()
    # No items added, so the "empty" message should appear
    response = client.get(
        url_for("main.load_watchlist"), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert (
        b'<table class="table w-full table-fixed">' not in response.data
    )  # Table should NOT be there
    assert b"Your Watchlist is Empty!" in response.data  # Empty message should be there
    assert b'<div id="controls-bar"' in response.data


def test_load_watchlist_full_page_reload(client):
    """Test the /load_watchlist route as a full page request (should render index)."""
    response = client.get(url_for("main.load_watchlist"))  # No HX-Request header
    assert response.status_code == 200
    assert b"ShowTrackr" in response.data  # Full page structure
    assert b'<div id="watchlist-area"' in response.data  # Main container


def test_about_page_loads(client):
    """Test that the about page loads correctly."""
    response = client.get(url_for("main.about"))
    assert response.status_code == 200
    assert b"About ShowTrackr" in response.data


def test_load_watchlist_filter_status(client, db_session):
    """Test loading watchlist with status filter."""
    add_test_item(db_session, title="Watched Movie", status="Watched")
    add_test_item(db_session, title="Plan Movie", status="Plan to Watch")
    response = client.get(
        url_for("main.load_watchlist", filter_status="Watched"),
        headers={"HX-Request": "true"},
    )
    assert b"Watched Movie" in response.data
    assert b"Plan Movie" not in response.data


def test_load_watchlist_filter_type(client, db_session):
    """Test loading watchlist with type filter."""
    add_test_item(db_session, title="Test Movie Type", type="movie")
    add_test_item(db_session, title="Test TV Type", type="tv")
    response = client.get(
        url_for("main.load_watchlist", filter_type="tv"),
        headers={"HX-Request": "true"},
    )
    assert b"Test TV Type" in response.data
    assert b"Test Movie Type" not in response.data


def test_load_watchlist_filter_single_year(client, db_session):
    """Test loading watchlist with single year filter."""
    add_test_item(db_session, title="Movie 2023", year=2023)
    add_test_item(db_session, title="Movie 2022", year=2022)
    response = client.get(
        url_for("main.load_watchlist", filter_years=[2023]),
        headers={"HX-Request": "true"},
    )
    assert b"Movie 2023" in response.data
    assert b"Movie 2022" not in response.data


def test_load_watchlist_filter_multiple_years(client, db_session):
    """Test loading watchlist with multiple years filter."""
    add_test_item(db_session, title="Movie 2023 Multi", year=2023)
    add_test_item(db_session, title="Movie 2022 Multi", year=2022)
    add_test_item(db_session, title="Movie 2021 Multi", year=2021)
    response = client.get(
        url_for("main.load_watchlist", filter_years=[2023, 2022]),
        headers={"HX-Request": "true"},
    )
    assert b"Movie 2023 Multi" in response.data
    assert b"Movie 2022 Multi" in response.data
    assert b"Movie 2021 Multi" not in response.data


def test_load_watchlist_filter_rating_range(client, db_session):
    """Test loading watchlist with rating range filter."""
    add_test_item(db_session, title="Rating 5", rating=5)
    add_test_item(db_session, title="Rating 8", rating=8)
    add_test_item(db_session, title="Rating 10", rating=10)
    response = client.get(
        url_for("main.load_watchlist", filter_rating_min=7, filter_rating_max=9),
        headers={"HX-Request": "true"},
    )
    assert b"Rating 8" in response.data
    assert b"Rating 5" not in response.data
    assert b"Rating 10" not in response.data


def test_load_watchlist_filter_no_results(client, db_session):
    """Test loading watchlist with filters that yield no results."""
    add_test_item(db_session, title="Unique Movie", year=2000)
    response = client.get(
        url_for("main.load_watchlist", filter_years=[1990]),
        headers={"HX-Request": "true"},
    )
    assert b"Unique Movie" not in response.data
    assert b"No results found." in response.data


def test_load_watchlist_sort_title_asc_desc(client, db_session):
    """Test loading watchlist with title sorting in both directions."""
    WatchlistItem.query.delete()
    db_session.commit()

    item_b = add_test_item(db_session, title="Banana", date_watched=date(2023, 1, 1))
    item_a = add_test_item(db_session, title="Apple", date_watched=date(2023, 1, 2))
    item_c = add_test_item(db_session, title="Cherry", date_watched=date(2023, 1, 3))

    # Test ASC
    response_asc = client.get(
        url_for("main.load_watchlist", sort="title", order="asc"),
        headers={"HX-Request": "true"},
    )
    content_asc = response_asc.data.decode()
    assert b"Apple" in response_asc.data
    assert b"Banana" in response_asc.data
    assert b"Cherry" in response_asc.data
    assert (
        content_asc.find("Apple")
        < content_asc.find("Banana")
        < content_asc.find("Cherry")
    )

    # Test DESC
    response_desc = client.get(
        url_for("main.load_watchlist", sort="title", order="desc"),
        headers={"HX-Request": "true"},
    )
    content_desc = response_desc.data.decode()
    assert b"Apple" in response_desc.data
    assert b"Banana" in response_desc.data
    assert b"Cherry" in response_desc.data
    assert (
        content_desc.find("Cherry")
        < content_desc.find("Banana")
        < content_desc.find("Apple")
    )

    # Clean up
    db_session.delete(item_a)
    db_session.delete(item_b)
    db_session.delete(item_c)
    db_session.commit()


def test_load_watchlist_sort_year_nulls_last(client, db_session):
    """Test loading watchlist with year sorting, ensuring nulls are last."""
    add_test_item(
        db_session, title="Year Null", year=None, date_watched=date(2023, 1, 1)
    )
    add_test_item(
        db_session, title="Year 2022", year=2022, date_watched=date(2023, 1, 2)
    )
    add_test_item(
        db_session, title="Year 2023", year=2023, date_watched=date(2023, 1, 3)
    )

    # Test DESC (Newest first, Nulls last)
    response_desc = client.get(
        url_for("main.load_watchlist", sort="year", order="desc"),
        headers={"HX-Request": "true"},
    )
    content_desc = response_desc.data.decode()
    assert (
        content_desc.find("Year 2023")
        < content_desc.find("Year 2022")
        < content_desc.find("Year Null")
    )

    # Test ASC (Oldest first, Nulls last)
    response_asc = client.get(
        url_for("main.load_watchlist", sort="year", order="asc"),
        headers={"HX-Request": "true"},
    )
    content_asc = response_asc.data.decode()
    assert (
        content_asc.find("Year 2022")
        < content_asc.find("Year 2023")
        < content_asc.find("Year Null")
    )


def test_load_watchlist_sort_rating_nulls_last(client, db_session):
    """Test loading watchlist with rating sorting, ensuring nulls are last."""
    add_test_item(
        db_session, title="Rating Null", rating=None, date_watched=date(2023, 1, 1)
    )
    add_test_item(db_session, title="Rating 5", rating=5, date_watched=date(2023, 1, 2))
    add_test_item(db_session, title="Rating 8", rating=8, date_watched=date(2023, 1, 3))

    response_desc = client.get(
        url_for("main.load_watchlist", sort="rating", order="desc"),
        headers={"HX-Request": "true"},
    )
    content_desc = response_desc.data.decode()
    assert (
        content_desc.find("Rating 8")
        < content_desc.find("Rating 5")
        < content_desc.find("Rating Null")
    )

    response_asc = client.get(
        url_for("main.load_watchlist", sort="rating", order="asc"),
        headers={"HX-Request": "true"},
    )
    content_asc = response_asc.data.decode()
    assert (
        content_asc.find("Rating 5")
        < content_asc.find("Rating 8")
        < content_asc.find("Rating Null")
    )


def test_404_error_page(client):
    """Test that a 404 error page loads correctly."""
    response = client.get("/a-route-that-does-not-exist")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
    assert b"404" in response.data


def test_500_error_page_on_index_route(client, app):
    """Test that a 500 error page loads correctly on the index route."""
    with patch("src.watchlist.routes.main.get_watchlist_data") as mock_get_data:
        mock_get_data.side_effect = Exception(
            "Mocked 500 error from get_watchlist_data"
        )

        response = client.get(url_for("main.index"))
        assert response.status_code == 500
        assert b"Internal Server Error" in response.data
        assert b"500" in response.data
