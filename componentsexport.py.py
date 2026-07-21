import streamlit as st
import pandas as pd

def render_export_button(df: pd.DataFrame, file_label: str = "dataset"):
    """CSV export helper button."""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {file_label.title()} (CSV)",
        data=csv,
        file_name=f"{file_label.lower().replace(' ', '_')}.csv",
        mime='text/csv'
    )