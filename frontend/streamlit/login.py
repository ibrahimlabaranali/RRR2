import streamlit as st
import sqlite3
import hashlib

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/GitHubProjects/frontend/streamlit/users.db"

# --- Utility Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, nin FROM users WHERE username=? AND password=?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

# --- Streamlit Login UI ---
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Road Freight Risk AI – Login")

st.subheader("👤 User Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not username or not password:
        st.warning("⚠️ Please enter both username and password.")
    else:
        user = authenticate_user(username, password)
        if user:
            user_id, uname, role, nin = user
            st.success(f"✅ Welcome {uname} ({role})")
            st.session_state.authenticated = True
            st.session_state.username = uname
            st.session_state.role = role
            st.session_state.nin = nin  # Track user identity for logs/security

            # Redirect
            if role == "admin":
                st.switch_page("admin_dashboard.py")
            elif role == "user":
                st.switch_page("user_dashboard.py")
            else:
                st.error("❌ Unknown role. Contact admin.")
        else:
            st.error("❌ Invalid username or password.")

st.markdown("---")
st.markdown("📌 Don't have an account? [Register here](signup.py)")
