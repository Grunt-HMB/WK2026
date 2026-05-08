import streamlit as st
from modules.scoring import build_scoreboard


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return f"https://flagcdn.com/w40/{code}.png"


def show_my_predictions(user, matches_df, predictions_df):
    st.markdown("### Mijn voorspellingen")

    user_id = str(user["user_id"])

    if predictions_df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    df = predictions_df[predictions_df["user_id"].astype(str) == user_id]

    if df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    merged = df.merge(matches_df, on="match_id", how="left")
    merged = merged.sort_values(["groep", "datum", "tijd", "match_id"], kind="stable")

    for group, group_df in merged.groupby("groep", sort=False):
        st.subheader(f"Groep {group}")

        for _, row in group_df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([1.2, 3.8, 0.8, 0.8, 0.9])

                with c1:
                    st.caption(f"{row.get('datum', '')}")
                    st.caption(f"{row.get('tijd', '')}")

                with c2:
                    f1 = flag_img(row.get("team1_code", ""))
                    f2 = flag_img(row.get("team2_code", ""))

                    cc1, cc2, cc3, cc4, cc5 = st.columns([0.25, 1.1, 0.15, 0.25, 1.1])

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
                    else:
                        st.caption("-")

                with c5:
                    status = str(row.get("status", "")).upper()

                    if status == "Definitief":
                        st.success("Definitief")
                    elif status == "Voorlopig":
                        st.warning("Voorlopig")
                    else:
                        st.caption(status)


def show_scoreboard(users_df, matches_df, predictions_df, results_df):
    st.markdown("### Scorebord")

    scoreboard, detail = build_scoreboard(
        users_df,
        matches_df,
        predictions_df,
        results_df,
    )

    if scoreboard.empty:
        st.info("Nog geen scorebord beschikbaar.")
        return

    st.dataframe(scoreboard, use_container_width=True, hide_index=True)

    with st.expander("Detail per wedstrijd"):
        columns = [
            "naam",
            "groep",
            "team1",
            "team2",
            "prediction",
            "score1",
            "score2",
            "real_team1",
            "real_team2",
            "punten",
        ]

        existing = [c for c in columns if c in detail.columns]

        st.dataframe(
            detail[existing],
            use_container_width=True,
            hide_index=True,
        )


def show_rules():
    st.markdown("### Reglement")

    st.markdown(
        """
### Punten
- Juiste 1/X/2: **3 punten**
- Exacte score: **+2 punten**
- Juist doelpuntenverschil: **+1 punt**

### Opslaan
- **Concept opslaan**: later nog wijzigen.
- **Definitief indienen**: ingediend, maar nog wijzigbaar tot de deadline.

### Deadline
Na de tornooi-start kan niemand nog wijzigen.
"""
    )
