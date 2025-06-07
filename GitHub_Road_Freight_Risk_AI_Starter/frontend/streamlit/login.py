import streamlit as st
import sqlite3
import hashlib

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/GitHubProjects/frontend/streamlit/users.db"

# --- Hashing utility ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Authenticate user ---
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# --- Streamlit Page ---
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Road Freight Risk AI - Login")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.form_submit_button("Login")

if login_btn:
    if not username or not password:
        st.warning("⚠️ Please enter both username and password.")
    else:
        user = authenticate_user(username, password)
        if user:
            user_id, username, _, role = user
            st.success(f"✅ Welcome {username} ({role})!")

            if role == "admin":
                st.switch_page("pages/admin_dashboard.py")
            elif role == "user":
                st.switch_page("pages/user_dashboard.py")
            else:
                st.error("❌ Unknown role. Contact system admin.")
        else:
            st.error("❌ Invalid username or password.")

# --- Link to Signup Page ---
st.page_link("pages/signup.py", label="👉 Don't have an account? Sign up here", icon="📝")
