import streamlit as st
from database import get_connection

def render_settings():
    st.markdown("## ⚙️ System Configuration")
    st.caption("Workspace preferences, integration webhooks, and security settings.")

    user = st.session_state.get("user", {})

    st.markdown("### User Profile")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Full Name", value=user.get("full_name", ""))
        st.text_input("Email Address", value=user.get("email", ""))
    with c2:
        st.text_input("Role", value=user.get("role", ""), disabled=True)
        st.text_input("Username", value=user.get("username", ""), disabled=True)

    st.markdown("---")
    st.markdown("### Cloud & BIM Engine Integration")
    st.checkbox("Enable Autodesk ACC Auto-Sync", value=True)
    st.checkbox("Enable Automated Clash Detection on Upload", value=True)
    st.checkbox("Send Slack / Teams Notifications for Structural Risk Alerts", value=False)

    if st.button("Save Settings"):
        st.success("Configuration preferences updated successfully!")