import streamlit as st
from database import get_connection

def render_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🏗️ Nexus BIM Automation Hub")
        st.markdown("#### Enterprise Infrastructure & Model Lifecycle Management")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submitted = st.form_submit_button("Sign In")

            if submitted:
                conn = get_connection()
                user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
                conn.close()

                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = dict(user)
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")