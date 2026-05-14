import streamlit as st

from modules.database import (
    load_users,
    load_matches,
    load_results,
    load_standings,
)
from modules.auth import (
    show_login_page,
    show_register_page,
    require_login,
    restore_login_from_cookie,
    logout,
    get_display_team_name,
)
from modules.pronostiek import show_pronostiek
from modules.admin_results import show_admin_results

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)


@st.cache_data(ttl=60)
def get_users():
    return load_users()


users_df = get_users()
cookies = restore_login_from_cookie(users_df)

if "main_page" not in st.session_state:
    st.session_state.main_page = "🏠 Hoofdmenu"


def go_to(page):
    st.session_state.main_page = page
    st.rerun()


st.markdown("""
<style>
.block-container {
    max-width: 820px;
    padding-top: 1rem !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    padding-bottom: 5rem !important;
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

.user-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 14px;
    padding: 0.8rem;
    margin-bottom: 1rem;
    text-align: center;
}

.user-name {
    font-size: 1.1rem;
    font-weight: 900;
}

.user-team {
    color: #cbd5e1;
    font-size: 0.9rem;
}

.stButton button {
    min-height: 42px;
    border-radius: 12px;
    font-weight: 800;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


if st.session_state.main_page != "🏠 Hoofdmenu":
    if st.button("☰ Hoofdmenu", use_container_width=True):
        go_to("🏠 Hoofdmenu")


if st.session_state.main_page == "🏠 Hoofdmenu":

    st.markdown(
        '<div class="main-title">⚽ WK 2026 Pronostiek</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">Kies wat je wil doen</div>',
        unsafe_allow_html=True,
    )

    if "user" in st.session_state:

        user = st.session_state["user"]

        naam = str(user.get("naam", "") or "").strip()
        team = get_display_team_name(user)

        st.markdown(
            f"""
<div class="user-card">
    <div>Ingelogd als</div>
    <div class="user-name">{naam}</div>
    <div class="user-team">{team}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⚽ Pronostiek invullen", use_container_width=True, type="primary"):
            go_to("⚽ Pronostiek")

        if st.button("📊 Algemene standen", use_container_width=True):
            go_to("📊 Algemene standen")

        if st.button("🖨️ Stand uitprinten / PDF maken", use_container_width=True):
            go_to("🖨️ Stand uitprinten")

        if bool(user.get("admin", False)):
            st.write("---")
            st.markdown("### ⚙️ Admin")

            if st.button("🏆 Officiële uitslagen", use_container_width=True):
                go_to("🏆 Admin uitslagen")

        st.write("---")

        if st.button("🚪 Uitloggen", use_container_width=True):
            logout(cookies)

    else:

        if st.button("🔐 Inloggen", use_container_width=True, type="primary"):
            go_to("🔐 Inloggen")

        if st.button("📝 Registreren", use_container_width=True):
            go_to("📝 Registreren")

        st.info("Log in om je pronostiek in te vullen.")

        st.write("---")

        if st.button("📊 Algemene standen bekijken", use_container_width=True):
            go_to("📊 Algemene standen")


elif st.session_state.main_page == "🔐 Inloggen":
    show_login_page(users_df)


elif st.session_state.main_page == "📝 Registreren":
    show_register_page(users_df)


elif st.session_state.main_page == "⚽ Pronostiek":

    user = require_login()

    if user is not None:
        show_pronostiek(
            user_id=user["naam"],
            standings_df=load_standings(),
        )


elif st.session_state.main_page == "🏆 Admin uitslagen":

    user = require_login()

    if user is not None:
        if bool(user.get("admin", False)):
            show_admin_results(
                load_matches(),
                load_results(),
            )
        else:
            st.error("Geen adminrechten.")


elif st.session_state.main_page == "🖨️ Stand uitprinten":

    user = require_login()

    if user is not None:
        st.subheader("🖨️ Stand uitprinten")
        st.info("Hier komt later de PDF-export.")


elif st.session_state.main_page == "📊 Algemene standen":

    st.subheader("📊 Algemene standen")
    st.info("Hier komt later het algemene klassement.")
