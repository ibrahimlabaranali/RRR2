import sqlite3
import hashlib

DB_PATH = "C:/Users/dribr/OneDrive/Dokumentumok/GitHubProjects/frontend/streamlit/users.db"

# Hashing password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Register new user (returns success message or error)
def register_user(username, password, role):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True, "✅ User registered successfully."
    except sqlite3.IntegrityError:
        return False, "❌ Username already exists."
    except Exception as e:
        return False, f"❌ Registration failed: {e}"

# Validate login credentials
def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", 
                   (username, hash_password(password)))
    result = cursor.fetchone()
    conn.close()
    if result:
        return True, result[0]  # (True, "admin"/"user")
    return False, None
