import streamlit as st
from components.floors import render_floors

st.set_page_config(page_title="Floors", page_icon="📐", layout="wide")
render_floors()