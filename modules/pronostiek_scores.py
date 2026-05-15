import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR EEN SCHONE MOBIELE LOOK ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    .match-box {
        background: #1a202c;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
        border: 1px solid #2d3748;
    }

    .team-name {
        font-size: 1rem;
        font-weight: bold;
        color: white;
        margin-bottom: 4px;
    }
    
    /* Zorg dat de selectboxen compact zijn */
    div[data-testid="stSelectbox"] > div {
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- DATA INITIALISATIE ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
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

    # Speeldag Slider (werkt altijd goed op mobiel)
    sd = st.select_slider("Speeldag", options=["1", "2", "3"], value="1")
    
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]
    score_options = list(range(11)) # Scores van 0 t/m 10

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        with st.container():
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.7rem; color:#718096;'>{m['datum']} • {m['tijd']}</div>", unsafe_allow_html=True)
            
            # Team 1 uitslag
            st.markdown(f'<div class="team-name">{country_flag(m["team1_code"])} {m["team1"]}</div>', unsafe_allow_html=True)
            s1 = st.selectbox(
                f"Score {m['team1']}", 
                options=score_options, 
                index=score_options.index(data['score1']),
                key=f"s1_{m_id}",
                label_visibility="collapsed"
            )

            # Team 2 uitslag
            st.markdown(f'<div class="team-name">{country_flag(m["team2_code"])} {m["team2"]}</div>', unsafe_allow_html=True)
            s2 = st.selectbox(
                f"Score {m['team2']}", 
                options=score_options, 
                index=score_options.index(data['score2']),
                key=f"s2_{m_id}",
                label_visibility="collapsed"
            )

            # Logica
            if s1 > s2: res = "1"
            elif s1 < s2: res = "2"
            else: res = "X"
            
            st.session_state.score_predictions[m_id] = {"prediction": res, "score1": s1, "score2": s2}
            
            color = "#48bb78" if res != "X" else "#ecc94b"
            st.markdown(f"<div style='text-align:right; font-weight:bold; color:{color};'>Gok: {res}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
