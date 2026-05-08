import pandas as pd


GROUPS = list("ABCDEFGHIJKL")


ROUND_OF_32_MATCHES = {
    "M73": ("2A", "2B"),
    "M74": ("1E", "3ABCDF"),
    "M75": ("1F", "2C"),
    "M76": ("1C", "2F"),
    "M77": ("1I", "3CDFGH"),
    "M78": ("2E", "2I"),
    "M79": ("1A", "3CEFHI"),
    "M80": ("1L", "3EHIJK"),
    "M81": ("1D", "3BEFIJ"),
    "M82": ("1G", "3AEHIJ"),
    "M83": ("2K", "2L"),
    "M84": ("1H", "2J"),
    "M85": ("1B", "3EFGIJ"),
    "M86": ("1J", "2H"),
    "M87": ("1K", "3DEIJL"),
    "M88": ("2D", "2G"),
}


ROUND_OF_16_MATCHES = {
    "M89": ("W74", "W77"),
    "M90": ("W73", "W75"),
    "M91": ("W76", "W78"),
    "M92": ("W79", "W80"),
    "M93": ("W83", "W84"),
    "M94": ("W81", "W82"),
    "M95": ("W86", "W88"),
    "M96": ("W85", "W87"),
}


QUARTER_FINALS = {
    "M97": ("W89", "W90"),
    "M98": ("W93", "W94"),
    "M99": ("W91", "W92"),
    "M100": ("W95", "W96"),
}


SEMI_FINALS = {
    "M101": ("W97", "W98"),
    "M102": ("W99", "W100"),
}


FINAL_MATCHES = {
    "M103": ("L101", "L102"),
    "M104": ("W101", "W102"),
}


def safe_int(value, default=0):
    try:
        if pd.isna(value) or value == "":
            return default
        return int(value)
    except Exception:
        return default


def clean_team(value):
    return str(value or "").strip()


def is_played(row):
    return str(row.get("score1", "")).strip() != "" and str(row.get("score2", "")).strip() != ""


def get_match_winner(row):
    team1 = clean_team(row.get("team1", ""))
    team2 = clean_team(row.get("team2", ""))

    score1 = safe_int(row.get("score1", ""))
    score2 = safe_int(row.get("score2", ""))

    if score1 > score2:
        return team1
    if score2 > score1:
        return team2

    manual_winner = clean_team(row.get("winner", ""))
    return manual_winner


def get_match_loser(row):
    winner = get_match_winner(row)
    team1 = clean_team(row.get("team1", ""))
    team2 = clean_team(row.get("team2", ""))

    if winner == team1:
        return team2
    if winner == team2:
        return team1

    return ""


def calculate_base_group_table(matches_df, fifa_ranking_df=None):
    rows = []

    group_matches = matches_df[
        matches_df["groep"].astype(str).str.upper().isin(GROUPS)
    ].copy()

    teams = set()

    for _, row in group_matches.iterrows():
        teams.add(clean_team(row.get("team1", "")))
        teams.add(clean_team(row.get("team2", "")))

    teams = sorted([t for t in teams if t])

    for team in teams:
        team_matches = group_matches[
            (group_matches["team1"].astype(str) == team)
            | (group_matches["team2"].astype(str) == team)
        ]

        group = ""

        played = 0
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        points = 0

        for _, match in team_matches.iterrows():
            if not is_played(match):
                group = str(match.get("groep", "")).strip().upper()
                continue

            group = str(match.get("groep", "")).strip().upper()

            score1 = safe_int(match.get("score1", ""))
            score2 = safe_int(match.get("score2", ""))

            if clean_team(match.get("team1", "")) == team:
                gf = score1
                ga = score2
            else:
                gf = score2
                ga = score1

            played += 1
            goals_for += gf
            goals_against += ga

            if gf > ga:
                wins += 1
                points += 3
            elif gf == ga:
                draws += 1
                points += 1
            else:
                losses += 1

        rows.append({
            "groep": group,
            "team": team,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_diff": goals_for - goals_against,
            "points": points,
            "conduct_score": 0,
            "fifa_rank": 999,
            "previous_fifa_rank": 999,
        })

    table = pd.DataFrame(rows)

    if fifa_ranking_df is not None and not fifa_ranking_df.empty:
        ranking = fifa_ranking_df.copy()
        ranking["team"] = ranking["team"].astype(str).str.strip()

        table = table.merge(
            ranking[["team", "fifa_rank", "previous_fifa_rank"]],
            on="team",
            how="left",
            suffixes=("", "_rank"),
        )

        table["fifa_rank"] = table["fifa_rank_rank"].fillna(table["fifa_rank"])
        table["previous_fifa_rank"] = table["previous_fifa_rank_rank"].fillna(table["previous_fifa_rank"])

        table = table.drop(
            columns=[
                c for c in ["fifa_rank_rank", "previous_fifa_rank_rank"]
                if c in table.columns
            ]
        )

    return table


def head_to_head_stats(matches_df, teams):
    rows = []

    h2h_matches = matches_df[
        (matches_df["team1"].isin(teams))
        & (matches_df["team2"].isin(teams))
    ].copy()

    for team in teams:
        played = 0
        goals_for = 0
        goals_against = 0
        points = 0

        for _, match in h2h_matches.iterrows():
            if not is_played(match):
                continue

            score1 = safe_int(match.get("score1", ""))
            score2 = safe_int(match.get("score2", ""))

            if clean_team(match.get("team1", "")) == team:
                gf = score1
                ga = score2
            else:
                gf = score2
                ga = score1

            played += 1
            goals_for += gf
            goals_against += ga

            if gf > ga:
                points += 3
            elif gf == ga:
                points += 1

        rows.append({
            "team": team,
            "h2h_points": points,
            "h2h_goal_diff": goals_for - goals_against,
            "h2h_goals_for": goals_for,
        })

    return pd.DataFrame(rows)


def sort_group_with_fifa_rules(group_df, matches_df):
    group_df = group_df.copy()

    final_rows = []

    for points_value in sorted(group_df["points"].unique(), reverse=True):
        tied = group_df[group_df["points"] == points_value].copy()

        if len(tied) == 1:
            final_rows.append(tied)
            continue

        teams = tied["team"].tolist()
        h2h = head_to_head_stats(matches_df, teams)

        tied = tied.merge(h2h, on="team", how="left")

        tied = tied.sort_values(
            by=[
                "h2h_points",
                "h2h_goal_diff",
                "h2h_goals_for",
                "goal_diff",
                "goals_for",
                "conduct_score",
                "fifa_rank",
                "previous_fifa_rank",
            ],
            ascending=[
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
            ],
            kind="stable",
        )

        final_rows.append(tied)

    result = pd.concat(final_rows, ignore_index=True)
    result["position"] = range(1, len(result) + 1)

    return result


def calculate_group_standings(matches_df, fifa_ranking_df=None):
    base_table = calculate_base_group_table(matches_df, fifa_ranking_df)
    all_groups = []

    for group in GROUPS:
        group_df = base_table[base_table["groep"] == group].copy()

        if group_df.empty:
            continue

        group_matches = matches_df[matches_df["groep"].astype(str).str.upper() == group].copy()
        sorted_group = sort_group_with_fifa_rules(group_df, group_matches)

        all_groups.append(sorted_group)

    if not all_groups:
        return pd.DataFrame()

    return pd.concat(all_groups, ignore_index=True)


def get_team_by_position(standings_df, group, position):
    row = standings_df[
        (standings_df["groep"] == group)
        & (standings_df["position"] == position)
    ]

    if row.empty:
        return ""

    return str(row.iloc[0]["team"])


def calculate_best_thirds(standings_df):
    thirds = standings_df[standings_df["position"] == 3].copy()

    if thirds.empty:
        return pd.DataFrame()

    thirds = thirds.sort_values(
        by=[
            "points",
            "goal_diff",
            "goals_for",
            "conduct_score",
            "fifa_rank",
            "previous_fifa_rank",
        ],
        ascending=[
            False,
            False,
            False,
            False,
            True,
            True,
        ],
        kind="stable",
    ).reset_index(drop=True)

    thirds["third_rank"] = range(1, len(thirds) + 1)
    thirds["qualified_third"] = thirds["third_rank"] <= 8

    return thirds


def resolve_third_place_team(best_thirds_df, allowed_groups):
    allowed_groups = list(allowed_groups)

    possible = best_thirds_df[
        (best_thirds_df["qualified_third"] == True)
        & (best_thirds_df["groep"].isin(allowed_groups))
    ].copy()

    if possible.empty:
        return ""

    possible = possible.sort_values("third_rank", ascending=True)
    return str(possible.iloc[0]["team"])


def resolve_slot(slot, standings_df, best_thirds_df, results_by_match):
    slot = str(slot).strip().upper()

    if slot.startswith("1") and len(slot) == 2:
        return get_team_by_position(standings_df, slot[1], 1)

    if slot.startswith("2") and len(slot) == 2:
        return get_team_by_position(standings_df, slot[1], 2)

    if slot.startswith("3"):
        allowed_groups = slot[1:]
        return resolve_third_place_team(best_thirds_df, allowed_groups)

    if slot.startswith("W"):
        return results_by_match.get(slot, "")

    if slot.startswith("L"):
        return results_by_match.get(slot, "")

    return ""


def build_results_by_match(matches_df):
    results = {}

    for _, row in matches_df.iterrows():
        match_id = str(row.get("match_id", "")).upper().replace("MATCH", "M").strip()

        if not match_id:
            continue

        winner = get_match_winner(row)
        loser = get_match_loser(row)

        number = match_id.replace("M", "")

        if winner:
            results[f"W{number}"] = winner

        if loser:
            results[f"L{number}"] = loser

    return results


def apply_knockout_engine(matches_df, fifa_ranking_df=None):
    updated = matches_df.copy()

    standings_df = calculate_group_standings(updated, fifa_ranking_df)
    best_thirds_df = calculate_best_thirds(standings_df)

    results_by_match = build_results_by_match(updated)

    all_knockout = {}
    all_knockout.update(ROUND_OF_32_MATCHES)
    all_knockout.update(ROUND_OF_16_MATCHES)
    all_knockout.update(QUARTER_FINALS)
    all_knockout.update(SEMI_FINALS)
    all_knockout.update(FINAL_MATCHES)

    for match_id, slots in all_knockout.items():
        team1_slot, team2_slot = slots

        team1 = resolve_slot(team1_slot, standings_df, best_thirds_df, results_by_match)
        team2 = resolve_slot(team2_slot, standings_df, best_thirds_df, results_by_match)

        mask = updated["match_id"].astype(str).str.upper().eq(match_id)

        if mask.any():
            if team1:
                updated.loc[mask, "team1"] = team1
            if team2:
                updated.loc[mask, "team2"] = team2

    return updated, standings_df, best_thirds_df
