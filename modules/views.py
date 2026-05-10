import streamlit as st
import pandas as pd
import html
import re
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from modules.scoring import build_scoreboard
from modules.knockout_engine import calculate_group_standings, calculate_best_thirds


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


def esc(value):
    return html.escape(str(value or ""))


def create_ranking_pdf(scoreboard):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=42,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    story = []

    title = Paragraph("WK 2026 Pronostiek - Rankschikking", styles["Title"])
    story.append(title)

    now = datetime.now(ZoneInfo("Europe/Brussels")).strftime("%d-%m-%Y %H:%M")
    story.append(Paragraph(f"Gegenereerd op: {now}", styles["Normal"]))
    story.append(Spacer(1, 18))

    data = [["#", "Ploeg", "Punten", "Juiste voorspellingen"]]

    for _, row in scoreboard.iterrows():
        pos = int(row["positie"])
        ploeg = str(row.get("naam", ""))
        punten = int(row.get("totaal_punten", 0))
        juist = int(row.get("wedstrijden", 0))

        if pos == 1:
            pos_label = "1"
        elif pos == 2:
            pos_label = "2"
        elif pos == 3:
            pos_label = "3"
        else:
            pos_label = str(pos)

        data.append([pos_label, ploeg, punten, juist])

    table = Table(
        data,
        colWidths=[45, 250, 80, 130],
        repeatRows=1,
    )

    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ]

    if len(data) > 1:
        table_style.append(("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#fef3c7")))
    if len(data) > 2:
        table_style.append(("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#e5e7eb")))
    if len(data) > 3:
        table_style.append(("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#fed7aa")))

    table.setStyle(TableStyle(table_style))

    story.append(table)

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()


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
                        st.info("X -> 1")
                    elif pred == "X2":
                        st.info("X -> 2")
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


def show_prediction_ranking(users_df, matches_df, predictions_df, results_df):
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

    pdf_bytes = create_ranking_pdf(scoreboard)

    st.download_button(
        label="📄 Download rankschikking als PDF",
        data=pdf_bytes,
        file_name="WK2026_Rankschikking.pdf",
        mime="application/pdf",
        use_container_width=False,
    )

    table_html = """
<style>
.rank-wrap {
    max-width: 780px;
    margin: 18px auto 0 auto;
}

.rank-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 14px;
    overflow: hidden;
}

.rank-table th {
    background: rgba(255,255,255,0.04);
    color: #cbd5e1;
    font-weight: 800;
    padding: 14px 16px;
    text-align: center;
    border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.rank-table td {
    padding: 15px 16px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    color: white;
    font-weight: 750;
    text-align: center;
}

.rank-table tr:last-child td {
    border-bottom: none;
}

.rank-table .rank-col {
    width: 90px;
}

.rank-table .team-col {
    text-align: left;
    width: 42%;
}

.rank-table .points-col {
    width: 120px;
    font-weight: 900;
}

.rank-table .correct-col {
    width: 190px;
}

.rank-table .top1 {
    background: rgba(250, 204, 21, 0.10);
}

.rank-table .top2 {
    background: rgba(203, 213, 225, 0.08);
}

.rank-table .top3 {
    background: rgba(251, 146, 60, 0.08);
}
</style>

<div class="rank-wrap">
<table class="rank-table">
<thead>
<tr>
    <th class="rank-col">#</th>
    <th class="team-col">Ploeg</th>
    <th class="points-col">Punten</th>
    <th class="correct-col">Juiste voorspellingen</th>
</tr>
</thead>
<tbody>
"""

    for _, row in scoreboard.iterrows():
        pos = int(row["positie"])

        if pos == 1:
            rank_label = "🥇 1"
            row_class = "top1"
        elif pos == 2:
            rank_label = "🥈 2"
            row_class = "top2"
        elif pos == 3:
            rank_label = "🥉 3"
            row_class = "top3"
        else:
            rank_label = str(pos)
            row_class = ""

        ploeg = esc(row.get("naam", ""))
        punten = int(row.get("totaal_punten", 0))
        juist = int(row.get("wedstrijden", 0))

        table_html += f"""
<tr class="{row_class}">
    <td class="rank-col">{rank_label}</td>
    <td class="team-col">{ploeg}</td>
    <td class="points-col">{punten}</td>
    <td class="correct-col">{juist}</td>
</tr>
"""

    table_html += """
</tbody>
</table>
</div>
"""

    st.markdown(table_html, unsafe_allow_html=True)


def show_official_group_standings(matches_df):
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


def show_official_knockout(matches_df):
    df = matches_df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()

    for col in ["match_id", "ronde", "stage", "datum", "tijd", "team1", "team2"]:
        if col not in df.columns:
            df[col] = ""

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
            | (
                df.get("groep", "")
                .astype(str)
                .str.upper()
                .isin(list("ABCDEFGHIJKL"))
            )
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

        status = (
            "✅ bekend"
            if team1_known and team2_known
            else "⏳ nog niet volledig bekend"
        )

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


def show_scoreboard(users_df, matches_df, predictions_df, results_df):
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
        show_prediction_ranking(
            users_df,
            matches_df,
            predictions_df,
            results_df,
        )

    with tab2:
        show_official_group_standings(matches_df)

    with tab3:
        show_official_knockout(matches_df)


def show_rules():
    st.markdown("### Reglement")

    st.markdown(
        """
### Punten
- Juiste 1/X/2: **3 punten**
- Juiste ploeg op juiste plaats in de eindrondes: **5 punten**

### Opslaan
- **Opslaan Pronostiek**: Niet vergeten hierop te klikken. Als verder sluit is alles weg**
### Deadline
Een wedstrijd sluit automatisch **1 uur vóór de aftrap**.
"""
    )
