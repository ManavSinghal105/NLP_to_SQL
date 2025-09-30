import sqlite3

conn = sqlite3.connect("demo1.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    city TEXT,
    signup_date DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product TEXT,
    amount REAL,
    order_date DATE,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
)
""")


cursor.executemany("INSERT INTO customers (name, city, signup_date) VALUES (?, ?, ?)", [
    ("Alice", "New York", "2023-12-01"),
    ("Bob", "San Francisco", "2024-01-10"),
    ("Charlie", "New York", "2024-02-15")
])

cursor.executemany("INSERT INTO orders (customer_id, product, amount, order_date) VALUES (?, ?, ?, ?)", [
    (1, "Laptop", 1200, "2024-02-20"),
    (2, "Phone", 800, "2024-02-22"),
    (1, "Mouse", 25, "2024-02-25")
])

conn.commit()
conn.close()
