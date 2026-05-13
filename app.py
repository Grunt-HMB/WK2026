import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 0 !important;
    padding-left: 0.35rem !important;
    padding-right: 0.35rem !important;
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
    padding: 0.4rem 0.55rem 0.55rem 0.55rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 168px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.45rem 0.7rem !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.3rem !important;
}

.st-key-top_bar button {
    height: 40px !important;
    min-height: 40px !important;
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
    gap: 0.1rem 0.45rem !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    padding: 0.1rem 0.15rem !important;
    margin: 0 !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] span {
    font-size: 0.82rem !important;
    font-weight: 800 !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* =========================================================
DATA EDITOR
========================================================= */

div[data-testid="stDataFrame"] {
    font-size: 0.78rem !important;
}

div[data-testid="stDataFrame"] [role="gridcell"] {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
}

div[data-testid="stDataFrame"] [role="columnheader"] {
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
    font-size: 0.72rem !important;
}

/* selectbox in data editor compacter */
div[data-testid="stDataFrame"] input {
    font-size: 0.78rem !important;
}

/* Streamlit footer deels weg */
footer {
    visibility: hidden;
}

@media (max-width: 480px) {
    .top-spacer {
        height: 164px;
    }

    .block-container {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }

    .st-key-menu_keuze label[data-baseweb="radio"] span {
        font-size: 0.76rem !important;
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


def get_existing_prediction(match_id):
    match_id = str(match_id).strip()

    data = st.session_state.local_predictions.get(match_id, {})

    if isinstance(data, dict):
        value = data.get("prediction", "")
    else:
        value = data

    value = str(value).upper().strip()

    if value not in ["1", "X", "2"]:
        return "X"

    return value


def normalize_time(value):
    txt = str(value or "").strip()

    if txt.endswith(":00") and txt.count(":") == 2:
        txt = txt[: txt.rfind(":")]

    return txt


# =========================================================
# SESSION STATE
# =========================================================

if "menu_keuze" not in st.session_state:
    st.session_state.menu_keuze = "⚽ Wedstrijden"

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
# BESTAANDE PRONOSTIEKEN LADEN
# =========================================================

if not st.session_state.loaded_predictions:

    if not predictions_df.empty:

        for _, row in predictions_df.iterrows():

            match_id = str(row.get("match_id", "")).strip()

            if not match_id:
                continue

            st.session_state.local_predictions[match_id] = {
                "prediction": str(row.get("prediction", "")).upper().strip(),
                "score1": row.get("score1", ""),
                "score2": row.get("score2", ""),
            }

    st.session_state.loaded_predictions = True


# =========================================================
# VASTE TOPBALK
# =========================================================

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


# =========================================================
# PAGINA: WEDSTRIJDEN
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstrijden":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")

    else:

        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

        rows = []

        for _, match in wedstrijden.iterrows():

            match_id = str(match.get("match_id", "")).strip()

            if not match_id:
                continue

            datum = str(match.get("datum", "")).strip()
            tijd = normalize_time(match.get("tijd", ""))

            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()

            team1_code = str(match.get("team1_code", "")).strip()
            team2_code = str(match.get("team2_code", "")).strip()

            wedstrijd = (
                f"{country_flag(team1_code)} {team1} "
                f"vs "
                f"{country_flag(team2_code)} {team2}"
            )

            rows.append({
                "match_id": match_id,
                "Wanneer": f"{datum} {tijd}",
                "●": "🟢",
                "Wedstrijd": wedstrijd,
                "1/X/2": get_existing_prediction(match_id),
            })

        editor_df = pd.DataFrame(rows)

        edited_df = st.data_editor(
            editor_df,
            hide_index=True,
            use_container_width=True,
            height=620,
            disabled=[
                "match_id",
                "Wanneer",
                "●",
                "Wedstrijd",
            ],
            column_config={
                "match_id": None,

                "Wanneer": st.column_config.TextColumn(
                    "Wanneer",
                    width="small",
                ),

                "●": st.column_config.TextColumn(
                    "",
                    width="small",
                ),

                "Wedstrijd": st.column_config.TextColumn(
                    "Wedstrijd",
                    width="large",
                ),

                "1/X/2": st.column_config.SelectboxColumn(
                    "1/X/2",
                    options=["1", "X", "2"],
                    required=True,
                    width="small",
                ),
            },
            key="wedstrijden_editor",
        )

        for _, row in edited_df.iterrows():

            match_id = str(row["match_id"]).strip()
            prediction = str(row["1/X/2"]).upper().strip()

            if prediction not in ["1", "X", "2"]:
                prediction = "X"

            st.session_state.local_predictions[match_id] = {
                "prediction": prediction,
                "score1": "",
                "score2": "",
            }


# =========================================================
# PAGINA: STANDEN
# =========================================================

elif st.session_state.menu_keuze == "📊 Standen":

    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


# =========================================================
# PAGINA: KNOCKOUT
# =========================================================

elif st.session_state.menu_keuze == "🏆 Knockout":

    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


# =========================================================
# PAGINA: MIJN
# =========================================================

elif st.session_state.menu_keuze == "👤 Mijn":

    st.subheader("👤 Mijn pronostiek")

    if not st.session_state.local_predictions:
        st.info("Nog geen pronostieken gekozen.")
    else:

        mijn_rows = []

        for match_id, data in st.session_state.local_predictions.items():

            if isinstance(data, dict):
                prediction = data.get("prediction", "")
            else:
                prediction = data

            mijn_rows.append({
                "match_id": match_id,
                "pronostiek": prediction,
            })

        st.dataframe(
            pd.DataFrame(mijn_rows),
            use_container_width=True,
            hide_index=True,
        )