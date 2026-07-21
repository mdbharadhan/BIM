import streamlit as st
from components.notifications import render_notifications_feed

st.set_page_config(page_title="Notifications", page_icon="🔔", layout="wide")
render_notifications_feed()