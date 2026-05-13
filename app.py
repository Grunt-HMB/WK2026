import streamlit as st

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

USER_ID = "Tom"


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
    padding-top: 0.4rem !important;
    padding-left: 0.55rem !important;
    padding-right: 0.55rem !important;
    padding-bottom: 5rem !important;
}

/* Sidebar weg */
section[data-testid="stSidebar"] {
    display: none;
}

/* Streamlit default spacing compacter */
div[data-testid="stVerticalBlock"] {
    gap: 0.55rem !important;
}

/* =========================================================
STICKY OPSLAAN
========================================================= */

.sticky-save {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: #0e1117;
    padding-top: 0.4rem;
    padding-bottom: 0.7rem;
    margin-bottom: 0.6rem;
}

/* Info melding compacter */
div[data-testid="stAlert"] {
    padding: 0.65rem 0.85rem !important;
    font-size: 0.9rem !important;
    border-radius: 12px !important;
}

/* Opslaan knop */
.stButton > button[kind="primary"] {
    min-height: 44px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    border-radius: 12px !important;
}

/* =========================================================
TABS
========================================================= */

button[data-baseweb="tab"] {
    padding-left: 0.45rem !important;
    padding-right: 0.45rem !important;
    font-size: 0.95rem !important;
}

div[data-baseweb="tab-list"] {
    gap: 0.1rem !important;
}

/* =========================================================
WEDSTRIJD CARD
========================================================= */

.match-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 10px;
}

/* Binnenlayout */
.match-grid {
    display: grid;
    grid-template-columns: 66px 1fr;
    gap: 8px;
    align-items: center;
}

.match-date {
    color: #cbd5e1;
    font-size: 0.82rem;
    line-height: 1.35;
}

.match-status {
    color: #22c55e;
    font-weight: 800;
    font-size: 0.82rem;
    margin-top: 2px;
}

.match-teams {
    min-width: 0;
}

.team {
    font-size: 0.96rem;
    font-weight: 800;
    line-height: 1.32;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.vs {
    font-size: 0.68rem;
    color: #94a3b8;
    margin: 0;
}

/* =========================================================
RADIO 1/X/2
========================================================= */

.compact-radio div[role="radiogroup"] {
    display: flex !important;
    gap: 5px !important;
    justify-content: flex-end !important;
    flex-wrap: nowrap !important;
}

.compact-radio label[data-baseweb="radio"] {
    background: #1f2937;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 10px;
    min-width: 36px;
    height: 34px;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.compact-radio label[data-baseweb="radio"] span {
    font-weight: 800 !important;
    font-size: 0.88rem !important;
}

/* Radio bolletje verbergen */
.compact-radio label[data-baseweb="radio"] input {
    display: none;
}

/* Labelruimte weg */
.compact-radio > div {
    margin: 0 !important;
}

/* =========================================================
MOBIEL
========================================================= */

@media (max-width: 480px) {

    .block-container {
        padding-left: 0.45rem !important;
        padding-right: 0.45rem !important;
    }

    .match-card {
        padding: 9px;
        border-radius: 14px;
    }

    .match-grid {
        grid-template-columns: 60px 1fr;
        gap: 7px;
    }

    .match-date {
        font-size: 0.78rem;
    }

    .match-status {
        font-size: 0.78rem;
    }

    .team {
        font-size: 0.9rem;
    }

    .vs {
        font-size: 0.64rem;
    }

    .compact-radio label[data-baseweb="radio"] {
        min-width: 34px;
        height: 32px;
    }

    .compact-radio label[data-baseweb="radio"] span {
        font-size: 0.84rem !important;
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
    radio_key = f"pred_{match_id}"

    value = st.session_state.get(radio_key, "X")

    st.session_state.local_predictions[match_id] = {
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
# STICKY OPSLAAN
# =========================================================

st.markdown('<div class="sticky-save">', unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)


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
# TAB: WEDSTRIJDEN
# =========================================================

with tab_wedstrijden:

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
    else:

        if "match_id" in wedstrijden.columns:
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

            current_value = get_prediction_value(match_id)
            radio_key = f"pred_{match_id}"

            if radio_key not in st.session_state:
                st.session_state[radio_key] = current_value

            st.markdown('<div class="match-card">', unsafe_allow_html=True)

            col_info, col_radio = st.columns(
                [1.45, 0.55],
                vertical_alignment="center",
            )

            with col_info:

                html = f"""
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
                """

                st.markdown(html, unsafe_allow_html=True)

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
# TAB: STANDEN
# =========================================================

with tab_standen:

    st.subheader("📊 Standen")

    st.write("Hier komen de groepsstanden.")


# =========================================================
# TAB: KNOCKOUT
# =========================================================

with tab_knockout:

    st.subheader("🏆 Knockout")

    st.write("Hier komt het knockoutschema.")


# =========================================================
# TAB: MIJN
# =========================================================

with tab_mijn:

    st.subheader("👤 Mijn pronostiek")

    if not st.session_state.local_predictions:
        st.info("Nog geen pronostieken gekozen.")
    else:
        st.write(st.session_state.local_predictions)