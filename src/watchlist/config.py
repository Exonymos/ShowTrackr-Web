# src/watchlist/config.py
import os
from datetime import date
from pathlib import Path

# Application Info
APP_VERSION = "0.2.1"

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
VALID_THEMES = [
    "cupcake",
    "dracula",
    "light",
    "dark",
    "bumblebee",
    "synthwave",
    "emerald",
    "halloween",
    "corporate",
    "forest",
    "retro",
    "black",
    "valentine",
    "luxury",
    "garden",
    "business",
    "lofi",
    "night",
    "pastel",
    "coffee",
    "fantasy",
    "dim",
    "wireframe",
    "sunset",
    "cmyk",
    "abyss",
    "autumn",
    "acid",
    "lemonade",
    "winter",
    "nord",
    "caramellatte",
    "silk",
]
