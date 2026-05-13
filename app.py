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
    max-width: 760px;
    padding-top: 0 !important;
    padding-left: 0.25rem !important;
    padding-right: 0.25rem !important;
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
    padding: 0.28rem 0.45rem 0.35rem 0.45rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
}

.st-key-top_bar > div {
    max-width: 760px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 145px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.32rem 0.5rem !important;
    font-size: 0.72rem !important;
    margin-bottom: 0.2rem !important;
    border-radius: 10px !important;
}

.st-key-top_bar button {
    height: 36px !important;
    min-height: 36px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
}

/* =========================================================
MENU
========================================================= */

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: space-between !important;
    gap: 0.1rem !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    border: none !important;
    padding: 0.05rem 0.08rem !important;
    margin: 0 !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] span {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
}

/* =========================================================
WEDSTRIJD CARD
========================================================= */

[class*="st-key-match_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 13px;
    padding: 0.45rem 0.5rem;
    margin-bottom: 0.45rem;
}

/* Streamlit columns geforceerd naast elkaar */
[class*="st-key-match_"] div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.35rem !important;
}

/* Datumkolom */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
    flex: 0 0 58px !important;
    width: 58px !important;
    min-width: 58px !important;
}

/* Teams */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(2) {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
}

/* 1/X/2 */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
    flex: 0 0 116px !important;
    width: 116px !important;
    min-width: 116px !important;
}

[class*="st-key-match_"] p {
    margin-bottom: 0 !important;
    line-height: 1.22 !important;
}

/* Datum tekst */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) p {
    font-size: 0.68rem !important;
}

/* Team tekst */
[class*="st-key-match_"] div[data-testid="column"]:nth-of-type(2) p {
    font-size: 0.78rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Segmented control */
[class*="st-key-match_"] div[data-testid="stSegmentedControl"] {
    margin: 0 !important;
}

[class*="st-key-match_"] div[data-testid="stSegmentedControl"] button {
    min-width: 30px !important;
    height: 29px !important;
    padding: 0 !important;
    font-size: 0.74rem !important;
    font-weight: 800 !important;
}

/* Algemene spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.32rem !important;
}

footer {
    visibility: hidden;
}

@media (max-width: 430px) {

    .block-container {
        padding-left: 0.15rem !important;
        padding-right: 0.15rem !important;
    }

    .top-spacer {
        height: 142px;
    }

    [class*="st-key-match_"] {
        padding: 0.4rem 0.42rem;
    }

    [class*="st-key-match_"] div[data-testid="stHorizontalBlock"] {
        gap: 0.28rem !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) {
        flex-basis: 54px !important;
        width: 54px !important;
        min-width: 54px !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(3) {
        flex-basis: 108px !important;
        width: 108px !important;
        min-width: 108px !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(1) p {
        font-size: 0.64rem !important;
    }

    [class*="st-key-match_"] div[data-testid="column"]:nth-of-type(2) p {
        font-size: 0.74rem !important;
    }

    [class*="st-key-match_"] div[data-testid="stSegmentedControl"] button {
        min-width: 27px !important;
        height: 27px !important;
        font-size: 0.68rem !important;
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


def normalize_time(value):
    txt = str(value or "").strip()

    if txt.endswith(":00") and txt.count(":") == 2:
        txt = txt[: txt.rfind(":")]

    return txt


def compact_date(value):
    txt = str(value or "").strip()
    parts = txt.split("-")

    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"

    return txt


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


def prediction_changed(match_id):
    match_id = str(match_id).strip()
    key = f"pred_{match_id}"

    prediction = st.session_state.get(key, "X")

    if prediction not in ["1", "X", "2"]:
        prediction = "X"

    st.session_state.local_predictions[match_id] = {
        "prediction": prediction,
        "score1": "",
        "score2": "",
    }


# =========================================================
# SESSION STATE
# =========================================================

if "menu_keuze" not in st.session_state:
    st.session_state.menu_keuze = "⚽ Wedstr."

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
# TOPBALK
# =========================================================

with st.container(key="top_bar"):

    st.info(
        "Lokaal bewaard. Druk OPSLAAN.",
        icon="💾",
    )

    if st.button("OPSLAAN", use_container_width=True, type="primary"):

        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        get_predictions_cached.clear()

        st.success(f"Opgeslagen: {saved}")

    st.radio(
        "Menu",
        [
            "⚽ Wedstr.",
            "📊 Stand",
            "🏆 KO",
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

if st.session_state.menu_keuze == "⚽ Wedstr.":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")

    else:

        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

        if "ronde" in wedstrijden.columns:
            wedstrijden = wedstrijden[
                wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)
            ].copy()

        sort_cols = []

        for col in ["datum", "tijd", "match_id"]:
            if col in wedstrijden.columns:
                sort_cols.append(col)

        if sort_cols:
            wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

        for _, match in wedstrijden.iterrows():

            match_id = str(match.get("match_id", "")).strip()

            if not match_id:
                continue

            datum = compact_date(match.get("datum", ""))
            tijd = normalize_time(match.get("tijd", ""))

            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()

            team1_code = str(match.get("team1_code", "")).strip()
            team2_code = str(match.get("team2_code", "")).strip()

            key = f"pred_{match_id}"

            if key not in st.session_state:
                st.session_state[key] = get_existing_prediction(match_id)

            with st.container(key=f"match_{match_id}"):

                col_date, col_teams, col_choice = st.columns(
                    [0.55, 2.25, 1.05],
                    vertical_alignment="center",
                )

                with col_date:
                    st.markdown(
                        f"""
                        **{datum}**  
                        {tijd}  
                        🟢
                        """
                    )

                with col_teams:
                    st.markdown(
                        f"""
                        **{country_flag(team1_code)} {team1}**  
                        tegen  
                        **{country_flag(team2_code)} {team2}**
                        """
                    )

                with col_choice:
                    st.segmented_control(
                        "Pronostiek",
                        ["1", "X", "2"],
                        key=key,
                        label_visibility="collapsed",
                        on_change=prediction_changed,
                        args=(match_id,),
                    )


# =========================================================
# PAGINA: STANDEN
# =========================================================

elif st.session_state.menu_keuze == "📊 Stand":

    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


# =========================================================
# PAGINA: KNOCKOUT
# =========================================================

elif st.session_state.menu_keuze == "🏆 KO":

    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


# =========================================================
# PAGINA: MIJN
# =========================================================

elif st.session_state.menu_keuze == "👤 Mijn":

    st.subheader("👤 Mijn pronostiek")

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

    if not mijn_rows:
        st.info("Nog geen pronostieken gekozen.")
    else:
        st.dataframe(
            pd.DataFrame(mijn_rows),
            use_container_width=True,
            hide_index=True,
        )