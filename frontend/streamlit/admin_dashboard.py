import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import streamlit_js_eval
import plotly.express as px

API_URL = "https://road-freight-risk-ai.onrender.com"

# ---------- Page Config ----------
st.set_page_config(page_title="Admin Dashboard - Road Freight Risk AI", layout="wide")
st.title("🛡️ Road Freight Risk AI – Admin Dashboard")

# ---------- Session Check ----------
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("⛔ Access Denied. Please log in via the login page.")
    st.stop()

if st.session_state.role != "admin":
    st.error("⛔ This page is restricted to Admin users.")
    st.stop()

username = st.session_state.username
st.markdown(f"👋 Welcome, **Admin {username}**")

# ---------- GPS Initialization ----------
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""

if st.button("🔄 Refresh Admin GPS Location"):
    result = streamlit_js_eval.get_geolocation()
    if result and "latitude" in result and "longitude" in result:
        st.session_state.gps_lat = result["latitude"]
        st.session_state.gps_lon = result["longitude"]
        st.success(f"📍 Admin GPS: ({result['latitude']}, {result['longitude']})")
    else:
        st.warning("⚠️ Could not get location.")

# ---------- Fetch All Reports ----------
st.markdown("### 📍 All Submitted Risk Reports")
try:
    res = requests.get(f"{API_URL}/reports/")
    if res.status_code == 200:
        data = res.json()
        if data:
            df = pd.DataFrame(data)

            # Show map
            m = folium.Map(location=[10.5, 7.4], zoom_start=6)
            for report in data:
                try:
                    folium.Marker(
                        location=[report["lat"], report["lon"]],
                        popup=f"{report['risk_type']} - {report['location']}",
                        icon=folium.Icon(color="red" if "armed" in report["risk_type"].lower() else "blue")
                    ).add_to(m)
                except:
                    continue
            st_folium(m, width=900)

            # Show table
            st.markdown("### 🧾 Risk Report Table")
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download All Reports", csv, "all_risk_reports.csv", "text/csv")

            # ---------- Analytics ----------
            st.markdown("### 📈 Risk Category Distribution")
            fig = px.histogram(df, x="risk_type", color="risk_type", title="Reported Risks by Type")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📍 State-wise Report Count")
            fig2 = px.histogram(df, x="state", color="state", title="Risk Reports by State")
            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("📭 No reports submitted yet.")
    else:
        st.error(f"❌ Failed to fetch reports: {res.status_code}")
except Exception as e:
    st.error(f"❌ Exception: {e}")

# ---------- Admin Logout ----------
if st.button("🚪 Logout Admin"):
    st.session_state.clear()
    st.success("✅ Admin logged out. Refresh or go to the login page.")
