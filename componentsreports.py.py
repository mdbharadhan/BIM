import streamlit as st
import pandas as pd
from database import get_connection

def render_reports():
    st.markdown("## 📑 Compliance & BIM Analytics Reports")
    st.caption("Generate structured compliance data and exported audit logs.")

    conn = get_connection()

    report_type = st.selectbox("Select Report Dataset", ["Building Inventory", "Structural Health Summary", "BIM Model Registry", "System Activity Logs"])

    if report_type == "Building Inventory":
        df = pd.read_sql_query("SELECT code, name, campus, manager, status FROM buildings", conn)
    elif report_type == "Structural Health Summary":
        df = pd.read_sql_query("SELECT element_tag, category, material, health_index, status FROM structural_elements", conn)
    elif report_type == "BIM Model Registry":
        df = pd.read_sql_query("SELECT file_name, format, file_size_mb, version, status FROM bim_models", conn)
    else:
        df = pd.read_sql_query("SELECT timestamp, username, action, details FROM activity_logs", conn)

    st.markdown("### Data Preview")
    st.dataframe(df, use_container_width=True)

    # Download Section
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {report_type} (CSV)",
        data=csv_data,
        file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
        mime="text/csv"
    )

    conn.close()