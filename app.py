import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Road Freight Risk AI", layout="wide")
st.title("🚛 Road Freight Risk Reporting System")

API_URL = "http://localhost:8000"

def submit_report():
    with st.form("report_form"):
        name = st.text_input("Your Name")
        risk_type = st.selectbox("Select Risk Type", ["Accident", "Flooding", "Robbery", "Bad Road", "Other"])
        description = st.text_area("Description")
        location = st.text_input("Exact Location")
        lga = st.text_input("Local Government Area (LGA)")
        lat = st.number_input("Latitude", format="%.6f")
        lon = st.number_input("Longitude", format="%.6f")
        submitted = st.form_submit_button("Submit")
        if submitted:
            data = {
                "reporter_name": name,
                "risk_type": risk_type,
                "description": description,
                "location": location,
                "lga": lga,
                "latitude": lat,
                "longitude": lon
            }
            res = requests.post(f"{API_URL}/report", json=data)
            if res.status_code == 200:
                st.success("✅ Report submitted successfully")
            else:
                st.error("❌ Failed to submit report")

def view_reports():
    st.subheader("All Submitted Reports")
    res = requests.get(f"{API_URL}/reports")
    if res.status_code == 200:
        reports = res.json()
        df = pd.DataFrame(reports)
        st.dataframe(df)
        st.map(df[["latitude", "longitude"]])
    else:
        st.error("Failed to fetch reports")

tab1, tab2 = st.tabs(["📨 Submit Report", "📍 View Reports"])

with tab1:
    submit_report()

with tab2:
    view_reports()
