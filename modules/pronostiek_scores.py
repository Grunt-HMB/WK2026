import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. Krachtige CSS voor een strakke mobiele weergave
    st.markdown("""
    <style>
    /* Forceer knoppen en scores op één regel, ook op mobiel */
    .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .score-unit {
        display: flex;
        align-items: center;
        gap: 5px;
        flex: 1;
    }
    .score-display {
        background: #1e293b;
        color: #60a5fa;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        min-width: 50px;
        height: 45px;
        line-height: 45px;
    }
    .vs-label { font-weight: bold; color: #94a3b8; font-size: 1.2rem; }
    .match-title { font-weight: bold; font-size: 1.1rem; color: white; margin-bottom: 8px; }
    
    /* Maak Streamlit knoppen vierkant/compact voor de +/- */
    div.stButton > button {
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        font-size: 1.5rem !important;
    }
    /* De grote actieknoppen bovenaan */
    .action-btn button {
        width: 100% !important;
        height: auto !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Veilige conversie om 'ValueError: invalid literal for int() with base 10: ''' te voorkomen
    def safe_int(val):
        if val is None or str(val).strip() == "":
            return 0
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return 0

    # 2. Data laden met cache
    @st.cache_data(ttl=10)
    def get_data(uid):
        m = load_matches()
        p = load_predictions(uid)
        # Filter op groepsfase indien nodig
        if not m.empty and "ronde" in m.columns:
            m = m[m["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
        return m, p

    matches_df, predictions_df = get_data(user_id)

    # 3. Initialiseer Session State (eenmalig per login)
    if "temp_scores" not in st.session_state:
        st.session_state.temp_scores = {}
        preds_map = predictions_df.set_index('match_id').to_dict('index') if not predictions_df.empty else {}
        
        for _, row in matches_df.iterrows():
            m_id = str(row['match_id'])
            p = preds_map.get(m_id) or preds_map.get(safe_int(m_id)) or {}
            st.session_state.temp_scores[m_id] = {
                "s1": safe_int(p.get('score1', 0)),
                "s2": safe_int(p.get('score2', 0))
            }

    # 4. Header & Navigatie
    st.title("🏆 Je Pronostiek")
    
    c_nav, c_save = st.columns(2)
    with c_nav:
        if st.button("🏠 Menu", key="btn_home", use_container_width=True):
            st.session_state.main_page = "🏠 Hoofdmenu"
            st.rerun()
    with c_save:
        if st.button("💾 OPSLAAN", type="primary", key="btn_save", use_container_width=True):
            final_data = {}
            for mid, s in st.session_state.temp_scores.items():
                res = "1" if s["s1"] > s["s2"] else "2" if s["s1"] < s["s2"] else "X"
                final_data[mid] = {"score1": s["s1"], "score2": s["s2"], "prediction": res}
            
            if batch_save_predictions(user_id, final_data, status="concept"):
                st.success("✅ Opgeslagen!")
                st.cache_data.clear()
            else:
                st.error("Opslaan mislukt.")

    st.divider()

    # 5. Wedstrijd Matrix
    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        if m_id not in st.session_state.temp_scores:
            st.session_state.temp_scores[m_id] = {"s1": 0, "s2": 0}
            
        scores = st.session_state.temp_scores[m_id]

        st.markdown(f"<div class='match-title'>{match['team1']} vs {match['team2']}</div>", unsafe_allow_html=True)
        
        # Gebruik kolommen maar hou ze heel smal om stapelen te voorkomen
        col1, col_vs, col2 = st.columns([1, 0.2, 1])
        
        with col1: # Team 1 controls
            sub1, sub2, sub3 = st.columns([1, 1.5, 1])
            if sub1.button("−", key=f"m1_{m_id}"):
                st.session_state.temp_scores[m_id]["s1"] = max(0, scores["s1"] - 1)
                st.rerun()
            sub2.markdown(f"<div class='score-display'>{scores['s1']}</div>", unsafe_allow_html=True)
            if sub3.button("+", key=f"p1_{m_id}"):
                st.session_state.temp_scores[m_id]["s1"] += 1
                st.rerun()

        with col_vs:
            st.markdown("<div style='text-align:center; line-height:45px;' class='vs-label'>-</div>", unsafe_allow_html=True)

        with col2: # Team 2 controls
            sub4, sub5, sub6 = st.columns([1, 1.5, 1])
            if sub4.button("−", key=f"m2_{m_id}"):
                st.session_state.temp_scores[m_id]["s2"] = max(0, scores["s2"] - 1)
                st.rerun()
            sub5.markdown(f"<div class='score-display'>{scores['s2']}</div>", unsafe_allow_html=True)
            if sub6.button("+", key=f"p2_{m_id}"):
                st.session_state.temp_scores[m_id]["s2"] += 1
                st.rerun()
        
        st.markdown("<div style='margin-bottom:25px;'></div>", unsafe_allow_html=True)
