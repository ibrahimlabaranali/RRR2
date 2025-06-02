import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

API_URL = "https://road-freight-risk-ai.onrender.com"

st.set_page_config(layout="wide")
st.title("🚚 Road Freight Risk AI Dashboard")

st.header("Submit New Report")
with st.form("risk_form"):
    category = st.selectbox("Risk Category", ["Armed Robbery", "Flooding", "Accident", "Protest", "Banditry", "Other"])
    location = st.text_input("Location (e.g., Kaduna - Abuja Highway)")
    notes = st.text_area("Additional Notes (Optional)")
    submitted = st.form_submit_button("Submit Report")

    if submitted:
        response = requests.post(f"{API_URL}/report", json={
            "category": category,
            "location": location,
            "notes": notes
        })
        if response.status_code == 200:
            st.success("✅ Report submitted successfully")
        else:
            st.error("❌ Failed to submit report")

st.header("🗺 View Reported Risks")
map = folium.Map(location=[10.5, 7.4], zoom_start=6)
risk_data = requests.get(f"{API_URL}/report/all").json()

for report in risk_data:
    folium.Marker(
        location=[report["latitude"], report["longitude"]],
        popup=f'{report["category"]}: {report["location"]}',
        icon=folium.Icon(color="red" if report["category"] == "Armed Robbery" else "blue")
    ).add_to(map)

st_folium(map, width=900)

