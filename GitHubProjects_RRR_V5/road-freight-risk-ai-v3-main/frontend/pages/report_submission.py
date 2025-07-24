# pages/report_submission.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

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

# Page configuration
st.set_page_config(
    page_title="Submit Risk Report",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Authentication Check ==========
if not st.session_state.get("authenticated"):
    st.error("🔐 Please log in to submit reports.")
    st.page_link("pages/login.py", label="🔐 Go to Login")
    st.stop()

# ========== Initialize Session State ==========
if "report_data" not in st.session_state:
    st.session_state.report_data = {}
if "show_confirmation" not in st.session_state:
    st.session_state.show_confirmation = False

# ========== Get Configuration ==========
API_URL = get_api_url()
username = st.session_state.get("username", "unknown_user")

# ========== Sidebar ==========
st.sidebar.title("🚨 Submit Risk Report")
st.sidebar.write(f"👤 Logged in as: **{username}**")

# Logout button
if st.sidebar.button("🔓 Logout", type="primary"):
    for key in ["authenticated", "username", "role", "user_id"]:
        st.session_state[key] = None if key in ["username", "role", "user_id"] else False
    st.rerun()

# ========== Main Content ==========
st.title("🚨 Submit Road Risk Report")
st.markdown("Report road hazards, security incidents, or other risks to help keep our community safe.")

# ========== GPS Location Function ==========
def get_location():
    """Get current GPS location using JavaScript"""
    st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    window.parent.postMessage({
                        type: 'location',
                        latitude: lat,
                        longitude: lng
                    }, '*');
                },
                function(error) {
                    console.error("Location error:", error);
                }
            );
        }
        </script>
    """, unsafe_allow_html=True)

# ========== Form Validation ==========
def validate_form(risk_type, location, description):
    """Validate form inputs"""
    errors = []
    
    if not risk_type or risk_type == "Select":
        errors.append("Risk type is required")
    
    if not location:
        errors.append("Location is required")
    
    if risk_type == "Other" and not description:
        errors.append("Description is required when risk type is 'Other'")
    
    return errors

# ========== Report Submission ==========
def submit_report_with_confirmation():
    """Submit report with confirmation prompt"""
    st.session_state.show_confirmation = True

def confirm_and_submit():
    """Final submission after confirmation"""
    try:
        # Prepare report data
        report_data = {
            "username": st.session_state.get("username"),
            "risk_type": st.session_state.report_data["risk_type"],
            "latitude": st.session_state.report_data["latitude"],
            "longitude": st.session_state.report_data["longitude"],
            "location": st.session_state.report_data["location"],
            "description": st.session_state.report_data.get("description"),
            "confirmed": True
        }
        
        # Submit report with timeout
        with st.spinner("Submitting report..."):
            response = requests.post(f"{API_URL}/reports/submit", json=report_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            st.success("✅ Report submitted successfully!")
            
            # Display safety advice
            if result.get("advice"):
                st.info("🛡️ **Safety Advice:**")
                st.write(result["advice"])
            
            # Show confirmation count
            if result.get("confirmations", 0) > 0:
                st.info(f"✅ Confirmed by {result['confirmations']} other drivers")
            
            # Reset form
            st.session_state.report_data = {}
            st.session_state.show_confirmation = False
            st.rerun()
            
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"❌ Error: {error_detail}")
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        st.error(f"🚫 Network error: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

# ========== Main Form ==========
with st.form("risk_report_form", clear_on_submit=False):
    st.subheader("📍 Location Information")
    
    # GPS coordinates
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input(
            "Latitude",
            value=9.0578,
            format="%.6f",
            help="Your current GPS latitude"
        )
    with col2:
        longitude = st.number_input(
            "Longitude", 
            value=7.4951,
            format="%.6f",
            help="Your current GPS longitude"
        )
    
    # Manual location input
    location = st.text_input(
        "Location Description",
        placeholder="e.g., Lagos-Ibadan Expressway, Km 45",
        help="Describe the specific location of the risk"
    )
    
    st.subheader("⚠️ Risk Details")
    
    # Risk type selection
    risk_type = st.selectbox(
        "Risk Type",
        ["Select", "Flooding", "Armed Robbery", "Banditry", "Protest", 
         "Road Closure", "Accident", "Kidnap", "Other"],
        help="Select the type of risk you're reporting"
    )
    
    # Custom description for "Other" or additional details
    description = st.text_area(
        "Description (Required for 'Other' risk type)",
        placeholder="Provide additional details about the risk...",
        height=100,
        help="Describe the incident in detail"
    )
    
    # File upload
    st.subheader("📎 Attachments (Optional)")
    uploaded_file = st.file_uploader(
        "Upload Image or Audio",
        type=["jpg", "jpeg", "png", "gif", "mp3", "wav", "m4a"],
        help="Upload photos or voice recordings (max 5MB)"
    )
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        if file_size > 5:
            st.error("❌ File size exceeds 5MB limit")
        else:
            st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size:.1f}MB)")
    
    # Submit button
    submitted = st.form_submit_button("📤 Submit Report", type="primary")
    
    if submitted:
        # Validate form
        errors = validate_form(risk_type, location, description)
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Store form data for confirmation
            st.session_state.report_data = {
                "risk_type": risk_type,
                "latitude": latitude,
                "longitude": longitude,
                "location": location,
                "description": description if description else None,
                "file": uploaded_file
            }
            
            # Show confirmation dialog
            submit_report_with_confirmation()

# ========== Confirmation Dialog ==========
if st.session_state.show_confirmation:
    st.markdown("---")
    st.subheader("🔍 Confirm Report Details")
    
    data = st.session_state.report_data
    
    # Display report summary
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Risk Type:**", data["risk_type"])
        st.write("**Location:**", data["location"])
        st.write("**Coordinates:**", f"{data['latitude']:.6f}, {data['longitude']:.6f}")
    
    with col2:
        if data.get("description"):
            st.write("**Description:**", data["description"])
        if data.get("file"):
            st.write("**Attachment:**", data["file"].name)
    
    # Confirmation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Confirm & Submit", type="primary"):
            confirm_and_submit()
    
    with col2:
        if st.button("✏️ Edit Report", type="secondary"):
            st.session_state.show_confirmation = False
            st.rerun()
    
    with col3:
        if st.button("❌ Cancel"):
            st.session_state.report_data = {}
            st.session_state.show_confirmation = False
            st.rerun()

# ========== Recent Reports Section ==========
st.markdown("---")
st.subheader("📋 Your Recent Reports")

try:
    reports, error = fetch_user_reports(API_URL, username)
    
    if error:
        st.warning(f"⚠️ Could not load recent reports: {error}")
    elif reports:
        df = pd.DataFrame(reports)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False).head(5)
        
        for _, report in df.iterrows():
            with st.expander(f"{report['risk_type']} - {report['location']} ({report['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Risk Type:** {report['risk_type']}")
                    st.write(f"**Location:** {report['location']}")
                    if report.get('description'):
                        st.write(f"**Description:** {report['description']}")
                with col2:
                    st.write(f"**Severity:** {report.get('severity', 'Unknown')}")
                    st.write(f"**Confirmations:** {report.get('confirmations', 0)}")
                    if report.get('advice'):
                        st.info(f"**Advice:** {report['advice']}")
    else:
        st.info("📭 No reports found. Submit your first report above!")
        
except Exception as e:
    st.error(f"❌ Error loading reports: {e}")

# ========== Safety Tips ==========
st.markdown("---")
st.subheader("💡 Safety Tips")
st.markdown("""
- **Always verify your location** before submitting a report
- **Provide clear descriptions** to help other drivers
- **Upload photos** when safe to do so
- **Confirm reports** from other drivers to improve accuracy
- **Follow safety advice** provided by the system
""")

# ========== Quick Actions ==========
st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh", type="secondary", use_container_width=True):
        st.rerun()

with col2:
    if st.button("📍 View Dashboard", type="secondary", use_container_width=True):
        st.switch_page("pages/user_dashboard.py")

with col3:
    if st.button("🏠 Go Home", type="secondary", use_container_width=True):
        st.switch_page("streamlit_app.py")

# ========== Footer ==========
st.markdown("---")
st.caption("🚨 In case of emergency, contact local authorities immediately.")
st.caption("📱 Report Submission | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 