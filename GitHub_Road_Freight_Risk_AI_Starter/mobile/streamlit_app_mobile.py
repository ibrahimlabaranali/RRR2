import streamlit as st
import requests
import datetime
import sqlite3
import hashlib
import folium
from streamlit_folium import st_folium
import pandas as pd
from io import BytesIO
import os
from dotenv import load_dotenv

# ------------- Load Env Variables -------------
load_dotenv()
API_URL = os.getenv("API_URL", "https://road-freight-risk-ai.onrender.com/reports/")
DB_FILE = os.getenv("USER_DB", "users.db")

# ------------- Page Config -------------
st.set_page_config(page_title="📱 Road Risk Reporter", layout="wide")
st.title("🚚 Road Risk Reporter (Mobile)")

# ------------- Helpers -------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def create_user_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nin TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password, nin, role="user"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, nin, role) VALUES (?, ?, ?, ?)",
              (username, hash_password(password), nin, role))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username, role FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

# ------------- Init DB & Session -------------
create_user_table()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# ------------- Risk Suggestion -------------
def suggest_risks(state):
    risks = {
        "Kaduna": ["Banditry", "Kidnapping", "Checkpoint Delay"],
        "Lagos": ["Robbery", "Protest", "Traffic"],
        "Borno": ["Insurgency", "Road Block"],
    }
    return risks.get(state, ["Accident", "Flooding", "Other"])

# ------------- User Auth UI -------------
auth_choice = st.radio("Select", ["🔐 Login", "📝 Register"], horizontal=True)

if not st.session_state.logged_in:
    with st.form("auth_form"):
        st.subheader("Account Access")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if auth_choice == "📝 Register":
            nin = st.text_input("NIN")
            submit = st.form_submit_button("Register")
            if submit:
                if all([username, password, nin]):
                    try:
                        register_user(username, password, nin)
                        st.success("✅ Account created.")
                    except:
                        st.error("⚠️ Username already exists.")
                else:
                    st.warning("All fields required.")
        else:
            submit = st.form_submit_button("Login")
            if submit:
                result = login_user(username, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = result[0]
                    st.session_state.role = result[1]
                    st.success(f"✅ Welcome {result[0]} ({result[1]})")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")

# ------------- Main App -------------
if st.session_state.logged_in:

    with st.expander("🚨 Submit Road Risk Report", expanded=True):
        with st.form("report_form"):
            location = st.text_input("Road / Area")
            state = st.selectbox("State", ["Kaduna", "Lagos", "Borno", "Abuja"])
            lga = st.text_input("LGA")
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            risk_type = st.selectbox("Risk Type", suggest_risks(state) + ["Other"])
            description = st.text_area("More Details (optional)")
            send = st.form_submit_button("📤 Submit Report")

        if send and all([location, state, lga, lat, lon, risk_type]):
            payload = {
                "username": st.session_state.username,
                "location": location,
                "state": state,
                "lga": lga,
                "lat": lat,
                "lon": lon,
                "risk_type": risk_type,
                "description": description,
                "timestamp": str(datetime.datetime.utcnow())
            }
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code == 201:
                    st.success("✅ Report submitted.")
                else:
                    st.error("🚫 Submission failed.")
            except Exception as e:
                st.error(f"🚨 Error: {e}")

    if st.session_state.role == "admin":
        st.subheader("📊 Admin Dashboard")
        try:
            res = requests.get(API_URL)
            df = pd.DataFrame(res.json())
            st.dataframe(df)

            with st.expander("📥 Export Data"):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download CSV", csv, "reports.csv", "text/csv")

                excel = BytesIO()
                df.to_excel(excel, index=False, engine="xlsxwriter")
                st.download_button("⬇️ Download Excel", excel.getvalue(), "reports.xlsx", "application/vnd.ms-excel")

            st.subheader("🗺 Map of Reports")
            m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
            for _, row in df.iterrows():
                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    popup=f"{row['risk_type']} – {row['location']}",
                    tooltip=row["description"],
                    icon=folium.Icon(color="red")
                ).add_to(m)
            st_folium(m, width=700)

        except Exception as e:
            st.error(f"❌ Error loading reports: {e}")

    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

