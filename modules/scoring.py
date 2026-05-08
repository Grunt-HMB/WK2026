import pandas as pd
from modules.utils import safe_int, result_from_score

def calculate_points(row):
    prediction = str(row.get("prediction", ""))

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

    merged = predictions_df.merge(results_df, on="match_id", how="inner")
    merged = merged.merge(matches_df, on="match_id", how="left")
    merged = merged.merge(users_df[["user_id", "naam"]], on="user_id", how="left")

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
