import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR ONWRIGBARE HORIZONTALE RIJEN ---
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
        padding: 8px;
        margin-bottom: 10px;
        border: 1px solid #2d3748;
    }

    /* Dwing de kolommen om NAAST elkaar te blijven op mobiel */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 5px !important;
    }

    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important; /* Cruciaal: laat kolommen krimpen */
    }

    /* Stijl voor de teamnaam en vlag */
    .team-info-mini {
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: -5px;
    }

    /* Verberg standaard labels van sliders */
    div[data-testid="stWidgetLabel"] { display: none !important; }

    /* Maak de slider-widget compacter */
    .stSlider { margin-top: -10px !important; }
    
    .score-summary {
        text-align: center;
        font-size: 1rem;
        font-weight: 900;
        margin-top: 5px;
        color: #63b3ed;
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
            for _, row in db_preds.iterrows():
                st.session_state.score_predictions[str(row['match_id'])] = {
                    "prediction": row['prediction'], "score1": int(row['score1']), "score2": int(row['score2'])
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

    sd = st.select_slider("Speeldag", options=["1", "2", "3"], value="1")
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        d = st.session_state.score_predictions[m_id]

        with st.container():
            st.markdown('<div class="match-box">', unsafe_allow_html=True)
            
            # De Rij met twee kolommen die we via CSS dwingen
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown(f'<div class="team-info-mini">{country_flag(m["team1_code"])} {m["team1"]}</div>', unsafe_allow_html=True)
                s1 = st.select_slider(f"sl1_{m_id}", options=list(range(11)), value=d['score1'], key=f"s1_{m_id}")

            with col_right:
                st.markdown(f'<div class="team-info-mini">{country_flag(m["team2_code"])} {m["team2"]}</div>', unsafe_allow_html=True)
                s2 = st.select_slider(f"sl2_{m_id}", options=list(range(11)), value=d['score2'], key=f"s2_{m_id}")

            # Resultaat bepaling
            res = "1" if s1 > s2 else ("2" if s2 > s1 else "X")
            st.session_state.score_predictions[m_id] = {"prediction": res, "score1": s1, "score2": s2}
            
            res_color = "#48bb78" if res != "X" else "#ecc94b"
            st.markdown(f'<div class="score-summary">{s1} - {s2} <span style="font-size:0.7rem; color:{res_color};">({res})</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
