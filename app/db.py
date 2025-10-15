"""SQLite database helpers and query utilities for the McD Calories app."""

from __future__ import annotations

import sqlite3
from typing import Iterable, List, Optional
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a request-scoped SQLite connection.

    The connection is cached on Flask's `g` object and configured to return
    rows as `sqlite3.Row` so columns can be accessed by name.

    Returns:
      An open `sqlite3.Connection` bound to the current request context.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e: Optional[BaseException] = None) -> None:
    """Close the request-scoped SQLite connection if it was created.

    Args:
      e: Optional exception that triggered teardown. Not used.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def list_categories() -> List[str]:
    """Fetch distinct product categories sorted alphabetically.

    Returns:
      A list of unique category names (strings).
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT category FROM items ORDER BY category ASC;"
    ).fetchall()
    return [r["category"] for r in rows]


def list_items(category: Optional[str] = None, q: Optional[str] = None) -> Iterable[sqlite3.Row]:
    """Fetch items filtered by category and/or case-insensitive name query.

    Args:
      category: Optional category name to filter by (exact match).
      q: Optional search term to filter by item name using SQL LIKE.

    Returns:
      An iterable of `sqlite3.Row` objects representing items.
    """
    conn = get_db()
    sql = "SELECT * FROM items WHERE 1=1"
    params: list = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if q:
        sql += " AND name LIKE ?"
        params.append(f"%{q}%")
    sql += " ORDER BY name ASC"
    return conn.execute(sql, params).fetchall()


# Optional schema helper for initializing an empty database.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  energy_kcal INTEGER NOT NULL,
  fat_g REAL NOT NULL,
  sat_fat_g REAL NOT NULL,
  carbs_g REAL NOT NULL,
  sugars_g REAL NOT NULL,
  fiber_g REAL NOT NULL,
  protein_g REAL NOT NULL,
  salt_g REAL NOT NULL,
  slug TEXT UNIQUE,
  serving_label TEXT NOT NULL
);
"""


def ensure_schema() -> None:
    """Create the base schema if it does not yet exist.

    Executes `SCHEMA_SQL` and commits the transaction.
    """
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
