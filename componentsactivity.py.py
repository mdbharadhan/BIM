import streamlit as st
import pandas as pd
from database import get_connection

def render_activity_stream():
    """Renders audit trails and user activity logs."""
    st.markdown("### 📜 System Activity Logs")
    conn = get_connection()
    df_logs = pd.read_sql_query("SELECT timestamp, username, action, details FROM activity_logs ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    
    if df_logs.empty:
        st.info("No activity logged in current session.")
    else:
        st.dataframe(df_logs, use_container_width=True, hide_index=True)