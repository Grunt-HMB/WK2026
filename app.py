import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

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
    padding-top: 0.4rem !important;
    padding-left: 0.55rem !important;
    padding-right: 0.55rem !important;
    padding-bottom: 4rem !important;
}

/* Sidebar verbergen op mobiel */
section[data-testid="stSidebar"] {
    display: none;
}

/* Sticky save-blok */
div[data-testid="stVerticalBlock"]:has(.save-anchor) {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: #0e1117;
    padding-bottom: 0.5rem;
}

/* Info kleiner */
div[data-testid="stAlert"] {
    padding: 0.55rem 0.8rem !important;
    font-size: 0.9rem !important;
}

/* Tabs compacter */
button[data-baseweb="tab"] {
    padding-left: 0.45rem !important;
    padding-right: 0.45rem !important;
    font-size: 0.95rem !important;
}

/* Wedstrijdkaart */
.match-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 15px;
    padding: 12px;
    margin-bottom: 12px;
}

/* Compacte match-grid */
.match-grid {
    display: grid;
    grid-template-columns: 72px 1fr auto;
    gap: 10px;
    align-items: center;
}

.match-date {
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.35;
}

.match-status {
    color: #22c55e;
    font-weight: 800;
    font-size: 0.85rem;
    margin-top: 3px;
}

.match-teams {
    min-width: 0;
}

.team {
    font-size: 1rem;
    font-weight: 800;
    line-height: 1.35;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.vs {
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 1px 0;
}

/* Radio compact rechts */
.compact-radio div[role="radiogroup"] {
    display: flex !important;
    gap: 5px !important;
    justify-content: flex-end !important;
}

.compact-radio label[data-baseweb="radio"] {
    background: #1f2937;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    min-width: 42px;
    height: 38px;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.compact-radio label[data-baseweb="radio"] span {
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}

.compact-radio label[data-baseweb="radio"] input {
    display: none;
}

/* Mobiel extra compact */
@media (max-width: 480px) {

    .match-card {
        padding: 10px;
    }

    .match-grid {
        grid-template-columns: 64px 1fr auto;
        gap: 7px;
    }

    .match-date {
        font-size: 0.82rem;
    }

    .team {
        font-size: 0.94rem;
    }

    .compact-radio label[data-baseweb="radio"] {
        min-width: 36px;
        height: 34px;
    }

    .compact-radio label[data-baseweb="radio"] span {
        font-size: 0.88rem !important;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w20/{code}.png" '
        f'style="width:20px;height:14px;object-fit:cover;'
        f'border-radius:2px;margin-right:5px;vertical-align:-2px;">'
    )


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
    key = f"pred_{match_id}"
    value = st.session_state.get(key, "X")

    st.session_state.local_predictions[str(match_id)] = {
        "prediction": value,
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
# STICKY SAVE BLOK
# =========================================================

with st.container():
    st.markdown('<span class="save-anchor"></span>', unsafe_allow_html=True)

    st.info(
        "Wijzigingen blijven lokaal staan. Klik op OPSLAAN om alles tegelijk te bewaren.",
        icon="💾",
    )

    if st.button("OPSLAAN", use_container_width=True, type="primary"):
        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        get_predictions_cached.clear()
        st.success(f"Pronostiek opgeslagen ({saved} wedstrijden).")


# =========================================================
# TOP NAVIGATION
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

    if "match_id" in wedstrijden.columns:
        wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

    for _, match in wedstrijden.iterrows():

        match_id = str(match.get("match_id", "")).strip()

        if not match_id:
            continue

        datum = str(match.get("datum", ""))
        tijd = str(match.get("tijd", ""))
        team1 = str(match.get("team1", ""))
        team2 = str(match.get("team2", ""))
        team1_code = str(match.get("team1_code", ""))
        team2_code = str(match.get("team2_code", ""))

        current_value = get_prediction_value(match_id)

        radio_key = f"pred_{match_id}"

        if radio_key not in st.session_state:
            st.session_state[radio_key] = current_value

        st.markdown('<div class="match-card">', unsafe_allow_html=True)

        col_info, col_radio = st.columns([1, 0.45], vertical_alignment="center")

        with col_info:

            st.markdown(f"""
            <div class="match-grid">
                <div class="match-date">
                    <b>{datum}</b><br>
                    {tijd}<br>
                    <div class="match-status">🟢 Open</div>
                </div>

                <div class="match-teams">
                    <div class="team">{flag_img(team1_code)}{team1}</div>
                    <div class="vs">tegen</div>
                    <div class="team">{flag_img(team2_code)}{team2}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_radio:

            st.markdown('<div class="compact-radio">', unsafe_allow_html=True)

            st.radio(
                "Pronostiek",
                ["1", "X", "2"],
                key=radio_key,
                horizontal=True,
                label_visibility="collapsed",
                on_change=prediction_changed,
                args=(match_id,),
            )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


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
# MIJN PRONOSTIEK
# =========================================================

with tab_mijn:
    st.subheader("👤 Mijn pronostiek")
    st.write(st.session_state.local_predictions)
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