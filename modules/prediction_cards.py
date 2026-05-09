import streamlit as st

from modules.prediction_state import set_prediction


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
    choice = str(choice)
    selected = str(selected or "").upper()

    if selected == choice:
        return f"✅ {choice}"

    return choice


def render_prediction_buttons(match_id, selected, disabled):
    st.markdown('<div class="match-actions">', unsafe_allow_html=True)

    c1, cx, c2 = st.columns(3, gap="small")

    with c1:
        if st.button(
            prediction_label("1", selected),
            key=f"btn_1_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):
            set_prediction(match_id, "1")
            st.rerun()

    with cx:
        if st.button(
            prediction_label("X", selected),
            key=f"btn_x_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):
            set_prediction(match_id, "X")
            st.rerun()

    with c2:
        if st.button(
            prediction_label("2", selected),
            key=f"btn_2_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):
            set_prediction(match_id, "2")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_match_card(match, disabled):
    match_id = str(match["match_id"])

    team1 = str(match.get("team1", ""))
    team2 = str(match.get("team2", ""))

    code1 = str(match.get("team1_code", "")).upper()
    code2 = str(match.get("team2_code", "")).upper()

    flag1 = flag_img(code1)
    flag2 = flag_img(code2)

    date = str(match.get("datum", ""))
    time = str(match.get("tijd", ""))

    current = st.session_state["local_predictions"].get(match_id, {})
    selected = str(current.get("prediction", "")).upper()

    score1 = current.get("score1", "")
    score2 = current.get("score2", "")

    if score1 != "" and score2 != "":
        middle = f"{score1}-{score2}"
    else:
        middle = "-"

    with st.container(border=True):
        left, right = st.columns([7, 2.1], gap="small")

        with left:
            st.markdown(
                f"""
<div class="match-row">
    <div class="match-date">
        {date}<br>{time}
    </div>

    <div class="match-teams">
        <div class="team-left">
            <span>{flag1}</span>
            <span class="team-name">{team1}</span>
        </div>

        <div class="match-score">{middle}</div>

        <div class="team-right">
            <span>{flag2}</span>
            <span class="team-name">{team2}</span>
        </div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

        with right:
            render_prediction_buttons(match_id, selected, disabled)
