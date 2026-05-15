import streamlit as st
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)

def show_pronostiek_scores(user_id="Tom"):
    # 1. CSS voor mobiele layout (forceert knoppen op 1 regel)
    st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; }
    
    /* Forceer kolommen om naast elkaar te blijven op mobiel */
    div[data-testid="column"] {
        width: auto !important;
        flex-basis: auto !important;
        min-width: 0px !important;
        flex-grow: 1 !important;
    }
    
    .match-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }

    .match-info { font-size: 0.8rem; color: #9ca3af; margin-bottom: 4px; }
    .team-line { font-size: 0.95rem; font-weight: 800; margin-bottom: 10px; }

    .score-box {
        background: #000;
        color: #60a5fa;
        font-size: 1.3rem;
        font-weight: 900;
        text-align: center;
        border-radius: 8px;
        border: 1px solid #1d4ed8;
        padding: 2px 0;
        min-width: 40px;
    }
    
    /* Maak de knoppen vierkant en groot genoeg voor touch */
    .stButton button {
        height: 42px !important;
        width: 42px !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
        padding: 0 !important;
    }
    
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # 2. Data laden
    @st.cache_data(ttl=60)
    def get_cached_data(uid):
        return load_matches(), load_predictions(uid)

    matches_df, predictions_df = get_cached_data(user_id)

    # 3. Session State vullen
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
        
        # Maak een lookup van bestaande voorspellingen
        preds_map = {}
        if not predictions_df.empty:
            for _, p in predictions_df.iterrows():
                preds_map[str(p['match_id'])] = {
                    "s1": int(p.get('score1', 0)),
                    "s2": int(p.get('score2', 0))
                }

        # Vul session state met alle wedstrijden
        for _, m in matches_df.iterrows():
            m_id = str(m['match_id'])
            # Alleen groepsfase filter (optioneel, haal weg als je alles wilt zien)
            if "ronde" in m and "groep" not in str(m['ronde']).lower():
                continue
                
            p_data = preds_map.get(m_id, {"s1": 0, "s2": 0})
            st.session_state.score_predictions[m_id] = {
                "team1": m['team1'],
                "team2": m['team2'],
                "t1_code": m.get('team1_code', ''),
                "t2_code": m.get('team2_code', ''),
                "datum": str(m.get('datum', '')),
                "tijd": str(m.get('tijd', '')),
                "s1": p_data["s1"],
                "s2": p_data["s2"]
            }

    # 4. De "Fragment" functie (Dit zorgt voor de snelheid)
    @st.fragment
    def match_row(m_id):
        data = st.session_state.score_predictions[m_id]
        
        with st.container():
            st.markdown(f"""
            <div class="match-info">{data['datum']} | {data['tijd'][:5]}</div>
            <div class="team-line">{data['team1']} vs {data['team2']}</div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c_gap, c4, c5, c6 = st.columns([1, 1.2, 1, 0.3, 1, 1.2, 1])
            
            with c1:
                if st.button("−", key=f"m1_{m_id}"):
                    st.session_state.score_predictions[m_id]['s1'] = max(0, data['s1'] - 1)
                    st.rerun(scope="fragment") # Ververst alleen deze regel!
            with c2:
                st.markdown(f"<div class='score-box'>{data['s1']}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("+", key=f"p1_{m_id}"):
                    st.session_state.score_predictions[m_id]['s1'] += 1
                    st.rerun(scope="fragment")

            with c_gap: st.write("")

            with c4:
                if st.button("−", key=f"m2_{m_id}"):
                    st.session_state.score_predictions[m_id]['s2'] = max(0, data['s2'] - 1)
                    st.rerun(scope="fragment")
            with c5:
                st.markdown(f"<div class='score-box'>{data['s2']}</div>", unsafe_allow_html=True)
            with c6:
                if st.button("+", key=f"p2_{m_id}"):
                    st.session_state.score_predictions[m_id]['s2'] += 1
                    st.rerun(scope="fragment")
            st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #374151;'>", unsafe_allow_html=True)

    # --- UI WEERGAVE ---
    st.title("🏆 Pronostiek")

    # Top bar knoppen
    col_menu, col_save = st.columns(2)
    with col_menu:
        if st.button("☰ Menu", key="main_menu", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with col_save:
        if st.button("💾 OPSLAAN", type="primary", key="save_btn", use_container_width=True):
            # Formatteer data voor database
            to_save = {}
            for mid, d in st.session_state.score_predictions.items():
                res = "X"
                if d['s1'] > d['s2']: res = "1"
                elif d['s1'] < d['s2']: res = "2"
                to_save[mid] = {"score1": d['s1'], "score2": d['s2'], "prediction": res}
            
            saved = batch_save_predictions(user_id, to_save, status="concept")
            st.success(f"Opgeslagen: {saved} matchen")
            st.cache_data.clear()

    # Loop door de matchen in session state
    if not st.session_state.score_predictions:
        st.warning("Geen wedstrijden gevonden om weer te geven.")
    else:
        for m_id in st.session_state.score_predictions.keys():
            match_row(m_id)
