import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches
from modules.database import connect_to_gsheet


def prediction_from_score(score1, score2):
    if score1 > score2: return "1"
    elif score1 < score2: return "2"
    else: return "X"


def show_pronostiek_scores(user_id: str):
    st.markdown(f"### 🎯 {user_id} - Voorspellingen")
    
    st.markdown("""
    <style>
    .compact-card {
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        background-color: #f9f9f9;
        margin-bottom: 9px;
    }
    .team-name {
        font-size: 15.5px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .score-input {
        font-size: 24px;
        font-weight: 700;
        text-align: center;
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
        st.session_state.setdefault(f"s1_{mid}", 0)
        st.session_state.setdefault(f"s2_{mid}", 0)

    for _, match in df.iterrows():
        mid = str(match["match_id"])
        t1 = match.get("team1", "Team 1")
        t2 = match.get("team2", "Team 2")
        groep = match.get("groep", "-")
        datum = match.get("datum", "")
        tijd = match.get("tijd", "")

        with st.container(border=True):
            st.caption(f"**G{groep}** • {datum} • {tijd}")

            # Team 1 row
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"<div class='team-name'>{t1}</div>", unsafe_allow_html=True)
            with col2:
                c = st.columns([1, 2, 1])
                if c[0].button("−", key=f"min1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = max(0, st.session_state[f"s1_{mid}"] - 1)
                st.number_input("", key=f"num1_{mid}", value=st.session_state[f"s1_{mid}"],
                               min_value=0, max_value=15, label_visibility="collapsed")
                if c[2].button("+", key=f"plus1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = min(15, st.session_state[f"s1_{mid}"] + 1)

            # VS
            st.markdown("<p style='text-align:center; margin:4px 0; color:#666;'>VS</p>", unsafe_allow_html=True)

            # Team 2 row
            col3, col4 = st.columns([1, 4])
            with col3:
                st.markdown(f"<div class='team-name' style='text-align:right'>{t2}</div>", unsafe_allow_html=True)
            with col4:
                c2 = st.columns([1, 2, 1])
                if c2[0].button("−", key=f"min2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = max(0, st.session_state[f"s2_{mid}"] - 1)
                st.number_input("", key=f"num2_{mid}", value=st.session_state[f"s2_{mid}"],
                               min_value=0, max_value=15, label_visibility="collapsed")
                if c2[2].button("+", key=f"plus2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = min(15, st.session_state[f"s2_{mid}"] + 1)

    # Fixed save button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 OPSLAAN ALLE VOORSPELLINGEN", 
                 type="primary", 
                 use_container_width=True):
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
        
        with st.spinner("Opslaan naar Google Sheets..."):
            save_predictions_to_sheet(rows)
            st.success("✅ Succesvol opgeslagen!")
