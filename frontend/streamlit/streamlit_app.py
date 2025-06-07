import streamlit as st

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ You must log in first.")
    st.stop()

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import streamlit_js_eval
import pandas as pd

API_URL = "https://road-freight-risk-ai.onrender.com"

st.set_page_config(layout="wide")
st.title("🚚 Road Freight Risk AI Dashboard")

st.markdown("✅ **GPS location detection is enabled** (grant browser access if prompted).")

# --------- JavaScript GPS Injection ---------
components.html("""
<script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const coords = position.coords;
            window.parent.postMessage(
                JSON.stringify({ latitude: coords.latitude, longitude: coords.longitude }), "*"
            );
        },
        (err) => {
            window.parent.postMessage(JSON.stringify({error: err.message}), "*");
        }
    );
</script>
""", height=0)

# --------- Session State Defaults ---------
if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""
if "gps_error" not in st.session_state:
    st.session_state.gps_error = None

# --------- GPS Response Handler ---------
def handle_js_response():
    result = streamlit_js_eval.get_geolocation()
    if result and "latitude" in result and "longitude" in result:
        st.session_state.gps_lat = result["latitude"]
        st.session_state.gps_lon = result["longitude"]
        st.session_state.gps_error = None
    elif result and "error" in result:
        st.session_state.gps_error = result["error"]
    else:
        st.session_state.gps_error = "No location info received."

# --------- Manual Refresh Button ---------
if st.button("🔄 Refresh GPS Coordinates"):
    handle_js_response()
    if st.session_state.gps_error:
        st.warning(f"⚠️ GPS Error: {st.session_state.gps_error}")
    else:
        st.success(f"📍 Location refreshed: ({st.session_state.gps_lat}, {st.session_state.gps_lon})")
        st.markdown(f"📌 **Current GPS Location:** `{st.session_state.gps_lat}, {st.session_state.gps_lon}`")

# --------- Smart Advice Generator ---------
def generate_safety_advice(risk_category, state, lga):
    risk = risk_category.lower()
    location = f"{lga}, {state}".title()
    if "armed robbery" in risk:
        return f"⚠️ Avoid travel at night in {location}. Consider convoy escort and notify authorities."
    elif "banditry" in risk:
        return f"🚨 {location} is prone to attacks. Postpone non-essential trips. Use only secured, approved routes."
    elif "flood" in risk:
        return f"🌊 Check weather before traveling through {location}. Avoid flooded roads."
    elif "protest" in risk:
        return f"🛑 Avoid protest zones in {location}. Take alternative routes and monitor security updates."
    elif "accident" in risk:
        return f"🚧 Expect delays around {location}. Follow signs and proceed cautiously."
    elif "checkpoint" in risk:
        return f"🕒 Prepare for delays in {location}. Carry ID and cooperate with officials."
    else:
        return f"ℹ️ Travel cautiously through {location}. Check updates before departure."

# --------- Smart Form ---------
st.markdown("### 📨 Submit New Report")
with st.form("risk_form"):
    user_id = st.text_input("User ID", value="1", help="Enter your assigned user number.")
    category = st.selectbox("Risk Category", ["Armed Robbery", "Flooding", "Accident", "Protest", "Banditry", "Checkpoint Delay", "Other"], help="Choose the main type of road freight risk.")
    location = st.text_input("Specific Location (e.g., Kaduna - Abuja Highway)", help="Be descriptive, e.g., 'Zaria Bypass'.")
    state = st.text_input("State", help="Capitalise the name of the Nigerian state.").title()
    lga = st.text_input("Local Government Area (LGA)", help="Capitalise and ensure accuracy.").title()

    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("Latitude", value=str(st.session_state.gps_lat))
    with col2:
        lon = st.text_input("Longitude", value=str(st.session_state.gps_lon))

    notes = st.text_area("Additional Notes (Optional)")

    if category and state and lga:
        st.info("🧠 Smart Safety Advice: " + generate_safety_advice(category, state, lga))

    submitted = st.form_submit_button("Submit Report")
    if submitted:
        try:
            if not lat.strip() or not lon.strip():
                raise ValueError("Latitude and Longitude cannot be empty.")
            payload = {
                "user_id": int(user_id.strip()) if user_id.strip().isdigit() else 1,
                "risk_type": category,
                "description": notes,
                "location": location,
                "state": state,
                "lga": lga,
                "lat": float(lat.strip()),
                "lon": float(lon.strip())
            }
            response = requests.post(f"{API_URL}/reports/", json=payload)
            if response.status_code == 200:
                st.success("✅ Report submitted successfully.")
            else:
                st.error(f"❌ Failed to submit report: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")

# --------- Display Existing Reports on Map ---------
st.markdown("### 🗺 View Reported Risks")
try:
    map = folium.Map(location=[10.5, 7.4], zoom_start=6)
    res = requests.get(f"{API_URL}/reports/")
    if res.status_code == 200:
        risk_data = res.json()
        for report in risk_data:
            try:
                icon_color = {
                    "Armed Robbery": "red",
                    "Banditry": "darkred",
                    "Flooding": "blue",
                    "Accident": "orange",
                    "Protest": "green",
                    "Checkpoint Delay": "purple",
                }.get(report["risk_type"], "gray")

                folium.Marker(
                    location=[report["lat"], report["lon"]],
                    popup=f'{report["risk_type"]} - {report["location"]}',
                    icon=folium.Icon(color=icon_color)
                ).add_to(map)
            except:
                continue
        st_folium(map, width=900)

        # Show table
        df = pd.DataFrame(risk_data)
        with st.expander("📄 View Risk Report Table"):
            st.dataframe(df)

    else:
        st.error(f"❌ Failed to load reports: {res.status_code} - {res.text}")
except Exception as e:
    st.error(f"❌ Failed to load reports: {e}")

# --------- Download Offline Map ---------
if st.button("⬇️ Download Risk Data (Offline Use)"):
    try:
        data = requests.get(f"{API_URL}/reports/").json()
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV Map", csv, "offline_risks.csv", "text/csv")
    except Exception as e:
        st.error(f"❌ Unable to fetch downloadable map: {e}")
