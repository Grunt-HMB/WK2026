import streamlit as st

from modules.database import batch_upsert_predictions
from modules.settings import TOURNAMENT_START
from modules.utils import tournament_locked

from modules.prediction_cards import render_match_card
from modules.prediction_phases import (
    filter_matches_by_phase,
    get_phase_buttons,
    show_phase_buttons,
)
from modules.prediction_standings import show_group_standings
from modules.prediction_state import load_existing_predictions, user_is_final
from modules.prediction_styles import inject_prediction_css


def show_group_phase(user, matches_df, predictions_df, standings_df=None):
    inject_prediction_css()

    user_id = str(user["user_id"])

    load_existing_predictions(user_id, predictions_df)

    locked = tournament_locked()
    final = user_is_final(user_id, predictions_df)

    disabled = locked

    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad Matches.")
        return

    phases = get_phase_buttons(matches_df)

    if not phases:
        st.warning("Geen groepen of rondes gevonden in tabblad Matches.")
        return

    st.markdown("## 👥 Groepsfase / Eindfase")
    st.caption("Maak je voorspellingen per poule of eindfase.")

    if locked:
        st.error("🔒 Het tornooi is gestart. Wijzigen is niet meer mogelijk.")
    elif final:
        st.success("✅ Je pronostiek is ingediend. Je mag nog wijzigen tot de deadline.")
    else:
        st.info(f"🟢 Open tot {TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}.")

    selected_phase = show_phase_buttons(phases)
    selected_matches = filter_matches_by_phase(matches_df, selected_phase)

    show_group_standings(
        selected_phase,
        standings_df,
        matches_df,
    )

    selected_matches = selected_matches.copy()
    selected_matches["match_id_sort"] = (
        selected_matches["match_id"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(0)
        .astype(int)
    )

    selected_matches = selected_matches.sort_values(
        ["match_id_sort"],
        kind="stable",
    )

    st.subheader(selected_phase["key"])

    if selected_matches.empty:
        st.warning("Geen wedstrijden gevonden voor deze groep of eindfase.")
    else:
        for _, match in selected_matches.iterrows():
            render_match_card(match, disabled)

    st.markdown("---")

    b1, b2 = st.columns(2)

    with b1:
        if st.button(
            "💾 Voorlopig opslaan",
            use_container_width=True,
            disabled=disabled,
        ):
            count = batch_upsert_predictions(
                user_id,
                st.session_state["local_predictions"],
                "Voorlopig",
            )

            st.success(f"{count} keuzes opgeslagen als Voorlopig.")
            st.rerun()

    with b2:
        if st.button(
            "✅ Definitief indienen",
            use_container_width=True,
            disabled=disabled,
        ):
            count = batch_upsert_predictions(
                user_id,
                st.session_state["local_predictions"],
                "FINAL",
            )

            st.success(f"{count} keuzes definitief ingediend.")
            st.rerun()
