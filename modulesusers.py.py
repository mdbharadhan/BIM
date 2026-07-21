import sqlite3
from database import get_connection

def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT id, username, full_name, email, role FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]

def create_user(username, password, full_name, email, role="Architect"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
        (username, password, full_name, email, role)
    )
    conn.commit()
    conn.close()