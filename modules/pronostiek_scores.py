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
    
    # Better mobile styling
    st.markdown("""
    <style>
    .match-card {
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #444;
        background-color: #1e1e1e;
        margin-bottom: 14px;
    }
    .team-name {
        font-size: 17px;
        font-weight: 600;
    }
    .score-container {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Initialize
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

            c1, c2 = st.columns([5, 5])

            # Team 1
            with c1:
                st.markdown(f"<div class='team-name'>{t1}</div>", unsafe_allow_html=True)
                st.number_input(
                    label="",
                    min_value=0,
                    max_value=15,
                    value=st.session_state[f"s1_{mid}"],
                    key=f"s1_{mid}",
                    label_visibility="collapsed"
                )

            # Team 2
            with c2:
                st.markdown(f"<div class='team-name' style='text-align:right'>{t2}</div>", unsafe_allow_html=True)
                st.number_input(
                    label="",
                    min_value=0,
                    max_value=15,
                    value=st.session_state[f"s2_{mid}"],
                    key=f"s2_{mid}",
                    label_visibility="collapsed"
                )

            st.markdown("<p style='text-align:center; margin:8px 0; color:#888;'>VS</p>", unsafe_allow_html=True)

    # Fixed Save Button
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
            st.success("✅ Alles opgeslagen!")
