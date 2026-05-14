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
        "points",
    ]

    available_cols = [c for c in cols if c in df.columns]
    table = df[available_cols].copy()

    table = table.rename(
        columns={
            "position": "#",
            "team": "Ploeg",
            "played": "Wedstr.",
            "wins": "Gew.",
            "draws": "Gelijk",
            "losses": "Verl.",
            "points": "Punten",
        }
    )

    return table


def apply_manual_tie_order(group_df, group, prefix):
    if group_df is None or group_df.empty:
        return group_df

    required = ["team", "points", "position"]

    for col in required:
        if col not in group_df.columns:
            return group_df

    df = group_df.copy()

    df["team"] = df["team"].astype(str).str.strip()
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0).astype(int)
    df["position"] = pd.to_numeric(df["position"], errors="coerce").fillna(999).astype(int)

    tied_points = (
        df.groupby("points")
        .size()
        .reset_index(name="count")
    )

    tied_points = tied_points[tied_points["count"] > 1]["points"].tolist()

    if not tied_points:
        df = df.sort_values("position", kind="stable").reset_index(drop=True)
        df["position"] = range(1, len(df) + 1)
        return df

    st.markdown("##### Volgorde bij gelijke punten")

    manual_positions = {}

    for points in sorted(tied_points, reverse=True):
        tied_rows = (
            df[df["points"] == points]
            .sort_values("position", kind="stable")
            .copy()
        )

        tied_teams = tied_rows["team"].tolist()

        teams_above = df[df["points"] > points].shape[0]
        start_position = teams_above + 1

        point_label = "punt" if points == 1 else "punten"
        st.caption(f"Gelijke stand: {points} {point_label}")

        chosen = []

        for offset, original_team in enumerate(tied_teams):
            position = start_position + offset

            available = [team for team in tied_teams if team not in chosen]

            if original_team in available:
                default_index = available.index(original_team)
            else:
                default_index = 0

            selected_team = st.selectbox(
                f"Plaats {position}",
                available,
                index=default_index,
                key=f"tie_{prefix}_{group}_{points}_{position}",
            )

            chosen.append(selected_team)
            manual_positions[selected_team] = position

    for team, position in manual_positions.items():
        df.loc[df["team"] == team, "position"] = position

    df = df.sort_values(
        ["position", "team"],
        ascending=[True, True],
        kind="stable",
    ).reset_index(drop=True)

    df["position"] = range(1, len(df) + 1)

    return df


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

                user_group = apply_manual_tie_order(
                    user_group,
                    group=group,
                    prefix="user",
                )

                user_table = format_standings_table(user_group)

                if user_table.empty:
                    st.caption("Nog geen voorspelde stand.")
                else:
                    st.table(user_table)
