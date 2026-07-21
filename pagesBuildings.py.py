import streamlit as st
from components.buildings import render_buildings

st.set_page_config(page_title="Buildings", page_icon="🏢", layout="wide")
render_buildings()