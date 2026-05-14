import pandas as pd
import streamlit as st

from modules.knockout_engine import calculate_group_standings


POINTS_RESULT = 3
POINTS_GROUP_POSITION = 5


def to_int_or_none(value):
    try:
        txt = str(value or "").strip()
        if txt == "":
            return None
        return int(float(txt))
    except Exception:
        return None


def result_from_score(score1, score2):
    s1 = to_int_or_none(score1)
    s2 = to_int_or_none(score2)

    if s1 is None or s2 is None:
        return ""

    if s1 > s2:
        return "1"

    if s1 < s2:
        return "2"

    return "X"


def prediction_to_score(prediction):
    prediction = str(prediction or "").upper().strip()

    if prediction == "1":
        return "1", "0"

    if prediction == "X":
        return "0", "0"

    if prediction == "2":
        return "0", "1"

    return "", ""


def ensure_columns(df, columns):
    if df is None:
        df = pd.DataFrame()

    df = df.copy()

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df


def build_match_points(predictions_df, results_df):
    predictions_df = ensure_columns(
        predictions_df,
        ["user_id", "match_id", "prediction"],
    )

    results_df = ensure_columns(
        results_df,
        ["match_id", "real_team1", "real_team2"],
    )

    if predictions_df.empty or results_df.empty:
        return pd.DataFrame(
            columns=[
                "user_id",
                "gespeeld",
                "juiste_resultaten",
                "punten_resultaat",
            ]
        )

    predictions_df["user_id"] = predictions_df["user_id"].astype(str).str.strip()
    predictions_df["match_id"] = predictions_df["match_id"].astype(str).str.strip()
    predictions_df["prediction"] = predictions_df["prediction"].astype(str).str.upper().str.strip()

    results_df["match_id"] = results_df["match_id"].astype(str).str.strip()

    results_df["official_result"] = results_df.apply(
        lambda row: result_from_score(
            row.get("real_team1", ""),
            row.get("real_team2", ""),
        ),
        axis=1,
    )

    results_df = results_df[
        results_df["official_result"].isin(["1", "X", "2"])
    ].copy()

    if results_df.empty:
        return pd.DataFrame(
            columns=[
                "user_id",
                "gespeeld",
                "juiste_resultaten",
                "punten_resultaat",
            ]
        )

    merged = predictions_df.merge(
        results_df[["match_id", "official_result"]],
        on="match_id",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(
            columns=[
                "user_id",
                "gespeeld",
                "juiste_resultaten",
                "punten_resultaat",
            ]
        )

    merged["correct_result"] = merged["prediction"] == merged["official_result"]
    merged["punten_resultaat"] = merged["correct_result"].astype(int) * POINTS_RESULT

    return merged.groupby("user_id", as_index=False).agg(
        gespeeld=("match_id", "count"),
        juiste_resultaten=("correct_result", "sum"),
        punten_resultaat=("punten_resultaat", "sum"),
    )


def build_predicted_group_standings_for_user(matches_df, user_predictions_df):
    if matches_df is None or matches_df.empty:
        return pd.DataFrame()

    predicted_matches = matches_df.copy()

    for col in ["score1", "score2"]:
        if col not in predicted_matches.columns:
            predicted_matches[col] = ""

        predicted_matches[col] = predicted_matches[col].astype("object")
        predicted_matches[col] = ""

    prediction_map = {}

    if user_predictions_df is not None and not user_predictions_df.empty:
        for _, row in user_predictions_df.iterrows():
            match_id = str(row.get("match_id", "")).strip()
            prediction = str(row.get("prediction", "")).upper().strip()

            if match_id and prediction in ["1", "X", "2"]:
                prediction_map[match_id] = prediction

    for idx, row in predicted_matches.iterrows():
        match_id = str(row.get("match_id", "")).strip()
        prediction = prediction_map.get(match_id, "")

        score1, score2 = prediction_to_score(prediction)

        predicted_matches.at[idx, "score1"] = score1
        predicted_matches.at[idx, "score2"] = score2

    return calculate_group_standings(predicted_matches)


def build_group_position_points(users_df, predictions_df, matches_df, official_standings_df):
    users_df = ensure_columns(users_df, ["user_id"])
    predictions_df = ensure_columns(predictions_df, ["user_id", "match_id", "prediction"])
    official_standings_df = ensure_columns(
        official_standings_df,
        ["groep", "team", "position"],
    )

    if (
        users_df.empty
        or predictions_df.empty
        or matches_df is None
        or matches_df.empty
        or official_standings_df.empty
    ):
        return pd.DataFrame(
            columns=[
                "user_id",
                "juiste_pouleposities",
                "punten_poulepositie",
            ]
        )

    users_df["user_id"] = users_df["user_id"].astype(str).str.strip()
    predictions_df["user_id"] = predictions_df["user_id"].astype(str).str.strip()

    official = official_standings_df.copy()
    official["groep"] = official["groep"].astype(str).str.strip()
    official["team"] = official["team"].astype(str).str.strip()
    official["position"] = official["position"].astype(str).str.strip()

    official = official[
        (official["groep"] != "")
        & (official["team"] != "")
        & (official["position"] != "")
    ].copy()

    if official.empty:
        return pd.DataFrame(
            columns=[
                "user_id",
                "juiste_pouleposities",
                "punten_poulepositie",
            ]
        )

    rows = []

    for user_id in users_df["user_id"].tolist():
        user_predictions = predictions_df[
            predictions_df["user_id"] == str(user_id)
        ].copy()

        predicted_standings = build_predicted_group_standings_for_user(
            matches_df=matches_df,
            user_predictions_df=user_predictions,
        )

        if predicted_standings is None or predicted_standings.empty:
            rows.append({
                "user_id": str(user_id),
                "juiste_pouleposities": 0,
                "punten_poulepositie": 0,
            })
            continue

        predicted = predicted_standings.copy()

        if "groep" not in predicted.columns or "team" not in predicted.columns or "position" not in predicted.columns:
            rows.append({
                "user_id": str(user_id),
                "juiste_pouleposities": 0,
                "punten_poulepositie": 0,
            })
            continue

        predicted["groep"] = predicted["groep"].astype(str).str.strip()
        predicted["team"] = predicted["team"].astype(str).str.strip()
        predicted["position"] = predicted["position"].astype(str).str.strip()

        compare = predicted[["groep", "team", "position"]].merge(
            official[["groep", "team", "position"]],
            on=["groep", "team"],
            how="inner",
            suffixes=("_pred", "_official"),
        )

        if compare.empty:
            correct_positions = 0
        else:
            correct_positions = int(
                (
                    compare["position_pred"].astype(str)
                    == compare["position_official"].astype(str)
                ).sum()
            )

        rows.append({
            "user_id": str(user_id),
            "juiste_pouleposities": correct_positions,
            "punten_poulepositie": correct_positions * POINTS_GROUP_POSITION,
        })

    return pd.DataFrame(rows)


def build_scoreboard(users_df, predictions_df, results_df, matches_df, official_standings_df):
    users_df = ensure_columns(
        users_df,
        ["user_id", "naam", "team_name"],
    )

    users_df["user_id"] = users_df["user_id"].astype(str).str.strip()

    match_points = build_match_points(
        predictions_df=predictions_df,
        results_df=results_df,
    )

    position_points = build_group_position_points(
        users_df=users_df,
        predictions_df=predictions_df,
        matches_df=matches_df,
        official_standings_df=official_standings_df,
    )

    summary = users_df[["user_id", "naam", "team_name"]].copy()

    summary = summary.merge(
        match_points,
        on="user_id",
        how="left",
    )

    summary = summary.merge(
        position_points,
        on="user_id",
        how="left",
    )

    for col in [
        "gespeeld",
        "juiste_resultaten",
        "punten_resultaat",
        "juiste_pouleposities",
        "punten_poulepositie",
    ]:
        if col not in summary.columns:
            summary[col] = 0

        summary[col] = summary[col].fillna(0).astype(int)

    summary["punten"] = (
        summary["punten_resultaat"]
        + summary["punten_poulepositie"]
    )

    summary["naam"] = summary["naam"].fillna(summary["user_id"])
    summary["team_name"] = summary["team_name"].fillna("")

    summary = summary.sort_values(
        [
            "punten",
            "punten_resultaat",
            "punten_poulepositie",
            "juiste_resultaten",
            "juiste_pouleposities",
            "naam",
        ],
        ascending=[False, False, False, False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    summary["positie"] = range(1, len(summary) + 1)

    return summary[
        [
            "positie",
            "naam",
            "team_name",
            "gespeeld",
            "juiste_resultaten",
            "punten_resultaat",
            "juiste_pouleposities",
            "punten_poulepositie",
            "punten",
        ]
    ]


def show_scoreboard(users_df, predictions_df, results_df, matches_df, official_standings_df):
    st.subheader("🏆 Scoreboard")

    st.caption(
        f"Puntentelling: {POINTS_RESULT} punten voor juiste 1/X/2, "
        f"+ {POINTS_GROUP_POSITION} punten als de juiste ploeg op de juiste plaats staat na de poulefase."
    )

    scoreboard_df = build_scoreboard(
        users_df=users_df,
        predictions_df=predictions_df,
        results_df=results_df,
        matches_df=matches_df,
        official_standings_df=official_standings_df,
    )

    if scoreboard_df.empty:
        st.info("Nog geen scoreboard beschikbaar.")
        return

    display_df = scoreboard_df.rename(
        columns={
            "positie": "#",
            "naam": "Naam",
            "team_name": "Ploeg",
            "gespeeld": "Wedstr.",
            "juiste_resultaten": "Juist 1/X/2",
            "punten_resultaat": "Ptn 1/X/2",
            "juiste_pouleposities": "Juiste pos.",
            "punten_poulepositie": "Ptn pos.",
            "punten": "Totaal",
        }
    )

    st.table(display_df)
