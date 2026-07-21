import streamlit as st
from components.dashboard import render_dashboard

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
render_dashboard()