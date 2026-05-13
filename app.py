import streamlit as st

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"


st.markdown("""
<style>

.block-container {
    max-width: 900px;
    padding-top: 0 !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
    padding-bottom: 5rem !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

/* =========================================================
VASTE TOPBALK
========================================================= */

.st-key-top_bar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;
    background: #0e1117 !important;
    padding: 0.35rem 0.5rem 0.45rem 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 188px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.45rem 0.7rem !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.25rem !important;
}

.st-key-top_bar button {
    height: 39px !important;
    min-height: 39px !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
}

/* =========================================================
MENU
========================================================= */

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 0.15rem 0.45rem !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    padding: 0.15rem 0.2rem !important;
    margin: 0 !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] span {
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

/* =========================================================
MATCH CARD
========================================================= */

[class*="st-key-match_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 13px;
    padding: 0.45rem;
    margin-bottom: 0.42rem;
}

/* Forceer Streamlit columns naast elkaar */
[class*="st-key-match_"] div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.3rem !important;
}

/* Datumkolom */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
    flex: 0 0 58px !important;
    width: 58px !important;
    min-width: 58px !important;
}

/* Teamskolom */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(2) {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
}

/* Pronostiekkolom */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
    flex: 0 0 104px !important;
    width: 104px !important;
    min-width: 104px !important;
}

.match-date {
    font-size: 0.68rem;
    line-height: 1.18;
    color: #d1d5db;
}

.match-status {
    color: #22c55e;
    font-weight: 800;
}

.match-teams {
    font-size: 0.78rem;
    line-height: 1.18;
    min-width: 0;
    overflow: hidden;
}

.match-team {
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.match-vs {
    font-size: 0.56rem;
    color: #94a3b8;
}

/* =========================================================
RADIO 1/X/2
========================================================= */

[class*="st-key-match_"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: flex-end !important;
    gap: 0.18rem !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] {
    background: #1f2937;
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 8px;
    min-width: 30px !important;
    width: 30px !important;
    height: 28px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] span {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] > div:first-child {
    margin-right: 0.06rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.32rem !important;
}

@media (max-width: 420px) {

    .top-spacer {
        height: 184px;
    }

    [class*="st-key-match_"] {
        padding: 0.38rem;
    }

    [class*="st-key-match_"] div[data-testid="stHorizontalBlock"] {
        gap: 0.25rem !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
        flex-basis: 54px !important;
        width: 54px !important;
        min-width: 54px !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
        flex-basis: 96px !important;
        width: 96px !important;
        min-width: 96px !important;
    }

    .match-date {
        font-size: 0.64rem;
    }

    .match-teams {
        font-size: 0.73rem;
    }

    .match-vs {
        font-size: 0.52rem;
    }

    [class*="st-key-match_"] label[data-baseweb="radio"] {
        min-width: 27px !important;
        width: 27px !important;
        height: 26px !important;
    }

    [class*="st-key-match_"] label[data-baseweb="radio"] span {
        font-size: 0.68rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


def country_flag(code):
    code = str(code or "").strip().upper()

    if len(code) != 2:
        return ""

    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


def get_prediction_value(match_id):
    data = st.session_state.local_predictions.get(str(match_id), {})

    if isinstance(data, dict):
        value = data.get("prediction", "")
    else:
        value = data

    value = str(value).upper().strip()

    if value not in ["1", "X", "2"]:
        return "X"

    return value


def prediction_changed(match_id):
    match_id = str(match_id).strip()
    key = f"pred_{match_id}"

    st.session_state.local_predictions[match_id] = {
        "prediction": st.session_state.get(key, "X"),
        "score1": "",
        "score2": "",
    }


if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False

if "menu_keuze" not in st.session_state:
    st.session_state.menu_keuze = "⚽ Wedstrijden"


@st.cache_data(ttl=60)
def get_matches_cached():
    return load_matches()


@st.cache_data(ttl=60)
def get_predictions_cached(user_id):
    return load_predictions(user_id)


matches_df = get_matches_cached()
predictions_df = get_predictions_cached(USER_ID)


if not st.session_state.loaded_predictions:

    if not predictions_df.empty:

        for _, row in predictions_df.iterrows():

            match_id = str(row.get("match_id", "")).strip()

            if match_id:
                st.session_state.local_predictions[match_id] = {
                    "prediction": str(row.get("prediction", "")).upper().strip(),
                    "score1": row.get("score1", ""),
                    "score2": row.get("score2", ""),
                }

    st.session_state.loaded_predictions = True


with st.container(key="top_bar"):

    st.info(
        "Wijzigingen blijven lokaal. Klik op OPSLAAN om alles te bewaren.",
        icon="💾",
    )

    if st.button("OPSLAAN", use_container_width=True, type="primary"):
        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        get_predictions_cached.clear()

        st.success(f"Opgeslagen: {saved} wedstrijden.")

    st.radio(
        "Menu",
        [
            "⚽ Wedstrijden",
            "📊 Standen",
            "🏆 Knockout",
            "👤 Mijn",
        ],
        key="menu_keuze",
        horizontal=True,
        label_visibility="collapsed",
    )


st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)


if st.session_state.menu_keuze == "⚽ Wedstrijden":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")

    else:

        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

        for _, match in wedstrijden.iterrows():

            match_id = str(match.get("match_id", "")).strip()

            if not match_id:
                continue

            datum = str(match.get("datum", "")).strip()
            tijd = str(match.get("tijd", "")).strip()

            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()

            team1_code = str(match.get("team1_code", "")).strip()
            team2_code = str(match.get("team2_code", "")).strip()

            radio_key = f"pred_{match_id}"

            if radio_key not in st.session_state:
                st.session_state[radio_key] = get_prediction_value(match_id)

            with st.container(key=f"match_{match_id}"):

                col_date, col_teams, col_pred = st.columns(
                    [0.55, 1.75, 0.85],
                    vertical_alignment="center",
                )

                with col_date:
                    st.markdown(
                        f"""
                        <div class="match-date">
                            <b>{datum}</b><br>
                            {tijd}<br>
                            <span class="match-status">🟢 Open</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_teams:
                    st.markdown(
                        f"""
                        <div class="match-teams">
                            <div class="match-team">{country_flag(team1_code)} {team1}</div>
                            <div class="match-vs">tegen</div>
                            <div class="match-team">{country_flag(team2_code)} {team2}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_pred:
                    st.radio(
                        "Pronostiek",
                        ["1", "X", "2"],
                        key=radio_key,
                        horizontal=True,
                        label_visibility="collapsed",
                        on_change=prediction_changed,
                        args=(match_id,),
                    )


elif st.session_state.menu_keuze == "📊 Standen":

    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


elif st.session_state.menu_keuze == "🏆 Knockout":

    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


elif st.session_state.menu_keuze == "👤 Mijn":

    st.subheader("👤 Mijn pronostiek")

    if not st.session_state.local_predictions:
        st.info("Nog geen pronostieken gekozen.")
    else:
        st.write(st.session_state.local_predictions)