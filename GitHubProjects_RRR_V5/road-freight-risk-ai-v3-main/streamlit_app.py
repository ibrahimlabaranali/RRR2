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
st.set_page_config(
    page_title="🚛 Road Freight Risk AI",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Custom CSS for better mobile experience
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mobile-optimized {
        max-width: 100%;
        padding: 0.5rem;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 🚛 Main Header
st.markdown('<h1 class="main-header">🚛 Road Freight Risk AI</h1>', unsafe_allow_html=True)

# 🔐 Sidebar Navigation
st.sidebar.markdown("## 📱 Navigation")
st.sidebar.markdown("### 👤 User Access")
st.sidebar.page_link("frontend/pages/user_register.py", label="📝 Register (User)")
st.sidebar.page_link("frontend/pages/user_login.py", label="🔐 Login (User)")
st.sidebar.page_link("frontend/pages/forgot_password.py", label="🔑 Forgot Password")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Admin Access")
admin_access_code = st.sidebar.text_input("🔑 Admin Code", type="password")
if admin_access_code == "sahel-admin-2024":
    st.sidebar.page_link("frontend/pages/admin_register.py", label="🛡 Admin Register")
    st.sidebar.page_link("frontend/pages/admin_login.py", label="🔐 Admin Login")

# 🔑 Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_id = None

# 📍 Location auto-fill function
def get_location():
    st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const coords = `${pos.coords.latitude},${pos.coords.longitude}`;
                    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                    if (input) input.value = coords;
                },
                (err) => console.log("Location error:", err)
            );
        }
        </script>
    """, unsafe_allow_html=True)

# 🔑 Login Form
if not st.session_state.authenticated:
    st.markdown('<div class="mobile-optimized">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            nin = st.text_input("NIN", max_chars=11, placeholder="Enter your NIN")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", type="primary")
            
            if submit_button:
                if not nin or not password:
                    st.error("❌ Please fill in all fields.")
                else:
                    try:
                        with st.spinner("🔐 Logging in..."):
                            res = requests.post(
                                f"{API_URL}/auth/login", 
                                json={"nin": nin, "password": password},
                                timeout=10
                            )
                            
                        if res.status_code == 200:
                            user = res.json()
                            st.session_state.authenticated = True
                            st.session_state.username = user["username"]
                            st.session_state.role = user["role"]
                            st.session_state.user_id = user.get("user_id")
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid NIN or password.")
                    except requests.exceptions.Timeout:
                        st.error("⏰ Login timeout. Please try again.")
                    except requests.exceptions.RequestException:
                        st.error("🌐 Connection error. Please check your internet connection.")
                    except Exception as e:
                        st.error(f"⚠️ Login error: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📝 New User?")
        if st.button("Register Now", type="secondary"):
            st.switch_page("frontend/pages/user_register.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 🔓 Logout
if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_id = None
    st.rerun()

# 🙌 Welcome Message
st.success(f"Welcome, **{st.session_state.username}** ({st.session_state.role})")

# 📍 Submit Road Risk Report
st.markdown('<div class="mobile-optimized">', unsafe_allow_html=True)
st.header("📍 Submit Road Risk Report")

with st.form("risk_report_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        get_location()
        location = st.text_input("Location (GPS auto-fill or manual)", placeholder="Enter location")
        
    with col2:
        risk_type = st.selectbox(
            "Risk Type", 
            ["Select", "Flooding", "Robbery", "Protest", "Road Block", "Kidnap", "Other"], 
            index=0
        )
    
    description = st.text_area("Describe the incident", placeholder="Provide detailed description of the risk...")
    
    if risk_type == "Other":
        risk_type = st.text_input("Enter custom risk type")
    
    # 🎤 Voice Upload
    st.markdown("### 🎤 Voice Report (Optional)")
    audio_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'm4a'], help="Max 5MB")
    
    submitted = st.form_submit_button("Submit Report", type="primary")
    
    if submitted:
        if not location or risk_type == "Select" or not description:
            st.error("❌ Please fill in all required fields.")
        else:
            try:
                with st.spinner("📤 Submitting report..."):
                    report_data = {
                        "username": st.session_state.username,
                        "risk_type": risk_type,
                        "location": location,
                        "description": description,
                        "confirmed": True
                    }
                    
                    res = requests.post(
                        f"{API_URL}/reports/submit",
                        json=report_data,
                        timeout=15
                    )
                
                if res.status_code == 200:
                    result = res.json()
                    st.success("✅ Report submitted successfully!")
                    
                    # Display safety advice
                    if "advice" in result:
                        st.info(f"💡 **Safety Advice**: {result['advice']}")
                    
                    # Display confirmation count
                    if "confirmations" in result:
                        st.info(f"👥 **Community Confirmations**: {result['confirmations']}")
                        
                else:
                    st.error(f"❌ Error submitting report: {res.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Submission timeout. Please try again.")
            except requests.exceptions.RequestException:
                st.error("🌐 Connection error. Please check your internet connection.")
            except Exception as e:
                st.error(f"⚠️ Submission error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# 📊 Recent Reports
st.markdown("---")
st.header("📊 Recent Reports")

try:
    with st.spinner("📊 Loading recent reports..."):
        res = requests.get(f"{API_URL}/reports/all", timeout=10)
    
    if res.status_code == 200:
        reports = res.json()
        if reports:
            df = pd.DataFrame(reports)
            st.dataframe(df[['username', 'risk_type', 'location', 'created_at']], use_container_width=True)
        else:
            st.info("📭 No reports found.")
    else:
        st.warning("⚠️ Could not load recent reports.")
        
except requests.exceptions.Timeout:
    st.warning("⏰ Loading timeout.")
except requests.exceptions.RequestException:
    st.warning("🌐 Connection error.")
except Exception as e:
    st.warning(f"⚠️ Error loading reports: {str(e)}")

# 🗺️ Map View
st.markdown("---")
st.header("🗺️ Risk Map")

try:
    with st.spinner("🗺️ Loading map..."):
        res = requests.get(f"{API_URL}/reports/all", timeout=10)
    
    if res.status_code == 200:
        reports = res.json()
        if reports:
            # Create map centered on Nigeria
            m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
            
            for report in reports:
                try:
                    # Extract coordinates from location (assuming format: "lat,lon")
                    if ',' in str(report.get('location', '')):
                        lat, lon = map(float, str(report['location']).split(',')[:2])
                        
                        # Color based on risk type
                        colors = {
                            'Robbery': 'red',
                            'Kidnap': 'darkred',
                            'Flooding': 'blue',
                            'Protest': 'orange',
                            'Road Block': 'yellow',
                            'Other': 'gray'
                        }
                        color = colors.get(report['risk_type'], 'gray')
                        
                        folium.Marker(
                            [lat, lon],
                            popup=f"""
                            <b>{report['risk_type']}</b><br>
                            Location: {report['location']}<br>
                            Reported by: {report['username']}<br>
                            Time: {report.get('created_at', 'N/A')}
                            """,
                            icon=folium.Icon(color=color, icon='warning')
                        ).add_to(m)
                except:
                    continue
            
            st_folium(m, use_container_width=True)
        else:
            st.info("🗺️ No reports to display on map.")
    else:
        st.warning("⚠️ Could not load map data.")
        
except requests.exceptions.Timeout:
    st.warning("⏰ Map loading timeout.")
except requests.exceptions.RequestException:
    st.warning("🌐 Connection error.")
except Exception as e:
    st.warning(f"⚠️ Error loading map: {str(e)}")

# 📱 Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🚛 Road Freight Risk AI v3.0 | Optimized for Mobile & Cloud Deployment</p>
    <p>Built with ❤️ for safer road transportation</p>
</div>
""", unsafe_allow_html=True) 