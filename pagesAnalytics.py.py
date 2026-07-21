import streamlit as st
import plotly.express as px
from modules.analytics import get_structural_risk_distribution

st.set_page_config(page_title="BIM Analytics", page_icon="📈", layout="wide")

st.markdown("## 📈 Advanced Asset Telemetry & Analytics")

df_risk = get_structural_risk_distribution()
if not df_risk.empty:
    fig = px.pie(df_risk, names='risk_category', values='count', title='Structural Risk Levels', color_discrete_sequence=['#22C55E', '#F59E0B', '#EF4444'])
    st.plotly_chart(fig, use_container_width=True)