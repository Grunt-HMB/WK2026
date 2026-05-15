import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def set_score(match_id, s1, s2):
        match_id = str(match_id)
        s1, s2 = max(0, min(int(s1), 50)), max(0, min(int(s2), 50))
        diff = s1 - s2
        pred = "1" if diff > 0 else ("2" if diff < 0 else "X")
        st.session_state.score_predictions[match_id] = {
            "prediction": pred, "score1": s1, "score2": s2
        }
        st.session_state[f"score_pred_{match_id}"] = pred

    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # --- CSS VOOR EXTREME COMPACTHEID ---
    st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    
    /* Forceer kolommen om NOOIT te groeien of te wrappen */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        justify-content: flex-start !important;
    }

    [data-testid="column"] {
        min-width: 0px !important;
        flex-shrink: 1 !important;
    }

    /* Maak de knoppen exact zo breed als nodig */
    .stButton button {
        padding: 0 !important;
        min-width: 32px !important;
        width: 32px !important;
        height: 32px !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
    }

    /* De score display box */
    .score-display {
        background: #0f172a;
        border: 1px solid #475569;
        border-radius: 4px;
        text-align: center;
        width: 32px;
        height: 32px;
        line-height: 32px;
        font-weight: 900;
        font-size: 1rem;
        color: white;
    }

    /* Segmented control (1-X-2) smal houden */
    div[data-testid="stSegmentedControl"] { width: 100px !important; }
    div[data-testid="stSegmentedControl"] button {
        min-width: 32px !important;
        width: 32px !important;
        height: 32px !important;
        padding: 0 !important;
    }

    .match-card {
        background: #1e293b;
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 8px;
    }

    .team-label {
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 4px;
        white-space: nowrap;
    }
    
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # --- Data laden ---
    m_df, p_df = load_matches(), load_predictions(user_id)
    if not st.session_state[loaded_key]:
        for _, r in p_df.iterrows():
            st.session_state.score_predictions[str(r['match_id'])] = {
                "prediction": str(r['prediction']), "score1": r['score1'], "score2": r['score2']
            }
        st.session_state[loaded_key] = True

    # --- Header ---
    c_menu, c_save = st.columns([1, 1])
    with c_menu:
        if st.button("☰ Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"; st.rerun()
    with c_save:
        if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
            batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
            st.toast("Opgeslagen!")

    # --- Wedstrijdlijst ---
    for _, match in m_df.iterrows():
        mid = str(match["match_id"])
        if mid not in st.session_state.score_predictions:
            st.session_state.score_predictions[mid] = {"prediction": "X", "score1": 0, "score2": 0}
        
        s1 = st.session_state.score_predictions[mid]["score1"]
        s2 = st.session_state.score_predictions[mid]["score2"]
        
        with st.container():
            st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-label">{country_flag(match.get("team1_code"))} {match["team1"]} vs {match["team2"]} {country_flag(match.get("team2_code"))}</div>', unsafe_allow_html=True)

            # We gebruiken nu exact 7 kolommen die we dwingen heel smal te zijn
            # [1|X|2] [-] [0] [+] [-] [0] [+]
            cols = st.columns([3, 1, 1, 1, 1, 1, 1])
            
            with cols[0]:
                st.segmented_control("P", ["1", "X", "2"], key=f"score_pred_{mid}", label_visibility="collapsed")
            
            # Team 1 scores
            with cols[1]:
                if st.button("−", key=f"m1_{mid}"): set_score(mid, s1-1, s2); st.rerun()
            with cols[2]:
                st.markdown(f'<div class="score-display">{s1}</div>', unsafe_allow_html=True)
            with cols[3]:
                if st.button("+", key=f"p1_{mid}"): set_score(mid, s1+1, s2); st.rerun()

            # Team 2 scores
            with cols[4]:
                if st.button("−", key=f"m2_{mid}"): set_score(mid, s1, s2-1); st.rerun()
            with cols[5]:
                if st.markdown(f'<div class="score-display">{s2}</div>', unsafe_allow_html=True): pass
            with cols[6]:
                if st.button("+", key=f"p2_{mid}"): set_score(mid, s1, s2+1); st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)
