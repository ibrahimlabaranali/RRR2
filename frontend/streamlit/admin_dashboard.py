import streamlit as st
import requests

st.title("👤 Admin User Management")

token = st.session_state.get("access_token", None)

if not token or st.session_state.get("role") != "admin":
    st.warning("Admin login required.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://127.0.0.1:8000/users", headers=headers)

if response.status_code == 200:
    users = response.json()
    st.subheader("Registered Users")
    st.table(users)
else:
    st.error("Failed to load user data")
