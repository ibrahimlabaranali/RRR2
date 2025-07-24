# streamlit_login.py

import streamlit as st
import requests

# ================================
# 🔐 Backend Configuration
# ================================
API_URL = "https://your-backend-name.up.railway.app/auth/login"

# ================================
# 🚪 Login Page UI
# ================================
st.title("🔐 Road Risk Reporter - Login")
st.markdown("Welcome back. Please enter your credentials to continue.")

# Login form
with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    submitted = st.form_submit_button("Login")

# ================================
# 🚀 Handle Login Submission
# ================================
if submitted:
    if not username or not password:
        st.warning("Please enter both username and password.")
    else:
        with st.spinner("Authenticating..."):
            try:
                response = requests.post(API_URL, json={"username": username, "password": password})
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    st.session_state["auth_token"] = token
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.success(f"✅ Login successful. Welcome, {username}!")
                    st.balloons()
                else:
                    error = response.json().get("detail", "Login failed.")
                    st.error(f"❌ {error}")
            except Exception as e:
                st.error(f"⚠️ Error connecting to server: {e}")

# ================================
# 🧠 Logged-in State
# ================================
if st.session_state.get("logged_in"):
    st.success(f"You are logged in as **{st.session_state['username']}**.")
    st.markdown("➡️ [Go to dashboard](./dashboard)")
