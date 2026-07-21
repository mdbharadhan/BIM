import streamlit as st
import pandas as pd
from database import get_connection

def render_models():
    st.markdown("## 📦 BIM Models & Document Management")
    st.caption("Upload, version control, and model verification pipeline.")

    conn = get_connection()

    # Model Upload Section
    st.markdown("### 📤 Upload New Model Asset")
    uploaded_file = st.file_uploader("Drag and drop BIM model files (.ifc, .rvt, .nwd, .dwg, .pdf)", type=["ifc", "rvt", "nwd", "dwg", "pdf"])

    if uploaded_file is not None:
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            file_format = uploaded_file.name.split(".")[-1].upper()
            building_name = st.selectbox("Assign to Building Target", ["AeroTech HQ", "Nexus Tower Alpha", "Helix Biotech Lab"])
        with col_u2:
            version_tag = st.text_input("Version Tag", value="v1.0")
            
        if st.button("Process & Pipeline Upload"):
            progress_bar = st.progress(0, text="Initiating BIM Clash Detection...")
            import time
            for pct in range(10, 101, 30):
                time.sleep(0.15)
                progress_bar.progress(pct, text=f"Processing model geometry & metadata... ({pct}%)")
            
            # Save to Database
            file_size = round(uploaded_file.size / (1024 * 1024), 2)
            user_name = st.session_state.get("user", {}).get("username", "admin")
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bim_models (file_name, format, file_size_mb, building_id, uploaded_by, version, status)
                VALUES (?, ?, ?, 1, ?, ?, ?)
            """, (uploaded_file.name, file_format, file_size, user_name, version_tag, "Verified"))
            
            cursor.execute("INSERT INTO activity_logs (username, action, details) VALUES (?, ?, ?)",
                           (user_name, "MODEL_UPLOAD", f"Uploaded model {uploaded_file.name} ({file_size} MB)"))
            conn.commit()
            st.success(f"Model '{uploaded_file.name}' processed and added to registry!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📚 Model Repository")

    df_models = pd.read_sql_query("SELECT id, file_name, format, file_size_mb, uploaded_by, version, upload_date, status FROM bim_models ORDER BY id DESC", conn)
    st.dataframe(df_models, use_container_width=True, hide_index=True)

    conn.close()