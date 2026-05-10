import streamlit as st

from modules.prediction_cards import match_is_locked
from modules.prediction_state import set_prediction
from modules.wedstrijd_helpers import (
    get_value,
    flag_img,
    is_knockout_stage,
)


def get_selected_prediction(match_id):
    current = st.session_state.get("local_predictions", {}).get(str(match_id), {})
    return str(current.get("prediction", "")).upper().strip()


def prediction_label(choice, selected):
    selected = str(selected or "").upper().strip()

    if choice == "X" and selected in ["X", "X1", "X2"]:
        return "✅ X"

    if selected == choice:
        return f"✅ {choice}"

    return choice


def knockout_extra_label(team, selected_code, selected):
    selected = str(selected or "").upper().strip()

    if selected == selected_code:
        return f"✅ {team} gaat door"

    return f"{team} gaat door"


def show_prediction_buttons(match, match_id, selected):
    closed = match_is_locked(match)

    stage = str(get_value(match, "stage")).strip()
    knockout = is_knockout_stage(stage)

    team1 = str(get_value(match, "team1")).strip()
    team2 = str(get_value(match, "team2")).strip()

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

    if knockout and selected == "X":
        st.caption("Wie gaat door na verlengingen/penalty's?")

        k1, k2 = st.columns(2, gap="small")

        with k1:
            if st.button(
                knockout_extra_label(team1, "X1", selected),
                key=f"wed_btn_x1_{match_id}",
                use_container_width=True,
                disabled=closed or team1 == "",
            ):
                set_prediction(match_id, "X1")
                st.rerun()

        with k2:
            if st.button(
                knockout_extra_label(team2, "X2", selected),
                key=f"wed_btn_x2_{match_id}",
                use_container_width=True,
                disabled=closed or team2 == "",
            ):
                set_prediction(match_id, "X2")
                st.rerun()

    if knockout and selected in ["X1", "X2"]:
        doorgaan = team1 if selected == "X1" else team2
        st.caption(f"Na gelijkspel gaat door: **{doorgaan}**")


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
            [0.85, 0.65, 1.15, 4.6, 1.9],
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
