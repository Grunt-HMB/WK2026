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


def show_pronostiek_scores(user_id):
    st.markdown(f"### 🎯 Scores invullen: {user_id}")

    st.markdown(
        """
        <style>
        div[data-testid="stFormSubmitButton"] > button {
            position: fixed;
            bottom: 15px;
            left: 15px;
            z-index: 9999;

            width: 150px;
            height: 48px;

            border-radius: 14px;
            font-size: 17px;
            font-weight: 800;

            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
        }

        .block-container {
            padding-bottom: 90px;
        }

        div[data-testid="stNumberInput"] input {
            text-align: center;
            font-weight: 800;
            font-size: 20px;
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

    with st.form("pronostiek_form"):

        for _, match in dag_df.iterrows():

            m_id = str(match.get("match_id", "0"))

            t1 = str(match.get("team1", "Team 1"))
            t2 = str(match.get("team2", "Team 2"))

            groep = str(match.get("groep", "-"))
            datum = str(match.get("datum", "GEEN DATUM"))
            tijd = str(match.get("tijd", "00:00"))

            with st.container(border=True):

                st.caption(f"Groep {groep} • {datum} • {tijd}")

                st.markdown(f"**{t1}**")

                st.number_input(
                    f"Score {t1}",
                    min_value=0,
                    max_value=15,
                    value=0,
                    step=1,
                    key=f"s1_{m_id}",
                    label_visibility="collapsed",
                )

                st.number_input(
                    f"Score {t2}",
                    min_value=0,
                    max_value=15,
                    value=0,
                    step=1,
                    key=f"s2_{m_id}",
                    label_visibility="collapsed",
                )

                st.markdown(f"**{t2}**")

        submitted = st.form_submit_button(
            "💾 Opslaan",
            use_container_width=False,
            type="primary",
        )

    if submitted:

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
