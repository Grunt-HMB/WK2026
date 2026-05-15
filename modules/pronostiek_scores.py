import streamlit as st
from modules.database import load_matches, load_predictions, batch_save_predictions

def show_pronostiek_scores(user_id="Tom"):
    # --- CSS voor Mobiele Optimalisatie ---
    st.markdown("""
        <style>
        .block-container { padding: 0.5rem !important; }
        
        /* Forceer kolommen om naast elkaar te blijven op mobiel */
        [data-testid="column"] {
            width: auto !important;
            flex-basis: auto !important;
            min-width: 0px !important;
        }
        
        /* De Match Card */
        .match-box {
            background: #1e293b;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 8px;
            border: 1px solid #334155;
        }
        
        .team-text { font-size: 0.9rem; font-weight: 700; margin-bottom: 5px; }
        
        /* Custom styling voor de score cijfers */
        .score-display {
            background: #0f172a;
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 900;
            padding: 2px 12px;
            border-radius: 5px;
            border: 1px solid #3b82f6;
            text-align: center;
            min-width: 35px;
        }
        
        /* Maak st.button heel compact */
        .stButton button {
            padding: 0px 10px !important;
            height: 35px !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Data Laden & State ---
    if "score_predictions" not in st.session_state:
        # Hier laad je eenmalig je data in de session_state
        matches = load_matches()
        preds = load_predictions(user_id)
        # Combineer dit in een dictionary in session_state
        st.session_state.score_predictions = {} 
        # (Logica om de dict te vullen met match_id: {s1, s2})

    # --- De Lijst ---
    st.title("Touch Prono")
    
    # "Opslaan" knop bovenaan die wél een rerun doet
    if st.button("💾 ALLES OPSLAAN", type="primary", use_container_width=True):
        batch_save_predictions(user_id, st.session_state.score_predictions)
        st.success("Opgeslagen!")
        st.rerun()

    for m_id, data in st.session_state.score_predictions.items():
        # We gebruiken een unieke container per wedstrijd
        with st.container():
            st.markdown(f"<div class='team-text'>{data['team1']} - {data['team2']}</div>", unsafe_allow_html=True)
            
            # De cruciale regel: we zetten alles in zeer kleine kolommen
            # Door de CSS bovenin blijven deze kolommen NAAST elkaar op mobiel
            c1, c2, c3, spacer, c4, c5, c6 = st.columns([1, 1.2, 1, 0.5, 1, 1.2, 1])
            
            # Team 1
            with c1:
                if st.button("−", key=f"m1_{m_id}"):
                    st.session_state.score_predictions[m_id]['s1'] = max(0, data['s1'] - 1)
                    # GEEN st.rerun() hier -> de waarde in session_state verandert, 
                    # maar we laten Streamlit pas verversen als de gebruiker dat wil of 
                    # we gebruiken een trucje met fragmenten.
            with c2:
                st.markdown(f"<div class='score-display'>{data['s1']}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("+", key=f"p1_{m_id}"):
                    st.session_state.score_predictions[m_id]['s1'] += 1
            
            # Team 2
            with c4:
                if st.button("−", key=f"m2_{m_id}"):
                    st.session_state.score_predictions[m_id]['s2'] = max(0, data['s2'] - 1)
            with c5:
                st.markdown(f"<div class='score-display'>{data['s2']}</div>", unsafe_allow_html=True)
            with c6:
                if st.button("+", key=f"p2_{m_id}"):
                    st.session_state.score_predictions[m_id]['s2'] += 1
