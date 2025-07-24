import sqlite3
import hashlib
import os
from typing import Optional, Tuple

# --------- CONFIG ---------
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


# --------- SECURITY FUNCTIONS ---------
def hash_password(password: str) -> str:
    """Returns SHA-256 hash of the input password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# --------- DB SETUP ---------
def init_db() -> None:
    """Initializes the user database with required schema."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                nin TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()


# --------- USER OPERATIONS ---------
def register_user(username: str, password: str, nin: str, role: str = "user") -> Tuple[bool, str]:
    """
    Attempts to register a new user.

    Returns:
        (True, "Success") if registration succeeds,
        (False, "Reason") otherwise
    """
    if not username or not password or not nin:
        return False, "All fields are required."

    if len(nin) != 11 or not nin.isdigit():
        return False, "NIN must be 11 digits."

    hashed_pw = hash_password(password)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? OR nin=?", (username, nin))
            if c.fetchone():
                return False, "Username or NIN already exists."

            c.execute("INSERT INTO users (username, password, role, nin) VALUES (?, ?, ?, ?)",
                      (username, hashed_pw, role, nin))
            conn.commit()
        return True, "User registered successfully."
    except Exception as e:
        return False, f"Database error: {e}"


def authenticate_user(username: str, password: str) -> Optional[Tuple[int, str, str, str]]:
    """
    Authenticates a user.

    Returns:
        (id, username, role, nin) if valid, None otherwise.
    """
    hashed_pw = hash_password(password)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, role, nin FROM users WHERE username=? AND password=?",
                      (username, hashed_pw))
            user = c.fetchone()
        return user
    except Exception:
        return None


def get_user_by_nin(nin: str) -> Optional[Tuple[int, str, str]]:
    """
    Fetches a user by NIN.

    Returns:
        (id, username, role) if found, None otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, role FROM users WHERE nin=?", (nin,))
            return c.fetchone()
    except Exception:
        return None
