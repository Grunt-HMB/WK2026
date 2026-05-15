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

    # --- CSS VOOR OPTIMALE MOBIELE LAYOUT ---
    st.markdown("""
    <style>
    /* Pagina marges minimaliseren */
    .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.4rem !important; 
        padding-right: 0.4rem !important; 
    }

    /* Kaart styling */
    .match-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Team namen groter op eigen regel */
    .team-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 1rem;
        font-weight: 800;
        color: white;
    }

    /* Forceer de knoppenrij op één lijn */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
        align-items: center !important;
    }

    [data-testid="column"] {
        min-width: 0px !important;
        flex: 1 1 auto !important;
    }

    /* Knoppen compacter voor duim-bediening */
    .stButton button {
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        background-color: #334155 !important;
    }

    /* Score getal display */
    .score-display {
        background: #0f172a;
        border: 1px solid #475569;
        border-radius: 6px;
        text-align: center;
        height: 36px;
        line-height: 36px;
        font-weight: 900;
        font-size: 1.1rem;
        color: #38bdf8;
    }

    /* 1-X-2 Segmented control styling */
    div[data-testid="stSegmentedControl"] button {
        height: 36px !important;
        min-width: 35px !important;
    }

    .top-bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0f172a; padding: 10px; border-bottom: 2px solid #334155;
    }
    .spacer { height: 70px; }
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

    # --- Top Bar ---
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)
    c_menu, c_save = st.columns([1, 1])
    with c_menu:
        if st.button("☰ Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"; st.rerun()
    with c_save:
        if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
            batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
            st.toast("Opgeslagen!")
    st.markdown('</div><div class="spacer"></div>', unsafe_allow_html=True)

    # --- Wedstrijden ---
    for _, match in m_df.iterrows():
        mid = str(match["match_id"])
        if mid not in st.session_state.score_predictions:
            st.session_state.score_predictions[mid] = {"prediction": "X", "score1": 0, "score2": 0}
        
        s1 = st.session_state.score_predictions[mid]["score1"]
        s2 = st.session_state.score_predictions[mid]["score2"]
        pred_key = f"score_pred_{mid}"

        # De kaart container
        st.markdown(f"""
            <div class="match-card">
                <div class="team-header">
                    <span>{country_flag(match.get('team1_code'))} {match['team1']}</span>
                    <span style="color:#94a3b8; font-size:0.8rem;">VS</span>
                    <span>{match['team2']} {country_flag(match.get('team2_code'))}</span>
                </div>
            """, unsafe_allow_html=True)

        # De knoppenrij (onder de namen, dus volle breedte beschikbaar)
        cols = st.columns([2.5, 0.8, 0.8, 0.8, 0.2, 0.8, 0.8, 0.8])
        
        with cols[0]:
            st.segmented_control("P", ["1", "X", "2"], key=pred_key, label_visibility="collapsed")
        
        with cols[1]:
            if st.button("−", key=f"m1_{mid}", use_container_width=True): set_score(mid, s1-1, s2); st.rerun()
        with cols[2]:
            st.markdown(f'<div class="score-display">{s1}</div>', unsafe_allow_html=True)
        with cols[3]:
            if st.button("+", key=f"p1_{mid}", use_container_width=True): set_score(mid, s1+1, s2); st.rerun()

        with cols[4]:
            st.markdown('<div style="text-align:center; padding-top:4px;">-</div>', unsafe_allow_html=True)

        with cols[5]:
            if st.button("−", key=f"m2_{mid}", use_container_width=True): set_score(mid, s1, s2-1); st.rerun()
        with cols[6]:
            st.markdown(f'<div class="score-display">{s2}</div>', unsafe_allow_html=True)
        with cols[7]:
            if st.button("+", key=f"p2_{mid}", use_container_width=True): set_score(mid, s1, s2+1); st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
