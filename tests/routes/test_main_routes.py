# tests/routes/test_main_routes.py
import pytest
from flask import url_for
from src.watchlist.models import WatchlistItem


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

    item = WatchlistItem(title="Test Item for HTMX", type="movie")
    db_session.add(item)
    db_session.commit()

    response = client.get(
        url_for("main.load_watchlist"), headers={"HX-Request": "true"}
    )
    # Check for table from _watchlist_items.html
    assert b'<table class="table w-full table-fixed">' in response.data
    # Check for controls bar from _controls_bar_oob.html
    assert b'<div id="controls-bar"' in response.data
    assert b'hx-swap-oob="outerHTML:#controls-bar"' in response.data

    db_session.delete(item)
    db_session.commit()


def test_load_watchlist_htmx_empty(client):
    """Test the /load_watchlist route via HTMX when no items exist."""
    # No items added, so the "empty" message should appear
    response = client.get(
        url_for("main.load_watchlist"), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert (
        b'<table class="table w-full table-fixed">' not in response.data
    )  # Table should NOT be there
    assert b"Your watchlist is empty." in response.data  # Empty message should be there
    assert b'<div id="controls-bar"' in response.data


def test_load_watchlist_full_page_reload(client):
    """Test the /load_watchlist route as a full page request (should render index)."""
    response = client.get(url_for("main.load_watchlist"))  # No HX-Request header
    assert response.status_code == 200
    assert b"ShowTrackr" in response.data  # Full page structure
    assert b"Welcome to ShowTrackr!" in response.data
    assert b'<div id="watchlist-area"' in response.data  # Main container


def test_about_page_loads(client):
    """Test that the about page loads correctly."""
    response = client.get(url_for("main.about"))
    assert response.status_code == 200
    assert b"About ShowTrackr" in response.data
    assert b"Changelog" in response.data  # Check for tab
