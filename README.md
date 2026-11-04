# Smart Warehouse — Inventory Management System

A command-line interface (CLI) application for warehouse inventory tracking and management backed by a local SQLite database.

## Key Features
- **Product Management**: Add new products with initial quantities and price.
- **Stock In / Stock Out**: Record incoming shipments and customer dispatches.
- **Stock Deficit Protection**: Built-in validation prevents dispensing more stock than is available.
- **Inventory Overview**: View formatted tables of all items and their quantities.
- **Search by ID**: Rapid product lookup with detailed attribute inspection.
- **Persistent Storage**: All changes are safely committed to a local SQLite relational database.
- **Input Validation & Error Handling**: Graceful handling of invalid user inputs and database constraints.

## Tech Stack
- **Language**: Python 3
- **Database**: SQLite3 / SQL
- **Interface**: CLI (Terminal UI)

## Getting Started

### Prerequisites
- Python 3.8+ installed.

### Running the Application
```bash
python main.py
```
