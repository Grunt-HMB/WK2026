import streamlit as st
from modules.database import load_predictions, batch_save_predictions
# Hier importeren we jouw nieuwe module
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR MOBIELE STABILITEIT ---
    # We gebruiken grote knoppen en duidelijke inputs zodat 'dikke vingers' geen probleem zijn
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Vastgezette bovenbalk zodat Opslaan altijd bereikbaar is */
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    /* De popover-knop die de wedstrijd representeert */
    div[data-testid="stPopover"] > button {
        height: 65px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background-color: #1a202c !important;
    }
    
    /* Meta-info (datum/tijd) styling */
    .match-meta {
        font-size: 0.75rem;
        color: #718096;
        margin-top: 10px;
        margin-left: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- INITIALISATIE DATA ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    # Eenmalig laden uit de database per sessie
    load_flag = f"loaded_scores_{user_id}"
    if load_flag not in st.session_state:
        try:
            db_preds = load_predictions(user_id)
            if not db_preds.empty:
                for _, row in db_preds.iterrows():
                    st.session_state.score_predictions[str(row['match_id'])] = {
                        "prediction": row['prediction'], 
                        "score1": int(row['score1']), 
                        "score2": int(row['score2'])
                    }
            st.session_state[load_flag] = True
        except Exception as e:
            st.error(f"Fout bij laden: {e}")

    # --- TOP BAR (FIXED) ---
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
                batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.toast("✅ Pronostiek opgeslagen!", icon="⚽")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # --- SPEELDAG SELECTIE ---
    # Een slider werkt op mobiel vaak fijner dan kleine radio-rondjes
    sd = st.select_slider(
        "Kies Speeldag", 
        options=["1", "2", "3"], 
        value="1",
        help="Schuif om de wedstrijden van een andere speeldag te zien"
    )
    
    st.divider()

    # --- WEDSTRIJD LIJST ---
    current_matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    if not current_matches:
        st.warning(f"Geen wedstrijden gevonden voor speeldag {sd}")

    for m in current_matches:
        m_id = str(m["match_id"])
        
        # Default waarden als er nog niets in de state staat
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]
        
        # Toon datum en tijd boven de knop
        st.markdown(f"<div class='match-meta'>{m['datum']} • {m['tijd']} • Groep {m['groep']}</div>", unsafe_allow_html=True)
        
        # De "Knop" is een Popover: dit voorkomt dat kolommen verspringen op mobiel
        label = f"{country_flag(m['team1_code'])} {data['score1']} — {data['score2']} {country_flag(m['team2_code'])}"
        
        with st.popover(label, use_container_width=True):
            st.markdown(f"### {m['team1']} vs {m['team2']}")
            
            # Input voor Team 1
            new_s1 = st.number_input(
                f"Score {m['team1']}", 
                min_value=0, max_value=50, 
                value=int(data['score1']), 
                key=f"in1_{m_id}",
                step=1
            )
            
            # Input voor Team 2
            new_s2 = st.number_input(
                f"Score {m['team2']}", 
                min_value=0, max_value=50, 
                value=int(data['score2']), 
                key=f"in2_{m_id}",
                step=1
            )
            
            # Logica voor 1-X-2 (wordt direct berekend)
            if new_s1 > new_s2: res = "1"
            elif new_s1 < new_s2: res = "2"
            else: res = "X"
            
            # Sla wijzigingen direct op in de session_state
            st.session_state.score_predictions[m_id] = {
                "prediction": res,
                "score1": new_s1,
                "score2": new_s2
            }
            
            st.info(f"Gok: **{res}**")

    st.markdown("<br><br>", unsafe_allow_html=True)
