import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):
    # 1. Schone CSS (alleen voor de score-vakjes en spacing)
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    .stButton button { width: 100%; padding: 0px !important; height: 40px !important; font-weight: bold !important; }
    .score-label {
        background: #000; color: #60a5fa; font-size: 1.2rem; font-weight: 900;
        text-align: center; border-radius: 5px; border: 1px solid #1d4ed8;
        line-height: 40px; height: 40px;
    }
    .match-header { font-size: 0.85rem; font-weight: 700; margin-top: 10px; }
    hr { margin: 10px 0 !important; opacity: 0.2; }
    </style>
    """, unsafe_allow_html=True)

    # 2. Data laden met foutcontrole
    matches_df, predictions_df = load_matches(), load_predictions(user_id)

    if matches_df.empty:
        st.error("Geen data gevonden in de database. Controleer de tabel 'matches'.")
        return

    # 3. Session State Initialisatie
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
        
        # Maak lookup van bestaande voorspellingen
        preds_map = {str(p['match_id']): p for _, p in predictions_df.iterrows()} if not predictions_df.empty else {}

        for _, m in matches_df.iterrows():
            m_id = str(m['match_id'])
            # We laden ELKE wedstrijd (we filteren later wel in de UI indien nodig)
            p_data = preds_map.get(m_id, {})
            st.session_state.score_predictions[m_id] = {
                "team1": m['team1'], "team2": m['team2'],
                "s1": int(p_data.get('score1', 0)),
                "s2": int(p_data.get('score2', 0))
            }

    # 4. TOP NAVIGATIE
    c_nav1, c_nav2 = st.columns([1, 1])
    with c_nav1:
        if st.button("☰ Hoofdmenu"):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c_nav2:
        if st.button("💾 OPSLAAN", type="primary"):
            to_save = {mid: {"score1": d['s1'], "score2": d['s2'], 
                       "prediction": ("1" if d['s1'] > d['s2'] else "2" if d['s1'] < d['s2'] else "X")} 
                       for mid, d in st.session_state.score_predictions.items()}
            saved = batch_save_predictions(user_id, to_save, status="concept")
            st.success(f"✅ {saved} opgeslagen!")
            st.cache_data.clear()

    st.divider()

    # 5. DE WEDSTRIJDEN (met st.fragment voor snelheid)
    @st.fragment
    def render_match(m_id):
        d = st.session_state.score_predictions[m_id]
        
        # Toon teams boven de knoppen
        st.markdown(f"<div class='match-header'>{d['team1']} vs {d['team2']}</div>", unsafe_allow_html=True)
        
        # Knoppen en score op één regel
        # We gebruiken 7 smalle kolommen die Streamlit op mobiel meestal nog net naast elkaar houdt
        col1, col2, col3, col_gap, col4, col5, col6 = st.columns([1, 1.5, 1, 0.2, 1, 1.5, 1])
        
        with col1:
            if st.button("−", key=f"m1_{m_id}"):
                st.session_state.score_predictions[m_id]['s1'] = max(0, d['s1'] - 1)
                st.rerun(scope="fragment")
        with col2:
            st.markdown(f"<div class='score-label'>{d['s1']}</div>", unsafe_allow_html=True)
        with col3:
            if st.button("+", key=f"p1_{m_id}"):
                st.session_state.score_predictions[m_id]['s1'] += 1
                st.rerun(scope="fragment")

        with col4:
            if st.button("−", key=f"m2_{m_id}"):
                st.session_state.score_predictions[m_id]['s2'] = max(0, d['s2'] - 1)
                st.rerun(scope="fragment")
        with col5:
            st.markdown(f"<div class='score-label'>{d['s2']}</div>", unsafe_allow_html=True)
        with col6:
            if st.button("+", key=f"p2_{m_id}"):
                st.session_state.score_predictions[m_id]['s2'] += 1
                st.rerun(scope="fragment")
        st.markdown("<hr>", unsafe_allow_html=True)

    # Render alle matchen
    for m_id in st.session_state.score_predictions.keys():
        render_match(m_id)
