import streamlit as st
import pandas as pd
from database import get_connection

def render_buildings():
    st.markdown("## 🏢 Facility Inventory")
    st.caption("Registered buildings, campuses, and assignment managers.")

    conn = get_connection()

    df_b = pd.read_sql_query("SELECT code, name, campus, manager, status FROM buildings", conn)
    st.dataframe(df_b, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### ➕ Add New Building")
    with st.form("add_building_form"):
        c1, c2 = st.columns(2)
        code = c1.text_input("Building Code (e.g., BLD-03)")
        name = c2.text_input("Building Name")
        campus = c1.text_input("Campus Location")
        manager = c2.text_input("Facility Manager")
        
        if st.form_submit_button("Register Facility"):
            if code and name:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO buildings (code, name, campus, manager, status) VALUES (?, ?, ?, ?, 'Active')",
                               (code, name, campus, manager))
                conn.commit()
                st.success(f"Building '{name}' added successfully!")
                st.rerun()
            else:
                st.warning("Please fill required fields.")

    conn.close()