import re
import streamlit as st

from modules.wedstrijd_helpers import (
    get_value,
    is_group_stage,
)
from modules.wedstrijd_standings import (
    calculate_group_standings,
    calculate_best_thirds,
    get_team_by_position,
    resolve_third_team,
)


def get_selected_prediction(match_id):
    current = st.session_state.get("local_predictions", {}).get(str(match_id), {})
    return str(current.get("prediction", "")).upper().strip()


def get_match_winner_from_prediction(row):
    match_id = str(get_value(row, "match_id", "wedstrijd_id", "id")).strip()
    prediction = get_selected_prediction(match_id)

    team1 = str(get_value(row, "team1", "land1", "thuisploeg")).strip()
    team2 = str(get_value(row, "team2", "land2", "uitploeg")).strip()

    if prediction == "1":
        return team1

    if prediction == "2":
        return team2

    if prediction == "X1":
        return team1

    if prediction == "X2":
        return team2

    return ""


def get_match_loser_from_prediction(row):
    match_id = str(get_value(row, "match_id", "wedstrijd_id", "id")).strip()
    prediction = get_selected_prediction(match_id)

    team1 = str(get_value(row, "team1", "land1", "thuisploeg")).strip()
    team2 = str(get_value(row, "team2", "land2", "uitploeg")).strip()

    if prediction == "1":
        return team2

    if prediction == "2":
        return team1

    if prediction == "X1":
        return team2

    if prediction == "X2":
        return team1

    return ""


def build_results_by_match(wedstrijden):
    results = {}

    for _, row in wedstrijden.iterrows():
        match_id = str(get_value(row, "match_id")).strip()

        if match_id == "":
            continue

        winner = get_match_winner_from_prediction(row)
        loser = get_match_loser_from_prediction(row)

        if winner:
            results[f"W{match_id}"] = winner

        if loser:
            results[f"L{match_id}"] = loser

    return results


def resolve_slot(slot, standings_df, best_thirds_df, results_by_match):
    original = str(slot or "").strip()
    normalized = original.upper().replace(" ", "")

    if re.fullmatch(r"1[A-L]", normalized):
        return get_team_by_position(standings_df, normalized[1], 1) or original

    if re.fullmatch(r"2[A-L]", normalized):
        return get_team_by_position(standings_df, normalized[1], 2) or original

    if re.fullmatch(r"3[A-L]+", normalized):
        allowed_groups = list(normalized[1:])
        return resolve_third_team(best_thirds_df, allowed_groups) or original

    if re.fullmatch(r"W\d+", normalized):
        return results_by_match.get(normalized, original)

    if re.fullmatch(r"L\d+", normalized):
        return results_by_match.get(normalized, original)

    return original


def resolve_knockout_teams(wedstrijden):
    wedstrijden = wedstrijden.copy()

    standings_df = calculate_group_standings(wedstrijden)
    best_thirds_df = calculate_best_thirds(standings_df)

    for _ in range(6):
        results_by_match = build_results_by_match(wedstrijden)

        for index, row in wedstrijden.iterrows():
            stage = str(get_value(row, "stage")).strip()

            if is_group_stage(stage):
                continue

            team1 = str(get_value(row, "team1")).strip()
            team2 = str(get_value(row, "team2")).strip()

            wedstrijden.at[index, "team1"] = resolve_slot(
                team1,
                standings_df,
                best_thirds_df,
                results_by_match,
            )

            wedstrijden.at[index, "team2"] = resolve_slot(
                team2,
                standings_df,
                best_thirds_df,
                results_by_match,
            )

    return wedstrijden, standings_df, best_thirds_df
