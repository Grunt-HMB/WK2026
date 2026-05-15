import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):

    # =========================================================
    # HELPERS
    # =========================================================

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def format_date(value):
        txt = str(value or "").strip()
        parts = txt.split("-")
        return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else txt

    def format_time(value):
        txt = str(value or "").strip()
        return ":".join(txt.split(":")[:2]) if txt.count(":") >= 2 else txt

    def result_from_score(score1, score2):
        try:
            s1, s2 = int(score1), int(score2)
            if s1 > s2: return "1"
            if s1 < s2: return "2"
            return "X"
        except: return ""

    def ensure_match_prediction(match_id):
        match_id = str(match_id)
        if match_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[match_id] = {
                "prediction": "", "score1": 0, "score2": 0,
            }

    # =========================================================
    # CSS & SESSION STATE
    # =========================================================

    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}

    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    st.markdown("""
    <style>
    .block-container { max-width: 820px; padding: 0 0.4rem 5rem 0.4rem !important; }
    section[data-testid="stSidebar"] { display: none; }
    .st-key-score_top_bar {
        position: fixed !important; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.12);
    }
    .top-spacer { height: 75px; }
    [class*="st-key-score_match_card_"] {
        background: #111827; border: 1px solid rgba(255,255,255,0.13);
        border-radius: 14px; padding: 0.6rem !important; margin-bottom: 0.5rem;
    }
    .match-meta { font-size: 0.75rem; color: #cbd5e1; margin-bottom: 0.2rem; }
    .match-line { font-size: 0.95rem; font-weight: 900; margin-bottom: 0.5rem; }
    .result-badge {
        display: inline-block; margin-left: 0.4rem; background: rgba(37,99,235,0.2);
        border: 1px solid rgba(96,165,250,0.55); border-radius: 12px;
        padding: 0.1rem 0.5rem; font-size: 0.8rem; color: #bfdbfe;
    }
    .score-value {
        height: 34px; line-height: 34px; text-align: center; font-weight: 900;
        background: #0b1220; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px;
    }
    .score-gap { line-height: 34px; text-align: center; color: #64748b; font-weight: 900; }
    
    /* Knoppen styling */
    [class*="st-key-minus"] button, [class*="st-key-plus"] button {
        border-radius: 8px !important; min-height: 34px !important; height: 34px !important;
    }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # DATA
    # =========================================================

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                m_id = str(row.get("match_id", "")).strip()
                if m_id:
                    s1, s2 = int(float(row.get("score1", 0))), int(float(row.get("score2", 0)))
                    st.session_state.score_predictions[m_id] = {
                        "prediction": result_from_score(s1, s2),
                        "score1": s1, "score2": s2,
                    }
        st.session_state[loaded_key] = True

    # =========================================================
    # TOP BAR (Geen formulier meer)
    # =========================================================

    with st.container(key="score_top_bar"):
        c_h, c_s = st.columns([1, 1.4])
        with c_h:
            if st.button("☰ Menu", key="btn_menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c_s:
            if st.button("💾 ALLES OPSLAAN", key="btn_save_all", type="primary", use_container_width=True):
                saved = batch_save_predictions(
                    user_id=user_id,
                    local_predictions=st.session_state.score_predictions,
                    status="concept"
                )
                st.cache_data.clear()
                st.success(f"Opgeslagen: {saved} wedstrijden!")
                st.balloons()

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # =========================================================
    # WEDSTRIJDEN LIJST
    # =========================================================

    wedstrijden = matches_df.copy()
    if "ronde" in wedstrijden.columns:
        wedstrijden = wedstrijden[wedstrijden["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
    
    wedstrijden = wedstrijden.sort_values(["datum", "tijd"], kind="stable")

    for _, match in wedstrijden.iterrows():
        m_id = str(match.get("match_id", "")).strip()
        ensure_match_prediction(m_id)
        
        data = st.session_state.score_predictions[m_id]
        s1, s2 = data["score1"], data["score2"]

        with st.container(key=f"score_match_card_{m_id}"):
            st.markdown(f"""
                <div class="match-meta"><b>{format_date(match.get('datum'))}</b> &nbsp; {format_time(match.get('tijd'))}</div>
                <div class="match-line">
                    {country_flag(match.get('team1_code'))} {match.get('team1')} 
                    <span style="color:#6b7280;">vs</span> 
                    {match.get('team2')} {country_flag(match.get('team2_code'))}
                    <span class="result-badge">{data['prediction']}</span>
                </div>
            """, unsafe_allow_html=True)

            cols = st.columns([1, 1, 1, 0.4, 1, 1, 1], gap="small")
            
            # Team 1 Controls
            if cols[0].button("−", key=f"minus1_{m_id}"):
                new_s1 = max(0, s1 - 1)
                st.session_state.score_predictions[m_id].update({"score1": new_s1, "prediction": result_from_score(new_s1, s2)})
                st.rerun()
            
            cols[1].markdown(f"<div class='score-value'>{s1}</div>", unsafe_allow_html=True)
            
            if cols[2].button("+", key=f"plus1_{m_id}"):
                new_s1 = min(50, s1 + 1)
                st.session_state.score_predictions[m_id].update({"score1": new_s1, "prediction": result_from_score(new_s1, s2)})
                st.rerun()

            cols[3].markdown("<div class='score-gap'>-</div>", unsafe_allow_html=True)

            # Team 2 Controls
            if cols[4].button("−", key=f"minus2_{m_id}"):
                new_s2 = max(0, s2 - 1)
                st.session_state.score_predictions[m_id].update({"score2": new_s2, "prediction": result_from_score(s1, new_s2)})
                st.rerun()
            
            cols[5].markdown(f"<div class='score-value'>{s2}</div>", unsafe_allow_html=True)
            
            if cols[6].button("+", key=f"plus2_{m_id}"):
                new_s2 = min(50, s2 + 1)
                st.session_state.score_predictions[m_id].update({"score2": new_s2, "prediction": result_from_score(s1, new_s2)})
                st.rerun()
