import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Session management (simplified for Streamlit)
if "user" not in st.session_state:
    st.session_state.user = None

def signup(email, password):
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        return result.user
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

def login(email, password):
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return result.user
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def save_reflection(user_id, date, entry):
    existing = supabase.table("reflections").select("*").eq("user_id", user_id).eq("date", date).execute()
    if existing.data:
        supabase.table("reflections").update({"reflection": entry}).eq("user_id", user_id).eq("date", date).execute()
    else:
        supabase.table("reflections").insert({"user_id": user_id, "date": date, "reflection": entry}).execute()

def get_user_reflections(user_id):
    result = supabase.table("reflections").select("*").eq("user_id", user_id).order("date", desc=False).execute()
    return result.data

# Streamlit App
st.set_page_config(page_title="The Ready Soul", layout="centered")
st.title("🌿 The Ready Soul – Multi-User Reflections")

if not st.session_state.user:
    st.subheader("Login or Sign Up")
    choice = st.radio("Choose an action", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Continue"):
        if choice == "Sign Up":
            user = signup(email, password)
        else:
            user = login(email, password)
        if user:
            st.session_state.user = user
            st.success("Logged in successfully!")
            st.experimental_rerun()
else:
    st.success(f"Welcome, {st.session_state.user.email}")
    st.markdown("---")

    # Reflections UI
    today = datetime.today().strftime('%Y-%m-%d')
    st.subheader(f"🗓️ Reflection for {today}")
    entry = st.text_area("Write your thoughts for today:")

    if st.button("Save Today's Reflection"):
        save_reflection(st.session_state.user.id, today, entry)
        st.success("Reflection saved.")

    st.markdown("---")
    st.subheader("📅 View Past Reflections")
    reflections = get_user_reflections(st.session_state.user.id)
    if reflections:
        date_options = [r["date"] for r in reflections]
        selected_date = st.selectbox("Select a date", date_options[::-1])
        selected = next(r for r in reflections if r["date"] == selected_date)
        updated_entry = st.text_area("Edit Reflection", selected["reflection"])
        if st.button("Update Reflection"):
            save_reflection(st.session_state.user.id, selected_date, updated_entry)
            st.success("Reflection updated.")
    else:
        st.info("No reflections yet. Start journaling today!")

    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()
