import streamlit as st
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

    def update_score(match_id, team_num, delta):
        match_id = str(match_id)
        data = st.session_state.score_predictions[match_id]
        field = f"score{team_num}"
        data[field] = max(0, min(int(data[field]) + delta, 50))
        data["prediction"] = result_from_score(data["score1"], data["score2"])

    # =========================================================
    # SESSION STATE & DATA
    # =========================================================
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                m_id = str(row.get("match_id", "")).strip()
                if m_id:
                    s1 = int(float(row.get("score1", 0)))
                    s2 = int(float(row.get("score2", 0)))
                    st.session_state.score_predictions[m_id] = {
                        "prediction": result_from_score(s1, s2),
                        "score1": s1, "score2": s2
                    }
        st.session_state[loaded_key] = True

    # =========================================================
    # CSS (CRUCIAAL VOOR MOBIEL)
    # =========================================================
    st.markdown("""
    <style>
    .block-container { max-width: 820px; padding: 0 0.5rem 5rem 0.5rem !important; }
    
    /* Forceer kolommen naast elkaar op mobiel */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }
    
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 4px !important;
    }

    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .top-spacer { height: 70px; }

    .match-card {
        background: #111827; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 12px; margin-bottom: 8px;
    }
    
    .score-value {
        background: #0b1220; border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px; text-align: center; font-weight: 900;
        height: 32px; line-height: 32px; font-size: 1rem;
    }

    .result-badge {
        background: rgba(37,99,235,0.2); border: 1px solid #60a5fa;
        padding: 1px 6px; border-radius: 6px; font-size: 0.75rem; color: #bfdbfe;
    }
    
    /* Maak knoppen compact voor mobiel */
    button { padding: 0 !important; height: 32px !important; min-height: 32px !important; }
    </style>
    """, unsafe_allow_html=True)

    # =========================================================
    # UI
    # =========================================================
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns([1, 1.4])
        with c1:
            if st.button("☰ Menu", use_container_width=True):
                st.session_state.main_page = "Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
                saved = batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.success(f"Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    for _, match in matches_df.iterrows():
        m_id = str(match.get("match_id", "")).strip()
        if not m_id: continue
        
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "", "score1": 0, "score2": 0}
            
        data = st.session_state.score_predictions[m_id]

        st.markdown(f"""
        <div class="match-card">
            <div style="font-size:0.7rem; color:#9ca3af;">{format_date(match.get('datum'))} | {format_time(match.get('tijd'))}</div>
            <div style="font-weight:900; font-size:0.85rem; margin-bottom:8px;">
                {country_flag(match.get('team1_code'))} {match.get('team1')} vs {match.get('team2')} {country_flag(match.get('team2_code'))}
                <span class="result-badge">{data['prediction']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # De kolommen binnen een container met een specifieke key om CSS te targeten
        with st.container():
            cols = st.columns([1, 1, 1, 0.3, 1, 1, 1])
            
            with cols[0]: st.button("−", key=f"m1_{m_id}", on_click=update_score, args=(m_id, 1, -1), use_container_width=True)
            with cols[1]: st.markdown(f'<div class="score-value">{data["score1"]}</div>', unsafe_allow_html=True)
            with cols[2]: st.button("+", key=f"p1_{m_id}", on_click=update_score, args=(m_id, 1, 1), use_container_width=True)
            
            with cols[3]: st.markdown('<div style="text-align:center; line-height:32px;">-</div>', unsafe_allow_html=True)
            
            with cols[4]: st.button("−", key=f"m2_{m_id}", on_click=update_score, args=(m_id, 2, -1), use_container_width=True)
            with cols[5]: st.markdown(f'<div class="score-value">{data["score2"]}</div>', unsafe_allow_html=True)
            with cols[6]: st.button("+", key=f"p2_{m_id}", on_click=update_score, args=(m_id, 2, 1), use_container_width=True)
