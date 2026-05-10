import streamlit as st
import pandas as pd
from modules.scoring import build_scoreboard

def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return f"https://flagcdn.com/w40/{code}.png"


def normalize_match_id_columns(left_df, right_df):
    left_df = left_df.copy()
    right_df = right_df.copy()

    if "match_id" not in left_df.columns:
        left_df["match_id"] = ""

    if "match_id" not in right_df.columns:
        right_df["match_id"] = ""

    left_df["match_id"] = left_df["match_id"].astype(str).str.strip()
    right_df["match_id"] = right_df["match_id"].astype(str).str.strip()

    return left_df, right_df


def normalize_sort_columns(df):
    df = df.copy()

    for col in ["groep", "datum", "tijd", "match_id"]:
        if col not in df.columns:
            df[col] = ""

    return df


def show_my_predictions(user, matches_df, predictions_df):
    st.markdown("### Mijn voorspellingen")

    user_id = str(user["user_id"])

    if predictions_df is None or predictions_df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    df = predictions_df[predictions_df["user_id"].astype(str) == user_id].copy()

    if df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    df, matches_df = normalize_match_id_columns(df, matches_df)

    merged = df.merge(
        matches_df,
        on="match_id",
        how="left",
        suffixes=("_prediction", ""),
    )

    merged = normalize_sort_columns(merged)

    merged["match_id_sort"] = (
        merged["match_id"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(0)
        .astype(int)
    )

    merged = merged.sort_values(
        ["groep", "datum", "tijd", "match_id_sort"],
        kind="stable",
    )

    for group, group_df in merged.groupby("groep", sort=False):
        group_label = str(group).strip()

        if group_label == "" or group_label.lower() == "nan":
            group_label = "Onbekend"

        st.subheader(group_label)

        for _, row in group_df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([1.2, 3.8, 0.8, 0.8, 0.9])

                with c1:
                    st.caption(f"{row.get('datum', '')}")
                    st.caption(f"{row.get('tijd', '')}")

                with c2:
                    f1 = flag_img(row.get("team1_code", ""))
                    f2 = flag_img(row.get("team2_code", ""))

                    cc1, cc2, cc3, cc4, cc5 = st.columns(
                        [0.25, 1.1, 0.15, 0.25, 1.1],
                        gap="small",
                    )

                    with cc1:
                        if f1:
                            st.image(f1, width=28)

                    with cc2:
                        st.markdown(f"**{row.get('team1', '')}**")

                    with cc3:
                        st.markdown("**-**")

                    with cc4:
                        if f2:
                            st.image(f2, width=28)

                    with cc5:
                        st.markdown(f"**{row.get('team2', '')}**")

                with c3:
                    score1 = str(row.get("score1", ""))
                    score2 = str(row.get("score2", ""))

                    if score1 != "" and score2 != "":
                        st.markdown(f"**{score1} - {score2}**")
                    else:
                        st.caption("Geen score")

                with c4:
                    pred = str(row.get("prediction", "")).upper()

                    if pred == "1":
                        st.success("1")
                    elif pred == "X":
                        st.info("X")
                    elif pred == "2":
                        st.error("2")
                    elif pred == "X1":
                        st.info("X → 1")
                    elif pred == "X2":
                        st.info("X → 2")
                    else:
                        st.caption("-")

                with c5:
                    status = str(row.get("status", ""))

                    if status.upper() == "FINAL":
                        st.success("Definitief")
                    elif status.lower() == "voorlopig":
                        st.warning("Voorlopig")
                    else:
                        st.caption(status)


def show_scoreboard(users_df, matches_df, predictions_df, results_df):
    import streamlit as st
    import pandas as pd
    import html
    import re

    from modules.scoring import build_scoreboard
    from modules.knockout_engine import calculate_group_standings, calculate_best_thirds

    def esc(value):
        return html.escape(str(value or ""))

    def is_unresolved_team(value):
        text = str(value or "").strip().upper().replace(" ", "")

        if text == "":
            return True

        patterns = [
            r"^[123][A-L]+$",
            r"^W\d+$",
            r"^L\d+$",
        ]

        return any(re.match(pattern, text) for pattern in patterns)

    def stage_label(value):
        text = str(value or "").strip().lower()

        labels = {
            "round of 32": "1/16 finales",
            "round of 16": "1/8 finales",
            "quarterfinals": "Kwartfinales",
            "semifinals": "Halve finales",
            "third place": "Troostwedstrijd",
            "final": "Finale",
        }

        return labels.get(text, str(value or "").strip())

    def show_prediction_ranking():
        scoreboard, details = build_scoreboard(
            users_df,
            matches_df,
            predictions_df,
            results_df,
        )

        if scoreboard is None or scoreboard.empty:
            st.info("Er zijn nog geen punten berekend.")
            return

        scoreboard = scoreboard.copy().reset_index(drop=True)
        scoreboard.insert(0, "positie", range(1, len(scoreboard) + 1))

        def positie_label(pos):
            if pos == 1:
                return "🥇 1"
            if pos == 2:
                return "🥈 2"
            if pos == 3:
                return "🥉 3"
            return str(pos)

        scoreboard["positie"] = scoreboard["positie"].apply(positie_label)

        display_df = scoreboard.rename(
            columns={
                "positie": "#",
                "display_name": "Ploeg",
                "totaal_punten": "Punten",
                "wedstrijden": "Gescoorde wedstrijden",
            }
        )

        st.dataframe(
            display_df[
                [
                    "#",
                    "Deelnemer",
                    "Punten",
                    "Gescoorde wedstrijden",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )

    def show_official_group_standings():
        standings_df = calculate_group_standings(matches_df)

        if standings_df is None or standings_df.empty:
            st.info("Er zijn nog geen officiële groepsstanden beschikbaar.")
            return

        groups = sorted(standings_df["groep"].dropna().unique().tolist())
        cols = st.columns(2)

        for index, group in enumerate(groups):
            group_df = standings_df[
                standings_df["groep"].astype(str).str.upper() == str(group).upper()
            ].copy()

            group_df = group_df[
                [
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
            ]

            group_df = group_df.rename(
                columns={
                    "position": "#",
                    "team": "Team",
                    "played": "P",
                    "wins": "W",
                    "draws": "G",
                    "losses": "V",
                    "goals_for": "DV",
                    "goals_against": "DT",
                    "goal_diff": "+/-",
                    "points": "Ptn",
                }
            )

            with cols[index % 2]:
                with st.container(border=True):
                    st.markdown(f"### Groep {group}")
                    st.dataframe(
                        group_df,
                        hide_index=True,
                        use_container_width=True,
                    )

        best_thirds_df = calculate_best_thirds(standings_df)

        if best_thirds_df is not None and not best_thirds_df.empty:
            st.markdown("### 🥉 Beste derdes")

            thirds = best_thirds_df[
                [
                    "third_rank",
                    "groep",
                    "team",
                    "played",
                    "points",
                    "goal_diff",
                    "goals_for",
                    "qualified_third",
                ]
            ].copy()

            thirds = thirds.rename(
                columns={
                    "third_rank": "#",
                    "groep": "Groep",
                    "team": "Team",
                    "played": "P",
                    "points": "Ptn",
                    "goal_diff": "+/-",
                    "goals_for": "DV",
                    "qualified_third": "Door",
                }
            )

            st.dataframe(
                thirds,
                hide_index=True,
                use_container_width=True,
            )

    def show_official_knockout():
        df = matches_df.copy()
        df.columns = df.columns.astype(str).str.strip().str.lower()

        for col in ["match_id", "ronde", "stage", "datum", "tijd", "team1", "team2"]:
            if col not in df.columns:
                df[col] = ""

        if "match_id_sort" not in df.columns:
            df["match_id_sort"] = (
                df["match_id"]
                .astype(str)
                .str.extract(r"(\d+)")
                .fillna(999999)
                .astype(int)
            )

        knockout = df[
            ~(
                (df["ronde"].astype(str).str.lower() == "group")
                | (df["stage"].astype(str).str.lower().str.startswith("group"))
                | (df.get("groep", "").astype(str).str.upper().isin(list("ABCDEFGHIJKL")))
            )
        ].copy()

        if knockout.empty:
            st.info("Geen eindrondes gevonden.")
            return

        knockout = knockout.sort_values("match_id_sort", kind="stable")

        current_round = None

        for _, row in knockout.iterrows():
            ronde = str(row.get("ronde", "")).strip()
            if ronde == "":
                ronde = str(row.get("stage", "")).strip()

            label = stage_label(ronde)

            if label != current_round:
                st.markdown("---")
                st.markdown(f"### 🏆 {label}")
                current_round = label

            team1 = str(row.get("team1", "")).strip()
            team2 = str(row.get("team2", "")).strip()

            team1_known = not is_unresolved_team(team1)
            team2_known = not is_unresolved_team(team2)

            team1_display = team1 if team1_known else f"⏳ {team1}"
            team2_display = team2 if team2_known else f"⏳ {team2}"

            status = "✅ bekend" if team1_known and team2_known else "⏳ nog niet volledig bekend"

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([0.9, 1.2, 4.0, 1.6])

                with c1:
                    st.markdown(f"**#{row.get('match_id', '')}**")

                with c2:
                    st.caption(str(row.get("datum", "")))
                    st.caption(str(row.get("tijd", "")))

                with c3:
                    st.markdown(
                        f"**{esc(team1_display)}**  -  **{esc(team2_display)}**",
                        unsafe_allow_html=True,
                    )

                with c4:
                    st.caption(status)

    st.markdown("## 🏆 Rankschikking")
    st.caption("Pronostiekstand, officiële groepsstanden en eindrondes.")

    tab1, tab2, tab3 = st.tabs(
        [
            "🏆 Pronostiek",
            "📊 Officiële groepsstand",
            "🏟️ Eindrondes",
        ]
    )

    with tab1:
        show_prediction_ranking()

    with tab2:
        show_official_group_standings()

    with tab3:
        show_official_knockout()


def show_rules():
    st.markdown("### Reglement")

    st.markdown(
        """
### Punten
- Juiste 1/X/2: **3 punten**

### Opslaan
- **Voorlopig opslaan**: later nog wijzigen.
- **Definitief indienen**: ingediend, maar nog wijzigbaar tot de deadline.

### Deadline
Een wedstrijd sluit automatisch **1 uur vóór de aftrap**.
"""
    )
