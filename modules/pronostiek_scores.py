import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR MOOIE KAARTJES & MOBIEL ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    /* Stijl voor het wedstrijd-kaartje */
    .match-card {
        background: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .match-header {
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 10px;
        color: #ffffff;
        text-align: center;
    }

    .match-info {
        font-size: 0.75rem;
        color: #a0aec0;
        text-align: center;
        margin-bottom: 15px;
    }

    /* Maak de number input labels onzichtbaar maar behoud de ruimte */
    label[data-testid="stWidgetLabel"] {
        font-weight: 600 !important;
        color: #cbd5e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- INITIALISATIE ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    load_flag = f"loaded_scores_{user_id}"
    if load_flag not in st.session_state:
        try:
            db_preds = load_predictions(user_id)
            for _, row in db_preds.iterrows():
                st.session_state.score_predictions[str(row['match_id'])] = {
                    "prediction": row['prediction'], 
                    "score1": int(row['score1']), 
                    "score2": int(row['score2'])
                }
            st.session_state[load_flag] = True
        except: pass

    # --- TOP BAR ---
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
                batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.toast("✅ Pronostiek opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # --- SPEELDAG ---
    sd = st.select_slider("Kies Speeldag", options=["1", "2", "3"], value="1")
    
    # --- WEDSTRIJDEN ---
    current_matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in current_matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        # Start van het kaartje
        st.markdown(f"""
        <div class="match-card">
            <div class="match-info">{m['datum']} • {m['tijd']} • Groep {m['groep']}</div>
            <div class="match-header">
                {country_flag(m['team1_code'])} {m['team1']} vs {m['team2']} {country_flag(m['team2_code'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Invoer velden direct onder de namen
        # We gebruiken 2 kolommen voor de scores, die blijven op mobiel meestal wel naast elkaar
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            new_s1 = st.number_input(
                f"Score {m['team1']}", 
                min_value=0, max_value=20, 
                value=int(data['score1']), 
                key=f"in1_{m_id}"
            )
        
        with col_s2:
            new_s2 = st.number_input(
                f"Score {m['team2']}", 
                min_value=0, max_value=20, 
                value=int(data['score2']), 
                key=f"in2_{m_id}"
            )

        # Berekening
        if new_s1 > new_s2: res = "1"
        elif new_s1 < new_s2: res = "2"
        else: res = "X"
        
        st.session_state.score_predictions[m_id] = {
            "prediction": res, "score1": new_s1, "score2": new_s2
        }

        # Toon gok onder de inputs
        color = "#48bb78" if res != "X" else "#ecc94b"
        st.markdown(f"<p style='text-align:center; color:{color}; font-weight:bold;'>Gok: {res}</p>", unsafe_allow_html=True)
        st.markdown("---")

    st.markdown("<br><br>", unsafe_allow_html=True)
