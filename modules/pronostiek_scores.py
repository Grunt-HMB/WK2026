import streamlit as st
from modules.database import load_predictions, batch_save_predictions
from modules.pronostiek_matches import HARDCODED_MATCHES 

def show_pronostiek_scores(user_id="Tom"):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # --- CSS VOOR EXTREEM MINIMALISTISCHE GRID ---
    st.markdown("""
    <style>
    /* Verwijder alle standaard Streamlit witruimte bovenin */
    .block-container { padding: 0rem !important; }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Forceer een grid van 3 kolommen die NOOIT breekt */
    .row-container {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 10px;
        width: 100%;
        padding: 20px 10px;
    }

    .team-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .vs-cell {
        font-weight: bold;
        color: #718096;
        margin-top: 20px; /* Uitlijning met sliders */
    }

    .name-label {
        font-size: 0.9rem;
        font-weight: bold;
        color: white;
        margin-bottom: -10px;
    }

    /* Verberg labels en maak sliders smal */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    .stSlider { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- DATA ---
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    # We pakken alleen de allereerste wedstrijd uit de lijst
    m = HARDCODED_MATCHES[0]
    m_id = str(m["match_id"])
    
    if m_id not in st.session_state.score_predictions:
        st.session_state.score_predictions[m_id] = {"score1": 0, "score2": 0}
    
    data = st.session_state.score_predictions[m_id]

    # --- DE LAYOUT ---
    # We gebruiken Streamlit columns maar dwingen ze met de CSS hierboven
    col1, col_vs, col2 = st.columns([1, 0.2, 1])

    with col1:
        st.markdown(f'<div class="team-cell"><div class="name-label">{country_flag(m["team1_code"])} {m["team1"]}</div></div>', unsafe_allow_html=True)
        s1 = st.select_slider("s1", options=list(range(11)), value=data['score1'], key="s1")

    with col_vs:
        st.markdown('<div class="vs-cell">VS</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="team-cell"><div class="name-label">{country_flag(m["team2_code"])} {m["team2"]}</div></div>', unsafe_allow_html=True)
        s2 = st.select_slider("s2", options=list(range(11)), value=data['score2'], key="s2")

    # Update state
    st.session_state.score_predictions[m_id]["score1"] = s1
    st.session_state.score_predictions[m_id]["score2"] = s2

    # Grote uitslag weergave onderaan
    st.markdown(f"<h1 style='text-align: center; color: white;'>{s1} — {s2}</h1>", unsafe_allow_html=True)
