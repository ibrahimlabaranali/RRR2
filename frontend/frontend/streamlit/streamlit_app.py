
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

API_URL = "https://road-freight-risk-ai.onrender.com"

st.set_page_config(layout="wide")
st.title("🚚 Road Freight Risk AI Dashboard")

st.markdown("### 📨 Submit New Report")

components.html("""
<script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const coords = position.coords;
            window.parent.postMessage(
                JSON.stringify({
                    latitude: coords.latitude,
                    longitude: coords.longitude
                }), "*"
            );
        },
        (err) => {
            window.parent.postMessage(JSON.stringify({error: err.message}), "*");
        }
    );
</script>
""", height=0)

if "gps_lat" not in st.session_state:
    st.session_state.gps_lat = ""
if "gps_lon" not in st.session_state:
    st.session_state.gps_lon = ""
if "gps_error" not in st.session_state:
    st.session_state.gps_error = None

def handle_js_response():
    import streamlit_js_eval
    result = streamlit_js_eval.get_geolocation()
    if result and "latitude" in result and "longitude" in result:
        st.session_state.gps_lat = result["latitude"]
        st.session_state.gps_lon = result["longitude"]
    elif "error" in result:
        st.session_state.gps_error = result["error"]

st.markdown("✅ Location auto-detection via GPS is enabled (if you allow it in your browser).")
handle_js_response()

with st.form("risk_form"):
    user_id = st.text_input("User ID", value="1")
    category = st.selectbox("Risk Category", ["Armed Robbery", "Flooding", "Accident", "Protest", "Banditry", "Other"])
    location = st.text_input("Location (e.g., Kaduna - Abuja Highway)")
    state = st.text_input("State")
    lga = st.text_input("Local Government Area (LGA)")

    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("Latitude", value=str(st.session_state.gps_lat))
    with col2:
        lon = st.text_input("Longitude", value=str(st.session_state.gps_lon))

    notes = st.text_area("Additional Notes (Optional)")
    submitted = st.form_submit_button("Submit Report")

    if submitted:
        try:
            payload = {
                "user_id": int(user_id),
                "risk_type": category,
                "description": notes,
                "location": location,
                "state": state,
                "lga": lga,
                "lat": float(lat),
                "lon": float(lon)
            }
            response = requests.post(f"{API_URL}/reports/", json=payload)
            if response.status_code == 200:
                st.success("✅ Report submitted successfully")
            else:
                st.error(f"❌ Failed to submit report: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")

st.markdown("### 🗺 View Reported Risks")

try:
    map = folium.Map(location=[10.5, 7.4], zoom_start=6)
    risk_data = requests.get(f"{API_URL}/reports/").json()

    for report in risk_data:
        try:
            folium.Marker(
                location=[report["lat"], report["lon"]],
                popup=f'{report["risk_type"]} - {report["location"]}',
                icon=folium.Icon(color="red" if report["risk_type"] == "Armed Robbery" else "blue")
            ).add_to(map)
        except Exception as err:
            continue

    st_folium(map, width=900)

except Exception as e:
    st.error(f"❌ Failed to load reports: {e}")
