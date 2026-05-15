import streamlit as st
import pandas as pd

def show_pronostiek_scores(user_id):
    from modules.data_loader import get_matches, get_predictions, save_predictions
    
    st.title("⚽ Jouw Voorspellingen")
    st.subheader("Vul je scores in en klik onderaan op opslaan")

    # Data ophalen
    matches_df = get_matches()
    predictions_df = get_predictions(user_id)

    # Voorspellingen in een map zetten voor snel opzoeken
    preds_map = {}
    for _, row in predictions_df.iterrows():
        m_id = str(row.get('match_id', ''))
        if m_id:
            preds_map[m_id] = row

    # Formulier starten
    with st.form(key=f"form_{user_id}"):
        temp_results = {}

        for _, match in matches_df.iterrows():
            m_id = str(match['match_id'])
            
            # Bestaande waarden ophalen (of 0 als er niets is)
            p = preds_map.get(m_id, {})
            
            def safe_int(val):
                try:
                    return int(float(val)) if val and str(val).strip() != "" else 0
                except: return 0

            default_s1 = safe_int(p.get('score1', 0))
            default_s2 = safe_int(p.get('score2', 0))

            st.write(f"**{match['team1']} — {match['team2']}**")
            
            # Gebruik number_input in plaats van buttons om binnen het formulier te blijven
            col1, col2 = st.columns(2)
            with col1:
                s1 = st.number_input(f"Score {match['team1']}", min_value=0, max_value=20, value=default_s1, key=f"s1_{m_id}")
            with col2:
                s2 = st.number_input(f"Score {match['team2']}", min_value=0, max_value=20, value=default_s2, key=f"s2_{m_id}")
            
            temp_results[m_id] = {'score1': s1, 'score2': s2}
            st.divider()

        # De verzendknop
        submit_button = st.form_submit_button(label="💾 Voorspellingen Opslaan", use_container_width=True)

        if submit_button:
            success = save_predictions(user_id, temp_results)
            if success:
                st.success("✅ Je voorspellingen zijn succesvol opgeslagen!")
                st.rerun()
            else:
                st.error("❌ Er ging iets mis bij het opslaan. Probeer het opnieuw.")
