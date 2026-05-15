import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):

    # --- Helper Functies ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def result_from_score(score1, score2):
        try:
            s1, s2 = int(score1), int(score2)
            if s1 > s2: return "1"
            if s1 < s2: return "2"
            return "X"
        except: return ""

    def default_score_for_prediction(prediction):
        p = str(prediction or "").upper().strip()
        if p == "1": return 1, 0
        if p == "X": return 0, 0
        if p == "2": return 0, 1
        return 0, 0

    def ensure_match_prediction(match_id):
        if str(match_id) not in st.session_state.score_predictions:
            st.session_state.score_predictions[str(match_id)] = {
                "prediction": "", "score1": "", "score2": ""
            }

    def set_score(match_id, score1, score2):
        match_id = str(match_id)
        s1, s2 = max(0, min(int(score1), 50)), max(0, min(int(score2), 50))
        pred = result_from_score(s1, s2)
        st.session_state.score_predictions[match_id] = {
            "prediction": pred, "score1": s1, "score2": s2
        }
        st.session_state[f"score_pred_{match_id}"] = pred

    def prediction_changed(match_id):
        key = f"score_pred_{match_id}"
        chosen = st.session_state.get(key)
        if chosen not in ["1", "X", "2"]: return
        
        data = st.session_state.score_predictions.get(str(match_id), {})
        s1_curr = str(data.get("score1", "")).strip()
        
        if s1_curr == "" or result_from_score(data.get("score1", 0), data.get("score2", 0)) != chosen:
            s1, s2 = default_score_for_prediction(chosen)
            set_score(match_id, s1, s2)

    # --- Session State & Data ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # --- CSS VOOR ECHTE MOBIELE WEERGAVE ---
    st.markdown("""
    <style>
    .block-container { max-width: 820px; padding-top: 0 !important; padding-left: 0.2rem !important; padding-right: 0.2rem !important; }
    section[data-testid="stSidebar"] { display: none; }

    /* FORCEER KOLOMMEN NAAST ELKAAR OP MOBIEL (GEEN STACKING) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0.15rem !important;
    }

    [data-testid="column"] {
        width: auto !important;
        min-width: 0px !important;
        flex-grow: 1 !important;
    }

    /* Kaart Styling */
    [class*="st-key-score_match_card_"] {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 12px;
        padding: 0.6rem !important;
        margin-bottom: 0.5rem;
    }

    .match-teams-onecell {
        font-size: 0.88rem;
        font-weight: 800;
        margin-bottom: 8px;
        color: white;
    }

    /* Knoppen en Display compacter */
    .stButton button {
        height: 32px !important;
        min-height: 32px !important;
        padding: 0px !important;
        font-weight: 900 !important;
    }

    .score-display {
        background: #0b1220;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        text-align: center;
        font-weight: 900;
        height: 32px;
        line-height: 32px;
        font-size: 0.95rem;
        color: white;
    }

    /* Segmented Control (1 X 2) */
    div[data-testid="stSegmentedControl"] { min-width: 95px !important; }
    div[data-testid="stSegmentedControl"] button {
        height: 32px !important;
        padding: 0px !important;
        font-size: 0.75rem !important;
    }

    .st-key-score_top_bar {
        position: fixed !important; top: 0; left: 0; right: 0; z-index: 9999;
        background: #0e1117; padding: 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .top-spacer { height: 70px; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # --- Data laden ---
    @st.cache_data(ttl=60)
    def get_data(uid): return load_matches(), load_predictions(uid)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                mid = str(row.get("match_id", "")).strip()
                if mid:
                    st.session_state.score_predictions[mid] = {
                        "prediction": str(row.get("prediction", "")).upper(),
                        "score1": row.get("score1", 0),
                        "score2": row.get("score2", 0)
                    }
        st.session_state[loaded_key] = True

    # --- UI Elements ---
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("☰ Menu", key="back_btn", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"; st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", key="save_btn", use_container_width=True, type="primary"):
                saved = batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.toast(f"✅ {saved} opgeslagen"); st.cache_data.clear()

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # --- Wedstrijdlijst ---
    for _, match in matches_df.iterrows():
        mid = str(match["match_id"]).strip()
        ensure_match_prediction(mid)
        
        # State synchronisatie
        pred_key = f"score_pred_{mid}"
        if pred_key not in st.session_state:
            st.session_state[pred_key] = st.session_state.score_predictions[mid]["prediction"]

        s1 = st.session_state.score_predictions[mid]["score1"]
        s2 = st.session_state.score_predictions[mid]["score2"]

        with st.container(key=f"score_match_card_{mid}"):
            st.markdown(f"""<div class="match-teams-onecell">
                {country_flag(match.get('team1_code'))} {match['team1']} 
                <span style="color:#64748b;">vs</span> 
                {country_flag(match.get('team2_code'))} {match['team2']}
            </div>""", unsafe_allow_html=True)

            # De cruciale kolom verdeling
            cols = st.columns([2.6, 0.7, 0.7, 0.7, 0.2, 0.7, 0.7, 0.7])
            
            with cols[0]:
                st.segmented_control("P", ["1", "X", "2"], key=pred_key, 
                                     label_visibility="collapsed", on_change=prediction_changed, args=(mid,))
            
            # Team 1 scores
            with cols[1]:
                if st.button("−", key=f"m1_{mid}", use_container_width=True):
                    set_score(mid, s1-1, s2); st.rerun()
            with cols[2]:
                st.markdown(f'<div class="score-display">{s1}</div>', unsafe_allow_html=True)
            with cols[3]:
                if st.button("+", key=f"p1_{mid}", use_container_width=True):
                    set_score(mid, s1+1, s2); st.rerun()

            with cols[4]:
                st.markdown('<div style="text-align:center; color:#475569;">-</div>', unsafe_allow_html=True)

            # Team 2 scores
            with cols[5]:
                if st.button("−", key=f"m2_{mid}", use_container_width=True):
                    set_score(mid, s1, s2-1); st.rerun()
            with cols[6]:
                st.markdown(f'<div class="score-display">{s2}</div>', unsafe_allow_html=True)
            with cols[7]:
                if st.button("+", key=f"p2_{mid}", use_container_width=True):
                    set_score(mid, s1, s2+1); st.rerun()
