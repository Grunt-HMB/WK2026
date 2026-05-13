import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="WK 2026",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* =========================================================
ALGEMEEN
========================================================= */

.block-container {
    max-width: 900px;
    padding-top: 0.5rem !important;
    padding-left: 0.7rem !important;
    padding-right: 0.7rem !important;
    padding-bottom: 4rem !important;
}

section[data-testid="stSidebar"] {
    display: none;
}

/* =========================================================
HEADER
========================================================= */

.main-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
}

.save-bar {
    position: sticky;
    top: 0;
    z-index: 999;

    background: #0e1117;

    padding-top: 0.4rem;
    padding-bottom: 0.6rem;

    margin-bottom: 1rem;
}

/* =========================================================
CARD
========================================================= */

.match-card {
    background: #111827;

    border-radius: 16px;

    padding: 14px;

    margin-bottom: 12px;

    border: 1px solid rgba(255,255,255,0.06);
}

.match-header {
    font-size: 0.82rem;
    color: #cbd5e1;

    margin-bottom: 10px;

    line-height: 1.4;
}

.team-name {
    font-size: 1rem;
    font-weight: 700;

    margin-bottom: 6px;
}

/* =========================================================
RADIO
========================================================= */

div[role="radiogroup"] {
    display: flex !important;
    justify-content: center;
    gap: 0.5rem;
}

label[data-baseweb="radio"] {
    background: #1f2937;

    border-radius: 10px;

    padding: 0.25rem 0.6rem;

    min-width: 48px;

    justify-content: center;

    border: 1px solid rgba(255,255,255,0.08);
}

label[data-baseweb="radio"] span {
    font-weight: 700 !important;
}

/* radio bolletje weg */
label[data-baseweb="radio"] input {
    display: none;
}

/* =========================================================
MOBIEL
========================================================= */

@media (max-width: 768px) {

    .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    .main-title {
        font-size: 1.45rem;
    }

    .match-card {
        padding: 12px;
        border-radius: 14px;
    }

    .team-name {
        font-size: 0.96rem;
    }

    label[data-baseweb="radio"] {
        min-width: 44px;
        padding: 0.2rem 0.4rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded_predictions" not in st.session_state:
    st.session_state.loaded_predictions = False


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data(ttl=60)
def get_matches_cached():
    return load_matches()


@st.cache_data(ttl=60)
def get_predictions_cached(user_id):
    return load_predictions(user_id)


matches_df = get_matches_cached()

USER_ID = "Tom"

predictions_df = get_predictions_cached(USER_ID)


# =========================================================
# LOAD EXISTING PREDICTIONS
# =========================================================

if not st.session_state.loaded_predictions:

    if not predictions_df.empty:

        for _, row in predictions_df.iterrows():

            st.session_state.local_predictions[
                str(row["match_id"])
            ] = row["prediction"]

    st.session_state.loaded_predictions = True


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">⚽ WK 2026 Pronostiek</div>',
    unsafe_allow_html=True
)


# =========================================================
# SAVE BAR
# =========================================================

st.markdown('<div class="save-bar">', unsafe_allow_html=True)

save_col1, save_col2 = st.columns([3, 1])

with save_col1:
    st.info(
        "Wijzigingen worden lokaal bijgehouden. Klik op OPSLAAN om alles tegelijk te bewaren.",
        icon="💾"
    )

with save_col2:

    if st.button(
        "OPSLAAN",
        use_container_width=True,
        type="primary"
    ):

        batch_save_predictions(
            USER_ID,
            st.session_state.local_predictions
        )

        get_predictions_cached.clear()

        st.success("Pronostiek opgeslagen")

st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TOP NAVIGATION
# =========================================================

wedstrijd_tab, standen_tab, knockout_tab, profiel_tab = st.tabs([
    "⚽ Wedstrijden",
    "📊 Standen",
    "🏆 Knockout",
    "👤 Mijn"
])


# =========================================================
# WEDSTRIJDEN
# =========================================================

with wedstrijd_tab:

    wedstrijden = matches_df.copy()

    for _, match in wedstrijden.iterrows():

        match_id = str(match["match_id"])

        st.markdown(
            '<div class="match-card">',
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="match-header">
            {match['datum']}<br>
            {match['tijd']}<br>
            🟢 Open
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="team-name">🇧🇪 {match["team1"]}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="team-name">🇧🇷 {match["team2"]}</div>',
            unsafe_allow_html=True
        )

        current_value = st.session_state.local_predictions.get(
            match_id,
            "X"
        )

        with st.form(f"form_{match_id}"):

            prediction = st.radio(
                "",
                ["1", "X", "2"],
                horizontal=True,
                index=["1", "X", "2"].index(current_value),
                key=f"radio_{match_id}",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "Bevestig",
                use_container_width=True
            )

            if submitted:

                st.session_state.local_predictions[
                    match_id
                ] = prediction

                st.toast(
                    f"Voorspelling opgeslagen: {prediction}",
                    icon="⚽"
                )

        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# STANDEN
# =========================================================

with standen_tab:

    st.subheader("📊 Standen")

    st.write("Hier komen de groepsstanden")


# =========================================================
# KNOCKOUT
# =========================================================

with knockout_tab:

    st.subheader("🏆 Knockout")

    st.write("Hier komt het knockoutschema")


# =========================================================
# PROFIEL
# =========================================================

with profiel_tab:

    st.subheader("👤 Mijn pronostiek")

    st.write(st.session_state.local_predictions)