import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

USER_ID = "Tom"


# =========================================================
# HELPERS
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()

    if len(code) != 2:
        return "⚽"

    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


def format_date(value):
    txt = str(value or "").strip()

    parts = txt.split("-")

    # 11-06-26 -> 11/06
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"

    return txt


def format_time(value):
    txt = str(value or "").strip()

    # 21:00:00 -> 21:00
    if txt.count(":") >= 2:
        txt = ":".join(txt.split(":")[:2])

    return txt


def get_prediction(match_id):
    value = st.session_state.local_predictions.get(
        str(match_id),
        "X",
    )

    if isinstance(value, dict):
        value = value.get("prediction", "X")

    value = str(value).upper().strip()

    if value not in ["1", "X", "2"]:
        value = "X"

    return value


def save_all_predictions():

    predictions_to_save = {}

    for key, value in st.session_state.items():

        if not key.startswith("pred_"):
            continue

        match_id = key.replace("pred_", "")

        prediction = str(value).upper().strip()

        if prediction not in ["1", "X", "2"]:
            prediction = "X"

        predictions_to_save[match_id] = {
            "prediction": prediction,
            "score1": "",
            "score2": "",
        }

    if not predictions_to_save:
        return 0

    saved = batch_save_predictions(
        USER_ID,
        predictions_to_save,
        "concept",
    )

    st.cache_data.clear()

    return saved


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    max-width: 820px;
    padding-top: 0 !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
    padding-bottom: 5rem !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

/* =========================================================
TOP BAR
========================================================= */

.st-key-top_bar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;

    z-index: 999999 !important;

    background: #0e1117 !important;

    padding:
        0.45rem
        0.55rem
        0.55rem
        0.55rem !important;

    border-bottom:
        1px solid rgba(255,255,255,0.10);
}

.st-key-top_bar > div {
    max-width: 820px;
    margin-left: auto;
    margin-right: auto;
}

.top-spacer {
    height: 180px;
}

.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.38rem 0.6rem !important;
    font-size: 0.76rem !important;
    margin-bottom: 0.25rem !important;
    border-radius: 10px !important;
}

.st-key-top_bar button {
    min-height: 38px !important;
    height: 38px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
}

/* =========================================================
MENU
========================================================= */

.menu-buttons button {
    font-size: 0.78rem !important;
    padding: 0.15rem !important;
}

/* =========================================================
MATCH CARD
========================================================= */

[class*="st-key-match_card_"] {

    background: #111827;

    border:
        1px solid rgba(255,255,255,0.12);

    border-radius: 14px;

    padding:
        0.7rem
        0.7rem
        0.6rem
        0.7rem !important;

    margin-bottom: 0.55rem;
}

/* bovenste lijn */

.match-top {

    display: grid;

    grid-template-columns:
        64px
        1fr;

    gap: 0.65rem;

    align-items: center;
}

.match-date {

    text-align: center;

    font-size: 0.78rem;

    color: #cbd5e1;

    line-height: 1.15;
}

.match-status {
    color: #22c55e;
    font-size: 0.95rem;
    font-weight: 900;
}

.match-teams {

    font-size: 0.92rem;

    font-weight: 800;

    line-height: 1.32;

    min-width: 0;
}

.team-line {

    white-space: nowrap;

    overflow: hidden;

    text-overflow: ellipsis;
}

/* =========================================================
1 X 2
========================================================= */

[class*="st-key-match_card_"]
div[data-testid="stSegmentedControl"] {

    margin-top: 0.55rem !important;
}

[class*="st-key-match_card_"]
div[data-testid="stSegmentedControl"] button {

    min-width: 52px !important;

    height: 34px !important;

    padding: 0 !important;

    font-weight: 800 !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

footer {
    visibility: hidden;
}

/* =========================================================
MOBILE
========================================================= */

@media (max-width: 430px) {

    .top-spacer {
        height: 175px;
    }

    .block-container {
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
    }

    [class*="st-key-match_card_"] {

        padding:
            0.6rem
            0.6rem
            0.55rem
            0.6rem !important;
    }

    .match-top {

        grid-template-columns:
            58px
            1fr;

        gap: 0.5rem;
    }

    .match-date {
        font-size: 0.72rem;
    }

    .match-teams {
        font-size: 0.84rem;
    }

    [class*="st-key-match_card_"]
    div[data-testid="stSegmentedControl"] button {

        min-width: 46px !important;

        height: 31px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Wedstrijden"

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False


# =========================================================
# DATA
# =========================================================

@st.cache_data(ttl=60)
def get_data():
    return (
        load_matches(),
        load_predictions(USER_ID),
    )


matches_df, predictions_df = get_data()


# =========================================================
# LOAD EXISTING PREDICTIONS
# =========================================================

if not st.session_state.loaded_predictions:

    if not predictions_df.empty:

        for _, row in predictions_df.iterrows():

            match_id = str(
                row.get("match_id", "")
            ).strip()

            if not match_id:
                continue

            prediction = str(
                row.get("prediction", "X")
            ).upper().strip()

            if prediction not in ["1", "X", "2"]:
                prediction = "X"

            st.session_state.local_predictions[
                match_id
            ] = prediction

    st.session_state.loaded_predictions = True


# =========================================================
# TOP BAR
# =========================================================

with st.container(key="top_bar"):

    st.info(
        "Kies uitslagen en druk OPSLAAN.",
        icon="⚡",
    )

    if st.button(
        "💾 NU ALLES OPSLAAN",
        use_container_width=True,
        type="primary",
    ):

        saved = save_all_predictions()

        st.success(
            f"Opgeslagen: {saved} wedstrijden"
        )

    st.markdown(
        '<div class="menu-buttons">',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button(
            "⚽ Wedstr.",
            use_container_width=True,
        ):
            st.session_state.page = "Wedstrijden"
            st.rerun()

    with c2:
        if st.button(
            "📊 Stand",
            use_container_width=True,
        ):
            st.session_state.page = "Stand"
            st.rerun()

    with c3:
        if st.button(
            "🏆 KO",
            use_container_width=True,
        ):
            st.session_state.page = "KO"
            st.rerun()

    with c4:
        if st.button(
            "👤 Mijn",
            use_container_width=True,
        ):
            st.session_state.page = "Mijn"
            st.rerun()

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


st.markdown(
    '<div class="top-spacer"></div>',
    unsafe_allow_html=True,
)


# =========================================================
# WEDSTRIJDEN
# =========================================================

if st.session_state.page == "Wedstrijden":

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:

        st.warning("Geen wedstrijden gevonden.")

    else:

        if "match_id" in wedstrijden.columns:

            wedstrijden["match_id"] = (
                wedstrijden["match_id"]
                .astype(str)
                .str.strip()
            )

        if "ronde" in wedstrijden.columns:

            wedstrijden = wedstrijden[
                wedstrijden["ronde"]
                .astype(str)
                .str.lower()
                .str.contains("groep", na=False)
            ].copy()

        sort_cols = [
            c for c in [
                "datum",
                "tijd",
                "match_id",
            ]
            if c in wedstrijden.columns
        ]

        if sort_cols:

            wedstrijden = wedstrijden.sort_values(
                sort_cols,
                kind="stable",
            )

        for _, match in wedstrijden.iterrows():

            match_id = str(
                match.get("match_id", "")
            ).strip()

            if not match_id:
                continue

            datum = format_date(
                match.get("datum", "")
            )

            tijd = format_time(
                match.get("tijd", "")
            )

            team1 = str(
                match.get("team1", "")
            ).strip()

            team2 = str(
                match.get("team2", "")
            ).strip()

            team1_code = match.get(
                "team1_code",
                "",
            )

            team2_code = match.get(
                "team2_code",
                "",
            )

            pred_key = f"pred_{match_id}"

            if pred_key not in st.session_state:

                st.session_state[pred_key] = (
                    get_prediction(match_id)
                )

            with st.container(
                key=f"match_card_{match_id}"
            ):

                st.markdown(
                    f"""
<div class="match-top">

    <div class="match-date">
        <b>{datum}</b><br>
        {tijd}<br>
        <span class="match-status">●</span>
    </div>

    <div class="match-teams">

        <div class="team-line">
            {country_flag(team1_code)} {team1}
        </div>

        <div class="team-line">
            {country_flag(team2_code)} {team2}
        </div>

    </div>

</div>
                    """,
                    unsafe_allow_html=True,
                )

                st.segmented_control(
                    "Pronostiek",
                    ["1", "X", "2"],
                    key=pred_key,
                    default=st.session_state[pred_key],
                    label_visibility="collapsed",
                )


# =========================================================
# STAND
# =========================================================

elif st.session_state.page == "Stand":

    st.subheader("📊 Standen")
    st.write("Hier komen de groepsstanden.")


# =========================================================
# KO
# =========================================================

elif st.session_state.page == "KO":

    st.subheader("🏆 Knockout")
    st.write("Hier komt het knockoutschema.")


# =========================================================
# MIJN
# =========================================================

elif st.session_state.page == "Mijn":

    st.subheader("👤 Mijn pronostiek")

    rows = []

    for key, value in st.session_state.items():

        if not key.startswith("pred_"):
            continue

        rows.append({
            "match_id": key.replace(
                "pred_",
                "",
            ),
            "pronostiek": value,
        })

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "Nog geen voorspellingen gekozen."
        )