import streamlit as st
from welcome_page import welcome_page
from signup_page import sign_up
from login_page import login
from motivate_page import mood_selection_page
from journal_entry_page import journal_entry_page 
from past_entries import view_past_entries_page
from dotenv import load_dotenv
import os

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL")


# Set the page configuration ONCE at the top of app.py
st.set_page_config(page_title="AI Journaling - MoodoAI", page_icon="🤖", layout="wide")

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "Welcome"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "users" not in st.session_state:
    st.session_state.users = {}
if "username" not in st.session_state:
    st.session_state.username = None
if "selected_mood" not in st.session_state: 
    st.session_state.selected_mood = None

# Sidebar navigation
st.sidebar.title("🚀 Navigation")
selected_page = st.sidebar.radio(
    "Go to:",
    ["🏠 Welcome", "🔑 Login", "📝 Sign Up", "💬 Motivate", "📖 Journal", "📚 View Entries"],
    index=["Welcome", "Login", "Sign Up", "Motivate", "Journal", "View Entries"].index(st.session_state.page)
)


# Update the current page based on sidebar selection
if selected_page.startswith("🏠"):
    st.session_state.page = "Welcome"
elif selected_page.startswith("🔑"):
    st.session_state.page = "Login"
elif selected_page.startswith("📝"):
    st.session_state.page = "Sign Up"
elif selected_page.startswith("💬"):
    if not st.session_state.logged_in:
        st.sidebar.warning("🔒 Please log in to access Motivate.")
        st.session_state.page = "Login"
    else:
        st.session_state.page = "Motivate"
elif selected_page.startswith("📖"):
    if not st.session_state.logged_in:
        st.sidebar.warning("🔒 Please log in to access the Journal.")
        st.session_state.page = "Login"
    else:
        st.session_state.page = "Journal"
elif selected_page.startswith("📚"):
    if not st.session_state.logged_in:
        st.sidebar.warning("🔒 Please log in to view your entries.")
        st.session_state.page = "Login"
    else:
        st.session_state.page = "View Entries"

# Add Logout button if the user is logged in
if st.session_state.logged_in:
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None  # Clear the username on logout
        st.session_state.page = "Welcome"
        st.sidebar.success("You have been logged out successfully.")

# Page routing logic
if st.session_state.page == "Welcome":
    welcome_page()
elif st.session_state.page == "Sign Up":
    sign_up()
elif st.session_state.page == "Login":
    login()
elif st.session_state.page == "Motivate":
    if st.session_state.username:
        mood_selection_page(username=st.session_state.username)
    else:
        st.error("You need to log in to use this page.")
elif st.session_state.page == "Journal":
    if st.session_state.username:
        journal_entry_page(username=st.session_state.username)
    else:
        st.error("You need to log in to access the Journal page.")
elif st.session_state.page == "View Entries":
    if st.session_state.username:
        view_past_entries_page(username=st.session_state.username)  # New page for viewing entries
    else:
        st.error("You need to log in to view your journal entries.")
