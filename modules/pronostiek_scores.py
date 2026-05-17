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
        border: 1px solid #333; 
        background-color: #1e1e1e; 
        margin-bottom: 10px; 
    }
    .team-name { 
        font-size: 16px; 
        font-weight: 600; 
        margin-bottom: 4px; 
    }
    .score-label {
        font-size: 15px;
        color: #aaa;
        margin-bottom: 2px;
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

            # Team 1
            st.markdown(f"<div class='team-name'>{t1}</div>", unsafe_allow_html=True)
            st.markdown("<div class='score-label'>− &nbsp;&nbsp; Score &nbsp;&nbsp; +</div>", unsafe_allow_html=True)
            st.number_input(
                label="",
                min_value=0,
                max_value=15,
                value=st.session_state[f"s1_{mid}"],
                key=f"num1_{mid}",
                label_visibility="collapsed"
            )

            st.markdown("<p style='text-align:center; margin:6px 0; color:#777;'>VS</p>", unsafe_allow_html=True)

            # Team 2
            st.markdown(f"<div class='team-name' style='text-align:right'>{t2}</div>", unsafe_allow_html=True)
            st.markdown("<div class='score-label'>− &nbsp;&nbsp; Score &nbsp;&nbsp; +</div>", unsafe_allow_html=True)
            st.number_input(
                label="",
                min_value=0,
                max_value=15,
                value=st.session_state[f"s2_{mid}"],
                key=f"num2_{mid}",
                label_visibility="collapsed"
            )

    # Fixed Save Button
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("💾 OPSLAAN ALLE VOORSPELLINGEN", 
                 type="primary", 
                 use_container_width=True):
        rows = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, match in df.iterrows():
            mid = str(match["match_id"])
            s1 = st.session_state.get(f"num1_{mid}", 0)   # Note: using the number_input key
            s2 = st.session_state.get(f"num2_{mid}", 0)
            
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
            st.success("✅ Alles opgeslagen!")
