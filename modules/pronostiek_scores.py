import streamlit as st
import pandas as pd

def show_pronostiek_scores(user_id):
    # 1. Importeer data_loader functies binnen de functie
    from modules.data_loader import get_matches, get_predictions, update_prediction

    # 2. Haal data op en controleer of matches_df bestaat (Oplossing voor NameError)
    matches_df = get_matches()
    if matches_df is None or matches_df.empty:
        st.error("Kon de wedstrijden niet laden.")
        return

    predictions_df = get_predictions(user_id)

    # 3. CSS voor de knoppen
    st.markdown("""
        <style>
        div.stButton > button { width: 45px !important; height: 45px !important; padding: 0 !important; font-size: 1.5rem !important; }
        .score-value { background-color: #1e293b; border-radius: 8px; color: #60a5fa; font-size: 22px; font-weight: bold; text-align: center; line-height: 45px; height: 45px; }
        </style>
    """, unsafe_allow_html=True)

    # 4. Maak een kaart van bestaande voorspellingen (Oplossing voor ValueError)
    preds_map = {}
    if not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            m_id = str(row.get('match_id', '')).strip()
            if m_id:
                # Veilig omzetten naar int, vervang leeg door 0
                try:
                    s1 = int(float(row.get('score1', 0))) if row.get('score1') not in [None, ''] else 0
                    s2 = int(float(row.get('score2', 0))) if row.get('score2') not in [None, ''] else 0
                except:
                    s1, s2 = 0, 0
                preds_map[m_id] = {'score1': s1, 'score2': s2}

    st.title("⚽ Jouw Voorspellingen")

    # 5. De Loop door de wedstrijden
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id']).strip()
        p = preds_map.get(m_id, {'score1': 0, 'score2': 0})

        # Gebruik session_state om waarden vast te houden
        if f"s1_{m_id}" not in st.session_state:
            st.session_state[f"s1_{m_id}"] = p['score1']
        if f"s2_{m_id}" not in st.session_state:
            st.session_state[f"s2_{m_id}"] = p['score2']

        st.write(f"**{match['team1']} — {match['team2']}**")
        
        cols = st.columns([1, 1.5, 1, 0.5, 1, 1.5, 1])
        
        # Team 1
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

        # Team 2
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
