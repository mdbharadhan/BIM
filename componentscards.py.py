import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = None, color: str = "#38BDF8"):
    """Renders a custom enterprise KPI card."""
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;">
        <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: {color}; margin-top: 4px;">{value}</div>
        {f'<div style="font-size: 0.8rem; color: #22C55E; margin-top: 4px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)