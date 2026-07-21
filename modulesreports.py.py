import pandas as pd
from database import get_connection

def generate_compliance_report(dataset_name: str):
    conn = get_connection()
    if dataset_name == "Buildings":
        df = pd.read_sql_query("SELECT * FROM buildings", conn)
    elif dataset_name == "Structural":
        df = pd.read_sql_query("SELECT * FROM structural_elements", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM bim_models", conn)
    conn.close()
    return df