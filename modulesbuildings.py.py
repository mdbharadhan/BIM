import pandas as pd
from database import get_connection

def fetch_all_buildings():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM buildings", conn)
    conn.close()
    return df

def add_building(code: str, name: str, campus: str, manager: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO buildings (code, name, campus, manager, status) VALUES (?, ?, ?, ?, 'Active')",
        (code, name, campus, manager)
    )
    conn.commit()
    conn.close()