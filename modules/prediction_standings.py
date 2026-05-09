import streamlit as st


def show_group_standings(selected_phase, standings_df):
    if selected_phase["type"] != "groep":
        return

    if standings_df is None or standings_df.empty:
        return

    group = str(selected_phase["value"])

    group_standings = standings_df[
        standings_df["groep"].astype(str) == group
    ].copy()

    if group_standings.empty:
        return

    st.markdown(f"### 📊 Stand Groep {group}")

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

    table = group_standings[cols].copy()

    table = table.rename(
        columns={
            "position": "#",
            "team": "Team",
            "played": "G",
            "wins": "W",
            "draws": "Gelijk",
            "losses": "V",
            "goals_for": "DV",
            "goals_against": "DT",
            "goal_diff": "DS",
            "points": "Ptn",
        }
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )
