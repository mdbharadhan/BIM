import streamlit as st
import pandas as pd
from database import get_connection

def render_reports():
    st.markdown("## 📑 Compliance & BIM Analytics Reports")[cite: 8]
    st.caption("Generate structured compliance data and exported audit logs.")[cite: 8]

    conn = get_connection()[cite: 8]

    report_type = st.selectbox("Select Report Dataset", ["Building Inventory", "Structural Health Summary", "BIM Model Registry", "System Activity Logs"])[cite: 8]

    if report_type == "Building Inventory":[cite: 8]
        df = pd.read_sql_query("SELECT code, name, campus, manager, status FROM buildings", conn)[cite: 8]
    elif report_type == "Structural Health Summary":[cite: 8]
        df = pd.read_sql_query("SELECT element_tag, category, material, health_index, status FROM structural_elements", conn)[cite: 8]
    elif report_type == "BIM Model Registry":[cite: 8]
        df = pd.read_sql_query("SELECT file_name, format, file_size_mb, version, status FROM bim_models", conn)[cite: 8]
    else:[cite: 8]
        df = pd.read_sql_query("SELECT timestamp, username, action, details FROM activity_logs", conn)[cite: 8]

    st.markdown("### Data Preview")[cite: 8]
    st.dataframe(df, use_container_width=True)[cite: 8]

    # Download Section
    csv_data = df.to_csv(index=False).encode('utf-8')[cite: 8]
    st.download_button(
        label=f"📥 Download {report_type} (CSV)",
        data=csv_data,
        file_name=f"{report_type.lower().replace(' ', '_')}_report.csv",
        mime="text/csv"
    )[cite: 8]

    conn.close()[cite: 8]