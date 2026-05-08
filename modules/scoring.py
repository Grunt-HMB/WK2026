import pandas as pd
from modules.utils import safe_int, result_from_score


def normalize_key_columns(users_df, matches_df, predictions_df, results_df):
    users_df = users_df.copy()
    matches_df = matches_df.copy()
    predictions_df = predictions_df.copy()
    results_df = results_df.copy()

    for df in [users_df, predictions_df]:
        if "user_id" in df.columns:
            df["user_id"] = df["user_id"].astype(str).str.strip()

    for df in [matches_df, predictions_df, results_df]:
        if "match_id" in df.columns:
            df["match_id"] = df["match_id"].astype(str).str.strip()

    return users_df, matches_df, predictions_df, results_df


def calculate_points(row):
    prediction = str(row.get("prediction", "")).strip().upper()

    real1 = safe_int(row.get("real_team1"))
    real2 = safe_int(row.get("real_team2"))

    if real1 is None or real2 is None:
        return 0

    real_result = result_from_score(real1, real2)

    points = 0

    if prediction == real_result:
        points += 3

    pred1 = safe_int(row.get("score1"))
    pred2 = safe_int(row.get("score2"))

    if pred1 is not None and pred2 is not None:
        if pred1 == real1 and pred2 == real2:
            points += 2
        elif (pred1 - pred2) == (real1 - real2):
            points += 1

    return points


def build_scoreboard(users_df, matches_df, predictions_df, results_df):
    if predictions_df.empty or results_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    users_df, matches_df, predictions_df, results_df = normalize_key_columns(
        users_df,
        matches_df,
        predictions_df,
        results_df,
    )

    required_predictions = ["user_id", "match_id", "prediction"]
    required_results = ["match_id", "real_team1", "real_team2"]
    required_users = ["user_id", "naam"]

    for col in required_predictions:
        if col not in predictions_df.columns:
            return pd.DataFrame(), pd.DataFrame()

    for col in required_results:
        if col not in results_df.columns:
            return pd.DataFrame(), pd.DataFrame()

    for col in required_users:
        if col not in users_df.columns:
            return pd.DataFrame(), pd.DataFrame()

    merged = predictions_df.merge(
        results_df,
        on="match_id",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    merged = merged.merge(
        matches_df,
        on="match_id",
        how="left",
        suffixes=("", "_match"),
    )

    merged = merged.merge(
        users_df[["user_id", "naam"]],
        on="user_id",
        how="left",
    )

    merged["naam"] = merged["naam"].fillna("Onbekend")
    merged["punten"] = merged.apply(calculate_points, axis=1)

    scoreboard = (
        merged.groupby("naam", as_index=False)
        .agg(
            totaal_punten=("punten", "sum"),
            wedstrijden=("match_id", "count"),
        )
        .sort_values(["totaal_punten", "naam"], ascending=[False, True])
    )

    return scoreboard, merged
