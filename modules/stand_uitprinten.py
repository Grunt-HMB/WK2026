import inspect
import time
import streamlit as st
import streamlit.components.v1 as components

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
from modules.pronostiek import show_pronostiek
from modules.pronostiek_scores import show_pronostiek_scores
from modules.admin_results import show_admin_results
from modules.scoreboard import show_scoreboard
from modules.poule_standen import show_poule_standen


st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# PRINT TESTPAGINA (MET 1/X/2 EN DUBBEL TOETSENBORD)
# =========================================================

def show_stand_uitprinten():
    st.title("🖨️ Stand uitprinten")

    team1 = "Mexico"
    team2 = "Zuid-Afrika"

    html_code = f"""
    <div style="
        font-family: Arial, sans-serif;
        display: flex;
        justify-content: center;
        padding-top: 10px;
    ">
        <div style="
            width: 100%;
            max-width: 440px;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #ddd;
            background: #ffffff;
            color: #111827;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        ">

            <h2 style="
                text-align: center;
                margin-top: 0;
                margin-bottom: 20px;
                font-size: 22px;
            ">
                Score invullen
            </h2>

            <div style="
                display: grid;
                grid-template-columns: 1fr 120px 1fr;
                gap: 10px;
                align-items: center;
                margin-bottom: 20px;
            ">
                <div style="text-align: right; font-size: 16px; font-weight: 800;">
                    <div style="margin-bottom: 4px;">{team1}</div>
                    <input id="score1" type="text" placeholder="0" readonly 
                        style="width: 55px; height: 38px; font-size: 22px; text-align: center; border: 2px solid #cbd5e1; border-radius: 8px; outline: none; background: #fff;">
                </div>
                
                <div style="display: flex; gap: 4px; justify-content: center;">
                    <button onclick="choosePrediction('1')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">1</button>
                    <button onclick="choosePrediction('X')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">X</button>
                    <button onclick="choosePrediction('2')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">2</button>
                </div>

                <div style="text-align: left; font-size: 16px; font-weight: 800;">
                    <div style="margin-bottom: 4px;">{team2}</div>
                    <input id="score2" type="text" placeholder="0" readonly 
                        style="width: 55px; height: 38px; font-size: 22px; text-align: center; border: 2px solid #cbd5e1; border-radius: 8px; outline: none; background: #fff;">
                </div>
            </div>

            <div id="prediction-alert" style="text-align: center; font-weight: bold; color: #2563eb; font-size: 14px; margin-bottom: 15px; display: none;"></div>

            <div id="keyboard-panel" style="display: none; background: #f8fafc; padding: 14px; border-radius: 12px; border: 1px solid #e2e8f0;">
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
                    <span style="font-weight: bold; font-size: 13px; color: #475569;">Exacte doelpunten:</span>
                    <button onclick="closePanel()" style="background: #ef4444; color: white; border: none; border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: bold; cursor: pointer;">Sluiten</button>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div>
                        <div style="font-size: 12px; font-weight: bold; margin-bottom: 6px; text-align: center; color: #64748b;">{team1}</div>
                        <div id="grid-t1" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px;"></div>
                    </div>

                    <div>
                        <div style="font-size: 12px; font-weight: bold; margin-bottom: 6px; text-align: center; color: #64748b;">{team2}</div>
                        <div id="grid-t2" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px;"></div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        var label1 = "{team1}";
        var label2 = "{team2}";

        function choosePrediction(type) {{
            var text = "";
            if(type === '1') text = "Gekozen: " + label1 + " wint (1)";
            if(type === 'X') text = "Gekozen: Gelijkspel (X)";
            if(type === '2') text = "Gekozen: " + label2 + " wint (2)";
            
            document.getElementById('prediction-alert').innerText = text;
            document.getElementById('prediction-alert').style.display = 'block';
            
            document.getElementById('keyboard-panel').style.display = 'block';
            buildKeyboards();
        }}

        function closePanel() {{
            document.getElementById('keyboard-panel').style.display = 'none';
        }}

        function addVal1(val) {{ document.getElementById('score1').value += val; }}
        function delVal1() {{ var v = document.getElementById('score1').value; document.getElementById('score1').value = v.substring(0, v.length - 1); }}
        
        function addVal2(val) {{ document.getElementById('score2').value += val; }}
        function delVal2() {{ var v = document.getElementById('score2').value; document.getElementById('score2').value = v.substring(0, v.length - 1); }}

        function buildKeyboards() {{
            var nums1 = [0,1,2,3,4,5,6,7,8,9];
            nums1.sort(() => Math.random() - 0.5);
            
            var nums2 = [0,1,2,3,4,5,6,7,8,9];
            nums2.sort(() => Math.random() - 0.5);

            var grid1 = document.getElementById('grid-t1');
            var grid2 = document.getElementById('grid-t2');
            
            // Bouw Toetsenbord Links
            var html1 = "";
            for(var i=0; i<9; i++) {{
                html1 += `<input type="button" value="${{nums1[i]}}" onclick="addVal1('${{nums1[i]}}')" style="height:36px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #cbd5e1; border-radius:4px; font-size:14px;">`;
            }}
            html1 += `<input type="button" value="←" onclick="delVal1()" style="height:36px; cursor:pointer; background:#cbd5e1; border:1px solid #94a3b8; border-radius:4px; font-size:12px; font-weight:bold;">`;
            html1 += `<input type="button" value="${{nums1[9]}}" onclick="addVal1('${{nums1[9]}}')" style="height:36px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #cbd5e1; border-radius:4px; font-size:14px;">`;
            grid1.innerHTML = html1;

            // Bouw Toetsenbord Rechts
            var html2 = "";
            for(var i=0; i<9; i++) {{
                html2 += `<input type="button" value="${{nums2[i]}}" onclick="addVal2('${{nums2[i]}}')" style="height:36px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #cbd5e1; border-radius:4px; font-size:14px;">`;
            }}
            html2 += `<input type="button" value="←" onclick="delVal2()" style="height:36px; cursor:pointer; background:#cbd5e1; border:1px solid #94a3b8; border-radius:4px; font-size:12px; font-weight:bold;">`;
            html2 += `<input type="button" value="${{nums2[9]}}" onclick="addVal2('${{nums2[9]}}')" style="height:36px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #cbd5e1; border-radius:4px; font-size:14px;">`;
            grid2.innerHTML = html2;
        }}
    </script>
    """

    components.html(html_code, height=540)


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
# DATA & LOGIN HERSTEL
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
# NAVIGATIE LOGICA
# =========================================================

if "main_page" not in st.session_state:
    st.session_state.main_page = "🏠 Hoofdmenu"


def go_to(page):
    st.session_state.main_page = page
    st.rerun()


# =========================================================
# CSS STYLING
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
# TOP NAVIGATIE
# =========================================================

if st.session_state.main_page not in ["🏠 Hoofdmenu", "⚽ Pronostiek", "🎯 Pronostiek scores"]:
    if st.button("☰ Hoofdmenu", use_container_width=True):
        go_to("🏠 Hoofdmenu")


# =========================================================
# PAGINA ROUTING
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

        if st.button("⚽ Winnaars voorspellen (1X2)", use_container_width=True):
            go_to("⚽ Pronostiek")

        if st.button("🎯 Exacte scores invullen", use_container_width=True, type="primary"):
            go_to("🎯 Pronostiek scores")

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
                go_to("🖨️ Stand uitprinten")

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


elif st.session_state.main_page == "⚽ Pronostiek":
    user = require_login()
    if user:
        show_pronostiek(
            user_id=str(user["naam"]),
            standings_df=load_standings(),
        )


elif st.session_state.main_page == "🎯 Pronostiek scores":
    user = require_login()
    if user:
        safe_user_id = str(user.get("naam", "Gast"))
        show_pronostiek_scores(user_id=safe_user_id)


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


elif st.session_state.main_page == "🖨️ Stand uitprinten":
    user = require_login()

    if user and bool(user.get("admin", False)):
        show_stand_uitprinten()
    else:
        st.error("Toegang geweigerd.")
