import streamlit as st
import os

# Page Configuration - Enterprise Setup
st.set_page_config(
    page_title="Nexus BIM Automation Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
from database import init_db
init_db()

# Load Custom Enterprise CSS
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Component Imports
from components.login import render_login_page
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.buildings import render_buildings
from components.floors import render_floors
from components.structural import render_structural
from components.models import render_models
from components.reports import render_reports
from components.ai_assistant import render_ai_assistant
from components.settings import render_settings

# Session Authentication State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def main():
    if not st.session_state["authenticated"]:
        render_login_page()
    else:
        # Render Navigation & Layout Components
        render_navbar()
        selected_page = render_sidebar()
        
        # Route Pages
        if selected_page == "Dashboard":
            render_dashboard()
        elif selected_page == "Buildings":
            render_buildings()
        elif selected_page == "Floors":
            render_floors()
        elif selected_page == "Structural":
            render_structural()
        elif selected_page == "BIM Models":
            render_models()
        elif selected_page == "Reports":
            render_reports()
        elif selected_page == "AI Assistant":
            render_ai_assistant()
        elif selected_page == "Settings":
            render_settings()

if __name__ == "__main__":
    main()