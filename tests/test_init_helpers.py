# tests/test_init_helpers.py
import pytest
from src.watchlist import (
    get_validated_theme,
)
from src.watchlist import (
    config,
)


def test_get_validated_theme_default(app):
    with app.test_request_context("/"):  # Need app context for session
        mock_session = {}
        assert get_validated_theme(mock_session) == config.DEFAULT_THEME
        assert mock_session.get("theme") == config.DEFAULT_THEME


def test_get_validated_theme_valid_in_session(app):
    with app.test_request_context("/"):
        mock_session = {}
        valid_theme = "dark"  # Assuming 'dark' is in config.VALID_THEMES
        if valid_theme not in config.VALID_THEMES:
            valid_theme = (
                config.VALID_THEMES[0] if config.VALID_THEMES else config.DEFAULT_THEME
            )

        mock_session["theme"] = valid_theme
        assert get_validated_theme(mock_session) == valid_theme
        assert mock_session.get("theme") == valid_theme


def test_get_validated_theme_invalid_in_session(app):
    with app.test_request_context("/"):
        mock_session = {}
        mock_session["theme"] = "invalid-theme-name"
        assert get_validated_theme(mock_session) == config.DEFAULT_THEME
        assert mock_session.get("theme") == config.DEFAULT_THEME


def test_get_validated_theme_empty_valid_themes_list(app, monkeypatch):
    # Temporarily mock VALID_THEMES to be empty
    monkeypatch.setattr(config, "VALID_THEMES", [])
    with app.test_request_context("/"):
        mock_session = {"theme": "some-theme"}
        # If VALID_THEMES is empty, it should still default to DEFAULT_THEME
        assert get_validated_theme(mock_session) == config.DEFAULT_THEME
        assert mock_session.get("theme") == config.DEFAULT_THEME
