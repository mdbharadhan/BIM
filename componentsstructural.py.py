import streamlit as st
import pandas as pd
from database import get_connection

def render_structural():
    st.markdown("## 🦴 Structural Integrity & Asset Health")
    st.caption("Sensors and inspection logs monitoring columns, beams, load-bearing walls, and slabs.")

    conn = get_connection()

    df_struct = pd.read_sql_query("""
        SELECT s.element_tag, b.name as building_name, s.category, s.material, s.health_index, s.status, s.last_inspection_date
        FROM structural_elements s
        JOIN buildings b ON s.building_id = b.id
    """, conn)

    if df_struct.empty:
        st.info("No structural elements logged.")
    else:
        # Display elements
        for _, row in df_struct.iterrows():
            health = row['health_index']
            color = "#22C55E" if health >= 90 else "#F59E0B" if health >= 75 else "#EF4444"
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); padding: 1rem; border-radius: 12px; margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: #38BDF8; font-weight: 700;">{row['element_tag']}</span>
                    <span style="margin-left: 10px; font-size: 0.85rem; color: #94A3B8;">[{row['category']}] &bull; {row['building_name']}</span>
                    <div style="font-size: 0.8rem; color: #CBD5E1; margin-top: 4px;">Material: <b>{row['material']}</b> | Last Inspected: {row['last_inspection_date']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.4rem; font-weight: 800; color: {color};">{health}%</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Health Index</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    conn.close()