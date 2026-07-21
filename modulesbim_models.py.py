import pandas as pd
from database import get_connection

def fetch_all_bim_models():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM bim_models ORDER BY id DESC", conn)
    conn.close()
    return df