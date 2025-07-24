# pages/forgot_password.py

import streamlit as st
import requests
import re
import os
from dotenv import load_dotenv

# 🌍 Load API endpoint
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# 📄 Page Setup
st.set_page_config(page_title="🔐 Forgot Password", layout="centered")
st.title("🔐 Reset Your Password")

# 🧾 Instructions
st.markdown("""
If you’ve forgotten your password, enter the email address you registered with.
We’ll send a password reset link if it’s valid.
""")

# 📧 Email Form
email = st.text_input("📧 Enter your registered email")

# ✅ Email Format Validator
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# 🚀 Submit Button
if st.button("📩 Send Reset Link"):
    if not email:
        st.warning("⚠️ Please enter your email.")
    elif not is_valid_email(email):
        st.error("❌ Invalid email format.")
    else:
        try:
            response = requests.post(f"{API_URL}/auth/forgot-password", json={"email": email})
            if response.status_code == 200:
                st.success("✅ A password reset link has been sent to your email.")
            elif response.status_code == 404:
                st.error("❌ Email not found. Please enter a valid registered email.")
            else:
                st.error("⚠️ Something went wrong. Please try again later.")
        except Exception as e:
            st.error(f"🚫 Network error: {e}")

# 🔙 Back to login
st.markdown("---")
st.page_link("pages/user_login.py", label="🔐 Back to Login")
