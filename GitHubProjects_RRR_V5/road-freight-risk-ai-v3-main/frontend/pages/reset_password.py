# pages/reset_password.py

import streamlit as st
import requests
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Reset Password",
    page_icon="🔐",
    layout="centered"
)

# Get token from URL parameters
def get_token_from_url():
    """Extract token from URL parameters"""
    # In Streamlit, we can access query parameters
    params = st.experimental_get_query_params()
    return params.get("token", [None])[0]

# Password validation
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    return True, "Password is strong"

# Main UI
st.title("🔐 Reset Your Password")
st.markdown("Enter your new password below.")

# Get token from URL
token = get_token_from_url()

if not token:
    st.error("❌ Invalid or missing reset token.")
    st.markdown("Please use the reset link from your email.")
    st.page_link("pages/login.py", label="🔐 Back to Login")
    st.stop()

# Password reset form
with st.form("reset_password_form"):
    st.subheader("🔑 New Password")
    
    new_password = st.text_input(
        "New Password",
        type="password",
        placeholder="Enter your new password",
        help="Password must be at least 8 characters with uppercase, lowercase, and number"
    )
    
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Confirm your new password"
    )
    
    submitted = st.form_submit_button("🔄 Reset Password")
    
    if submitted:
        # Validate passwords
        if not new_password:
            st.error("❌ Please enter a new password.")
        elif not confirm_password:
            st.error("❌ Please confirm your password.")
        elif new_password != confirm_password:
            st.error("❌ Passwords do not match.")
        else:
            # Validate password strength
            is_valid, message = validate_password(new_password)
            if not is_valid:
                st.error(f"❌ {message}")
            else:
                # Submit password reset
                try:
                    response = requests.post(f"{API_URL}/auth/reset-password", json={
                        "token": token,
                        "new_password": new_password
                    })
                    
                    if response.status_code == 200:
                        st.success("✅ Password reset successfully!")
                        st.balloons()
                        st.markdown("You can now log in with your new password.")
                        
                        # Clear session and redirect
                        if "logged_in" in st.session_state:
                            del st.session_state["logged_in"]
                        if "username" in st.session_state:
                            del st.session_state["username"]
                        
                        st.page_link("pages/login.py", label="🔐 Go to Login")
                        
                    elif response.status_code == 400:
                        error_detail = response.json().get("detail", "Invalid token")
                        if "expired" in error_detail.lower():
                            st.error("❌ Reset link has expired. Please request a new one.")
                            st.page_link("pages/forgot_password.py", label="🔄 Request New Reset Link")
                        else:
                            st.error(f"❌ {error_detail}")
                    else:
                        st.error("❌ An error occurred. Please try again.")
                        
                except Exception as e:
                    st.error(f"🚫 Network error: {e}")

# Password strength indicator
if new_password:
    is_valid, message = validate_password(new_password)
    if is_valid:
        st.success(f"✅ {message}")
    else:
        st.warning(f"⚠️ {message}")

# Security tips
st.markdown("---")
st.subheader("🔒 Password Security Tips")
st.markdown("""
- Use at least 8 characters
- Include uppercase and lowercase letters
- Include numbers
- Consider using special characters
- Don't reuse passwords from other accounts
- Use a password manager for better security
""")

# Footer
st.markdown("---")
st.caption("🔐 For security reasons, this reset link will expire after 1 hour.") 