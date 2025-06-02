import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/login"  # Ensure your FastAPI login endpoint is at this path

st.set_page_config(page_title="User Login", page_icon="🔐")
st.title("🔐 Road Freight Risk AI - Login")

# Session init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = {}

# UI: Login form
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("⚠️ Please fill in both fields.")
        else:
            try:
                response = requests.post(API_URL, json={"username": username, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.user_data = data
                    st.success(f"✅ Welcome {data['username']}! Role: {data['role']}")
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid credentials")
            except Exception as e:
                st.error(f"🚨 Login failed: {e}")

# UI: Post-login view
if st.session_state.logged_in:
    user = st.session_state.user_data
    st.info(f"👤 Logged in as {user['username']} ({user['role']})")

    if user["role"] == "admin":
        st.success("🛠️ Access to Admin Dashboard")
    elif user["role"] == "driver":
        st.success("🚚 Access to Driver Risk Reporting")
    elif user["role"] == "viewer":
        st.success("📊 Access to Viewer Dashboard")
    else:
        st.warning("🔍 Role not recognized")

    # Logout button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_data = {}
        st.experimental_rerun()
