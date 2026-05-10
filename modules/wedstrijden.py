import re
import streamlit as st
import pandas as pd

from modules.database import batch_upsert_predictions
from modules.prediction_cards import match_is_locked
from modules.prediction_state import (
    load_existing_predictions,
    mark_predictions_saved,
    set_prediction,
)


GROUPS = list("ABCDEFGHIJKL")

DUTCH_WEEKDAYS = [
    "maandag",
    "dinsdag",
    "woensdag",
    "donderdag",
    "vrijdag",
    "zaterdag",
    "zondag",
]

DUTCH_MONTHS = {
    "januari": "January",
    "februari": "February",
    "maart": "March",
    "april": "April",
    "mei": "May",
    "juni": "June",
    "juli": "July",
    "augustus": "August",
    "september": "September",
    "oktober": "October",
    "november": "November",
    "december": "December",
}


def normalize_columns(df):
    if df is None:
        return None

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


def get_value(row, *names):
    for name in names:
        if name in row and str(row.get(name, "")).strip() != "":
            return row.get(name, "")
    return ""


def clean_dutch_date(value):
    text = str(value or "").strip().lower()

    for day in DUTCH_WEEKDAYS:
        text = text.replace(day, "")

    text = " ".join(text.split())

    for nl, en in DUTCH_MONTHS.items():
        text = text.replace(nl, en)

    return text


def create_sort_columns(wedstrijden):
    wedstrijden = wedstrijden.copy()

    for col in ["datum", "tijd", "match_id", "match_id_sort"]:
        if col not in wedstrijden.columns:
            wedstrijden[col] = ""

    wedstrijden["datum_sort"] = pd.to_datetime(
        wedstrijden["datum"].apply(clean_dutch_date),
        format="%d %B %Y",
        errors="coerce",
    )

    wedstrijden["tijd_sort"] = pd.to_datetime(
        wedstrijden["tijd"].astype(str).str.strip(),
        format="%H:%M",
        errors="coerce",
    )

    wedstrijden["match_id_sort"] = pd.to_numeric(
        wedstrijden["match_id_sort"],
        errors="coerce",
    ).fillna(
        pd.to_numeric(wedstrijden["match_id"], errors="coerce")
    ).fillna(999999)

    return wedstrijden


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:30px;height:22px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.25);vertical-align:middle;">'
    )


def prediction_label(choice, selected):
    selected = str(selected or "").upper().strip()

    if selected == choice:
        return f"✅ {choice}"

    return choice


def get_selected_prediction(match_id):
    current = st.session_state.get("local_predictions", {}).get(str(match_id), {})
    return str(current.get("prediction", "")).upper().strip()


def is_group_stage(stage):
    stage = str(stage or "").strip().lower()
    return stage.startswith("group ")


def get_group_letter(stage):
    stage = str(stage or "").strip().upper()
    match = re.search(r"GROUP\s+([A-L])", stage)

    if match:
        return match.group(1)

    return ""


def is_knockout_stage(stage):
    return not is_group_stage(stage)


def get_match_winner_from_prediction(row):
    match_id = str(get_value(row, "match_id", "wedstrijd_id", "id")).strip()
    prediction = get_selected_prediction(match_id)

    team1 = str(get_value(row, "team1", "land1", "thuisploeg")).strip()
    team2 = str(get_value(row, "team2", "land2", "uitploeg")).strip()

    if prediction == "1":
        return team1

    if prediction == "2":
        return team2

    return ""


def get_match_loser_from_prediction(row):
    match_id = str(get_value(row, "match_id", "wedstrijd_id", "id")).strip()
    prediction = get_selected_prediction(match_id)

    team1 = str(get_value(row, "team1", "land1", "thuisploeg")).strip()
    team2 = str(get_value(row, "team2", "land2", "uitploeg")).strip()

    if prediction == "1":
        return team2

    if prediction == "2":
        return team1

    return ""


def calculate_group_standings(wedstrijden):
    tables = {}

    group_matches = wedstrijden[
        wedstrijden["stage"].astype(str).str.lower().str.startswith("group ")
    ].copy()

    for _, match in group_matches.iterrows():
        stage = str(get_value(match, "stage")).strip()
        group = get_group_letter(stage)

        if group == "":
            continue

        team1 = str(get_value(match, "team1")).strip()
        team2 = str(get_value(match, "team2")).strip()

        if team1 == "" or team2 == "":
            continue

        if group not in tables:
            tables[group] = {}

        for team in [team1, team2]:
            if team not in tables[group]:
                tables[group][team] = {
                    "groep": group,
                    "team": team,
                    "P": 0,
                    "W": 0,
                    "G": 0,
                    "V": 0,
                    "Ptn": 0,
                }

        match_id = str(get_value(match, "match_id")).strip()
        prediction = get_selected_prediction(match_id)

        if prediction not in ["1", "X", "2"]:
            continue

        tables[group][team1]["P"] += 1
        tables[group][team2]["P"] += 1

        if prediction == "1":
            tables[group][team1]["W"] += 1
            tables[group][team1]["Ptn"] += 3
            tables[group][team2]["V"] += 1

        elif prediction == "2":
            tables[group][team2]["W"] += 1
            tables[group][team2]["Ptn"] += 3
            tables[group][team1]["V"] += 1

        elif prediction == "X":
            tables[group][team1]["G"] += 1
            tables[group][team2]["G"] += 1
            tables[group][team1]["Ptn"] += 1
            tables[group][team2]["Ptn"] += 1

    all_rows = []

    for group, table in tables.items():
        df = pd.DataFrame(list(table.values()))

        df = df.sort_values(
            ["Ptn", "W", "team"],
            ascending=[False, False, True],
            kind="stable",
        ).reset_index(drop=True)

        df["positie"] = range(1, len(df) + 1)
        all_rows.append(df)

    if not all_rows:
        return pd.DataFrame()

    return pd.concat(all_rows, ignore_index=True)


def get_team_by_position(standings_df, group, position):
    if standings_df.empty:
        return ""

    row = standings_df[
        (standings_df["groep"].astype(str).str.upper() == str(group).upper())
        & (standings_df["positie"] == position)
    ]

    if row.empty:
        return ""

    return str(row.iloc[0]["team"])


def calculate_best_thirds(standings_df):
    if standings_df.empty:
        return pd.DataFrame()

    thirds = standings_df[standings_df["positie"] == 3].copy()

    if thirds.empty:
        return pd.DataFrame()

    thirds = thirds.sort_values(
        ["Ptn", "W", "team"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    thirds["third_rank"] = range(1, len(thirds) + 1)
    thirds["qualified"] = thirds["third_rank"] <= 8

    return thirds


def resolve_third_team(best_thirds_df, allowed_groups):
    if best_thirds_df.empty:
        return ""

    allowed_groups = [str(g).upper() for g in allowed_groups]

    possible = best_thirds_df[
        (best_thirds_df["qualified"] == True)
        & (best_thirds_df["groep"].astype(str).str.upper().isin(allowed_groups))
    ].copy()

    if possible.empty:
        return ""

    possible = possible.sort_values("third_rank", ascending=True)
    return str(possible.iloc[0]["team"])


def build_results_by_match(wedstrijden):
    results = {}

    for _, row in wedstrijden.iterrows():
        match_id = str(get_value(row, "match_id")).strip()

        if match_id == "":
            continue

        winner = get_match_winner_from_prediction(row)
        loser = get_match_loser_from_prediction(row)

        if winner:
            results[f"W{match_id}"] = winner

        if loser:
            results[f"L{match_id}"] = loser

    return results


def resolve_slot(slot, standings_df, best_thirds_df, results_by_match):
    original = str(slot or "").strip()
    normalized = original.upper().replace(" ", "")

    if re.fullmatch(r"1[A-L]", normalized):
        return get_team_by_position(standings_df, normalized[1], 1) or original

    if re.fullmatch(r"2[A-L]", normalized):
        return get_team_by_position(standings_df, normalized[1], 2) or original

    if re.fullmatch(r"3[A-L]+", normalized):
        allowed_groups = list(normalized[1:])
        return resolve_third_team(best_thirds_df, allowed_groups) or original

    if re.fullmatch(r"W\d+", normalized):
        return results_by_match.get(normalized, original)

    if re.fullmatch(r"L\d+", normalized):
        return results_by_match.get(normalized, original)

    return original


def resolve_knockout_teams(wedstrijden):
    wedstrijden = wedstrijden.copy()

    standings_df = calculate_group_standings(wedstrijden)
    best_thirds_df = calculate_best_thirds(standings_df)

    for _ in range(6):
        results_by_match = build_results_by_match(wedstrijden)

        for index, row in wedstrijden.iterrows():
            stage = str(get_value(row, "stage")).strip()

            if is_group_stage(stage):
                continue

            team1 = str(get_value(row, "team1")).strip()
            team2 = str(get_value(row, "team2")).strip()

            wedstrijden.at[index, "team1"] = resolve_slot(
                team1,
                standings_df,
                best_thirds_df,
                results_by_match,
            )

            wedstrijden.at[index, "team2"] = resolve_slot(
                team2,
                standings_df,
                best_thirds_df,
                results_by_match,
            )

    return wedstrijden, standings_df, best_thirds_df


def show_prediction_buttons(match, match_id, selected):
    closed = match_is_locked(match)

    stage = str(get_value(match, "stage")).strip()
    knockout = is_knockout_stage(stage)

    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        if st.button(
            prediction_label("1", selected),
            key=f"wed_btn_1_{match_id}",
            use_container_width=True,
            disabled=closed,
        ):
            set_prediction(match_id, "1")
            st.rerun()

    with c2:
        if st.button(
            prediction_label("X", selected),
            key=f"wed_btn_x_{match_id}",
            use_container_width=True,
            disabled=closed or knockout,
        ):
            set_prediction(match_id, "X")
            st.rerun()

    with c3:
        if st.button(
            prediction_label("2", selected),
            key=f"wed_btn_2_{match_id}",
            use_container_width=True,
            disabled=closed,
        ):
            set_prediction(match_id, "2")
            st.rerun()


def show_wedstrijd_row(match):
    match_id = str(get_value(match, "match_id", "wedstrijd_id", "id")).strip()

    datum = str(get_value(match, "datum", "date")).strip()
    tijd = str(get_value(match, "tijd", "uur", "time")).strip()

    team1 = str(get_value(match, "team1", "land1", "thuisploeg")).strip()
    team2 = str(get_value(match, "team2", "land2", "uitploeg")).strip()

    team1_code = str(get_value(match, "team1_code", "land1_code", "code1")).strip()
    team2_code = str(get_value(match, "team2_code", "land2_code", "code2")).strip()

    closed = match_is_locked(match)

    status_html = (
        '<span style="color:#ef4444;font-weight:900;">🔒 Gesloten</span>'
        if closed
        else '<span style="color:#22c55e;font-weight:900;">🟢 Open</span>'
    )

    selected = get_selected_prediction(match_id)

    with st.container(border=True):
        col_date, col_time, col_status, col_match, col_buttons = st.columns(
            [0.85, 0.65, 1.15, 4.6, 1.7],
            gap="small",
        )

        with col_date:
            st.markdown(f"**{datum}**")

        with col_time:
            st.markdown(f"**{tijd}**")

        with col_status:
            st.markdown(status_html, unsafe_allow_html=True)

        with col_match:
            flag1 = flag_img(team1_code)
            flag2 = flag_img(team2_code)

            st.markdown(
                f"""
<div style="display:flex;align-items:center;gap:9px;font-size:1rem;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
    <span>{flag1}</span>
    <span>{team1}</span>
    <span style="color:#64748b;">-</span>
    <span>{flag2}</span>
    <span>{team2}</span>
</div>
""",
                unsafe_allow_html=True,
            )

        with col_buttons:
            show_prediction_buttons(match, match_id, selected)


def show_group_standings(standings_df):
    st.markdown("## 📊 Rankschikking groepsfase")
    st.caption("Deze stand wordt live berekend op basis van jouw groepsfase-keuzes.")

    if standings_df.empty:
        st.info("Nog geen groepsstanden beschikbaar.")
        return

    groups = sorted(standings_df["groep"].dropna().unique().tolist())

    cols = st.columns(2)

    for index, group in enumerate(groups):
        group_df = standings_df[standings_df["groep"] == group].copy()

        group_df = group_df[
            ["positie", "team", "P", "W", "G", "V", "Ptn"]
        ]

        group_df = group_df.rename(
            columns={
                "positie": "#",
                "team": "Team",
            }
        )

        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"### Group {group}")
                st.dataframe(
                    group_df,
                    hide_index=True,
                    use_container_width=True,
                )


def show_best_thirds(best_thirds_df):
    if best_thirds_df.empty:
        return

    st.markdown("## 🥉 Beste derdes")

    df = best_thirds_df.copy()
    df = df[
        ["third_rank", "groep", "team", "P", "W", "G", "V", "Ptn", "qualified"]
    ]

    df = df.rename(
        columns={
            "third_rank": "#",
            "groep": "Groep",
            "team": "Team",
            "qualified": "Door",
        }
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )


def show_wedstrijden(user, wedstrijden_df, predictions_df):
    st.markdown("## 📅 Wedstrijden")
    st.caption("Alle wedstrijden met open/gesloten status en snelle 1/X/2-keuze.")

    user_id = str(user["user_id"])
    load_existing_predictions(user_id, predictions_df)

    if wedstrijden_df is None or wedstrijden_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad 'Wedstrijden'.")
        return

    wedstrijden = normalize_columns(wedstrijden_df)

    required_columns = [
        "stage",
        "datum",
        "tijd",
        "team1",
        "team2",
        "match_id",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in wedstrijden.columns
    ]

    if missing_columns:
        st.error(
            "Tabblad 'Wedstrijden' mist deze kolommen: "
            + ", ".join(missing_columns)
        )
        st.write("Gevonden kolommen:", wedstrijden.columns.tolist())
        return

    wedstrijden = create_sort_columns(wedstrijden)
    wedstrijden = wedstrijden.sort_values(
        ["datum_sort", "tijd_sort", "match_id_sort"],
        kind="stable",
    )

    wedstrijden, standings_df, best_thirds_df = resolve_knockout_teams(wedstrijden)

    tab_wedstrijden, tab_stand = st.tabs(
        [
            "📅 Wedstrijden",
            "📊 Groepsstanden",
        ]
    )

    with tab_wedstrijden:
        for _, match in wedstrijden.iterrows():
            show_wedstrijd_row(match)

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("💾 Voorlopig opslaan", use_container_width=True):
                count = batch_upsert_predictions(
                    user_id,
                    st.session_state.get("local_predictions", {}),
                    "Voorlopig",
                )

                mark_predictions_saved()
                st.success(f"{count} keuzes opgeslagen als Voorlopig.")
                st.rerun()

        with c2:
            if st.button("✅ Definitief indienen", use_container_width=True):
                count = batch_upsert_predictions(
                    user_id,
                    st.session_state.get("local_predictions", {}),
                    "FINAL",
                )

                mark_predictions_saved()
                st.success(f"{count} keuzes definitief ingediend.")
                st.rerun()

    with tab_stand:
        show_group_standings(standings_df)
        show_best_thirds(best_thirds_df)
