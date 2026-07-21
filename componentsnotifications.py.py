import streamlit as st

def render_notifications_feed():
    """Renders active system alerts and notifications."""
    st.markdown("### 🔔 Active System Alerts")
    alerts = [
        {"type": "error", "msg": "CRITICAL: Beam BEAM-B04 health index dropped below threshold (78%)."},
        {"type": "info", "msg": "INFO: New model 'Aerotech_Arch_v2.ifc' uploaded and verified."},
        {"type": "success", "msg": "SUCCESS: Autodesk Construction Cloud auto-sync completed."}
    ]
    for alert in alerts:
        if alert["type"] == "error":
            st.error(alert["msg"])
        elif alert["type"] == "info":
            st.info(alert["msg"])
        elif alert["type"] == "success":
            st.success(alert["msg"])