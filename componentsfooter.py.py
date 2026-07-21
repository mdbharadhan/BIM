import streamlit as st

def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 0.8rem; padding: 1rem 0;">
        Nexus BIM Automation Hub &bull; Enterprise Infrastructure Management &bull; v2.4.0<br>
        &copy; 2026 Nexus Systems Inc. All rights reserved.
    </div>
    """, unsafe_allow_html=True)