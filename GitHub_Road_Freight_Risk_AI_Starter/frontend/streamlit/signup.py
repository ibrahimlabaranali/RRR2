import streamlit as st
import sqlite3
import hashlib

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/GitHubProjects/frontend/streamlit/users.db"

# Utility: Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Register new user
def register_user(username, password, role):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True, "✅ Registration successful. Please log in."
    except sqlite3.IntegrityError:
        return False, "❌ Username already exists."

# --------- Streamlit UI ---------
st.set_page_config(page_title="Sign Up", layout="centered")
st.title("📝 Road Freight Risk AI - Sign Up")

init_db()

with st.form("signup_form"):
    username = st.text_input("Choose Username")
    password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    role = st.radio("Select Role", options=["user", "admin"])

    submitted = st.form_submit_button("Register")
    if submitted:
        if not username or not password or not confirm_password:
            st.warning("⚠️ All fields are required.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            success, message = register_user(username, password, role)
            if success:
                st.success(message)
            else:
                st.error(message)
