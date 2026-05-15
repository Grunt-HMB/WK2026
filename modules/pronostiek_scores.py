import streamlit as st

# Veilig de data_loader importeren
try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches

def show_pronostiek_scores(user_id):
    # Forceer user_id naar string voor de zekerheid
    naam = str(user_id)
    st.subheader(f"🏟️ Pronostiek voor {naam}")
    
    df = get_matches()
    if df.empty:
        st.error("Geen wedstrijden kunnen laden.")
        return

    # Filter per speeldag (1, 2 of 3)
    dagen = sorted(df['speeldag'].unique())
    gekozen_dag = st.select_slider("Kies Speeldag", options=dagen)
    
    dag_df = df[df['speeldag'] == gekozen_dag]

    # Toon elke wedstrijd
    for _, match in dag_df.iterrows():
        draw_match_card(match)

def draw_match_card(match):
    # STAP 1: Alle data dwingen naar strings (voorkomt TypeErrors in Python 3.14)
    m_id = str(match.get('match_id', '0'))
    t1 = str(match.get('team1', 'Team 1'))
    t2 = str(match.get('team2', 'Team 2'))
    c1 = str(match.get('team1_code', '??'))
    c2 = str(match.get('team2_code', '??'))
    tijd = str(match.get('tijd', '00:00'))
    groep = str(match.get('groep', '-'))

    with st.container(border=True):
        # Bovenste regel: info
        st.caption(f"Groep {groep} • {tijd}")
        
        # Drie kolommen: Team links | Scores | Team rechts
        col_links, col_midden, col_rechts = st.columns([4, 3, 4])
        
        with col_links:
            st.write(f"**{t1}**")
            st.caption(c1)
            
        with col_midden:
            # Score-invoer
            s1, s2 = st.columns(2)
            with s1:
                st.number_input("T1", 0, 15, 0, 1, key=f"s1_{m_id}", label_visibility="collapsed")
            with s2:
                st.number_input("T2", 0, 15, 0, 1, key=f"s2_{m_id}", label_visibility="collapsed")
            
        with col_rechts:
            # GEEN HTML MEER: Gewone Streamlit markdown met uitlijning
            # Dit is de veiligste methode tegen TypeErrors
            st.markdown(f"<p style='text-align:right; margin:0;'><b>{t2}</b></p>", unsafe_content_allowed=True)
            st.markdown(f"<p style='text-align:right; margin:0; color:gray; font-size:0.8em;'>{c2}</p>", unsafe_content_allowed=True)

    # Ruimte tussen de kaarten
    st.write("")
