import sqlite3
from config import DB_PATH

def test_database_connection():
    """Verify local database file connectivity."""
    conn = sqlite3.connect(DB_PATH)
    assert conn is not None
    conn.close()