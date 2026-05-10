import streamlit as st

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

    if predictions_df.empty:
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

        if group_label == "Knock-out":
            st.subheader("Knock-out")
        else:
            st.subheader(f"Groep {group_label}")

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

    st.markdown(
        """
<h1 style="
    display:flex;
    align-items:center;
    gap:14px;
    font-size:2.5rem;
    margin-bottom:0.2rem;
">
🏆 Rangschikking
</h1>
""",
        unsafe_allow_html=True,
    )

    st.caption("Overzicht van de huidige stand in de WK-pronostiek.")

    if users_df is None or users_df.empty:
        st.warning("Geen gebruikers gevonden.")
        return

    if predictions_df is None or predictions_df.empty:
        st.info("Er zijn nog geen voorspellingen opgeslagen.")
        return

    users = users_df.copy()
    predictions = predictions_df.copy()

    users.columns = users.columns.astype(str).str.strip().str.lower()
    predictions.columns = predictions.columns.astype(str).str.strip().str.lower()

    if "points" not in predictions.columns:
        predictions["points"] = 0

    predictions["points"] = pd.to_numeric(
        predictions["points"],
        errors="coerce",
    ).fillna(0)

    scoreboard = (
        predictions
        .groupby("user_id", as_index=False)
        .agg(
            punten=("points", "sum"),
            voorspellingen=("match_id", "count"),
        )
    )

    scoreboard["user_id"] = scoreboard["user_id"].astype(str).str.strip()
    users["user_id"] = users["user_id"].astype(str).str.strip()

    name_col = "name"

    if "naam" in users.columns:
        name_col = "naam"

    elif "username" in users.columns:
        name_col = "username"

    scoreboard = scoreboard.merge(
        users[["user_id", name_col]],
        on="user_id",
        how="left",
    )

    scoreboard = scoreboard.rename(
        columns={
            name_col: "deelnemer",
        }
    )

    scoreboard["deelnemer"] = scoreboard["deelnemer"].fillna(
        "Onbekende speler"
    )

    scoreboard = scoreboard.sort_values(
        ["punten", "voorspellingen", "deelnemer"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    scoreboard.insert(0, "positie", range(1, len(scoreboard) + 1))

    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    scoreboard["medal"] = scoreboard["positie"].map(medals).fillna("")

    st.markdown(
        """
<h2 style="
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:1.6rem;
">
🏅 Huidige top 3
</h2>
""",
        unsafe_allow_html=True,
    )

    top3 = scoreboard.head(3)

    if not top3.empty:
        cols = st.columns(3)

        gradients = {
            1: "linear-gradient(145deg,#3b2f00,#facc15)",
            2: "linear-gradient(145deg,#1e293b,#cbd5e1)",
            3: "linear-gradient(145deg,#3f1d0d,#fdba74)",
        }

        borders = {
            1: "#facc15",
            2: "#cbd5e1",
            3: "#fdba74",
        }

        shadows = {
            1: "0 0 30px rgba(250,204,21,0.35)",
            2: "0 0 22px rgba(203,213,225,0.25)",
            3: "0 0 22px rgba(251,146,60,0.25)",
        }

        for i, (_, row) in enumerate(top3.iterrows()):
            positie = int(row["positie"])

            with cols[i]:
                st.markdown(
                    f"""
<div style="
    background:#111827;
    border:2px solid {borders[positie]};
    border-radius:24px;
    padding:30px 20px;
    text-align:center;
    box-shadow:{shadows[positie]};
    min-height:330px;
    display:flex;
    flex-direction:column;
    justify-content:center;
">

<div style="
    font-size:4rem;
    margin-bottom:10px;
">
{row["medal"]}
</div>

<div style="
    font-size:1.8rem;
    font-weight:900;
    color:white;
    margin-bottom:12px;
">
{row["deelnemer"]}
</div>

<div style="
    font-size:3.2rem;
    font-weight:900;
    background:{gradients[positie]};
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:5px;
">
{int(row["punten"])}
</div>

<div style="
    color:#94a3b8;
    font-weight:700;
    font-size:1rem;
    margin-bottom:18px;
">
punten
</div>

<div style="
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;
    padding:10px;
    color:#e2e8f0;
    font-weight:700;
">
⚽ {int(row["voorspellingen"])} voorspellingen
</div>

</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
<h2 style="
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:2rem;
">
📋 Volledige rangschikking
</h2>
""",
        unsafe_allow_html=True,
    )

    display_df = scoreboard[
        [
            "positie",
            "medal",
            "deelnemer",
            "punten",
            "voorspellingen",
        ]
    ].copy()

    display_df["positie"] = display_df.apply(
        lambda row: (
            f'{row["medal"]} {row["positie"]}'
            if row["medal"] != ""
            else str(row["positie"])
        ),
        axis=1,
    )

    display_df = display_df.drop(columns=["medal"])

    display_df = display_df.rename(
        columns={
            "positie": "#",
            "deelnemer": "Deelnemer",
            "punten": "Punten",
            "voorspellingen": "Voorspellingen",
        }
    )

    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
    )


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
Na de tornooi-start kan niemand nog wijzigen.
"""
    )
