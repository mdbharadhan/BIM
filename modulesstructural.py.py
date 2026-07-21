import pandas as pd
from database import get_connection

def fetch_structural_elements():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM structural_elements", conn)
    conn.close()
    return df