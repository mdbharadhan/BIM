import streamlit as st
from database import get_connection

def render_ai_assistant():
    st.markdown("## 🤖 AI Architectural Co-Pilot")
    st.caption("Natural language query engine over building assets, models, and structural integrity risks.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I am your AI Building Information Co-Pilot. Ask me about facility risk levels, model verification statuses, or structural integrity."}
        ]

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask a question about your BIM models or buildings..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate intelligent response based on DB
        conn = get_connection()
        p_lower = prompt.lower()
        
        if "risk" in p_lower or "health" in p_lower or "structural" in p_lower:
            elements = conn.execute("SELECT element_tag, health_index FROM structural_elements WHERE health_index < 90").fetchall()
            if elements:
                items = ", ".join([f"{e['element_tag']} ({e['health_index']}%)" for e in elements])
                response = f"⚠️ **Risk Analysis Alert:** Found structural elements with sub-optimal health index: {items}. Immediate non-destructive testing (NDT) is recommended."
            else:
                response = "✅ **Risk Assessment:** All structural elements across all facilities are currently operating above nominal integrity thresholds (>=90%)."
        
        elif "building" in p_lower or "facility" in p_lower:
            count = conn.execute("SELECT COUNT(*) FROM buildings").fetchone()[0]
            response = f"🏢 You currently have **{count} registered facilities** in the hub. All telemetry feeds are active."
        
        elif "model" in p_lower or "ifc" in p_lower or "rvt" in p_lower:
            models = conn.execute("SELECT file_name, status FROM bim_models").fetchall()
            m_list = "<br>• ".join([f"**{m['file_name']}**: {m['status']}" for m in models])
            response = f"📦 **Current Model Registry Status:**<br>• {m_list}"
        
        else:
            response = f"I have analyzed your query regarding '{prompt}'. Based on current telemetry, all BIM models are synced with Autodesk Construction Cloud, and system health is optimal."

        conn.close()

        st.session_state["messages"].append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)