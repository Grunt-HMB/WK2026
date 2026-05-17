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
        padding: 10px 12px;
        border-radius: 10px;
        border: 1px solid #444;
        background-color: #1e1e1e;
        margin-bottom: 10px;
    }
    .team-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stButton button {
        height: 42px;
        font-size: 20px;
        font-weight: bold;
    }
    .score-display {
        font-size: 28px;
        font-weight: 800;
        min-width: 48px;
        text-align: center;
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

            # Team 1 - Horizontal layout
            c1 = st.columns([3.5, 1, 1.2, 1])
            with c1[0]:
                st.markdown(f"**{t1}**")
            with c1[1]:
                if st.button("−", key=f"min1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = max(0, st.session_state[f"s1_{mid}"] - 1)
            with c1[2]:
                st.markdown(f"<div class='score-display'>{st.session_state[f's1_{mid}']}</div>", unsafe_allow_html=True)
            with c1[3]:
                if st.button("+", key=f"plus1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = min(15, st.session_state[f"s1_{mid}"] + 1)

            st.markdown("<p style='text-align:center; margin:4px 0; color:#666;'>VS</p>", unsafe_allow_html=True)

            # Team 2 - Horizontal layout
            c2 = st.columns([3.5, 1, 1.2, 1])
            with c2[0]:
                st.markdown(f"**{t2}**")
            with c2[1]:
                if st.button("−", key=f"min2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = max(0, st.session_state[f"s2_{mid}"] - 1)
            with c2[2]:
                st.markdown(f"<div class='score-display'>{st.session_state[f's2_{mid}']}</div>", unsafe_allow_html=True)
            with c2[3]:
                if st.button("+", key=f"plus2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = min(15, st.session_state[f"s2_{mid}"] + 1)

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
            st.success("✅ Opgeslagen!")
