import streamlit as st

def render_summary_metrics(building_count: int, model_count: int, risk_count: int):
    """Displays high-level executive summary metrics."""
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Facilities Registered", building_count)
    c2.metric("Active BIM Asset Models", model_count)
    c3.metric("Structural Health Risk Alerts", risk_count, delta_color="inverse")