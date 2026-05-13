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


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    max-width: 900px;
    padding-top: 0.25rem !important;
    padding-left: 0.35rem !important;
    padding-right: 0.35rem !important;
    padding-bottom: 5rem !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

/* =========================================================
OPSLAAN VAST BOVENAAN
========================================================= */

.st-key-sticky_save {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;

    background: #0e1117 !important;
    padding: 0.35rem 0.55rem 0.55rem 0.55rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

/* Breedte van de vaste balk beperken */
.st-key-sticky_save > div {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

/* Ruimte maken onder vaste opslaanbalk */
.save-spacer {
    height: 118px;
}

/* Info compacter */
.st-key-sticky_save div[data-testid="stAlert"] {
    padding: 0.45rem 0.7rem !important;
    font-size: 0.84rem !important;
    margin-bottom: 0.35rem !important;
}

/* Opslaan knop */
.st-key-sticky_save button {
    height: 42px !important;
    min-height: 42px !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
}

/* =========================================================
TABS
========================================================= */

button[data-baseweb="tab"] {
    padding-left: 0.35rem !important;
    padding-right: 0.35rem !important;
    font-size: 0.9rem !important;
}

div[data-baseweb="tab-list"] {
    gap: 0 !important;
}

/* =========================================================
MATCH CARD
========================================================= */

[class*="st-key-match_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 13px;
    padding: 0.45rem 0.5rem;
    margin-bottom: 0.45rem;
}

/* Streamlit columns NIET laten stapelen op mobiel */
[class*="st-key-match_"] div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.35rem !important;
}

/* Kolom 1: datum */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
    flex: 0 0 62px !important;
    width: 62px !important;
    min-width: 62px !important;
}

/* Kolom 2: teams */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(2) {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
}

/* Kolom 3: radio */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
    flex: 0 0 128px !important;
    width: 128px !important;
    min-width: 128px !important;
}

/* Tekst compacter */
[class*="st-key-match_"] p {
    margin-bottom: 0 !important;
    line-height: 1.25 !important;
}

.match-date {
    font-size: 0.74rem;
    color: #d1d5db;
}

.match-teams {
    font-size: 0.82rem;
    line-height: 1.22;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.match-vs {
    font-size: 0.62rem;
    color: #94a3b8;
}

/* =========================================================
RADIO 1 X 2
========================================================= */

[class*="st-key-match_"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: flex-end !important;
    gap: 0.25rem !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] {
    background: #1f2937;
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 9px;
    min-width: 34px !important;
    width: 34px !important;
    height: 31px !important;
    padding: 0 !important;
    margin: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] span {
    font-size: 0.78rem !important;
    font-weight: 800 !important;
}

[class*="st-key-match_"] label[data-baseweb="radio"] > div:first-child {
    margin-right: 0.12rem !important;
}

/* Minder algemene witruimte */
div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

@media (max-width: 420px) {
    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
        flex-basis: 56px !important;
        width: 56px !important;
        min-width: 56px !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
        flex-basis: 118px !important;
        width: 118px !important;
        min-width: 118px !important;
    }

    .match-date {
        font-size: 0.7rem;
    }

    .match-teams {
        font-size: 0.78rem;
    }

    [class*="st-key-match_"] label[data-baseweb="radio"] {
        min-width: 31px !important;
        width: 31px !important;
        height: 29px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

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


# =========================================================
# SESSION STATE
# =========================================================

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False


# =========================================================
# DATA
# =========================================================

@st.cache_data(ttl=60)
def get_matches_cached():
    return load_matches()


@st.cache_data(ttl=60)
def get_predictions_cached(user_id):
    return load_predictions(user_id)


matches_df = get_matches_cached()
predictions_df = get_predictions_cached(USER_ID)


# =========================================================
# BESTAANDE VOORSPELLINGEN LADEN
# =========================================================

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


# =========================================================
# VASTE OPSLAANBALK
# =========================================================

with st.container(key="sticky_save"):

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


st.markdown('<div class="save-spacer"></div>', unsafe_allow_html=True)


# =========================================================
# TABS
# =========================================================

tab_wedstrijden, tab_standen, tab_knockout, tab_mijn = st.tabs([
    "⚽ Wedstrijden",
    "📊 Standen",
    "🏆 Knockout",
    "👤 Mijn",
])


# =========================================================
# WEDSTRIJDEN
# =========================================================

with tab_wedstrijden:

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
                    [0.7, 1.55, 1.05],
                    vertical_alignment="center",
                )

                with col_date:
                    st.markdown(
                        f"""
                        <div class="match-date">
                            <b>{datum}</b><br>
                            {tijd}<br>
                            🟢 <b>Open</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_teams:
                    st.markdown(
                        f"""
                        <div class="match-teams">
                            <b>{country_flag(team1_code)} {team1}</b><br>
                            <span class="match-vs">tegen</span><br>
                            <b>{country_flag(team2_code)} {team2}</b>
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


# =========================================================
# STANDEN
# =========================================================

with tab_standen:
    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


# =========================================================
# KNOCKOUT
# =========================================================

with tab_knockout:
    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


# =========================================================
# MIJN
# =========================================================

with tab_mijn:
    st.subheader("👤 Mijn pronostiek")

    if not st.session_state.local_predictions:
        st.info("Nog geen pronostieken gekozen.")
    else:
        st.write(st.session_state.local_predictions)