import streamlit as st
from modules.data_loader import get_matches

def show_pronostiek_scores(user_id):
    st.title("⚽ Mijn Pronostiek")
    
    df = get_matches()

    # Filter op Speeldag (1, 2 of 3) om de lijst behapbaar te houden op mobiel
    speeldagen = sorted(df['speeldag'].unique())
    gekozen_dag = st.select_slider("Selecteer Speeldag", options=speeldagen)
    
    filtered_df = df[df['speeldag'] == gekozen_dag]

    st.subheader(f"Speeldag {gekozen_dag}")

    for _, match in filtered_df.iterrows():
        with st.container(border=True):
            # Header met Groep en Tijd
            st.caption(f"Groep {match['groep']} • {match['datum']} • {match['tijd']}")
            
            # Kolommen: Team 1 | Score Inputs | Team 2
            col1, col_score, col2 = st.columns([4, 3, 4])
            
            with col1:
                st.markdown(f"**{match['team1']}**")
                st.caption(match['team1_code'])
            
            with col_score:
                # Twee invoervelden naast elkaar voor de score
                s1, s2 = st.columns(2)
                with s1:
                    st.number_input("T1", min_value=0, max_value=15, step=1, 
                                    key=f"in1_{match['match_id']}", label_visibility="collapsed")
                with s2:
                    st.number_input("T2", min_value=0, max_value=15, step=1, 
                                    key=f"in2_{match['match_id']}", label_visibility="collapsed")
            
            with col2:
                # Rechts uitlijnen voor het tweede team
                st.markdown(f"<div style='text-align: right;'><b>{match['team2']}</b></div>", unsafe_content_allowed=True)
                st.markdown(f"<div style='text-align: right; color: gray; font-size: 0.8em;'>{match['team2_code']}</div>", unsafe_content_allowed=True)

    if st.button("Opslaan", use_container_width=True, type="primary"):
        st.success("Scores voor deze speeldag zijn verwerkt!")
