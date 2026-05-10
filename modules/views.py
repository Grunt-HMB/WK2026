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
    st.markdown(
        """
<style>
.rank-wrapper {
    max-width: 760px;
    margin: auto;
}

.rank-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 900;
    margin-bottom: 0.2rem;
}

.rank-subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 2rem;
    font-weight: 600;
}

.rank-table {
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 16px;
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(148,163,184,0.20);
}

.rank-table thead tr {
    background: rgba(255,255,255,0.04);
}

.rank-table th {
    padding: 16px;
    text-align: center;
    color: #cbd5e1;
    font-size: 0.95rem;
    font-weight: 800;
    border-bottom: 1px solid rgba(148,163,184,0.18);
}

.rank-table td {
    padding: 18px 16px;
    text-align: center;
    color: white;
    font-size: 1rem;
    font-weight: 700;
    border-bottom: 1px solid rgba(148,163,184,0.12);
}

.rank-table tr:last-child td {
    border-bottom: none;
}

.rank-gold {
    background: linear-gradient(
        90deg,
        rgba(250,204,21,0.18),
        rgba(250,204,21,0.04)
    );
}

.rank-silver {
    background: linear-gradient(
        90deg,
        rgba(203,213,225,0.16),
        rgba(203,213,225,0.04)
    );
}

.rank-bronze {
    background: linear-gradient(
        90deg,
        rgba(251,146,60,0.16),
        rgba(251,146,60,0.04)
    );
}

.rank-position {
    font-size: 1.15rem;
    font-weight: 900;
}

.rank-points {
    font-size: 1.15rem;
    font-weight: 900;
    color: #f8fafc;
}

.rank-name {
    font-size: 1.08rem;
    font-weight: 850;
}

@media (max-width: 768px) {
    .rank-wrapper {
        max-width: 100%;
    }

    .rank-table th,
    .rank-table td {
        padding: 12px 8px;
        font-size: 0.9rem;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rank-wrapper">', unsafe_allow_html=True)

    st.markdown(
        '<div class="rank-title">🏆 Rangschikking</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="rank-subtitle">Overzicht van de huidige stand in de WK-pronostiek.</div>',
        unsafe_allow_html=True,
    )

    scoreboard, details = build_scoreboard(
        users_df,
        matches_df,
        predictions_df,
        results_df,
    )

    if scoreboard is None or scoreboard.empty:
        st.info("Er zijn nog geen punten berekend.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    scoreboard = scoreboard.copy().reset_index(drop=True)
    scoreboard.insert(0, "positie", range(1, len(scoreboard) + 1))

    table_html = """
<table class="rank-table">
<thead>
<tr>
    <th style="width:15%">#</th>
    <th>Deelnemer</th>
    <th style="width:22%">Punten</th>
    <th style="width:28%">Gescoord</th>
</tr>
</thead>
<tbody>
"""

    for _, row in scoreboard.iterrows():
        pos = int(row["positie"])

        row_class = ""

        if pos == 1:
            row_class = "rank-gold"
            rank_label = "🥇 1"
        elif pos == 2:
            row_class = "rank-silver"
            rank_label = "🥈 2"
        elif pos == 3:
            row_class = "rank-bronze"
            rank_label = "🥉 3"
        else:
            rank_label = str(pos)

        table_html += f"""
<tr class="{row_class}">
    <td class="rank-position">{rank_label}</td>
    <td class="rank-name">{row["naam"]}</td>
    <td class="rank-points">{int(row["totaal_punten"])}</td>
    <td>{int(row["wedstrijden"])}</td>
</tr>
"""

    table_html += """
</tbody>
</table>
"""

    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


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
