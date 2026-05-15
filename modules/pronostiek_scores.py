import streamlit as st
import pandas as pd

def show_pronostiek_scores(user_id):
    # 1. DATA LADEN & VOORBEREIDEN
    # Vervang dit door jouw eigen data-ophaal functie
    from modules.data_loader import get_matches, get_predictions 
    
    matches_df = get_matches()
    predictions_df = get_predictions(user_id)
    
    # Maak een map van bestaande voorspellingen
    preds_map = {}
    for _, row in predictions_df.iterrows():
        m_id = str(row.get('match_id', ''))
        if m_id:
            preds_map[m_id] = row

    # 2. CSS VOOR DE LAYOUT (Mobiel proof & nette knoppen)
    st.markdown("""
        <style>
        /* Forceer kolommen om naast elkaar te blijven op mobiel */
        [data-testid="column"] {
            min-width: 0px !important;
            flex-basis: 0 !important;
            flex-grow: 1 !important;
        }
        
        .stHorizontalBlock {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }

        /* Maak de knoppen mooi vierkant */
        div.stButton > button {
            width: 45px !important;
            height: 45px !important;
            padding: 0 !important;
            font-size: 1.5rem !important;
            border-radius: 8px !important;
        }

        /* De score vakjes */
        .score-value {
            background-color: #1e293b;
            border: 1px solid #3b82f6;
            border-radius: 8px;
            color: #60a5fa;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            line-height: 45px;
            height: 45px;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"Pronostiek van {user_id}")

    # 3. DE MATCHES TONEN
    for _, match in matches_df.iterrows():
        m_id = str(match['match_id'])
        
        # Haal score op, met veilige afhandeling voor lege waarden
        p = preds_map.get(m_id, {})
        
        # Initialiseer session state voor deze match als die nog niet bestaat
        if f"s1_{m_id}" not in st.session_state:
            try:
                raw_s1 = p.get('score1', 0)
                st.session_state[f"s1_{m_id}"] = int(float(raw_s1)) if raw_s1 != '' else 0
                
                raw_s2 = p.get('score2', 0)
                st.session_state[f"s2_{m_id}"] = int(float(raw_s2)) if raw_s2 != '' else 0
            except (ValueError, TypeError):
                st.session_state[f"s1_{m_id}"] = 0
                st.session_state[f"s2_{m_id}"] = 0

        st.write(f"**{match['team1']} — {match['team2']}**")
        
        # Gebruik kolommen: [-, score1, +,  spacer,  -, score2, +]
        cols = st.columns([1, 1.5, 1, 0.4, 1, 1.5, 1])
        
        # Team 1 controls
        if cols[0].button("−", key=f"m1_{m_id}"):
            if st.session_state[f"s1_{m_id}"] > 0:
                st.session_state[f"s1_{m_id}"] -= 1
                # Hier kun je direct je opslag-functie aanroepen
        
        cols[1].markdown(f"<div class='score-value'>{st.session_state[f's1_{m_id}']}</div>", unsafe_allow_html=True)
        
        if cols[2].button("+", key=f"p1_{m_id}"):
            st.session_state[f"s1_{m_id}"] += 1

        # Team 2 controls
        if cols[4].button("−", key=f"m2_{m_id}"):
            if st.session_state[f"s2_{m_id}"] > 0:
                st.session_state[f"s2_{m_id}"] -= 1
        
        cols[5].markdown(f"<div class='score-value'>{st.session_state[f's2_{m_id}']}</div>", unsafe_allow_html=True)
        
        if cols[6].button("+", key=f"p2_{m_id}"):
            st.session_state[f"s2_{m_id}"] += 1
            
        st.divider()

    # Optioneel: Een algemene "Opslaan" knop onderaan
    if st.button("Alles Opslaan", width="stretch"):
        # Logica om alle st.session_state[f"s1_{m_id}"] waarden naar je DB te schrijven
        st.success("Scores opgeslagen!")
