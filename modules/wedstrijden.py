import streamlit as st
import pandas as pd

from modules.database import batch_upsert_predictions
from modules.prediction_cards import match_is_locked
from modules.prediction_state import (
    load_existing_predictions,
    mark_predictions_saved,
    set_prediction,
)


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
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )
    return df


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

    if "datum" not in wedstrijden.columns:
        wedstrijden["datum"] = ""

    if "tijd" not in wedstrijden.columns:
        wedstrijden["tijd"] = ""

    if "match_id" not in wedstrijden.columns:
        wedstrijden["match_id"] = ""

    if "match_id_sort" not in wedstrijden.columns:
        wedstrijden["match_id_sort"] = wedstrijden["match_id"]

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
    )

    wedstrijden["match_id_sort"] = wedstrijden["match_id_sort"].fillna(
        pd.to_numeric(wedstrijden["match_id"], errors="coerce")
    )

    wedstrijden["match_id_sort"] = wedstrijden["match_id_sort"].fillna(999999)

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


def get_value(row, *names):
    for name in names:
        if name in row and str(row.get(name, "")).strip() != "":
            return row.get(name, "")

    return ""


def prediction_label(choice, selected):
    selected = str(selected or "").upper().strip()

    if selected == choice:
        return f"✅ {choice}"

    return choice


def get_selected_prediction(match_id):
    current = st.session_state.get("local_predictions", {}).get(str(match_id), {})
    return str(current.get("prediction", "")).upper().strip()


def show_prediction_buttons(match, match_id, selected):
    closed = match_is_locked(match)

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
            disabled=closed,
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


def init_team(table, team):
    if team not in table:
        table[team] = {
            "Team": team,
            "P": 0,
            "W": 0,
            "G": 0,
            "V": 0,
            "Ptn": 0,
        }


def calculate_group_standings(wedstrijden):
    group_tables = {}

    for _, match in wedstrijden.iterrows():
        group_name = str(
            get_value(match, "groep", "stage", "poule", "group")
        ).strip()

        if group_name == "":
            group_name = "Onbekend"

        match_id = str(get_value(match, "match_id", "wedstrijd_id", "id")).strip()
        team1 = str(get_value(match, "team1", "land1", "thuisploeg")).strip()
        team2 = str(get_value(match, "team2", "land2", "uitploeg")).strip()

        if team1 == "" or team2 == "":
            continue

        if group_name not in group_tables:
            group_tables[group_name] = {}

        table = group_tables[group_name]

        init_team(table, team1)
        init_team(table, team2)

        prediction = get_selected_prediction(match_id)

        if prediction not in ["1", "X", "2"]:
            continue

        table[team1]["P"] += 1
        table[team2]["P"] += 1

        if prediction == "1":
            table[team1]["W"] += 1
            table[team1]["Ptn"] += 3
            table[team2]["V"] += 1

        elif prediction == "2":
            table[team2]["W"] += 1
            table[team2]["Ptn"] += 3
            table[team1]["V"] += 1

        elif prediction == "X":
            table[team1]["G"] += 1
            table[team2]["G"] += 1
            table[team1]["Ptn"] += 1
            table[team2]["Ptn"] += 1

    result = {}

    for group_name, table in group_tables.items():
        df = pd.DataFrame(list(table.values()))

        if not df.empty:
            df = df.sort_values(
                ["Ptn", "W", "Team"],
                ascending=[False, False, True],
                kind="stable",
            ).reset_index(drop=True)

            df.insert(0, "#", range(1, len(df) + 1))

        result[group_name] = df

    return result


def show_group_standings(wedstrijden):
    st.markdown("## 📊 Rankschikking per poule")
    st.caption("Deze stand wordt live berekend op basis van jouw 1/X/2-keuzes.")

    standings = calculate_group_standings(wedstrijden)

    if not standings:
        st.info("Nog geen poules gevonden.")
        return

    group_names = sorted(standings.keys())

    cols = st.columns(2)

    for index, group_name in enumerate(group_names):
        df = standings[group_name]

        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"### {group_name}")

                if df.empty:
                    st.info("Nog geen data.")
                else:
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

    tab_wedstrijden, tab_stand = st.tabs(
        [
            "📅 Wedstrijden",
            "📊 Rankschikking",
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
        show_group_standings(wedstrijden)
