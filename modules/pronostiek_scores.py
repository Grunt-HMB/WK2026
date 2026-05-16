import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from modules.data_loader import get_matches
except ImportError:
    from data_loader import get_matches

from modules.database import connect_to_gsheet


def prediction_from_score(score1, score2):
    score1 = int(score1)
    score2 = int(score2)

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

    expected_columns = [
        "user_id",
        "match_id",
        "prediction",
        "score1",
        "score2",
        "status",
        "timestamp",
    ]

    if existing_df.empty:
        existing_df = pd.DataFrame(columns=expected_columns)

    for col in expected_columns:
        if col not in existing_df.columns:
            existing_df[col] = ""

    existing_df = existing_df[expected_columns]

    for _, row in new_df.iterrows():
        existing_df = existing_df[
            ~(
                (existing_df["user_id"].astype(str) == str(row["user_id"]))
                &
                (existing_df["match_id"].astype(str) == str(row["match_id"]))
            )
        ]

    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    final_df = final_df[expected_columns]

    ws.clear()
    ws.update([expected_columns] + final_df.astype(str).values.tolist())


def show_team(team_name):
    st.markdown(
        f"""
        <div style="
            font-weight:700;
            font-size:15px;
            line-height:1.2;
            padding-top:6px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        ">
            {team_name}
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_score(key):
    if key not in st.session_state:
        st.session_state[key] = 0


def score_control(key):
    init_score(key)

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        if st.button("−", key=f"minus_{key}", use_container_width=True):
            st.session_state[key] = max(0, int(st.session_state[key]) - 1)
            st.rerun()

    with c2:
        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:22px;
                font-weight:800;
                padding-top:6px;
            ">
                {st.session_state[key]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        if st.button("+", key=f"plus_{key}", use_container_width=True):
            st.session_state[key] = min(15, int(st.session_state[key]) + 1)
            st.rerun()


def show_pronostiek_scores(user_id):
    st.markdown(f"### 🎯 Scores invullen: {user_id}")

    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button {
            min-height: 34px;
            padding: 2px 6px;
            font-size: 18px;
            font-weight: 800;
            border-radius: 8px;
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            position: fixed;
            bottom: 15px;
            left: 15px;
            z-index: 9999;
            width: 130px;
            height: 46px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(0,0,0,0.30);
        }

        .block-container {
            padding-bottom: 80px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = get_matches()

    if df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    dag_df = df.copy()

    for _, match in dag_df.iterrows():
        m_id = str(match.get("match_id", "0"))

        t1 = str(match.get("team1", "Team 1"))
        t2 = str(match.get("team2", "Team 2"))

        tijd = str(match.get("tijd", "00:00"))
        groep = str(match.get("groep", "-"))

        key1 = f"s1_{m_id}"
        key2 = f"s2_{m_id}"

        init_score(key1)
        init_score(key2)

        with st.container(border=True):
            st.caption(f"Groep {groep} • {tijd}")

            col_l, col_s1, col_s2, col_r = st.columns([3, 3, 3, 3])

            with col_l:
                show_team(t1)

            with col_s1:
                score_control(key1)

            with col_s2:
                score_control(key2)

            with col_r:
                show_team(t2)

    if st.button(
        "💾 Opslaan",
        use_container_width=False,
        type="primary",
        key="btn_save_pronostiek_scores",
    ):
        rows = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for _, match in dag_df.iterrows():
            m_id = str(match.get("match_id", "0"))

            score1 = int(st.session_state.get(f"s1_{m_id}", 0))
            score2 = int(st.session_state.get(f"s2_{m_id}", 0))

            rows.append({
                "user_id": user_id,
                "match_id": m_id,
                "prediction": prediction_from_score(score1, score2),
                "score1": score1,
                "score2": score2,
                "status": "Voorlopig",
                "timestamp": now,
            })

        save_predictions_to_sheet(rows)

        st.success("Je scores zijn opgeslagen!")
