import streamlit as st

def render_sidebar():
    st.sidebar.title("📌 Navigation")
    
    pages = [
        "Dashboard",
        "Buildings",
        "Floors",
        "Structural",
        "BIM Models",
        "Reports",
        "AI Assistant",
        "Settings"
    ]
    
    selected_page = st.sidebar.radio("Go to", pages)
    st.sidebar.markdown("---")
    st.sidebar.caption("Nexus BIM Platform v2.4.0\n© 2026 Nexus Systems")
    
    return selected_page