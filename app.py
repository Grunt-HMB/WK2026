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
# CSS - Fix voor Menu Zichtbaarheid & Snelheid
# =========================================================

st.markdown("""
<style>
.block-container {
    max-width: 720px;
    padding: 0 0.3rem 5rem 0.3rem !important;
}

section[data-testid="stSidebar"] { display: none; }

/* FIX: Menu & Top Bar zichtbaarheid */
.st-key-top_bar {
    position: fixed !important;
    top: 0; left: 0; right: 0;
    z-index: 999999;
    background: #0e1117 !important; /* Forceer donkere achtergrond */
    padding: 0.5rem 0.5rem 0.8rem 0.5rem !important;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}

.top-spacer { height: 190px; }

/* Menu Knoppen Styling */
.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
    background: #1f2937;
    border-radius: 12px;
    padding: 4px;
}

.st-key-menu_keuze label {
    flex: 1;
    text-align: center;
    background: transparent !important;
    border: none !important;
    padding: 6px 2px !important;
    margin: 0 !important;
}

/* Verberg cirkels en selectie-indicator */
.st-key-menu_keuze label div:first-child { display: none !important; }
.st-key-menu_keuze label[data-checked="true"] {
    background: #3b82f6 !important; /* Blauwe kleur voor actieve tab */
    border-radius: 8px !important;
}

/* Match Card */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.5rem !important;
    margin-bottom: 0.3rem;
}

.match-info-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.match-date {
    min-width: 42px;
    font-size: 0.7rem;
    color: #9ca3af;
    line-height: 1.1;
}

.match-teams {
    flex-grow: 1;
    font-size: 0.82rem;
    font-weight: 600;
    line-height: 1.3;
}

/* Knoppen compacter */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 34px !important;
    height: 30px !important;
    font-size: 0.75rem !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA & SESSION
# =========================================================

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

@st.cache_data(ttl=60)
def get_data():
    return load_matches(), load_predictions(USER_ID)

matches_df, predictions_df = get_data()

# Eenmalig laden van database naar session state
if "loaded" not in st.session_state:
    for _, row in predictions_df.iterrows():
        mid = str(row.get("match_id", ""))
        if mid:
            st.session_state.local_predictions[mid] = str(row.get("prediction", "X")).upper()
    st.session_state.loaded = True

# =========================================================
# HELPERS
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2: return "⚽"
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

def save_all():
    """Batch save functie die alles in één keer wegschrijft"""
    # Verzamel alle huidige session_state keuzes
    to_save = {}
    for key, val in st.session_state.items():
        if key.startswith("pred_") and val:
            mid = key.replace("pred_", "")
            to_save[mid] = {"prediction": val, "score1": "", "score2": ""}
    
    if to_save:
        saved_count = batch_save_predictions(USER_ID, to_save, "concept")
        st.cache_data.clear()
        return saved_count
    return 0

# =========================================================
# UI - TOP BAR
# =========================================================

with st.container(key="top_bar"):
    st.info("Kies je uitslagen en klik op OPSLAAN.", icon="⚡")
    
    if st.button("💾 NU ALLES OPSLAAN", use_container_width=True, type="primary"):
        count = save_all()
        st.success(f"Gelukt! {count} wedstrijden opgeslagen.")

    st.radio("Menu", ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"], 
             key="menu_keuze", horizontal=True, label_visibility="collapsed")

st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

# =========================================================
# WEDSTRIJDEN LIJST
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstr.":
    df = matches_df.copy()
    
    for _, match in df.iterrows():
        mid = str(match.get("match_id", ""))
        key = f"pred_{mid}"
        
        # Snelheidstip: Gebruik 'value' zonder 'on_change' voor directe respons
        default_val = st.session_state.local_predictions.get(mid, "X")
        
        with st.container(key=f"match_card_{mid}"):
            col_info, col_pred = st.columns([1.8, 1.0], gap="small")
            
            with col_info:
                datum = str(match.get('datum', ''))[5:] if match.get('datum') else ""
                tijd = str(match.get('tijd', ''))[:5]
                t1 = f"{country_flag(match.get('team1_code'))} {match.get('team1')}"
                t2 = f"{country_flag(match.get('team2_code'))} {match.get('team2')}"
                
                st.markdown(f"""
                <div class="match-info-container">
                    <div class="match-date"><b>{datum}</b><br>{tijd}</div>
                    <div class="match-teams">{t1}<br>{t2}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_pred:
                # Door on_change weg te laten is de UI veel vlotter
                st.segmented_control(
                    "P", ["1", "X", "2"],
                    key=key,
                    default=default_val,
                    label_visibility="collapsed"
                )

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("Mijn Voorlopige Keuzes")
    # Toon wat er momenteel in de widgets staat
    huidige_keuzes = {k.replace("pred_", ""): v for k, v in st.session_state.items() if k.startswith("pred_")}
    st.write(huidige_keuzes)