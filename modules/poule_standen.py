import pandas as pd
import streamlit as st

from modules.knockout_engine import calculate_group_standings


def prediction_to_score(prediction):
    prediction = str(prediction or "").upper().strip()

    if prediction == "1":
        return "1", "0"

    if prediction == "X":
        return "0", "0"

    if prediction == "2":
        return "0", "1"

    return "", ""


def format_standings_table(df):
    if df is None or df.empty:
        return pd.DataFrame()

    cols = [
        "position",
        "team",
        "played",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_diff",
        "points",
    ]

    available_cols = [c for c in cols if c in df.columns]

    table = df[available_cols].copy()

    table = table.rename(
        columns={
            "position": "#",
            "team": "Team",
            "played": "M",
            "wins": "W",
            "draws": "G",
            "losses": "V",
            "goals_for": "DV",
            "goals_against": "DT",
            "goal_diff": "DS",
            "points": "Ptn",
        }
    )

    return table


def build_user_group_standings(matches_df, predictions_df):
    if matches_df is None or matches_df.empty:
        return pd.DataFrame()

    predicted_matches = matches_df.copy()

    for col in ["score1", "score2"]:
        if col not in predicted_matches.columns:
            predicted_matches[col] = ""

        predicted_matches[col] = predicted_matches[col].astype("object")
        predicted_matches[col] = ""

    predictions_map = {}

    if predictions_df is not None and not predictions_df.empty:
        for _, row in predictions_df.iterrows():
            match_id = str(row.get("match_id", "")).strip()
            prediction = str(row.get("prediction", "")).upper().strip()

            if match_id and prediction in ["1", "X", "2"]:
                predictions_map[match_id] = prediction

    for idx, row in predicted_matches.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        prediction = predictions_map.get(match_id, "")

        score1, score2 = prediction_to_score(prediction)

        predicted_matches.at[idx, "score1"] = score1
        predicted_matches.at[idx, "score2"] = score2

    return calculate_group_standings(predicted_matches)


def show_poule_standen(matches_df, official_standings_df, predictions_df):
    st.subheader("📊 Poulestanden")
    st.caption("Officiële poulestanden naast jouw voorspelde poulestanden.")

    user_standings_df = build_user_group_standings(
        matches_df=matches_df,
        predictions_df=predictions_df,
    )

    groups = []

    if official_standings_df is not None and not official_standings_df.empty:
        if "groep" in official_standings_df.columns:
            groups += (
                official_standings_df["groep"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

    if user_standings_df is not None and not user_standings_df.empty:
        if "groep" in user_standings_df.columns:
            groups += (
                user_standings_df["groep"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

    groups = sorted(set([g for g in groups if g]))

    if not groups:
        st.info("Nog geen poulestanden beschikbaar.")
        return

    for group in groups:
        official_group = pd.DataFrame()
        user_group = pd.DataFrame()

        if official_standings_df is not None and not official_standings_df.empty:
            official_group = official_standings_df[
                official_standings_df["groep"].astype(str).str.strip() == group
            ].copy()

        if user_standings_df is not None and not user_standings_df.empty:
            user_group = user_standings_df[
                user_standings_df["groep"].astype(str).str.strip() == group
            ].copy()

        with st.container(border=True):
            st.markdown(f"### Groep {group}")

            col_official, col_user = st.columns(2, gap="medium")

            with col_official:
                st.markdown("#### Officieel")
                official_table = format_standings_table(official_group)

                if official_table.empty:
                    st.caption("Nog geen officiële stand.")
                else:
                    st.table(official_table)

            with col_user:
                st.markdown("#### Mijn voorspelling")
                user_table = format_standings_table(user_group)

                if user_table.empty:
                    st.caption("Nog geen voorspelde stand.")
                else:
                    st.table(user_table)
