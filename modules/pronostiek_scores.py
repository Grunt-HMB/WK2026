import streamlit as st
import pandas as pd
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # 1. Pagina instellingen voor maximale breedte
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
        .block-container { padding-top: 1rem !important; }
        footer { visibility: hidden; }
        /* Maak de editor groter voor mobiel gebruik */
        [data-testid="stDataEditor"] { width: 100% !important; }
        </style>
    """, unsafe_allow_html=True)

    # 2. Data laden
    @st.cache_data(ttl=60)
    def get_ui_data(uid):
        m = load_matches()
        p = load_predictions(uid)
        # Alleen groepsfase
        if "ronde" in m.columns:
            m = m[m["ronde"].astype(str).str.lower().str.contains("groep", na=False)]
        return m, p

    matches_df, predictions_df = get_ui_data(user_id)

    # 3. Data voorbereiden voor de editor
    # We voegen de huidige voorspellingen samen met de wedstrijden
    df_editor = matches_df[['match_id', 'datum', 'tijd', 'team1', 'team2']].copy()
    
    # Scores toevoegen (koppelen op match_id)
    preds_map = predictions_df.set_index('match_id')[['score1', 'score2']].to_dict('index')
    df_editor['Huis'] = df_editor['match_id'].apply(lambda x: int(preds_map.get(x, {}).get('score1', 0)))
    df_editor['Uit'] = df_editor['match_id'].apply(lambda x: int(preds_map.get(x, {}).get('score2', 0)))
    
    # Mooie weergave voor de teams
    df_editor['Wedstrijd'] = df_editor['team1'] + " vs " + df_editor['team2']
    
    # Alleen de kolommen die we willen tonen
    display_df = df_editor[['datum', 'tijd', 'Wedstrijd', 'Huis', 'Uit', 'match_id']]

    st.title("🏆 Je Pronostiek")
    st.info("Klik op de scores om ze aan te passen. Klik daarna onderaan op 'Opslaan'.")

    # 4. De Data Editor (De "Magie")
    edited_df = st.data_editor(
        display_df,
        column_config={
            "match_id": None, # Verberg ID
            "datum": st.column_config.TextColumn("Datum", disabled=True),
            "tijd": st.column_config.TextColumn("Tijd", disabled=True),
            "Wedstrijd": st.column_config.TextColumn("Wedstrijd", disabled=True),
            "Huis": st.column_config.NumberColumn("Huis", min_value=0, max_value=50, step=1),
            "Uit": st.column_config.NumberColumn("Uit", min_value=0, max_value=50, step=1),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    # 5. Opslaan knop
    if st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True):
        # Omzetten naar het formaat dat jouw database verwacht
        final_predictions = {}
        for _, row in edited_df.iterrows():
            m_id = str(row['match_id'])
            s1 = int(row['Huis'])
            s2 = int(row['Uit'])
            
            # Bepaal resultaat (1, X, 2)
            res = "X"
            if s1 > s2: res = "1"
            elif s1 < s2: res = "2"
            
            final_predictions[m_id] = {
                "score1": s1,
                "score2": s2,
                "prediction": res
            }
        
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=final_predictions,
            status="concept"
        )
        st.success(f"✅ {saved} uitslagen succesvol opgeslagen!")
        st.cache_data.clear()
        st.rerun()

    if st.button("☰ Terug naar Menu"):
        st.session_state.main_page = "🏠 Hoofdmenu"
        st.rerun()
