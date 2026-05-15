import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele breedte en score-vakjes
    st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .score-label {
        background: #0e1117; color: #3b82f6; font-size: 1.2rem; font-weight: bold;
        text-align: center; border: 2px solid #3b82f6; border-radius: 8px;
        line-height: 40px; height: 40px; margin: 2px 0;
    }
    .match-row { margin-top: 15px; border-top: 1px solid #334155; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

    # 2. Data laden
    m_df, p_df = load_matches(), load_predictions(user_id)

    # --- DEBUG SECTIE (Haal dit weg als het werkt) ---
    if m_df.empty:
        st.error("❌ De database gaf geen wedstrijden terug. Check je 'matches' tabel.")
        return
    # ------------------------------------------------

    # 3. Session State vullen
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
        
        # Maak lookup van bestaande voorspellingen
        preds = {str(row['match_id']): row for _, row in p_df.iterrows()} if not p_df.empty else {}

        for _, m in m_df.iterrows():
            m_id = str(m['match_id'])
            p_match = preds.get(m_id, {})
            st.session_state.score_predictions[m_id] = {
                "t1": m.get('team1', 'Team A'),
                "t2": m.get('team2', 'Team B'),
                "s1": int(p_match.get('score1', 0)),
                "s2": int(p_match.get('score2', 0))
            }

    # 4. Navigatie
    c1, c2 = st.columns(2)
    with c1:
        if st.button("☰ Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c2:
        if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
            data = {mid: {"score1": d['s1'], "score2": d['s2'], 
                    "prediction": ("1" if d['s1'] > d['s2'] else "2" if d['s1'] < d['s2'] else "X")} 
                    for mid, d in st.session_state.score_predictions.items()}
            saved = batch_save_predictions(user_id, data, status="concept")
            st.success(f"✅ {saved} uitslagen opgeslagen!")

    st.write(f"Aantal wedstrijden geladen: {len(st.session_state.score_predictions)}")

    # 5. Wedstrijden tonen met fragmenten voor snelheid
    def render_row(mid):
        # We maken een lokale referentie naar de data
        d = st.session_state.score_predictions[mid]
        
        st.markdown(f"**{d['t1']} vs {d['t2']}**")
        
        # 6 kolommen: [-][Score][+]  [-][Score][+]
        cols = st.columns(6)
        
        # Team 1
        if cols[0].button("−", key=f"m1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] = max(0, d['s1'] - 1)
            st.rerun(scope="fragment")
        cols[1].markdown(f"<div class='score-label'>{d['s1']}</div>", unsafe_allow_html=True)
        if cols[2].button("+", key=f"p1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] += 1
            st.rerun(scope="fragment")

        # Team 2
        if cols[3].button("−", key=f"m2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] = max(0, d['s2'] - 1)
            st.rerun(scope="fragment")
        cols[4].markdown(f"<div class='score-label'>{d['s2']}</div>", unsafe_allow_html=True)
        if cols[5].button("+", key=f"p2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] += 1
            st.rerun(scope="fragment")

    # Maak per wedstrijd een fragment aan
    for mid in st.session_state.score_predictions.keys():
        with st.container():
            # Gebruik st.fragment om te zorgen dat alleen dit deel ververst
            st.fragment(render_row)(mid)
