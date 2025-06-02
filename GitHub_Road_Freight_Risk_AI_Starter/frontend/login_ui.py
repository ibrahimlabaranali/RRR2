import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/auth/login"

st.title("🔐 User Login - Road Freight Risk AI")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not username or not password:
        st.warning("Please fill in both fields.")
    else:
        response = requests.post(API_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Logged in successfully!")
            st.session_state["access_token"] = data["access_token"]
            st.session_state["role"] = data["role"]
        else:
            st.error("❌ Invalid credentials")
