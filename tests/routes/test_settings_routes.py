# tests/routes/test_settings_routes.py
import pytest
from flask import url_for, session, get_flashed_messages
from src.watchlist import config
from src.watchlist.models import WatchlistItem
from src.watchlist import db as main_db
from src.watchlist.routes.settings import allowed_file
import json
import io
from tests.conftest import add_test_item


def test_settings_page_loads(client):
    """Test that the settings page loads correctly."""
    response = client.get(url_for("settings.show_settings"))
    assert response.status_code == 200
    assert b"Settings" in response.data
    assert b"Theme Selector" in response.data
    assert b"Pagination Size" in response.data
    assert b"Database Management" in response.data


def test_set_theme_success(client):
    """Test setting a valid theme."""
    valid_theme_to_set = "dracula"
    if valid_theme_to_set not in config.VALID_THEMES:
        valid_theme_to_set = (
            config.VALID_THEMES[1]
            if len(config.VALID_THEMES) > 1
            else config.DEFAULT_THEME
        )

    with client.session_transaction() as sess:
        sess["theme"] = config.DEFAULT_THEME  # Ensure a starting theme

    response = client.post(
        url_for("settings.set_theme"), data={"theme": valid_theme_to_set}
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Refresh") == "true"

    # Check session directly
    with client.session_transaction() as sess:
        assert sess["theme"] == valid_theme_to_set

    # Verify by making a subsequent request and checking the rendered theme
    home_response = client.get(url_for("main.index"))
    assert home_response.status_code == 200
    assert f'data-theme="{valid_theme_to_set}"'.encode() in home_response.data


def test_set_theme_invalid(client):
    """Test setting an invalid theme."""
    initial_theme = config.DEFAULT_THEME
    with client.session_transaction() as sess:
        sess["theme"] = initial_theme

    response = client.post(
        url_for("settings.set_theme"), data={"theme": "invalid_theme_name"}
    )
    assert response.status_code == 400

    # Check session remains unchanged
    with client.session_transaction() as sess:
        assert sess["theme"] == initial_theme


def test_set_pagination_size_success(client):
    """Test setting a valid pagination size."""
    size_to_set = 30
    assert size_to_set in config.VALID_PAGINATION_SIZES

    with client.session_transaction() as sess:
        sess["pagination_size"] = config.DEFAULT_ITEMS_PER_PAGE

    response = client.post(
        url_for("settings.set_pagination_size"),
        data={"pagination_size": str(size_to_set)},
    )
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "loadWatchlist"
    assert "Items per page set to" in response.headers.get("X-HX-Alert")
    assert response.headers.get("X-HX-Alert-Type") == "success"

    with client.session_transaction() as sess:
        assert sess["pagination_size"] == size_to_set


def test_set_pagination_size_invalid_value(client):
    """Test setting an invalid pagination size (not in VALID_PAGINATION_SIZES)."""
    initial_size = config.DEFAULT_ITEMS_PER_PAGE
    with client.session_transaction() as sess:
        sess["pagination_size"] = initial_size

    response = client.post(
        url_for("settings.set_pagination_size"), data={"pagination_size": "99"}
    )
    assert response.status_code == 400
    assert "Invalid pagination size selected" in response.headers.get("X-HX-Alert")

    with client.session_transaction() as sess:
        assert sess["pagination_size"] == initial_size


def test_set_pagination_size_non_integer(client):
    """Test setting a non-integer pagination size."""
    initial_size = config.DEFAULT_ITEMS_PER_PAGE
    with client.session_transaction() as sess:
        sess["pagination_size"] = initial_size

    response = client.post(
        url_for("settings.set_pagination_size"), data={"pagination_size": "abc"}
    )
    assert response.status_code == 400
    assert "Invalid pagination size input" in response.headers.get("X-HX-Alert")

    with client.session_transaction() as sess:
        assert sess["pagination_size"] == initial_size


def test_export_data_json(client, db_session):
    """Test exporting data as JSON."""
    WatchlistItem.query.delete()
    db_session.commit()

    # Add specific data for this export test
    item1 = WatchlistItem(title="Export Movie 1", type="movie", year=2020)
    item2 = WatchlistItem(
        title="Export Show 1", type="tv", status="Plan to Watch", rating=7
    )
    db_session.add_all([item1, item2])
    db_session.commit()

    response = client.get(url_for("settings.export_data_json"))
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert "attachment" in response.headers.get("Content-Disposition")
    assert response.headers.get("Content-Disposition").startswith(
        "attachment; filename=showtrackr_backup_"
    )
    assert response.headers.get("Content-Disposition").endswith(".json")

    exported_data = json.loads(response.data.decode("utf-8"))
    assert len(exported_data) == 2
    assert any(d["title"] == "Export Movie 1" for d in exported_data)
    assert any(
        d["title"] == "Export Show 1" and d["rating"] == 7 for d in exported_data
    )

    # Clean up
    db_session.delete(item1)
    db_session.delete(item2)
    db_session.commit()


def test_import_data_json_replace_existing(client, db_session, app):
    """Test importing data with replace_existing set to True."""
    # Add initial items
    add_test_item(db_session, title="Old Movie 1", type="movie")
    add_test_item(db_session, title="Old Show 1", type="tv")
    assert WatchlistItem.query.count() == 2

    # New data to import
    new_data = [{"title": "New Imported Movie", "type": "movie", "year": 2024}]
    json_string = json.dumps(new_data)
    bytes_io = io.BytesIO(json_string.encode("utf-8"))
    data_payload = {"backup_file": (bytes_io, "replace_backup.json")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data_payload,
            content_type="multipart/form-data",
            follow_redirects=True,  # To capture flash messages on the redirected page
        )

    assert response.status_code == 200
    assert b"1 items imported successfully." in response.data  # Check flash message

    # Verify database state
    items_after_import = WatchlistItem.query.all()
    assert len(items_after_import) == 1
    assert items_after_import[0].title == "New Imported Movie"
    assert WatchlistItem.query.filter_by(title="Old Movie 1").count() == 0


def test_import_data_json_empty_array(client, db_session, app):
    """Test importing an empty JSON array."""
    WatchlistItem.query.delete()
    db_session.commit()

    add_test_item(db_session, title="Movie To Be Deleted", type="movie")
    db_session.commit()
    assert WatchlistItem.query.count() == 1

    empty_data = []
    json_string = json.dumps(empty_data)
    bytes_io = io.BytesIO(json_string.encode("utf-8"))
    data_payload = {"backup_file": (bytes_io, "empty_backup.json")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data_payload,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"0 items imported successfully." in response.data
    assert WatchlistItem.query.count() == 0


def test_import_data_json_invalid_data_types(client, db_session, app):
    """Test importing data with invalid types for rating and year."""
    WatchlistItem.query.delete()
    main_db.session.commit()

    # Rating is a string, year is a string that's not a number
    invalid_type_data = [
        {"title": "Valid Title 1", "type": "movie", "year": "2020", "rating": 8},
        {"title": "Invalid Rating Type", "type": "tv", "rating": "high"},
        {"title": "Invalid Year Type", "type": "movie", "year": "twentytwenty"},
    ]
    json_string = json.dumps(invalid_type_data)
    bytes_io = io.BytesIO(json_string.encode("utf-8"))
    data_payload = {"backup_file": (bytes_io, "invalid_types.json")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data_payload,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"3 items imported successfully." in response.data

    items = WatchlistItem.query.order_by(WatchlistItem.title).all()
    assert len(items) == 3
    assert items[0].title == "Invalid Rating Type"
    assert items[0].rating is None
    assert items[1].title == "Invalid Year Type"
    assert items[1].year is None
    assert items[2].title == "Valid Title 1"
    assert items[2].year == 2020
    assert items[2].rating == 8


def test_import_data_json_success(client, db_session, app):
    """Test importing data from a valid JSON file."""
    # Ensure database is initially empty for this test or has known state
    WatchlistItem.query.delete()  # Clear existing items for this specific test
    db_session.commit()

    initial_count = WatchlistItem.query.count()
    assert initial_count == 0

    test_data = [
        {
            "title": "Import Movie 1",
            "type": "movie",
            "year": 2021,
            "status": "Watched",
            "rating": 8,
        },
        {"title": "Import Show 1", "type": "tv", "status": "Plan to Watch"},
    ]
    json_string = json.dumps(test_data)
    bytes_io = io.BytesIO(json_string.encode("utf-8"))

    data = {"backup_file": (bytes_io, "test_backup.json")}

    # Use test_request_context to simulate a request with follow_redirects
    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"items imported successfully" in response.data  # Check for flash message

    # Verify data in the database
    items_after_import = WatchlistItem.query.all()
    assert len(items_after_import) == 2
    assert WatchlistItem.query.filter_by(title="Import Movie 1").count() == 1
    assert (
        WatchlistItem.query.filter_by(
            title="Import Show 1", status="Plan to Watch"
        ).count()
        == 1
    )

    # Clean up
    WatchlistItem.query.delete()
    db_session.commit()


def test_import_data_json_invalid_file_type(client, app):
    """Test importing data with an invalid file type."""
    bytes_io = io.BytesIO(b"this is not json content")
    data = {"backup_file": (bytes_io, "test_backup.txt")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Invalid file type. Please upload a .json file." in response.data


def test_import_data_json_malformed_json(client, app):
    """Test importing data with a malformed JSON file."""
    bytes_io = io.BytesIO(b"{'title': 'Malformed Movie', 'type': 'movie'")
    data = {"backup_file": (bytes_io, "malformed.json")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"Invalid JSON file. Please upload a valid backup." in response.data


def test_import_data_json_missing_required_fields(client, db_session, app):
    """Test importing data where items are missing required fields (title, type)."""
    WatchlistItem.query.delete()
    db_session.commit()

    test_data = [
        {"type": "movie", "year": 2021},  # Missing title
        {"title": "Valid Import", "type": "tv"},
    ]
    json_string = json.dumps(test_data)
    bytes_io = io.BytesIO(json_string.encode("utf-8"))
    data = {"backup_file": (bytes_io, "missing_fields.json")}

    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    assert response.status_code == 200
    assert b"1 items imported successfully" in response.data
    assert b"1 items were skipped" in response.data

    assert WatchlistItem.query.count() == 1
    assert WatchlistItem.query.filter_by(title="Valid Import").count() == 1

    # Clean up
    WatchlistItem.query.delete()
    db_session.commit()


def test_import_no_file_selected(client, app):
    """Test import when no file is selected."""
    with app.test_request_context():
        response = client.post(
            url_for("settings.import_data_json"),
            data={},
            content_type="multipart/form-data",
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"No file part in the request" in response.data


def test_allowed_file_helper():
    """Test the allowed_file helper function."""
    assert allowed_file("backup.json") is True
    assert allowed_file("backup.JSON") is True
    assert allowed_file("backup.txt") is False
    assert allowed_file("backupjson") is False
    assert allowed_file(".json") is False
    assert allowed_file("noextension") is False
