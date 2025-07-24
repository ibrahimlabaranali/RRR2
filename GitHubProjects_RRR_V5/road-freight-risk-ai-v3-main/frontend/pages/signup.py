# streamlit_signup.py

import streamlit as st
import requests

# ===========================
# 🔗 Backend API Endpoint
# ===========================
API_URL = "https://your-backend-name.up.railway.app/auth/register"  # Replace with your real URL

# ===========================
# 📋 Page Title & Instructions
# ===========================
st.title("📝 Register for Road Risk Reporter")
st.markdown("Please fill out the form below to create your account.")

# ===========================
# 📥 Registration Form
# ===========================
with st.form("signup_form"):
    username = st.text_input("Username", placeholder="Choose a username")
    password = st.text_input("Password", type="password", placeholder="Choose a strong password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")
    nin = st.text_input("National Identification Number (NIN)", max_chars=11)
    role = st.selectbox("Select Role", ["user", "admin"])

    submit = st.form_submit_button("Create Account")

# ===========================
# 🚀 Handle Form Submission
# ===========================
if submit:
    if not username or not password or not confirm_password or not nin:
        st.warning("Please fill in all fields.")
    elif password != confirm_password:
        st.error("❌ Passwords do not match.")
    elif len(password) < 6:
        st.warning("🔒 Password should be at least 6 characters.")
    elif not nin.isdigit() or len(nin) != 11:
        st.warning("🆔 NIN must be 11 digits.")
    else:
        with st.spinner("Creating your account..."):
            try:
                response = requests.post(API_URL, json={
                    "username": username,
                    "password": password,
                    "nin": nin,
                    "role": role
                })

                if response.status_code == 200 or response.status_code == 201:
                    st.success("✅ Account created successfully! You can now log in.")
                    st.balloons()
                else:
                    error_msg = response.json().get("detail", "Registration failed. Please try again.")
                    st.error(f"❌ {error_msg}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
