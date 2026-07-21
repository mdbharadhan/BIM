import streamlit as st
from components.ai_assistant import render_ai_assistant

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
render_ai_assistant()