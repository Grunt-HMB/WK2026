import streamlit as st

from modules.database import batch_upsert_predictions
from modules.prediction_cards import match_is_locked
from modules.prediction_state import (
    load_existing_predictions,
    mark_predictions_saved,
    set_prediction,
)


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

    current = st.session_state.get("local_predictions", {}).get(match_id, {})
    selected = str(current.get("prediction", "")).upper().strip()

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


def show_wedstrijden(user, wedstrijden_df, predictions_df):
    st.markdown("## 📅 Wedstrijden")
    st.caption("Alle wedstrijden met open/gesloten status en snelle 1/X/2-keuze.")

    user_id = str(user["user_id"])
    load_existing_predictions(user_id, predictions_df)

    if wedstrijden_df is None or wedstrijden_df.empty:
        st.warning("Geen wedstrijden gevonden in tabblad 'Wedstrijden'.")
        return

    wedstrijden = wedstrijden_df.copy()

    if "match_id" not in wedstrijden.columns:
        wedstrijden["match_id"] = ""

    wedstrijden["match_id_sort"] = (
        wedstrijden["match_id"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(0)
        .astype(int)
    )

    wedstrijden = wedstrijden.sort_values(
        ["datum", "tijd", "match_id_sort"],
        kind="stable",
    )

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
