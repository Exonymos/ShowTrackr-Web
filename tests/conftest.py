# tests/conftest.py
import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pytest
import os
from src.watchlist import create_app, db as main_db
from src.watchlist.models import WatchlistItem

# Determine the base directory of the project for correct data path
TEST_DATA_DIR = project_root / "tests" / "test_data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    db_file_name = f"test_showtrackr_{os.urandom(4).hex()}.db"
    db_path = TEST_DATA_DIR / db_file_name
    test_db_uri = f"sqlite:///{db_path.resolve()}"

    # Store original env vars to restore them later
    original_env = os.environ.copy()

    # Set test-specific environment variables BEFORE app creation
    os.environ["FLASK_ENV"] = "testing"
    os.environ["DATABASE_URL"] = test_db_uri
    os.environ["FLASK_DEBUG"] = "False"
    os.environ["SECRET_KEY"] = "pytest-secret-key"

    app_instance = create_app()

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

    # Explicitly update app.config AFTER creation for test-specific settings
    app_instance.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": test_db_uri,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "pytest-secret-key",
            "SERVER_NAME": "localhost.test",
            "DEBUG": False,
        }
    )

    with app_instance.app_context():
        main_db.create_all()

    yield app_instance

    with app_instance.app_context():
        main_db.drop_all()

    try:
        os.remove(db_path)
    except OSError as e:
        print(f"Error removing test database {db_path}: {e}")


@pytest.fixture()
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture()
def db_session(app):
    """
    Provides the application's database session for tests.
    Ensures that any changes made during a test are rolled back.
    """
    with app.app_context():
        main_db.session.begin_nested()

        @main_db.event.listens_for(main_db.session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not session.is_active:
                session.begin_nested()

        yield main_db.session

        main_db.session.rollback()
