import streamlit as st

# Veiligheidscheck voor de import van de data_loader
try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches

def show_pronostiek_scores(user_id):
    st.markdown(f"### 🏟️ Pronostiek: {user_id}")
    
    df = get_matches()
    if df.empty:
        st.error("Geen wedstrijddata gevonden. Controleer pronostiek_matches.py")
        return

    # Filter op speeldag
    speeldagen = sorted(df['speeldag'].unique())
    gekozen_dag = st.select_slider("Kies Speeldag", options=speeldagen)
    
    dag_df = df[df['speeldag'] == gekozen_dag]

    for _, match in dag_df.iterrows():
        draw_match_card(match)

def draw_match_card(match):
    # CRUCIALE FIX: Forceer alles naar string en gebruik een fallback
    # Dit voorkomt de TypeError als data ontbreekt
    m_id = str(match.get('match_id', '0'))
    t1 = str(match.get('team1', 'Onbekend'))
    t2 = str(match.get('team2', 'Onbekend'))
    c1 = str(match.get('team1_code', '??'))
    c2 = str(match.get('team2_code', '??'))
    tijd = str(match.get('tijd', '00:00'))
    groep = str(match.get('groep', '-'))

    with st.container(border=True):
        st.caption(f"Groep {groep} • {tijd}")
        
        col_l, col_s, col_r = st.columns([4, 3, 4])
        
        with col_l:
            st.markdown(f"**{t1}**")
            st.caption(c1)
            
        with col_s:
            # Gebruik keys gebaseerd op m_id voor de scores
            s1, s2 = st.columns(2)
            s1.number_input("T1", 0, 15, 0, 1, key=f"s1_{m_id}", label_visibility="collapsed")
            s2.number_input("T2", 0, 15, 0, 1, key=f"s2_{m_id}", label_visibility="collapsed")
            
        with col_r:
            # De plek waar de crash gebeurde is nu beveiligd door de str() conversie hierboven
            st.markdown(
                f"<div style='text-align: right;'><b>{t2}</b><br>"
                f"<span style='color: gray; font-size: 0.8em;'>{c2}</span></div>", 
                unsafe_content_allowed=True
            )
