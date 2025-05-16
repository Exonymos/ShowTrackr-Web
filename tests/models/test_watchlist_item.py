# tests/models/test_watchlist_item.py
import pytest
from datetime import date, datetime, timezone
from src.watchlist.models import WatchlistItem
from src.watchlist import db


def test_new_watchlist_item_defaults(db_session):
    """Test creation of a new WatchlistItem with default values."""
    item = WatchlistItem(title="Test Movie", type="movie")
    db_session.add(item)
    db_session.commit()

    assert item.id is not None
    assert item.title == "Test Movie"
    assert item.type == "movie"
    assert item.status == "Watched"
    assert item.date_added is not None
    assert isinstance(item.date_added, datetime)
    assert (
        datetime.now(timezone.utc).replace(tzinfo=None) - item.date_added
    ).total_seconds() < 10
    assert item.date_modified is not None

    # Clean up
    db_session.delete(item)
    db_session.commit()


def test_watchlist_item_custom_values(db_session):
    """Test creation with custom values."""
    custom_date_added_utc = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    custom_date_watched = date(2023, 1, 15)

    item = WatchlistItem(
        title="Custom Show",
        type="tv",
        year=2022,
        status="Plan to Watch",
        rating=8,
        overview="A great show.",
        poster_url="http://example.com/poster.jpg",
        tmdb_id="tv123",
        imdb_id="tt123",
        boxd_id="show1",
        notes="Watch soon.",
        date_added=custom_date_added_utc,
        date_watched=custom_date_watched,
    )
    db_session.add(item)
    db_session.commit()

    assert item.title == "Custom Show"
    assert item.type == "tv"
    assert item.year == 2022
    assert item.status == "Plan to Watch"
    assert item.rating == 8
    assert item.overview == "A great show."
    assert item.poster_url == "http://example.com/poster.jpg"
    assert item.tmdb_id == "tv123"
    assert item.imdb_id == "tt123"
    assert item.boxd_id == "show1"
    assert item.notes == "Watch soon."
    assert item.date_added.replace(tzinfo=None) == custom_date_added_utc.replace(
        tzinfo=None
    )
    assert item.date_watched == custom_date_watched

    # Test date_modified updates on edit
    original_modified = item.date_modified
    item.notes = "Watched it!"
    db_session.commit()
    assert item.date_modified.replace(tzinfo=None) > original_modified.replace(
        tzinfo=None
    )

    # Clean up
    db_session.delete(item)
    db_session.commit()


def test_get_display_poster():
    """Test the get_display_poster method."""
    item_with_poster = WatchlistItem(
        title="P", type="movie", poster_url="http://example.com/image.png"
    )
    item_no_poster = WatchlistItem(title="N", type="tv", poster_url="  ")
    item_none_poster = WatchlistItem(title="O", type="movie", poster_url=None)

    assert item_with_poster.get_display_poster() == "http://example.com/image.png"
    assert item_no_poster.get_display_poster() is None
    assert item_none_poster.get_display_poster() is None


def test_get_primary_quicklink():
    """Test the get_primary_quicklink method for priority."""
    # IMDb only
    item1 = WatchlistItem(title="T1", type="movie", imdb_id="tt001")
    link1 = item1.get_primary_quicklink()
    assert (
        link1 is not None
        and link1[0] == "IMDb"
        and link1[1] == "https://www.imdb.com/title/tt001"
    )

    # Letterboxd only
    item2 = WatchlistItem(title="T2", type="movie", boxd_id="boxd001")
    link2 = item2.get_primary_quicklink()
    assert (
        link2 is not None
        and link2[0] == "Letterboxd"
        and link2[1] == "https://boxd.it/boxd001"
    )

    # TMDb only (movie)
    item3 = WatchlistItem(title="T3", type="movie", tmdb_id="tmdb001")
    link3 = item3.get_primary_quicklink()
    assert (
        link3 is not None
        and link3[0] == "TMDb"
        and link3[1] == "https://www.themoviedb.org/movie/tmdb001"
    )

    # TMDb only (tv)
    item3tv = WatchlistItem(title="T3TV", type="tv", tmdb_id="tmdbtv001")
    link3tv = item3tv.get_primary_quicklink()
    assert (
        link3tv is not None
        and link3tv[0] == "TMDb"
        and link3tv[1] == "https://www.themoviedb.org/tv/tmdbtv001"
    )

    # IMDb and TMDb (IMDb should be chosen)
    item4 = WatchlistItem(title="T4", type="movie", imdb_id="tt002", tmdb_id="tmdb002")
    link4 = item4.get_primary_quicklink()
    assert link4 is not None and link4[0] == "IMDb"

    # Letterboxd and TMDb (Letterboxd should be chosen)
    item5 = WatchlistItem(
        title="T5", type="movie", boxd_id="boxd002", tmdb_id="tmdb003"
    )
    link5 = item5.get_primary_quicklink()
    assert link5 is not None and link5[0] == "Letterboxd"

    # All three (IMDb should be chosen)
    item6 = WatchlistItem(
        title="T6", type="movie", imdb_id="tt003", boxd_id="boxd003", tmdb_id="tmdb004"
    )
    link6 = item6.get_primary_quicklink()
    assert link6 is not None and link6[0] == "IMDb"

    # No IDs
    item7 = WatchlistItem(title="T7", type="movie")
    link7 = item7.get_primary_quicklink()
    assert link7 is None
