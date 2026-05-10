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
    import html
    import pandas as pd

    def esc(value):
        return html.escape(str(value or ""))

    def get_name_col(users):
        for col in ["naam", "name", "username", "speler", "deelnemer"]:
            if col in users.columns:
                return col
        return "user_id"

    def cup_svg(rank):
        if rank == 1:
            main = "#facc15"
            light = "#fde68a"
            dark = "#92400e"
        elif rank == 2:
            main = "#cbd5e1"
            light = "#f8fafc"
            dark = "#475569"
        else:
            main = "#fb923c"
            light = "#fed7aa"
            dark = "#7c2d12"

        return f"""
<svg class="lb-cup-svg" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="cupGradient{rank}" cx="35%" cy="22%" r="75%">
      <stop offset="0%" stop-color="{light}"/>
      <stop offset="45%" stop-color="{main}"/>
      <stop offset="100%" stop-color="{dark}"/>
    </radialGradient>
  </defs>

  <path d="M62 42 H158 V95 C158 126 137 148 110 148 C83 148 62 126 62 95 Z"
        fill="url(#cupGradient{rank})" stroke="{light}" stroke-width="5"/>

  <path d="M62 58 H28 C28 92 43 112 67 116"
        fill="none" stroke="{light}" stroke-width="10" stroke-linecap="round"/>

  <path d="M158 58 H192 C192 92 177 112 153 116"
        fill="none" stroke="{light}" stroke-width="10" stroke-linecap="round"/>

  <circle cx="110" cy="90" r="31" fill="rgba(0,0,0,0.20)" stroke="{light}" stroke-width="4"/>
  <text x="110" y="103" text-anchor="middle" font-size="43" font-weight="900" fill="white">{rank}</text>

  <rect x="96" y="145" width="28" height="32" rx="4" fill="{dark}" stroke="{main}" stroke-width="4"/>
  <rect x="70" y="174" width="80" height="18" rx="5" fill="#1f2937" stroke="{main}" stroke-width="4"/>
</svg>
"""

    st.markdown(
        """
<style>
.lb-title {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 2.45rem;
    font-weight: 950;
    margin-bottom: 0.25rem;
}

.lb-subtitle {
    color: #94a3b8;
    font-weight: 650;
    margin-bottom: 2rem;
}

.lb-top-header {
    display: grid;
    grid-template-columns: auto 1fr auto 1fr;
    align-items: center;
    gap: 16px;
    margin: 1.7rem 0 1.4rem 0;
}

.lb-top-label {
    color: #facc15;
    font-size: 1.45rem;
    font-weight: 950;
    letter-spacing: 0.04em;
}

.lb-line-left {
    height: 1px;
    background: linear-gradient(90deg, #facc15, transparent);
}

.lb-line-right {
    height: 1px;
    background: linear-gradient(90deg, transparent, #facc15);
}

.lb-center {
    font-size: 2rem;
}

.lb-podium-grid {
    display: grid;
    grid-template-columns: 1fr 1.12fr 1fr;
    gap: 24px;
    margin-bottom: 2.5rem;
}

.lb-card {
    background:
        radial-gradient(circle at 20% 10%, rgba(255,255,255,0.10), transparent 30%),
        linear-gradient(145deg, #0f172a, #020617);
    border-radius: 20px;
    padding: 24px;
    min-height: 250px;
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 22px;
    align-items: center;
}

.lb-card.gold {
    border: 2px solid #facc15;
    box-shadow: 0 0 34px rgba(250,204,21,0.32);
    transform: translateY(-10px);
}

.lb-card.silver {
    border: 2px solid #cbd5e1;
    box-shadow: 0 0 24px rgba(203,213,225,0.25);
}

.lb-card.bronze {
    border: 2px solid #fb923c;
    box-shadow: 0 0 24px rgba(251,146,60,0.25);
}

.lb-cup-svg {
    width: 145px;
    height: 145px;
    filter: drop-shadow(0 0 16px rgba(250,204,21,0.20));
}

.lb-info {
    border-left: 1px solid rgba(148,163,184,0.25);
    padding-left: 22px;
}

.lb-rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 10px;
    font-size: 1.35rem;
    font-weight: 950;
    margin-bottom: 13px;
}

.lb-rank-badge.gold {
    background: linear-gradient(135deg, #facc15, #a16207);
    color: white;
}

.lb-rank-badge.silver {
    background: linear-gradient(135deg, #f8fafc, #64748b);
    color: #0f172a;
}

.lb-rank-badge.bronze {
    background: linear-gradient(135deg, #fb923c, #9a3412);
    color: white;
}

.lb-name {
    color: white;
    font-size: 1.55rem;
    font-weight: 950;
    margin-bottom: 20px;
}

.lb-points {
    font-size: 3.2rem;
    font-weight: 950;
    line-height: 1;
}

.lb-points.gold {
    color: #facc15;
}

.lb-points.silver {
    color: #cbd5e1;
}

.lb-points.bronze {
    color: #fb923c;
}

.lb-points-label {
    color: #94a3b8;
    font-weight: 750;
    margin-top: 5px;
    margin-bottom: 20px;
}

.lb-predictions {
    color: #e5e7eb;
    font-weight: 850;
}

.lb-section-title {
    font-size: 1.75rem;
    font-weight: 950;
    margin: 1.8rem 0 1rem 0;
}

.lb-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.28);
    border-radius: 15px;
}

.lb-table th {
    background: rgba(15,23,42,0.95);
    color: #cbd5e1;
    text-align: left;
    padding: 15px 18px;
    border-bottom: 1px solid rgba(148,163,184,0.28);
}

.lb-table td {
    color: white;
    padding: 15px 18px;
    border-bottom: 1px solid rgba(148,163,184,0.16);
    font-weight: 800;
}

.lb-table tr.gold-row {
    background: linear-gradient(90deg, rgba(250,204,21,0.25), rgba(250,204,21,0.04));
}

.lb-table tr.silver-row {
    background: linear-gradient(90deg, rgba(203,213,225,0.20), rgba(203,213,225,0.04));
}

.lb-table tr.bronze-row {
    background: linear-gradient(90deg, rgba(251,146,60,0.22), rgba(251,146,60,0.04));
}

.lb-rank-cell {
    display: flex;
    align-items: center;
    gap: 12px;
}

.lb-mini-cup .lb-cup-svg {
    width: 34px;
    height: 34px;
}

@media(max-width: 1000px) {
    .lb-podium-grid {
        grid-template-columns: 1fr;
    }

    .lb-card.gold {
        transform: none;
    }

    .lb-card {
        grid-template-columns: 125px 1fr;
    }

    .lb-cup-svg {
        width: 120px;
        height: 120px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="lb-title">🏆 Rangschikking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lb-subtitle">Overzicht van de huidige stand in de WK-pronostiek.</div>',
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

    name_col = get_name_col(users)

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

    st.markdown(
        """
<div class="lb-top-header">
    <div class="lb-top-label">★ TOP 3</div>
    <div class="lb-line-left"></div>
    <div class="lb-center">🏆</div>
    <div class="lb-line-right"></div>
</div>
""",
        unsafe_allow_html=True,
    )

    css_by_pos = {
        1: "gold",
        2: "silver",
        3: "bronze",
    }

    cards = {}

    for _, row in top3.iterrows():
        pos = int(row["positie"])
        css = css_by_pos.get(pos, "bronze")

        cards[pos] = f"""
<div class="lb-card {css}">
    <div>{cup_svg(pos)}</div>
    <div class="lb-info">
        <div class="lb-rank-badge {css}">{pos}</div>
        <div class="lb-name">{esc(row["deelnemer"])}</div>
        <div class="lb-points {css}">{int(row["punten"])}</div>
        <div class="lb-points-label">punten</div>
        <div class="lb-predictions">⚽ {int(row["voorspellingen"])} voorspellingen</div>
    </div>
</div>
"""

    podium_html = '<div class="lb-podium-grid">'
    podium_html += cards.get(2, "")
    podium_html += cards.get(1, "")
    podium_html += cards.get(3, "")
    podium_html += "</div>"

    st.markdown(podium_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="lb-section-title">📋 Volledige rangschikking</div>',
        unsafe_allow_html=True,
    )

    table_html = """
<table class="lb-table">
<thead>
<tr>
    <th style="width:16%;">#</th>
    <th>Deelnemer</th>
    <th style="width:22%;">Punten</th>
    <th style="width:25%;">Voorspellingen</th>
</tr>
</thead>
<tbody>
"""

    for _, row in scoreboard.iterrows():
        pos = int(row["positie"])
        css = css_by_pos.get(pos, "")
        row_class = f"{css}-row" if css else ""

        if pos in [1, 2, 3]:
            rank_html = f"""
<div class="lb-rank-cell">
    <span class="lb-mini-cup">{cup_svg(pos)}</span>
    <span>{pos}</span>
</div>
"""
        else:
            rank_html = str(pos)

        table_html += f"""
<tr class="{row_class}">
    <td>{rank_html}</td>
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
