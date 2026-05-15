import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele knoppen en layout
    st.markdown("""
    <style>
    /* Forceer kolommen naast elkaar op mobiel */
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

    # 2. Data laden (Hetzelfde als in je werkende editor-versie)
    @st.cache_data(ttl=10) # Korte cache voor vlotter laden
    def get_data(uid):
        m = load_matches()
        p = load_predictions(uid)
        if "ronde" in m.columns:
            m = m[m["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
        return m, p

    matches_df, predictions_df = get_data(user_id)

    # 3. Synchroniseer DataFrame naar Session State
    # Dit zorgt ervoor dat de getallen op je scherm veranderen bij een klik
    if "temp_scores" not in st.session_state:
        st.session_state.temp_scores = {}
        # Maak map van bestaande voorspellingen
        preds_map = predictions_df.set_index('match_id').to_dict('index') if not predictions_df.empty else {}
        
        for _, row in matches_df.iterrows():
            m_id = str(row['match_id'])
            p = preds_map.get(m_id if m_id in preds_map else int(m_id) if m_id.isdigit() else None, {})
            st.session_state.temp_scores[m_id] = {
                "s1": int(p.get('score1', 0)),
                "s2": int(p.get('score2', 0))
            }

    # 4. Navigatie & Opslaan
    st.title("🏆 Je Pronostiek")
    
    col_nav, col_save = st.columns(2)
    with col_nav:
        if st.button("🏠 Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with col_save:
        if st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True):
            final_predictions = {}
            for mid, scores in st.session_state.temp_scores.items():
                s1, s2 = scores["s1"], scores["s2"]
                res = "1" if s1 > s2 else "2" if s1 < s2 else "X"
                final_predictions[mid] = {"score1": s1, "score2": s2, "prediction": res}
            
            saved = batch_save_predictions(user_id, final_predictions, status="concept")
            st.success(f"✅ {saved} uitslagen opgeslagen!")
            st.cache_data.clear()

    st.divider()

    # 5. Render de rijen
    # We gebruiken GEEN fragment hier om zeker te zijn dat de data laadt
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        scores = st.session_state.temp_scores.get(m_id, {"s1": 0, "s2": 0})

        st.markdown(f"<div class='match-label'>{match['team1']} vs {match['team2']}</div>", unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        # Team 1 controls
        if c1.button("−", key=f"btn_m1_{m_id}"):
            st.session_state.temp_scores[m_id]["s1"] = max(0, scores["s1"] - 1)
            st.rerun()
        c2.markdown(f"<div class='score-container'>{scores['s1']}</div>", unsafe_allow_html=True)
        if c3.button("+", key=f"btn_p1_{m_id}"):
            st.session_state.temp_scores[m_id]["s1"] += 1
            st.rerun()

        # Team 2 controls
        if c4.button("−", key=f"btn_m2_{m_id}"):
            st.session_state.temp_scores[m_id]["s2"] = max(0, scores["s2"] - 1)
            st.rerun()
        c5.markdown(f"<div class='score-container'>{scores['s2']}</div>", unsafe_allow_html=True)
        if c6.button("+", key=f"btn_p2_{m_id}"):
            st.session_state.temp_scores[m_id]["s2"] += 1
            st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
