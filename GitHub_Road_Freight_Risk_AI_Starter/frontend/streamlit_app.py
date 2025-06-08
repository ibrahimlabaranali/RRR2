import streamlit as st
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://road-freight-risk-ai.onrender.com")

st.set_page_config(page_title="Road Freight Risk AI", layout="centered")

# ---------- Title and Description ----------
st.title("🚚 Road Freight Risk AI – Home")
st.markdown("""
Welcome to the **Road Freight Risk AI System** – an intelligent platform for reporting, viewing, and analyzing transport risks across Nigeria.

**🛡 Key Features:**
- Smart GPS detection and offline fallback
- Role-based dashboards for Admins and Drivers
- Secure login with NIN verification
- Real-time visualisation and CSV downloads
- SMS fallback reporting
""")

# ---------- Check Backend Connection ----------
try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        st.success("✅ Backend is live and connected.")
    else:
        st.warning("⚠️ Backend API not responding as expected.")
except Exception as e:
    st.error(f"🚫 Cannot connect to backend: {e}")

# ---------- Session State Setup ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# ---------- Redirect Logged-in Users ----------
if st.session_state.authenticated:
    st.success(f"Welcome back, {st.session_state.username} ({st.session_state.role})")

    if st.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    if st.session_state.role == "admin":
        with st.spinner("Redirecting to admin dashboard..."):
            time.sleep(1)
            st.switch_page("pages/admin_dashboard.py")
    elif st.session_state.role == "user":
        with st.spinner("Redirecting to user dashboard..."):
            time.sleep(1)
            st.switch_page("pages/user_dashboard.py")

# ---------- Sidebar Navigation ----------
st.sidebar.markdown("## 👤 Account Access")
st.sidebar.page_link("pages/login.py", label="🔐 Login")
st.sidebar.page_link("pages/signup.py", label="📝 Register")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/admin_dashboard.py", label="📊 Admin Dashboard")
st.sidebar.page_link("pages/user_dashboard.py", label="📍 User Dashboard")
st.sidebar.markdown("")

# ---------- Footer ----------
st.markdown("---")
st.markdown("Made with ❤️ by **Sahel Innovation & Technologies Ltd.**")
