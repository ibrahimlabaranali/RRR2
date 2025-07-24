# pages/admin_register.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="🛡 Admin Registration", layout="centered")
st.title("🛡 Register New Admin")

admin_access = st.text_input("Admin Access Code", type="password")
username = st.text_input("Full Name")
nin = st.text_input("Admin NIN", max_chars=11)
password = st.text_input("Create Password", type="password")

if st.button("Register Admin"):
    if admin_access != "sahel-admin-2024":
        st.error("❌ Invalid Admin Access Code.")
    elif username and nin and password:
        try:
            res = requests.post(f"{API_URL}/auth/register", json={
                "username": username,
                "nin": nin,
                "password": password,
                "role": "admin"
            })
            if res.status_code == 200:
                st.success("✅ Admin registered successfully.")
            else:
                st.error(f"❌ {res.json().get('detail', 'Registration failed.')}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    else:
        st.warning("⚠ Please fill all fields.")
