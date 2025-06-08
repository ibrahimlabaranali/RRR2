import streamlit as st
import sqlite3
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# ---------- CONFIG ----------
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🛡️ Road Freight Risk AI – Admin Dashboard")

API_URL = "https://road-freight-risk-ai.onrender.com/reports/"
DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/Road Freight Risk AI/GitHub_Road_Freight_Risk_AI_Starter/frontend/streamlit/users.db"

# ---------- SESSION VALIDATION ----------
if "role" not in st.session_state or st.session_state.role != "admin":
    st.error("❌ Access denied. Admins only.")
    st.stop()

st.success(f"✅ Welcome, Admin {st.session_state.username} (NIN: {st.session_state.nin})")

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📍 View Freight Risk Reports", "🧑‍💻 Manage Users", "📊 Export Data"])

# ---------- TAB 1: MAP VIEW ----------
with tab1:
    st.subheader("📍 Visual Map of Reported Risks")

    try:
        res = requests.get(API_URL)
        data = res.json() if res.status_code == 200 else []
        df = pd.DataFrame(data)

        m = folium.Map(location=[10.5, 7.4], zoom_start=6)

        for r in data:
            folium.Marker(
                location=[r["lat"], r["lon"]],
                popup=f"{r['risk_type']} - {r['location']} ({r['state']}, {r['lga']})",
                icon=folium.Icon(color="red" if r["risk_type"] == "Armed Robbery" else "blue")
            ).add_to(m)

        st_folium(m, width=900, height=450)
        st.markdown("📍 Use the map above to monitor high-risk freight corridors.")

    except Exception as e:
        st.error(f"⚠️ Could not load map: {e}")
        df = pd.DataFrame()  # fallback to avoid crash in export tab

# ---------- TAB 2: USER MANAGEMENT ----------
with tab2:
    st.subheader("🧑‍💻 Registered Users")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, role, nin FROM users")
        users = c.fetchall()
        conn.close()

        user_df = pd.DataFrame(users, columns=["ID", "Username", "Role", "NIN"])
        st.dataframe(user_df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Failed to load users: {e}")
        user_df = pd.DataFrame()

# ---------- TAB 3: EXPORT ----------
with tab3:
    st.subheader("📊 Download Risk and User Data")

    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Risk Reports (CSV)", csv, "freight_risk_reports.csv", "text/csv")

    if 'user_df' in locals() and not user_df.empty:
        user_csv = user_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download User Data (CSV)", user_csv, "registered_users.csv", "text/csv")

    if df.empty and user_df.empty:
        st.warning("⚠️ No data available for export.")
