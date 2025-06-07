import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit_js_eval

API_URL = "https://road-freight-risk-ai.onrender.com"

# ---------- Page Config ----------
st.set_page_config(page_title="User Dashboard - Road Freight Risk AI", layout="wide")
st.title("👤 Road Freight Risk AI – User Dashboard")

# ---------- Session Check ----------
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("⛔ Access Denied. Please log in via the login page.")
    st.stop()

username = st.session_state.username
role = st.session_state.role

st.markdown(f"👋 Welcome, **{username}** | Role: `{role.title()}`")

# ---------- GPS Handler ----------
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""

st.markdown("### 📍 GPS Location")
if st.button("🔄 Refresh GPS Location"):
    result = streamlit_js_eval.get_geolocation()
    if result and "latitude" in result and "longitude" in result:
        st.session_state.gps_lat = result["latitude"]
        st.session_state.gps_lon = result["longitude"]
        st.success(f"📍 Updated GPS: ({result['latitude']}, {result['longitude']})")
    else:
        st.warning("⚠️ Failed to get location. Allow browser GPS access.")

# ---------- Fetch User Reports ----------
def fetch_user_reports(username):
    try:
        res = requests.get(f"{API_URL}/reports/")
        if res.status_code == 200:
            all_data = res.json()
            return [r for r in all_data if r.get("user_id") == username]
        else:
            st.error(f"❌ API Error: {res.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Exception: {e}")
        return []

# ---------- View Reports ----------
st.markdown("### 🗺 Your Submitted Reports")
user_reports = fetch_user_reports(username)

if user_reports:
    m = folium.Map(location=[10.5, 7.4], zoom_start=6)
    for report in user_reports:
        try:
            folium.Marker(
                location=[report["lat"], report["lon"]],
                popup=f"{report['risk_type']} - {report['location']}",
                icon=folium.Icon(color="blue")
            ).add_to(m)
        except:
            continue
    st_folium(m, width=900)

    df = pd.DataFrame(user_reports)
    st.markdown("### 📊 Data Table of Your Reports")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Your Reports", csv, "user_reports.csv", "text/csv")
else:
    st.info("📭 No reports found.")

# ---------- Logout ----------
if st.button("🚪 Logout"):
    st.session_state.clear()
    st.success("✅ Logged out successfully. Please refresh or return to the login page.")
