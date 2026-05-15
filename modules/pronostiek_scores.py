import streamlit as st
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # --- Helper Functies ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def set_score(match_id, s1, s2):
        match_id = str(match_id)
        s1, s2 = max(0, min(int(s1), 50)), max(0, min(int(s2), 50))
        diff = s1 - s2
        pred = "1" if diff > 0 else ("2" if diff < 0 else "X")
        st.session_state.score_predictions[match_id] = {"prediction": pred, "score1": s1, "score2": s2}
        st.session_state[f"score_pred_{match_id}"] = pred

    # --- Session State ---
    if "score_predictions" not in st.session_state: st.session_state.score_predictions = {}
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state: st.session_state[loaded_key] = False

    # --- CSS VOOR MAXIMALE COMPACTHEID ---
    st.markdown("""
    <style>
    .block-container { padding: 0.2rem !important; }
    
    /* Forceer kolommen op één rij zonder padding */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="column"] { min-width: 0px !important; flex: 1 1 auto !important; }

    /* Maak de knoppen super smal */
    .stButton button {
        height: 32px !important;
        padding: 0 !important;
        font-size: 0.9rem !important;
        font-weight: 900 !important;
    }
    
    /* Segmented control (1-X-2) versmallen */
    div[data-testid="stSegmentedControl"] button {
        min-width: 30px !important;
        height: 32px !important;
        padding: 0 !important;
    }

    .score-box {
        background: #0b1220;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 4px;
        text-align: center;
        height: 32px;
        line-height: 32px;
        font-weight: 900;
        font-size: 0.9rem;
    }

    .match-card {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 6px;
    }

    .top-bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 99;
        background: #0e1117; padding: 6px; border-bottom: 1px solid #333;
    }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # --- Data ---
    m_df, p_df = load_matches(), load_predictions(user_id)
    if not st.session_state[loaded_key]:
        for _, r in p_df.iterrows():
            st.session_state.score_predictions[str(r['match_id'])] = {
                "prediction": str(r['prediction']), "score1": r['score1'], "score2": r['score2']
            }
        st.session_state[loaded_key] = True

    # --- UI ---
    st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)
    
    for _, match in m_df.iterrows():
        mid = str(match["match_id"])
        if mid not in st.session_state.score_predictions:
            st.session_state.score_predictions[mid] = {"prediction": "X", "score1": 0, "score2": 0}
        
        pred_key = f"score_pred_{mid}"
        s1 = st.session_state.score_predictions[mid]["score1"]
        s2 = st.session_state.score_predictions[mid]["score2"]

        with st.container():
            st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
            st.markdown(f"**{country_flag(match.get('team1_code'))} vs {country_flag(match.get('team2_code'))}**")
            
            # We gebruiken nu slechts 5 kolommen (veel stabieler op mobiel)
            c_pred, c_m1, c_s1, c_p1, c_sep, c_m2, c_s2, c_p2 = st.columns([2.5, 0.8, 0.8, 0.8, 0.2, 0.8, 0.8, 0.8])
            
            with c_pred:
                st.segmented_control("P", ["1", "X", "2"], key=pred_key, label_visibility="collapsed")
            
            # Team 1
            with c_m1:
                if st.button("−", key=f"m1_{mid}"): set_score(mid, s1-1, s2); st.rerun()
            with c_s1:
                st.markdown(f'<div class="score-box">{s1}</div>', unsafe_allow_html=True)
            with c_p1:
                if st.button("+", key=f"p1_{mid}"): set_score(mid, s1+1, s2); st.rerun()

            with c_sep:
                st.markdown('<div style="text-align:center;">-</div>', unsafe_allow_html=True)

            # Team 2
            with c_m2:
                if st.button("−", key=f"m2_{mid}"): set_score(mid, s1, s2-1); st.rerun()
            with c_s2:
                st.markdown(f'<div class="score-box">{s2}</div>', unsafe_allow_html=True)
            with c_p2:
                if st.button("+", key=f"p2_{mid}"): set_score(mid, s1, s2+1); st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Save knop onderaan (vaster dan topbar op sommige telefoons)
    if st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True):
        batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
        st.toast("Opgeslagen!")
