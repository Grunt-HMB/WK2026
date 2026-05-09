import streamlit as st

from modules.database import batch_upsert_predictions
from modules.settings import TOURNAMENT_START

from modules.prediction_cards import match_is_locked, render_match_card
from modules.prediction_phases import (
    filter_matches_by_phase,
    get_phase_buttons,
    show_phase_buttons,
)
from modules.prediction_standings import show_group_standings
from modules.prediction_state import (
    discard_unsaved_predictions,
    load_existing_predictions,
    mark_predictions_saved,
    user_is_final,
)
from modules.prediction_styles import inject_prediction_css


def find_phase_by_key(phases, phase_key):
    for phase in phases:
        if phase["key"] == phase_key:
            return phase

    return None


def get_open_predictions_only(matches_df):
    open_match_ids = set()

    for _, match in matches_df.iterrows():
        match_id = str(match.get("match_id", "")).strip()

        if not match_id:
            continue

        if not match_is_locked(match):
            open_match_ids.add(match_id)

    local_predictions = st.session_state.get("local_predictions", {})

    return {
        match_id: data
        for match_id, data in local_predictions.items()
        if str(match_id).strip() in open_match_ids
    }


def save_current_predictions(user_id, status, matches_df):
    open_predictions = get_open_predictions_only(matches_df)
    total_predictions = len(st.session_state.get("local_predictions", {}))

    count = batch_upsert_predictions(
        user_id,
        open_predictions,
        status,
    )

    mark_predictions_saved()

    skipped = total_predictions - len(open_predictions)

    return count, skipped


def show_pending_phase_change_prompt(user_id, phases, matches_df):
    pending_key = st.session_state.get("pending_phase_key", "")

    if not pending_key:
        return False

    pending_phase = find_phase_by_key(phases, pending_key)

    if pending_phase is None:
        st.session_state["pending_phase_key"] = ""
        return False

    label = pending_phase.get("label", pending_key)

    st.warning(f"Je hebt niet-opgeslagen wijzigingen. Opslaan voor je naar {label} gaat?")

    c1, c2, c3 = st.columns([1, 1, 4], gap="small")

    with c1:
        if st.button("✅ Ja, opslaan", use_container_width=True):
            count, skipped = save_current_predictions(user_id, "Voorlopig", matches_df)

            st.session_state["selected_phase_key"] = pending_key
            st.session_state["pending_phase_key"] = ""

            if skipped > 0:
                st.warning(
                    f"{count} keuzes opgeslagen. "
                    f"{skipped} gesloten wedstrijd(en) niet opgeslagen."
                )
            else:
                st.success(f"{count} keuzes opgeslagen.")

            st.rerun()

    with c2:
        if st.button("❌ Nee", use_container_width=True):
            discard_unsaved_predictions()

            st.session_state["selected_phase_key"] = pending_key
            st.session_state["pending_phase_key"] = ""

            st.rerun()

    return True


def show_group_phase(user, matches_df, predictions_df, standings_df=None):
    inject_prediction_css()

    user_id = str(user["user_id"])

    load_existing_predictions(user_id, predictions_df)

    final = user_is_final(user_id, predictions_df)
    disabled = False

    if matches_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad Matches.")
        return

    phases = get_phase_buttons(matches_df)

    if not phases:
        st.warning("Geen groepen of rondes gevonden in tabblad Matches.")
        return

    st.markdown("## 👥 Groepsfase / Eindfase")
    st.caption("Maak je voorspellingen per poule of eindfase.")

    if final:
        st.success("✅ Je pronostiek is ingediend. Je mag nog wijzigen tot een wedstrijd sluit.")
    else:
        st.info("🟢 Wedstrijden sluiten automatisch 1 uur voor aftrap.")

    st.caption(
        f"Algemene tornooidatum: {TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}. "
        "Per wedstrijd geldt: sluiten 1 uur voor aftrap."
    )

    if st.session_state.get("unsaved_changes", False):
        st.warning("⚠️ Je hebt niet-opgeslagen wijzigingen.")

    selected_phase = show_phase_buttons(phases)

    prompt_active = show_pending_phase_change_prompt(user_id, phases, matches_df)

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

    if prompt_active:
        st.caption("Kies hierboven eerst of je je wijzigingen wil opslaan.")
    elif selected_matches.empty:
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
        ):
            count, skipped = save_current_predictions(user_id, "Voorlopig", matches_df)

            if skipped > 0:
                st.warning(
                    f"{count} keuzes opgeslagen. "
                    f"{skipped} gesloten wedstrijd(en) niet opgeslagen."
                )
            else:
                st.success(f"{count} keuzes opgeslagen als Voorlopig.")

            st.rerun()

    with b2:
        if st.button(
            "✅ Definitief indienen",
            use_container_width=True,
        ):
            count, skipped = save_current_predictions(user_id, "FINAL", matches_df)

            if skipped > 0:
                st.warning(
                    f"{count} keuzes definitief ingediend. "
                    f"{skipped} gesloten wedstrijd(en) niet opgeslagen."
                )
            else:
                st.success(f"{count} keuzes definitief ingediend.")

            st.rerun()
