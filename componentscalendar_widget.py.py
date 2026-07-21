import streamlit as st
import datetime

def render_inspection_calendar():
    """Renders upcoming inspection dates widget."""
    st.markdown("### 🗓️ Scheduled Maintenance Calendar")
    selected_date = st.date_input("Select Inspection Date", datetime.date.today())
    st.info(f"Showing scheduled events for: **{selected_date}**")