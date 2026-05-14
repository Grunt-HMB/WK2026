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
# CSS - Forceert 1 rij op mobiel
# =========================================================

st.markdown("""
<style>
/* Algemene Container */
.block-container {
    max-width: 720px;
    padding-top: 0 !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
    padding-bottom: 5rem !important;
}

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
    padding: 0.4rem 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.top-spacer {
    height: 180px;
}

/* Knoppen en Radio */
.st-key-top_bar button {
    height: 38px !important;
    border-radius: 8px !important;
}

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
}

.st-key-menu_keuze label {
    padding: 2px !important;
}

/* FORCEER HORIZONTALE KOLOMMEN OP MOBIEL */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: 0.3rem !important;
}

/* Match Card Styling */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.4rem 0.5rem !important;
    margin-bottom: 0.4rem;
}

/* Tekst grootte en witruimte */
[class*="st-key-match_card_"] p {
    font-size: 0.78rem !important;
    margin: 0 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

/* Maak Segmented Control compacter */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 32px !important;
    height: 28px !important;
    font-size: 0.7rem !important;
    padding: 0 !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2: return "⚽"
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

def normalize_time(value):
    txt = str(value or "").strip()
    return txt[:5] if ":" in txt else txt

def compact_date(value):
    txt = str(value or "").strip()
    parts = txt.split("-")
    return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else txt

def get_existing_prediction(match_id):
    data = st.session_state.local_predictions.get(str(match_id), "X")
    if isinstance(data, dict):
        return data.get("prediction", "X")
    return str(data).upper()

def prediction_changed(match_id):
    key = f"pred_{match_id}"
    st.session_state.local_predictions[str(match_id)] = {
        "prediction": st.session_state.get(key, "X"),
        "score1": "",
        "score2": "",
    }

# =========================================================
# DATA & SESSION
# =========================================================

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

@st.cache_data(ttl=60)
def get_data():
    return load_matches(), load_predictions(USER_ID)

matches_df, predictions_df = get_data()

if "loaded" not in st.session_state:
    for _, row in predictions_df.iterrows():
        mid = str(row.get("match_id", ""))
        if mid:
            st.session_state.local_predictions[mid] = {
                "prediction": str(row.get("prediction", "X")).upper(),
                "score1": row.get("score1", ""),
                "score2": row.get("score2", ""),
            }
    st.session_state.loaded = True

# =========================================================
# UI
# =========================================================

with st.container(key="top_bar"):
    st.info("Keuzes zijn lokaal bewaard.", icon="💾")
    if st.button("OPSLAAN", use_container_width=True, type="primary"):
        saved = batch_save_predictions(USER_ID, st.session_state.local_predictions, "concept")
        st.cache_data.clear()
        st.success("Opgeslagen!")

    st.radio("Menu", ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"], 
             key="menu_keuze", horizontal=True, label_visibility="collapsed")

st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

if st.session_state.menu_keuze == "⚽ Wedstr.":
    df = matches_df.copy()
    if "ronde" in df.columns:
        df = df[df["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
    
    for _, match in df.iterrows():
        mid = str(match.get("match_id", ""))
        t1 = f"{country_flag(match.get('team1_code'))} {match.get('team1')}"
        t2 = f"{country_flag(match.get('team2_code'))} {match.get('team2')}"
        
        key = f"pred_{mid}"
        if key not in st.session_state:
            st.session_state[key] = get_existing_prediction(mid)

        with st.container(key=f"match_card_{mid}"):
            # We gebruiken hier st.columns maar de CSS hierboven dwingt ze horizontaal
            c1, c2, c3 = st.columns([0.6, 1.8, 1.1], gap="small")
            
            with c1:
                st.markdown(f"**{compact_date(match.get('datum'))}**\n\n{normalize_time(match.get('tijd'))}")
            
            with c2:
                # Landen onder elkaar voor leesbaarheid binnen de rij
                st.markdown(f"{t1}\n\n{t2}")
            
            with c3:
                st.segmented_control(
                    "P", ["1", "X", "2"],
                    key=key,
                    label_visibility="collapsed",
                    on_change=prediction_changed,
                    args=(mid,)
                )

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("Mijn keuzes")
    st.json(st.session_state.local_predictions)