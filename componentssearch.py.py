import streamlit as st

def render_search_bar(placeholder: str = "Search assets, tags, or models..."):
    """Search input field component."""
    return st.text_input("🔍 Search", placeholder=placeholder)