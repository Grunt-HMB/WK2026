import streamlit as st

from modules.pronostiek import show_pronostiek

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "main_page" not in st.session_state:
    st.session_state.main_page = "⚽ Pronostiek"

with st.popover("☰ Hoofdmenu"):
    if st.button("🔐 Inloggen", use_container_width=True):
        st.session_state.main_page = "🔐 Inloggen"

    if st.button("📝 Registreren", use_container_width=True):
        st.session_state.main_page = "📝 Registreren"

    if st.button("⚽ Pronostiek", use_container_width=True):
        st.session_state.main_page = "⚽ Pronostiek"

    if st.button("🖨️ Stand uitprinten", use_container_width=True):
        st.session_state.main_page = "🖨️ Stand uitprinten"


if st.session_state.main_page == "⚽ Pronostiek":
    show_pronostiek(user_id="Tom")

elif st.session_state.main_page == "🔐 Inloggen":
    st.subheader("🔐 Inloggen")
    st.info("Hier komt het login-gedeelte.")

elif st.session_state.main_page == "📝 Registreren":
    st.subheader("📝 Registreren")
    st.info("Hier komt het registratie-gedeelte.")

elif st.session_state.main_page == "🖨️ Stand uitprinten":
    st.subheader("🖨️ Stand uitprinten")
    st.info("Hier komt later de PDF-export.")
