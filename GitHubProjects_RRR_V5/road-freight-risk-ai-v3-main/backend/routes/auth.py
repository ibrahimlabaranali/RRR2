# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Form, Depends
from pydantic import BaseModel, EmailStr
import sqlite3
import bcrypt
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt

load_dotenv()
router = APIRouter()

DB_PATH = os.getenv("USER_DB", "users.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@roadriskai.com")


class AuthRequest(BaseModel):
    username: str
    password: str
    nin: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    nin: str


def send_reset_email(email: str, reset_token: str):
    """Send password reset email securely"""
    try:
        reset_link = f"https://your-frontend-url.com/reset-password?token={reset_token}"
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = "Password Reset - Road Freight Risk AI"
        
        body = f"""
        Hello,
        
        You requested a password reset for your Road Freight Risk AI account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Road Freight Risk AI Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        if SMTP_USERNAME and SMTP_PASSWORD:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        else:
            # For development/testing - log instead of sending
            print(f"RESET EMAIL (DEV): {email} - Token: {reset_token}")
            return True
            
    except Exception as e:
        print(f"Email sending error: {e}")
        return False


def create_reset_token(email: str) -> str:
    """Create a secure reset token"""
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "password_reset"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_reset_token(token: str) -> str:
    """Verify and decode reset token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type")
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


@router.post("/register")
def register_user(auth: UserRegistration):
    """Register a new user with email validation"""
    if not auth.nin.isdigit() or len(auth.nin) != 11:
        raise HTTPException(status_code=400, detail="Invalid NIN format")
    
    # Validate email format
    if not auth.email or "@" not in auth.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate password strength
    if len(auth.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    hashed_pw = bcrypt.hashpw(auth.password.encode(), bcrypt.gensalt())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, 
            email TEXT UNIQUE,
            password TEXT, 
            nin TEXT, 
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, nin, role) VALUES (?, ?, ?, ?, ?)",
            (auth.username, auth.email, hashed_pw, auth.nin, "user")
        )
        conn.commit()
        return {"status": "success", "message": "✅ Registered successfully"}
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            raise HTTPException(status_code=409, detail="Username already exists")
        elif "email" in str(e):
            raise HTTPException(status_code=409, detail="Email already registered")
        else:
            raise HTTPException(status_code=409, detail="Registration failed")
    finally:
        conn.close()


@router.post("/login")
def login_user(auth: AuthRequest):
    """Login with username/NIN and password"""
    if not auth.username or not auth.password or not auth.nin:
        raise HTTPException(status_code=400, detail="All fields are required")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, password, role FROM users WHERE username=? AND nin=?", 
        (auth.username, auth.nin)
    )
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(auth.password.encode(), result[3]):
        user_id, username, email, _, role = result
        return {
            "status": "success", 
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "message": "✅ Login successful"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    """Handle forgot password request"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email=?", (request.email,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        # Don't reveal if email exists or not for security
        return {"status": "success", "message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = create_reset_token(request.email)
    
    # Store reset token (in production, use Redis or database)
    # For now, we'll use a simple file-based approach
    reset_tokens_file = "reset_tokens.txt"
    with open(reset_tokens_file, "a") as f:
        f.write(f"{request.email}:{reset_token}:{datetime.utcnow().isoformat()}\n")
    
    # Send reset email
    if send_reset_email(request.email, reset_token):
        return {"status": "success", "message": "If the email exists, a reset link has been sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send reset email")


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    if len(request.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    try:
        email = verify_reset_token(request.token)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Hash new password
    hashed_pw = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt())
    
    # Update password in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.commit()
    conn.close()
    
    # Clean up used token
    reset_tokens_file = "reset_tokens.txt"
    if os.path.exists(reset_tokens_file):
        with open(reset_tokens_file, "r") as f:
            lines = f.readlines()
        with open(reset_tokens_file, "w") as f:
            for line in lines:
                if not line.startswith(f"{email}:"):
                    f.write(line)
    
    return {"status": "success", "message": "✅ Password reset successfully"}


@router.get("/verify-email/{email}")
def verify_email_exists(email: str):
    """Check if email exists (for frontend validation)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    return {"exists": result is not None}
