import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):
    # 1. Minimale CSS - Alleen voor de score-look, GEEN knop-hacks
    st.markdown("""
    <style>
    .score-display {
        background-color: #0e1117;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 5px 0;
        margin: 2px 0;
    }
    .match-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 15px;
        color: #f8fafc;
    }
    /* Zorg dat kolommen NOOIT onder elkaar klappen op mobiel */
    [data-testid="column"] {
        min-width: 0px !important;
        flex: 1 1 0% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Data ophalen (met extra checks voor kolomnamen)
    matches_df, predictions_df = load_matches(), load_predictions(user_id)

    if matches_df.empty:
        st.error("Geen wedstrijden gevonden in de database.")
        return

    # 3. Session State vullen
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
        
        # Maak een simpele dictionary van bestaande voorspellingen
        preds_dict = {}
        if not predictions_df.empty:
            for _, p in predictions_df.iterrows():
                preds_dict[str(p['match_id'])] = p

        for _, m in matches_df.iterrows():
            m_id = str(m['match_id'])
            p = preds_dict.get(m_id, {})
            st.session_state.score_predictions[m_id] = {
                "team1": m.get('team1', 'Onbekend'),
                "team2": m.get('team2', 'Onbekend'),
                "s1": int(p.get('score1', 0)) if p.get('score1') else 0,
                "s2": int(p.get('score2', 0)) if p.get('score2') else 0,
            }

    # 4. Navigatie bovenaan
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☰ Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c2:
        if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
            formatted_data = {}
            for mid, d in st.session_state.score_predictions.items():
                res = "X"
                if d['s1'] > d['s2']: res = "1"
                elif d['s1'] < d['s2']: res = "2"
                formatted_data[mid] = {"score1": d['s1'], "score2": d['s2'], "prediction": res}
            
            saved = batch_save_predictions(user_id, formatted_data, status="concept")
            st.success(f"Gelukt! {saved} wedstrijden opgeslagen.")

    st.divider()

    # 5. De Wedstrijden (Gebruik st.fragment voor snelheid)
    @st.fragment
    def match_item(m_id):
        d = st.session_state.score_predictions[m_id]
        
        st.markdown(f"<div class='match-title'>{d['team1']} - {d['team2']}</div>", unsafe_allow_html=True)
        
        # We gebruiken 6 kolommen: [Minus, Score, Plus] [Minus, Score, Plus]
        # Door onze CSS blijven deze 6 kolommen ALTIJD op één regel.
        cols = st.columns(6)
        
        # Team 1
        if cols[0].button("−", key=f"m1_{m_id}"):
            st.session_state.score_predictions[m_id]['s1'] = max(0, d['s1'] - 1)
            st.rerun(scope="fragment")
        
        cols[1].markdown(f"<div class='score-display'>{d['s1']}</div>", unsafe_allow_html=True)
        
        if cols[2].button("+", key=f"p1_{m_id}"):
            st.session_state.score_predictions[m_id]['s1'] += 1
            st.rerun(scope="fragment")
            
        # Team 2
        if cols[3].button("−", key=f"m2_{m_id}"):
            st.session_state.score_predictions[m_id]['s2'] = max(0, d['s2'] - 1)
            st.rerun(scope="fragment")
            
        cols[4].markdown(f"<div class='score-display'>{d['s2']}</div>", unsafe_allow_html=True)
        
        if cols[5].button("+", key=f"p2_{m_id}"):
            st.session_state.score_predictions[m_id]['s2'] += 1
            st.rerun(scope="fragment")

    # Toon alle wedstrijden
    for m_id in st.session_state.score_predictions.keys():
        match_item(m_id)
