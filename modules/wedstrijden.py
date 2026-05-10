import streamlit as st

from modules.database import batch_upsert_predictions
from modules.prediction_state import (
    load_existing_predictions,
    mark_predictions_saved,
)

from modules.wedstrijd_helpers import (
    normalize_columns,
    get_value,
)

from modules.wedstrijd_knockout import resolve_knockout_teams
from modules.wedstrijd_components import show_wedstrijd_row
from modules.wedstrijd_standings import (
    show_group_standings,
    show_best_thirds,
)


def validate_required_columns(wedstrijden):
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

    if "ronde" not in wedstrijden.columns and "stage" not in wedstrijden.columns:
        missing_columns.append("ronde of stage")

    return missing_columns


def show_save_buttons(user_id):
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


def get_round_value(match):
    ronde = str(get_value(match, "ronde")).strip()
    stage = str(get_value(match, "stage")).strip()

    if ronde:
        return ronde

    return stage


def round_title(match):
    ronde = get_round_value(match)
    groep = str(get_value(match, "groep")).strip().upper()

    ronde_clean = ronde.strip().lower()

    if ronde_clean == "group":
        return "🌍 Groepsfase"

    if ronde_clean.startswith("group "):
        return "🌍 Groepsfase"

    titles = {
        "round of 32": "🏆 1/16 finales",
        "round of 16": "🏆 1/8 finales",
        "quarterfinals": "🏆 Kwartfinales",
        "quarter finals": "🏆 Kwartfinales",
        "semifinals": "🏆 Halve finales",
        "semi finals": "🏆 Halve finales",
        "third place": "🥉 Troostwedstrijd",
        "final": "🏆 Finale",
    }

    if ronde_clean in titles:
        return titles[ronde_clean]

    if groep in list("ABCDEFGHIJKL"):
        return "🌍 Groepsfase"

    return ronde if ronde else "Wedstrijden"


def show_wedstrijden_list(wedstrijden):
    vorige_titel = None

    for _, match in wedstrijden.iterrows():
        titel = round_title(match)

        if titel != vorige_titel:
            st.markdown("---")
            st.markdown(f"## {titel}")
            vorige_titel = titel

        show_wedstrijd_row(match)


def show_wedstrijden(user, wedstrijden_df, predictions_df):
    st.markdown("## 📅 Wedstrijden")
    st.caption("Alle wedstrijden met open/gesloten status en snelle 1/X/2-keuze.")

    user_id = str(user["user_id"])
    load_existing_predictions(user_id, predictions_df)

    if wedstrijden_df is None or wedstrijden_df.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    wedstrijden = normalize_columns(wedstrijden_df)

    missing_columns = validate_required_columns(wedstrijden)

    if missing_columns:
        st.error(
            "Tabblad 'Matches' mist deze kolommen: "
            + ", ".join(missing_columns)
        )
        st.write("Gevonden kolommen:", wedstrijden.columns.tolist())
        return

    wedstrijden["match_id_sort"] = (
        wedstrijden["match_id"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(999999)
        .astype(int)
    )

    wedstrijden = wedstrijden.sort_values(
        ["match_id_sort"],
        kind="stable",
    )

    wedstrijden, standings_df, best_thirds_df = resolve_knockout_teams(
        wedstrijden
    )

    tab_wedstrijden, tab_stand = st.tabs(
        [
            "📅 Wedstrijden",
            "📊 Groepsstanden",
        ]
    )

    with tab_wedstrijden:
        show_wedstrijden_list(wedstrijden)
        show_save_buttons(user_id)

    with tab_stand:
        show_group_standings(standings_df)
        show_best_thirds(best_thirds_df)
