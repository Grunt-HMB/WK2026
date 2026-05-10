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
<style>
.rank-title {
    font-size: 2.4rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
}

.rank-subtitle {
    color: #94a3b8;
    font-weight: 600;
    margin-bottom: 2rem;
}

.podium-wrap {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin-top: 1rem;
    margin-bottom: 2rem;
}

.podium-card {
    background: #111827;
    border-radius: 24px;
    padding: 26px 18px;
    text-align: center;
    min-height: 260px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.podium-gold {
    border: 2px solid #facc15;
    box-shadow: 0 0 28px rgba(250, 204, 21, 0.35);
}

.podium-silver {
    border: 2px solid #cbd5e1;
    box-shadow: 0 0 28px rgba(203, 213, 225, 0.28);
}

.podium-bronze {
    border: 2px solid #fb923c;
    box-shadow: 0 0 28px rgba(251, 146, 60, 0.28);
}

.cup-icon {
    font-size: 4.5rem;
    line-height: 1;
    margin-bottom: 14px;
}

.cup-gold {
    color: #facc15;
    text-shadow: 0 0 18px rgba(250,204,21,0.55);
}

.cup-silver {
    color: #e5e7eb;
    text-shadow: 0 0 18px rgba(229,231,235,0.45);
}

.cup-bronze {
    color: #fb923c;
    text-shadow: 0 0 18px rgba(251,146,60,0.45);
}

.player-name {
    font-size: 1.55rem;
    font-weight: 900;
    color: white;
    margin-bottom: 10px;
}

.player-points {
    font-size: 3rem;
    font-weight: 900;
    margin-bottom: 0;
}

.points-gold { color: #facc15; }
.points-silver { color: #cbd5e1; }
.points-bronze { color: #fb923c; }

.points-label {
    color: #94a3b8;
    font-weight: 800;
    margin-bottom: 18px;
}

.prediction-pill {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 10px;
    font-weight: 800;
    color: #e5e7eb;
}

@media (max-width: 900px) {
    .podium-wrap {
        grid-template-columns: 1fr;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rank-title">🏆 Rangschikking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rank-subtitle">Overzicht van de huidige stand in de WK-pronostiek.</div>',
        unsafe_allow_html=True,
    )

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

    if "user_id" not in users.columns or "user_id" not in predictions.columns:
        st.error("Kolom 'user_id' ontbreekt in Users of Predictions.")
        return

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

    scoreboard = scoreboard.rename(columns={name_col: "deelnemer"})
    scoreboard["deelnemer"] = scoreboard["deelnemer"].fillna("Onbekende speler")

    scoreboard = scoreboard.sort_values(
        ["punten", "voorspellingen", "deelnemer"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    scoreboard.insert(0, "positie", range(1, len(scoreboard) + 1))

    st.markdown("## 🏅 Huidige top 3")

    top3 = scoreboard.head(3).copy()

    cup_map = {
        1: {
            "cup": "🏆",
            "card_class": "podium-gold",
            "cup_class": "cup-gold",
            "points_class": "points-gold",
            "label": "Goud",
        },
        2: {
            "cup": "🏆",
            "card_class": "podium-silver",
            "cup_class": "cup-silver",
            "points_class": "points-silver",
            "label": "Zilver",
        },
        3: {
            "cup": "🏆",
            "card_class": "podium-bronze",
            "cup_class": "cup-bronze",
            "points_class": "points-bronze",
            "label": "Brons",
        },
    }

    cards_html = '<div class="podium-wrap">'

    for _, row in top3.iterrows():
        positie = int(row["positie"])
        style = cup_map.get(positie, cup_map[3])

        cards_html += f"""
<div class="podium-card {style["card_class"]}">
    <div class="cup-icon {style["cup_class"]}">{style["cup"]}</div>
    <div class="player-name">{row["deelnemer"]}</div>
    <div class="player-points {style["points_class"]}">{int(row["punten"])}</div>
    <div class="points-label">punten</div>
    <div class="prediction-pill">⚽ {int(row["voorspellingen"])} voorspellingen</div>
</div>
"""

    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("## 📋 Volledige rangschikking")

    def rank_icon(pos):
        if pos == 1:
            return "🏆 Goud"
        if pos == 2:
            return "🏆 Zilver"
        if pos == 3:
            return "🏆 Brons"
        return str(pos)

    display_df = scoreboard[
        [
            "positie",
            "deelnemer",
            "punten",
            "voorspellingen",
        ]
    ].copy()

    display_df["positie"] = display_df["positie"].apply(rank_icon)

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
