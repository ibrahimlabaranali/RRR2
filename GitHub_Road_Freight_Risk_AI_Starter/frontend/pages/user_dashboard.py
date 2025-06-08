import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# ----------------- CONFIG -----------------
st.set_page_config(page_title="User Dashboard", layout="wide")
st.title("📦 Road Freight Risk AI – User Dashboard")

# ----------------- SECURITY CHECK -----------------
if "role" not in st.session_state or st.session_state.role != "user":
    st.error("❌ Access denied. Users only.")
    st.stop()

st.success(f"✅ Welcome {st.session_state.username} (NIN: {st.session_state.nin})")

# ----------------- API ENDPOINT -----------------
API_URL = "https://road-freight-risk-ai.onrender.com/reports/"
SUBMIT_URL = "https://road-freight-risk-ai.onrender.com/reports/"

# ----------------- TABS -----------------
tab1, tab2 = st.tabs(["📍 View Road Risk Reports", "🚨 Submit New Risk Report"])

# ----------------- TAB 1: VIEW REPORTS -----------------
with tab1:
    st.subheader("🗺️ Map of Road Freight Risks with Filters")

    try:
        res = requests.get(API_URL)
        data = res.json() if res.status_code == 200 else []
        df = pd.DataFrame(data)

        if not df.empty:
            # Convert timestamp to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # ----------------- FILTER SECTION -----------------
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_risk = st.multiselect("Filter by Risk Type", df["risk_type"].unique().tolist(), default=None)

            with col2:
                selected_state = st.multiselect("Filter by State", df["state"].unique().tolist(), default=None)

            with col3:
                date_range = st.date_input("Filter by Date Range", 
                                           [df["timestamp"].min().date(), df["timestamp"].max().date()])

            # Apply filters
            if selected_risk:
                df = df[df["risk_type"].isin(selected_risk)]

            if selected_state:
                df = df[df["state"].isin(selected_state)]

            if date_range:
                start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]

            # ----------------- MAP -----------------
            st.subheader("🗺️ Filtered Map View")
            m = folium.Map(location=[10.5, 7.4], zoom_start=6)

            for _, r in df.iterrows():
                popup_text = f"Type: {r['risk_type']}<br>Location: {r['location']}<br>Date: {r['timestamp'].date()}"
                folium.Marker(
                    location=[r["lat"], r["lon"]],
                    popup=popup_text,
                    icon=folium.Icon(color="red" if "robbery" in r["risk_type"].lower() else "blue")
                ).add_to(m)

            st_folium(m, height=450)

            # ----------------- TABLE + DOWNLOAD -----------------
            st.subheader("📋 Filtered Reports Table")
            st.dataframe(df.drop(columns=["lat", "lon"]), use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Filtered Reports CSV", csv, "filtered_road_risks.csv", "text/csv")

        else:
            st.warning("⚠️ No risk reports found.")

    except Exception as e:
        st.error(f"⚠️ Could not retrieve risk data: {e}")

# ----------------- TAB 2: SUBMIT NEW REPORT -----------------
with tab2:
    st.subheader("📢 Submit New Freight Risk")

    with st.form("report_form"):
        location = st.text_input("Location (e.g., Abuja–Kaduna Road)")
        lat = st.number_input("Latitude", format="%.6f")
        lon = st.number_input("Longitude", format="%.6f")
        state = st.text_input("State")
        lga = st.text_input("Local Government Area")
        risk_type = st.selectbox("Risk Type", [
            "Armed Robbery", "Banditry", "Road Block", "Protest", "Flooding",
            "Accident", "Checkpoint Delay", "Kidnapping", "Other"
        ])
        description = st.text_area("Additional Details")
        submit = st.form_submit_button("📤 Submit Report")

    if submit:
        if not all([location, state, lga, risk_type]):
            st.warning("⚠️ Please complete all required fields.")
        else:
            report = {
                "username": st.session_state.username,
                "nin": st.session_state.nin,
                "location": location,
                "lat": lat,
                "lon": lon,
                "state": state,
                "lga": lga,
                "risk_type": risk_type,
                "description": description,
                "timestamp": str(datetime.datetime.utcnow())
            }
            try:
                response = requests.post(SUBMIT_URL, json=report)
                if response.status_code == 201:
                    st.success("✅ Risk report submitted successfully!")
                else:
                    st.error("❌ Failed to submit. Try again.")
            except Exception as e:
                st.error(f"⚠️ Submission error: {e}")
