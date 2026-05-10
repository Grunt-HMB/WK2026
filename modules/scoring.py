import re
import pandas as pd

from modules.utils import result_from_score


def safe_int(value, default=None):
    try:
        if pd.isna(value):
            return default

        text = str(value).strip()

        if text == "":
            return default

        return int(float(text.replace(",", ".")))

    except Exception:
        return default


GROUPS = list("ABCDEFGHIJKL")
GROUP_MATCH_COUNT_TOTAL = 72

KNOCKOUT_TEAM_POINTS = 5
RESULT_POINTS = 3


def clean_df(df):
    if df is None:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


def ensure_cols(df, cols):
    df = df.copy()

    for col in cols:
        if col not in df.columns:
            df[col] = ""

    return df


def norm_id(value):
    return str(value or "").strip()


def norm_prediction(value):
    value = str(value or "").strip().upper()

    if value in ["X1", "X2"]:
        return "X"

    return value


def is_group_stage(row):
    stage = str(row.get("stage", "")).strip().lower()
    groep = str(row.get("groep", "")).strip().upper()

    if stage.startswith("group "):
        return True

    return groep in GROUPS


def is_knockout_stage(row):
    return not is_group_stage(row)


def get_group(row):
    stage = str(row.get("stage", "")).strip().upper()
    groep = str(row.get("groep", "")).strip().upper()

    match = re.search(r"GROUP\s+([A-L])", stage)

    if match:
        return match.group(1)

    if groep in GROUPS:
        return groep

    return ""


def is_played(row):
    score1 = str(row.get("score1", "")).strip()
    score2 = str(row.get("score2", "")).strip()

    return score1 != "" and score2 != ""


def get_group_matches(matches_df, group):
    return matches_df[
        matches_df.apply(
            lambda row: is_group_stage(row) and get_group(row) == group,
            axis=1,
        )
    ].copy()


def group_is_complete(matches_df, group):
    group_matches = get_group_matches(matches_df, group)

    if group_matches.empty:
        return False

    return group_matches.apply(is_played, axis=1).all()


def all_groups_complete(matches_df):
    group_matches = matches_df[
        matches_df.apply(is_group_stage, axis=1)
    ].copy()

    if group_matches.empty:
        return False

    played_count = int(group_matches.apply(is_played, axis=1).sum())

    if played_count < GROUP_MATCH_COUNT_TOTAL:
        return False

    for group in GROUPS:
        if not group_is_complete(matches_df, group):
            return False

    return True


def calculate_match_result_points(prediction, real1, real2):
    prediction = norm_prediction(prediction)

    real1 = safe_int(real1)
    real2 = safe_int(real2)

    if real1 is None or real2 is None:
        return 0

    real_result = result_from_score(real1, real2)

    if prediction == real_result:
        return RESULT_POINTS

    return 0


def calculate_group_standings(matches_df):
    tables = {}

    group_matches = matches_df[
        matches_df.apply(is_group_stage, axis=1)
    ].copy()

    for _, row in group_matches.iterrows():
        group = get_group(row)

        if not group:
            continue

        team1 = str(row.get("team1", "")).strip()
        team2 = str(row.get("team2", "")).strip()

        if not team1 or not team2:
            continue

        if group not in tables:
            tables[group] = {}

        for team in [team1, team2]:
            if team not in tables[group]:
                tables[group][team] = {
                    "groep": group,
                    "team": team,
                    "played": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_for": 0,
                    "goals_against": 0,
                    "goal_diff": 0,
                    "points": 0,
                }

        if not is_played(row):
            continue

        score1 = safe_int(row.get("score1", ""), 0)
        score2 = safe_int(row.get("score2", ""), 0)

        tables[group][team1]["played"] += 1
        tables[group][team2]["played"] += 1

        tables[group][team1]["goals_for"] += score1
        tables[group][team1]["goals_against"] += score2

        tables[group][team2]["goals_for"] += score2
        tables[group][team2]["goals_against"] += score1

        tables[group][team1]["goal_diff"] = (
            tables[group][team1]["goals_for"]
            - tables[group][team1]["goals_against"]
        )

        tables[group][team2]["goal_diff"] = (
            tables[group][team2]["goals_for"]
            - tables[group][team2]["goals_against"]
        )

        if score1 > score2:
            tables[group][team1]["wins"] += 1
            tables[group][team1]["points"] += 3
            tables[group][team2]["losses"] += 1

        elif score2 > score1:
            tables[group][team2]["wins"] += 1
            tables[group][team2]["points"] += 3
            tables[group][team1]["losses"] += 1

        else:
            tables[group][team1]["draws"] += 1
            tables[group][team2]["draws"] += 1
            tables[group][team1]["points"] += 1
            tables[group][team2]["points"] += 1

    all_rows = []

    for group, teams in tables.items():
        df = pd.DataFrame(list(teams.values()))

        df = df.sort_values(
            ["points", "goal_diff", "goals_for", "wins", "team"],
            ascending=[False, False, False, False, True],
            kind="stable",
        ).reset_index(drop=True)

        df["position"] = range(1, len(df) + 1)
        all_rows.append(df)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)


def calculate_user_predicted_group_standings(matches_df, user_predictions):
    predicted_matches = matches_df.copy()

    for index, row in predicted_matches.iterrows():
        if not is_group_stage(row):
            continue

        match_id = norm_id(row.get("match_id"))
        prediction = norm_prediction(user_predictions.get(match_id, ""))

        if prediction == "1":
            predicted_matches.at[index, "score1"] = 1
            predicted_matches.at[index, "score2"] = 0

        elif prediction == "2":
            predicted_matches.at[index, "score1"] = 0
            predicted_matches.at[index, "score2"] = 1

        elif prediction == "X":
            predicted_matches.at[index, "score1"] = 1
            predicted_matches.at[index, "score2"] = 1

        else:
            predicted_matches.at[index, "score1"] = ""
            predicted_matches.at[index, "score2"] = ""

    return calculate_group_standings(predicted_matches)


def get_team_by_position(standings_df, group, position):
    if standings_df.empty:
        return ""

    row = standings_df[
        (standings_df["groep"].astype(str).str.upper() == str(group).upper())
        & (standings_df["position"] == position)
    ]

    if row.empty:
        return ""

    return str(row.iloc[0]["team"])


def calculate_best_thirds(standings_df):
    if standings_df.empty:
        return pd.DataFrame()

    thirds = standings_df[standings_df["position"] == 3].copy()

    if thirds.empty:
        return pd.DataFrame()

    thirds = thirds.sort_values(
        ["points", "goal_diff", "goals_for", "wins", "team"],
        ascending=[False, False, False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    thirds["third_rank"] = range(1, len(thirds) + 1)
    thirds["qualified"] = thirds["third_rank"] <= 8

    return thirds


def resolve_best_third(best_thirds_df, allowed_groups):
    if best_thirds_df.empty:
        return ""

    allowed_groups = [str(g).upper() for g in allowed_groups]

    possible = best_thirds_df[
        (best_thirds_df["qualified"] == True)
        & (best_thirds_df["groep"].astype(str).str.upper().isin(allowed_groups))
    ].copy()

    if possible.empty:
        return ""

    possible = possible.sort_values("third_rank", ascending=True)
    return str(possible.iloc[0]["team"])


def normalize_slot(slot):
    original = str(slot or "").strip()
    normalized = original.upper().replace(" ", "")

    normalized = normalized.replace("EERSTEGROEP", "1")
    normalized = normalized.replace("TWEEDEGROEP", "2")
    normalized = normalized.replace("DERDEGROEP", "3")
    normalized = normalized.replace("WINNAAR", "W")
    normalized = normalized.replace("VERLIEZER", "L")

    return original, normalized


def resolve_slot(slot, standings_df, best_thirds_df, results_by_match, matches_df, allow_best_thirds):
    original, normalized = normalize_slot(slot)

    if re.fullmatch(r"1[A-L]", normalized):
        group = normalized[1]

        if not group_is_complete(matches_df, group):
            return original

        return get_team_by_position(standings_df, group, 1) or original

    if re.fullmatch(r"2[A-L]", normalized):
        group = normalized[1]

        if not group_is_complete(matches_df, group):
            return original

        return get_team_by_position(standings_df, group, 2) or original

    if re.fullmatch(r"3[A-L]+", normalized):
        if not allow_best_thirds:
            return original

        return resolve_best_third(best_thirds_df, list(normalized[1:])) or original

    if re.fullmatch(r"W\d+", normalized):
        return results_by_match.get(normalized, original)

    if re.fullmatch(r"L\d+", normalized):
        return results_by_match.get(normalized, original)

    return original


def get_base_team(row, side):
    placeholder_col = f"{side}_placeholder"

    placeholder = str(row.get(placeholder_col, "")).strip()

    if placeholder:
        return placeholder

    return str(row.get(side, "")).strip()


def get_winner_from_prediction(row, user_predictions):
    match_id = norm_id(row.get("match_id"))
    prediction = str(user_predictions.get(match_id, "")).upper().strip()

    team1 = str(row.get("team1", "")).strip()
    team2 = str(row.get("team2", "")).strip()

    if prediction in ["1", "X1"]:
        return team1

    if prediction in ["2", "X2"]:
        return team2

    return ""


def get_loser_from_prediction(row, user_predictions):
    match_id = norm_id(row.get("match_id"))
    prediction = str(user_predictions.get(match_id, "")).upper().strip()

    team1 = str(row.get("team1", "")).strip()
    team2 = str(row.get("team2", "")).strip()

    if prediction in ["1", "X1"]:
        return team2

    if prediction in ["2", "X2"]:
        return team1

    return ""


def build_results_by_prediction(predicted_df, user_predictions):
    results = {}

    for _, row in predicted_df.iterrows():
        match_id = norm_id(row.get("match_id"))

        if not match_id:
            continue

        winner = get_winner_from_prediction(row, user_predictions)
        loser = get_loser_from_prediction(row, user_predictions)

        if winner:
            results[f"W{match_id}"] = winner

        if loser:
            results[f"L{match_id}"] = loser

    return results


def build_predicted_bracket(matches_df, user_predictions):
    predicted = matches_df.copy()

    for index, row in predicted.iterrows():
        if is_knockout_stage(row):
            predicted.at[index, "team1"] = get_base_team(row, "team1")
            predicted.at[index, "team2"] = get_base_team(row, "team2")

    standings_df = calculate_user_predicted_group_standings(
        predicted,
        user_predictions,
    )

    if all_groups_complete_from_predictions(matches_df, user_predictions):
        best_thirds_df = calculate_best_thirds(standings_df)
        allow_best_thirds = True
    else:
        best_thirds_df = pd.DataFrame()
        allow_best_thirds = False

    for _ in range(8):
        results_by_match = build_results_by_prediction(predicted, user_predictions)

        for index, row in predicted.iterrows():
            if is_group_stage(row):
                continue

            team1_slot = str(row.get("team1", "")).strip()
            team2_slot = str(row.get("team2", "")).strip()

            predicted.at[index, "team1"] = resolve_slot(
                team1_slot,
                standings_df,
                best_thirds_df,
                results_by_match,
                predicted,
                allow_best_thirds,
            )

            predicted.at[index, "team2"] = resolve_slot(
                team2_slot,
                standings_df,
                best_thirds_df,
                results_by_match,
                predicted,
                allow_best_thirds,
            )

    return predicted


def all_groups_complete_from_predictions(matches_df, user_predictions):
    group_matches = matches_df[
        matches_df.apply(is_group_stage, axis=1)
    ].copy()

    if group_matches.empty:
        return False

    completed = 0

    for _, row in group_matches.iterrows():
        match_id = norm_id(row.get("match_id"))
        prediction = norm_prediction(user_predictions.get(match_id, ""))

        if prediction in ["1", "X", "2"]:
            completed += 1

    return completed >= GROUP_MATCH_COUNT_TOTAL


def get_winner_from_real_result(row):
    score1 = safe_int(row.get("score1"))
    score2 = safe_int(row.get("score2"))

    if score1 is None or score2 is None:
        return ""

    team1 = str(row.get("team1", "")).strip()
    team2 = str(row.get("team2", "")).strip()

    if score1 > score2:
        return team1

    if score2 > score1:
        return team2

    winner = str(row.get("winner", "")).strip()
    return winner


def get_loser_from_real_result(row):
    winner = get_winner_from_real_result(row)

    team1 = str(row.get("team1", "")).strip()
    team2 = str(row.get("team2", "")).strip()

    if winner == team1:
        return team2

    if winner == team2:
        return team1

    return ""


def build_results_by_real_result(real_df):
    results = {}

    for _, row in real_df.iterrows():
        match_id = norm_id(row.get("match_id"))

        if not match_id:
            continue

        winner = get_winner_from_real_result(row)
        loser = get_loser_from_real_result(row)

        if winner:
            results[f"W{match_id}"] = winner

        if loser:
            results[f"L{match_id}"] = loser

    return results


def build_real_bracket(matches_df):
    real = matches_df.copy()

    for index, row in real.iterrows():
        if is_knockout_stage(row):
            real.at[index, "team1"] = get_base_team(row, "team1")
            real.at[index, "team2"] = get_base_team(row, "team2")

    standings_df = calculate_group_standings(real)

    if all_groups_complete(real):
        best_thirds_df = calculate_best_thirds(standings_df)
        allow_best_thirds = True
    else:
        best_thirds_df = pd.DataFrame()
        allow_best_thirds = False

    for _ in range(8):
        results_by_match = build_results_by_real_result(real)

        for index, row in real.iterrows():
            if is_group_stage(row):
                continue

            team1_slot = str(row.get("team1", "")).strip()
            team2_slot = str(row.get("team2", "")).strip()

            real.at[index, "team1"] = resolve_slot(
                team1_slot,
                standings_df,
                best_thirds_df,
                results_by_match,
                real,
                allow_best_thirds,
            )

            real.at[index, "team2"] = resolve_slot(
                team2_slot,
                standings_df,
                best_thirds_df,
                results_by_match,
                real,
                allow_best_thirds,
            )

    return real


def calculate_knockout_team_points(predicted_bracket, real_bracket):
    points = 0

    predicted_lookup = predicted_bracket.set_index("match_id").to_dict("index")
    real_lookup = real_bracket.set_index("match_id").to_dict("index")

    for match_id, real_row in real_lookup.items():
        if match_id not in predicted_lookup:
            continue

        if not is_knockout_stage(real_row):
            continue

        predicted_row = predicted_lookup[match_id]

        real_team1 = str(real_row.get("team1", "")).strip()
        real_team2 = str(real_row.get("team2", "")).strip()

        predicted_team1 = str(predicted_row.get("team1", "")).strip()
        predicted_team2 = str(predicted_row.get("team2", "")).strip()

        if re.match(r"^[123][A-L]+$", real_team1.upper()) or re.match(r"^[WL]\d+$", real_team1.upper()):
            continue

        if re.match(r"^[123][A-L]+$", real_team2.upper()) or re.match(r"^[WL]\d+$", real_team2.upper()):
            continue

        if real_team1 and predicted_team1 and real_team1 == predicted_team1:
            points += KNOCKOUT_TEAM_POINTS

        if real_team2 and predicted_team2 and real_team2 == predicted_team2:
            points += KNOCKOUT_TEAM_POINTS

    return points


def build_scoreboard(users_df, matches_df, predictions_df, results_df):
    users_df = clean_df(users_df)
    matches_df = clean_df(matches_df)
    predictions_df = clean_df(predictions_df)
    results_df = clean_df(results_df)

    users_df = ensure_cols(users_df, ["user_id", "naam"])
    matches_df = ensure_cols(
        matches_df,
        [
            "match_id",
            "stage",
            "groep",
            "team1",
            "team2",
            "score1",
            "score2",
            "winner",
            "team1_placeholder",
            "team2_placeholder",
        ],
    )
    predictions_df = ensure_cols(
        predictions_df,
        ["user_id", "match_id", "prediction", "score1", "score2", "status"],
    )
    results_df = ensure_cols(results_df, ["match_id", "real_team1", "real_team2"])

    users_df["user_id"] = users_df["user_id"].astype(str).str.strip()
    matches_df["match_id"] = matches_df["match_id"].astype(str).str.strip()
    predictions_df["user_id"] = predictions_df["user_id"].astype(str).str.strip()
    predictions_df["match_id"] = predictions_df["match_id"].astype(str).str.strip()
    results_df["match_id"] = results_df["match_id"].astype(str).str.strip()

    if predictions_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    result_scores = results_df.set_index("match_id").to_dict("index")

    rows = []
    detail_rows = []

    real_bracket = build_real_bracket(matches_df)

    for _, user in users_df.iterrows():
        user_id = str(user.get("user_id", "")).strip()
        naam = str(user.get("naam", user_id)).strip()

        user_preds_df = predictions_df[predictions_df["user_id"] == user_id].copy()

        user_points = 0
        scored_matches = 0

        if not user_preds_df.empty:
            user_predictions = dict(
                zip(
                    user_preds_df["match_id"].astype(str),
                    user_preds_df["prediction"].astype(str),
                )
            )

            predicted_bracket = build_predicted_bracket(
                matches_df,
                user_predictions,
            )

            for _, pred_row in user_preds_df.iterrows():
                match_id = str(pred_row.get("match_id", "")).strip()

                if match_id not in result_scores:
                    continue

                result_row = result_scores[match_id]

                points = calculate_match_result_points(
                    pred_row.get("prediction", ""),
                    result_row.get("real_team1", ""),
                    result_row.get("real_team2", ""),
                )

                user_points += points

                if points > 0:
                    scored_matches += 1

                detail_rows.append(
                    {
                        "user_id": user_id,
                        "naam": naam,
                        "match_id": match_id,
                        "type": "uitslag",
                        "punten": points,
                    }
                )

            ko_points = 0

            if all_groups_complete(matches_df):
                ko_points = calculate_knockout_team_points(
                    predicted_bracket,
                    real_bracket,
                )
                user_points += ko_points

            detail_rows.append(
                {
                    "user_id": user_id,
                    "naam": naam,
                    "match_id": "",
                    "type": "knockout_ploegen",
                    "punten": ko_points,
                }
            )

        rows.append(
            {
                "naam": naam,
                "totaal_punten": user_points,
                "wedstrijden": scored_matches,
            }
        )

    scoreboard = pd.DataFrame(rows)

    scoreboard = scoreboard.sort_values(
        ["totaal_punten", "wedstrijden", "naam"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    return scoreboard, pd.DataFrame(detail_rows)
