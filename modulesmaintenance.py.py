import pandas as pd

def fetch_maintenance_tickets():
    return pd.DataFrame([
        {"ticket_id": "TCK-101", "asset": "BEAM-B04", "priority": "High", "status": "Open"},
        {"ticket_id": "TCK-102", "asset": "COL-A12", "priority": "Low", "status": "Resolved"}
    ])