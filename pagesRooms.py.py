import streamlit as st
import pandas as pd
from database import get_connection

st.set_page_config(page_title="Room Registry", page_icon="🚪", layout="wide")

st.markdown("## 🚪 Space & Room Registry")
st.caption("Detailed room allocation, spatial metrics, and functional capacity.")

conn = get_connection()
df_rooms = pd.read_sql_query("""
    SELECT r.room_number, r.purpose, r.capacity, f.floor_number, b.name as building_name
    FROM rooms r
    JOIN floors f ON r.floor_id = f.id
    JOIN buildings b ON f.building_id = b.id
""", conn)

if not df_rooms.empty:
    st.dataframe(df_rooms, use_container_width=True, hide_index=True)
else:
    st.info("No spatial room data currently cataloged.")

conn.close()