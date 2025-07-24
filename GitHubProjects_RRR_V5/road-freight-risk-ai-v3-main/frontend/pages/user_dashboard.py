# user_dashboard.py

import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ========== 📌 Setup ==========
st.set_page_config(
    page_title="📍 Road Risk Reporter",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Configuration ==========
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_api_url():
    """Get API URL with fallback"""
    return os.getenv("API_URL", "https://road-freight-risk-ai.onrender.com")

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_user_reports(api_url, username):
    """Fetch user reports with error handling"""
    try:
        response = requests.get(f"{api_url}/reports/user/{username}", timeout=10)
        if response.status_code == 200:
            return response.json(), None
        else:
            return [], f"API Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return [], f"Network Error: {str(e)}"

# ========== Authentication Check ==========
if not st.session_state.get("authenticated"):
    st.error("🔐 Please log in to access the dashboard.")
    st.page_link("pages/login.py", label="🔐 Go to Login")
    st.stop()

# ========== Get User Info ==========
username = st.session_state.get("username", "unknown_user")
user_role = st.session_state.get("role", "user")
API_BASE = get_api_url()

# ========== Sidebar ==========
st.sidebar.title("🚦 Road Risk Reporter")
st.sidebar.write(f"👤 Logged in as: **{username}**")
st.sidebar.write(f"🔑 Role: **{user_role}**")

# Logout button
if st.sidebar.button("🔓 Logout", type="primary"):
    for key in ["authenticated", "username", "role", "user_id"]:
        st.session_state[key] = None if key in ["username", "role", "user_id"] else False
    st.rerun()

# ========== Main Content ==========
st.title("🗺 Your Road Risk Dashboard")

# ========== 📍 Get GPS Location ==========
st.subheader("📍 Current Location")

# Try to get GPS location
try:
    coords = streamlit_js_eval(
        js_expressions="navigator.geolocation.getCurrentPosition", 
        key="get_location"
    )
    
    if coords and coords.get("coords"):
        latitude = coords["coords"]["latitude"]
        longitude = coords["coords"]["longitude"]
        st.success(f"📍 GPS Location: {latitude:.6f}, {longitude:.6f}")
    else:
        st.warning("📍 GPS location not available. Using default coordinates.")
        latitude = 9.0578
        longitude = 7.4951
except Exception as e:
    st.warning("📍 GPS access denied. Please enter coordinates manually.")
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=9.0578, format="%.6f")
    with col2:
        longitude = st.number_input("Longitude", value=7.4951, format="%.6f")

# ========== 📡 Fetch Reports ==========
st.subheader("📋 Your Reports")

with st.spinner("Loading your reports..."):
    reports, error = fetch_user_reports(API_BASE, username)

if error:
    st.error(f"❌ {error}")
    st.info("Please check your connection and try again.")
    df = pd.DataFrame()
else:
    df = pd.DataFrame(reports)
    
    if not df.empty:
        st.success(f"✅ Found {len(df)} reports")
        
        # Convert timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
    else:
        st.info("📭 No reports found. Submit your first report!")
        df = pd.DataFrame()

# ========== 🗺 Map Display ==========
if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
    st.subheader("🧭 Risk Map")
    
    try:
        # Create map with user's location as center
        map_center = [latitude, longitude]
        risk_map = folium.Map(
            location=map_center, 
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add user's current location
        folium.Marker(
            location=map_center,
            popup="📍 Your Current Location",
            tooltip="You are here",
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(risk_map)
        
        # Add risk markers
        for _, row in df.iterrows():
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                # Determine marker color based on risk severity
                risk_type = row.get('risk_type', 'Unknown')
                severity = row.get('severity', 'low')
                
                if severity == 'high':
                    color = 'red'
                elif severity == 'medium':
                    color = 'orange'
                else:
                    color = 'blue'
                
                # Create popup content
                popup_content = f"""
                <b>Risk Type:</b> {risk_type}<br>
                <b>Location:</b> {row.get('location', 'Unknown')}<br>
                <b>Time:</b> {row.get('timestamp', 'Unknown')}<br>
                <b>Severity:</b> {severity}<br>
                <b>Confirmations:</b> {row.get('confirmations', 0)}
                """
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{risk_type} - {row.get('location', 'Unknown')}",
                    icon=folium.Icon(color=color, icon="warning-sign")
                ).add_to(risk_map)
        
        # Display map
        st_folium(risk_map, width=800, height=500)
        
    except Exception as e:
        st.error(f"❌ Error displaying map: {str(e)}")
        st.info("Map display is temporarily unavailable.")

# ========== 📋 Risk Table ==========
if not df.empty:
    st.subheader("📊 Report Summary")
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reports", len(df))
    
    with col2:
        unique_risks = df['risk_type'].nunique() if 'risk_type' in df.columns else 0
        st.metric("Risk Types", unique_risks)
    
    with col3:
        total_confirmations = df['confirmations'].sum() if 'confirmations' in df.columns else 0
        st.metric("Total Confirmations", total_confirmations)
    
    with col4:
        avg_severity = df['severity'].value_counts().index[0] if 'severity' in df.columns and not df.empty else 'N/A'
        st.metric("Most Common Severity", avg_severity)
    
    # Display detailed table
    st.subheader("📋 Detailed Reports")
    
    if 'timestamp' in df.columns and 'risk_type' in df.columns:
        display_columns = ['timestamp', 'risk_type', 'location', 'severity', 'confirmations']
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            st.dataframe(
                df[available_columns].head(10),
                use_container_width=True,
                hide_index=True
            )
            
            # Export option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download All Reports (CSV)",
                data=csv,
                file_name=f"risk_reports_{username}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ========== Quick Actions ==========
st.subheader("🚀 Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚨 Submit New Report", type="primary", use_container_width=True):
        st.switch_page("pages/report_submission.py")

with col2:
    if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
        st.rerun()

# ========== Footer ==========
st.markdown("---")
st.caption("📍 Dashboard | Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
