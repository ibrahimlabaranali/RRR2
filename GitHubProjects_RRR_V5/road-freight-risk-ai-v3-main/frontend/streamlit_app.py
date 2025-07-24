import streamlit as st
import time
import requests
import os
from dotenv import load_dotenv

# ---------- Load .env ----------
load_dotenv()

# ---------- Configuration ----------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_api_url():
    """Get API URL with fallback"""
    return os.getenv("API_URL", "https://road-freight-risk-ai.onrender.com")

@st.cache_data(ttl=60)  # Cache for 1 minute
def check_backend_health(api_url):
    """Check backend health with timeout"""
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        return response.status_code == 200, response.status_code
    except requests.exceptions.RequestException:
        return False, None

# ---------- Page Setup ----------
st.set_page_config(
    page_title="Road Freight Risk AI",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- Initialize Session State ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- Get API URL ----------
API_URL = get_api_url()

# ---------- Backend Health Check ----------
with st.spinner("Checking backend connection..."):
    backend_healthy, status_code = check_backend_health(API_URL)

if backend_healthy:
    st.success("✅ Backend Connected")
else:
    st.error(f"🚫 Backend Connection Failed (Status: {status_code})")
    st.warning("Some features may be unavailable. Please try again later.")

# ---------- Title ----------
st.title("🚚 Road Freight Risk AI – Home")

st.markdown("""
Welcome to the **Road Freight Risk AI System**.

### 🔑 Key Features
- 🛰 Smart GPS or manual fallback
- 📍 Select risk type (flooding, protest, robbery, etc.)
- 📲 Mobile-friendly PWA with offline caching
- 📊 Admin heatmap and CSV download
- 🛡️ Real-time safety advice
- ✅ Community confirmations
""")

# ---------- Authentication Status ----------
if st.session_state.authenticated:
    st.success(f"Welcome, {st.session_state.username} ({st.session_state.role})")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔓 Logout", type="primary"):
            # Clear session state
            for key in ["authenticated", "username", "role", "user_id"]:
                st.session_state[key] = None if key in ["username", "role", "user_id"] else False
            st.rerun()

    # Role-based navigation
    if st.session_state.role == "admin":
        st.info("👨‍💼 Admin Dashboard Available")
        if st.button("📊 Go to Admin Dashboard", type="secondary"):
            st.switch_page("pages/admin_dashboard.py")
    elif st.session_state.role == "user":
        st.info("👤 User Dashboard Available")
        if st.button("📍 Go to User Dashboard", type="secondary"):
            st.switch_page("pages/user_dashboard.py")

else:
    st.info("🔐 Please log in to access the dashboard")

# ---------- Sidebar Navigation ----------
st.sidebar.markdown("## 🚀 Quick Actions")

if not st.session_state.authenticated:
    st.sidebar.page_link("pages/login.py", label="🔐 Login", icon="🔐")
    st.sidebar.page_link("pages/signup.py", label="📝 Register", icon="📝")
    st.sidebar.page_link("pages/forgot_password.py", label="🔑 Forgot Password", icon="🔑")
else:
    st.sidebar.page_link("pages/report_submission.py", label="🚨 Submit Report", icon="🚨")
    if st.session_state.role == "admin":
        st.sidebar.page_link("pages/admin_dashboard.py", label="📊 Admin Dashboard", icon="📊")
    else:
        st.sidebar.page_link("pages/user_dashboard.py", label="📍 User Dashboard", icon="📍")

st.sidebar.markdown("---")
st.sidebar.markdown("## 📚 Help & Support")
st.sidebar.markdown("📖 [Documentation](https://github.com/your-repo/docs)")
st.sidebar.markdown("🐛 [Report Issues](https://github.com/your-repo/issues)")

# ---------- System Status ----------
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔧 System Status")

# Backend status indicator
if backend_healthy:
    st.sidebar.success("🟢 Backend Online")
else:
    st.sidebar.error("🔴 Backend Offline")

# User status
if st.session_state.authenticated:
    st.sidebar.success(f"🟢 Logged in as {st.session_state.username}")
else:
    st.sidebar.info("🟡 Not logged in")

# ---------- Footer ----------
st.markdown("---")
st.caption("Developed by Sahel Innovation & Technologies Ltd. | Version 3.0.0")
