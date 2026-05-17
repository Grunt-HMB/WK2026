import streamlit as st
import pandas as pd
from datetime import datetime

# Your imports...
try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches
from modules.database import connect_to_gsheet


def prediction_from_score(score1, score2):
    if score1 > score2: return "1"
    elif score1 < score2: return "2"
    else: return "X"


def flag_emoji(country):
    flags = {"Netherlands": "🇳🇱", "Germany": "🇩🇪", "France": "🇫🇷", "Spain": "🇪🇸", 
             "England": "🇬🇧", "Italy": "🇮🇹", "Belgium": "🇧🇪", "Portugal": "🇵🇹"}
    return flags.get(country, "🏴")


def show_pronostiek_scores(user_id: str):
    st.markdown(f"### 🎯 {user_id} - Voorspellingen")
    
    st.markdown("""
    <style>
    .match-card {
        padding: 10px 12px;
        border-radius: 12px;
        border: 1px solid #ddd;
        background-color: #fafafa;
        margin-bottom: 10px;
    }
    .team-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .score-container {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .score-btn {
        font-size: 18px !important;
        padding: 4px 12px !important;
        min-width: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Initialize session state
    for _, m in df.iterrows():
        mid = str(m["match_id"])
        if f"s1_{mid}" not in st.session_state:
            st.session_state[f"s1_{mid}"] = 0
        if f"s2_{mid}" not in st.session_state:
            st.session_state[f"s2_{mid}"] = 0

    for _, match in df.iterrows():
        mid = str(match["match_id"])
        t1 = match.get("team1", "Team1")
        t2 = match.get("team2", "Team2")
        groep = match.get("groep", "-")
        datum = match.get("datum", "")
        tijd = match.get("tijd", "")

        with st.container(border=True):
            st.caption(f"**Groep {groep}** • {datum} • {tijd}")

            # Row 1: Team names + flags
            col1, col2 = st.columns([5, 5])
            with col1:
                st.markdown(f"**{flag_emoji(t1)} {t1}**")
            with col2:
                st.markdown(f"**{t2} {flag_emoji(t2)}**")

            # Row 2: Scores side by side
            c1, c2, c3 = st.columns([5, 2, 5])
            
            with c1:
                btn1 = st.columns([1, 3, 1])
                if btn1[0].button("−", key=f"min1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = max(0, st.session_state[f"s1_{mid}"] - 1)
                st.number_input("", min_value=0, max_value=15, value=st.session_state[f"s1_{mid}"],
                               key=f"num1_{mid}", label_visibility="collapsed")
                if btn1[2].button("+", key=f"plus1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = min(15, st.session_state[f"s1_{mid}"] + 1)

            with c2:
                st.markdown("**VS**", unsafe_allow_html=True)

            with c3:
                btn2 = st.columns([1, 3, 1])
                if btn2[0].button("−", key=f"min2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = max(0, st.session_state[f"s2_{mid}"] - 1)
                st.number_input("", min_value=0, max_value=15, value=st.session_state[f"s2_{mid}"],
                               key=f"num2_{mid}", label_visibility="collapsed")
                if btn2[2].button("+", key=f"plus2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = min(15, st.session_state[f"s2_{mid}"] + 1)

    # === FIXED SAVE BUTTON ===
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 OPSLAAN ALLE VOORSPELLINGEN", type="primary", use_container_width=True):
        rows = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, match in df.iterrows():
            mid = str(match["match_id"])
            s1 = st.session_state.get(f"s1_{mid}", 0)
            s2 = st.session_state.get(f"s2_{mid}", 0)
            
            rows.append({
                "user_id": user_id,
                "match_id": mid,
                "prediction": prediction_from_score(s1, s2),
                "score1": s1,
                "score2": s2,
                "status": "Voorlopig",
                "timestamp": now,
            })
        
        with st.spinner("Opslaan..."):
            save_predictions_to_sheet(rows)
            st.success("✅ Alles succesvol opgeslagen!")
