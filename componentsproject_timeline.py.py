import streamlit as st

def render_project_timeline():
    """Gantt / milestone timeline component."""
    st.markdown("### 📅 Construction & Inspection Milestones")
    st.markdown("""
    - **Q1 2026**: Structural Non-Destructive Testing (NDT) Phase I `[Completed]`
    - **Q2 2026**: BIM Model Geometry Clash Verification `[Completed]`
    - **Q3 2026**: Sensor Health Index Calibration `[In Progress]`
    - **Q4 2026**: Compliance Audit & Final Handover `[Scheduled]`
    """)