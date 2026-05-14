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
# CSS - Fix voor Menu, Layout en Snelheid
# =========================================================

st.markdown("""
<style>
.block-container {
    max-width: 720px;
    padding: 0 0.35rem 5rem 0.35rem !important;
}

section[data-testid="stSidebar"] { display: none; }

/* Top Bar: Altijd zichtbaar en dekkend */
.st-key-top_bar {
    position: fixed !important;
    top: 0; left: 0; right: 0;
    z-index: 999999 !important;
    background: #0e1117 !important;
    padding: 0.5rem 0.5rem 0.8rem 0.5rem !important;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}

.top-spacer { height: 185px; }

/* Menu Knoppen: Duidelijk actieve tab */
.st-key-menu_keuze div[role="radiogroup"] {
    display: flex !important;
    justify-content: space-between !important;
    background: #1f2937 !important;
    border-radius: 12px;
    padding: 4px;
    margin-top: 5px;
}

.st-key-menu_keuze label {
    flex: 1;
    text-align: center;
    background: transparent !important;
    border: none !important;
    padding: 6px 2px !important;
    margin: 0 !important;
}

.st-key-menu_keuze label div:first-child { display: none !important; }

.st-key-menu_keuze label[data-checked="true"] {
    background: #3b82f6 !important;
    border-radius: 8px !important;
}

.st-key-menu_keuze label span {
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
}

/* Match Card: Compacte rij-layout */
[class*="st-key-match_card_"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.45rem !important;
    margin-bottom: 0.35rem;
}

.match-row-wrapper {
    display: flex;
    align-items: center;
    width: 100%;
}

.match-info {
    display: flex;
    align-items: center;
    flex-grow: 1;
    gap: 10px;
}

.match-date {
    min-width: 42px;
    font-size: 0.7rem;
    color: #9ca3af;
    line-height: 1.1;
    text-align: center;
}

.match-teams {
    font-size: 0.82rem;
    font-weight: 600;
    line-height: 1.4;
    white-space: nowrap;
}

/* Knoppen compacter voor mobiel */
[class*="st-key-match_card_"] div[data-testid="stSegmentedControl"] button {
    min-width: 32px !important;
    height: 30px !important;
    font-size: 0.75rem !important;
    padding: 0 !important;
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

# Eenmalig inladen
if "loaded" not in st.session_state:
    for _, row in predictions_df.iterrows():
        mid = str(row.get("match_id", "")).strip()
        if mid:
            st.session_state.local_predictions[mid] = str(row.get("prediction", "X")).upper().strip()
    st.session_state.loaded = True

def save_all_predictions():
    """Verzamelt alle widgets-waarden en slaat ze in één keer op."""
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
# TOP BAR
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
# PAGINA: WEDSTRIJDEN
# =========================================================

if st.session_state.menu_keuze == "⚽ Wedstr.":
    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden.")
    else:
        df = matches_df.copy()
        # Sorteer op datum en tijd indien aanwezig
        sort_cols = [c for c in ["datum", "tijd"] if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols)

        for _, match in df.iterrows():
            mid = str(match.get("match_id", "")).strip()
            if not mid: continue
            
            key = f"pred_{mid}"
            
            # Veilig de default waarde bepalen om StreamlitAPIException te voorkomen
            db_val = st.session_state.local_predictions.get(mid, "X")
            safe_default = db_val if db_val in ["1", "X", "2"] else "X"

            with st.container(key=f"match_card_{mid}"):
                # Gebruik kolommen voor de rij-indeling
                col_info, col_pred = st.columns([1.9, 1.0], gap="small")
                
                with col_info:
                    datum_str = str(match.get('datum', ''))
                    datum = datum_str[5:].replace('-', '/') if len(datum_str) > 5 else datum_str
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
                    # Geen on_change voor maximale snelheid
                    st.segmented_control(
                        "P", 
                        options=["1", "X", "2"],
                        key=key,
                        default=safe_default,
                        label_visibility="collapsed"
                    )

# =========================================================
# OVERIGE PAGINA'S
# =========================================================

elif st.session_state.menu_keuze == "👤 Mijn":
    st.subheader("Mijn Keuzes (niet vergeten op te slaan!)")
    huidige_lijst = []
    for k, v in st.session_state.items():
        if k.startswith("pred_"):
            huidige_lijst.append({"Match": k.replace("pred_", ""), "Voorspelling": v})
    
    if huidige_lijst:
        st.table(pd.DataFrame(huidige_lijst))
    else:
        st.info("Nog geen keuzes gemaakt op deze pagina.")

else:
    st.info(f"De pagina '{st.session_state.menu_keuze}' is nog in opbouw.")