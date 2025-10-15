"""Application factory for the McD Calories Flask app."""

from pathlib import Path
import os
from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application.

    This function follows the Flask application factory pattern. It:
      1) Creates the Flask app instance.
      2) Configures the secret key and database path (env vars supported).
      3) Registers routes and lifecycle hooks.

    Environment variables:
      FLASK_SECRET_KEY: Optional secret key for session signing.
      DATABASE: Optional absolute/relative path to the SQLite database file.

    Returns:
      The configured Flask application instance.
    """
    app = Flask(__name__)

    # Secret key: use env if provided, fall back to a dev-safe default.
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Database path: env override or default to data/menu.sqlite in the project root.
    base_dir = Path(__file__).resolve().parent.parent
    db_path = os.getenv("DATABASE", str(base_dir / "data" / "menu.sqlite.db"))
    app.config["DATABASE"] = db_path

    # Register routes.
    from .routes import register_routes
    register_routes(app)

    # Ensure database connections are properly closed after each request.
    from .db import close_db
    app.teardown_appcontext(close_db)


    return app
