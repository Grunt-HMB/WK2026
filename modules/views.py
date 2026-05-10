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
    import html

    def esc(value):
        return html.escape(str(value or ""))

    def trophy_svg(color, stroke, number):
        return f"""
<svg viewBox="0 0 140 140" class="trophy-svg">
    <defs>
        <linearGradient id="cup{number}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{stroke}" />
            <stop offset="45%" stop-color="{color}" />
            <stop offset="100%" stop-color="#111827" />
        </linearGradient>
    </defs>
    <path d="M42 28 H98 V62 C98 81 86 94 70 94 C54 94 42 81 42 62 Z"
          fill="url(#cup{number})" stroke="{stroke}" stroke-width="4"/>
    <path d="M42 38 H22 C22 58 31 70 45 72"
          fill="none" stroke="{stroke}" stroke-width="7" stroke-linecap="round"/>
    <path d="M98 38 H118 C118 58 109 70 95 72"
          fill="none" stroke="{stroke}" stroke-width="7" stroke-linecap="round"/>
    <rect x="62" y="92" width="16" height="20" rx="3" fill="{stroke}" />
    <rect x="43" y="112" width="54" height="13" rx="4" fill="#1f2937" stroke="{stroke}" stroke-width="3"/>
    <circle cx="70" cy="58" r="20" fill="rgba(255,255,255,0.18)" stroke="{stroke}" stroke-width="3"/>
    <text x="70" y="66" text-anchor="middle" font-size="28" font-weight="900" fill="white">{number}</text>
</svg>
"""

    st.markdown(
        """
<style>
.rank-page-title {
    display: flex;
    align-items: center;
    gap: 18px;
    font-size: 2.6rem;
    font-weight: 950;
    margin-bottom: 0.1rem;
}

.rank-page-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    font-weight: 650;
    margin-bottom: 2.1rem;
}

.top3-header {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr;
    align-items: center;
    gap: 18px;
    margin: 2rem 0 1.2rem 0;
}

.top3-title {
    color: #facc15;
    font-size: 1.55rem;
    font-weight: 950;
    letter-spacing: 0.03em;
}

.top3-line {
    height: 1px;
    background: linear-gradient(90deg, #facc15, transparent);
}

.top3-line.right {
    background: linear-gradient(90deg, transparent, #facc15);
}

.top3-center {
    font-size: 2.1rem;
}

.podium-grid {
    display: grid;
    grid-template-columns: 1fr 1.06fr 1fr;
    gap: 26px;
    margin-bottom: 2.6rem;
}

.podium-card {
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.08), transparent 34%),
        linear-gradient(145deg, #0f172a, #020617);
    border-radius: 22px;
    padding: 26px 28px;
    min-height: 250px;
    display: grid;
    grid-template-columns: 150px 1fr;
    align-items: center;
    gap: 24px;
    position: relative;
}

.podium-card.gold {
    border: 2px solid #facc15;
    box-shadow: 0 0 32px rgba(250,204,21,0.28);
    transform: translateY(-12px);
}

.podium-card.silver {
    border: 2px solid #cbd5e1;
    box-shadow: 0 0 24px rgba(203,213,225,0.22);
}

.podium-card.bronze {
    border: 2px solid #fb923c;
    box-shadow: 0 0 24px rgba(251,146,60,0.22);
}

.trophy-svg {
    width: 145px;
    height: 145px;
    filter: drop-shadow(0 0 18px rgba(250,204,21,0.22));
}

.podium-info {
    border-left: 1px solid rgba(148,163,184,0.22);
    padding-left: 24px;
}

.rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 42px;
    height: 42px;
    border-radius: 10px;
    font-size: 1.35rem;
    font-weight: 950;
    margin-bottom: 14px;
}

.rank-badge.gold { background: linear-gradient(135deg,#facc15,#a16207); color: white; }
.rank-badge.silver { background: linear-gradient(135deg,#e5e7eb,#64748b); color: #0f172a; }
.rank-badge.bronze { background: linear-gradient(135deg,#fb923c,#9a3412); color: white; }

.podium-name {
    font-size: 1.65rem;
    font-weight: 950;
    color: white;
    margin-bottom: 20px;
}

.podium-points {
    font-size: 3.2rem;
    font-weight: 950;
    line-height: 1;
}

.podium-points.gold { color: #facc15; }
.podium-points.silver { color: #cbd5e1; }
.podium-points.bronze { color: #fb923c; }

.podium-label {
    color: #94a3b8;
    font-weight: 750;
    margin-top: 5px;
    margin-bottom: 22px;
}

.prediction-count {
    color: #e5e7eb;
    font-size: 1.05rem;
    font-weight: 850;
}

.rank-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.28);
    border-radius: 16px;
    font-size: 1rem;
}

.rank-table th {
    background: rgba(15,23,42,0.92);
    color: #cbd5e1;
    text-align: left;
    padding: 15px 18px;
    border-bottom: 1px solid rgba(148,163,184,0.28);
}

.rank-table td {
    padding: 15px 18px;
    border-bottom: 1px solid rgba(148,163,184,0.16);
    color: white;
    font-weight: 750;
}

.rank-table tr.gold-row {
    background: linear-gradient(90deg, rgba(250,204,21,0.25), rgba(250,204,21,0.06));
}

.rank-table tr.silver-row {
    background: linear-gradient(90deg, rgba(203,213,225,0.20), rgba(203,213,225,0.04));
}

.rank-table tr.bronze-row {
    background: linear-gradient(90deg, rgba(251,146,60,0.20), rgba(251,146,60,0.04));
}

.rank-table tr:last-child td {
    border-bottom: none;
}

.rank-cell {
    display: flex;
    align-items: center;
    gap: 12px;
}

.mini-cup {
    width: 28px;
    height: 28px;
}

@media (max-width: 1000px) {
    .podium-grid {
        grid-template-columns: 1fr;
    }

    .podium-card.gold {
        transform: none;
    }

    .podium-card {
        grid-template-columns: 120px 1fr;
    }

    .trophy-svg {
        width: 115px;
        height: 115px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="rank-page-title">🏆 Rangschikking</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="rank-page-subtitle">Overzicht van de huidige stand in de WK-pronostiek.</div>',
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

    top3 = scoreboard.head(3).copy()

    style_map = {
        1: {
            "class": "gold",
            "color": "#facc15",
            "stroke": "#fde047",
        },
        2: {
            "class": "silver",
            "color": "#cbd5e1",
            "stroke": "#f8fafc",
        },
        3: {
            "class": "bronze",
            "color": "#fb923c",
            "stroke": "#fdba74",
        },
    }

    st.markdown(
        """
<div class="top3-header">
    <div class="top3-title">★ TOP 3</div>
    <div class="top3-line"></div>
    <div class="top3-center">🏆</div>
    <div class="top3-line right"></div>
</div>
""",
        unsafe_allow_html=True,
    )

    cards_by_position = {}

    for _, row in top3.iterrows():
        pos = int(row["positie"])
        style = style_map.get(pos, style_map[3])
        css_class = style["class"]

        cards_by_position[pos] = f"""
<div class="podium-card {css_class}">
    <div>
        {trophy_svg(style["color"], style["stroke"], pos)}
    </div>
    <div class="podium-info">
        <div class="rank-badge {css_class}">{pos}</div>
        <div class="podium-name">{esc(row["deelnemer"])}</div>
        <div class="podium-points {css_class}">{int(row["punten"])}</div>
        <div class="podium-label">punten</div>
        <div class="prediction-count">⚽ {int(row["voorspellingen"])} voorspellingen</div>
    </div>
</div>
"""

    podium_html = '<div class="podium-grid">'
    podium_html += cards_by_position.get(2, "")
    podium_html += cards_by_position.get(1, "")
    podium_html += cards_by_position.get(3, "")
    podium_html += "</div>"

    st.markdown(podium_html, unsafe_allow_html=True)

    st.markdown("## 📋 Volledige rangschikking")

    table_html = """
<table class="rank-table">
<thead>
<tr>
    <th style="width:15%;">#</th>
    <th>Deelnemer</th>
    <th style="width:22%;">Punten</th>
    <th style="width:25%;">Voorspellingen</th>
</tr>
</thead>
<tbody>
"""

    for _, row in scoreboard.iterrows():
        pos = int(row["positie"])
        style = style_map.get(pos)
        row_class = ""

        if pos == 1:
            row_class = "gold-row"
        elif pos == 2:
            row_class = "silver-row"
        elif pos == 3:
            row_class = "bronze-row"

        if style:
            rank_display = f"""
<span class="rank-cell">
    <span class="mini-cup">{trophy_svg(style["color"], style["stroke"], pos)}</span>
    <span>{pos}</span>
</span>
"""
        else:
            rank_display = str(pos)

        table_html += f"""
<tr class="{row_class}">
    <td>{rank_display}</td>
    <td>{esc(row["deelnemer"])}</td>
    <td>{int(row["punten"])}</td>
    <td>⚽ {int(row["voorspellingen"])}</td>
</tr>
"""

    table_html += """
</tbody>
</table>
"""

    st.markdown(table_html, unsafe_allow_html=True)


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
