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
# CSS - Definitieve Fix voor Menu en Tekst-breedte
# =========================================================

st.markdown("""
<style>
.block-container {
    max-width: 720px;
    padding: 0 0.3rem 5rem 0.3rem !important;
}

section[data-testid="stSidebar"] { display: none; }

/* Top Bar Styling */
.st-key-top_bar {
    position: fixed !important;
    top: 0; left: 0; right: 0;
    z-index: 999999 !important;
    background: #0e1117 !important;
    padding: 0.5rem 0.5rem 0.6rem 0.5rem !important;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}

.top-spacer { height: 185px; }

/* Menu (Radio) Fix - Zorg dat tekst ALTIJD zichtbaar is */
.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
    background: #1f2937 !important;
    border-radius: 10px;
    padding: 4px;
    margin-top: 8px;
}

.st-key-menu_keuze label {
    flex: 1;
    text-align: center;
    background: transparent !important;
    border: none !important;
    padding: 6px 2px !important;
}

.st-key-menu_keuze label div:first-child { display: none !important; }

/* Actieve tab kleur */
.st-key-menu_keuze label[data-checked="true"] {
    background: #3b82f6 !important;
    border-radius: 8px !important;
}

/* Forceer witte tekst voor alle menu items */
.st-key-menu_keuze label span {
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    text-shadow: 0px 0px 2px black;
}

/* Match Card Layout */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.4rem !important;
    margin-bottom: 0.3rem;
}

.match-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Datum iets breder maken tegen afkappen */
.match-date {
    min-width: 55px; 
    font-size: 0.72rem;
    color: #9ca3af;
    line-height: 1.2;
    text-align: left;
}

.match-teams {
    font-size: 0.8rem;
    font-weight: 600;
    line-height: 1.3;
    overflow: hidden;
}

/* Segmented Control compact houden */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 32px !important;
    height: 28px !important;
    font-size: 0.72rem !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS & DATA
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

    st.radio(
        "Menu", 
        ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"], 
        key="menu_keuze", 
        horizontal=True, 
        label_visibility="collapsed"
    )

st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

# =========================================================
# WEDSTRIJDEN LIJST
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstr.":
    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden.")
    else:
        df = matches_df.copy()
        for _, match in df.iterrows():
            mid = str(match.get("match_id", "")).strip()
            if not mid: continue
            
            key = f"pred_{mid}"
            db_val = st.session_state.local_predictions.get(mid, "X")
            safe_default = db_val if db_val in ["1", "X", "2"] else "X"

            with st.container(key=f"match_card_{mid}"):
                # Kolom verhouding: 0.8 voor datum/info, 1.0 voor de knoppen
                col_info, col_pred = st.columns([1.8, 1.0], gap="small")
                
                with col_info:
                    datum_raw = str(match.get('datum', ''))
                    # Fix voor datum weergave (DD/MM)
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
                        "P", 
                        options=["1", "X", "2"],
                        key=key,
                        default=safe_default,
                        label_visibility="collapsed"
                    )

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("Mijn Keuzes")
    huidige_lijst = [{"Match": k.replace("pred_", ""), "Voorspelling": v} 
                     for k, v in st.session_state.items() if k.startswith("pred_")]
    if huidige_lijst:
        st.table(pd.DataFrame(huidige_lijst))
    else:
        st.info("Nog geen keuzes gemaakt.")