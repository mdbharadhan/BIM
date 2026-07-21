import streamlit as st
import os
from config import UPLOADS_DIR, ALLOWED_EXTENSIONS

def render_file_upload_widget(target_subfolder: str = "ifc"):
    """Generic file uploader pipeline component."""
    uploaded_file = st.file_uploader(
        f"Upload BIM Asset ({', '.join(ALLOWED_EXTENSIONS)})", 
        type=ALLOWED_EXTENSIONS
    )
    if uploaded_file is not None:
        save_path = os.path.join(UPLOADS_DIR, target_subfolder, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded successfully to `{save_path}`")
        return save_path
    return None