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


def build_prediction_standings(matches_df):
    if matches_df is None or matches_df.empty:
        return None

    predicted_matches = matches_df.copy()

    for col in ["score1", "score2"]:
        if col not in predicted_matches.columns:
            predicted_matches[col] = ""

        predicted_matches[col] = predicted_matches[col].astype("object")
        predicted_matches[col] = ""

    local_predictions = st.session_state.get("local_predictions", {})

    for idx, row in predicted_matches.iterrows():
        match_id = str(row.get("match_id", "")).strip()

        pred_data = local_predictions.get(match_id, {})

        if isinstance(pred_data, dict):
            prediction = str(pred_data.get("prediction", "")).upper().strip()
        else:
            prediction = str(pred_data or "").upper().strip()

        score1, score2 = prediction_to_score(prediction)

        predicted_matches.at[idx, "score1"] = str(score1)
        predicted_matches.at[idx, "score2"] = str(score2)

    return calculate_group_standings(predicted_matches)


def format_standings_table(group_standings):
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

    available_cols = [c for c in cols if c in group_standings.columns]

    table = group_standings[available_cols].copy()

    table = table.rename(
        columns={
            "position": "#",
            "team": "Team",
            "played": "M",
            "wins": "W",
            "draws": "X",
            "losses": "V",
            "goals_for": "DV",
            "goals_against": "DT",
            "goal_diff": "DS",
            "points": "Ptn",
        }
    )

    return table


def show_single_standings(title, group_standings):
    st.markdown(title)

    if group_standings is None or group_standings.empty:
        st.caption("Nog geen stand beschikbaar.")
        return

    table = format_standings_table(group_standings)
    st.dataframe(table, use_container_width=True, hide_index=True)


def show_all_group_standings(official_standings_df, matches_df):
    st.subheader("📊 Groepsstanden")

    predicted_standings_df = build_prediction_standings(matches_df)

    groups = []

    if official_standings_df is not None and not official_standings_df.empty:
        if "groep" in official_standings_df.columns:
            groups += official_standings_df["groep"].dropna().astype(str).unique().tolist()

    if predicted_standings_df is not None and not predicted_standings_df.empty:
        if "groep" in predicted_standings_df.columns:
            groups += predicted_standings_df["groep"].dropna().astype(str).unique().tolist()

    groups = sorted(set([g for g in groups if g.strip() != ""]))

    if not groups:
        st.info("Nog geen groepsstanden beschikbaar.")
        return

    selected_group = st.selectbox(
        "Groep",
        groups,
        key="standings_group_select",
    )

    predicted_group = None
    official_group = None

    if predicted_standings_df is not None and not predicted_standings_df.empty:
        predicted_group = predicted_standings_df[
            predicted_standings_df["groep"].astype(str) == str(selected_group)
        ].copy()

    if official_standings_df is not None and not official_standings_df.empty:
        official_group = official_standings_df[
            official_standings_df["groep"].astype(str) == str(selected_group)
        ].copy()

    st.markdown(f"### Groep {selected_group}")

    col_pred, col_real = st.columns(2, gap="medium")

    with col_pred:
        show_single_standings("#### Mijn voorspelde stand", predicted_group)

    with col_real:
        show_single_standings("#### Officiële stand", official_group)
