import streamlit as st
import pandas as pd
from modules.database import (
    load_predictions,
    batch_save_predictions,
)

# =========================================================
# HARDCODED DATA (Alle 72 wedstrijden)
# =========================================================
HARDCODED_MATCHES = [
    {"match_id": "1", "speeldag": "1", "ronde": "Groep", "groep": "A", "team1": "Mexico", "team2": "Zuid-Afrika", "datum": "11-06-26", "tijd": "21:00", "team1_code": "MX", "team2_code": "ZA"},
    {"match_id": "2", "speeldag": "1", "ronde": "Groep", "groep": "A", "team1": "Zuid-Korea", "team2": "Tsjechië", "datum": "12-06-26", "tijd": "4:00", "team1_code": "KR", "team2_code": "CZ"},
    {"match_id": "3", "speeldag": "1", "ronde": "Groep", "groep": "B", "team1": "Canada", "team2": "Bosnië", "datum": "12-06-26", "tijd": "21:00", "team1_code": "CA", "team2_code": "BA"},
    {"match_id": "4", "speeldag": "1", "ronde": "Groep", "groep": "D", "team1": "Verenigde Staten", "team2": "Paraguay", "datum": "13-06-26", "tijd": "3:00", "team1_code": "US", "team2_code": "PY"},
    {"match_id": "5", "speeldag": "1", "ronde": "Groep", "groep": "D", "team1": "Australië", "team2": "Turkije", "datum": "13-06-26", "tijd": "6:00", "team1_code": "AU", "team2_code": "TR"},
    {"match_id": "6", "speeldag": "1", "ronde": "Groep", "groep": "B", "team1": "Qatar", "team2": "Zwitserland", "datum": "13-06-26", "tijd": "21:00", "team1_code": "QA", "team2_code": "CH"},
    {"match_id": "7", "speeldag": "1", "ronde": "Groep", "groep": "C", "team1": "Brazilië", "team2": "Marokko", "datum": "14-06-26", "tijd": "0:00", "team1_code": "BR", "team2_code": "MA"},
    {"match_id": "8", "speeldag": "1", "ronde": "Groep", "groep": "C", "team1": "Haïti", "team2": "Schotland", "datum": "14-06-26", "tijd": "3:00", "team1_code": "HT", "team2_code": "GB"},
    {"match_id": "9", "speeldag": "1", "ronde": "Groep", "groep": "E", "team1": "Duitsland", "team2": "Curaçao", "datum": "14-06-26", "tijd": "19:00", "team1_code": "DE", "team2_code": "CW"},
    {"match_id": "10", "speeldag": "1", "ronde": "Groep", "groep": "F", "team1": "Nederland", "team2": "Japan", "datum": "14-06-26", "tijd": "22:00", "team1_code": "NL", "team2_code": "JP"},
    {"match_id": "11", "speeldag": "1", "ronde": "Groep", "groep": "E", "team1": "Ivoorkust", "team2": "Ecuador", "datum": "15-06-26", "tijd": "1:00", "team1_code": "CI", "team2_code": "EC"},
    {"match_id": "12", "speeldag": "1", "ronde": "Groep", "groep": "F", "team1": "Zweden", "team2": "Tunesië", "datum": "15-06-26", "tijd": "4:00", "team1_code": "SE", "team2_code": "TN"},
    {"match_id": "13", "speeldag": "1", "ronde": "Groep", "groep": "H", "team1": "Spanje", "team2": "Kaapverdië", "datum": "15-06-26", "tijd": "18:00", "team1_code": "ES", "team2_code": "CV"},
    {"match_id": "14", "speeldag": "1", "ronde": "Groep", "groep": "G", "team1": "België", "team2": "Egypte", "datum": "15-06-26", "tijd": "21:00", "team1_code": "BE", "team2_code": "EG"},
    {"match_id": "15", "speeldag": "1", "ronde": "Groep", "groep": "H", "team1": "Saoedi-Arabië", "team2": "Uruguay", "datum": "16-06-26", "tijd": "0:00", "team1_code": "SA", "team2_code": "UY"},
    {"match_id": "16", "speeldag": "1", "ronde": "Groep", "groep": "G", "team1": "Iran", "team2": "Nieuw-Zeeland", "datum": "16-06-26", "tijd": "3:00", "team1_code": "IR", "team2_code": "NZ"},
    {"match_id": "17", "speeldag": "1", "ronde": "Groep", "groep": "I", "team1": "Frankrijk", "team2": "Senegal", "datum": "16-06-26", "tijd": "21:00", "team1_code": "FR", "team2_code": "SN"},
    {"match_id": "18", "speeldag": "1", "ronde": "Groep", "groep": "I", "team1": "Irak", "team2": "Noorwegen", "datum": "17-06-26", "tijd": "2:00", "team1_code": "IQ", "team2_code": "NO"},
    {"match_id": "19", "speeldag": "1", "ronde": "Groep", "groep": "J", "team1": "Argentinië", "team2": "Algerije", "datum": "17-06-26", "tijd": "3:00", "team1_code": "AR", "team2_code": "DZ"},
    {"match_id": "20", "speeldag": "1", "ronde": "Groep", "groep": "J", "team1": "Oostenrijk", "team2": "Jordanië", "datum": "17-06-26", "tijd": "6:00", "team1_code": "AT", "team2_code": "JO"},
    {"match_id": "21", "speeldag": "1", "ronde": "Groep", "groep": "K", "team1": "Portugal", "team2": "DR Congo", "datum": "17-06-26", "tijd": "19:00", "team1_code": "PT", "team2_code": "CD"},
    {"match_id": "22", "speeldag": "1", "ronde": "Groep", "groep": "L", "team1": "Engeland", "team2": "Kroatië", "datum": "17-06-26", "tijd": "21:00", "team1_code": "GB", "team2_code": "HR"},
    {"match_id": "23", "speeldag": "1", "ronde": "Groep", "groep": "L", "team1": "Ghana", "team2": "Panama", "datum": "18-06-26", "tijd": "1:00", "team1_code": "GH", "team2_code": "PA"},
    {"match_id": "24", "speeldag": "1", "ronde": "Groep", "groep": "K", "team1": "Oezbekistan", "team2": "Colombia", "datum": "18-06-26", "tijd": "4:00", "team1_code": "UZ", "team2_code": "CO"},
    {"match_id": "25", "speeldag": "2", "ronde": "Groep", "groep": "A", "team1": "Tsjechië", "team2": "Zuid-Afrika", "datum": "18-06-26", "tijd": "18:00", "team1_code": "CZ", "team2_code": "ZA"},
    {"match_id": "26", "speeldag": "2", "ronde": "Groep", "groep": "B", "team1": "Zwitserland", "team2": "Bosnië", "datum": "18-06-26", "tijd": "21:00", "team1_code": "CH", "team2_code": "BA"},
    {"match_id": "27", "speeldag": "2", "ronde": "Groep", "groep": "B", "team1": "Canada", "team2": "Qatar", "datum": "19-06-26", "tijd": "0:00", "team1_code": "CA", "team2_code": "QA"},
    {"match_id": "28", "speeldag": "2", "ronde": "Groep", "groep": "A", "team1": "Mexico", "team2": "Zuid-Korea", "datum": "19-06-26", "tijd": "4:00", "team1_code": "MX", "team2_code": "KR"},
    {"match_id": "29", "speeldag": "2", "ronde": "Groep", "groep": "D", "team1": "Verenigde Staten", "team2": "Australië", "datum": "19-06-26", "tijd": "21:00", "team1_code": "US", "team2_code": "AU"},
    {"match_id": "30", "speeldag": "2", "ronde": "Groep", "groep": "C", "team1": "Schotland", "team2": "Marokko", "datum": "20-06-26", "tijd": "0:00", "team1_code": "GB", "team2_code": "MA"},
    {"match_id": "31", "speeldag": "2", "ronde": "Groep", "groep": "C", "team1": "Brazilië", "team2": "Haïti", "datum": "20-06-26", "tijd": "3:00", "team1_code": "BR", "team2_code": "HT"},
    {"match_id": "32", "speeldag": "2", "ronde": "Groep", "groep": "D", "team1": "Turkije", "team2": "Paraguay", "datum": "20-06-26", "tijd": "6:00", "team1_code": "TR", "team2_code": "PY"},
    {"match_id": "33", "speeldag": "2", "ronde": "Groep", "groep": "F", "team1": "Tunesië", "team2": "Japan", "datum": "20-06-26", "tijd": "6:00", "team1_code": "TN", "team2_code": "JP"},
    {"match_id": "34", "speeldag": "2", "ronde": "Groep", "groep": "F", "team1": "Nederland", "team2": "Zweden", "datum": "20-06-26", "tijd": "19:00", "team1_code": "NL", "team2_code": "SE"},
    {"match_id": "35", "speeldag": "2", "ronde": "Groep", "groep": "E", "team1": "Duitsland", "team2": "Ivoorkust", "datum": "20-06-26", "tijd": "22:00", "team1_code": "DE", "team2_code": "CI"},
    {"match_id": "36", "speeldag": "2", "ronde": "Groep", "groep": "E", "team1": "Ecuador", "team2": "Curaçao", "datum": "21-06-26", "tijd": "2:00", "team1_code": "EC", "team2_code": "CW"},
    {"match_id": "37", "speeldag": "2", "ronde": "Groep", "groep": "H", "team1": "Spanje", "team2": "Saoedi-Arabië", "datum": "21-06-26", "tijd": "18:00", "team1_code": "ES", "team2_code": "SA"},
    {"match_id": "38", "speeldag": "2", "ronde": "Groep", "groep": "G", "team1": "België", "team2": "Iran", "datum": "21-06-26", "tijd": "21:00", "team1_code": "BE", "team2_code": "IR"},
    {"match_id": "39", "speeldag": "2", "ronde": "Groep", "groep": "H", "team1": "Uruguay", "team2": "Kaapverdië", "datum": "22-06-26", "tijd": "0:00", "team1_code": "UY", "team2_code": "CV"},
    {"match_id": "40", "speeldag": "2", "ronde": "Groep", "groep": "G", "team1": "Nieuw-Zeeland", "team2": "Egypte", "datum": "22-06-26", "tijd": "3:00", "team1_code": "NZ", "team2_code": "EG"},
    {"match_id": "41", "speeldag": "2", "ronde": "Groep", "groep": "J", "team1": "Argentinië", "team2": "Oostenrijk", "datum": "22-06-26", "tijd": "19:00", "team1_code": "AR", "team2_code": "AT"},
    {"match_id": "42", "speeldag": "2", "ronde": "Groep", "groep": "I", "team1": "Frankrijk", "team2": "Irak", "datum": "22-06-26", "tijd": "23:00", "team1_code": "FR", "team2_code": "IQ"},
    {"match_id": "43", "speeldag": "2", "ronde": "Groep", "groep": "I", "team1": "Noorwegen", "team2": "Senegal", "datum": "23-06-26", "tijd": "2:00", "team1_code": "NO", "team2_code": "SN"},
    {"match_id": "44", "speeldag": "2", "ronde": "Groep", "groep": "J", "team1": "Jordanië", "team2": "Algerije", "datum": "23-06-26", "tijd": "3:00", "team1_code": "JO", "team2_code": "DZ"},
    {"match_id": "45", "speeldag": "2", "ronde": "Groep", "groep": "K", "team1": "Portugal", "team2": "Oezbekistan", "datum": "23-06-26", "tijd": "19:00", "team1_code": "PT", "team2_code": "UZ"},
    {"match_id": "46", "speeldag": "2", "ronde": "Groep", "groep": "L", "team1": "Engeland", "team2": "Ghana", "datum": "23-06-26", "tijd": "22:00", "team1_code": "GB", "team2_code": "GH"},
    {"match_id": "47", "speeldag": "2", "ronde": "Groep", "groep": "L", "team1": "Panama", "team2": "Kroatië", "datum": "24-06-26", "tijd": "1:00", "team1_code": "PA", "team2_code": "HR"},
    {"match_id": "48", "speeldag": "2", "ronde": "Groep", "groep": "K", "team1": "Colombia", "team2": "DR Congo", "datum": "24-06-26", "tijd": "4:00", "team1_code": "CO", "team2_code": "CD"},
    {"match_id": "49", "speeldag": "3", "ronde": "Groep", "groep": "B", "team1": "Zwitserland", "team2": "Canada", "datum": "24-06-26", "tijd": "21:00", "team1_code": "CH", "team2_code": "CA"},
    {"match_id": "50", "speeldag": "3", "ronde": "Groep", "groep": "B", "team1": "Bosnië", "team2": "Qatar", "datum": "24-06-26", "tijd": "21:00", "team1_code": "BA", "team2_code": "QA"},
    {"match_id": "51", "speeldag": "3", "ronde": "Groep", "groep": "C", "team1": "Marokko", "team2": "Haïti", "datum": "25-06-26", "tijd": "0:00", "team1_code": "MA", "team2_code": "HT"},
    {"match_id": "52", "speeldag": "3", "ronde": "Groep", "groep": "C", "team1": "Schotland", "team2": "Brazilië", "datum": "25-06-26", "tijd": "0:00", "team1_code": "GB", "team2_code": "BR"},
    {"match_id": "53", "speeldag": "3", "ronde": "Groep", "groep": "A", "team1": "Zuid-Afrika", "team2": "Zuid-Korea", "datum": "25-06-26", "tijd": "3:00", "team1_code": "ZA", "team2_code": "KR"},
    {"match_id": "54", "speeldag": "3", "ronde": "Groep", "groep": "A", "team1": "Tsjechië", "team2": "Mexico", "datum": "25-06-26", "tijd": "3:00", "team1_code": "CZ", "team2_code": "MX"},
    {"match_id": "55", "speeldag": "3", "ronde": "Groep", "groep": "E", "team1": "Curaçao", "team2": "Ivoorkust", "datum": "25-06-26", "tijd": "22:00", "team1_code": "CW", "team2_code": "CI"},
    {"match_id": "56", "speeldag": "3", "ronde": "Groep", "groep": "E", "team1": "Ecuador", "team2": "Duitsland", "datum": "25-06-26", "tijd": "22:00", "team1_code": "EC", "team2_code": "DE"},
    {"match_id": "57", "speeldag": "3", "ronde": "Groep", "groep": "F", "team1": "Japan", "team2": "Zweden", "datum": "26-06-26", "tijd": "1:00", "team1_code": "JP", "team2_code": "SE"},
    {"match_id": "58", "speeldag": "3", "ronde": "Groep", "groep": "F", "team1": "Tunesië", "team2": "Nederland", "datum": "26-06-26", "tijd": "1:00", "team1_code": "TN", "team2_code": "NL"},
    {"match_id": "59", "speeldag": "3", "ronde": "Groep", "groep": "D", "team1": "Turkije", "team2": "Verenigde Staten", "datum": "26-06-26", "tijd": "4:00", "team1_code": "TR", "team2_code": "US"},
    {"match_id": "60", "speeldag": "3", "ronde": "Groep", "groep": "D", "team1": "Paraguay", "team2": "Australië", "datum": "26-06-26", "tijd": "4:00", "team1_code": "PY", "team2_code": "AU"},
    {"match_id": "61", "speeldag": "3", "ronde": "Groep", "groep": "I", "team1": "Noorwegen", "team2": "Frankrijk", "datum": "26-06-26", "tijd": "21:00", "team1_code": "NO", "team2_code": "FR"},
    {"match_id": "62", "speeldag": "3", "ronde": "Groep", "groep": "I", "team1": "Senegal", "team2": "Irak", "datum": "26-06-26", "tijd": "21:00", "team1_code": "SN", "team2_code": "IQ"},
    {"match_id": "63", "speeldag": "3", "ronde": "Groep", "groep": "H", "team1": "Kaapverdië", "team2": "Saoedi-Arabië", "datum": "27-06-26", "tijd": "2:00", "team1_code": "CV", "team2_code": "SA"},
    {"match_id": "64", "speeldag": "3", "ronde": "Groep", "groep": "H", "team1": "Uruguay", "team2": "Spanje", "datum": "27-06-26", "tijd": "2:00", "team1_code": "UY", "team2_code": "ES"},
    {"match_id": "65", "speeldag": "3", "ronde": "Groep", "groep": "G", "team1": "Nieuw-Zeeland", "team2": "België", "datum": "27-06-26", "tijd": "5:00", "team1_code": "NZ", "team2_code": "BE"},
    {"match_id": "66", "speeldag": "3", "ronde": "Groep", "groep": "G", "team1": "Egypte", "team2": "Iran", "datum": "27-06-26", "tijd": "5:00", "team1_code": "EG", "team2_code": "IR"},
    {"match_id": "67", "speeldag": "3", "ronde": "Groep", "groep": "L", "team1": "Panama", "team2": "Engeland", "datum": "27-06-26", "tijd": "23:00", "team1_code": "PA", "team2_code": "GB"},
    {"match_id": "68", "speeldag": "3", "ronde": "Groep", "groep": "L", "team1": "Kroatië", "team2": "Ghana", "datum": "27-06-26", "tijd": "23:00", "team1_code": "HR", "team2_code": "GH"},
    {"match_id": "69", "speeldag": "3", "ronde": "Groep", "groep": "K", "team1": "Colombia", "team2": "Portugal", "datum": "28-06-26", "tijd": "1:30", "team1_code": "CO", "team2_code": "PT"},
    {"match_id": "70", "speeldag": "3", "ronde": "Groep", "groep": "K", "team1": "DR Congo", "team2": "Oezbekistan", "datum": "28-06-26", "tijd": "1:30", "team1_code": "CD", "team2_code": "UZ"},
    {"match_id": "71", "speeldag": "3", "ronde": "Groep", "groep": "J", "team1": "Algerije", "team2": "Oostenrijk", "datum": "28-06-26", "tijd": "4:00", "team1_code": "DZ", "team2_code": "AT"},
    {"match_id": "72", "speeldag": "3", "ronde": "Groep", "groep": "J", "team1": "Jordanië", "team2": "Argentinië", "datum": "28-06-26", "tijd": "4:00", "team1_code": "JO", "team2_code": "AR"},
]

def show_pronostiek_scores(user_id="Tom"):

    # CALLBACK FUNCTIE
    def update_score_callback(match_id, team_num, delta):
        m_id = str(match_id)
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        field = f"score{team_num}"
        curr_val = st.session_state.score_predictions[m_id][field]
        st.session_state.score_predictions[m_id][field] = max(0, int(curr_val) + delta)
        
        # Bereken 1-X-2
        s1 = st.session_state.score_predictions[m_id]["score1"]
        s2 = st.session_state.score_predictions[m_id]["score2"]
        if s1 > s2: res = "1"
        elif s1 < s2: res = "2"
        else: res = "X"
        st.session_state.score_predictions[m_id]["prediction"] = res

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2: return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    # CSS VOOR STABIELE MOBIELE LAYOUT
    st.markdown("""
    <style>
    .block-container { padding: 0 0.5rem 5rem 0.5rem !important; }
    
    /* Forceer horizontale knoppen in de popover */
    [data-testid="stPopoverBody"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    
    .st-key-score_top_bar {
        position: fixed; top: 0; left: 0; right: 0; z-index: 999;
        background: #0e1117; padding: 0.5rem; border-bottom: 1px solid #30363d;
    }
    .top-spacer { height: 70px; }

    /* Stijl voor de wedstrijdrijen */
    .match-info { font-size: 0.75rem; color: #8b949e; margin-bottom: -5px; }
    
    /* Verberg standaard Streamlit padding */
    [data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # INITIALISATIE
    if "score_predictions" not in st.session_state:
        st.session_state.score_predictions = {}
    
    if f"loaded_{user_id}" not in st.session_state:
        db_preds = load_predictions(user_id)
        for _, row in db_preds.iterrows():
            st.session_state.score_predictions[str(row['match_id'])] = {
                "prediction": row['prediction'], "score1": int(row['score1']), "score2": int(row['score2'])
            }
        st.session_state[f"loaded_{user_id}"] = True

    # TOP BAR
    with st.container(key="score_top_bar"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Menu", use_container_width=True):
                st.session_state.main_page = "🏠 Hoofdmenu"
                st.rerun()
        with c2:
            if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
                batch_save_predictions(user_id, st.session_state.score_predictions, "concept")
                st.toast("✅ Opgeslagen!")

    st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)

    # SPEELDAG SELECTIE
    sd = st.radio("Speeldag", ["1", "2", "3"], horizontal=True, label_visibility="collapsed")
    
    # WEERGAVE MATCHEN
    for m in [x for x in HARDCODED_MATCHES if x["speeldag"] == sd]:
        m_id = m["match_id"]
        if m_id not in st.session_state.score_predictions:
            st.session_state.score_predictions[m_id] = {"prediction": "X", "score1": 0, "score2": 0}
        
        data = st.session_state.score_predictions[m_id]
        
        # Informatie boven de knop
        st.markdown(f"<div class='match-info'>{m['datum']} - {m['tijd']} - Groep {m['groep']}</div>", unsafe_allow_html=True)
        
        # De Popover is de "Knop" om de uitslag in te geven
        btn_label = f"{country_flag(m['team1_code'])} {data['score1']} - {data['score2']} {country_flag(m['team2_code'])}"
        with st.popover(btn_label, use_container_width=True):
            st.subheader(f"{m['team1']} vs {m['team2']}")
            
            # De + en - controls binnen de popover
            col1, col2, col3, col_sep, col4, col5, col6 = st.columns([1,1,1,0.2,1,1,1])
            with col1: st.button("−", key=f"m1_{m_id}", on_click=update_score_callback, args=(m_id, 1, -1))
            with col2: st.title(f"{data['score1']}")
            with col3: st.button("+", key=f"p1_{m_id}", on_click=update_score_callback, args=(m_id, 1, 1))
            
            with col_sep: st.write("")
            
            with col4: st.button("−", key=f"m2_{m_id}", on_click=update_score_callback, args=(m_id, 2, -1))
            with col5: st.title(f"{data['score2']}")
            with col6: st.button("+", key=f"p2_{m_id}", on_click=update_score_callback, args=(m_id, 2, 1))
            
            st.write(f"Resultaat: **{data['prediction']}**")

    st.markdown("---")
    st.caption("Klik op een wedstrijd om de score aan te passen.")
