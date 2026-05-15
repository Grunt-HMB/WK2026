import streamlit as st
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def set_score(match_id, s1, s2):
        match_id = str(match_id)
        s1, s2 = max(0, min(int(s1), 50)), max(0, min(int(s2), 50))
        diff = s1 - s2
        pred = "1" if diff > 0 else ("2" if diff < 0 else "X")
        st.session_state.score_predictions[match_id] = {"prediction": pred, "score1": s1, "score2": s2}
        st.session_state[f"score_pred_{match_id}"] = pred

    if "score_predictions" not in st.session_state: st.session_state.score_predictions = {}
    loaded_key = f"loaded_score_predictions_{user_id}"
    if loaded_key not in st.session_state: st.session_state[loaded_key] = False

    # --- DE COMPACT FIX CSS ---
    st.markdown("""
    <style>
    /* Hoofdpagina marges weg */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }

    /* FORCEER KOLOMMEN NAAST ELKAAR EN LINKS UITGELIJND */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: flex-start !important; /* Zet alles tegen elkaar aan de linkerkant */
        gap: 2px !important;
    }

    /* Maak elke kolom exact zo breed als zijn inhoud */
    [data-testid="column"] {
        width: auto !important;
        min-width: unset !important;
        flex: 0 1 auto !important;
    }

    /* Specifieke breedtes voor de elementen (ongeveer 1 karakter breed) */
    .stButton button {
        min-width: 34px !important;
        width: 34px !important;
        height: 34px !important;
        padding: 0 !important;
        font-weight: 900 !important;
    }

    .score-display {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 4px;
        text-align: center;
        width: 34px;
        height: 34px;
        line-height: 34px;
        font-weight: 900;
        color: white;
    }

    /* 1-X-2 knoppen compact */
    div[data-testid="stSegmentedControl"] { width: auto !important; }
    div[data-testid="stSegmentedControl"] button {
        min-width: 32px !important;
        width: 32px !important;
        padding: 0 !important;
    }

    .match-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 8px;
    }

    .team-text { font-size: 0.85rem; font-weight: 700; margin-bottom: 6px; }
    
    /* Top Menu Fix */
    .top-btns [data-testid="stHorizontalBlock"] { justify-content: space-between !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- Data ---
    m_df, p_df = load_matches(), load_predictions(user_id)
    if not st.session_state[loaded_key]:
        for _, r in p_df.iterrows():
            st.session_state.score_predictions[str(r['match_id'])] = {
                "prediction": str(r['prediction']), "score1": r['score1'], "score2": r['score2']
            }
        st.session_state[loaded_key] = True

    # --- Menu ---
    with st.container(key="top-btns"):
        c1, c2 = st.columns(2)
        c1.button("☰ Menu", use_container_width=True, on_click=lambda: st.session_state.update({"main_page": "🏠 Hoofdmenu"}))
        if c2.button("💾 OPSLAAN", type="primary", use_container_width=True):
            batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
            st.toast("Opgeslagen!")

    # --- Wedstrijden ---
    for _, match in m_df.iterrows():
        mid = str(match["match_id"])
        ensure_data = st.session_state.score_predictions.setdefault(mid, {"prediction": "X", "score1": 0, "score2": 0})
        
        s1, s2 = ensure_data["score1"], ensure_data["score2"]

        with st.container():
            st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-text">{country_flag(match.get("team1_code"))} {match["team1"]} vs {match["team2"]}</div>', unsafe_allow_html=True)

            # 7 kolommen, allemaal 'auto' breedte
            cols = st.columns([1, 1, 1, 1, 1, 1, 1])
            
            with cols[0]:
                st.segmented_control("P", ["1", "X", "2"], key=f"p_{mid}", label_visibility="collapsed")
            
            # Team 1
            with cols[1]:
                if st.button("−", key=f"m1_{mid}"): set_score(mid, s1-1, s2); st.rerun()
            with cols[2]:
                st.markdown(f'<div class="score-display">{s1}</div>', unsafe_allow_html=True)
            with cols[3]:
                if st.button("+", key=f"p1_{mid}"): set_score(mid, s1+1, s2); st.rerun()

            # Team 2
            with cols[4]:
                if st.button("−", key=f"m2_{mid}"): set_score(mid, s1, s2-1); st.rerun()
            with cols[5]:
                st.markdown(f'<div class="score-display">{s2}</div>', unsafe_allow_html=True)
            with cols[6]:
                if st.button("+", key=f"p2_{mid}"): set_score(mid, s1, s2+1); st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)
