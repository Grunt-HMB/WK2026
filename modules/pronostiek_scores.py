import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR ONVERBIDDELIJKE HORIZONTALE LAYOUT ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Top Bar */
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    /* Match Container */
    .match-box {
        background: #1a202c;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #2d3748;
    }

    /* FORCEER NAAST ELKAAR OP MOBIEL */
    /* We targeten de specifieke div die Streamlit kolommen bevat */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 10px !important;
    }

    /* Team labels compact */
    .team-label-fixed {
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: -10px;
    }

    /* Verberg labels van de sliders */
    div[data-testid="stWidgetLabel"] {
        display: none !important;
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
                st.toast("✅ Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # Speeldag Slider
    sd = st.select_slider("Speeldag", options=["1", "2", "3"], value="1")
    
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]
    score_range = list(range(11))

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        with st.container():
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.6rem; color:#718096; text-align:center;'>{m['datum']} • {m['tijd']}</div>", unsafe_allow_html=True)
            
            # De kolommen die we horizontaal dwingen
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'<div class="team-label-fixed">{country_flag(m["team1_code"])} {m["team1"]}</div>', unsafe_allow_html=True)
                s1 = st.select_slider("s1", options=score_range, value=data['score1'], key=f"sl1_{m_id}")

            with col2:
                st.markdown(f'<div class="team-label-fixed">{country_flag(m["team2_code"])} {m["team2"]}</div>', unsafe_allow_html=True)
                s2 = st.select_slider("s2", options=score_range, value=data['score2'], key=f"sl2_{m_id}")

            # Berekening resultaat
            if s1 > s2: res = "1"
            elif s1 < s2: res = "2"
            else: res = "X"
            
            st.session_state.score_predictions[m_id] = {"prediction": res, "score1": s1, "score2": s2}
            
            color = "#48bb78" if res != "X" else "#ecc94b"
            st.markdown(f"<div style='text-align:center; font-weight:bold; color:{color}; font-size:0.85rem; margin-top:5px;'>{s1} - {s2} (Gok: {res})</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
