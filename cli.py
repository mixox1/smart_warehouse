"""Command-line interface for the Smart Warehouse application."""

from typing import Callable, Optional

import database
import storage

MENU = """
=== Smart Warehouse ===
1. Add new product
2. Receive stock (incoming)
3. Issue stock (outgoing)
4. Show all products
5. Find product by ID
0. Exit
"""


def prompt_int(message: str, minimum: Optional[int] = None) -> int:
    """Ask until the user enters a valid integer (>= minimum if given)."""
    while True:
        raw = input(message).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Error: please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Error: value must be at least {minimum}.")
            continue
        return value


def prompt_float(message: str, minimum: float = 0.0) -> float:
    """Ask until the user enters a valid number (>= minimum)."""
    while True:
        raw = input(message).strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            print("Error: please enter a number.")
            continue
        if value != value or value in (float("inf"), float("-inf")):
            print("Error: please enter a finite number.")
            continue
        if value < minimum:
            print(f"Error: value must be at least {minimum}.")
            continue
        return value


def print_products(products) -> None:
    """Print products as an aligned table."""
    if not products:
        print("The warehouse is empty.")
        return
    header = f"{'ID':>4}  {'Name':<25} {'Category':<15} {'Qty':>8} {'Price':>10}"
    print(header)
    print("-" * len(header))
    for p in products:
        print(
            f"{p['id']:>4}  {p['name'][:25]:<25} {(p['category'] or '-')[:15]:<15} "
            f"{p['quantity']:>8} {p['price']:>10.2f}"
        )


def add_product_action() -> None:
    name = input("Product name: ")
    category = input("Category (optional): ")
    quantity = prompt_int("Initial quantity: ", minimum=0)
    price = prompt_float("Price per unit: ")
    product_id = storage.add_product(name, category, quantity, price)
    print(f"Product added with ID {product_id}.")


def receive_action() -> None:
    product_id = prompt_int("Product ID: ", minimum=1)
    amount = prompt_int("Amount to receive: ", minimum=1)
    new_qty = storage.receive_stock(product_id, amount)
    print(f"Stock received. New quantity: {new_qty}.")


def issue_action() -> None:
    product_id = prompt_int("Product ID: ", minimum=1)
    amount = prompt_int("Amount to issue: ", minimum=1)
    new_qty = storage.issue_stock(product_id, amount)
    print(f"Stock issued. New quantity: {new_qty}.")


def list_action() -> None:
    print_products(storage.list_products())


def find_action() -> None:
    product_id = prompt_int("Product ID: ", minimum=1)
    print_products([storage.find_product(product_id)])


ACTIONS: dict[str, Callable[[], None]] = {
    "1": add_product_action,
    "2": receive_action,
    "3": issue_action,
    "4": list_action,
    "5": find_action,
}


def run() -> None:
    """Initialize the database and run the interactive menu loop."""
    try:
        database.init_db()
    except Exception as exc:
        print(f"Fatal: cannot initialize database: {exc}")
        return

    while True:
        print(MENU)
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if choice == "0":
            print("Goodbye!")
            return
        action = ACTIONS.get(choice)
        if action is None:
            print("Error: unknown option, choose 0-5.")
            continue
        try:
            action()
        except storage.WarehouseError as exc:
            print(f"Error: {exc}")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.")
