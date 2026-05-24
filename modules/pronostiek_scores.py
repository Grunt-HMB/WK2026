import streamlit as st
import pandas as pd
from modules.database import (
    load_matches,
    load_predictions,
    batch_save_predictions,
)


def show_pronostiek_scores(user_id="Tom", standings_df=None):

    def country_flag(code):
        code = str(code or "").strip().upper()
        if len(code) != 2:
            return "⚽"
        return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

    def format_date(value):
        txt = str(value or "").strip()
        parts = txt.split("-")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return txt

    def format_time(value):
        txt = str(value or "").strip()
        if txt.count(":") >= 2:
            return ":".join(txt.split(":")[:2])
        return txt

    if "local_predictions" not in st.session_state:
        st.session_state.local_predictions = {}

    loaded_key = f"loaded_predictions_{user_id}"
    if loaded_key not in st.session_state:
        st.session_state[loaded_key] = False

    st.markdown(
        """
        <style>
        .block-container { 
            padding-top: 65px !important;
            padding-bottom: 95px !important;
        }

        .st-key-save_button_top button {
            position: fixed !important;
            bottom: 15px !important;
            left: 15px !important;
            z-index: 9999999 !important;

            width: 150px !important;
            height: 50px !important;

            border-radius: 14px !important;
            font-size: 16px !important;
            font-weight: 800 !important;

            box-shadow: 0 4px 16px rgba(0,0,0,0.45) !important;
        }

        .st-key-back_to_main_menu button {
            position: fixed !important;
            top: 12px !important;
            left: 15px !important;
            z-index: 9999999 !important;

            width: 150px !important;
            height: 42px !important;
        }

        [class*="st-key-match_card_"] {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 14px;
            padding: 0.65rem !important;
            margin-bottom: 0.65rem;
        }

        .match-date-small {
            font-size: 0.82rem;
            color: #94a3b8;
            margin-bottom: 4px;
        }

        .match-teams-onecell {
            font-weight: 700;
            line-height: 1.35;
        }

        .score-inputs {
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.08);
        }

        .score-label {
            font-size: 0.78rem;
            color: #94a3b8;
            margin-bottom: 3px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    @st.cache_data(ttl=60)
    def get_data(active_user_id):
        return load_matches(), load_predictions(active_user_id)

    matches_df, predictions_df = get_data(user_id)

    if not st.session_state[loaded_key]:
        if not predictions_df.empty:
            for _, row in predictions_df.iterrows():
                mid = str(row.get("match_id", "")).strip()

                if mid:
                    pred = str(row.get("prediction", "")).upper().strip()

                    if pred in ["1", "X", "2"]:
                        st.session_state.local_predictions[mid] = {
                            "prediction": pred,
                            "score1": int(row.get("score1", 0)),
                            "score2": int(row.get("score2", 0)),
                        }

        st.session_state[loaded_key] = True

    if st.button(
        "☰ Hoofdmenu",
        key="back_to_main_menu",
        use_container_width=False,
    ):
        st.session_state.main_page = "🏠 Hoofdmenu"
        st.rerun()

    if st.button(
        "💾 OPSLAAN",
        key="save_button_top",
        use_container_width=False,
        type="primary",
    ):
        st.write(st.session_state.local_predictions)
        saved = batch_save_predictions(
            user_id=user_id,
            local_predictions=st.session_state.local_predictions,
            status="concept",
        )

        st.success(f"Opgeslagen: {saved} wedstrijden")

    wedstrijden = matches_df.copy()

    if wedstrijden.empty:
        st.warning("Geen wedstrijden gevonden.")
        return

    wedstrijden["match_id"] = wedstrijden["match_id"].astype(str).str.strip()

    for _, match in wedstrijden.iterrows():

        match_id = str(match.get("match_id", "")).strip()

        if not match_id:
            continue

        datum = format_date(match.get("datum", ""))
        tijd = format_time(match.get("tijd", ""))

        team1 = str(match.get("team1", "")).strip()
        team2 = str(match.get("team2", "")).strip()

        team1_code = match.get("team1_code", "")
        team2_code = match.get("team2_code", "")

        pred_key = f"pred_{match_id}"

        current = st.session_state.local_predictions.get(match_id, {})
        current_pred = current.get("prediction")

        with st.container(key=f"match_card_{match_id}"):

            col_info, col_pred = st.columns([2.1, 1], gap="small")

            with col_info:
                st.markdown(
                    f"""
                    <div class="match-date-small">
                        <b>{datum}</b> &nbsp; {tijd} &nbsp; 🟢
                    </div>

                    <div class="match-teams-onecell">
                        {country_flag(team1_code)} {team1}
                        <span style="color:#9ca3af;">vs</span>
                        {country_flag(team2_code)} {team2}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_pred:
                selected = st.segmented_control(
                    label="Pronostiek",
                    options=["1", "X", "2"],
                    key=pred_key,
                    default=current_pred,
                    label_visibility="collapsed",
                )

                if selected:
                    if match_id not in st.session_state.local_predictions:
                        st.session_state.local_predictions[match_id] = {}

                    st.session_state.local_predictions[match_id]["prediction"] = selected

                if selected:
                    st.markdown(
                        '<div class="score-inputs">',
                        unsafe_allow_html=True,
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown(
                            f"<div class='score-label'>{team1}</div>",
                            unsafe_allow_html=True,
                        )

                        s1 = st.number_input(
                            "",
                            min_value=0,
                            max_value=15,
                            value=int(current.get("score1", 0)),
                            key=f"score1_{match_id}",
                            label_visibility="collapsed",
                        )

                        st.session_state.local_predictions[match_id]["score1"] = s1

                    with c2:
                        st.markdown(
                            f"<div class='score-label'>{team2}</div>",
                            unsafe_allow_html=True,
                        )

                        s2 = st.number_input(
                            "",
                            min_value=0,
                            max_value=15,
                            value=int(current.get("score2", 0)),
                            key=f"score2_{match_id}",
                            label_visibility="collapsed",
                        )

                        st.session_state.local_predictions[match_id]["score2"] = s2

                    st.markdown("</div>", unsafe_allow_html=True)
