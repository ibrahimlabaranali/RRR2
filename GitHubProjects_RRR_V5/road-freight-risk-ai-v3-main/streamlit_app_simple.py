import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="🚛 Road Freight Risk AI",
    page_icon="🚛",
    layout="wide"
)

# Main header
st.title("🚛 Road Freight Risk AI")
st.markdown("### 📱 Mobile-Optimized Risk Reporting System")

# Simple login form
st.header("🔐 Login")
with st.form("login_form"):
    nin = st.text_input("NIN", max_chars=11)
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")
    
    if submit:
        if nin and password:
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"nin": nin, "password": password},
                    timeout=10
                )
                if response.status_code == 200:
                    st.success("✅ Login successful!")
                else:
                    st.error("❌ Login failed")
            except:
                st.error("🌐 Connection error")
        else:
            st.error("❌ Please fill all fields")

# Simple report form
st.header("📍 Submit Risk Report")
with st.form("report_form"):
    location = st.text_input("Location")
    risk_type = st.selectbox("Risk Type", ["Flooding", "Robbery", "Protest", "Road Block", "Other"])
    description = st.text_area("Description")
    submit_report = st.form_submit_button("Submit Report")
    
    if submit_report:
        if location and description:
            st.success("✅ Report submitted!")
        else:
            st.error("❌ Please fill all fields")

# Footer
st.markdown("---")
st.markdown("🚛 Road Freight Risk AI v3.0 | Optimized for Streamlit Cloud") 