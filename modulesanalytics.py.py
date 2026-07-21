import pandas as pd
from database import get_connection

def get_structural_risk_distribution():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT 
            CASE 
                WHEN health_index >= 90 THEN 'Optimal (>=90%)'
                WHEN health_index >= 75 THEN 'Warning (75-89%)'
                ELSE 'Critical (<75%)'
            END as risk_category,
            COUNT(*) as count
        FROM structural_elements
        GROUP BY risk_category
    """, conn)
    conn.close()
    return df