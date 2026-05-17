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
    .match-card {
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #333;
        background-color: #1e1e1e;
        margin-bottom: 12px;
    }
    .team-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 8px 0;
    }
    .score-big {
        font-size: 32px;
        font-weight: 800;
        min-width: 50px;
        text-align: center;
    }
    .stButton button {
        height: 48px;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Initialize scores
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
            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.markdown(f"**{t1}**")
            with col2:
                if st.button("−", key=f"min1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = max(0, st.session_state[f"s1_{mid}"] - 1)
                    st.rerun()
            with col3:
                st.markdown(f"<div class='score-big'>{st.session_state[f's1_{mid}']}</div>", unsafe_allow_html=True)
                if st.button("+", key=f"plus1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = min(15, st.session_state[f"s1_{mid}"] + 1)
                    st.rerun()

            st.markdown("<p style='text-align:center; margin:4px 0; color:#777;'>VS</p>", unsafe_allow_html=True)

            # Team 2
            col4, col5, col6 = st.columns([4, 2, 2])
            with col4:
                st.markdown(f"**{t2}**")
            with col5:
                if st.button("−", key=f"min2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = max(0, st.session_state[f"s2_{mid}"] - 1)
                    st.rerun()
            with col6:
                st.markdown(f"<div class='score-big'>{st.session_state[f's2_{mid}']}</div>", unsafe_allow_html=True)
                if st.button("+", key=f"plus2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = min(15, st.session_state[f"s2_{mid}"] + 1)

    # Save button (fixed at bottom)
    st.markdown("<br><br>", unsafe_allow_html=True)
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
            st.success("✅ Opgeslagen!")
