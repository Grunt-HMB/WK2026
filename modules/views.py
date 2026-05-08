import streamlit as st
from modules.scoring import build_scoreboard
from modules.utils import flag_emoji

def show_my_predictions(user, matches_df, predictions_df):
    st.markdown('<div class="main-title">Mijn voorspellingen</div>', unsafe_allow_html=True)

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

    for _, row in merged.iterrows():
        f1 = flag_emoji(row.get("team1_code", ""))
        f2 = flag_emoji(row.get("team2_code", ""))

        score = ""
        if str(row.get("score1", "")) != "" and str(row.get("score2", "")) != "":
            score = f" | score {row.get('score1')} - {row.get('score2')}"

        st.write(
            f"{row.get('groep')} | {row.get('datum')} {row.get('tijd')} — "
            f"{f1} {row.get('team1')} - {f2} {row.get('team2')} → "
            f"**{row.get('prediction')}**{score} ({row.get('status')})"
        )

def show_scoreboard(users_df, matches_df, predictions_df, results_df):
    st.markdown('<div class="main-title">Scorebord</div>', unsafe_allow_html=True)

    scoreboard, detail = build_scoreboard(users_df, matches_df, predictions_df, results_df)

    if scoreboard.empty:
        st.info("Nog geen scorebord beschikbaar.")
        return

    st.dataframe(scoreboard, use_container_width=True, hide_index=True)

    with st.expander("Detail per wedstrijd"):
        columns = [
            "naam", "groep", "team1", "team2",
            "prediction", "score1", "score2",
            "real_team1", "real_team2", "punten"
        ]
        existing = [c for c in columns if c in detail.columns]
        st.dataframe(detail[existing], use_container_width=True, hide_index=True)

def show_rules():
    st.markdown('<div class="main-title">Reglement</div>', unsafe_allow_html=True)
    st.markdown("""
### Punten
- Juiste 1/X/2: **3 punten**
- Exacte score: **+2 punten**
- Juist doelpuntenverschil: **+1 punt**

### Opslaan
- **Concept opslaan**: later nog wijzigen.
- **Definitief indienen**: niet meer wijzigen.

### Deadline
Na de tornooi-start kan niemand nog wijzigen.
""")
