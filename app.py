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
# CSS - De definitieve "One-Row" Fix
# =========================================================

st.markdown("""
<style>
.block-container {
    max-width: 720px;
    padding: 0 0.3rem 5rem 0.3rem !important;
}

section[data-testid="stSidebar"] { display: none; }

/* Top Bar */
.st-key-top_bar {
    position: fixed !important;
    top: 0; left: 0; right: 0;
    z-index: 999999;
    background: #0e1117;
    padding: 0.3rem 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.top-spacer { height: 175px; }

/* Menu Styling */
.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
}

.st-key-menu_keuze label {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
}

.st-key-menu_keuze label div:first-child { display: none !important; }

/* Match Card Container */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.5rem !important;
    margin-bottom: 0.3rem;
}

/* Flexbox Row voor de wedstrijd */
.match-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    gap: 5px;
}

.match-date {
    min-width: 45px;
    font-size: 0.7rem;
    color: #9ca3af;
    line-height: 1.2;
}

.match-teams {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.team-line {
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Segmented control klein houden */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
    min-width: 100px;
}

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
    return data.get("prediction", "X") if isinstance(data, dict) else str(data).upper()

def prediction_changed(match_id):
    key = f"pred_{match_id}"
    st.session_state.local_predictions[str(match_id)] = {
        "prediction": st.session_state.get(key, "X"),
        "score1": "", "score2": "",
    }

# =========================================================
# DATA
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
                "score1": row.get("score1", ""), "score2": row.get("score2", ""),
            }
    st.session_state.loaded = True

# =========================================================
# UI
# =========================================================

with st.container(key="top_bar"):
    st.info("Lokaal bewaard. Klik op OPSLAAN.", icon="💾")
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
        key = f"pred_{mid}"
        if key not in st.session_state:
            st.session_state[key] = get_existing_prediction(mid)

        # We gebruiken een combinatie van HTML (voor de rij-flow) en Streamlit (voor de knoppen)
        with st.container(key=f"match_card_{mid}"):
            # We maken 2 kolommen: Links de info (HTML), Rechts de knoppen (Streamlit)
            # Dit is de enige manier om overlap te voorkomen op mobiel
            col_info, col_pred = st.columns([2.2, 1.0], gap="small")
            
            with col_info:
                st.markdown(f"""
                <div class="match-row">
                    <div class="match-date">
                        <b>{compact_date(match.get('datum'))}</b><br>{normalize_time(match.get('tijd'))}
                    </div>
                    <div class="match-teams">
                        <div class="team-line">{country_flag(match.get('team1_code'))} {match.get('team1')}</div>
                        <div class="team-line">{country_flag(match.get('team2_code'))} {match.get('team2')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_pred:
                st.segmented_control(
                    "P", ["1", "X", "2"],
                    key=key,
                    label_visibility="collapsed",
                    on_change=prediction_changed,
                    args=(mid,)
                )

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("Mijn Keuzes")
    st.write(st.session_state.local_predictions)