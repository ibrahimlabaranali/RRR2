import streamlit as st
import requests

# ----------- CONFIG -----------
API_URL = "http://127.0.0.1:8000/auth/login"
st.set_page_config(page_title="Login - Road Freight Risk AI", layout="centered")

# ----------- UI -----------
st.title("🔐 Login to Road Freight Risk AI")
st.markdown("Please enter your credentials to access your dashboard.")

with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    submitted = st.form_submit_button("Login")

if submitted:
    if not username or not password:
        st.warning("⚠️ Please enter both username and password.")
    else:
        try:
            response = requests.post(API_URL, json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()

                # Store credentials in session
                st.session_state["access_token"] = data.get("access_token")
                st.session_state["role"] = data.get("role")
                st.session_state["username"] = username
                st.session_state["nin"] = data.get("nin")

                st.success(f"✅ Logged in as **{username}** ({data['role']})")

                # Redirect based on role
                if data["role"] == "admin":
                    st.switch_page("pages/admin_dashboard.py")
                elif data["role"] == "user":
                    st.switch_page("pages/user_dashboard.py")
                else:
                    st.error("❌ Unknown role. Please contact admin.")
            elif response.status_code == 401:
                st.error("❌ Invalid username or password.")
            else:
                st.error(f"⚠️ Server error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the backend server. Please ensure the API is running.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ----------- Link to Register -----------
st.markdown("---")
st.markdown("🚀 New user? [Register here](signup_ui.py)")
