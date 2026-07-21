import pandas as pd
from database import get_connection

def get_rooms_by_floor(floor_id: int):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM rooms WHERE floor_id = ?", conn, params=(floor_id,))
    conn.close()
    return df