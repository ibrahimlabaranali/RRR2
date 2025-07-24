import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os
from dotenv import load_dotenv
from folium.plugins import HeatMap

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "https://road-freight-risk-ai.onrender.com")

# Set Streamlit page config
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Check admin authentication
if not st.session_state.get("authenticated") or st.session_state.get("role") != "admin":
    st.error("⛔ Unauthorized access. Admins only.")
    st.stop()

st.title("📊 Admin Dashboard – Road Risk Reports")
st.markdown("Monitor, visualize, and manage all reported freight transport risks across Nigeria.")

# Date filter in sidebar
selected_date = st.sidebar.date_input("📅 Filter by Date")

# Toggle controls
use_heatmap = st.sidebar.checkbox("🌡 Show Heatmap", value=False)
filter_sms = st.sidebar.checkbox("📱 SMS-only Reports", value=False)
show_markers = st.sidebar.checkbox("📍 Show Risk Markers", value=True)

# Fetch report data
try:
    response = requests.get(f"{API_URL}/reports")
    if response.status_code == 200:
        reports = response.json()
        df = pd.DataFrame(reports)

        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Filter by date
        if selected_date:
            df = df[df['timestamp'].dt.date == selected_date]

        # Filter SMS
        if filter_sms:
            df = df[df['source'] == 'sms']

        st.subheader("🗺 Map of Reported Risks")

        # Create map
        base_map = folium.Map(location=[9.0820, 8.6753], zoom_start=6)

        # Marker colors
        color_map = {
            "Flooding": "blue",
            "Robbery": "red",
            "Protest": "orange",
            "Banditry": "darkred",
            "Accident": "green",
            "Blocked Road": "purple",
            "Other": "gray"
        }

        # Heatmap layer
        if use_heatmap and not df.empty:
            heat_data = [[row['latitude'], row['longitude']] for _, row in df.iterrows() if row['latitude'] and row['longitude']]
            HeatMap(heat_data).add_to(base_map)

        # Risk markers
        if show_markers and not df.empty:
            for _, row in df.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=6,
                    color=color_map.get(row['risk_type'], "gray"),
                    fill=True,
                    fill_opacity=0.8,
                    popup=folium.Popup(f"""
                        <strong>Risk:</strong> {row['risk_type']}<br>
                        <strong>User:</strong> {row['username']}<br>
                        <strong>Time:</strong> {row['timestamp']}<br>
                        <strong>Location:</strong> {row['location']}<br>
                        <strong>Source:</strong> {row['source']}
                    """, max_width=250)
                ).add_to(base_map)

        # Render folium map
        st_data = st_folium(base_map, width=1200, height=600)

        # Show raw data table
        st.markdown("---")
        st.subheader("📋 Risk Report Table")
        st.dataframe(df[['username', 'risk_type', 'location', 'timestamp', 'source']].sort_values(by='timestamp', ascending=False), use_container_width=True)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Reports as CSV", data=csv, file_name="road_risk_reports.csv", mime='text/csv')

        # Risk type summary
        st.markdown("---")
        st.subheader("📊 Risk Type Summary")
        summary = df['risk_type'].value_counts().reset_index()
        summary.columns = ["Risk Type", "Count"]
        st.bar_chart(summary.set_index("Risk Type"))

    else:
        st.error(f"❌ Error: API returned {response.status_code}")
except Exception as e:
    st.error(f"🚫 Connection error: {e}")

# Logout option
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout"):
    for key in ["authenticated", "username", "role"]:
        st.session_state[key] = False if key == "authenticated" else None
    st.experimental_rerun()
