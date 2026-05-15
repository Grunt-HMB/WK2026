import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele knoppen naast elkaar (Touch-vriendelijk)
    st.markdown("""
    <style>
    [data-testid="column"] { flex: 1 1 0% !important; min-width: 0px !important; }
    .score-label {
        background: #1e293b; color: #60a5fa; font-size: 1.3rem; font-weight: bold;
        text-align: center; border: 1px solid #3b82f6; border-radius: 6px;
        line-height: 40px; height: 40px; margin: 2px 0;
    }
    .match-header { font-weight: bold; font-size: 1rem; margin-top: 15px; color: white; }
    hr { margin: 10px 0 !important; border-top: 1px solid #334155 !important; }
    </style>
    """, unsafe_allow_html=True)

    # Helper om veilig getallen te verwerken
    def safe_int(val):
        try:
            if val is None or val == "": return 0
            return int(float(val))
        except: return 0

    # 2. Data laden (Precies zoals in je werkende versie)
    @st.cache_data(ttl=60)
    def get_raw_data(uid):
        m = load_matches()
        p = load_predictions(uid)
        # Filter op groepsfase (als kolom bestaat)
        if "ronde" in m.columns:
            m = m[m["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
        return m, p

    matches_df, predictions_df = get_raw_data(user_id)

    # 3. Initialiseer Session State als deze nog niet bestaat
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
        
        # Maak een map van bestaande voorspellingen
        preds_map = predictions_df.set_index('match_id').to_dict('index') if not predictions_df.empty else {}

        for _, row in matches_df.iterrows():
            m_id = str(row['match_id'])
            p = preds_map.get(m_id if m_id in preds_map else int(m_id) if m_id.isdigit() else m_id, {})
            
            st.session_state.score_predictions[m_id] = {
                "t1": row['team1'],
                "t2": row['team2'],
                "s1": safe_int(p.get('score1', 0)),
                "s2": safe_int(p.get('score2', 0))
            }

    # 4. Navigatie & Opslaan
    st.title("🏆 Je Pronostiek")
    
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("🏠 Menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c_nav2:
        if st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True):
            final_data = {}
            for mid, d in st.session_state.score_predictions.items():
                s1, s2 = d['s1'], d['s2']
                res = "1" if s1 > s2 else "2" if s1 < s2 else "X"
                final_data[mid] = {"score1": s1, "score2": s2, "prediction": res}
            
            saved = batch_save_predictions(user_id, final_data, status="concept")
            st.success(f"✅ {saved} uitslagen opgeslagen!")
            st.cache_data.clear()

    st.divider()

    # 5. De wedstrijd rijen (met st.fragment voor snelheid)
    @st.fragment
    def render_match(mid):
        # We halen de data direct uit de session_state
        d = st.session_state.score_predictions[mid]
        
        st.markdown(f"<div class='match-header'>{d['t1']} vs {d['t2']}</div>", unsafe_allow_html=True)
        
        # 6 kolommen: [-] [score] [+]   [-] [score] [+]
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        # Team 1 (Huis)
        if c1.button("−", key=f"m1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] = max(0, d['s1'] - 1)
            st.rerun(scope="fragment")
        c2.markdown(f"<div class='score-label'>{d['s1']}</div>", unsafe_allow_html=True)
        if c3.button("+", key=f"p1_{mid}"):
            st.session_state.score_predictions[mid]['s1'] += 1
            st.rerun(scope="fragment")

        # Team 2 (Uit)
        if c4.button("−", key=f"m2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] = max(0, d['s2'] - 1)
            st.rerun(scope="fragment")
        c5.markdown(f"<div class='score-label'>{d['s2']}</div>", unsafe_allow_html=True)
        if c6.button("+", key=f"p2_{mid}"):
            st.session_state.score_predictions[mid]['s2'] += 1
            st.rerun(scope="fragment")
        
        st.markdown("<hr>", unsafe_allow_html=True)

    # Toon alle wedstrijden uit de session state
    if not st.session_state.score_predictions:
        st.warning("Geen wedstrijden gevonden. Druk op Menu en kom terug.")
    else:
        for m_id in st.session_state.score_predictions.keys():
            render_match(m_id)
