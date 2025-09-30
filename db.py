import sqlite3
from pathlib import Path
import subprocess, sys

def get_connection(db_name="demo1.db"):
    """Return SQLite connection, auto-seed if db missing."""
    if not Path(db_name).exists():
        subprocess.run([sys.executable, "seed_db.py"], check=True)
    return sqlite3.connect(db_name)

def extract_schema(db_name="demo1.db"):
    """Extract schema info for all tables in db."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    schema_info = []
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        col_str = ", ".join([f"{c[1]} ({c[2]})" for c in columns])
        schema_info.append(f"Table {table_name}: {col_str}")

    conn.close()
    return schema_info
