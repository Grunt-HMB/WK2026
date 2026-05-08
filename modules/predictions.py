import streamlit as st

from modules.database import batch_upsert_predictions
from modules.settings import TOURNAMENT_START
from modules.utils import result_from_score, tournament_locked


def flag_img(code):
    code = str(code or "").strip().lower()

    if len(code) != 2:
        return ""

    return (
        f'<img src="https://flagcdn.com/w40/{code}.png" '
        f'style="width:30px;height:22px;object-fit:cover;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.25);vertical-align:middle;">'
    )


def football_badge(choice):
    choice = str(choice or "").strip().upper()

    if choice not in ["1", "X", "2"]:
        choice = "-"

    color = "#111111"

    if choice == "1":
        color = "#16a34a"
    elif choice == "X":
        color = "#2563eb"
    elif choice == "2":
        color = "#dc2626"

    return (
        f'<div style="position:relative;width:46px;height:46px;'
        f'display:flex;align-items:center;justify-content:center;">'
        f'<span style="font-size:2.45rem;line-height:1;"><img src="https://upload.wikimedia.org/wikipedia/commons/d/d3/Soccerball.svg"
style="width:42px;height:42px;"></span>'
        f'<span style="position:absolute;inset:0;display:flex;'
        f'align-items:center;justify-content:center;font-size:1,9rem;'
        f'font-weight:900;color:#000000;'
        f'text-shadow:0 0 2px white,0 0 3px white,0 0 4px white;">'
        f'{choice}</span></div>'
    )


def load_existing_predictions(user_id, predictions_df):
    loaded_key = f"loaded_predictions_{user_id}"

    if "local_predictions" not in st.session_state:
        st.session_state["local_predictions"] = {}

    if loaded_key in st.session_state:
        return

    if predictions_df.empty:
        st.session_state[loaded_key] = True
        return

    user_preds = predictions_df[
        predictions_df["user_id"].astype(str) == str(user_id)
    ]

    for _, row in user_preds.iterrows():
        match_id = str(row.get("match_id", ""))

        if match_id:
            st.session_state["local_predictions"][match_id] = {
                "prediction": str(row.get("prediction", "")),
                "score1": row.get("score1", ""),
                "score2": row.get("score2", ""),
            }

    st.session_state[loaded_key] = True


def user_is_final(user_id, predictions_df):
    if predictions_df.empty:
        return False

    user_preds = predictions_df[
        predictions_df["user_id"].astype(str) == str(user_id)
    ]

    if user_preds.empty:
        return False

    return (user_preds["status"].astype(str).str.upper() == "FINAL").any()


def set_prediction(match_id, choice):
    if "local_predictions" not in st.session_state:
        st.session_state["local_predictions"] = {}

    current = st.session_state["local_predictions"].get(str(match_id), {})

    current["prediction"] = choice
    current.setdefault("score1", "")
    current.setdefault("score2", "")

    st.session_state["local_predictions"][str(match_id)] = current


def set_score(match_id, score1, score2):
    prediction = result_from_score(score1, score2)

    st.session_state["local_predictions"][str(match_id)] = {
        "prediction": prediction,
        "score1": score1,
        "score2": score2,
    }


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
                if st.button(
                    str(num),
                    key=f"{side}_{match_id}_{num}",
                    use_container_width=True,
                ):
                    st.session_state[score_key] = str(num)
                    st.rerun()

    bottom = st.columns(3, gap="small")

    with bottom[0]:
        if st.button(
            "0",
            key=f"{side}_{match_id}_0",
            use_container_width=True,
        ):
            st.session_state[score_key] = "0"
            st.rerun()

    with bottom[1]:
        if st.button(
            "⌫",
            key=f"reset_{side}_{match_id}",
            use_container_width=True,
        ):
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

        if (
            st.session_state[score1_key] != ""
            and
            st.session_state[score2_key] != ""
        ):
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

            if st.button(
                "✅ Bevestigen",
                key=f"confirm_score_{match_id}",
                use_container_width=True,
            ):
                set_score(match_id, s1, s2)

                st.session_state[f"show_score_{match_id}"] = False

                st.rerun()


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

    selected = str(current.get("prediction", ""))
    score1 = current.get("score1", "")
    score2 = current.get("score2", "")

    with st.container(border=True):

        col_date, col_time, col_info, col_1, col_x, col_2, col_ball, col_score = st.columns(
            [0.9, 0.7, 4.7, 0.45, 0.45, 0.45, 0.55, 1.05],
            gap="small",
        )

        with col_date:
            st.markdown(
                f"""
<div style="
font-size:0.82rem;
font-weight:800;
color:#64748b;
padding-top:7px;
">
{date}
</div>
""",
                unsafe_allow_html=True,
            )

        with col_time:
            st.markdown(
                f"""
<div style="
font-size:0.82rem;
font-weight:800;
color:#64748b;
padding-top:7px;
">
{time}
</div>
""",
                unsafe_allow_html=True,
            )

        with col_info:
            score_part = ""

            if score1 != "" and score2 != "":
                score_part = (
                    f"<span style='color:#64748b;"
                    f"margin-left:12px;font-weight:800;'>"
                    f"{score1}-{score2}</span>"
                )

            st.markdown(
                f"""
<div style="
display:flex;
align-items:center;
gap:9px;
font-size:1rem;
font-weight:900;
white-space:nowrap;
overflow:hidden;
text-overflow:ellipsis;
padding-top:3px;
">

<span>{flag1}</span>
<span>{team1}</span>

<span style="color:#64748b;margin:0 2px;">-</span>

<span>{flag2}</span>
<span>{team2}</span>

{score_part}

</div>
""",
                unsafe_allow_html=True,
            )

        with col_1:
            if st.button(
                "1",
                key=f"btn_1_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "1")
                st.rerun()

        with col_x:
            if st.button(
                "X",
                key=f"btn_x_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "X")
                st.rerun()

        with col_2:
            if st.button(
                "2",
                key=f"btn_2_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "2")
                st.rerun()

        with col_ball:
            st.markdown(
                football_badge(selected),
                unsafe_allow_html=True,
            )

        with col_score:
            if st.button(
                "Uitslag",
                key=f"score_button_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                st.session_state[f"show_score_{match_id}"] = (
                    not st.session_state.get(
                        f"show_score_{match_id}",
                        False,
                    )
                )

                st.rerun()

        if st.session_state.get(f"show_score_{match_id}", False):
            show_score_dialog(match, match_id)


def show_group_phase(user, matches_df, predictions_df):
    user_id = str(user["user_id"])

    load_existing_predictions(user_id, predictions_df)

    locked = tournament_locked()
    final = user_is_final(user_id, predictions_df)

    disabled = locked

    groups = sorted([
        str(g)
        for g in matches_df["groep"].dropna().unique()
        if str(g).strip() not in ["", "-", "Knock-out"]
    ])

    if not groups:
        st.warning("Geen groepen gevonden in tabblad Matches.")
        return

    top1, top2 = st.columns([3, 1])

    with top1:
        st.markdown("## 👥 Groepsfase")
        st.caption("Maak je voorspellingen per poule.")

    with top2:
        selected_group = st.selectbox(
            "Groep",
            groups,
            label_visibility="collapsed",
        )

    if locked:
        st.error("🔒 Het tornooi is gestart. Wijzigen is niet meer mogelijk.")

    elif final:
        st.success(
            "✅ Je pronostiek is ingediend. "
            "Je mag nog wijzigen tot de deadline."
        )

    else:
        st.info(
            f"🟢 Open tot "
            f"{TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}."
        )

    group_matches = matches_df[
        matches_df["groep"].astype(str) == str(selected_group)
    ].copy()

    group_matches = group_matches.sort_values(
        ["datum", "tijd", "match_id"],
        kind="stable",
    )

    st.subheader(f"Groep {selected_group}")

    for _, match in group_matches.iterrows():
        render_match_card(match, disabled)

    st.markdown("---")

    b1, b2 = st.columns(2)

    with b1:
        if st.button(
            "💾 Concept opslaan",
            use_container_width=True,
            disabled=disabled,
        ):
            count = batch_upsert_predictions(
                user_id,
                st.session_state["local_predictions"],
                "DRAFT",
            )

            st.success(f"{count} keuzes opgeslagen als concept.")

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

            st.success(
                f"{count} keuzes definitief ingediend."
            )

            st.rerun()
