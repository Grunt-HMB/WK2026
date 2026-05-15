import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele knoppen naast elkaar
    st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .score-label {
        background: #1e293b; color: #60a5fa; font-size: 1.3rem; font-weight: bold;
        text-align: center; border: 1px solid #3b82f6; border-radius: 6px;
        line-height: 38px; height: 38px; margin: 2px 0;
    }
    .match-header { font-weight: bold; font-size: 1rem; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

    # 2. Data ophalen
    m_df, p_df = load_matches(), load_predictions(user_id)

    # DEBUG: Toon kolommen als het leeg blijft
    if m_df.empty:
        st.error("De database geeft geen wedstrijden terug.")
        return

    # 3. Session State vullen (met kolom-detectie)
    if "score_predictions" not in st.session_state or st.button("🔄 Lijst herladen"):
        st.session_state.score_predictions = {}
        
        # Zoek kolomnamen (sommige DB's gebruiken hoofdletters)
        cols = {c.lower(): c for c in m_df.columns}
        id_col = cols.get('match_id', m_df.columns[0])
        t1_col = cols.get('team1', m_df.columns[1])
        t2_col = cols.get('team2', m_df.columns[2])

        # Bestaande voorspellingen indexeren
        preds = {str(row['match_id']): row for _, row in p_df.iterrows()} if not p_df.empty else {}

        for _, m in m_df.iterrows():
            m_id = str(m[id_col])
            p_match = preds.get(m_id, {})
            st.session_state.score_predictions[m_id] = {
                "t1": m[t1_col],
                "t2": m[t2_col],
                "s1": int(p_match.get('score1', 0)),
                "s2": int(p_match.get('score2', 0))
            }

    # 4. Navigatie & Opslaan
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c2:
        if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
            save_data = {mid: {
                "score1": d['s1'], "score2": d['s2'], 
                "prediction": ("1" if d['s1'] > d['s2'] else "2" if d['s1'] < d['s2'] else "X")
            } for mid, d in st.session_state.score_predictions.items()}
            
            saved = batch_save_predictions(user_id, save_data, status="concept")
            st.success(f"✅ {saved} uitslagen bewaard!")

    st.divider()

    # 5. De Touch-interface
    # We definiëren de rij-functie BUITEN de loop voor stabiliteit
    def render_row(mid):
        d = st.session_state.score_predictions[mid]
        st.markdown(f"<div class='match-header'>{d['t1']} vs {d['t2']}</div>", unsafe_allow_html=True)
        
        # 6 kolommen layout
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        # Team 1
        if c1.button("−", key=f"m1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] = max(0, d['s1'] - 1)
            st.rerun(scope="fragment")
        c2.markdown(f"<div class='score-label'>{d['s1']}</div>", unsafe_allow_html=True)
        if c3.button("+", key=f"p1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] += 1
            st.rerun(scope="fragment")

        # Team 2
        if c4.button("−", key=f"m2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] = max(0, d['s2'] - 1)
            st.rerun(scope="fragment")
        c5.markdown(f"<div class='score-label'>{d['s2']}</div>", unsafe_allow_html=True)
        if c6.button("+", key=f"p2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] += 1
            st.rerun(scope="fragment")
        st.write("") # Extra witregel

    # Toon de rijen
    for mid in st.session_state.score_predictions.keys():
        st.fragment(render_row)(mid)
