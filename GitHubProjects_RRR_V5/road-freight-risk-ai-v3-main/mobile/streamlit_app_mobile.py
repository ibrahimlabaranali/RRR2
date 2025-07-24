import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

# 🌍 Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# 🔐 Page config
st.set_page_config(page_title="📱 Road Risk AI", layout="centered")
st.title("📱 Road Freight Risk Reporter (Mobile)")

# 🔐 Sidebar Navigation
st.sidebar.markdown("## 📱 Navigation")
st.sidebar.page_link("pages/user_register.py", label="📝 Register (User)")
st.sidebar.page_link("pages/user_login.py", label="🔐 Login (User)")
st.sidebar.markdown("---")
admin_access_code = st.sidebar.text_input("🔑 Admin Code", type="password")
if admin_access_code == "sahel-admin-2024":
    st.sidebar.page_link("pages/admin_register.py", label="🛡 Admin Register")
    st.sidebar.page_link("pages/admin_login.py", label="🔐 Admin Login")

# 🔑 Session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

# 📍 Location auto-fill
def get_location():
    st.markdown("""
        <script>
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = `${pos.coords.latitude},${pos.coords.longitude}`;
                const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                if (input) input.value = coords;
            },
            (err) => console.log("Location error:", err)
        );
        </script>
    """, unsafe_allow_html=True)

# 🔑 Login
if not st.session_state.authenticated:
    st.subheader("🔐 Login")
    nin = st.text_input("NIN", max_chars=11)
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            res = requests.post(f"{API_URL}/auth/login", json={"nin": nin, "password": password})
            if res.status_code == 200:
                user = res.json()
                st.session_state.authenticated = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid NIN or password.")
        except Exception as e:
            st.error(f"⚠ Login error: {e}")
    st.stop()

# 🔓 Logout
if st.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# 🙌 Welcome
st.success(f"Welcome, {st.session_state.username} ({st.session_state.role})")

# 📍 Submit Road Risk
st.header("📍 Submit Road Risk Report")
get_location()
location = st.text_input("Location (auto or manual)")
description = st.text_area("Describe the incident")

# 🧠 Risk Type Classification
suggest_type = ""
if description:
    try:
        res = requests.post(f"{API_URL}/classify/text", json={"text": description})
        if res.status_code == 200:
            suggest_type = res.json()["risk_type"]
            st.info(f"🧠 Suggested Risk Type: **{suggest_type}**")
    except:
        st.warning("🤖 Could not classify risk type.")

risk_type = st.selectbox("Risk Type", ["Select", "Flooding", "Robbery", "Protest", "Road Block", "Kidnap", "Other"], index=0)
if risk_type == "Other":
    risk_type = st.text_input("Enter custom risk type")

# 🎤 Voice Upload
st.subheader("🎙️ Report via Voice (Optional)")
voice_file = st.file_uploader("Upload voice (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
if voice_file and st.button("🎧 Transcribe"):
    with st.spinner("Transcribing..."):
        try:
            res = requests.post(
                f"{API_URL}/voice/upload",
                files={"file": (voice_file.name, voice_file, voice_file.type)}
            )
            if res.status_code == 200:
                result = res.json()
                st.success("✅ Transcription Complete")
                st.text_area("📝 Transcription", result["transcription"], height=100)
                st.caption(f"🌐 Language: {result['language']}")
            else:
                st.error(f"❌ {res.json().get('detail', 'Voice transcription failed')}")
        except Exception as e:
            st.error(f"⚠ Upload error: {e}")

# 📨 Submit Form
if st.button("📨 Submit Report"):
    if location and risk_type != "Select":
        data = {
            "username": st.session_state.username,
            "location": location,
            "description": description,
            "risk_type": risk_type
        }
        try:
            res = requests.post(f"{API_URL}/reports/submit", json=data)
            if res.status_code == 200:
                st.success("✅ Report submitted successfully.")
            else:
                st.error("❌ Failed to submit report.")
        except Exception as e:
            st.error(f"🚫 Submit error: {e}")
    else:
        st.warning("⚠ Fill in all required fields.")

# 🗺️ Admin Dashboard
if st.session_state.role == "admin":
    st.subheader("🗺️ Admin Risk Dashboard")
    try:
        res = requests.get(f"{API_URL}/reports/all")
        if res.status_code == 200:
            reports = res.json()
            df = pd.DataFrame(reports)
            if not df.empty:
                m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
                for _, row in df.iterrows():
                    loc_parts = row["location"].split(",")
                    if len(loc_parts) == 2:
                        lat, lon = map(float, loc_parts)
                        icon = "⚠️" if row['risk_type'] in ["Robbery", "Kidnap"] else "💧" if row['risk_type'] == "Flooding" else "📢"
                        folium.Marker(
                            location=[lat, lon],
                            tooltip=f"{icon} {row['risk_type']}",
                            popup=row["description"]
                        ).add_to(m)
                st_folium(m, width=700)
                st.download_button("⬇ Download CSV", df.to_csv(index=False), "risk_reports.csv", "text/csv")
            else:
                st.info("📭 No reports available.")
        else:
            st.error("❌ Failed to load reports.")
    except Exception as e:
        st.error(f"💥 Map error: {e}")

st.markdown(
    """
    <link rel="manifest" href="/static/manifest.json" />
    <script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js');
    }

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        // Optionally show custom install button here
    });
    </script>
    """,
    unsafe_allow_html=True
)