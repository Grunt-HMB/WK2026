import pandas as pd
from modules.utils import safe_int, result_from_score


def clean_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def ensure_column(df, col):
    if col not in df.columns:
        df[col] = ""
    return df


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
    users_df = clean_columns(users_df)
    matches_df = clean_columns(matches_df)
    predictions_df = clean_columns(predictions_df)
    results_df = clean_columns(results_df)

    for col in ["user_id", "naam"]:
        users_df = ensure_column(users_df, col)

    for col in ["match_id", "groep", "team1", "team2"]:
        matches_df = ensure_column(matches_df, col)

    for col in ["user_id", "match_id", "prediction", "score1", "score2"]:
        predictions_df = ensure_column(predictions_df, col)

    for col in ["match_id", "real_team1", "real_team2"]:
        results_df = ensure_column(results_df, col)

    if predictions_df.empty or results_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    users_df["user_id"] = users_df["user_id"].astype(str).str.strip()
    predictions_df["user_id"] = predictions_df["user_id"].astype(str).str.strip()

    matches_df["match_id"] = matches_df["match_id"].astype(str).str.strip()
    predictions_df["match_id"] = predictions_df["match_id"].astype(str).str.strip()
    results_df["match_id"] = results_df["match_id"].astype(str).str.strip()

    merged = predictions_df.merge(
        results_df,
        on="match_id",
        how="inner",
        suffixes=("", "_result"),
    )

    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    if "user_id" not in merged.columns and "user_id_x" in merged.columns:
        merged["user_id"] = merged["user_id_x"]

    merged = merged.merge(
        matches_df,
        on="match_id",
        how="left",
        suffixes=("", "_match"),
    )

    if "user_id" not in merged.columns and "user_id_x" in merged.columns:
        merged["user_id"] = merged["user_id_x"]

    merged["user_id"] = merged["user_id"].astype(str).str.strip()

    users_small = users_df[["user_id", "naam"]].copy()
    users_small["user_id"] = users_small["user_id"].astype(str).str.strip()

    merged = merged.merge(
        users_small,
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
