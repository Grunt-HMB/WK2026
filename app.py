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
# CSS - Landscape optimalisatie & Menu Zichtbaarheid Fix
# =========================================================

st.markdown("""
<style>
/* Container optimalisatie voor Landscape */
.block-container {
    max-width: 800px;
    padding: 0 0.5rem 5rem 0.5rem !important;
}

section[data-testid="stSidebar"] { display: none; }

/* Top Bar: Fixed bovenin */
.st-key-top_bar {
    position: fixed !important;
    top: 0; left: 0; right: 0;
    z-index: 999999 !important;
    background: #0e1117 !important;
    padding: 0.5rem !important;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}

.top-spacer { height: 180px; }

/* MENU FIX: Gedwongen zichtbaarheid */
.st-key-menu_keuze {
    margin-top: 10px !important;
}

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: space-around !important;
    background: #1f2937 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 5px !important;
}

/* De labels (knoppen) zelf */
.st-key-menu_keuze label {
    flex: 1 !important;
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
    padding: 8px 2px !important;
    cursor: pointer !important;
}

/* Verberg de radio-cirkel die Streamlit er soms tussen propt */
.st-key-menu_keuze label div[data-testid="stMarkdownContainer"] {
    display: block !important;
}
.st-key-menu_keuze label div:first-child { 
    display: none !important; 
}

/* Tekst styling in het menu */
.st-key-menu_keuze label p {
    color: #ffffff !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-align: center !important;
}

/* Actieve tab kleur */
.st-key-menu_keuze label[data-checked="true"] {
    background: #3b82f6 !important;
}

/* Match Cards - Landscape vriendelijk */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.6rem !important;
    margin-bottom: 0.5rem;
}

.match-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.match-info {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-grow: 1;
}

.match-date {
    min-width: 60px;
    font-size: 0.75rem;
    color: #9ca3af;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,0.1);
    padding-right: 10px;
}

.match-teams {
    font-size: 0.9rem;
    font-weight: 600;
}

/* Knoppen iets groter voor Landscape/Vingers */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 45px !important;
    height: 35px !important;
    font-size: 0.85rem !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS & DATA (ongewijzigd maar essentieel)
# =========================================================

def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2: return "⚽"
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

@st.cache_data(ttl=60)
def get_data():
    return load_matches(), load_predictions(USER_ID)

matches_df, predictions_df = get_data()

if "local_predictions" not in st.session_state:
    st.session_state.local_predictions = {}

if "loaded" not in st.session_state:
    for _, row in predictions_df.iterrows():
        mid = str(row.get("match_id", "")).strip()
        if mid:
            st.session_state.local_predictions[mid] = str(row.get("prediction", "X")).upper().strip()
    st.session_state.loaded = True

def save_all_predictions():
    to_save = {}
    for key, val in st.session_state.items():
        if key.startswith("pred_") and val:
            mid = key.replace("pred_", "")
            to_save[mid] = {"prediction": val, "score1": "", "score2": ""}
    if to_save:
        count = batch_save_predictions(USER_ID, to_save, "concept")
        st.cache_data.clear()
        return count
    return 0

# =========================================================
# UI - TOP BAR
# =========================================================

with st.container(key="top_bar"):
    st.info("Kies je uitslagen. Klik dan op OPSLAAN.", icon="⚡")
    
    if st.button("💾 NU ALLES OPSLAAN", use_container_width=True, type="primary"):
        num = save_all_predictions()
        st.success(f"Opgeslagen: {num} wedstrijden!")

    # Menu met expliciete labels voor betere rendering
    st.radio(
        "Menu", 
        ["Wedstr.", "Stand", "K.O.", "Mijn"], 
        key="menu_keuze", 
        horizontal=True, 
        label_visibility="collapsed"
    )

st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

# =========================================================
# WEDSTRIJDEN LIJST
# =========================================================

if st.session_state.menu_keuze == "Wedstr.":
    df = matches_df.copy()
    for _, match in df.iterrows():
        mid = str(match.get("match_id", "")).strip()
        if not mid: continue
        
        key = f"pred_{mid}"
        db_val = st.session_state.local_predictions.get(mid, "X")
        safe_default = db_val if db_val in ["1", "X", "2"] else "X"

        with st.container(key=f"match_card_{mid}"):
            # Info links, Knoppen rechts
            col_info, col_pred = st.columns([2.5, 1.0], gap="small")
            
            with col_info:
                datum_raw = str(match.get('datum', ''))
                datum = datum_raw[5:].replace('-', '/') if len(datum_raw) > 5 else datum_raw
                tijd = str(match.get('tijd', ''))[:5]
                t1 = f"{country_flag(match.get('team1_code'))} {match.get('team1')}"
                t2 = f"{country_flag(match.get('team2_code'))} {match.get('team2')}"
                
                st.markdown(f"""
                <div class="match-info">
                    <div class="match-date"><b>{datum}</b><br>{tijd}</div>
                    <div class="match-teams">{t1}<br>{t2}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_pred:
                st.segmented_control(
                    "P", ["1", "X", "2"],
                    key=key,
                    default=safe_default,
                    label_visibility="collapsed"
                )

elif st.session_state.menu_keuze == "Mijn":
    st.subheader("Overzicht")
    huidige_lijst = [{"Match": k.replace("pred_", ""), "Uitslag": v} 
                     for k, v in st.session_state.items() if k.startswith("pred_")]
    st.table(pd.DataFrame(huidige_lijst))