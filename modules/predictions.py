import streamlit as st

from modules.database import batch_upsert_predictions
from modules.settings import TOURNAMENT_START
from modules.utils import flag_emoji, result_from_score, tournament_locked, safe_int


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


def score_display_html(team1, team2, score1, score2):
    left_score = score1 if score1 != "" else "-"
    right_score = score2 if score2 != "" else "-"

    return f"""
<div style="display:flex;justify-content:center;align-items:center;gap:35px;font-weight:800;margin:12px 0 22px 0;">
  <div style="text-align:center;min-width:130px;">
    <div style="font-size:1.1rem;">{team1}</div>
    <div style="font-size:3.4rem;color:#2563eb;">{left_score}</div>
  </div>
  <div style="font-size:2rem;">-</div>
  <div style="text-align:center;min-width:130px;">
    <div style="font-size:1.1rem;">{team2}</div>
    <div style="font-size:3.4rem;color:#dc2626;">{right_score}</div>
  </div>
</div>
"""


def show_number_pad(match_id, team_name, score_key, side):
    st.markdown(f"#### {team_name}")

    for row in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
        cols = st.columns(3)

        for idx, num in enumerate(row):
            with cols[idx]:
                if st.button(
                    str(num),
                    key=f"{side}_{match_id}_{num}",
                    use_container_width=True,
                ):
                    st.session_state[score_key] = str(num)
                    st.rerun()

    bottom = st.columns(3)

    with bottom[1]:
        if st.button(
            "0",
            key=f"{side}_{match_id}_0",
            use_container_width=True,
        ):
            st.session_state[score_key] = "0"
            st.rerun()

    if st.button(
        "⌫ Reset",
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
        st.markdown("### ⚽ Exacte uitslag")

        st.markdown(
            score_display_html(
                team1,
                team2,
                st.session_state[score1_key],
                st.session_state[score2_key],
            ),
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns(2)

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

            st.success(f"Voorspelling: {s1} - {s2} → {pred_text}")

            if st.button(
                "✅ Score bevestigen",
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

    flag1 = flag_emoji(code1)
    flag2 = flag_emoji(code2)

    date = str(match.get("datum", ""))
    time = str(match.get("tijd", ""))

    current = st.session_state["local_predictions"].get(match_id, {})

    selected = current.get("prediction", "")
    score1 = current.get("score1", "")
    score2 = current.get("score2", "")

    with st.container(border=True):
        col_date, col_match = st.columns([1.1, 4])

        with col_date:
            st.markdown(f"📅 **{date}**")
            st.markdown(f"🕒 **{time}**")

        with col_match:
            st.markdown(
                f"""
<div style="display:flex;align-items:center;justify-content:center;gap:16px;font-size:1.35rem;font-weight:800;margin-bottom:12px;">
  <span style="font-size:2.6rem;">{flag1}</span>
  <span>{team1}</span>
  <span style="margin:0 8px;">-</span>
  <span style="font-size:2.6rem;">{flag2}</span>
  <span>{team2}</span>
</div>
""",
                unsafe_allow_html=True,
            )

        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

        with c1:
            if st.button("1", key=f"btn_1_{match_id}", use_container_width=True, disabled=disabled):
                set_prediction(match_id, "1")
                st.rerun()

        with c2:
            if st.button("X", key=f"btn_x_{match_id}", use_container_width=True, disabled=disabled):
                set_prediction(match_id, "X")
                st.rerun()

        with c3:
            if st.button("2", key=f"btn_2_{match_id}", use_container_width=True, disabled=disabled):
                set_prediction(match_id, "2")
                st.rerun()

        with c4:
            if st.button("⚽ Uitslag", key=f"score_button_{match_id}", use_container_width=True, disabled=disabled):
                st.session_state[f"show_score_{match_id}"] = not st.session_state.get(
                    f"show_score_{match_id}",
                    False,
                )
                st.rerun()

        if selected:
            if score1 != "" and score2 != "":
                st.success(f"Gekozen: {score1} - {score2} → {selected}")
            else:
                st.success(f"Gekozen: {selected}")

        if st.session_state.get(f"show_score_{match_id}", False):
            show_score_dialog(match, match_id)


def show_group_phase(user, matches_df, predictions_df):
    user_id = str(user["user_id"])

    load_existing_predictions(user_id, predictions_df)

    locked = tournament_locked()
    final = user_is_final(user_id, predictions_df)

    disabled = locked or final

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
        st.warning("🔒 Je pronostiek is definitief ingediend.")
    else:
        st.info(f"🟢 Open tot {TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}.")

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

            st.success(f"{count} keuzes definitief ingediend.")
            st.rerun()
