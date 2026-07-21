import streamlit as st
from components.reports import render_reports

st.set_page_config(page_title="Reports", page_icon="📑", layout="wide")
render_reports()