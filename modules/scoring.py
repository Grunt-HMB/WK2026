import pandas as pd
from modules.utils import safe_int, result_from_score


def clean_df(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def ensure_cols(df, cols):
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    return df


def normalize_ids(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
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
    users_df = clean_df(users_df)
    matches_df = clean_df(matches_df)
    predictions_df = clean_df(predictions_df)
    results_df = clean_df(results_df)

    users_df = ensure_cols(users_df, ["user_id", "naam"])
    matches_df = ensure_cols(matches_df, ["match_id", "groep", "team1", "team2"])
    predictions_df = ensure_cols(
        predictions_df,
        ["user_id", "match_id", "prediction", "score1", "score2", "status"],
    )
    results_df = ensure_cols(results_df, ["match_id", "real_team1", "real_team2"])

    users_df = normalize_ids(users_df, ["user_id"])
    matches_df = normalize_ids(matches_df, ["match_id"])
    predictions_df = normalize_ids(predictions_df, ["user_id", "match_id"])
    results_df = normalize_ids(results_df, ["match_id"])

    if predictions_df.empty or results_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    predictions_clean = predictions_df[
        ["user_id", "match_id", "prediction", "score1", "score2", "status"]
    ].copy()

    results_clean = results_df[
        ["match_id", "real_team1", "real_team2"]
    ].copy()

    matches_clean = matches_df[
        ["match_id", "groep", "team1", "team2"]
    ].copy()

    users_clean = users_df[
        ["user_id", "naam"]
    ].copy()

    merged = pd.merge(
        predictions_clean,
        results_clean,
        on="match_id",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    merged = pd.merge(
        merged,
        matches_clean,
        on="match_id",
        how="left",
    )

    merged = pd.merge(
        merged,
        users_clean,
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
