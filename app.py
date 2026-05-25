import inspect
import time
import streamlit as st

from modules.database import (
    load_users,
    load_matches,
    load_results,
    load_standings,
    load_predictions,
)

from modules.auth import (
    show_login_page,
    show_register_page,
    require_login,
    restore_login_from_cookie,
    logout,
    get_display_team_name,
)

from modules.admin_results import show_admin_results
from modules.scoreboard import show_scoreboard
from modules.poule_standen import show_poule_standen
from modules.wedstrijdpoules import show_wedstrijdpoules


st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SPLASHSCREEN
# =========================================================

if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    splash = st.empty()

    with splash.container():
        st.markdown("""
        <div style="
            height: 75vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        ">
            <div style="font-size: 4rem;">⚽</div>
            <div style="font-size: 2rem; font-weight: 900;">
                WK 2026 Pronostiek
            </div>
            <div style="margin-top: 0.6rem; color: #94a3b8;">
                Laden...
            </div>
        </div>
        """, unsafe_allow_html=True)

    time.sleep(1.5)
    st.session_state.splash_done = True
    splash.empty()
    st.rerun()


# =========================================================
# DATA
# =========================================================

@st.cache_data(ttl=60)
def get_users():
    return load_users()


def show_scoreboard_safe():
    params = inspect.signature(show_scoreboard).parameters

    if "matches_df" in params and "official_standings_df" in params:
        show_scoreboard(
            users_df=load_users(),
            predictions_df=load_predictions(),
            results_df=load_results(),
            matches_df=load_matches(),
            official_standings_df=load_standings(),
        )
    else:
        show_scoreboard(
            users_df=load_users(),
            predictions_df=load_predictions(),
            results_df=load_results(),
        )


users_df = get_users()
cookies = restore_login_from_cookie(users_df)


# =========================================================
# NAVIGATIE
# =========================================================

if "main_page" not in st.session_state:
    st.session_state.main_page = "🏠 Hoofdmenu"

if st.query_params.get("stand_action"):
    st.session_state.main_page = "⚽ Poulewedstrijden"


def go_to(page):
    st.session_state.main_page = page
    st.rerun()


# =========================================================
# CSS
# =========================================================

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


# =========================================================
# HOME-KNOP
# =========================================================

if st.session_state.main_page not in [
    "🏠 Hoofdmenu",
]:
    if st.button("☰ Hoofdmenu", use_container_width=True):
        go_to("🏠 Hoofdmenu")


# =========================================================
# ROUTING
# =========================================================

if st.session_state.main_page == "🏠 Hoofdmenu":
    st.markdown('<div class="main-title">⚽ WK 2026 Pronostiek</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Kies wat je wil doen</div>', unsafe_allow_html=True)

    if "user" in st.session_state:
        user = st.session_state["user"]
        naam = str(user.get("naam", "") or "").strip()
        team = get_display_team_name(user)

        st.markdown(f"""
        <div class="user-card">
            <div>Ingelogd als</div>
            <div class="user-name">{naam}</div>
            <div class="user-team">{team}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚽ Poulewedstrijden", use_container_width=True):
            go_to("⚽ Poulewedstrijden")

        if st.button("📊 Poulestanden", use_container_width=True):
            go_to("📊 Poulestanden")

        if st.button("🏆 Scoreboard", use_container_width=True):
            go_to("🏆 Scoreboard")

        if bool(user.get("admin", False)):
            st.write("---")
            st.markdown("### ⚙️ Admin")

            if st.button("🏆 Officiële uitslagen invoeren", use_container_width=True):
                go_to("🏆 Admin uitslagen")

            if st.button("🖨️ Stand exporteren (PDF/Print)", use_container_width=True):
                go_to("⚽ Poulewedstrijden")

        st.write("---")

        if st.button("🚪 Uitloggen", use_container_width=True):
            logout(cookies)

    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔐 Inloggen", use_container_width=True, type="primary"):
                go_to("🔐 Inloggen")

        with col2:
            if st.button("📝 Registreren", use_container_width=True):
                go_to("📝 Registreren")

        st.info("Log in om deel te nemen aan de pronostiek.")

        st.write("---")

        if st.button("🏆 Scoreboard bekijken", use_container_width=True):
            go_to("🏆 Scoreboard")


elif st.session_state.main_page == "🔐 Inloggen":
    show_login_page(users_df)


elif st.session_state.main_page == "📝 Registreren":
    show_register_page(users_df)


elif st.session_state.main_page == "⚽ Poulewedstrijden":
    user = require_login()

    if user:
        safe_user_id = str(user.get("naam", "Gast"))
        show_wedstrijd_poules(user_id=safe_user_id)


elif st.session_state.main_page == "📊 Poulestanden":
    user = require_login()

    if user:
        show_poule_standen(
            matches_df=load_matches(),
            official_standings_df=load_standings(),
            predictions_df=load_predictions(user["naam"]),
        )


elif st.session_state.main_page == "🏆 Scoreboard":
    show_scoreboard_safe()


elif st.session_state.main_page == "🏆 Admin uitslagen":
    user = require_login()

    if user and bool(user.get("admin", False)):
        show_admin_results(
            load_matches(),
            load_results(),
        )
    else:
        st.error("Toegang geweigerd.")
