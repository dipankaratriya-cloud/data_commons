"""Authentication module for Streamlit app with Google Sheets access control."""

import streamlit as st
import hashlib
import json
import requests
from pathlib import Path
from typing import Optional, Tuple

# Google Sheet URL for allowed emails (publish as CSV)
# Format: https://docs.google.com/spreadsheets/d/SHEET_ID/gviz/tq?tqx=out:csv
ALLOWED_EMAILS_SHEET_ID = "1_qNWLfPJE3ImpSWnuo0bt5RJLBVnQdE5fSVnOohs1qg"

# Local file to store registered users
USERS_FILE = Path(__file__).parent.parent.parent / "users.json"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict:
    """Load registered users from JSON file."""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_users(users: dict) -> None:
    """Save registered users to JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_allowed_emails() -> set:
    """Fetch allowed emails from Google Sheet."""
    try:
        # Try CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{ALLOWED_EMAILS_SHEET_ID}/gviz/tq?tqx=out:csv"
        response = requests.get(csv_url, timeout=10)

        if response.status_code == 200:
            # Parse CSV content
            lines = response.text.strip().split('\n')
            emails = set()

            for line in lines[1:]:  # Skip header row
                # Handle CSV format (may have quotes)
                email = line.strip().strip('"').strip("'").lower()
                if email and '@' in email:
                    # Handle multiple columns - take first column
                    email = email.split(',')[0].strip().strip('"').lower()
                    if '@' in email:
                        emails.add(email)

            return emails

        # Fallback: try alternative URL format
        alt_url = f"https://docs.google.com/spreadsheets/d/{ALLOWED_EMAILS_SHEET_ID}/export?format=csv"
        response = requests.get(alt_url, timeout=10)

        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            emails = set()

            for line in lines[1:]:
                email = line.strip().strip('"').strip("'").lower()
                if email and '@' in email:
                    email = email.split(',')[0].strip().strip('"').lower()
                    if '@' in email:
                        emails.add(email)

            return emails

    except Exception as e:
        st.warning(f"Could not fetch allowed emails from Google Sheet: {e}")

    return set()


def is_email_allowed(email: str) -> bool:
    """Check if an email is in the allowed list from Google Sheet."""
    allowed_emails = get_allowed_emails()

    # If sheet is empty or inaccessible, show warning
    if not allowed_emails:
        st.warning("Could not verify email access. Please ensure the Google Sheet is publicly accessible.")
        return False

    return email.lower() in allowed_emails


def register_user(email: str, password: str) -> Tuple[bool, str]:
    """Register a new user."""
    email = email.lower().strip()

    # Validate email format
    if not email or '@' not in email:
        return False, "Please enter a valid email address"

    # Check if email is allowed
    if not is_email_allowed(email):
        return False, "Your email is not authorized to access this application. Please contact the administrator."

    # Load existing users
    users = load_users()

    # Check if already registered
    if email in users:
        return False, "This email is already registered. Please login instead."

    # Register new user
    users[email] = {
        "password_hash": hash_password(password),
        "registered": True
    }
    save_users(users)

    return True, "Registration successful! Please login."


def authenticate_user(email: str, password: str) -> Tuple[bool, str]:
    """Authenticate a user."""
    email = email.lower().strip()

    # Load users
    users = load_users()

    # Check if user exists
    if email not in users:
        return False, "Email not registered. Please sign up first."

    # Verify password
    if users[email]["password_hash"] != hash_password(password):
        return False, "Incorrect password. Please try again."

    # Verify email is still allowed (in case removed from sheet)
    if not is_email_allowed(email):
        return False, "Your access has been revoked. Please contact the administrator."

    return True, "Login successful!"


def show_auth_page() -> Optional[str]:
    """Display authentication page and return authenticated email or None."""

    # Check if already logged in
    if st.session_state.get("authenticated") and st.session_state.get("user_email"):
        return st.session_state["user_email"]

    # Auth page styling
    st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="auth-header">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="margin-bottom: 1rem;">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            <h1 style="color: #000000; margin: 0;">Metadata Extractor</h1>
            <p style="color: #6b7280; margin-top: 0.5rem;">Please login or sign up to continue</p>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for Login and Signup
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email", placeholder="your.email@example.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            login_submit = st.form_submit_button("Login", use_container_width=True, type="primary")

            if login_submit:
                if not login_email or not login_password:
                    st.error("Please enter both email and password")
                else:
                    success, message = authenticate_user(login_email, login_password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = login_email.lower()
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    with signup_tab:
        with st.form("signup_form"):
            signup_email = st.text_input("Email", placeholder="your.email@example.com", key="signup_email")
            signup_password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="signup_confirm")
            signup_submit = st.form_submit_button("Sign Up", use_container_width=True, type="primary")

            if signup_submit:
                if not signup_email or not signup_password:
                    st.error("Please fill in all fields")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(signup_email, signup_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    # Info box
    st.markdown("---")
    st.info("**Note:** Only authorized emails can access this application. Contact your administrator if you need access.")

    return None


def logout():
    """Logout the current user."""
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = None


def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated"):
            show_auth_page()
            return None
        return func(*args, **kwargs)
    return wrapper
