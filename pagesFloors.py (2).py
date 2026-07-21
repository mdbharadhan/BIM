import streamlit as st
from components.models import render_models

st.set_page_config(page_title="BIM Models", page_icon="📦", layout="wide")
render_models()