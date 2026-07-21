import pandas as pd
from database import get_connection

def fetch_floors_by_building(building_id: int):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM floors WHERE building_id = ?", conn, params=(building_id,))
    conn.close()
    return df