import sqlite3
import os
import hashlib
import time
import socket

# ✅ Make sure this path is correct and matches your Streamlit app's user DB
DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/Road Freight Risk AI/GitHub_Road_Freight_Risk_AI_Starter/frontend/streamlit/users.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def reset_database():
    # ✅ Ensure all parent folders exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # 🧹 Remove existing DB if found
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🧹 Existing database removed.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 🚧 Create users table
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

    # 📋 Create login log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT,
            ip_address TEXT,
            success INTEGER
        )
    ''')

    # 👥 Add admin and user test accounts
    users = [
        ("admin", hash_password("admin123"), "admin", "12345678901"),
        ("user", hash_password("user123"), "user", "10987654321")
    ]

    c.executemany('''
        INSERT INTO users (username, password, role, nin)
        VALUES (?, ?, ?, ?)
    ''', users)

    conn.commit()
    conn.close()
    print("✅ Database reset complete with test accounts.")

if __name__ == "__main__":
    reset_database()
