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
# CSS - Geoptimaliseerd voor Mobiel en Desktop
# =========================================================

st.markdown("""
<style>
/* Container settings */
.block-container {
    max-width: 720px;
    padding-top: 0 !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    padding-bottom: 5rem !important;
}

/* Verberg sidebar */
section[data-testid="stSidebar"] {
    display: none;
}

/* Vaste Top Bar */
.st-key-top_bar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999999 !important;
    background: #0e1117 !important;
    padding: 0.5rem 0.5rem 0.5rem 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    display: flex;
    justify-content: center;
}

.st-key-top_bar > div {
    width: 100%;
    max-width: 720px;
}

/* Spacer om content onder de vaste balk te krijgen */
.top-spacer {
    height: 185px;
}

/* Alert styling */
.st-key-top_bar div[data-testid="stAlert"] {
    padding: 0.4rem 0.6rem !important;
    font-size: 0.8rem !important;
    margin-bottom: 0.4rem !important;
    border-radius: 10px !important;
}

/* Button styling */
.st-key-top_bar button {
    height: 42px !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}

/* Radio menu styling */
.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    gap: 0px !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    padding: 5px !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* Match Cards */
[class*="st-key-match_card_"] {
    background: #1f2937;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 15px;
    padding: 0.8rem !important;
    margin-bottom: 0.6rem;
}

/* Voorkom overlap in tekst */
[class*="st-key-match_card_"] p {
    margin-bottom: 0.2rem !important;
    line-height: 1.4 !important;
    font-size: 0.95rem !important;
}

/* Segmented control centering */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
    display: flex;
    justify-content: center;
    margin-top: 0.8rem !important;
}

[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    flex-grow: 1;
    font-weight: 800 !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2:
        return "🏳️"
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
    data = st.session_state.local_predictions.get(str(match_id), {})
    if isinstance(data, dict):
        value = data.get("prediction", "X")
    else:
        value = data
    value = str(value).upper().strip()
    return value if value in ["1", "X", "2"] else "X"

def prediction_changed(match_id):
    key = f"pred_{match_id}"
    prediction = st.session_state.get(key, "X")
    st.session_state.local_predictions[str(match_id)] = {
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
# LOAD EXISTING PREDICTIONS
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
# TOP BAR
# =========================================================

with st.container(key="top_bar"):
    st.info("Lokaal bewaard. Vergeet niet op te slaan!", icon="💾")
    
    if st.button("OPSLAAN", use_container_width=True, type="primary"):
        saved = batch_save_predictions(
            user_id=USER_ID,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )
        get_predictions_cached.clear()
        st.success(f"Success! {saved} voorspellingen opgeslagen.")

    st.radio(
        "Menu",
        ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"],
        key="menu_keuze",
        horizontal=True,
        label_visibility="collapsed",
    )

# Padding to prevent overlap with fixed header
st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)


# =========================================================
# WEDSTRIJDEN
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstr.":
    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
    else:
        # Filter op groepsfase (optioneel)
        if "ronde" in wedstrijden.columns:
            wedstrijden = wedstrijden[
                wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)
            ].copy()

        # Sorteren
        sort_cols = [c for c in ["datum", "tijd", "match_id"] if c in wedstrijden.columns]
        if sort_cols:
            wedstrijden = wedstrijden.sort_values(sort_cols, kind="stable")

        for _, match in wedstrijden.iterrows():
            match_id = str(match.get("match_id", "")).strip()
            if not match_id: continue

            datum = compact_date(match.get("datum", ""))
            tijd = normalize_time(match.get("tijd", ""))
            team1 = str(match.get("team1", "")).strip()
            team2 = str(match.get("team2", "")).strip()
            t1_code = str(match.get("team1_code", "")).strip()
            t2_code = str(match.get("team2_code", "")).strip()

            key = f"pred_{match_id}"
            if key not in st.session_state:
                st.session_state[key] = get_existing_prediction(match_id)

            # Kaartje zonder kolommen voor betere mobiele flow
            with st.container(key=f"match_card_{match_id}"):
                st.markdown(f"**{datum}** • {tijd} 🟢")
                st.markdown(f"**{country_flag(t1_code)} {team1}**")
                st.markdown(f"**{country_flag(t2_code)} {team2}**")

                st.segmented_control(
                    "Pronostiek",
                    ["1", "X", "2"],
                    key=key,
                    label_visibility="collapsed",
                    on_change=prediction_changed,
                    args=(match_id,),
                )

# =========================================================
# ANDERE PAGINA'S (STUBS)
# =========================================================
elif st.session_state.menu_keuze == "📊 Stand":
    st.subheader("📊 Groepsstanden")
    st.info("Live standen worden tijdens het toernooi bijgewerkt.")

elif st.session_state.menu_keuze == "🏆 KO":
    st.subheader("🏆 Knock-out Fase")
    st.info("Het schema wordt zichtbaar na de groepsfase.")

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("👤 Mijn Pronostieken")
    mijn_rows = [{"Match ID": k, "Keuze": (v.get("prediction") if isinstance(v, dict) else v)} 
                 for k, v in st.session_state.local_predictions.items()]
    
    if not mijn_rows:
        st.info("Je hebt nog geen voorspellingen gedaan.")
    else:
        st.table(pd.DataFrame(mijn_rows))