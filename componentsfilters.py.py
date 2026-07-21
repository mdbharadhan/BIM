import streamlit as st

def render_facility_filter(building_names: list):
    """Dropdown filter component for facility targets."""
    return st.selectbox("Select Target Facility", ["All Facilities"] + building_names)