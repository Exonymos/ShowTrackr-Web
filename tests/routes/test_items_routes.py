# tests/routes/test_items_routes.py
import pytest
from flask import url_for
from src.watchlist.models import WatchlistItem
from src.watchlist import db as main_db
import re


def test_add_item_form_loads(client):
    """Test that the add item form partial loads."""
    response = client.get(
        url_for("items.add_item_form"), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert b"<form" in response.data
    assert b'id="item-form"' in response.data


def test_save_new_item_success(client, db_session):
    """Test saving a new item successfully."""
    data = {
        "title": "New Test Movie",
        "type": "movie",
        "year": "2024",
        "status": "Plan to Watch",
        "rating": "9",
    }
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "loadWatchlist"
    assert response.headers.get("X-Close-Modal") == "true"
    assert "saved successfully" in response.headers.get("X-HX-Alert")

    item = WatchlistItem.query.filter_by(title="New Test Movie").first()
    assert item is not None
    assert item.type == "movie"
    assert item.year == 2024
    assert item.status == "Plan to Watch"
    assert item.rating == 9

    # Clean up
    db_session.delete(item)
    db_session.commit()


def test_save_new_item_validation_failure_title(client):
    """Test saving a new item with validation failure."""
    data = {"type": "movie", "status": "Watched"}  # Missing title
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 400
    assert b"Title is required." in response.data
    assert b"<form" in response.data


def test_save_item_invalid_year_format(client):
    """Test saving an item with an invalid year format."""
    data = {
        "title": "Invalid Year Movie",
        "type": "movie",
        "year": "abc",
        "status": "Watched",
    }
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 400
    item = WatchlistItem.query.filter_by(title="Invalid Year Movie").first()
    if item:
        assert item.year is None
        main_db.session.delete(item)
        main_db.session.commit()


def test_save_item_rating_out_of_range(client):
    """Test saving an item with a rating out of range."""
    data_low = {
        "title": "Low Rating",
        "type": "movie",
        "rating": "0",
        "status": "Watched",
    }
    response_low = client.post(
        url_for("items.save_item"), data=data_low, headers={"HX-Request": "true"}
    )
    assert response_low.status_code == 400
    assert b"Rating must be between 1 and 10." in response_low.data

    data_high = {
        "title": "High Rating",
        "type": "movie",
        "rating": "11",
        "status": "Watched",
    }
    response_high = client.post(
        url_for("items.save_item"), data=data_high, headers={"HX-Request": "true"}
    )
    assert response_high.status_code == 400
    assert b"Rating must be between 1 and 10." in response_high.data


def test_save_item_invalid_date_watched_format(client):
    """Test saving an item with an invalid date watched format."""
    data = {
        "title": "Invalid Date",
        "type": "movie",
        "date_watched": "2023-13-01",
        "status": "Watched",
    }  # Invalid month
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 400
    assert b"Invalid Date Watched format" in response.data


def test_edit_non_existent_item(client):
    """Test editing a non-existent item."""
    data = {
        "item_id": "99999",
        "title": "Ghost Item",
        "type": "movie",
        "status": "Watched",
    }
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 404
    assert b"Item not found" in response.data


def test_edit_item_form_loads(client, db_session):
    """Test loading the edit form for an existing item."""
    item = WatchlistItem(title="Edit Me", type="tv")
    db_session.add(item)
    db_session.commit()

    response = client.get(
        url_for("items.edit_item_form", item_id=item.id), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert b"<form" in response.data
    assert b'id="item-form"' in response.data
    assert b'value="Edit Me"' in response.data
    assert re.search(rb"Delete\s*</button>", response.data) is not None

    # Clean up
    db_session.delete(item)
    db_session.commit()


def test_save_edited_item_success(client, db_session):
    """Test saving an edited item."""
    item = WatchlistItem(title="Original Title", type="movie", year=2000)
    db_session.add(item)
    db_session.commit()

    data = {
        "item_id": str(item.id),
        "title": "Updated Title",
        "type": "movie",
        "year": "2001",
        "status": "Watched",
        "rating": "7",
    }
    response = client.post(
        url_for("items.save_item"), data=data, headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert "Updated Title" in response.headers.get("X-HX-Alert")

    updated_item = db_session.get(WatchlistItem, item.id)
    assert updated_item.title == "Updated Title"
    assert updated_item.year == 2001
    assert updated_item.rating == 7

    # Clean up
    db_session.delete(updated_item)
    db_session.commit()


def test_delete_item_success(client, db_session):
    """Test deleting an item."""
    item = WatchlistItem(title="Delete Me", type="movie")
    db_session.add(item)
    db_session.commit()
    item_id = item.id

    response = client.delete(
        url_for("items.delete_item", item_id=item_id), headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "loadWatchlist"
    assert "deleted successfully" in response.headers.get("X-HX-Alert")
    assert response.headers.get("X-Close-Modal") == "true"

    deleted_item = db_session.get(WatchlistItem, item_id)
    assert deleted_item is None


def test_delete_non_existent_item(client):
    """Test deleting a non-existent item."""
    response = client.delete(
        url_for("items.delete_item", item_id=99999), headers={"HX-Request": "true"}
    )
    assert response.status_code == 404
    assert b"Item not found" in response.data
