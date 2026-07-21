import pandas as pd

def fetch_inspection_logs():
    return pd.DataFrame([
        {"inspection_id": "INSP-2026-01", "inspector": "Sarah Jenkins", "date": "2026-06-15", "rating": "Pass"},
        {"inspection_id": "INSP-2026-02", "inspector": "David Miller", "date": "2026-07-01", "rating": "Requires Action"}
    ])