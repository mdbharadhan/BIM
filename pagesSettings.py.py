import streamlit as st
from components.settings import render_settings

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
render_settings()