import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection

def render_dashboard():
    st.markdown("## 📊 Executive Overview")
    st.caption("Real-time telemetry across registered facilities, BIM models, and structural health alerts.")

    conn = get_connection()

    b_count = conn.execute("SELECT COUNT(*) FROM buildings").fetchone()[0]
    m_count = conn.execute("SELECT COUNT(*) FROM bim_models").fetchone()[0]
    s_count = conn.execute("SELECT COUNT(*) FROM structural_elements WHERE health_index < 80").fetchone()[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Facilities", b_count)
    c2.metric("Active BIM Models", m_count)
    c3.metric("Structural Risk Alerts", s_count, delta_color="inverse")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Structural Health Distribution")
        df_struct = pd.read_sql_query("SELECT element_tag, health_index FROM structural_elements", conn)
        if not df_struct.empty:
            fig = px.bar(df_struct, x='element_tag', y='health_index', color='health_index',
                         color_continuous_scale='RdYlGn', range_y=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Model Storage Breakdown (MB)")
        df_models = pd.read_sql_query("SELECT file_name, file_size_mb FROM bim_models", conn)
        if not df_models.empty:
            fig_pie = px.pie(df_models, names='file_name', values='file_size_mb', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    conn.close()