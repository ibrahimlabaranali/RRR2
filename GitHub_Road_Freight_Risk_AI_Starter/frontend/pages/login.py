import streamlit as st
import sqlite3
import hashlib

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/Road Freight Risk AI/GitHub_Road_Freight_Risk_AI_Starter/frontend/streamlit/users.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, nin, twofa_secret FROM users WHERE username=? AND password=?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login – 2-Step Verification")

# Step 1: Username and Password
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if "step" not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1 and st.button("Next"):
    user = get_user(username, password)
    if user:
        user_id, uname, role, nin, twofa = user
        # Store basic info temporarily
        st.session_state.temp_user = {
            "id": user_id,
            "username": uname,
            "role": role,
            "nin": nin,
            "twofa": twofa
        }
        st.session_state.step = 2
    else:
        st.error("❌ Invalid username or password.")

# Step 2: 2FA Prompt
if st.session_state.step == 2:
    st.info("📱 A 2FA code is required to complete login.")
    code = st.text_input("Enter 2FA Code")
    
    if st.button("Verify"):
        expected_code = st.session_state.temp_user["twofa"]
        if code == expected_code:
            st.success(f"✅ Welcome {st.session_state.temp_user['username']} ({st.session_state.temp_user['role']})")
            st.session_state.username = st.session_state.temp_user["username"]
            st.session_state.role = st.session_state.temp_user["role"]
            st.session_state.nin = st.session_state.temp_user["nin"]
            st.session_state.step = 1  # reset

            # Navigate to dashboard
            st.switch_page("admin_dashboard.py" if st.session_state.role == "admin" else "user_dashboard.py")
        else:
            st.error("❌ Incorrect 2FA code. Try again.")
