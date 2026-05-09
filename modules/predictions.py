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

            if st.button(
                "✅ Bevestigen",
                key=f"confirm_score_{match_id}",
                use_container_width=True,
            ):
                set_score(match_id, s1, s2)
                st.session_state[f"show_score_{match_id}"] = False
                st.rerun()


def prediction_label(choice, selected):
    choice = str(choice)
    selected = str(selected or "").upper()

    if selected == choice:
        if choice == "1":
            return "🟩 1"
        if choice == "X":
            return "🟦 X"
        if choice == "2":
            return "🟥 2"

    return choice


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
        col_date, col_time, col_info, col_1, col_x, col_2, col_score = st.columns(
            [0.9, 0.7, 5.2, 0.55, 0.55, 0.55, 1.15],
            gap="small",
        )

        with col_date:
            st.markdown(
                f"""
<div style="font-size:0.82rem;font-weight:800;color:#64748b;padding-top:7px;">
{date}
</div>
""",
                unsafe_allow_html=True,
            )

        with col_time:
            st.markdown(
                f"""
<div style="font-size:0.82rem;font-weight:800;color:#64748b;padding-top:7px;">
{time}
</div>
""",
                unsafe_allow_html=True,
            )

        with col_info:
            score_part = ""

            if score1 != "" and score2 != "":
                score_part = (
                    f"<span style='color:#64748b;margin-left:12px;font-weight:800;'>"
                    f"{score1}-{score2}</span>"
                )

            st.markdown(
                f"""
<div style="display:flex;align-items:center;gap:9px;font-size:1rem;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-top:3px;">
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
                prediction_label("1", selected),
                key=f"btn_1_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "1")
                st.rerun()

        with col_x:
            if st.button(
                prediction_label("X", selected),
                key=f"btn_x_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "X")
                st.rerun()

        with col_2:
            if st.button(
                prediction_label("2", selected),
                key=f"btn_2_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                set_prediction(match_id, "2")
                st.rerun()

        with col_score:
            if st.button(
                "Uitslag",
                key=f"score_button_{match_id}",
                use_container_width=True,
                disabled=disabled,
            ):
                st.session_state[f"show_score_{match_id}"] = not st.session_state.get(
                    f"show_score_{match_id}",
                    False,
                )
                st.rerun()

        if st.session_state.get(f"show_score_{match_id}", False):
            show_score_dialog(match, match_id)


def get_phase_buttons(matches_df):
    phases = []

    group_values = sorted([
        str(g)
        for g in matches_df["groep"].dropna().unique()
        if str(g).strip() not in ["", "-", "Knock-out"]
    ])

    for group in group_values:
        phases.append({
            "key": f"Groep {group}",
            "label": group,
            "type": "groep",
            "value": group,
        })

    ronde_order = [
        ("1/16", "1/16"),
        ("1/8", "1/8"),
        ("1/4", "1/4"),
        ("1/2", "1/2"),
        ("Troostfinale", "Troost"),
        ("Finale", "Finale"),
    ]

    if "ronde" in matches_df.columns:
        ronde_values = set(matches_df["ronde"].dropna().astype(str).str.strip().tolist())

        for ronde_value, label in ronde_order:
            if ronde_value in ronde_values:
                phases.append({
                    "key": ronde_value,
                    "label": label,
                    "type": "ronde",
                    "value": ronde_value,
                })

    return phases


def show_phase_buttons(phases):
    if not phases:
        return None

    valid_keys = [p["key"] for p in phases]

    if "selected_phase_key" not in st.session_state:
        st.session_state["selected_phase_key"] = valid_keys[0]

    if st.session_state["selected_phase_key"] not in valid_keys:
        st.session_state["selected_phase_key"] = valid_keys[0]

    st.markdown("### Kies groep / eindfase")

    cols_per_row = 8

    for start in range(0, len(phases), cols_per_row):
        row = phases[start:start + cols_per_row]
        cols = st.columns(cols_per_row, gap="small")

        for idx, phase in enumerate(row):
            with cols[idx]:
                is_active = st.session_state["selected_phase_key"] == phase["key"]
                label = f"✅ {phase['label']}" if is_active else phase["label"]

                if st.button(
                    label,
                    key=f"phase_button_{phase['key']}",
                    use_container_width=True,
                ):
                    st.session_state["selected_phase_key"] = phase["key"]
                    st.rerun()

    selected_key = st.session_state["selected_phase_key"]

    for phase in phases:
        if phase["key"] == selected_key:
            return phase

    return phases[0]


def filter_matches_by_phase(matches_df, phase):
    if phase["type"] == "groep":
        return matches_df[matches_df["groep"].astype(str) == str(phase["value"])].copy()

    if phase["type"] == "ronde":
        return matches_df[matches_df["ronde"].astype(str) == str(phase["value"])].copy()

    return matches_df.copy()


def show_group_phase(user, matches_df, predictions_df, standings_df=None):
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

    st.markdown("## 👥 Groepsfase")
    st.caption("Maak je voorspellingen per poule of eindfase.")

    if locked:
        st.error("🔒 Het tornooi is gestart. Wijzigen is niet meer mogelijk.")
    elif final:
        st.success("✅ Je pronostiek is ingediend. Je mag nog wijzigen tot de deadline.")
    else:
        st.info(f"🟢 Open tot {TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}.")

    selected_phase = show_phase_buttons(phases)
    selected_matches = filter_matches_by_phase(matches_df, selected_phase)
if selected_phase["type"] == "groep" and standings_df is not None and not standings_df.empty:
    group = str(selected_phase["value"])

    group_standings = standings_df[
        standings_df["groep"].astype(str) == group
    ].copy()

    if not group_standings.empty:
        st.markdown("### 📊 Stand")

        st.dataframe(
            group_standings[
                [
                    "position",
                    "team",
                    "played",
                    "wins",
                    "draws",
                    "losses",
                    "goals_for",
                    "goals_against",
                    "goal_diff",
                    "points",
                ]
            ],
            use_container_width=True,
            hide_index=True,
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
