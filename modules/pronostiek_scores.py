import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR COMPACTE INPUTS EN MOBIELE ROWS ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Top Bar */
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 75px; }

    /* Wedstrijd Kaartje */
    .match-card {
        background: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .match-header {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
    }

    .match-info {
        font-size: 0.7rem;
        color: #a0aec0;
        margin-bottom: 5px;
    }

    /* FORCEER KOLOMMEN NAAST ELKAAR OP MOBIEL */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="column"] {
        width: auto !important;
        flex: unset !important;
        min-width: unset !important;
    }

    /* SPECIFIEKE BREEDTE VOOR DE INPUT */
    div[data-testid="stNumberInput"] {
        width: 100px !important; /* Iets breder gemaakt voor + en - */
    }
    
    div[data-testid="stNumberInput"] > div {
        padding: 0 !important;
    }

    .prediction-text {
        text-align: center;
        font-weight: bold;
        font-size: 0.9rem;
        margin-top: 5px;
        margin-bottom: 15px;
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

    # --- SPEELDAG ---
    sd = st.select_slider("Kies Speeldag", options=["1", "2", "3"], value="1")
    
    # --- WEDSTRIJDEN ---
    current_matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in current_matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]

        # Header Kaartje
        st.markdown(f"""
        <div class="match-card">
            <div class="match-info">{m['datum']} • {m['tijd']}</div>
            <div class="match-header">
                {country_flag(m['team1_code'])} {m['team1']} - {m['team2']} {country_flag(m['team2_code'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # De scores (Strak naast elkaar zonder spacers)
        col_left, col_mid, col_right = st.columns([1, 0.2, 1])
        
        with col_left:
            new_s1 = st.number_input(
                "S1", min_value=0, max_value=20, 
                value=int(data['score1']), 
                key=f"in1_{m_id}", label_visibility="collapsed"
            )
        
        with col_mid:
            st.markdown("<div style='text-align:center; line-height:40px; font-weight:bold;'>-</div>", unsafe_allow_html=True)

        with col_right:
            new_s2 = st.number_input(
                "S2", min_value=0, max_value=20, 
                value=int(data['score2']), 
                key=f"in2_{m_id}", label_visibility="collapsed"
            )

        # Resultaat bepalen
        if new_s1 > new_s2: res = "1"
        elif new_s1 < new_s2: res = "2"
        else: res = "X"
        
        st.session_state.score_predictions[m_id] = {
            "prediction": res, "score1": new_s1, "score2": new_s2
        }

        # Gok tekst
        color = "#48bb78" if res != "X" else "#ecc94b"
        st.markdown(f'<div class="prediction-text" style="color:{color};">Gok: {res}</div>', unsafe_allow_html=True)
        st.divider()

    st.markdown("<br><br>", unsafe_allow_html=True)
