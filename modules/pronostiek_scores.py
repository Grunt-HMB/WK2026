import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    # --- CALLBACK (Directe verwerking) ---
    def change_score(m_id, team, delta):
        m_id = str(m_id)
        f = f"score{team}"
        st.session_state.score_predictions[m_id][f] = max(0, st.session_state.score_predictions[m_id][f] + delta)
        
        s1 = st.session_state.score_predictions[m_id]["score1"]
        s2 = st.session_state.score_predictions[m_id]["score2"]
        st.session_state.score_predictions[m_id]["prediction"] = "1" if s1 > s2 else ("2" if s2 > s1 else "X")

    # --- CSS VOOR ONWRIGBARE HORIZONTALE LAYOUT ---
    st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 10px; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 70px; }

    /* De Container voor de hele match */
    .match-box {
        background: #1a202c;
        border-radius: 10px;
        padding: 8px;
        margin-bottom: 12px;
        border: 1px solid #2d3748;
    }

    .match-header {
        font-size: 0.85rem;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-bottom: 8px;
    }

    /* Dwing alles op één regel met Flexbox */
    .flex-row {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-evenly !important;
        width: 100% !important;
    }

    /* Maak Streamlit knoppen extreem klein en forceer breedte */
    div.stButton > button {
        width: 35px !important;
        height: 35px !important;
        min-width: 35px !important;
        padding: 0 !important;
        font-size: 18px !important;
        border-radius: 5px !important;
    }

    .score-val {
        font-size: 1.3rem;
        font-weight: 900;
        color: #63b3ed;
        margin: 0 5px;
    }

    .vs-text {
        font-size: 0.7rem;
        color: #718096;
        font-weight: bold;
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

    sd = st.select_slider("Selecteer Speeldag", options=["1", "2", "3"], value="1")
    
    matches = [m for m in HARDCODED_MATCHES if str(m["speeldag"]) == sd]

    for m in matches:
        m_id = str(m["match_id"])
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        d = st.session_state.score_predictions[m_id]

        # MATCH KAARTJE
        st.markdown(f"""
        <div class="match-box">
            <div class="match-header">{country_flag(m['team1_code'])} {m['team1']} - {m['team2']} {country_flag(m['team2_code'])}</div>
        </div>
        """, unsafe_allow_html=True)

        # DE REGELEENHEID (We gebruiken één kolom die we via CSS dwingen horizontaal te zijn)
        # GEEN aparte st.columns meer per element!
        with st.container():
            st.markdown('<div class="flex-row">', unsafe_allow_html=True)
            
            # Team 1 Controls
            col1, col2, col3, col_vs, col4, col5, col6 = st.columns([1,1,1,0.5,1,1,1])
            
            with col1: st.button("−", key=f"m1_{m_id}", on_click=change_score, args=(m_id, 1, -1))
            with col2: st.markdown(f"<div class='score-val'>{d['score1']}</div>", unsafe_allow_html=True)
            with col3: st.button("+", key=f"p1_{m_id}", on_click=change_score, args=(m_id, 1, 1))
            
            with col_vs: st.markdown("<div class='vs-text'>VS</div>", unsafe_allow_html=True)
            
            with col4: st.button("−", key=f"m2_{m_id}", on_click=change_score, args=(m_id, 2, -1))
            with col5: st.markdown(f"<div class='score-val'>{d['score2']}</div>", unsafe_allow_html=True)
            with col6: st.button("+", key=f"p2_{m_id}", on_click=change_score, args=(m_id, 2, 1))

            st.markdown('</div>', unsafe_allow_html=True)

        res_color = "#48bb78" if d['prediction'] != "X" else "#ecc94b"
        st.markdown(f"<div style='text-align:center; font-size:0.8rem; font-weight:bold; color:{res_color}; margin-bottom:15px;'>Voorspelling: {d['prediction']}</div>", unsafe_allow_html=True)
        st.divider()

    st.markdown("<br><br>", unsafe_allow_html=True)

def country_flag(code):
    code = str(code or "").strip().upper()
    if len(code) != 2: return "⚽"
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)
