import streamlit as st
import pandas as pd

def show_pronostiek_scores(user_id):
    # 1. DATA LADEN (Oplossing voor NameError)
    from modules.data_loader import get_matches, get_predictions, update_prediction
    
    matches_df = get_matches()
    predictions_df = get_predictions(user_id)
    
    # Maak een map van bestaande voorspellingen
    preds_map = {}
    for _, row in predictions_df.iterrows():
        m_id = str(row.get('match_id', ''))
        if m_id:
            preds_map[m_id] = row

    # 2. CSS LAYOUT (Geen wijzigingen nodig, maar hier voor de volledigheid)
    st.markdown("""
        <style>
        [data-testid="column"] { min-width: 0px !important; flex-basis: 0 !important; flex-grow: 1 !important; }
        .stHorizontalBlock { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; gap: 0.5rem !important; }
        div.stButton > button { width: 45px !important; height: 45px !important; padding: 0 !important; font-size: 1.5rem !important; border-radius: 8px !important; }
        .score-value { background-color: #1e293b; border: 1px solid #3b82f6; border-radius: 8px; color: #60a5fa; font-size: 22px; font-weight: bold; text-align: center; line-height: 45px; height: 45px; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    st.title("⚽ Jouw Voorspellingen")

    # 3. MATCHES LOOP
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        p = preds_map.get(m_id, {})

        # Veilige conversie van score (Oplossing voor ValueError / int('') crash)
        def safe_int(val):
            try:
                if val is None or str(val).strip() == "":
                    return 0
                return int(float(val))
            except (ValueError, TypeError):
                return 0

        # Initialiseer session state als het leeg is
        if f"s1_{m_id}" not in st.session_state:
            st.session_state[f"s1_{m_id}"] = safe_int(p.get('score1', 0))
        if f"s2_{m_id}" not in st.session_state:
            st.session_state[f"s2_{m_id}"] = safe_int(p.get('score2', 0))

        st.write(f"**{match['team1']} — {match['team2']}**")
        
        # Gebruik kolommen (Oplossing voor UI verspringen op mobiel)
        cols = st.columns([1, 1.5, 1, 0.3, 1, 1.5, 1])
        
        # Team 1 Controls
        if cols[0].button("−", key=f"min1_{m_id}"):
            if st.session_state[f"s1_{m_id}"] > 0:
                st.session_state[f"s1_{m_id}"] -= 1
                update_prediction(user_id, m_id, st.session_state[f"s1_{m_id}"], st.session_state[f"s2_{m_id}"])
                st.rerun()

        cols[1].markdown(f"<div class='score-value'>{st.session_state[f's1_{m_id}']}</div>", unsafe_allow_html=True)

        if cols[2].button("+", key=f"plus1_{m_id}"):
            st.session_state[f"s1_{m_id}"] += 1
            update_prediction(user_id, m_id, st.session_state[f"s1_{m_id}"], st.session_state[f"s2_{m_id}"])
            st.rerun()

        # Team 2 Controls
        if cols[4].button("−", key=f"min2_{m_id}"):
            if st.session_state[f"s2_{m_id}"] > 0:
                st.session_state[f"s2_{m_id}"] -= 1
                update_prediction(user_id, m_id, st.session_state[f"s1_{m_id}"], st.session_state[f"s2_{m_id}"])
                st.rerun()

        cols[5].markdown(f"<div class='score-value'>{st.session_state[f's2_{m_id}']}</div>", unsafe_allow_html=True)

        if cols[6].button("+", key=f"plus2_{m_id}"):
            st.session_state[f"s2_{m_id}"] += 1
            update_prediction(user_id, m_id, st.session_state[f"s1_{m_id}"], st.session_state[f"s2_{m_id}"])
            st.rerun()
            
        st.divider()
