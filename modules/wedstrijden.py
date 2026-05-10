import streamlit as st

from modules.database import batch_upsert_predictions
from modules.prediction_state import (
    load_existing_predictions,
    mark_predictions_saved,
)

from modules.wedstrijd_helpers import (
    normalize_columns,
    create_sort_columns,
    get_value,
    stage_title,
)

from modules.wedstrijd_knockout import resolve_knockout_teams
from modules.wedstrijd_components import show_wedstrijd_row
from modules.wedstrijd_standings import (
    show_group_standings,
    show_best_thirds,
)


def validate_required_columns(wedstrijden):
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


def round_group_title(stage):
    stage = str(stage or "").strip()

    if stage.lower().startswith("group "):
        return "🌍 Groepsfase"

    return stage_title(stage)


def show_wedstrijden_list(wedstrijden):
    vorige_titel = None

    for _, match in wedstrijden.iterrows():
        stage = str(get_value(match, "stage")).strip()
        titel = round_group_title(stage)

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
        st.warning("Geen wedstrijden gevonden in tabblad 'Wedstrijden'.")
        return

    wedstrijden = normalize_columns(wedstrijden_df)

    missing_columns = validate_required_columns(wedstrijden)

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
        show_wedstrijden_list(wedstrijden)
        show_save_buttons(user_id)

    with tab_stand:
        show_group_standings(standings_df)
        show_best_thirds(best_thirds_df)
