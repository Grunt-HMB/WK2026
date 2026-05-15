import streamlit as st

def show_pronostiek_scores(user_id="Tom"):
    # CSS om te voorkomen dat kleine kolommen stapelen op mobiel
    st.markdown("""
        <style>
        /* Target de specifieke kolom-container van Streamlit */
        [data-testid="column"] {
            min-width: 0px !important;
        }
        
        /* Forceer horizontale layout voor de score-sectie */
        @media (max-width: 640px) {
            .stHorizontalBlock {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                align-items: center !important;
            }
        }

        /* Stijl voor de score vakjes */
        .score-box {
            background-color: #1e293b;
            border: 1px solid #3b82f6;
            border-radius: 5px;
            color: #60a5fa;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            padding: 5px 0;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # ... (rest van je data laad logica) ...

    # Voorbeeld van de verbeterde rij-opbouw:
    for _, match in matches_df.iterrows():
        st.write(f"**{match['team1']} vs {match['team2']}**")
        
        # We gebruiken 7 kolommen: [-, score1, +,  ruimte,  -, score2, +]
        cols = st.columns([1, 2, 1, 0.5, 1, 2, 1])
        
        # Team 1
        if cols[0].button("−", key=f"m1_{match['match_id']}"):
            update_score(match['match_id'], "s1", -1)
        
        cols[1].markdown(f"<div class='score-box'>{score1}</div>", unsafe_allow_html=True)
        
        if cols[2].button("+", key=f"p1_{match['match_id']}"):
            update_score(match['match_id'], "s1", 1)
            
        # Middelste kolom is leeg (spacer)
        
        # Team 2
        if cols[4].button("−", key=f"m2_{match['match_id']}"):
            update_score(match['match_id'], "s2", -1)
            
        cols[5].markdown(f"<div class='score-box'>{score2}</div>", unsafe_allow_html=True)
        
        if cols[6].button("+", key=f"p2_{match['match_id']}"):
            update_score(match['match_id'], "s2", 1)
        
        st.divider()
