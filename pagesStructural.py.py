import streamlit as st
from components.structural import render_structural

st.set_page_config(page_title="Structural Integrity", page_icon="🦴", layout="wide")
render_structural()