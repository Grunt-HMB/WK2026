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
# CSS - Geoptimaliseerd voor 1 Rij Layout
# =========================================================

st.markdown("""
<style>
/* Algemene Container */
.block-container {
    max-width: 720px;
    padding-top: 0 !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
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

.st-key-top_bar > div {
    max-width: 720px;
    margin: 0 auto;
}

.top-spacer {
    height: 180px;
}

/* Knoppen en Radio */
.st-key-top_bar button {
    height: 38px !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] {
    background: transparent !important;
    padding: 2px !important;
}

.st-key-menu_keuze label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

.st-key-menu_keuze span {
    font-size: 0.8rem !important;
}

/* Match Card - Compacte 1-Rij Layout */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.5rem 0.6rem !important;
    margin-bottom: 0.4rem;
}

/* Verklein tekst voor mobiel om op 1 rij te passen */
[class*="st-key-match_card_"] p {
    font-size: 0.82rem !important;
    margin: 0 !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Segmented Control (1 X 2) smaller maken */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] {
    gap: 2px !important;
}

[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 35px !important;
    height: 30px !important;
    padding: 0 !important;
    font-size: 0.75rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.2rem !important;
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
    if len(code) != 2: return "🏳️"
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
        val = data.get("prediction", "X")
    else:
        val = data
    return str(val).upper()

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
        st.success(f"Opgeslagen!")

    st.radio("M", ["⚽ Wedstr.", "📊 Stand", "🏆 KO", "👤 Mijn"], key="menu_keuze", horizontal=True, label_visibility="collapsed")

st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

if st.session_state.menu_keuze == "⚽ Wedstr.":
    if matches_df.empty:
        st.warning("Geen data.")
    else:
        # Filteren en sorteren
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
                # Hier gebeurt de '1 rij' magie:
                # Kolom 1: Datum/Tijd (smal)
                # Kolom 2: Wedstrijd teams (breed)
                # Kolom 3: 1X2 keuze (compact)
                c1, c2, c3 = st.columns([0.5, 1.8, 0.9], vertical_alignment="center")
                
                with c1:
                    st.markdown(f"**{compact_date(match.get('datum'))}**\n\n{normalize_time(match.get('tijd'))}")
                
                with c2:
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
    st.write(st.session_state.local_predictions)