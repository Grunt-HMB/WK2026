import streamlit as st
# Let op: de import moet overeenkomen met je mappenstructuur
try:
    from modules.data_loader import get_matches
except:
    from data_loader import get_matches

def show_pronostiek_scores(user_id):
    st.markdown(f"### ⚽ Pronostiek voor {user_id}")
    
    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijdgegevens gevonden.")
        return

    # Gebruik een slider om door de 72 wedstrijden te navigeren (mobiel vriendelijk)
    speeldagen = sorted(df['speeldag'].unique())
    gekozen_dag = st.select_slider("Selecteer Speeldag", options=speeldagen)
    
    filtered_df = df[df['speeldag'] == gekozen_dag]

    for _, match in filtered_df.iterrows():
        draw_match_card(match)

def draw_match_card(match):
    # Haal waarden veilig op om de TypeError uit je screenshot te voorkomen
    m_id = match.get('match_id', 0)
    t1 = match.get('team1', 'Onbekend')
    t2 = match.get('team2', 'Onbekend')
    c1 = match.get('team1_code', '??')
    c2 = match.get('team2_code', '??')
    tijd = match.get('tijd', '00:00')
    groep = match.get('groep', '?')

    with st.container(border=True):
        st.caption(f"Groep {groep} • {tijd}")
        
        # 3 kolommen: Links | Score | Rechts
        col_l, col_s, col_r = st.columns([4, 3, 4])
        
        with col_l:
            st.markdown(f"**{t1}**")
            st.caption(c1)
            
        with col_s:
            # Twee compacte inputs naast elkaar
            s1, s2 = st.columns(2)
            s1.number_input("T1", 0, 15, 0, 1, key=f"s1_{m_id}", label_visibility="collapsed")
            s2.number_input("T2", 0, 15, 0, 1, key=f"s2_{m_id}", label_visibility="collapsed")
            
        with col_r:
            # Deze HTML-div lost de uitlijning op de screenshot op
            st.markdown(
                f"<div style='text-align: right;'><b>{t2}</b><br>"
                f"<span style='color: gray; font-size: 0.8em;'>{c2}</span></div>", 
                unsafe_content_allowed=True
            )
