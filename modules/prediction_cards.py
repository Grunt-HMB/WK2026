import streamlit as st

from modules.utils import result_from_score
from modules.prediction_state import set_prediction, set_score


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:30px;height:22px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.25);vertical-align:middle;">'
    )


def score_header_html(team1, team2, score1, score2):
    left_score = score1 if score1 != "" else "-"
    right_score = score2 if score2 != "" else "-"

    return f"""
<div style="display:flex;align-items:center;justify-content:center;gap:14px;margin:4px 0 8px 0;">
  <div style="text-align:center;min-width:82px;">
    <div style="font-size:0.82rem;font-weight:800;">{team1}</div>
    <div style="font-size:2rem;font-weight:900;color:#2563eb;line-height:1;">{left_score}</div>
  </div>
  <div style="font-size:1.3rem;font-weight:900;">-</div>
  <div style="text-align:center;min-width:82px;">
    <div style="font-size:0.82rem;font-weight:800;">{team2}</div>
    <div style="font-size:2rem;font-weight:900;color:#dc2626;line-height:1;">{right_score}</div>
  </div>
</div>
"""


def show_number_pad(match_id, team_name, score_key, side):
    st.markdown(
        f"<div style='font-size:0.85rem;font-weight:900;margin-bottom:3px;'>{team_name}</div>",
        unsafe_allow_html=True,
    )

    for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
        cols = st.columns(3, gap="small")

        for idx, num in enumerate(row):
            with cols[idx]:
                if st.button(str(num), key=f"{side}_{match_id}_{num}", use_container_width=True):
                    st.session_state[score_key] = str(num)
                    st.rerun()

    bottom = st.columns(3, gap="small")

    with bottom[0]:
        if st.button("0", key=f"{side}_{match_id}_0", use_container_width=True):
            st.session_state[score_key] = "0"
            st.rerun()

    with bottom[1]:
        if st.button("⌫", key=f"reset_{side}_{match_id}", use_container_width=True):
            st.session_state[score_key] = ""
            st.rerun()


def show_score_dialog(match, match_id):
    team1 = str(match.get("team1", ""))
    team2 = str(match.get("team2", ""))

    current = st.session_state["local_predictions"].get(str(match_id), {})

    score1_key = f"temp_score1_{match_id}"
    score2_key = f"temp_score2_{match_id}"

    if score1_key not in st.session_state:
        st.session_state[score1_key] = str(current.get("score1", ""))

    if score2_key not in st.session_state:
        st.session_state[score2_key] = str(current.get("score2", ""))

    with st.container(border=True):
        st.markdown("##### ⚽ Exacte uitslag")

        st.markdown(
            score_header_html(
                team1,
                team2,
                st.session_state[score1_key],
                st.session_state[score2_key],
            ),
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns(2, gap="small")

        with col_left:
            show_number_pad(match_id, team1, score1_key, "s1")

        with col_right:
            show_number_pad(match_id, team2, score2_key, "s2")

        if st.session_state[score1_key] != "" and st.session_state[score2_key] != "":
            s1 = int(st.session_state[score1_key])
            s2 = int(st.session_state[score2_key])

            prediction = result_from_score(s1, s2)

            if prediction == "1":
                pred_text = f"{team1} wint"
            elif prediction == "2":
                pred_text = f"{team2} wint"
            else:
                pred_text = "Gelijkspel"

            st.success(f"{s1} - {s2} → {pred_text}")

            if st.button("✅ Bevestigen", key=f"confirm_score_{match_id}", use_container_width=True):
                set_score(match_id, s1, s2)
                st.session_state[f"show_score_{match_id}"] = False
                st.rerun()


def prediction_label(choice, selected):
    choice = str(choice)
    selected = str(selected or "").upper()

    if selected == choice:
        return f"✅ {choice}"

    return choice


def render_prediction_buttons(match_id, selected, disabled):
    st.markdown('<div class="match-actions">', unsafe_allow_html=True)

    b1, bx, b2, bs = st.columns([1, 1, 1, 1.9], gap="small")

    with b1:
        if st.button(prediction_label("1", selected), key=f"btn_1_{match_id}", use_container_width=True, disabled=disabled):
            set_prediction(match_id, "1")
            st.rerun()

    with bx:
        if st.button(prediction_label("X", selected), key=f"btn_x_{match_id}", use_container_width=True, disabled=disabled):
            set_prediction(match_id, "X")
            st.rerun()

    with b2:
        if st.button(prediction_label("2", selected), key=f"btn_2_{match_id}", use_container_width=True, disabled=disabled):
            set_prediction(match_id, "2")
            st.rerun()

    with bs:
        st.markdown('<div class="score-button">', unsafe_allow_html=True)

        if st.button("Uitslag", key=f"score_button_{match_id}", use_container_width=True, disabled=disabled):
            st.session_state[f"show_score_{match_id}"] = not st.session_state.get(
                f"show_score_{match_id}",
                False,
            )
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

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

    with st.container(border=True):
        col_info, col_buttons = st.columns([6.5, 2.8], gap="small")

        with col_info:
            score_part = ""

            if score1 != "" and score2 != "":
                score_part = (
                    f"<span style='color:#64748b;margin-left:10px;font-weight:900;'>"
                    f"{score1}-{score2}</span>"
                )

            st.markdown(
                f"""
<div style="display:flex;flex-direction:column;gap:3px;">
  <div style="font-size:0.78rem;font-weight:800;color:#64748b;">
    {date} &nbsp; {time}
  </div>
  <div style="display:flex;align-items:center;gap:8px;font-size:1rem;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
    <span>{flag1}</span>
    <span>{team1}</span>
    <span style="color:#64748b;">-</span>
    <span>{flag2}</span>
    <span>{team2}</span>
    {score_part}
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col_buttons:
            render_prediction_buttons(match_id, selected, disabled)

        if st.session_state.get(f"show_score_{match_id}", False):
            show_score_dialog(match, match_id)
