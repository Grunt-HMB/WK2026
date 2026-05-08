import streamlit as st
from modules.auth import show_login
from modules.matches import show_matches

st.set_page_config(page_title="WK 2026 Pronostiek", layout="wide")

st.title("⚽ WK 2026 Pronostiek")

user = show_login()

if user:
    show_matches(user)
