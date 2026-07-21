import streamlit as st

def render_navbar():
    user = st.session_state.get("user", {})
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🏗️ **Nexus BIM Hub** &nbsp;|&nbsp; <span style='font-size:1rem; color:#94A3B8;'>Enterprise Management</span>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"👤 **{user.get('full_name', 'User')}** ({user.get('role', 'Member')})")
        if st.button("Logout", key="nav_logout_btn"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()
    st.markdown("---")