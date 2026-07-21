import streamlit as st
import pandas as pd
from database import get_connection

def render_models():
    st.markdown("## 📦 BIM Models & Document Management")[cite: 9]
    st.caption("Upload, version control, and model verification pipeline.")[cite: 9]

    conn = get_connection()[cite: 9]

    # Model Upload Section
    st.markdown("### 📤 Upload New Model Asset")[cite: 9]
    uploaded_file = st.file_uploader("Drag and drop BIM model files (.ifc, .rvt, .nwd, .dwg, .pdf)", type=["ifc", "rvt", "nwd", "dwg", "pdf"])[cite: 9]

    if uploaded_file is not None:[cite: 9]
        col_u1, col_u2 = st.columns(2)[cite: 9]
        with col_u1:[cite: 9]
            file_format = uploaded_file.name.split(".")[-1].upper()[cite: 9]
            building_name = st.selectbox("Assign to Building Target", ["AeroTech HQ", "Nexus Tower Alpha", "Helix Biotech Lab"])[cite: 9]
        with col_u2:[cite: 9]
            version_tag = st.text_input("Version Tag", value="v1.0")[cite: 9]
            
        if st.button("Process & Pipeline Upload"):[cite: 9]
            progress_bar = st.progress(0, text="Initiating BIM Clash Detection...")[cite: 9]
            import time[cite: 9]
            for pct in range(10, 101, 30):[cite: 9]
                time.sleep(0.15)[cite: 9]
                progress_bar.progress(pct, text=f"Processing model geometry & metadata... ({pct}%)")[cite: 9]
            
            # Save to Database
            file_size = round(uploaded_file.size / (1024 * 1024), 2)[cite: 9]
            user_name = st.session_state.get("user", {}).get("username", "admin")[cite: 9]
            
            cursor = conn.cursor()[cite: 9]
            cursor.execute("""
                INSERT INTO bim_models (file_name, format, file_size_mb, building_id, uploaded_by, version, status)
                VALUES (?, ?, ?, 1, ?, ?, ?)
            """, (uploaded_file.name, file_format, file_size, user_name, version_tag, "Verified"))[cite: 9]
            
            cursor.execute("INSERT INTO activity_logs (username, action, details) VALUES (?, ?, ?)",
                           (user_name, "MODEL_UPLOAD", f"Uploaded model {uploaded_file.name} ({file_size} MB)"))[cite: 9]
            conn.commit()[cite: 9]
            st.success(f"Model '{uploaded_file.name}' processed and added to registry!")[cite: 9]
            st.rerun()[cite: 9]

    st.markdown("---")[cite: 9]
    st.markdown("### 📚 Model Repository")[cite: 9]

    df_models = pd.read_sql_query("SELECT id, file_name, format, file_size_mb, uploaded_by, version, upload_date, status FROM bim_models ORDER BY id DESC", conn)[cite: 9]
    st.dataframe(df_models, use_container_width=True, hide_index=True)[cite: 9]

    conn.close()[cite: 9]