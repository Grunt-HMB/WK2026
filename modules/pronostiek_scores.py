import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- CALLBACK VOOR DE KNOPPEN ---
    def change_score(m_id, team_num, delta):
        m_id = str(m_id)
        field = f"score{team_num}"
        current_val = st.session_state.score_predictions[m_id][field]
        new_val = max(0, current_val + delta)
        st.session_state.score_predictions[m_id][field] = new_val
        
        # Bereken direct de 1-X-2
        s1 = st.session_state.score_predictions[m_id]["score1"]
        s2 = st.session_state.score_predictions[m_id]["score2"]
        if s1 > s2: res = "1"
        elif s1 < s2: res = "2"
        else: res = "X"
        st.session_state.score_predictions[m_id]["prediction"] = res

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR ECHTE MOBIELE CONTROLS ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    .match-card {
        background: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .match-header { font-size: 1rem; font-weight: 700; color: #ffffff; }
    .match-info { font-size: 0.7rem; color: #a0aec0; margin-bottom: 5px; }

    /* Forceer de knoppen en score op één rij */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 5px !important;
    }

    /* Stijl voor de score getallen */
    .score-display {
        font-size: 1.5rem;
        font-weight: 800;
        min-width: 30px;
        text-align: center;
    }

    /* Maak de knoppen vierkant en compact */
    div.stButton > button {
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        font-size: 20px !important;
        border-radius: 8px !important;
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
                st.toast("✅ Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    sd = st.select_slider("Speeldag", options=["1", "2", "3"], value="1")
    
    current_matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in current_matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        st.markdown(f"""
        <div class="match-card">
            <div class="match-info">{m['datum']} • {m['tijd']}</div>
            <div class="match-header">{country_flag(m['team1_code'])} {m['team1']} - {m['team2']} {country_flag(m['team2_code'])}</div>
        </div>
        """, unsafe_allow_html=True)

        # EIGEN CONTROLS: [ - ] [ Getal ] [ + ]   -   [ - ] [ Getal ] [ + ]
        col1, col2, col3, col_sep, col4, col5, col6 = st.columns([1, 1, 1, 0.5, 1, 1, 1])
        
        with col1:
            st.button("−", key=f"min1_{m_id}", on_click=change_score, args=(m_id, 1, -1))
        with col2:
            st.markdown(f"<div class='score-display'>{data['score1']}</div>", unsafe_allow_html=True)
        with col3:
            st.button("+", key=f"plus1_{m_id}", on_click=change_score, args=(m_id, 1, 1))
            
        with col_sep:
            st.markdown("<div style='text-align:center; line-height:40px;'> </div>", unsafe_allow_html=True)

        with col4:
            st.button("−", key=f"min2_{m_id}", on_click=change_score, args=(m_id, 2, -1))
        with col5:
            st.markdown(f"<div class='score-display'>{data['score2']}</div>", unsafe_allow_html=True)
        with col6:
            st.button("+", key=f"plus2_{m_id}", on_click=change_score, args=(m_id, 2, 1))

        color = "#48bb78" if data['prediction'] != "X" else "#ecc94b"
        st.markdown(f'<p style="text-align:center; color:{color}; font-weight:bold; margin-top:5px;">Gok: {data["prediction"]}</p>', unsafe_allow_html=True)
        st.divider()

    st.markdown("<br><br>", unsafe_allow_html=True)
