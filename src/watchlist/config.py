# src/watchlist/config.py
import os
from datetime import date
from pathlib import Path

# Application Info
APP_VERSION = "0.3.0-dev"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Watchlist Defaults & Settings
DEFAULT_ITEMS_PER_PAGE = 15
VALID_PAGINATION_SIZES = [10, 15, 20, 30, 40, 50]
DEFAULT_SORT_COLUMN = "date_watched"
DEFAULT_SORT_ORDER = "desc"

# Placeholder values for achieving "nulls last" sorting via coalesce
NULL_SORT_PLACEHOLDER = {
    "date_asc": date(9999, 12, 31),
    "date_desc": date(1, 1, 1),
    "num_asc": 999999,
    "num_desc": -999999,
    "rating_asc": 99,
    "rating_desc": -1,
}

# Feedback Configuration
GOOGLE_APPS_SCRIPT_FEEDBACK_URL = os.environ.get(
    "GOOGLE_APPS_SCRIPT_FEEDBACK_URL", None
)
GOOGLE_SHEET_PUBLIC_URL = os.environ.get("GOOGLE_SHEET_PUBLIC_URL", None)

# UI / Theme Configuration
DEFAULT_THEME = "cupcake"
THEME_CATEGORIES = {
    "Light": [
        "acid",
        "bumblebee",
        "caramellatte",
        "corporate",
        "cupcake",  # Default
        "lemonade",
        "light",
        "lofi",
        "nord",
        "pastel",
        "retro",
        "silk",
        "valentine",
        "winter",
        "autumn",
    ],
    "Dark": [
        "abyss",
        "aqua",
        "black",
        "business",
        "coffee",
        "dark",
        "dim",
        "dracula",
        "ember",
        "forest",
        "halloween",
        "luxury",
        "night",
        "sunset",
        "synthwave",
    ],
}

# Generate a list of all valid themes from the categories
VALID_THEMES = [
    theme for category_themes in THEME_CATEGORIES.values() for theme in category_themes
]

# Fallback for DEFAULT_THEME
if DEFAULT_THEME not in VALID_THEMES:
    if VALID_THEMES:
        DEFAULT_THEME = VALID_THEMES[0]
    else:
        DEFAULT_THEME = "light"
