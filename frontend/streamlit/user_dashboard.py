# Streamlit user dashboard
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Road Freight Risk – User", layout="wide")
st.title("🛣️ Road Freight Risk Reporting")

st.info("Fill in the risk report form below")

with st.form("risk_form"):
    user_id = st.number_input("User ID", min_value=1, step=1)
    description = st.text_area("Describe the Incident", help="Describe what happened")
    location = st.text_input("Location Description", help="E.g. Kaduna-Zaria Expressway")
    submit = st.form_submit_button("Submit & Classify")

if submit:
    # Call classification API
    clf_response = requests.post("http://127.0.0.1:8000/classify/", json={"description": description})
    risk_type = clf_response.json()["risk_type"]

    # Dummy geo lookup (to be replaced by real LGA matching)
    geo_data = {
        "state": "Kaduna",
        "lga": "Zaria",
        "lat": 11.08,
        "lon": 7.72
    }

    report_data = {
        "user_id": user_id,
        "risk_type": risk_type,
        "description": description,
        "location": location,
        **geo_data
    }

    submit_response = requests.post("http://127.0.0.1:8000/report/", json=report_data)
    if submit_response.status_code == 200:
        st.success(f"✅ Report submitted as '{risk_type}'")
    else:
        st.error("❌ Submission failed")

# Map display
st.subheader("📍 Incident Map")
m = folium.Map(location=[10.5, 7.4], zoom_start=6)
folium.Marker([11.08, 7.72], popup="Kaduna-Zaria Expressway", tooltip="Sample").add_to(m)
st_folium(m, width=700)
