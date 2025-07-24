# pages/user_login.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="🔐 User Login", layout="centered")
st.title("🔐 Login (User)")

nin = st.text_input("NIN", max_chars=11)
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        res = requests.post(f"{API_URL}/auth/login", json={"nin": nin, "password": password})
        if res.status_code == 200:
            user = res.json()
            if user["role"] == "user":
                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.role = "user"
                st.success("✅ Welcome, user.")
                st.switch_page("mobile/streamlit_app_mobile.py")
            else:
                st.error("⚠ This is not a user account.")
        else:
            st.error("❌ Invalid credentials.")
    except Exception as e:
        st.error(f"⚠ Login error: {e}")
