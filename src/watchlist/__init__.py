# src/watchlist/__init__.py
import os
from flask import Flask, session, request, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_htmx import HTMX
from dotenv import load_dotenv
from pathlib import Path
from werkzeug.exceptions import HTTPException
from . import config

# Determine the base directory of the project
# This __init__.py file is in src/watchlist/ so,
# The project root is two levels up.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load .env
dotenv_path = DATA_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
htmx = HTMX()


# Theme Validation
def get_validated_theme(session_data) -> str:
    """Gets the theme from session, validates it, and returns a valid theme."""
    theme = session_data.get("theme", config.DEFAULT_THEME)
    if theme not in config.VALID_THEMES:
        theme = config.DEFAULT_THEME
        session_data["theme"] = theme
    return theme


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )

    # Configuration from config.py and .env
    app.config.from_object(config)  # Load defaults from config.py
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-insecure"),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{DATA_DIR / 'database.db'}",
        # Override DEBUG from .env if present
        DEBUG=os.environ.get("FLASK_DEBUG", "False").lower() == "true",
    )

    # Initialize Extensions with App Context
    db.init_app(app)
    migrate.init_app(app, db)
    htmx.init_app(app)

    # Import and Register Blueprints
    with app.app_context():
        from . import models
        from .routes import main_bp, items_bp, settings_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(items_bp)
        app.register_blueprint(settings_bp)

    # Context Processors
    @app.context_processor
    def inject_global_vars():
        """Injects validated theme and app version into templates."""
        theme = get_validated_theme(session)
        return dict(
            current_theme=theme,
            app_version=config.APP_VERSION,
            feedback_url=config.GOOGLE_APPS_SCRIPT_FEEDBACK_URL,
            sheet_url=config.GOOGLE_SHEET_PUBLIC_URL,
        )

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error: HTTPException):
        theme = get_validated_theme(session)
        return render_template("errors/404.html", current_theme=theme), 404

    @app.errorhandler(500)
    def internal_error(error: Exception):
        db.session.rollback()
        theme = get_validated_theme(session)
        current_app.logger.error(f"Server Error: {error}", exc_info=True)
        return render_template("errors/500.html", current_theme=theme), 500

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        if isinstance(e, HTTPException):
            return e
        # Handle non-HTTP exceptions as 500
        db.session.rollback()
        theme = get_validated_theme(session)
        current_app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
        return render_template("errors/500.html", current_theme=theme), 500

    return app
