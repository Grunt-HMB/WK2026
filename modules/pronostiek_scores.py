import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele knoppen en layout
    st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .score-container {
        background: #1e293b; color: #60a5fa; font-size: 1.3rem; font-weight: bold;
        text-align: center; border: 1px solid #3b82f6; border-radius: 6px;
        line-height: 40px; height: 40px; margin: 2px 0;
    }
    .match-label { font-weight: bold; font-size: 1rem; margin-top: 12px; color: white; }
    hr { margin: 12px 0 !important; border: 0; border-top: 1px solid #334155 !important; }
    .stButton button { width: 100%; height: 40px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

    # Hulpfunctie om veilig getallen te laden (voorkomt de ValueError uit je logs)
    def safe_int(val):
        if val is None or str(val).strip() == "":
            return 0
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return 0

    # 2. Data laden
    @st.cache_data(ttl=5)
    def get_data(uid):
        m = load_matches()
        p = load_predictions(uid)
        if "ronde" in m.columns:
            m = m[m["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
        return m, p

    matches_df, predictions_df = get_data(user_id)

    # 3. Initialiseer Session State
    if "temp_scores" not in st.session_state:
        st.session_state.temp_scores = {}
        preds_map = predictions_df.set_index('match_id').to_dict('index') if not predictions_df.empty else {}
        
        for _, row in matches_df.iterrows():
            m_id = str(row['match_id'])
            # Zoek match in voorspellingen (check zowel string als int match_id)
            p = preds_map.get(m_id) or preds_map.get(safe_int(m_id)) or {}
            
            st.session_state.temp_scores[m_id] = {
                "s1": safe_int(p.get('score1', 0)),
                "s2": safe_int(p.get('score2', 0))
            }

    # 4. Header & Opslaan
    st.title("🏆 Je Pronostiek")
    
    col_nav, col_save = st.columns(2)
    with col_nav:
        if st.button("🏠 Menu", width='stretch'):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with col_save:
        if st.button("💾 OPSLAAN", type="primary", width='stretch'):
            final_predictions = {}
            for mid, scores in st.session_state.temp_scores.items():
                s1, s2 = scores["s1"], scores["s2"]
                res = "1" if s1 > s2 else "2" if s1 < s2 else "X"
                final_predictions[mid] = {"score1": s1, "score2": s2, "prediction": res}
            
            saved = batch_save_predictions(user_id, final_predictions, status="concept")
            st.success(f"✅ Opgeslagen!")
            st.cache_data.clear()

    st.divider()

    # 5. De Knoppen-Matrix
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        # Zorg dat de match-id altijd in state bestaat
        if m_id not in st.session_state.temp_scores:
            st.session_state.temp_scores[m_id] = {"s1": 0, "s2": 0}
            
        scores = st.session_state.temp_scores[m_id]

        st.markdown(f"<div class='match-label'>{match['team1']} vs {match['team2']}</div>", unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        # Team 1
        if c1.button("−", key=f"m1_{m_id}"):
            st.session_state.temp_scores[m_id]["s1"] = max(0, scores["s1"] - 1)
            st.rerun()
        c2.markdown(f"<div class='score-container'>{scores['s1']}</div>", unsafe_allow_html=True)
        if c3.button("+", key=f"p1_{m_id}"):
            st.session_state.temp_scores[m_id]["s1"] += 1
            st.rerun()

        # Team 2
        if c4.button("−", key=f"m2_{m_id}"):
            st.session_state.temp_scores[m_id]["s2"] = max(0, scores["s2"] - 1)
            st.rerun()
        c5.markdown(f"<div class='score-container'>{scores['s2']}</div>", unsafe_allow_html=True)
        if c6.button("+", key=f"p2_{m_id}"):
            st.session_state.temp_scores[m_id]["s2"] += 1
            st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
