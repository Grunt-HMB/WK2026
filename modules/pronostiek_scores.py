import streamlit as st
import pandas as pd
from datetime import datetime

# Your existing imports
try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches
from modules.database import connect_to_gsheet


def prediction_from_score(score1, score2):
    if score1 > score2:
        return "1"
    elif score1 < score2:
        return "2"
    else:
        return "X"


def save_predictions_to_sheet(rows):
    sh = connect_to_gsheet()
    ws = sh.worksheet("Predictions")
    existing = ws.get_all_records()
    existing_df = pd.DataFrame(existing)
    
    new_df = pd.DataFrame(rows)
    expected_columns = ["user_id", "match_id", "prediction", "score1", "score2", "status", "timestamp"]
    
    if existing_df.empty:
        existing_df = pd.DataFrame(columns=expected_columns)
    
    # Remove old predictions for this user + match
    if not existing_df.empty:
        existing_df = existing_df[
            ~(
                (existing_df["user_id"].astype(str) == str(rows[0]["user_id"]))
                & (existing_df["match_id"].astype(str).isin(new_df["match_id"].astype(str)))
            )
        ]
    
    final_df = pd.concat([existing_df, new_df], ignore_index=True)[expected_columns]
    
    ws.clear()
    ws.update([expected_columns] + final_df.astype(str).values.tolist())


def flag_emoji(country: str) -> str:
    """Simple flag emoji fallback. Improve with a dict if needed."""
    # You can expand this with real mapping (e.g. NL -> 🇳🇱)
    flags = {
        "Netherlands": "🇳🇱", "Germany": "🇩🇪", "France": "🇫🇷", "Spain": "🇪🇸",
        "England": "🇬🇧", "Italy": "🇮🇹", "Belgium": "🇧🇪", "Portugal": "🇵🇹",
        # Add all your countries
    }
    return flags.get(country, "🏴")


def show_pronostiek_scores(user_id: str):
    st.markdown(f"### 🎯 {user_id} - Voorspellingen")
    
    # Mobile-optimized styling
    st.markdown("""
    <style>
    .fixed-save-btn {
        position: fixed;
        bottom: 15px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        width: 90%;
        max-width: 400px;
        height: 52px;
        font-size: 18px;
        font-weight: 800;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .match-card {
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin-bottom: 12px;
        background-color: #fafafa;
    }
    .score-input {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

    df = get_matches()
    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    # Initialize session state for all scores
    for _, match in df.iterrows():
        mid = str(match["match_id"])
        if f"s1_{mid}" not in st.session_state:
            st.session_state[f"s1_{mid}"] = 0
        if f"s2_{mid}" not in st.session_state:
            st.session_state[f"s2_{mid}"] = 0

    # Form for inputs (but save happens outside)
    for _, match in df.iterrows():
        mid = str(match["match_id"])
        t1 = match.get("team1", "Team 1")
        t2 = match.get("team2", "Team 2")
        groep = match.get("groep", "-")
        datum = match.get("datum", "")
        tijd = match.get("tijd", "")

        with st.container(border=True):
            st.caption(f"**Groep {groep}** • {datum} • {tijd}")
            
            col1, col2, col3 = st.columns([3, 2, 3])
            
            with col1:
                st.markdown(f"**{flag_emoji(t1)} {t1}**")
            
            with col2:
                st.markdown("<h3 style='text-align:center; margin:0;'>VS</h3>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"**{t2} {flag_emoji(t2)}**")
            
            # Score inputs with +/- buttons (very mobile friendly)
            c1, c2, c3 = st.columns([3, 2, 3])
            
            with c1:
                col_plus = st.columns([1, 2, 1])
                if col_plus[0].button("−", key=f"min1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = max(0, st.session_state[f"s1_{mid}"] - 1)
                st.number_input("Score", min_value=0, max_value=15, 
                              value=st.session_state[f"s1_{mid}"], 
                              key=f"disp1_{mid}", label_visibility="collapsed")
                if col_plus[2].button("+", key=f"plus1_{mid}", use_container_width=True):
                    st.session_state[f"s1_{mid}"] = min(15, st.session_state[f"s1_{mid}"] + 1)
            
            with c2:
                st.empty()
            
            with c3:
                col_plus2 = st.columns([1, 2, 1])
                if col_plus2[0].button("−", key=f"min2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = max(0, st.session_state[f"s2_{mid}"] - 1)
                st.number_input("Score", min_value=0, max_value=15, 
                              value=st.session_state[f"s2_{mid}"], 
                              key=f"disp2_{mid}", label_visibility="collapsed")
                if col_plus2[2].button("+", key=f"plus2_{mid}", use_container_width=True):
                    st.session_state[f"s2_{mid}"] = min(15, st.session_state[f"s2_{mid}"] + 1)

    # Fixed save button
    if st.button("💾 OPSLAAN", type="primary", use_container_width=True):
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
            st.success("✅ Alle voorspellingen succesvol opgeslagen!")
            st.balloons()
