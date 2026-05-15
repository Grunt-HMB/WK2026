import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- CALLBACK (Houdt de snelheid erin) ---
    def change_score(m_id, team, delta):
        m_id = str(m_id)
        f = f"score{team}"
        st.session_state.score_predictions[m_id][f] = max(0, st.session_state.score_predictions[m_id][f] + delta)
        
        # Bereken direct resultaat
        s1 = st.session_state.score_predictions[m_id]["score1"]
        s2 = st.session_state.score_predictions[m_id]["score2"]
        st.session_state.score_predictions[m_id]["prediction"] = "1" if s1 > s2 else ("2" if s2 > s1 else "X")

    # --- CSS VOOR EXTREEM COMPACTE LAYOUT ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    /* Vaste Top Bar */
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 70px; }

    /* Wedstrijd Rij */
    .match-row {
        background: #1a202c;
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 5px;
        border: 1px solid #2d3748;
    }
    
    .team-label { font-size: 0.85rem; font-weight: 600; color: white; }
    .match-meta { font-size: 0.65rem; color: #718096; margin-bottom: 2px; }

    /* Forceer knoppen horizontaal op 1 regel */
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        gap: 4px !important;
    }

    /* Maak de knoppen HEEL klein */
    button[kind="secondary"] {
        min-width: 30px !important;
        width: 30px !important;
        height: 30px !important;
        padding: 0 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }
    
    /* Score display tekst */
    .score-num {
        font-size: 1.2rem;
        font-weight: bold;
        min-width: 20px;
        text-align: center;
        color: #63b3ed;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- DATA INITIALISATIE ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    if f"loaded_{user_id}" not in st.session_state:
        try:
            db_preds = load_predictions(user_id)
            for _, row in db_preds.iterrows():
                st.session_state.score_predictions[str(row['match_id'])] = {
                    "prediction": row['prediction'], "score1": int(row['score1']), "score2": int(row['score2'])
                }
            st.session_state[f"loaded_{user_id}"] = True
        except: pass

    # --- TOP BAR ---
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
                batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.toast("✅ Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # Speeldag selectie heel compact
    sd = st.radio("Speeldag", ["1", "2", "3"], horizontal=True, label_visibility="collapsed")
    
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        d = st.session_state.score_predictions[m_id]

        # De volledige wedstrijd-unit
        with st.container():
            st.markdown(f"""
            <div class="match-row">
                <div class="match-meta">{m['datum']} • {m['tijd']}</div>
                <div class="team-label">{m['team1']} - {m['team2']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Eén enkele rij voor ALLE knoppen (geen losse kolommen meer per team)
            # Dit dwingt alles op 1 regel op mobiel
            ctrl = st.columns(1)[0]
            with ctrl:
                st.button("−", key=f"m1_{m_id}", on_click=change_score, args=(m_id, 1, -1))
                st.markdown(f"<span class='score-num'>{d['score1']}</span>", unsafe_allow_html=True)
                st.button("+", key=f"p1_{m_id}", on_click=change_score, args=(m_id, 1, 1))
                
                st.markdown("<span style='margin: 0 10px; font-weight: bold;'>vs</span>", unsafe_allow_html=True)
                
                st.button("−", key=f"m2_{m_id}", on_click=change_score, args=(m_id, 2, -1))
                st.markdown(f"<span class='score-num'>{d['score2']}</span>", unsafe_allow_html=True)
                st.button("+", key=f"p2_{m_id}", on_click=change_score, args=(m_id, 2, 1))
                
                # De voorspelling (1, X of 2) tonen we heel klein aan het einde
                res_color = "#48bb78" if d['prediction'] != "X" else "#ecc94b"
                st.markdown(f"<span style='color:{res_color}; font-weight:bold; margin-left:10px;'>{d['prediction']}</span>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
