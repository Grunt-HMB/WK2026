import streamlit as st
from modules.database import batch_upsert_predictions
from modules.settings import TOURNAMENT_START
from modules.utils import (
    flag_emoji,
    result_from_score,
    tournament_locked,
    safe_int,
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

        if not match_id:
            continue

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

    return (
        user_preds["status"]
        .astype(str)
        .str.upper()
        == "FINAL"
    ).any()


def set_prediction(match_id, choice):

    if "local_predictions" not in st.session_state:
        st.session_state["local_predictions"] = {}

    current = st.session_state["local_predictions"].get(str(match_id), {})

    current["prediction"] = choice

    if "score1" not in current:
        current["score1"] = ""

    if "score2" not in current:
        current["score2"] = ""

    st.session_state["local_predictions"][str(match_id)] = current


def set_score(match_id, score1, score2):

    prediction = result_from_score(score1, score2)

    st.session_state["local_predictions"][str(match_id)] = {
        "prediction": prediction,
        "score1": score1,
        "score2": score2,
    }


def show_score_dialog(match, match_id):

    team1 = str(match.get("team1", ""))
    team2 = str(match.get("team2", ""))

    current = st.session_state["local_predictions"].get(
        str(match_id),
        {}
    )

    with st.expander(
        f"⚽ Uitslag invullen: {team1} - {team2}",
        expanded=True
    ):

        c1, c2 = st.columns(2)

        with c1:

            score1 = st.number_input(
                team1,
                min_value=0,
                max_value=20,
                value=safe_int(current.get("score1")) or 0,
                step=1,
                key=f"score1_{match_id}",
            )

        with c2:

            score2 = st.number_input(
                team2,
                min_value=0,
                max_value=20,
                value=safe_int(current.get("score2")) or 0,
                step=1,
                key=f"score2_{match_id}",
            )

        if st.button(
            "Score bevestigen",
            key=f"confirm_score_{match_id}",
            use_container_width=True,
        ):

            set_score(match_id, score1, score2)

            st.session_state[
                f"show_score_{match_id}"
            ] = False

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

    current = st.session_state["local_predictions"].get(
        match_id,
        {}
    )

    selected = current.get("prediction", "")
    score1 = current.get("score1", "")
    score2 = current.get("score2", "")

    st.markdown(
        f"""
<div class="match-card">

    <div class="match-grid">

        <div class="datebox">
            📅 {date}<br>
            🕒 {time}
        </div>

        <div class="teams">

            <div class="team">
                <div class="flag">{flag1}</div>

                <div class="team-name">
                    {team1}
                </div>
            </div>

            <div class="vs">
                -
            </div>

            <div class="team right">
                <div class="flag">{flag2}</div>

                <div class="team-name">
                    {team2}
                </div>
            </div>

        </div>

    </div>

</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

    with c1:

        if st.button(
            "1",
            key=f"btn_1_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):

            set_prediction(match_id, "1")
            st.rerun()

    with c2:

        if st.button(
            "X",
            key=f"btn_x_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):

            set_prediction(match_id, "X")
            st.rerun()

    with c3:

        if st.button(
            "2",
            key=f"btn_2_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):

            set_prediction(match_id, "2")
            st.rerun()

    with c4:

        if st.button(
            "⚽ Uitslag",
            key=f"score_button_{match_id}",
            use_container_width=True,
            disabled=disabled,
        ):

            st.session_state[
                f"show_score_{match_id}"
            ] = not st.session_state.get(
                f"show_score_{match_id}",
                False
            )

            st.rerun()

    if selected:

        if score1 != "" and score2 != "":

            st.success(
                f"Gekozen: {score1} - {score2}  →  {selected}"
            )

        else:

            st.success(
                f"Gekozen: {selected}"
            )

    if st.session_state.get(
        f"show_score_{match_id}",
        False
    ):

        show_score_dialog(match, match_id)


def show_group_phase(user, matches_df, predictions_df):

    user_id = str(user["user_id"])

    load_existing_predictions(
        user_id,
        predictions_df
    )

    locked = tournament_locked()

    final = user_is_final(
        user_id,
        predictions_df
    )

    disabled = locked or final

    groups = sorted([
        str(g)
        for g in matches_df["groep"].dropna().unique()
        if str(g).strip()
        not in ["", "-", "Knock-out"]
    ])

    if not groups:

        st.warning(
            "Geen groepen gevonden in tabblad Matches."
        )

        return

    top1, top2 = st.columns([3, 1])

    with top1:

        st.markdown(
            '<div class="main-title">👥 Groepsfase</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="page-subtitle">Maak je voorspellingen per poule.</div>',
            unsafe_allow_html=True
        )

    with top2:

        selected_group = st.selectbox(
            "Groep",
            groups,
            label_visibility="collapsed"
        )

    if locked:

        st.error(
            "🔒 Het tornooi is gestart. Wijzigen is niet meer mogelijk."
        )

    elif final:

        st.warning(
            "🔒 Je pronostiek is definitief ingediend."
        )

    else:

        st.info(
            f"🟢 Open tot {TOURNAMENT_START.strftime('%d/%m/%Y %H:%M')}."
        )

    group_matches = matches_df[
        matches_df["groep"].astype(str)
        == str(selected_group)
    ].copy()

    group_matches = group_matches.sort_values(
        ["datum", "tijd", "match_id"],
        kind="stable"
    )

    st.subheader(f"Groep {selected_group}")

    for _, match in group_matches.iterrows():

        render_match_card(
            match,
            disabled
        )

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
                "DRAFT"
            )

            st.success(
                f"{count} keuzes opgeslagen als concept."
            )

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
                "FINAL"
            )

            st.success(
                f"{count} keuzes definitief ingediend."
            )

            st.rerun()
