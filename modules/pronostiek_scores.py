import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR PROPERE SLIDERS ---
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
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #2d3748;
    }

    .team-label {
        font-size: 1rem;
        font-weight: bold;
        color: white;
        margin-top: 10px;
    }

    /* Maak de slider labels iets subtieler */
    div[data-testid="stWidgetLabel"] p {
        font-size: 0.8rem !important;
        color: #a0aec0 !important;
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
                st.toast("✅ Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # Speeldag selectie
    sd = st.select_slider("Kies Speeldag", options=["1", "2", "3"], value="1")
    
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]
    score_range = list(range(11)) # 0 t/m 10

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        with st.container():
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.7rem; color:#718096; text-align:center;'>{m['datum']} • {m['tijd']}</div>", unsafe_allow_html=True)
            
            # Slider Team 1
            s1 = st.select_slider(
                f"{country_flag(m['team1_code'])} {m['team1']}",
                options=score_range,
                value=data['score1'],
                key=f"sl1_{m_id}"
            )

            # Slider Team 2
            s2 = st.select_slider(
                f"{country_flag(m['team2_code'])} {m['team2']}",
                options=score_range,
                value=data['score2'],
                key=f"sl2_{m_id}"
            )

            # Berekening resultaat
            if s1 > s2: res = "1"
            elif s1 < s2: res = "2"
            else: res = "X"
            
            st.session_state.score_predictions[m_id] = {"prediction": res, "score1": s1, "score2": s2}
            
            color = "#48bb78" if res != "X" else "#ecc94b"
            st.markdown(f"<div style='text-align:center; font-weight:bold; color:{color}; padding-top:10px;'>Gok: {res} ({s1} - {s2})</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
