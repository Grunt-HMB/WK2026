import streamlit as st
from modules.scoring import build_scoreboard


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:28px;height:20px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.20);vertical-align:middle;margin-right:5px;">'
    )


def prediction_badge(prediction):
    prediction = str(prediction or "").strip().upper()

    colors = {
        "1": ("#dcfce7", "#166534", "1"),
        "X": ("#e0f2fe", "#075985", "X"),
        "2": ("#fee2e2", "#991b1b", "2"),
    }

    bg, fg, label = colors.get(prediction, ("#f1f5f9", "#334155", "-"))

    return (
        f'<span style="display:inline-block;min-width:28px;text-align:center;'
        f'padding:3px 8px;border-radius:999px;background:{bg};color:{fg};'
        f'font-weight:900;border:1px solid rgba(0,0,0,0.08);">{label}</span>'
    )


def score_text(score1, score2):
    if str(score1) != "" and str(score2) != "":
        return f"{score1} - {score2}"
    return ""


def show_my_predictions(user, matches_df, predictions_df):
    st.markdown(
        '<div class="main-title">Mijn voorspellingen</div>',
        unsafe_allow_html=True,
    )

    user_id = str(user["user_id"])

    if predictions_df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    df = predictions_df[predictions_df["user_id"].astype(str) == user_id]

    if df.empty:
        st.info("Je hebt nog niets opgeslagen.")
        return

    merged = df.merge(matches_df, on="match_id", how="left")
    merged = merged.sort_values(
        ["groep", "datum", "tijd", "match_id"],
        kind="stable",
    )

    for group, group_df in merged.groupby("groep", sort=False):
        st.subheader(f"Groep {group}")

        for _, row in group_df.iterrows():
            f1 = flag_img(row.get("team1_code", ""))
            f2 = flag_img(row.get("team2_code", ""))

            prediction = row.get("prediction", "")
            score = score_text(row.get("score1", ""), row.get("score2", ""))
            status = str(row.get("status", "") or "")

            score_part = ""
            if score:
                score_part = (
                    f'<span style="font-weight:800;color:#0f172a;">'
                    f'{score}</span>'
                )

            status_color = "#64748b"
            if status.upper() == "FINAL":
                status_color = "#166534"
            elif status.upper() == "DRAFT":
                status_color = "#92400e"

            st.markdown(
                f"""
<div style="
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    border:1px solid #e2e8f0;
    border-radius:10px;
    padding:8px 10px;
    margin-bottom:6px;
    background:#ffffff;
">
    <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
        <span style="font-size:0.82rem;color:#64748b;min-width:92px;">
            {row.get('datum', '')} {row.get('tijd', '')}
        </span>
        <span style="font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            {f1} {row.get('team1', '')}
            <span style="color:#64748b;margin:0 4px;">-</span>
            {f2} {row.get('team2', '')}
        </span>
    </div>

    <div style="display:flex;align-items:center;gap:8px;white-space:nowrap;">
        {score_part}
        {prediction_badge(prediction)}
        <span style="font-size:0.78rem;color:{status_color};font-weight:800;">
            {status}
        </span>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )


def show_scoreboard(users_df, matches_df, predictions_df, results_df):
    st.markdown(
        '<div class="main-title">Scorebord</div>',
        unsafe_allow_html=True,
    )

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
        st.dataframe(detail[existing], use_container_width=True, hide_index=True)


def show_rules():
    st.markdown(
        '<div class="main-title">Reglement</div>',
        unsafe_allow_html=True,
    )

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
