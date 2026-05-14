import streamlit as st

from modules.pronostiek import show_pronostiek

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "main_page" not in st.session_state:
    st.session_state.main_page = "🏠 Hoofdmenu"


def go_to(page):
    st.session_state.main_page = page


st.markdown("""
<style>
.block-container {
    max-width: 820px;
    padding-top: 5rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
}

.main-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
}

.main-subtitle {
    text-align: center;
    color: #cbd5e1;
    font-size: 0.9rem;
    margin-bottom: 1.2rem;
}

.stButton button {
    min-height: 42px;
    border-radius: 12px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)


if st.session_state.main_page != "🏠 Hoofdmenu":
    if st.button("☰ Hoofdmenu", use_container_width=True):
        go_to("🏠 Hoofdmenu")
    st.write("")


if st.session_state.main_page == "🏠 Hoofdmenu":

    st.markdown('<div class="main-title">⚽ WK 2026 Pronostiek</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Kies wat je wil doen</div>', unsafe_allow_html=True)

    if st.button("🔐 Inloggen", use_container_width=True):
        go_to("🔐 Inloggen")

    if st.button("📝 Registreren", use_container_width=True):
        go_to("📝 Registreren")

    if st.button("⚽ Pronostiek invullen", use_container_width=True):
        go_to("⚽ Pronostiek")

    if st.button("🖨️ Stand uitprinten / PDF maken", use_container_width=True):
        go_to("🖨️ Stand uitprinten")


elif st.session_state.main_page == "🔐 Inloggen":
    st.subheader("🔐 Inloggen")
    st.info("Hier komt het login-gedeelte.")


elif st.session_state.main_page == "📝 Registreren":
    st.subheader("📝 Registreren")
    st.info("Hier komt het registratie-gedeelte.")


elif st.session_state.main_page == "⚽ Pronostiek":
    show_pronostiek(user_id="Tom")


elif st.session_state.main_page == "🖨️ Stand uitprinten":
    st.subheader("🖨️ Stand uitprinten")
    st.info("Hier komt later de PDF-export.")
