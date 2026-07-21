import streamlit as st
import pandas as pd

def render_custom_table(df: pd.DataFrame, title: str = "Data Registry"):
    """Styled dataframe renderer."""
    st.markdown(f"### {title}")
    if df.empty:
        st.warning("No records found.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)