import streamlit as st

def render_site_weather_widget():
    st.markdown("### 🌤️ Jobsite Environmental Telemetry")
    c1, c2, c3 = st.columns(3)
    c1.metric("Site Temp", "28°C", "Sunny")
    c2.metric("Wind Speed", "12 km/h", "Safe Crane Operations")
    c3.metric("Humidity", "65%", "Nominal Concrete Curing")