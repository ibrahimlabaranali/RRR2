import streamlit as st
import sqlite3
import hashlib
import socket
import time
import os

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/GitHubProjects/frontend/streamlit/users.db"
MAX_LOGIN_ATTEMPTS = 5

# ----------------- Utility Functions -----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            nin TEXT UNIQUE NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            locked_until INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            ip_address TEXT,
            success INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_login_attempt(username, success):
    ip = socket.gethostbyname(socket.gethostname())
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO login_logs (username, timestamp, ip_address, success) VALUES (?, ?, ?, ?)",
              (username, timestamp, ip, int(success)))
    conn.commit()
    conn.close()

def is_account_locked(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT locked_until FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return int(time.time()) < row[0]
    return False

def register_user(username, password, nin, role="user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? OR nin=?", (username, nin))
    if c.fetchone():
        conn.close()
        return False  # Duplicate username or NIN
    c.execute("INSERT INTO users (username, password, role, nin) VALUES (?, ?, ?, ?)",
              (username, hash_password(password), role, nin))
    conn.commit()
    conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, nin, failed_attempts FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def increment_failed_attempts(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username=?", (username,))
    c.execute("SELECT failed_attempts FROM users WHERE username=?", (username,))
    attempts = c.fetchone()[0]
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lockout_time = int(time.time()) + 600  # Lock for 10 mins
        c.execute("UPDATE users SET locked_until=?, failed_attempts=0 WHERE username=?", (lockout_time, username))
    conn.commit()
    conn.close()

def reset_failed_attempts(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET failed_attempts = 0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

# ----------------- UI -----------------
st.set_page_config(page_title="Login / Register", layout="centered")
st.title("🚚 Road Freight Risk AI – Secure Access Portal")

init_db()

menu = ["Login", "Register"]
choice = st.selectbox("Choose Action", menu)

# ---------- LOGIN FORM ----------
if choice == "Login":
    st.subheader("🔐 Login to Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if is_account_locked(username):
            st.error("❌ Account temporarily locked due to multiple failed attempts. Try again later.")
        else:
            user = authenticate_user(username, password)
            if user:
                user_id, uname, role, nin, _ = user
                st.session_state.authenticated = True
                st.session_state.username = uname
                st.session_state.role = role
                st.session_state.nin = nin

                reset_failed_attempts(username)
                log_login_attempt(username, True)

                st.success(f"✅ Welcome {uname} ({role})")

                if role == "admin":
                    st.switch_page("admin_dashboard.py")
                elif role == "user":
                    st.switch_page("user_dashboard.py")
            else:
                log_login_attempt(username, False)
                increment_failed_attempts(username)
                st.error("❌ Invalid username or password.")

# ---------- REGISTRATION FORM ----------
elif choice == "Register":
    st.subheader("✍️ Register New Account")
    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")
    new_nin = st.text_input("Your National Identification Number (11 digits)")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Register"):
        if not new_user or not new_pass or not new_nin:
            st.warning("⚠️ All fields are required.")
        elif not new_nin.isdigit() or len(new_nin) != 11:
            st.error("❌ NIN must be 11 numeric digits.")
        elif register_user(new_user, new_pass, new_nin, role):
            st.success("🎉 Registration successful. Please log in.")
        else:
            st.error("⚠️ Username or NIN already exists.")
