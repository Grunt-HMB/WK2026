import streamlit as st
import pandas as pd
from modules.data_loader import get_matches

def show_pronostiek_scores(user_id):
    st.title("🏆 WK 2026")
    
    # Haal de 72 matches op
    matches_df = get_matches()

    # Gebruik een selectbox voor de speeldag of groep om de lijst kort te houden
    st.sidebar.header("Filters")
    speeldag = st.sidebar.selectbox("Selecteer Speeldag", sorted(matches_df['speeldag'].unique()))
    
    # Filter de data
    filtered_df = matches_df[matches_df['speeldag'] == speeldag]

    st.subheader(f"Speeldag {speeldag}")

    # Loop door de gefilterde wedstrijden
    for _, match in filtered_df.iterrows():
        draw_match_card(match)

def draw_match_card(match):
    """Tekent een compacte kaart die op mobiel goed schaalt."""
    with st.container(border=True):
        # Header: Tijd en Groep
        st.caption(f"📅 {match['datum']} - {match['tijd']} | Groep {match['groep']}")
        
        # We gebruiken hier maar 3 kolommen: Team 1 | Input | Team 2
        # Dit blijft op mobiel redelijk stabiel
        c1, c2, c3 = st.columns([3, 2, 3])
        
        with c1:
            st.markdown(f"**{match['team1']}**")
            st.caption(match['team1_code'])
        
        with c2:
            # Compacte input velden naast elkaar
            i1, i2 = st.columns(2)
            with i1:
                st.text_input("1", label_visibility="collapsed", key=f"t1_{match['match_id']}", value="0")
            with i2:
                st.text_input("2", label_visibility="collapsed", key=f"t2_{match['match_id']}", value="0")
        
        with c3:
            # Rechts uitlijnen voor team 2
            st.markdown(f"<div style='text-align: right;'><b>{match['team2']}</b></div>", unsafe_content_allowed=True)
            st.markdown(f"<div style='text-align: right; color: gray;'>{match['team2_code']}</div>", unsafe_content_allowed=True)

        # Optioneel: een kleine 'Opslaan' knop per wedstrijd of één grote onderaan
