"""Business logic for the Smart Warehouse: validation and stock operations."""

import sqlite3
from typing import List, Optional

import database


class WarehouseError(Exception):
    """Base class for all warehouse-related errors."""


class ValidationError(WarehouseError):
    """Raised when user-supplied data is invalid."""


class ProductNotFoundError(WarehouseError):
    """Raised when a product with the given ID does not exist."""


class InsufficientStockError(WarehouseError):
    """Raised when trying to issue more items than are in stock."""


def _validate_id(product_id: int) -> int:
    if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
        raise ValidationError("Product ID must be a positive integer.")
    return product_id


def _validate_amount(amount: int) -> int:
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        raise ValidationError("Amount must be a positive integer.")
    return amount


def add_product(
    name: str,
    category: Optional[str] = None,
    quantity: int = 0,
    price: float = 0.0,
    db_path: str = database.DB_PATH,
) -> int:
    """Validate input and create a new product. Returns the new product ID."""
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Product name must not be empty.")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        raise ValidationError("Quantity must be a non-negative integer.")
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
        raise ValidationError("Price must be a non-negative number.")
    category = category.strip() if category and category.strip() else None
    try:
        return database.add_product(name.strip(), category, quantity, float(price), db_path)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Database error: {exc}") from exc


def list_products(db_path: str = database.DB_PATH) -> List[sqlite3.Row]:
    """Return all products."""
    try:
        return database.get_all_products(db_path)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Database error: {exc}") from exc


def find_product(product_id: int, db_path: str = database.DB_PATH) -> sqlite3.Row:
    """Return a product by ID or raise ProductNotFoundError."""
    _validate_id(product_id)
    try:
        product = database.get_product_by_id(product_id, db_path)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Database error: {exc}") from exc
    if product is None:
        raise ProductNotFoundError(f"Product with ID {product_id} not found.")
    return product


def receive_stock(product_id: int, amount: int, db_path: str = database.DB_PATH) -> int:
    """Register incoming stock. Returns the new quantity."""
    _validate_amount(amount)
    find_product(product_id, db_path)
    try:
        database.update_quantity(product_id, amount, db_path)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Database error: {exc}") from exc
    return find_product(product_id, db_path)["quantity"]


def issue_stock(product_id: int, amount: int, db_path: str = database.DB_PATH) -> int:
    """Register outgoing stock. Returns the new quantity.

    Raises InsufficientStockError if the warehouse holds fewer items than requested.
    """
    _validate_amount(amount)
    product = find_product(product_id, db_path)
    try:
        updated = database.update_quantity(product_id, -amount, db_path)
    except sqlite3.Error as exc:
        raise WarehouseError(f"Database error: {exc}") from exc
    if not updated:
        # The guarded UPDATE refused the change; re-read to report the current stock.
        available = find_product(product_id, db_path)["quantity"]
        raise InsufficientStockError(
            f"Not enough stock for '{product['name']}': requested {amount}, available {available}."
        )
    return find_product(product_id, db_path)["quantity"]
