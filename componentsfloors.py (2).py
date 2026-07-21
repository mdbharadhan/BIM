import streamlit as st
import pandas as pd
from database import get_connection

def render_floors():
    st.markdown("## 📐 Floor Plan & Spatial Registry")
    st.caption("Level-by-level breakdown across all facilities.")

    conn = get_connection()

    df_f = pd.read_sql_query("""
        SELECT f.floor_number, f.name as floor_name, b.name as building_name, f.area_sqm
        FROM floors f
        JOIN buildings b ON f.building_id = b.id
    """, conn)

    if not df_f.empty:
        st.dataframe(df_f, use_container_width=True, hide_index=True)
    else:
        st.info("No floor levels registered.")

    conn.close()