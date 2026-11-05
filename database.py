"""SQLite data access layer for the Smart Warehouse application."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator, List, Optional

DB_PATH = "warehouse.db"

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    price    REAL    NOT NULL DEFAULT 0.0 CHECK(price >= 0)
);
"""


@contextmanager
def get_connection(db_path: str = DB_PATH) -> Iterator[sqlite3.Connection]:
    """Open a connection, commit on success, roll back on error, always close."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DB_PATH) -> None:
    """Create the database schema if it does not exist yet."""
    with get_connection(db_path) as conn:
        conn.execute(CREATE_PRODUCTS_TABLE)


def add_product(
    name: str,
    category: Optional[str] = None,
    quantity: int = 0,
    price: float = 0.0,
    db_path: str = DB_PATH,
) -> int:
    """Insert a new product and return its generated ID."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO products (name, category, quantity, price) VALUES (?, ?, ?, ?)",
            (name, category, quantity, price),
        )
        return cursor.lastrowid


def get_all_products(db_path: str = DB_PATH) -> List[sqlite3.Row]:
    """Return all products ordered by ID."""
    with get_connection(db_path) as conn:
        return conn.execute("SELECT * FROM products ORDER BY id").fetchall()


def get_product_by_id(product_id: int, db_path: str = DB_PATH) -> Optional[sqlite3.Row]:
    """Return a product by ID, or None if it does not exist."""
    with get_connection(db_path) as conn:
        return conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()


def update_quantity(product_id: int, delta: int, db_path: str = DB_PATH) -> bool:
    """Atomically change the quantity by `delta` (positive or negative).

    Returns True if a product was updated. Returns False if the product does not
    exist or the change would make the quantity negative (the CHECK constraint
    is enforced by a guarded UPDATE).
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "UPDATE products SET quantity = quantity + ? "
            "WHERE id = ? AND quantity + ? >= 0",
            (delta, product_id, delta),
        )
        return cursor.rowcount == 1
