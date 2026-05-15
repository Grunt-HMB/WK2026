import streamlit as st
import pandas as pd

from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):

    # =========================================================
    # HELPERS & CALLBACKS
    # =========================================================

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2:
            return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def format_date(value):
        txt = str(value or "").strip()
        parts = txt.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return txt

    def format_time(value):
        txt = str(value or "").strip()
        if txt.count(":") >= 2:
            return ":".join(txt.split(":")[:2])
        return txt

    def result_from_score(score1, score2):
        try:
            s1 = int(score1)
            s2 = int(score2)
            if s1 > s2: return "1"
            if s1 < s2: return "2"
            return "X"
        except:
            return ""

    def ensure_match_prediction(match_id):
        match_id = str(match_id)
        if "score_predictions" not in st.session_state:
            st.session_state.score_predictions = {}
        
        if match_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[match_id] = {
                "prediction": "",
                "score1": 0,
                "score2": 0,
            }

    # CALLBACK FUNCTIE: Werkt de score bij zonder volledige rerun
    def update_score_callback(match_id, team_num, delta):
        match_id = str(match_id)
        ensure_match_prediction(match_id)
        
        current_data = st.session_state.score_predictions[match_id]
        field = f"score{team_num}"
        
        # Nieuwe waarde berekenen (tussen 0 en 50)
        new_val = max(0, min(int(current_data.get(field, 0)) + delta, 50))
        current_data[field] = new_val
        
        # Update direct de 1-X-2 voorspelling
        current_data["prediction"] = result_from_score(
            current_data["score1"], 
            current_data["score2"]
        )

    def save_all_predictions():
        saved_count = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.score_predictions,
            status="concept",
        )
        st.cache_data.clear()
        return saved_count

    # =========================================================
    # SESSION STATE INITIALISATIE
    # =========================================================

    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}

    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    # =========================================================
    # CSS
    # =========================================================

    st.markdown("""
    <style>
    .block-container { max-width: 820px; padding-bottom: 5rem !important; }
    
    /* Top Bar Styling */
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .top-spacer { height: 70px; }

    /* Card Styling */
    [class*="st-key-score_match_card_"] {
        background: #111827; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 15px !important; margin-bottom: 10px;
    }

    .match-meta { font-size: 0.8rem; color: #9ca3af; }
    .match-line { font-size: 1rem; font-weight: bold; margin: 5px 0; }
    .result-badge { 
        background: rgba(37,99,235,0.2); border: 1px solid #60a5fa;
        padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; margin-left: 10px;
    }

    /* Score Display */
    .score-value {
        background: #0b1220; border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px; text-align: center; font-weight: bold;
        height: 35px; line-height: 35px; font-size: 1.1rem;
    }
    .score-gap { text-align: center; line-height: 35px; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # DATA LADEN
    # =========================================================

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    # Eenmalig inladen van database naar session_state
    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                m_id = str(row.get("match_id", "")).strip()
                if not m_id: continue
                
                try:
                    s1 = int(float(row.get("score1", 0)))
                    s2 = int(float(row.get("score2", 0)))
                except:
                    s1, s2 = 0, 0

                st.session_state.score_predictions[m_id] = {
                    "prediction": result_from_score(s1, s2),
                    "score1": s1,
                    "score2": s2,
                }
        st.session_state[loaded_key] = True

    # =========================================================
    # UI: TOP BAR
    # =========================================================

    with st.container(key="score_top_bar"):
        col_home, col_save = st.columns([1, 1], gap="small")
        with col_home:
            if st.button("☰ Menu", key="back_btn", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with col_save:
            if st.button("💾 OPSLAAN", key="save_btn", type="primary", use_container_width=True):
                saved = save_all_predictions()
                st.toast(f"✅ {saved} voorspellingen opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # =========================================================
    # UI: WEDSTRIJD LIJST
    # =========================================================

    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Filter op groepsfase indien nodig
    if "ronde" in matches_df.columns:
        matches_df = matches_df[matches_df["ronde
