import streamlit as st
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # --- HELPERS ---
    def country_flag(code):
        code = str(code or "").strip().upper()
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397) if len(code) == 2 else "⚽"

    # --- CSS VOOR COMPACTE REGELS ---
    st.markdown("""
    <style>
    .block-container { padding: 0 0.5rem !important; max-width: 100% !important; }
    
    /* De Match Container */
    .match-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #111827;
        padding: 8px 10px;
        border-bottom: 1px solid #1f2937;
        gap: 8px;
    }

    /* Datum & Tijd (Links) */
    .time-box {
        font-size: 0.7rem;
        color: #94a3b8;
        min-width: 45px;
        line-height: 1.2;
    }

    /* Teams (Midden - Neemt alle overige ruimte in) */
    .teams-box {
        flex-grow: 1;
        font-size: 0.85rem;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Scorebord (Rechts) */
    .score-ui {
        display: flex;
        align-items: center;
        gap: 4px;
        background: #000;
        padding: 4px 8px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    .score-num {
        font-weight: 900;
        color: #fff;
        width: 18px;
        text-align: center;
    }
    
    .score-dash { color: #475569; font-size: 0.8rem; }
    
    /* Verberg standaard Streamlit elementen */
    div[data-testid="stVerticalBlock"] > div { border: none !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # --- DATA LADEN ---
    # (Houd je bestaande data-laad logica hier)
    matches_df, predictions_df = load_matches(), load_predictions(user_id)
    
    # Gebruik session_state om scores bij te houden
    if "scores" not in st.session_state:
        st.session_state.scores = {str(row['match_id']): {"s1": 0, "s2": 0} for _, row in matches_df.iterrows()}

    # --- TOP BAR ---
    st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True)

    # --- DE LIJST ---
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        s1 = st.session_state.scores[m_id]["s1"]
        s2 = st.session_state.scores[m_id]["s2"]

        # 1. We maken de regel visueel met HTML
        st.markdown(f"""
        <div class="match-row">
            <div class="time-box">
                {match['datum']}<br>{match['tijd'][:5]}
            </div>
            <div class="teams-box">
                {country_flag(match['team1_code'])} {match['team1'][:3]} - {match['team2'][:3]} {country_flag(match['team2_code'])}
            </div>
            <div class="score-ui">
                <div class="score-num">{s1}</div>
                <div class="score-dash">-</div>
                <div class="score-num">{s2}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. We zetten de knoppen in een heel kleine kolom-set direct onder of naast de HTML
        # Om het ECHT op één regel te houden op mobiel, gebruiken we Streamlit's 'popover' 
        # of we zetten kleine knoppen direct in columns met een specifieke breedte.
        
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        with c1: 
            if st.button("H+", key=f"hplus_{m_id}"): 
                st.session_state.scores[m_id]["s1"] += 1
                st.rerun()
        with c2:
            if st.button("H-", key=f"hmin_{m_id}"):
                st.session_state.scores[m_id]["s1"] = max(0, s1-1)
                st.rerun()
        with c3:
            if st.button("U+", key=f"uplus_{m_id}"):
                st.session_state.scores[m_id]["s2"] += 1
                st.rerun()
        with c4:
            if st.button("U-", key=f"umin_{m_id}"):
                st.session_state.scores[m_id]["s2"] = max(0, s2-1)
                st.rerun()
