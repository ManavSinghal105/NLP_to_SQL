import sqlite3
from pathlib import Path

DB = Path("demo1.db")

schema = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    city TEXT,
    signup_date DATE
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product TEXT,
    amount REAL,
    order_date DATE,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);
"""

seed_customers = [
    ("Alice",   "New York",        "2023-12-01"),
    ("Bob",     "San Francisco",   "2024-01-10"),
    ("Charlie", "New York",        "2024-02-15"),
]

seed_orders = [
    (1, "Laptop", 1200, "2024-02-20"),
    (2, "Phone",   800, "2024-02-22"),
    (1, "Mouse",    25, "2024-02-25"),
]

def main():
    first_time = not DB.exists()
    conn = sqlite3.connect(DB.as_posix())
    cur = conn.cursor()
    cur.executescript(schema)
    if first_time:
        cur.executemany("INSERT INTO customers (name, city, signup_date) VALUES (?, ?, ?)", seed_customers)
        cur.executemany("INSERT INTO orders (customer_id, product, amount, order_date) VALUES (?, ?, ?, ?)", seed_orders)
        print("✅ Created demo1.db and inserted sample data.")
    else:
        print("ℹ️ demo1.db already exists; left as-is.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
