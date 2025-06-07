import streamlit as st
from login import login_user

# Page config
st.set_page_config(page_title="Login | Road Freight Risk AI", layout="centered")

st.title("🔐 Road Freight Risk AI Login")

# Input fields
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = login_user(username, password)
    if user:
        st.success(f"✅ Welcome, {username}! Redirecting...")
        # Save session
        st.session_state.username = username
        st.session_state.role = user[3]  # Role from DB
        st.session_state.logged_in = True

        # Redirect
        if st.session_state.role == "admin":
            st.switch_page("admin_dashboard.py")
        else:
            st.switch_page("user_dashboard.py")
    else:
        st.error("❌ Invalid username or password")
