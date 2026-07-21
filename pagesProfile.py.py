import streamlit as st

st.set_page_config(page_title="User Profile", page_icon="👤", layout="wide")

st.markdown("## 👤 User Profile & Access Control")

user = st.session_state.get("user", {"username": "admin", "full_name": "Alex Mercer", "role": "Lead BIM Architect", "email": "alex.mercer@nexusbim.io"})

c1, c2 = st.columns(2)
with c1:
    st.text_input("Full Name", value=user.get("full_name"), disabled=True)
    st.text_input("Username", value=user.get("username"), disabled=True)
with c2:
    st.text_input("Email", value=user.get("email"), disabled=True)
    st.text_input("Assigned Role", value=user.get("role"), disabled=True)