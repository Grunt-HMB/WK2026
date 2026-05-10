import pandas as pd
import streamlit as st

from modules.wedstrijd_helpers import (
    get_value,
    get_group_letter,
)


def get_selected_prediction(match_id):
    current = st.session_state.get("local_predictions", {}).get(str(match_id), {})
    return str(current.get("prediction", "")).upper().strip()


def normalize_prediction_for_standings(prediction):
    prediction = str(prediction or "").upper().strip()

    if prediction in ["1", "X", "2"]:
        return prediction

    if prediction in ["X1", "X2"]:
        return "X"

    return ""


def calculate_group_standings(wedstrijden):
    tables = {}

    group_matches = wedstrijden[
        wedstrijden["stage"].astype(str).str.lower().str.startswith("group ")
    ].copy()

    for _, match in group_matches.iterrows():
        stage = str(get_value(match, "stage")).strip()
        group = get_group_letter(stage)

        if group == "":
            continue

        team1 = str(get_value(match, "team1")).strip()
        team2 = str(get_value(match, "team2")).strip()

        if team1 == "" or team2 == "":
            continue

        if group not in tables:
            tables[group] = {}

        for team in [team1, team2]:
            if team not in tables[group]:
                tables[group][team] = {
                    "groep": group,
                    "team": team,
                    "P": 0,
                    "W": 0,
                    "G": 0,
                    "V": 0,
                    "Ptn": 0,
                }

        match_id = str(get_value(match, "match_id")).strip()
        prediction = normalize_prediction_for_standings(
            get_selected_prediction(match_id)
        )

        if prediction not in ["1", "X", "2"]:
            continue

        tables[group][team1]["P"] += 1
        tables[group][team2]["P"] += 1

        if prediction == "1":
            tables[group][team1]["W"] += 1
            tables[group][team1]["Ptn"] += 3
            tables[group][team2]["V"] += 1

        elif prediction == "2":
            tables[group][team2]["W"] += 1
            tables[group][team2]["Ptn"] += 3
            tables[group][team1]["V"] += 1

        elif prediction == "X":
            tables[group][team1]["G"] += 1
            tables[group][team2]["G"] += 1
            tables[group][team1]["Ptn"] += 1
            tables[group][team2]["Ptn"] += 1

    all_rows = []

    for group, table in tables.items():
        df = pd.DataFrame(list(table.values()))

        df = df.sort_values(
            ["Ptn", "W", "team"],
            ascending=[False, False, True],
            kind="stable",
        ).reset_index(drop=True)

        df["positie"] = range(1, len(df) + 1)
        all_rows.append(df)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)


def get_team_by_position(standings_df, group, position):
    if standings_df.empty:
        return ""

    row = standings_df[
        (standings_df["groep"].astype(str).str.upper() == str(group).upper())
        & (standings_df["positie"] == position)
    ]

    if row.empty:
        return ""

    return str(row.iloc[0]["team"])


def calculate_best_thirds(standings_df):
    if standings_df.empty:
        return pd.DataFrame()

    thirds = standings_df[standings_df["positie"] == 3].copy()

    if thirds.empty:
        return pd.DataFrame()

    thirds = thirds.sort_values(
        ["Ptn", "W", "team"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    thirds["third_rank"] = range(1, len(thirds) + 1)
    thirds["qualified"] = thirds["third_rank"] <= 8

    return thirds


def resolve_third_team(best_thirds_df, allowed_groups):
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


def show_group_standings(standings_df):
    st.markdown("## 📊 Rankschikking groepsfase")
    st.caption("Deze stand wordt live berekend op basis van jouw groepsfase-keuzes.")

    if standings_df.empty:
        st.info("Nog geen groepsstanden beschikbaar.")
        return

    groups = sorted(standings_df["groep"].dropna().unique().tolist())
    cols = st.columns(2)

    for index, group in enumerate(groups):
        group_df = standings_df[standings_df["groep"] == group].copy()

        group_df = group_df[
            ["positie", "team", "P", "W", "G", "V", "Ptn"]
        ]

        group_df = group_df.rename(
            columns={
                "positie": "#",
                "team": "Team",
            }
        )

        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"### Group {group}")
                st.dataframe(
                    group_df,
                    hide_index=True,
                    use_container_width=True,
                )


def show_best_thirds(best_thirds_df):
    if best_thirds_df.empty:
        return

    st.markdown("## 🥉 Beste derdes")

    df = best_thirds_df.copy()
    df = df[
        ["third_rank", "groep", "team", "P", "W", "G", "V", "Ptn", "qualified"]
    ]

    df = df.rename(
        columns={
            "third_rank": "#",
            "groep": "Groep",
            "team": "Team",
            "qualified": "Door",
        }
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )
